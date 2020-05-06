import json
import unittest

from database import init_db
from tests.test_published_video import TestPublishedVideo
from tests.test_deleted_entry import TestDeletedEntry
from tests.test_subscription_request import TestSubscriptionRequest

from globals import CONFIG_PATH

API_VERSION = 1
API_BASEROUTE = '/api'


with open(CONFIG_PATH, 'r') as f:
    CONFIG = json.load(f)


def suite():
    my_suite = unittest.TestSuite()
    my_suite.addTest(TestPublishedVideo('test_published_video'))
    my_suite.addTest(TestDeletedEntry('test_deleted_entry'))
    my_suite.addTest(TestSubscriptionRequest('test_subscribe_request'))
    my_suite.addTest(TestSubscriptionRequest('test_unsubscribe_request'))
    return my_suite


if __name__ == '__main__':
    init_db()
    runner = unittest.TextTestRunner()
    runner.run(suite())
