import os
import json
import re
from datetime import datetime, timezone

from flask import Flask, make_response, request, jsonify, Response
from bs4 import BeautifulSoup
import hmac
import hashlib

from database import init_db
from database.models.channel import Channel
from database.models.video import Video
from database.operations import add_row, row_exists, update_channel, update_video, del_row_by_filter
from utils import pp_dict, datetime_ns_to_ms

from globals import CONFIG_PATH

API_VERSION = 1
API_BASEROUTE = '/api'

with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)

# Set up Flask.
app = Flask(__name__)

# FIXME: Add handling for UTC offset (need to remove the ':')
FEED_UPDATED_FMT = "%Y-%m-%dT%H:%M:%S.%f+00:00"
FEED_PUBLISHED_FMT = "%Y-%m-%dT%H:%M:%S+00:00"
FEED_DELETED_FMT = FEED_PUBLISHED_FMT


def check_required_args(request_args: list, required_keys: list):
    for key in required_keys:
        if key not in request_args:
            return {"result": False, "arg": key}

    return {"result": True, "arg": None}


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

    print("topic: {}\n"
          "challenge: {}\n"
          "mode: {}\n"
          "lease_seconds: {}".format(topic, challenge, mode, lease_seconds))

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
                else {'href': deleted_entry.link.get('href')}
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

    # Add to database if not exist, else update existing.
    if not row_exists(Video, video_id=entry["video_id"]):
        add_row(
            Video(video_id=entry["video_id"],
                  channel_id=entry["channel_id"],
                  video_title=entry["video_title"],
                  published_on=datetime.strptime(entry["published"], FEED_PUBLISHED_FMT),
                  updated_on=datetime.strptime(datetime_ns_to_ms(entry["updated"]), FEED_UPDATED_FMT)
                  )
        )
        if row_exists(Channel, channel_id=entry["channel_id"]):
            # Update channel title (only included with a Video Atom feed).
            update_channel(entry["channel_id"], channel_title=entry["channel_title"])
    else:
        update_video(entry['video_id'], video_title=entry["video_title"])

    if callback is not None:
        callback(result)

    return result


@app.route('{}/notifications'.format(API_BASEROUTE), methods=['GET', 'POST'])
def psh():
    retv = ''
    indent = 4 * ' '
    print("NEW {method} REQUEST: ".format(method=request.method))
    print("{indent}REQ-PATH: {}".format(request.path, indent=indent))

    print("{indent}HEADERS: ".format(indent=indent))
    for key, value in request.headers.items():
        print("{indent}{key}: {value}".format(key=key, value=value, indent=indent+indent))
    if len(request.args) > 0:
        print("{indent}ARGS: {}".format(request.args, indent=indent))
    if request.data is not None:
        print("{indent}DATA: \n{indent}{indent}{data}".format(data=request.data, indent=indent))
    if len(request.form) > 0:
        print("{indent}FORM: {}".format(request.form, indent=indent))
    if request.json is not None:
        print("{indent}JSON: {}".format(request.json, indent=indent))

    print("")

    if request.method == 'POST':
        # Verify HMAC authentication, if specified in config.
        if CONFIG["require_hmac_authentication"]:
            if 'X-Hub-Signature' in request.headers:
                signature = hmac.new(str.encode(CONFIG["hmac_secret"]), request.data, hashlib.sha1).hexdigest()
                if "sha1={}".format(signature) != request.headers['X-Hub-Signature']:
                    print("ERROR: HMAC Signature mismatch! ({theirs} != {ours})".format(
                        theirs=request.headers['X-Hub-Signature'], ours=signature))
                    return "ERROR: HMAC Signature mismatch!"

                print("Valid Signature! \\o/")
            else:
                print("ERROR: POST Request is missing required HMAC authentication (X-Hub-Signature) header!")
                return "ERROR: POST Request is missing required HMAC authentication (X-Hub-Signature) header!"

        datetime_stamp = datetime.now(timezone.utc).isoformat().replace(':', '-').replace('T', '_')
        # xml = BeautifulSoup(request.data, features="xml")  # Doesn't standardise tag casing
        xml = BeautifulSoup(request.data, "lxml")  # Standardises tag casing

        # print(xml.feed.prettify())
        if not os.path.isdir('request_cache'):
            os.mkdir('request_cache')
        with open('request_cache/post_request_at_{}.xml'.format(datetime_stamp), 'w') as f:
            f.write(xml.decode('utf-8'))

        if xml.feed.find('at:deleted-entry'):
            d = handle_deleted_entry(xml)
            if d is not None:
                pp_dict(d)
        else:
            if xml.feed.title.string == "YouTube video feed":
                d = handle_video(xml)
                if d is not None:
                    pp_dict(d)
            else:
                print("ERROR: Got unexpected feed type, aborting!")

    if request.method == 'GET':
        retv = handle_get(request)

    return make_response(retv, 200)


if __name__ == "__main__":
    init_db()

    app.run(host=CONFIG["bind_host"], port=CONFIG["bind_port"], debug=CONFIG["debug_flask"])
