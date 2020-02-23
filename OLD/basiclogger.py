import logging


class Basiclogger(object):
    log_format = "%(asctime)s. - %(name)s - %(levelname)-7s - Module:%(module)-18s  Function:%(funcName)-25s  Line Number:%(lineno)-8d - %(message)s"
    logging.basicConfig(level='INFO', format=log_format)
    logging.getLogger()
    logging.debug("Instantiating {} class...".format(__qualname__))
    logging.info('Starting up portable tester...')

    def __init__(self):
        pass
