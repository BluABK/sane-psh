import unittest
import os

# NB: This *MUST* be imported before any database modules, else config overrides fail.
# noinspection PyUnresolvedReferences
import tests.setup.apply_test_settings

from database import init_db
from handlers.config_handler import load_config
from tests.test_published_video import TestPublishedVideo
from tests.test_deleted_entry import TestDeletedEntry
from tests.test_subscription_request import TestSubscriptionRequest
from tests.test_config_handler import TestConfigHandler

is_travis = 'TRAVIS' in os.environ


def suite():
    my_suite = unittest.TestSuite()
    if not is_travis:
        my_suite.addTest(TestConfigHandler('test_custom_config_file_load'))
    my_suite.addTest(TestPublishedVideo('test_published_video'))
    my_suite.addTest(TestDeletedEntry('test_deleted_entry'))
    my_suite.addTest(TestSubscriptionRequest('test_subscribe_request'))
    my_suite.addTest(TestSubscriptionRequest('test_unsubscribe_request'))
    return my_suite


if __name__ == '__main__':
    config = load_config()
    init_db()
    runner = unittest.TextTestRunner()
    runner.run(suite())
