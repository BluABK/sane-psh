from flask import make_response, request, jsonify
import requests

from database.models.video import Video
from handlers.log_handler import create_logger
from utils import log_request
from database.operations import get_videos

log = create_logger(__name__)


def list_videos(stringify_datetime=True):
    sort_by_col = "published_on"
    order_descending = True

    log_request(request)

    video_dict_keys = Video.__table__.columns.keys()

    if "sort" in request.args:
        if request.args["sort"] in video_dict_keys:
            sort_by_col = request.args["sort"]
        else:
            return make_response("'sort' argument must be one of {}!".format(",".join(video_dict_keys)), 400)

    if "order" in request.args:
        if request.args["order"] == "asc":
            order_descending = False
        elif request.args["order"] == "desc":
            order_descending = True
        else:
            return make_response("'order' argument must be 'asc' or 'desc'!",  400)

    videos_list = get_videos(stringify_datetime, sort_by_col=sort_by_col, order_descending=order_descending)

    log.info("List videos request processed")
    log.debug(videos_list)

    return jsonify(videos_list)
