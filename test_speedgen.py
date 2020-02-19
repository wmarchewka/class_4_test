import basiclogger
import config
import speedgen_new
import time
import logging
import logger


class TestSpeedgen(object):
    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.config = config.Config()
        self.speed_0_name = self.config.speed_0_name
        self.speed_1_name = self.config.speed_1_name
        self.speed_0_shape = self.config.speed_0_shape
        self.speed_1_shape = self.config.speed_1_shape
        self.speed_0_spi_channel = self.config.speed_0_spi_channel
        self.speed_1_spi_channel = self.config.speed_0_spi_channel
        self.SPEED_0_CS = self.config.SPEED_0_CS  # 6  # SPEED SIMULATION TACH 1
        self.SPEED_1_CS = self.config.SPEED_1_CS  # 7  # SPEED SIMULATION TACH 2
        self.rotary_0_pins = self.config.rotary_0_pins
        self.rotary_1_pins = self.config.rotary_1_pins
        self.rotary_0_pin_0_debounce = self.config.rotary_0_pin_0_debounce
        self.rotary_0_pin_1_debounce = self.config.rotary_0_pin_1_debounce
        self.rotary_1_pin_0_debounce = self.config.rotary_1_pin_0_debounce
        self.rotary_1_pin_1_debounce = self.config.rotary_1_pin_1_debounce
        self.speed_0_thresholds = self.config.SPEED_0_thresholds
        self.speed_1_thresholds = self.config.SPEED_1_thresholds

        self.speed0 = speedgen_new.Speedgen(self.speed_0_name, self.speed_0_shape, self.speed_0_spi_channel, self.SPEED_0_CS,
                                            self.rotary_0_pins[0], self.rotary_0_pins[1], self.rotary_0_pin_0_debounce,
                                            self.rotary_0_pin_1_debounce, self.speed_0_thresholds)

        self.speed1 = speedgen_new.Speedgen(self.speed_1_name, self.speed_1_shape, self.speed_1_spi_channel, self.SPEED_1_CS,
                                            self.rotary_1_pins[0], self.rotary_1_pins[1], self.rotary_1_pin_0_debounce,
                                            self.rotary_1_pin_1_debounce, self.speed_1_thresholds)



if __name__ == "__main__":
    ts = TestSpeedgen()
    while (True):
        time.sleep(1)
