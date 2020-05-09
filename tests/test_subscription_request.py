import json
import os
import pathlib
import unittest

from werkzeug.datastructures import ImmutableMultiDict

# NB: This *MUST* be imported before any database modules, else config overrides fail.
# noinspection PyUnresolvedReferences
from tests.setup import apply_test_settings


from handlers.log_handler import create_logger
from database import init_db
from database.operations import get_channel
from handlers.config_handler import CONFIG
import settings
from main import handle_get

XML_FILEPATH = str(settings.TEST_DATA_PATH.joinpath('published_video.xml'))


class FakeGetRequest:
    def __init__(self, args: ImmutableMultiDict):
        self.args = args


class TestSubscriptionRequest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = create_logger(__name__)
        self.cb_dict = {}
        self.channel_id = "UCLozjflf3i84bu_2jLTK2rA"

    def assert_dict(self, test_dict, correct_dict):
        self.assertEqual(len(test_dict), len(correct_dict))

        for key in test_dict:
            if type(test_dict[key]) is dict:
                self.assert_dict(test_dict[key], correct_dict[key])
            else:
                self.assertEqual(test_dict[key], correct_dict[key])

    def test_subscribe_request(self):
        expected_result = {
            "channel_id": self.channel_id,
            "subscribed": True,
            "hmac_secret": None
        }

        req = FakeGetRequest(
            args=ImmutableMultiDict(
                [('hub.topic', 'https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCLozjflf3i84bu_2jLTK2rA'),
                 ('hub.challenge', '3613557208738996482'), ('hub.mode', 'subscribe'), ('hub.lease_seconds', '432000'),
                 ('hub.verify_token', CONFIG["verification_token"])])
        )

        handle_get(req)

        test_result = get_channel(self.channel_id)
        relevant_test_results = {
            "channel_id": test_result["channel_id"],
            "subscribed": test_result["subscribed"],
            "hmac_secret": test_result["hmac_secret"]
        }

        self.assert_dict(relevant_test_results, expected_result)

    def test_unsubscribe_request(self):
        expected_result = {
            "channel_id": self.channel_id,
            "subscribed": False,
            "hmac_secret": None
        }

        req = FakeGetRequest(
            args=ImmutableMultiDict(
                [('hub.topic', 'https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCLozjflf3i84bu_2jLTK2rA'),
                 ('hub.challenge', '17674212813144385002'), ('hub.mode', 'unsubscribe'),
                 ('hub.verify_token', CONFIG["verification_token"])])
        )

        handle_get(req)

        test_result = get_channel(self.channel_id)
        relevant_test_results = {
            "channel_id": test_result["channel_id"],
            "subscribed": test_result["subscribed"],
            "hmac_secret": test_result["hmac_secret"]
        }

        self.assert_dict(relevant_test_results, expected_result)


if __name__ == '__main__':
    init_db()
    unittest.main()
