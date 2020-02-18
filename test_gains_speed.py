import basiclogger
import speedgen_new
import gains
import time
import logging
import logger

class TestGainsSpeed(object):

    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.speedgen = speedgen_new.Speedgen(spi_channel=2)
        self.gains = gains.Gains(spi_channel=2)



if __name__ == "__main__":
    ts = TestGainsSpeed()
    while(True):
        time.sleep(1)
