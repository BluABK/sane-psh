# Sane YouTube PubSubHubbub Server

[![Build Status](https://api.travis-ci.org/BluABK/sane-psh.svg?branch=master)](https://travis-ci.org/BluABK/sane-psh)
[![GitHub issues](https://img.shields.io/github/issues/bluabk/sanepp.svg)](https://github.com/BluABK/sanepp/issues)
![GitHub repo size](https://img.shields.io/github/repo-size/bluabk/sanepp.svg?style=popout)
![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/bluabk/sanepp.svg)


## How to Use
###### (Recommended: Check out [YouTube's official guide](https://developers.google.com/youtube/v3/guides/push_notifications).)

1. Install on a server that is internet accessible.
2. Set the following required config options in `config.json`:
    * notifications_callback (e.g. `http://example.com/api/notifications`).
3. Start the server (e.g. `python3 main.py`).
4. Make a subscription request to the API:
    * cURL example: `curl -X POST http://example.com/api/subscribe?id=CHANNEL_ID`

## "PubSubHubbub"?
**[PubSubHubbub](https://github.com/pubsubhubbub/PubSubHubbub)** is an open protocol for distributed publish/subscribe communication on the Internet. It generalizes the concept of webhooks and allows data producers and data consumers to work in a decoupled way.

PubSubHubbub provides a way to subscribe, unsubscribe and receive updates from a resource, whether it's an RSS or Atom feed or any web accessible document (JSON...).