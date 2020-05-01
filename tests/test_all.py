import unittest
from tests.test_published_video import TestPublishedVideo


def suite():
    my_suite = unittest.TestSuite()
    my_suite.addTest(TestPublishedVideo('test_published_video'))
    return my_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
