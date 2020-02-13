import logger
import config
import gpio
import decoder
import spi

class Digpots(object):
    def __init__(self):
        self.gpio = gpio.Gpio()
        self.logger = logger.Logger()
        self.spi = spi.SPI()
        self.config = config.Config()
        self.decoder = decoder.Decoder()
