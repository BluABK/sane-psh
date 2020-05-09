# -*- coding: utf-8 -*-

import logging
import os
from logging.handlers import SocketHandler
from handlers.config_handler import load_config, get_option

config = load_config()

LOG_FILE_HANDLER = None
LOG_TO_FILE = get_option("log_to_file", default=True)


# create formatter and add it to the handlers
FORMATTER = logging.Formatter(u'%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DEFAULT_LOG_LEVELS = [0, 10, 20, 30, 40, 50]

# Logging levels (practically) static dict.
LOG_LEVELS = {'UNSET': 0,
              'SPAM': 1,
              'DEBUG9': 2,
              'DEBUG8': 3,
              'DB_DEBUG': 4,
              'DEBUG6': 5,
              'DEBUG5': 6,
              'DEBUG4': 7,
              'DEBUG3': 8,
              'DEBUG2': 9,
              'DEBUG': 10,
              'INFO': 20,
              'DB_INFO': 26,
              'WARNING': 30,
              'ERROR': 40,
              'CRITICAL': 50}

# Determine log level name by int:
# Separate the dictionary's values in a list, find the position of the given value, and gets the key at that position.
# Additionally order is guaranteed not to change through iterations, as long as the dictionary is not modified.
log_level = get_option("log_level", default=40)
log_level_name = list(LOG_LEVELS.keys())[list(LOG_LEVELS.values()).index(int(log_level))]
LOG_FILE = "{}.log".format(log_level_name)


def db_info(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DB_INFO (Level 26)
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DB_INFO']):
        self._log(LOG_LEVELS['DB_INFO'], message, args, **kwargs)


def debug2(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG2
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DEBUG2']):
        self._log(LOG_LEVELS['DEBUG2'], message, args, **kwargs)


def debug3(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG3
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DEBUG3']):
        self._log(LOG_LEVELS['DEBUG3'], message, args, **kwargs)


def debug4(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG4
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DEBUG4']):
        self._log(LOG_LEVELS['DEBUG4'], message, args, **kwargs)


def debug5(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG5
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DEBUG5']):
        self._log(LOG_LEVELS['DEBUG5'], message, args, **kwargs)


def debug6(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG6
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DEBUG6']):
        self._log(LOG_LEVELS['DEBUG6'], message, args, **kwargs)


def db_debug(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG7
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DB_DEBUG']):
        self._log(LOG_LEVELS['DB_DEBUG'], message, args, **kwargs)


def debug8(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG8
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DEBUG8']):
        self._log(LOG_LEVELS['DEBUG8'], message, args, **kwargs)


def debug9(self, message, *args, **kwargs):
    """
    Custom Logging level log function: DEBUG9
    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['DEBUG9']):
        self._log(LOG_LEVELS['DEBUG9'], message, args, **kwargs)


def spam(self, message, *args, **kwargs):
    """
    Custom Logging level log function: SPAM

    The logging level that is used for really spamming debug logging

    :param self:
    :param message: String to log
    :param args: logging args
    :param kwargs: logging keywords
    :return:
    """
    if self.isEnabledFor(LOG_LEVELS['SPAM']):
        self._log(LOG_LEVELS['SPAM'], message, args, **kwargs)


def create_logger_socket(facility):
    """
    Create and return a a logging instance that logs to socket.
    :param facility:
    :return:
    """
    return log_socket_instance.getChild(facility)


def create_file_handler(log_file=LOG_FILE, formatter=FORMATTER):
    """
    Creates *the* (singular) file handler for logging to text file.

    File handler needs to be global and a singular instance,
    to avoid spamming FDs for each create_logger() call.
    :param log_file:
    :param formatter:
    :return:
    """
    global LOG_FILE_HANDLER

    # Only create one instance of the file handler
    if LOG_TO_FILE is True and LOG_FILE_HANDLER is None:
        logfile_path = os.path.join(config["log_dir"], log_file)

        # Make sure logs dir exists, if not create it.
        if not os.path.isdir(config["log_dir"]):
            os.makedirs(config["log_dir"])

        # Make sure logfile exists, if not create it.
        if not os.path.isfile(logfile_path):
            open(logfile_path, 'a').close()

        LOG_FILE_HANDLER = logging.FileHandler(logfile_path, encoding="UTF-8")
        LOG_FILE_HANDLER.setLevel(logging.DEBUG)
        LOG_FILE_HANDLER.setFormatter(formatter)


def create_logger_file(facility, formatter=FORMATTER):
    """
    Create and return a a logging instance that logs to file.
    :param facility:
    :param formatter:
    :return:
    """
    global LOG_FILE_HANDLER

    log_file_instance = logging.getLogger(facility)

    log_file_instance.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    if not os.path.exists(config["log_dir"]):
        os.makedirs(config["log_dir"])

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    # patch the default logging formatter to use unicode format string
    logging._defaultFormatter = logging.Formatter(u"%(message)s")
    ch.setFormatter(formatter)

    # add the handlers to the logger
    log_file_instance.addHandler(LOG_FILE_HANDLER)
    log_file_instance.addHandler(ch)

    return log_file_instance


def create_logger(facility):
    """
    Creates a logger function based on the logging library
    :param facility:     Name of what's calling logger.
    :return:
    """
    create_file_handler()

    # create logger
    if LOG_TO_FILE is False:
        logger_instance = create_logger_socket(facility)
    else:
        logger_instance = create_logger_file(facility)

    # Attach a handle to the log levels dict.
    setattr(logger_instance, "my_log_levels", LOG_LEVELS)

    return logger_instance


# Logging to socket (log to file is False).
if LOG_TO_FILE is False:
    log_socket_instance = logging.getLogger('r')
    log_level = get_option("log_level", default=40)
    port = get_option("log_bind_port", default=19994)
    host = get_option("log_bind_host", default="127.0.0.1")

    log_socket_instance.setLevel(log_level)  # to send all records to socket logger

    socket_handler = SocketHandler(host, port)  # default listening address
    log_socket_instance.addHandler(socket_handler)

# Add custom logging levels (descending order)
for level, value in LOG_LEVELS.items():
    if value in DEFAULT_LOG_LEVELS:
        # Skip default levels
        continue

    # Add level name and value to static logging instance.
    logging.addLevelName(value, level)

# Define logging attributes for log levels and assign them to the appropriate function
logging.Logger.db_info = db_info
logging.Logger.debug2 = debug2
logging.Logger.debug3 = debug3
logging.Logger.debug4 = debug4
logging.Logger.debug5 = debug5
logging.Logger.debug6 = debug6
logging.Logger.db_debug = db_debug
logging.Logger.debug8 = debug8
logging.Logger.debug9 = debug9
logging.Logger.spam = spam

# Default logger facility
logger = create_logger('Sane-PSH')
