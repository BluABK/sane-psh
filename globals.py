import os
import pathlib

# Get directory this file resides in (should be the project root directory).
PROJECT_ROOT_DIR = pathlib.Path(__file__).parent.absolute()
DATABASE_FILENAME = 'sane-psh.db'
DATABASE_PATH = PROJECT_ROOT_DIR.joinpath(DATABASE_FILENAME)
TEST_DATA_PATH = PROJECT_ROOT_DIR.joinpath('tests').joinpath('data')
