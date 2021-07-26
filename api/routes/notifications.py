import json
import os
import re
import datetime
from datetime import timezone
from bs4 import BeautifulSoup
import hmac
import hashlib
from flask import make_response, request

from handlers.log_handler import create_logger
from handlers.config_handler import CONFIG
from utils import log_all_error, check_required_args, console_log, log_request, verify_request_hmac
from database.models.channel import Channel
from database.operations import add_row, update_channel, del_video_by_id, get_channel, get_video, \
    add_or_update_video
from utils import datetime_ns_to_ms

log = create_logger(__name__)

VIDEO_ID_HISTORY = []

# FIXME: Add handling for UTC offset (need to remove the ':')
FEED_UPDATED_FMT = "%Y-%m-%dT%H:%M:%S.%f+00:00"
FEED_PUBLISHED_FMT = "%Y-%m-%dT%H:%M:%S+00:00"
FEED_DELETED_FMT = FEED_PUBLISHED_FMT


def handle_get(req, callback=None):
    # If verification token is specified as a requirement, check that it is valid.
    if CONFIG["require_verification_token"] is True:
        if 'hub.verify_token' in list(req.args.keys()):
            if req.args["hub.verify_token"] != CONFIG["verification_token"]:
                return "ERROR: hub.verify_token mismatch!"
        else:
            return "ERROR: GET Request is missing required argument: hub.verify_token"

    # Check that all required args are included in the request:
    chk = check_required_args(list(req.args.keys()), ['hub.topic', 'hub.challenge', 'hub.mode'])
    if not chk["result"]:
        return "ERROR: GET Request is missing required argument: {arg}".format(arg=chk["arg"])

    verify_token = None  # FIXME: Unused!
    hmac_secret = None   # FIXME: Unused!
    topic = req.args["hub.topic"]
    r = r'^https:\/\/www\.youtube\.com\/xml\/feeds\/videos\.xml\?channel_id=(.*)$'
    channel_id = re.match(r, topic).groups()[0]
    challenge = req.args["hub.challenge"]
    mode = req.args["hub.mode"]
    lease_seconds = None
    if 'hub.lease_seconds' in req.args:
        lease_seconds = float(req.args["hub.lease_seconds"])
        expires_on = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp() + lease_seconds)
    else:
        if not mode == "unsubscribe":
            log.error("lease_seconds missing for mode: '{}'! Setting None".format(mode))

        expires_on = None

    log.info("New GET Request (mode: {mode}): topic: {topic}, challenge: {cha}, lease_seconds: {lease}".format(
        topic=topic, cha=challenge, mode=mode, lease=lease_seconds))

    # Add to database if not exist, else update existing.
    if not get_channel(channel_id):
        add_row(Channel(channel_id=channel_id, subscribed=bool(mode == "subscribe"), expires_on=expires_on))
    else:
        update_channel(channel_id, subscribed=(mode == "subscribe"), expires_on=expires_on)

    log.info("Returning challenge value: {challenge}.".format(challenge=challenge))
    return challenge


def handle_deleted_entry(xml, callback=None):
    deleted_entry = xml.feed.find('at:deleted-entry')
    result = {
        'deleted_entry': {
            'ref': deleted_entry['ref'],
            'when': deleted_entry['when'],
            'link':
                [{'href': lnk.get('href')} for lnk in deleted_entry.find_all('link')]
                if len(deleted_entry.find_all('link')) > 1
                else {'href': deleted_entry.link.get('href')},
            'kind': "delete"
        },
        'by': {
            'name': deleted_entry.find('at:by').find('name').string,
            'uri': deleted_entry.find('at:by').uri.string
        }
    }

    video_id = deleted_entry['ref'].split(':')[-1]

    if get_video(video_id):
        # Delete video from DB as it was deleted on YouTube's end.
        # del_row_by_filter(Video, video_id=video_id)
        del_video_by_id(video_id=video_id)

    if callback is not None:
        callback(result)

    return result


