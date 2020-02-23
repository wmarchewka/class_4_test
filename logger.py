import os
import logging
import logging.config

class Logger(object):

    log_config_file_path = "config/logging.ini"
    log = logging.getLogger(__name__)
    try:
        logging.config.fileConfig(log_config_file_path)
    except FileNotFoundError:
        logging_error = "Could not find " + str(log_config_file_path)
    log.disabled=False
    log.info("LOG LEVEL {}".format(log.getEffectiveLevel()))

    def __init__(self, level = None):
        self.log = Logger.log
        self.log.disabled = False
        if level:
            self.log.setLevel(level)
        self.log.debug("{} init complete...".format(__name__))
        self.log.debug("LOG LEVEL {}".format(self.log.getEffectiveLevel()))

