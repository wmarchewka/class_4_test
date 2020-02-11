import logger
import config
import gpio

class Decoder(object):
    def __init__(self):
        self.logger = logger.Logger()
        self.config = config.Config()
        self.gpio = gpio.Gpio()
