# import json
import unittest

from database.operations import wipe_db, db_is_empty
from handlers.log_handler import create_logger

log = create_logger(__name__)

# FIXME: Add handling for UTC offset (need to remove the ':')
FEED_UPDATED_FMT = "%Y-%m-%dT%H:%M:%S.%f+00:00"
FEED_PUBLISHED_FMT = "%Y-%m-%dT%H:%M:%S+00:00"
FEED_DELETED_FMT = FEED_PUBLISHED_FMT


def assert_dict(test_case: unittest.TestCase, expected: dict, actual: dict, msg=None):
    # Assert that dicts have same length.
    test_case.assertEqual(len(expected), len(actual))
    # log.debug2(json.dumps(expected, indent=4))
    # log.debug2(json.dumps(actual, indent=4))

    for key in actual:
        if type(actual[key]) is dict:
            # If value is dict, recurse further down.
            log.debug("Recursing into dict in key '{}'...".format(key))
            assert_dict(test_case, expected[key], actual[key])
        else:
            # Assert that values are equal.
            log.debug("Assert expected == actual [{key}]: '{exp_val}' == '{test_val}'".format(
                key=key, test_val=actual[key], exp_val=expected[key]))
            test_case.assertEqual(expected[key], actual[key])

    if msg:
        test_case.assertTrue(True, msg)


def asserted_db_wipe(test_case: unittest.TestCase):
    # Wipe DB
    test_case.assertTrue(wipe_db(), "DB successfully wiped.")
    # Check that DB was wiped successfully.
    test_case.assertTrue(db_is_empty(), "DB is empty.")