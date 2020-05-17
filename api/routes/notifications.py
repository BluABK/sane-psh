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
from settings import API_BASEROUTE, API_VERSION
from handlers.config_handler import CONFIG, has_option
from utils import log_all_error, check_required_args, console_log
from database.models.channel import Channel
from database.models.video import Video
from database.operations import add_row, row_exists, update_channel, update_video, del_row_by_filter
from utils import datetime_ns_to_ms, dict_to_pretty_string

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

    verify_token = None
    hmac_secret = None
    topic = req.args["hub.topic"]
    r = r'^https:\/\/www\.youtube\.com\/xml\/feeds\/videos\.xml\?channel_id=(.*)$'
    channel_id = re.match(r, topic).groups()[0]
    challenge = req.args["hub.challenge"]
    mode = req.args["hub.mode"]
    if 'hub.lease_seconds' in req.args:
        lease_seconds = req.args["hub.lease_seconds"]
    else:
        lease_seconds = ""

    log.info("New GET Request: topic: {}, challenge: {}, mode: {}, lease_seconds: {}".format(
        topic, challenge, mode, lease_seconds))

    # Add to database if not exist, else update existing.
    if not row_exists(Channel, channel_id=channel_id):
        add_row(Channel(channel_id=channel_id, subscribed=bool(mode == "subscribe"),
                        hmac_secret=hmac_secret))
    else:
        update_channel(channel_id, subscribed=(mode == "subscribe"),
                       hmac_secret=hmac_secret)

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

    if row_exists(Video, video_id=video_id):
        # Delete video from DB as it was deleted on YouTube's end.
        del_row_by_filter(Video, video_id=video_id)

    if callback is not None:
        callback(result)

    return result


def handle_video(xml, callback=None):
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

    # Add to database if not exist, else update existing.
    if not row_exists(Video, video_id=entry["video_id"]):
        # If there is more than two minutes time difference between publish and update,
        # the video is probably not freshly posted; treat it as an update.
        if updated_on.timestamp() - published_on.timestamp() > 120:
            entry["kind"] = "update"
        else:
            # Indicate video as new as it didn't exist in DB and update is less than two minutes older.
            entry["kind"] = "new"

            # DB sometimes isn't written fast enough for the above check to come true.
            # use a global list for reference, if configured to.
            if CONFIG["increase_kind_precision"] is True:
                if entry["video_id"] in VIDEO_ID_HISTORY:
                    # Video exists in the global video ID list, so it is an update.
                    entry["kind"] = "update"

            else:
                # Not configured for increased precision, so assume new.
                entry["kind"] = "new"

        # Write video to DB.
        add_row(
            Video(video_id=entry["video_id"],
                  channel_id=entry["channel_id"],
                  video_title=entry["video_title"],
                  published_on=published_on,
                  updated_on=updated_on
                  )
        )

        # Update global list of video IDs, if configured to.
        if CONFIG["increase_kind_precision"] is True:
            if entry["video_id"] not in VIDEO_ID_HISTORY:
                VIDEO_ID_HISTORY.append(entry["video_id"])

        if row_exists(Channel, channel_id=entry["channel_id"]):
            # Update channel title (only included with a Video Atom feed).
            update_channel(entry["channel_id"], channel_title=entry["channel_title"])

    # Update existing.
    else:
        entry["kind"] = "update"

        update_video(entry['video_id'], video_title=entry["video_title"])

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


# @app.route('{}/notifications'.format(API_BASEROUTE), methods=['GET', 'POST'])
def psh():
    datetime_stamp = datetime.datetime.now(timezone.utc).isoformat().replace(':', '-').replace('T', '_')
    retv = ''

    req_info = {
        "path": request.path,
        "headers": {k: v for k, v in request.headers.items()},
        "args": request.args,
        "data": request.data.decode("utf-8"),
        "form": request.form,
        "json": request.json}

    log.info("{method} {path} ({cnt_type}) {from_hdr}\n{req_info}".format(
        method=request.method,
        path=req_info["path"],
        from_hdr="From: {}".format(req_info["headers"]["From"]) if "From" in req_info["headers"] else "",
        cnt_type="({})".format(req_info["headers"]["Content-Type"]) if "Content-Type" in req_info["headers"] else "",
        req_info=json.dumps(req_info, indent=4)))

    if request.method == 'POST':
        # Verify HMAC authentication, if specified in config.
        if CONFIG["require_hmac_authentication"]:
            if 'X-Hub-Signature' in request.headers:
                signature = hmac.new(str.encode(CONFIG["hmac_secret"]), request.data, hashlib.sha1).hexdigest()
                if "sha1={}".format(signature) != request.headers['X-Hub-Signature']:
                    log_all_error("ERROR: HMAC Signature mismatch! ({theirs} != {ours})".format(
                        theirs=request.headers['X-Hub-Signature'], ours=signature))

                    return "ERROR: HMAC Signature mismatch!"
            else:
                log_all_error("ERROR: POST Request is missing required HMAC authentication (X-Hub-Signature) header!")

                return "ERROR: POST Request is missing required HMAC authentication (X-Hub-Signature) header!"

        # xml = BeautifulSoup(request.data, features="xml")  # Doesn't standardise tag casing
        xml = BeautifulSoup(request.data, "lxml")  # Standardises tag casing

        log.debug("XML/Atom feed\n{}".format(xml.feed.prettify()))
        if not os.path.isdir('request_cache'):
            os.mkdir('request_cache')
        with open('request_cache/post_request_at_{}.xml'.format(datetime_stamp), 'w') as f:
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

                return "ERROR: Got unexpected feed type, aborting!"

    if request.method == 'GET':
        retv = handle_get(request)

    return make_response(retv, 200)
