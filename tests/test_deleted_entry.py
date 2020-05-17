import unittest

from bs4 import BeautifulSoup

# NB: This *MUST* be imported before any database modules, else config overrides fail.
# noinspection PyUnresolvedReferences
from tests.setup import apply_test_settings

from handlers.log_handler import create_logger

from database import init_db
from utils import log_all_info
from api.routes.notifications import handle_deleted_entry
import settings

XML_FILEPATH = str(settings.TEST_DATA_PATH.joinpath('deleted_entry.xml'))


class TestDeletedEntry(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.log = create_logger(__name__)
        self.cb_dict = {}

    def assert_dict(self, test_dict, correct_dict):
        self.assertEqual(len(test_dict), len(correct_dict))

        for key in test_dict:
            if type(test_dict[key]) is dict:
                self.assert_dict(test_dict[key], correct_dict[key])
            else:
                self.assertEqual(test_dict[key], correct_dict[key])

    def test_deleted_entry(self):
        with open(XML_FILEPATH, 'r') as f:
            xml = BeautifulSoup(f.read(), "lxml")
            # xml = BeautifulSoup(f.read(), features="xml")

        expected_result = {
            'deleted_entry': {
                "ref": "yt:video:qX0wVo5GE6A",
                "when": "2020-05-01T16:58:14+00:00",
                "link": {"href": "https://www.youtube.com/watch?v=qX0wVo5GE6A"},
                "kind": "delete"
            },
            "by": {
                "name": "BluABK~",
                "uri": "https://www.youtube.com/channel/UCLozjflf3i84bu_2jLTK2rA"
            }
        }

        test_result = handle_deleted_entry(xml)
        log_all_info("Deleted: {video_id}".format(video_id=test_result["deleted_entry"]["ref"].split(':')[-1]))

        self.assert_dict(test_result, expected_result)


if __name__ == '__main__':
    init_db()
    unittest.main()
