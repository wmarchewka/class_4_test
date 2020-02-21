#libraries
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer
import argparse
import logging

#my libraries
import speedgen_new
import gains
import logger
import config


class TestGainsSpeed(object):

    logging.info("Instantiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.log = self.logger.log
        logger.Logger(level=logging.DEBUG)
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--debug', '-d', nargs="+", type=str)
        self.args = self.parser.parse_args()
        self.log.debug("Arguments passed into script: {}".format(self.args))
        self.logging_args= self.args.debug
        if self.logging_args:
            self.level_config = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, "CRITICAL" : logging.CRITICAL}  # etc.
            self.logging_level = self.level_config[self.logging_args[0]]
            logger.Logger(level=self.logging_level)
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

        self.speed0 = speedgen_new.Speedgen(self.speed_0_name, self.speed_0_shape, self.speed_0_spi_channel,
                                            self.SPEED_0_CS,
                                            self.rotary_0_pins[0], self.rotary_0_pins[1], self.rotary_0_pin_0_debounce,
                                            self.rotary_0_pin_1_debounce, self.speed_0_thresholds)

        self.speed1 = speedgen_new.Speedgen(self.speed_1_name, self.speed_1_shape, self.speed_1_spi_channel,
                                            self.SPEED_1_CS,
                                            self.rotary_1_pins[0], self.rotary_1_pins[1], self.rotary_1_pin_0_debounce,
                                            self.rotary_1_pin_1_debounce, self.speed_1_thresholds)

        self.gain0 = gains.Gains(self.gain_0_name, self.gain_0_spi_channel, self.GAIN_0_CS,
                                 self.rotary_2_pins[0], self.rotary_2_pins[1], self.rotary_2_pin_0_debounce,
                                 self.rotary_2_pin_1_debounce, self.gain_0_thresholds)

        self.gain1 = gains.Gains(self.gain_1_name, self.gain_1_spi_channel, self.GAIN_1_CS,
                                 self.rotary_3_pins[0], self.rotary_3_pins[1], self.rotary_3_pin_0_debounce,
                                 self.rotary_3_pin_1_debounce, self.gain_1_thresholds)

    def parse_args(self, arguments):
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-v", "--verbose"):
                print("enabling verbose mode")
            elif currentArgument in ("-h", "--help"):
                print("displaying help")
            elif currentArgument in ("-o", "--output"):
                print(("enabling special output mode (%s)") % (currentValue))

if __name__ == "__main__":
    app = QApplication(['PORTABLE TESTER'])
    # app.setStyle("fusion")
    start_window = OLD.gui.Mainwindow()
    ts = TestGainsSpeed()
    # the timer calls itself every 100ms to allow to break in GUI
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # runs every 100ms
    timer.start(100)
    app.exit(app.exec_())
