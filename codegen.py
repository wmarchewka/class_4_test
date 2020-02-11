import logger
import config
import spi
import gpio


class Codegen(object):
    def __init__(self):
        self.gpio = gpio.Gpio()
        self.logger = logger.Logger()
        self.spi = spi.SPI()
        self.config = config.Config()
