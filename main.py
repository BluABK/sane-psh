import json
from flask import Flask, make_response, request, jsonify
from bs4 import BeautifulSoup
import datetime

# Set up Flask.
app = Flask(__name__)


@app.route('/sane-psh/', methods=['GET', 'POST'])
def psh():
    print("HEADERS: {}".format(request.headers))
    # print("REQ_path {}".format(request.path))
    # print("ARGS: {}".format(request.args))
    # print("DATA: {}".format(request.data))
    # print("FORM: {}".format(request.form))
    # print("JSON: {}".format(request.json))
    datetime_stamp = datetime.datetime.utcnow().isoformat().replace(':', '-')
    # with open('request_at_{}'.format(datetime_stamp), 'w') as f:
    #     f.write(request.data)
    xml = BeautifulSoup(request.data, features="xml")

    # xml = ET.fromstring(request.data)
    print(xml.feed.prettify())
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

    return make_response('', 200)


if __name__ == "__main__":
    listener_bind_host = "127.0.0.1"
    listener_bind_port = 5000

    print("Hello world!")

    app.run(host=listener_bind_host, port=listener_bind_port, debug=True)
