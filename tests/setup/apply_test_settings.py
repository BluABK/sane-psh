import platform

from handlers import config_handler
import settings

# Load test config.
config_handler.load_config(config_file=settings.TEST_CONFIG_FILE_PATH)

if platform.system() == "Windows":
    # As Windows doesn't have the concept of root and instead uses drives,
    # you have to specify absolute path with 3 slashes (not four).
    SQLITE_ABS_PATH_BASE_URI = "sqlite:///"
else:
    # Linux / OSX / Other
    SQLITE_ABS_PATH_BASE_URI = "sqlite:////"

# Set Database path to an inconsequential test db file.
config_handler.CONFIG["custom_db_path"] = "{}{}".format(SQLITE_ABS_PATH_BASE_URI, str(settings.TEST_DATABASE_PATH))
