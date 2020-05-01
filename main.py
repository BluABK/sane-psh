import json
from flask import Flask, make_response, request, jsonify, Response
from bs4 import BeautifulSoup
import datetime
import os

# Set up Flask.
app = Flask(__name__)


@app.route('/sane-psh/', methods=['GET', 'POST'])
def psh():
    retv = ''
    headers= []

    print("HEADERS: {}".format(request.headers))
    print("REQ_path {}".format(request.path))
    print("ARGS: {}".format(request.args))
    print("DATA: {}".format(request.data))
    print("FORM: {}".format(request.form))
    print("JSON: {}".format(request.json))
    print("Method: {}".format(request.method))

    if request.method == 'POST':
        datetime_stamp = datetime.datetime.utcnow().isoformat().replace(':', '-')
        xml = BeautifulSoup(request.data, features="xml")

        print(xml.feed.prettify())
        if not os.path.isdir('dumps'):
            os.mkdir('dumps')
        with open('dumps/request_at_{}.xml'.format(datetime_stamp), 'w') as f:
            f.write(xml.feed.prettify())

        links = [{'href': lnk.get('href'), 'rel': lnk.get('rel')} for lnk in xml.feed.find_all('link')]
        title = xml.feed.title.string
        updated = xml.feed.updated.string
        entry = {
            'id': xml.feed.entry.id.string,
            'video_id': xml.feed.entry.find('yt:videoId').string,
            'channel_id': xml.feed.entry.find('yt:channelId').string,
            'title': xml.feed.entry.title.string,
            'links': [{'href': lnk.get('href'), 'rel': lnk.get('rel')} for lnk in xml.feed.entry.find_all('link')],
            'channel_title': xml.feed.entry.author.name,
            'channel_uri': xml.feed.entry.author.uri.string,
            'published': xml.feed.entry.published.string,
            'updated': xml.feed.entry.updated.string
        }

        print("\n")
        print("Links: {links}".format(links=links))
        print("Title: {title}".format(title=title))
        print("Updated: {updated}".format(updated=updated))
        print("Entry: :")
        for key, value in entry.items():
            print("\t{key}: {value}".format(key=key, value=value))

    if request.method == 'GET':
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

        retv = challenge

    return make_response(retv, 200)


if __name__ == "__main__":
    listener_bind_host = "127.0.0.1"
    listener_bind_port = 5000

    app.run(host=listener_bind_host, port=listener_bind_port, debug=True)
