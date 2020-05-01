import os
import unittest

from bs4 import BeautifulSoup

from main import handle_deleted_entry
from utils import pp_dict

XML_FILEPATH = 'dumps/deleted_entry.xml'


class TestDeletedEntry(unittest.TestCase):
    cb_dict = {}

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
                "ref": "yt:video:NqgaGLL508c",
                "when": "2020-05-01T16:58:14+00:00",
                "link": {"href": "https://www.youtube.com/watch?v=NqgaGLL508c"}
            },
            "by": {
                "name": "BluABK~",
                "uri": "https://www.youtube.com/channel/UCLozjflf3i84bu_2jLTK2rA"
            }
        }

        test_result = handle_deleted_entry(xml)

        self.assert_dict(test_result, expected_result)


if __name__ == '__main__':
    # Workaround for unreliable CWD:
    # When running test_all.py CWD is suddenly this dir, not project root,
    # but when running this test stand-alone CWD is project root.
    XML_FILEPATH = os.path.join('tests', XML_FILEPATH)
    unittest.main()
