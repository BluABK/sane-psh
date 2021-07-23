import sys
import os
import json
import datetime
from datetime import timezone

from handlers.log_handler import create_logger

log = create_logger(__name__)


def console_log(s, **kwargs):
    datetime_stamp_human_readable = datetime.datetime.now(timezone.utc).isoformat().replace('T', ' ').split('+')[0]
    print("[{dt}] {data}".format(dt=datetime_stamp_human_readable, data=s), **kwargs)


def log_all_info(s):
    log.info(s)
    console_log(s)


def log_all_error(s):
    log.error(s)
    console_log(s, file=sys.stderr)


def list_item_types_equal(li: list, t: type):
    for item in li:
        if type(item) is not t:
            return False

    return True


def pp_dict(d, indent_lvl=0, indent_str='    ', suffix_last_item=None):
    for key in d:
        if type(d[key]) is dict:
            print("{key}: ".format(key=repr(key)))
            pp_dict(d[key], indent_lvl=indent_lvl + 1)
        else:
            # Handle dicts within lists.
            if type(d[key]) is list and list_item_types_equal(d[key], dict):
                print("{key}: [".format(key=repr(key)))
                for item in d[key]:
                    # Suffix ternary: Only gets set if list has more than one item, to avoid confusing separators.
                    pp_dict(item, indent_lvl=indent_lvl + 1, suffix_last_item=',' if len(d[key]) > 1 else None)
                # Indent list close bracket to match indented list items (i.e. thus the +1).
                print("{indent}]".format(indent=(indent_lvl + 1) * indent_str))
            else:
                # Add suffix to last item in list if suffix is set.
                if key == list(d.keys())[-1] and suffix_last_item is not None:
                    print("{indent}{key}: {value}{suffix}".format(indent=indent_lvl * indent_str, key=repr(key),
                                                                  value=repr(d[key]), suffix=suffix_last_item))
                else:
                    print("{indent}{key}: {value}".format(indent=indent_lvl * indent_str, key=repr(key),
                                                          value=repr(d[key])))


def dict_to_pretty_string(d: dict, indent_lvl=0, indent_str='    ', suffix_last_item=None) -> str:
    s = ""
    for key in d:
        if type(d[key]) is dict:
            s += ("{key}: \n".format(key=repr(key)))
            dict_to_pretty_string(d[key], indent_lvl=indent_lvl + 1)
        else:
            # Handle dicts within lists.
            if type(d[key]) is list and list_item_types_equal(d[key], dict):
                s += "{key}: [\n".format(key=repr(key))
                for item in d[key]:
                    # Suffix ternary: Only gets set if list has more than one item, to avoid confusing separators.
                    dict_to_pretty_string(item, indent_lvl=indent_lvl + 1, suffix_last_item=',' if len(d[key]) > 1 else None)
                # Indent list close bracket to match indented list items (i.e. thus the +1).
                s += "{indent}]\n".format(indent=(indent_lvl + 1) * indent_str)
            else:
                # Add suffix to last item in list if suffix is set.
                if key == list(d.keys())[-1] and suffix_last_item is not None:
                     s += "{indent}{key}: {value}{suffix}\n".format(indent=indent_lvl * indent_str, key=repr(key),
                                                                    value=repr(d[key]), suffix=suffix_last_item)
                else:
                    s += "{indent}{key}: {value}\n".format(indent=indent_lvl * indent_str, key=repr(key),
                                                           value=repr(d[key]))
    return s


def datetime_ns_to_ms(dt: str) -> str:
    """
    Converts a datetime with nanoseconds to a datetime with milliseconds.

    :param dt:
    :return:
    """
    lhs, rhs = dt.split('.')
    offset = rhs.split('+')[1]
    ms = rhs.split('+')[0][:6]

    return "{}+{}".format(".".join([lhs, ms]), offset)


def datetime_ns_to_ms_str(dt: str, fmt: str) -> str:
    return datetime.datetime.strptime(datetime_ns_to_ms(dt), fmt).strftime(fmt)


def check_required_args(request_args: list, required_keys: list):
    for key in required_keys:
        if key not in request_args:
            return {"result": False, "arg": key}

    return {"result": True, "arg": None}


def log_request(request, logger=log.info):
    req_info = {
        "path": request.path,
        "headers": {k: v for k, v in request.headers.items()},
        "args": request.args,
        "data": request.data.decode("utf-8"),
        "form": request.form,
        "json": request.json}

    logger("Request: {method} {path} (Content-Type: '{cnt_type}') {from_hdr}\n{req_info}".format(
        method=request.method,
        path=req_info["path"],
        from_hdr="From: {}".format(req_info["headers"]["From"]) if "From" in req_info["headers"] else "",
        cnt_type="({})".format(req_info["headers"]["Content-Type"]) if "Content-Type" in req_info["headers"] else "",
        req_info=json.dumps(req_info, indent=4)))
