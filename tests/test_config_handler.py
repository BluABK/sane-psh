import json
import unittest

from handlers.config_handler import load_config, DEFAULT_CONFIG
import settings


class TestConfigHandler(unittest.TestCase):

    def assert_dict(self, test_dict, correct_dict):
        self.assertEqual(len(test_dict), len(correct_dict))

        for key in test_dict:
            if type(test_dict[key]) is dict:
                self.assert_dict(test_dict[key], correct_dict[key])
            else:
                self.assertEqual(test_dict[key], correct_dict[key])

    def test_custom_config_file_load(self):
        self.config = load_config(settings.TEST_CONFIG_FILE_PATH)

        with open(settings.TEST_CONFIG_FILE_PATH, 'r') as f:
            self.test_config_json = json.load(f)

            for key, value in self.test_config_json.items():
                if key in DEFAULT_CONFIG:
                    # Make sure the changed options actually differ from default.
                    self.assertNotEqual(value, DEFAULT_CONFIG[key])

                    # Make sure the changed option is actually set in the config.
                    self.assertEqual(value, self.config[key])


if __name__ == '__main__':
    unittest.main()
