import basiclogger
import gains
import time
import logging
import logger
import config

class TestGains(object):
    logging.info("Instantiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.config = config.Config()
        self.GAIN_0_CS = self.config.GAIN_0_CS
        self.GAIN_1_CS = self.config.GAIN_1_CS
        self.GAIN_0_THRESHOLDS = self.config.gain_0_thresholds
        self.GAIN_1_THRESHOLDS = self.config.gain_1_thresholds
        self.rotary_2_pins = self.config.rotary_2_pins
        self.rotary_3_pins = self.config.rotary_3_pins
        self.rotary_2_pin_0_debounce = self.config.rotary_2_pin_0_debounce
        self.rotary_2_pin_1_debounce = self.config.rotary_2_pin_1_debounce
        self.rotary_3_pin_0_debounce = self.config.rotary_3_pin_0_debounce
        self.rotary_3_pin_1_debounce = self.config.rotary_3_pin_1_debounce
        self.gain_0_spi_channel = self.config.gain_0_spi_channel
        self.gain_1_spi_channel = self.config.gain_0_spi_channel
        self.gain_0_name = self.config.gain_0_name
        self.gain_1_name = self.config.gain_1_name
        self.gain_0_thresholds = self.config.gain_0_thresholds
        self.gain_1_thresholds = self.config.gain_1_thresholds

        self.gain0 = gains.Gains(self.gain_0_name, self.gain_0_spi_channel, self.GAIN_0_CS,
                                            self.rotary_2_pins[0], self.rotary_2_pins[1], self.rotary_2_pin_0_debounce,
                                            self.rotary_2_pin_1_debounce, self.gain_0_thresholds)

        self.gain1 = gains.Gains(self.gain_1_name, self.gain_1_spi_channel, self.GAIN_1_CS,
                                 self.rotary_3_pins[0], self.rotary_3_pins[1], self.rotary_3_pin_0_debounce,
                                 self.rotary_3_pin_1_debounce, self.gain_1_thresholds)


if __name__ == "__main__":
    ts = TestGains()
    while (True):
        time.sleep(1)
