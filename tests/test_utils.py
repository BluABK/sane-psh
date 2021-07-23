import unittest

# FIXME: Add handling for UTC offset (need to remove the ':')
FEED_UPDATED_FMT = "%Y-%m-%dT%H:%M:%S.%f+00:00"
FEED_PUBLISHED_FMT = "%Y-%m-%dT%H:%M:%S+00:00"
FEED_DELETED_FMT = FEED_PUBLISHED_FMT


def assert_dict(test_case: unittest.TestCase, test_dict, correct_dict, msg=None):
    # Assert that dicts have same length.
    test_case.assertEqual(len(test_dict), len(correct_dict))

    for key in test_dict:
        if type(test_dict[key]) is dict:
            # If value is dict, recurse further down.
            assert_dict(test_case, test_dict[key], correct_dict[key])
        else:
            # Assert that values are equal.
            test_case.assertEqual(test_dict[key], correct_dict[key])

    if msg:
        test_case.assertTrue(True, msg)