def handle_video(xml, callback=None):
    """
    Handle Video XML data payload.

    Also adds key "kind" with value of "new" or "update",
    as some published videos aren't really new.
    :param xml:
    :param callback:
    :return:
    """
    # DB sometimes isn't written fast enough for the above check to come true.
    # use a global list for reference, if configured to.
    global VIDEO_ID_HISTORY

    result = {
        "links": [{'href': lnk.get('href'), 'rel': lnk.get('rel')} for lnk in xml.feed.find_all('link')],
        "title": xml.feed.title.string,
        "updated": xml.feed.updated.string,
        "entry": {
            'id': xml.feed.entry.id.string,
            'video_id': xml.feed.entry.find('yt:videoid').string,
            'channel_id': xml.feed.entry.find('yt:channelid').string,
            'video_title': xml.feed.entry.title.string,
            'links': [{'href': lnk.get('href'), 'rel': lnk.get('rel')} for lnk in xml.feed.entry.find_all('link')],
            'channel_title': xml.feed.entry.author.find('name').string,  # Need find due to name collision with 'name'.
            'channel_uri': xml.feed.entry.author.uri.string,
            'published': xml.feed.entry.published.string,
            'updated': xml.feed.entry.updated.string
        }
    }

    entry = result["entry"]

    published_on = datetime.datetime.strptime(entry["published"], FEED_PUBLISHED_FMT)
    updated_on = datetime.datetime.strptime(datetime_ns_to_ms(entry["updated"]), FEED_UPDATED_FMT)

    # # If there is more than two minutes time difference between publish and update,
    # # the video is probably not freshly posted; treat it as an update.
    # if updated_on.timestamp() - published_on.timestamp() > 120:
    # FIXME: Keep? ^

    # If video is already in DB, it is an update else it's a new video.
    if get_video(entry["video_id"]) or entry["video_id"] in VIDEO_ID_HISTORY:
        entry["kind"] = "update"
    else:
        entry["kind"] = "new"

    # Update global list of video IDs.
    if entry["video_id"] not in VIDEO_ID_HISTORY:
        VIDEO_ID_HISTORY.append(entry["video_id"])

    # Add Video to DB or update existing entry.
    add_or_update_video(video_id=entry["video_id"],
                        channel_id=entry["channel_id"],
                        video_title=entry["video_title"],
                        published_on=published_on,
                        updated_on=updated_on
                        )

    # Retroactively update channel title (only included with a Video Atom feed).
    if get_channel(entry["channel_id"]):
        update_channel(entry["channel_id"], channel_title=entry["channel_title"])

    if callback is not None:
        callback(result)

    return result


def handled_video_to_string(d):
    entry = d["entry"]
    channel_title = entry["channel_title"]
    video_title = entry["video_title"]

    url = entry["links"][0]["href"]

    return "{publish_kind} [{url}] {channel_title} - {video_title}".format(
        publish_kind="{}:".format(entry["kind"]).upper().ljust(7), channel_title=channel_title,
        video_title=video_title, url=url)


def psh():
    datetime_stamp = datetime.datetime.now(timezone.utc).isoformat().replace(':', '-').replace('T', '_')

    log_request(request)

    if request.method == 'POST':
        # Verify HMAC authentication, if specified in config.
        if CONFIG["require_hmac_authentication"] is True:
            if 'X-Hub-Signature' in request.headers:
                hmac_result = verify_request_hmac(
                    request.headers['X-Hub-Signature'], request.data,  CONFIG["hmac_secret"])

                if hmac_result["code"] != 200:
                    log_all_error("HTTP {code}: {msg}".format(**hmac_result))
            else:
                log_all_error("ERROR: POST Request is missing required HMAC authentication (X-Hub-Signature) header!")

        xml = BeautifulSoup(request.data, "lxml")  # "lxml" Standardises tag casing, "xml" does not.

        log.debug("XML/Atom feed\n{}".format(xml.feed.prettify()))
        if not os.path.isdir('request_cache'):
            os.mkdir('request_cache')
        with open('request_cache/post_request_at_{}.xml'.format(datetime_stamp), 'w', encoding="utf-8") as f:
            f.write(xml.decode('utf-8'))

        if xml.feed.find('at:deleted-entry'):
            d = handle_deleted_entry(xml)
            if d is not None:
                log.info("Deleted entry: \n{}".format(json.dumps(d, indent=4)))

                console_log("DELETE: {video_id}".format(video_id=d["deleted_entry"]["ref"].split(':')[-1]))
        else:
            if xml.feed.title.string == "YouTube video feed":
                d = handle_video(xml)
                if d is not None:
                    log.info("YouTube video: {vid_str}\n{obj}".format(
                        vid_str=handled_video_to_string(d),
                        obj=json.dumps(d, indent=4)))

                    # Print one-line result to console.
                    console_log(handled_video_to_string(d))
            else:
                log_all_error("ERROR: Got unexpected feed type, aborting!")

        # Confirm receipt of request to HUB, with a HTTP 200 OK.
        # If the signature does not match, subscribers MUST still return a 2xx success response
        # to acknowledge receipt, but locally ignore the message as invalid.
        return make_response('OK', 200)

    elif request.method == 'GET':
        # Handle GET request and obtain challenge code.
        challenge = handle_get(request)

        # Respond with HTTP 200 and challenge code as msg.
        return make_response(challenge, 200)
