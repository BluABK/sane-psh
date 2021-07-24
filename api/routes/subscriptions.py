from flask import make_response, request, jsonify
import requests

from handlers.config_handler import CONFIG
from handlers.log_handler import create_logger
from utils import log_request
from database.operations import get_channels, get_videos

log = create_logger(__name__)


def make_hub_subscription_request(channel_id, mode):
    """

    https://pubsubhubbub.github.io/PubSubHubbub/pubsubhubbub-core-0.4.html#rfc.section.5.1
    :return:
    """
    if CONFIG["notifications_callback"] == "":
        raise ValueError("Required config option 'notifications_callback' has been left blank!")

    # Set (required) headers.
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Set required args.
    args = {
        "hub.callback": CONFIG["notifications_callback"],
        "hub.verify": CONFIG["hub_verify_mode"],
        "hub.mode": mode,
        "hub.topic": "{videos_feed}?channel_id={channel_id}".format(
            videos_feed=CONFIG["youtube_video_feed"], channel_id=channel_id),
    }

    # Set optional args.
    if CONFIG["require_verification_token"] is True:
        args["hub.verify_token"] = CONFIG["verification_token"]
    if CONFIG["require_hmac_authentication"] is True:
        args["hub.secret"] = CONFIG["hmac_secret"]

    # Make request.
    log.info("Making hub subscription POST request (mode: {mode}) for channel ID: {channel_id}".format(
        channel_id=channel_id, mode=mode))
    req = requests.post(CONFIG["hub_url"], data=None, json=None, params=args, headers=headers)
    log.debug("Request dict:\n{}".format(req.__dict__))

    log.info("Received {method} request response {code} ({reason}){server} "
             "in {elapsed} for channel ID: {channel_id}".format(
                method=req.request.method.upper(),
                server=" from server '{}'".format(req.headers.get("Server")) if "Server" in req.headers.keys() else "",
                elapsed=str(req.elapsed),
                reason=req.reason,
                code=req.status_code,
                channel_id=channel_id))

    return req


def subscribe():
    log_request(request)

    if 'id' in request.args:
        channel_ids = request.args.getlist('id')[0].split(',')
        log.info("Subscribe to channel IDs: {}".format(channel_ids))
        for channel_id in channel_ids:
            try:
                req = make_hub_subscription_request(channel_id, "subscribe")
                # The hub MUST respond to a subscription request with an HTTP [RFC2616] 202 "Accepted" response
                # to indicate that the request was received and will now be verified (Section 5.3) and validated
                # (Section 5.2) by the hub
                if req.status_code != 202:
                    err_msg = "Hub Error: Expected status code: 202, got: {wrong_code}.".format(wrong_code=req.status_code)
                    log.error(err_msg)
                    return make_response(err_msg, 500)
            except Exception as exc:
                log.exception(exc)
                return make_response(str(exc), 500)

        log.info("Subscription request processed for channel IDs: {}".format(channel_ids))
        return jsonify(channel_ids)

    return make_response("Missing required argument: id", 400)


def unsubscribe():
    log_request(request)

    if 'id' in request.args:
        channel_ids = request.args.getlist('id')[0].split(',')
        log.info("Unsubscribe from channel IDs: {}".format(channel_ids))
        for channel_id in channel_ids:
            try:
                req = make_hub_subscription_request(channel_id, "unsubscribe")
                # The hub MUST respond to a subscription request with an HTTP [RFC2616] 202 "Accepted" response
                # to indicate that the request was received and will now be verified (Section 5.3) and validated
                # (Section 5.2) by the hub
                if req.status_code != 202:
                    err_msg = "Hub Error: Expected status code: 202, got: {wrong_code}.".format(wrong_code=req.status_code)
                    log.error(err_msg)
                    return make_response(err_msg, 500)
            except Exception as exc:
                log.exception(exc)
                return make_response(str(exc), 500)

        log.info("Subscription request processed for channel IDs: {}".format(channel_ids))
        return jsonify(channel_ids)

    return make_response("Missing required argument: id", 400)


def list_subscriptions(stringify_datetime=True):
    subscriptions_list = get_channels(stringify_datetime)

    log_request(request)

    log.info("List subscriptions request processed")
    log.debug(subscriptions_list)

    return jsonify(subscriptions_list)
