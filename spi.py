import logger
import config
import decoder

class SPI(object):
    def __init__(self):
        self.logger = logger.Logger()
        self.config = config.Config()
        self.decoder = decoder.Decoder()
