import unittest

from bs4 import BeautifulSoup

# NB: This *MUST* be imported before any database modules, else config overrides fail.
# noinspection PyUnresolvedReferences
from tests.setup import apply_test_settings


from handlers.log_handler import create_logger
from database.models.video import Video
import settings
from database import init_db
from database.operations import del_row_by_filter, row_exists
from main import handle_video, console_log_handled_video

XML_FILEPATH = str(settings.TEST_DATA_PATH.joinpath('published_video.xml'))


class TestPublishedVideo(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = create_logger(__name__)
        self.video_id = "qX0wVo5GE6A"
        self.cb_dict = {}

    def assert_dict(self, test_dict, correct_dict):
        self.assertEqual(len(test_dict), len(correct_dict))

        for key in test_dict:
            if type(test_dict[key]) is dict:
                self.assert_dict(test_dict[key], correct_dict[key])
            else:
                self.assertEqual(test_dict[key], correct_dict[key])

    def delete_video_if_exist(self):
        """
        Delete video from DB if it exists, to avoid polluting the test.
        :return:
        """
        if row_exists(Video, video_id=self.video_id):
            # Delete video from DB as it was deleted on YouTube's end.
            del_row_by_filter(Video, video_id=self.video_id)
            self.log.warning("Deleted existing video entry for: {}.".format(self.video_id))
            self.log.warning("Test environment/DB seems unclean!")

    def test_published_video(self):
        self.delete_video_if_exist()

        with open(XML_FILEPATH, 'r') as f:
            xml = BeautifulSoup(f.read(), "lxml")
            # xml = BeautifulSoup(f.read(), features="xml")

        expected_result = {
            'links': [{'href': 'https://pubsubhubbub.appspot.com', 'rel': ['hub']},
                      {'href': 'https://www.youtube.com/xml/feeds/videos.xml?channel_id=UCLozjflf3i84bu_2jLTK2rA',
                       'rel': ['self']},
                      {'href': 'https://www.youtube.com/watch?v=qX0wVo5GE6A', 'rel': ['alternate']}],
            'title': 'YouTube video feed', 'updated': '2020-05-01T17:04:02.426578815+00:00',
            'entry': {
                'id': 'yt:video:qX0wVo5GE6A',
                'video_id': self.video_id,
                'channel_id': 'UCLozjflf3i84bu_2jLTK2rA',
                'video_title': 'Test video (ignore me)',
                'links': [{'href': 'https://www.youtube.com/watch?v=qX0wVo5GE6A', 'rel': ['alternate']}],
                'channel_title': 'BluABK~',
                'channel_uri': 'https://www.youtube.com/channel/UCLozjflf3i84bu_2jLTK2rA',
                'published': '2020-05-01T17:03:45+00:00',
                'updated': '2020-05-01T17:04:02.426578815+00:00',
                'kind': 'new'
                }
             }

        test_result = handle_video(xml)
        console_log_handled_video(test_result)

        self.assert_dict(test_result, expected_result)


if __name__ == '__main__':
    init_db()
    unittest.main()
