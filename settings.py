import os
import pathlib

# Get directory this file resides in (should be the project root directory).
PROJECT_ROOT_DIR = pathlib.Path(__file__).parent.absolute()
DATABASE_FILENAME = 'sane-psh.db'
DATABASE_PATH = PROJECT_ROOT_DIR.joinpath(DATABASE_FILENAME)
CONFIG_PATH = PROJECT_ROOT_DIR.joinpath('config.json')
SAMPLE_CONFIG_PATH = PROJECT_ROOT_DIR.joinpath('config.json.sample')
LOG_DIR = PROJECT_ROOT_DIR.joinpath('logs')
LOG_FILE = LOG_DIR.joinpath('sane-psh.log')

API_VERSION = 1
API_BASEROUTE = '/api'

TEST_DATABASE_FILENAME = 'test.db'
TEST_DATABASE_PATH = PROJECT_ROOT_DIR.joinpath(TEST_DATABASE_FILENAME)
TEST_PATH = PROJECT_ROOT_DIR.joinpath('tests')
TEST_DATA_PATH = TEST_PATH.joinpath('data')
TEST_CONFIG_PATH = TEST_PATH.joinpath('config')
TEST_CONFIG_FILE_PATH = TEST_CONFIG_PATH.joinpath('test_config.json')

