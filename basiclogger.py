import logging

class Basiclogger(object):

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(lineno)d -%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)
    logging.getLogger()
    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):
        pass
