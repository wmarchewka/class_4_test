import logging

class Basiclogger(object):

    log_format = "%(asctime)s.%(msecs)03d - %(levelname)s - %(name)s - %(funcName)s - %(lineno)d -%(message)s"
    logging.basicConfig(level='DEBUG', format=log_format)
    logging.getLogger(__name__)
    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):
        pass