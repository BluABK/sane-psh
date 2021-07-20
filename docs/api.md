# API documentation (of sorts)

## /api/subscribe [POST]
Example run:
1. [USER] `curl -X POST http://sane-psh.bluabk.net/api/subscribe?id=UCzNWVDZQ55bjq8uILZ7_wyQ`
2. [SANE] `POST` [HUB] :
    1. Make POST (request holds until [HUB] GETs and verifies):
        ```json
            {
                "headers": {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                "args": {
                    "hub.callback": "<notifications_callback>",
                    "hub.verify": "<hub_verify_mode>",
                    "hub.mode": "subscribe",
                    "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCzNWVDZQ55bjq8uILZ7_wyQ"
                },
                "url":	"http://pubsubhubbub.appspot.com/?hub.callback=http%3A%2F%2Fsane-psh.bluabk.net%2Fapi%2Fnotifications&hub.verify=synchronous&hub.mode=subscribe&hub.topic=https%3A%2F%2Fwww.youtube.com%2Fxml%2Ffeeds%2Fvideos.xml%3Fchannel_id%3DUCzNWVDZQ55bjq8uILZ7_wyQ&hub.verify_token=<verification_token>&hub.secret=<hmac_secret>", 
                "encoding": "utf-8", 
                "history": [], 
                "request": "<PreparedRequest [POST]>"
            }
        ```   
        1. [HUB] `GET /api/notifications`:
           ```json
           {
                "path": "/api/notifications",
                "headers": {
                    "Host": "192.168.1.2:5015",
                    "Connection": "close",
                    "Cache-Control": "no-cache,max-age=0",
                    "Pragma": "no-cache",
                    "Accept": "*/*",
                    "From": "googlebot(at)googlebot.com",
                    "User-Agent": "FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)",
                    "Accept-Encoding": "gzip, deflate, br"
                },
                "args": {
                    "hub.topic": "https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCzNWVDZQ55bjq8uILZ7_wyQ",
                    "hub.challenge": "18010081214608488943",
                    "hub.verify_token": "<verification_token>",
                    "hub.mode": "subscribe",
                    "hub.lease_seconds": "432000"
                },
                "data": "",
                "form": {},
                "json": null
            }
           ```
        2. [SANE] return: `18010081214608488943`
    2. [SANE] Receive POST req response HTTP/202 from [HUB]:
          ```json
            {
                "_content": b"",
                "_content_consumed": True,
                "_next": None,
                "status_code": 202,
                "headers": {
                    "Cache-Control": "no-cache", 
                    "Content-Type": "text/plain; charset=utf-8", 
                    "X-Cloud-Trace-Context": "3aebb2842f3f85849ba039e666ff4207", 
                    "Date": "Mon, 19 Jul 2021 15:28:32 GMT", 
                    "Server": "Google Frontend", 
                    "Content-Length": "0"
                }, 
                "raw": <urllib3.response.HTTPResponse object at 0x00000271912A0F70>, 
                "url":	"http://pubsubhubbub.appspot.com/?hub.callback=http%3A%2F%2Fsane-psh.bluabk.net%2Fapi%2Fnotifications&hub.verify=synchronous&hub.mode=subscribe&hub.topic=https%3A%2F%2Fwww.youtube.com%2Fxml%2Ffeeds%2Fvideos.xml%3Fchannel_id%3DUCzNWVDZQ55bjq8uILZ7_wyQ&hub.verify_token=<verification_token>&hub.secret=<hmac_secret>", 
                "encoding": "utf-8", 
                "history": [], 
                "reason": "Accepted", 
                "cookies": <RequestsCookieJar[]>, 
                "elapsed": datetime.timedelta(seconds=1, microseconds=2119), 
                "request": <PreparedRequest [POST]>, 
                "connection": <requests.adapters.HTTPAdapter object at 0x00000271912C5AC0>
            }
        ```

## /api/unsubscibe [POST]
TODO (somewhat similar to subscribe)

## /api/notfications [GET, POST]
### GET
Used by [HUB] when subscribing/unsubscribing from a feed (channel).

### POST
Used to get notified by [HUB] about feed updates.
Content-Type: "application/atom+xml"

