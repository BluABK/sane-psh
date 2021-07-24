import datetime
import unittest

from werkzeug.datastructures import ImmutableMultiDict

# NB: This *MUST* be imported before any database modules, else config overrides fail.
import tests.setup
from database.models.channel import Channel

from handlers.log_handler import create_logger
from database import init_db
from database.operations import get_channel, add_row
from api.routes.notifications import handle_get
from tests.test_utils import assert_dict, asserted_db_wipe

CONFIG = tests.setup.CONFIG


class FakeGETRequest:
    def __init__(self, args: ImmutableMultiDict):
        self.args = args


class TestSubscriptionRequest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = create_logger(__name__)
        self.cb_dict = {}
        self.CHANNEL_ID = "UCLozjflf3i84bu_2jLTK2rA"
        self.CHANNEL_TITLE = "BluABK~"
        self.PUBLISHED_ON = datetime.datetime(2020, 5, 1, 17, 3, 45)
        self.UPDATED_ON = datetime.datetime(2020, 5, 1, 17, 4, 2, 426578)
        self.LEASE_SECONDS = 432000

    def setUp(self):
        """Hook method for setting up the test fixture before exercising it."""
        # Setup DB
        init_db()

        # Wipe DB
        asserted_db_wipe(self)

    def tearDown(self):
        """Hook method for deconstructing the test fixture after testing it."""
        # Wipe DB
        asserted_db_wipe(self)

    def test_subscribe_request(self):
        expected = {
            "channel_id": self.CHANNEL_ID,
            "subscribed": True,
        }

        req = FakeGETRequest(
            args=ImmutableMultiDict(
                [
                    ('hub.topic', 'https://www.youtube.com/xml/feeds/videos.xml?channel_id={}'.format(self.CHANNEL_ID)),
                    ('hub.challenge', '3613557208738996482'),
                    ('hub.mode', 'subscribe'),
                    ('hub.lease_seconds', str(self.LEASE_SECONDS)),
                    ('hub.verify_token', CONFIG["verification_token"])
                 ]
            )
        )

        handle_get(req)

        actual = get_channel(self.CHANNEL_ID)
        relevant_test_results = {
            "channel_id": actual["channel_id"],
            "subscribed": actual["subscribed"]
        }

        assert_dict(self, expected, relevant_test_results)

    def test_unsubscribe_request(self):
        # Set up DB:
        add_row(
            Channel(channel_id=self.CHANNEL_ID,
                    subscribed=True,
                    expires_on=datetime.datetime.now() + datetime.timedelta(0, self.LEASE_SECONDS)
                    )
        )

        expected = {
            "channel_id": self.CHANNEL_ID,
            "subscribed": False
        }

        req = FakeGETRequest(
            args=ImmutableMultiDict(
                [('hub.topic', 'https://www.youtube.com/xml/feeds/videos.xml?channel_id={}'.format(self.CHANNEL_ID)),
                 ('hub.challenge', '17674212813144385002'), ('hub.mode', 'unsubscribe'),
                 ('hub.verify_token', CONFIG["verification_token"])])
        )

        handle_get(req)

        actual = get_channel(self.CHANNEL_ID)
        relevant_test_results = {
            "channel_id": actual["channel_id"],
            "subscribed": actual["subscribed"]
        }

        assert_dict(self, expected, relevant_test_results)
