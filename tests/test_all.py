import unittest

from database import init_db
from tests.test_published_video import TestPublishedVideo
from tests.test_deleted_entry import TestDeletedEntry


def suite():
    my_suite = unittest.TestSuite()
    my_suite.addTest(TestPublishedVideo('test_published_video'))
    my_suite.addTest(TestDeletedEntry('test_deleted_entry'))
    return my_suite


if __name__ == '__main__':
    init_db()
    runner = unittest.TextTestRunner()
    runner.run(suite())
