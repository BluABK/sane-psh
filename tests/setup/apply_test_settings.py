from handlers import config_handler
import settings

# Load test config.
config_handler.load_config(config_file=settings.TEST_CONFIG_FILE_PATH)

# Set Database path to an inconsequential test db file.
config_handler.CONFIG["custom_db_path"] = "sqlite:////{}".format(str(settings.TEST_DATABASE_PATH))
