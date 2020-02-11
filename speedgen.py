import gpio
import rotary
import logger
import config

class Speed:
    def __init__(self):
        self.logger = logger.Logger()
        self.rotary = rotary.Rotary()
        self.gpio = gpio.Gpio()
        self.config = config.Config()
