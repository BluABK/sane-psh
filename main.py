import json
from flask import Flask, make_response, request, jsonify, Response
from bs4 import BeautifulSoup
import datetime
import os

from utils import pp_dict

# Set up Flask.
app = Flask(__name__)


def handle_get(req, callback=None):
    topic = request.args["hub.topic"]
    challenge = request.args["hub.challenge"]
    mode = request.args["hub.mode"]
    if 'hub.lease_seconds' in request.args:
        lease_seconds = request.args["hub.lease_seconds"]
    else:
        lease_seconds = ""
    if 'hub.verify_token' in request.args:
        verify_token = request.args['hub.verify_token']
        # retv = verify_token

    print("topic: {}\n"
          "challenge: {}\n"
          "mode: {}\n"
          "lease_seconds: {}".format(topic, challenge, mode, lease_seconds))

    return challenge


def handle_deleted_entry(xml, callback=None):
    deleted_entry = xml.find('at:deleted-entry')
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
            'title': xml.feed.entry.title.string,
            'links': [{'href': lnk.get('href'), 'rel': lnk.get('rel')} for lnk in xml.feed.entry.find_all('link')],
            'channel_title': xml.feed.entry.author.find('name').string,  # Need find due to name collision with 'name'.
            'channel_uri': xml.feed.entry.author.uri.string,
            'published': xml.feed.entry.published.string,
            'updated': xml.feed.entry.updated.string
        }
    }

    if callback is not None:
        callback(result)

    return result


@app.route('/sane-psh/', methods=['GET', 'POST'])
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
        datetime_stamp = datetime.datetime.utcnow().isoformat().replace(':', '-').replace('T', '_')
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
            d = handle_video(xml)
            if d is not None:
                pp_dict(d)

    if request.method == 'GET':
        retv = handle_get(request)

    return make_response(retv, 200)


if __name__ == "__main__":
    listener_bind_host = "127.0.0.1"
    listener_bind_port = 5000

    app.run(host=listener_bind_host, port=listener_bind_port, debug=True)
