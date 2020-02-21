import faulthandler

faulthandler.enable()
import logging
import argparse
import time
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer

# my imports
from config import Config
from speedgen_new import Speedgen
from gains import Gains
from logger import Logger
from gui.gui_new import Mainwindow
from codegen import Codegen

class Commander(object):

    logging.debug("Instantiating {} class...".format(__qualname__))

    def __init__(self):
        self.gain0_val = 0
        self.gain1_val = 0
        self.speed0_val = 0
        self.speed1_val = 0
        self.logger = Logger(level=logging.DEBUG)
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.codegen = Codegen()
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--debug', '-d', nargs="+", type=str)
        self.args = self.parser.parse_args()
        self.log.debug("Arguments passed into script: {}".format(self.args))
        self.logging_args = self.args.debug
        if self.logging_args:
            self.level_config = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, "CRITICAL": logging.CRITICAL}  # etc.
            self.logging_level = self.level_config[self.logging_args[0]]
            Logger(level=self.logging_level)
        self.config = Config()
        self.gui = Mainwindow(self)
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
        self.speed0 = Speedgen(self.speed_0_name, self.speed_0_shape, self.speed_0_spi_channel,
                                            self.SPEED_0_CS,
                                            self.rotary_0_pins[0], self.rotary_0_pins[1],
                                            self.rotary_0_pin_0_debounce,
                                            self.rotary_0_pin_1_debounce, self.speed_0_thresholds, self.speed_callback,
                                            self.commander_speed_move_callback)
        self.speed1 = Speedgen(self.speed_1_name, self.speed_1_shape, self.speed_1_spi_channel,
                                            self.SPEED_1_CS,
                                            self.rotary_1_pins[0], self.rotary_1_pins[1],
                                            self.rotary_1_pin_0_debounce,
                                            self.rotary_1_pin_1_debounce, self.speed_1_thresholds, self.speed_callback,
                                            self.commander_speed_move_callback)
        self.gain0 = Gains(self.gain_0_name, self.gain_0_spi_channel, self.GAIN_0_CS,
                                 self.rotary_2_pins[0], self.rotary_2_pins[1], self.rotary_2_pin_0_debounce,
                                 self.rotary_2_pin_1_debounce, self.gain_0_thresholds, self.gains_callback,
                                 self.commander_gain_move_callback)
        self.gain1 = Gains(self.gain_1_name, self.gain_1_spi_channel, self.GAIN_1_CS,
                                 self.rotary_3_pins[0], self.rotary_3_pins[1], self.rotary_3_pin_0_debounce,
                                 self.rotary_3_pin_1_debounce, self.gain_1_thresholds, self.gains_callback,
                                 self.commander_gain_move_callback)

    # ****************************************************************************************************************
    def startup_processes(self):
        pass

    # ****************************************************************************************************************
    def parse_args(self, arguments):
        """
        parses arguments sent from running the command line
        :param arguments:
        """
        for currentArgument, currentValue in arguments:
            if currentArgument in ("-v", "--verbose"):
                print("enabling verbose mode")
            elif currentArgument in ("-h", "--help"):
                print("displaying help")
            elif currentArgument in ("-o", "--output"):
                print(("enabling special output mode (%s)") % (currentValue))

    # ****************************************************************************************************************
    def speed_callback(self, name, frequency):
        """
        receives callback from the speed class to update screen
        :rtype: object
        """
        self.log.debug("Callback received from {} with value of {}".format(name, frequency))
        if name == "SPEED0":
            self.gui.window.LBL_pri_tach_freq.setText("{:5.0f}".format(frequency))
        if name == "SPEED1":
            self.gui.window.LBL_sec_tach_freq.setText("{:5.0f}".format(frequency))
        self.log.debug("updated GUI ")
    # ****************************************************************************************************************
    def gains_callback(self, name, gain):
        """
          receives callback from the speed class to update screen
          :rtype: object
          """
        self.log.debug("Callback received from {} with value of {}".format(name, gain))
        if name == "GAIN0":
            self.gui.window.LBL_primary_gain_percent.setText("{0:.3%}".format(gain))
        if name == "GAIN1":
            self.gui.window.LBL_secondary_gain_percent.setText("{0:.3%}".format(gain))

    # ****************************************************************************************************************
    def commander_speed_move_callback(self, name, direction, speed_increment):
        """
        when the physical speed dial is moved this callback is activated.  it causes the screen simulated
        dial to move
        :param name:
        :param direction:
        :param speed_increment:
        """
        self.log.debug("Callback from:{} Direction:{} Speed:{}".format(name, direction, speed_increment))
        if name == "SPEED0":
            if direction == 1:
                self.speed0_val = self.speed0_val + 1
            if direction == -1:
                self.speed0_val = self.speed0_val - 1
        self.gui.window.QDIAL_speed_1.setValue(self.speed0_val)
        if name == "SPEED1":
            if direction == 1:
                self.speed1_val = self.speed1_val + 1
            if direction == -1:
                self.speed1_val = self.speed1_val - 1
        self.gui.window.QDIAL_speed_2.setValue(self.speed1_val)

    # ****************************************************************************************************************
    def commander_gain_move_callback(self, name, direction, speed_increment):
        """
        when the physical speed dial is moved this callback is activated.  it causes the screen simulated
        dial to move
        :param name:
        :param direction:
        :param speed_increment:
        """
        self.log.debug("Callback from:{} Direction:{} Speed:{}".format(name, direction, speed_increment))
        if name == "GAIN0":
            if direction == 1:
                self.gain0_val = self.gain0_val + 1
            if direction == -1:
                self.gain0_val = self.gain0_val - 1
        self.gui.window.QDIAL_primary_gain.setValue(self.gain0_val)
        if name == "GAIN1":
            if direction == 1:
                self.gain1_val = self.gain1_val + 1
            if direction == -1:
                self.gain1_val = self.gain1_val - 1
        self.gui.window.QDIAL_secondary_gain.setValue(self.gain1_val)

    #****************************************************************************************************************
    def simulate_speed(self, name, sim_pins):
        """
        when the on screen dial is rotated, this routine is called to simulate the physical pot turning
        :param name:
        :param sim_pins:
        """
        self.log.debug("Simulating:{} PINS:{}".format(name, sim_pins))
        if name == "SPEED0":
            self.speed0.simulate(sim_pins)
        if name == "SPEED1":
            self.speed1.simulate(sim_pins)

    #****************************************************************************************************************
    def simulate_gain(self, name, sim_pins):
        """
        when the on screen dial is rotated, this routine is called to simulate the physical pot turning
        :param name:
        :param sim_pins:
        """
        self.log.debug("Simulating:{} PINS:{}".format(name, sim_pins))
        if name == "SPEED0":
            self.gain0.simulate(sim_pins)
        if name == "SPEED1":
            self.gain1.simulate(sim_pins)


if __name__ == "__main__":
    app = QApplication(['PORTABLE TESTER'])
    app.setWheelScrollLines(1)
    # app.setStyle("fusion")
    commander = Commander()
    # the timer calls itself every 100ms to allow to break in GUI
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # runs every 100ms
    timer.start(100)
    app.exit(app.exec_())
