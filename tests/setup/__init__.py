from handlers import config_handler
import settings

# Load test config.
config_handler.load_config(config_file=settings.TEST_CONFIG_FILE_PATH)
config_handler.CONFIG["custom_db_path"] = str(settings.TEST_DATABASE_PATH)

CONFIG = config_handler.CONFIG