#### Examples
##### New video posted: `POST /api/notifications`
```json
    {
        "path": "/api/notifications",
        "headers": {
            "Host": "10.159.81.30:5015",
            "Connection": "close",
            "Content-Length": "904",
            "Link": "<https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCzNWVDZQ55bjq8uILZ7_wyQ>; rel=self, <http://pubsubhubbub.appspot.com/>; rel=hub",
            "Content-Type": "application/atom+xml",
            "X-Hub-Signature": "sha1=1d72d7b01cf6a0ac377984b97e50119808f47606",
            "Cache-Control": "no-cache,max-age=0",
            "Pragma": "no-cache",
            "Accept": "*/*",
            "From": "googlebot(at)googlebot.com",
            "User-Agent": "FeedFetcher-Google; (+http://www.google.com/feedfetcher.html)",
            "Accept-Encoding": "gzip, deflate, br"
        },
        "args": {},
        "data": "<?xml version='1.0' encoding='UTF-8'?>\n<feed xmlns:yt=\"http://www.youtube.com/xml/schemas/2015\" xmlns=\"http://www.w3.org/2005/Atom\"><link rel=\"hub\" href=\"https://pubsubhubbub.appspot.com\"/><link rel=\"self\" href=\"https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCzNWVDZQ55bjq8uILZ7_wyQ\"/><title>YouTube video feed</title><updated>2021-07-19T15:40:45.613264165+00:00</updated><entry>\n  <id>yt:video:KXjiJpsl3d8</id>\n  <yt:videoId>KXjiJpsl3d8</yt:videoId>\n  <yt:channelId>UCzNWVDZQ55bjq8uILZ7_wyQ</yt:channelId>\n  <title>SEX EDUCATION Season 3 Teaser (2021)</title>\n  <link rel=\"alternate\" href=\"https://www.youtube.com/watch?v=KXjiJpsl3d8\"/>\n  <author>\n   <name>FRESH Movie Trailers</name>\n   <uri>https://www.youtube.com/channel/UCzNWVDZQ55bjq8uILZ7_wyQ</uri>\n  </author>\n  <published>2021-07-19T15:40:30+00:00</published>\n  <updated>2021-07-19T15:40:45.613264165+00:00</updated>\n </entry></feed>\n",
        "form": {},
        "json": null
    }
```

Data XML/Atom feed:
```xml
    <feed xmlns="http://www.w3.org/2005/Atom" xmlns:yt="http://www.youtube.com/xml/schemas/2015">
     <link href="https://pubsubhubbub.appspot.com" rel="hub"/>
     <link href="https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCzNWVDZQ55bjq8uILZ7_wyQ" rel="self"/>
     <title>YouTube video feed</title>
     <updated>2021-07-19T15:40:45.613264165+00:00</updated>
     <entry>
      <id>yt:video:KXjiJpsl3d8</id>
      <yt:videoid>KXjiJpsl3d8</yt:videoid>
      <yt:channelid>UCzNWVDZQ55bjq8uILZ7_wyQ</yt:channelid>
      <title>SEX EDUCATION Season 3 Teaser (2021)</title>
      <link href="https://www.youtube.com/watch?v=KXjiJpsl3d8" rel="alternate"/>
      <author>
       <name>FRESH Movie Trailers</name>
       <uri>https://www.youtube.com/channel/UCzNWVDZQ55bjq8uILZ7_wyQ</uri>
      </author>
      <published>2021-07-19T15:40:30+00:00</published>
      <updated>2021-07-19T15:40:45.613264165+00:00</updated>
     </entry>
    </feed>
```

## /api/subscriptions [GET]
Gets JSON list of current subscriptions.

### Example:
```json
{
  'UCzNWVDZQ55bjq8uILZ7_wyQ': {
    'channel_id': 'UCzNWVDZQ55bjq8uILZ7_wyQ', 
    'added_on': datetime.datetime(2021, 7, 19, 15, 28, 33, 651472), 
    'last_modified': datetime.datetime(2021, 7, 19, 15, 40, 51, 849221), 
    'subscribed': True, 
    'hmac_secret': None
  }, 
  'UCWOA1ZGywLbqmigxE4Qlvuw': {
    'channel_id': 'UCWOA1ZGywLbqmigxE4Qlvuw', 
    'added_on': datetime.datetime(2021, 7, 20, 13, 18, 39, 762758), 
    'last_modified': datetime.datetime(2021, 7, 20, 13, 18, 39, 763258), 
    'subscribed': True, 
    'hmac_secret': None
  }
}
```
