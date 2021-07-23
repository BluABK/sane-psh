import datetime
import unittest

from bs4 import BeautifulSoup

# NB: This *MUST* be imported before any database modules, else config overrides fail.
# noinspection PyUnresolvedReferences
import tests.setup


from handlers.log_handler import create_logger
from database.models.video import Video
import settings
from database import init_db
from database.operations import wipe_db, db_is_empty
from api.routes.notifications import handle_video, handled_video_to_string
from tests.test_utils import FEED_PUBLISHED_FMT, FEED_UPDATED_FMT, assert_dict, asserted_db_wipe
from utils import log_all_info, datetime_ns_to_ms_str

CONFIG = tests.setup.CONFIG
XML_FILEPATH = str(settings.TEST_DATA_PATH.joinpath('published_video.xml'))


class TestPublishedVideo(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = create_logger(__name__)
        self.cb_dict = {}

        self.CHANNEL_ID = "UCLozjflf3i84bu_2jLTK2rA"
        self.CHANNEL_TITLE = "BluABK~"
        self.VIDEO_ID = "qX0wVo5GE6A"
        self.VIDEO_TITLE = "Test video (ignore me)"
        self.PUBLISHED_ON = datetime.datetime(2020, 5, 1, 17, 3, 45)
        self.UPDATED_ON = datetime.datetime(2020, 5, 1, 17, 4, 2, 426578)

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

    def test_published_video(self):
        with open(XML_FILEPATH, 'r') as f:
            xml = BeautifulSoup(f.read(), "lxml")

        expected = {
            'links': [{'href': 'https://pubsubhubbub.appspot.com', 'rel': ['hub']},
                      {'href': 'https://www.youtube.com/xml/feeds/videos.xml?channel_id={}'.format(self.CHANNEL_ID),
                       'rel': ['self']},
                      {'href': 'https://www.youtube.com/watch?v={}'.format(self.VIDEO_ID), 'rel': ['alternate']}],
            'title': 'YouTube video feed',
            'updated': self.UPDATED_ON.strftime(FEED_UPDATED_FMT),
            'entry': {
                'id': 'yt:video:{}'.format(self.VIDEO_ID),
                'video_id': self.VIDEO_ID,
                'channel_id': self.CHANNEL_ID,
                'video_title': self.VIDEO_TITLE,
                'links': [{'href': 'https://www.youtube.com/watch?v={}'.format(self.VIDEO_ID), 'rel': ['alternate']}],
                'channel_title': self.CHANNEL_TITLE,
                'channel_uri': 'https://www.youtube.com/channel/{}'.format(self.CHANNEL_ID),
                'published': self.PUBLISHED_ON.strftime(FEED_PUBLISHED_FMT),
                'updated': self.UPDATED_ON.strftime(FEED_UPDATED_FMT),
                'kind': 'new'
                }
             }

        actual = handle_video(xml)

        # Convert nanoseconds to milliseconds for datetime compatibility
        actual["updated"] = datetime_ns_to_ms_str(actual["updated"], FEED_UPDATED_FMT)
        actual["entry"]["updated"] = datetime_ns_to_ms_str(actual["entry"]["updated"], FEED_UPDATED_FMT)

        self.log.info(handled_video_to_string(actual))

        assert_dict(self, expected, actual, "Handled kind:new XML is as expected.")

