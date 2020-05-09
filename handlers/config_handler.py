import copy
import json
import os

from settings import CONFIG_PATH, SAMPLE_CONFIG_PATH

# Default configuration (Use custom config.json to override its contents)
DEFAULT_CONFIG = {
    "bind_port": 5015,
    "bind_host": "0.0.0.0",
    "debug_flask": False,
    "flask_log_level": 0,
    "require_verification_token": False,
    "verification_token": "",
    "require_hmac_authentication": False,
    "hmac_secret": "",
    "increase_kind_precision": False
}

# Let's make sure we copy default config by value, not reference. So that it remains unmodified.
CONFIG = copy.deepcopy(DEFAULT_CONFIG)


def has_option(cfg: json, cfg_key: str):
    if cfg_key in cfg:
        return True

    return False


def has_custom_config(config_file=CONFIG_PATH):
    if os.path.isfile(config_file):
        return True
    else:
        return False


def update_sample_config(sample_config=SAMPLE_CONFIG_PATH):
    global DEFAULT_CONFIG

    with open(sample_config, 'w') as f:
        json.dump(DEFAULT_CONFIG, f, indent=4)


def set_custom_config_options(cfg: json):
    global CONFIG

    for key, value in cfg.items():
        CONFIG[key] = value


def load_config(config_file=CONFIG_PATH):
    global CONFIG

    # Create a sample config file.
    update_sample_config()

    # If config file doesn't exist
    if has_custom_config():
        try:
            with open(config_file) as f:
                # Override config options with those defined in the custom config file.
                set_custom_config_options(json.load(f))
        except Exception as exc:
            print("Error: Exception occurred while opening config file: {}! "
                  "Falling back to default config.".format(exc, config_file))
            pass

    return CONFIG
