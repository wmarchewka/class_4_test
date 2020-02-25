import os
import logging.config

class Logger(object):

    tmplog = logging.getLogger()
    tmplog.setLevel(logging.DEBUG)
    tmplog.info("Instantiating {} class...".format(__qualname__))
    del tmplog

    log_config_file_path = "config/logging.ini"
    log = logging.getLogger(__name__)
    try:
        logging.config.fileConfig(log_config_file_path)
    except FileNotFoundError:
        logging_error = "Could not find " + str(log_config_file_path)
    log.disabled=False
    log.info("LOG LEVEL {}".format(log.getEffectiveLevel()))

    def __init__(self, level = None):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.log = Logger.log
        self.log.disabled = False
        if level:
            self.log.setLevel(level)
        self.log.debug("{} init complete...".format(__name__))
        self.log.debug("LOG LEVEL {}".format(self.log.getEffectiveLevel()))

