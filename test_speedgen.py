import basiclogger
import speedgen_new
import time
import logging
import logger

class TestSpeedgen(object):

    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.speedgen = speedgen_new.Speedgen(spi_channel=2)



if __name__ == "__main__":
    ts = TestSpeedgen()
    while(True):
        time.sleep(1)
