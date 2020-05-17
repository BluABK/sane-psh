from flask import Flask
import logging

# from api.routes import notifications
import api.routes.notifications
from database import init_db
from handlers.log_handler import create_logger
from settings import API_BASEROUTE
from handlers.config_handler import load_config

if __name__ == "__main__":
    log = create_logger(__name__)
    log.info("Sane-PSH: Started.")
    config = load_config()
    init_db()

    # Set up Flask.
    flask_log = logging.getLogger('werkzeug')
    flask_log.setLevel(config["flask_log_level"])

    app = Flask(__name__)

    app.add_url_rule('{}/notifications'.format(API_BASEROUTE),
                     view_func=api.routes.notifications.psh, methods=['GET', 'POST'])

    app.run(host=config["bind_host"], port=config["bind_port"], debug=config["debug_flask"])
