import basiclogger
import gains
import time
import logging
import logger


class TestGains(object):
    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.gains = gains.Gains(spi_channel=2)


if __name__ == "__main__":
    ts = TestGains()
    while (True):
        time.sleep(1)
