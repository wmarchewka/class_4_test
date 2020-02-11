import gpio
import logger
import spi
import config

class Rotary:
    def __init__(self):
        self.gpio = gpio.Gpio()
        self.logger = logger.Logger()
        self.spi = spi.SPI()
        self.config = config.Config()
