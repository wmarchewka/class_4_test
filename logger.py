import os
import logging
import logging.config

class Logger(object):

    logging.debug("Initiating {} class...".format(__qualname__))

    log = logging.getLogger(__name__)
    log.info('Starting up portable tester...')
    cwd = os.getcwd()
    log.info("CWD: {}".format(cwd))
    log.debug("{} init complete...".format(__name__))
    log.disabled = False
    log_config_file_path = "config/logging.ini"
    try:
        logging.config.fileConfig(log_config_file_path)
    except FileNotFoundError:
        logging_error = "Could not find " + str(log_config_file_path)

    def __init__(self):
        self.log = Logger.log
        self.log.debug("{} init complete...".format(__name__))
