import datetime
import os
import json
import unittest

from bs4 import BeautifulSoup

# Setup tests (loads custom config, sets up DB etc..).
# NB: This *MUST* be imported before any database modules, else config overrides fail.
# noinspection PyUnresolvedReferences
import tests.setup
from database.models.video import Video
from tests.test_utils import assert_dict, FEED_PUBLISHED_FMT, asserted_db_wipe

from handlers.log_handler import create_logger

from database import init_db
from database.operations import db_is_empty, wipe_db, add_row, get_video
from utils import log_all_info
from api.routes.notifications import handle_deleted_entry
import settings


XML_FILEPATH = str(settings.TEST_DATA_PATH.joinpath('deleted_entry.xml'))


class TestDeletedEntry(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = create_logger(__name__)
        self.cb_dict = {}

        self.CHANNEL_ID = "UCLozjflf3i84bu_2jLTK2rA"
        self.CHANNEL_TITLE = "BluABK~"
        self.VIDEO_ID = "qX0wVo5GE6A"
        self.VIDEO_TITLE = "Test video (ignore me)"
        self.PUBLISHED_ON = datetime.datetime(2020, 5, 1, 16, 58, 14)
        self.UPDATED_ON = datetime.datetime(2020, 5, 1, 17, 4, 2, 426578)

    def setUp(self):
        """Hook method for setting up the test fixture before exercising it."""
        # Setup DB
        init_db()

        # Wipe DB
        asserted_db_wipe(self)

        # Write video to DB.
        add_row(
            Video(video_id=self.VIDEO_ID,
                  channel_id=self.CHANNEL_ID,
                  video_title=self.VIDEO_TITLE,
                  published_on=self.PUBLISHED_ON,
                  updated_on=self.UPDATED_ON
                  )
        )
        video = get_video(self.VIDEO_ID)
        self.assertIsInstance(video, dict, "get_video returned a dict.")

        if video:
            # Omit added on and last modified which will never match a preset expected dict.
            video.pop('added_on')
            video.pop('last_modified')

        expected_video = {
            'video_id': self.VIDEO_ID,
            'channel_id': self.CHANNEL_ID,
            'video_title': self.VIDEO_TITLE,
            'published_on': self.PUBLISHED_ON,
            'updated_on': self.UPDATED_ON
        }
        log_all_info(video)

        # Assert that get_video returns dict that matches expected dict.
        for key, value in zip(video, expected_video):
            self.assertEqual(video[key], expected_video[key],
                             "key '{}' in video (from get_video) matches expected value '{}'.".format(
                                 key, expected_video[key]))

        # assert_dict(self, video, expected_video, "get_video returns dict that matches expected dict.")

    def tearDown(self):
        """Hook method for deconstructing the test fixture after testing it."""
        # Wipe DB
        asserted_db_wipe(self)

    def test_deleted_entry(self):
        with open(XML_FILEPATH, 'r') as f:
            xml = BeautifulSoup(f.read(), "lxml")
            # xml = BeautifulSoup(f.read(), features="xml")

        expected_result = {
            'deleted_entry': {
                "ref": "yt:video:{}".format(self.VIDEO_ID),
                "when": self.PUBLISHED_ON.strftime(FEED_PUBLISHED_FMT),
                "link": {"href": "https://www.youtube.com/watch?v={}".format(self.VIDEO_ID)},
                "kind": "delete"
            },
            "by": {
                "name": self.CHANNEL_TITLE,
                "uri": "https://www.youtube.com/channel/{}".format(self.CHANNEL_ID)
            }
        }

        test_result = handle_deleted_entry(xml)
        log_all_info("Deleted: {video_id}".format(video_id=test_result["deleted_entry"]["ref"].split(':')[-1]))

        assert_dict(self, test_result, expected_result, "Handled kind:delete XML is as expected.")

        self.assertIsNone(get_video(self.VIDEO_ID), "Assert that video was deleted from DB.")

