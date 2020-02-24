import faulthandler
import sys
import signal

faulthandler.enable()
import argparse
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer

# my imports
from logger import Logger
from config import Config
from gui.gui_new import Mainwindow
from speedgen_new import Speedgen
from gains import Gains
from pollperm import Pollperm
from codegen import Codegen
from gpio import Gpio
from spi import SPI
from decoder import Decoder
from support.support import Support
from pollvalues import Pollvalues
from switches import Switches
from currentsense import CurrentSense


class Commander(object):
    Logger.log.debug("Instantiating {} class...".format(__qualname__))
    set_level = 0

    def __init__(self, logger):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.logger = logger
        self.config = Config(logger=self.logger)
        self.support = Support(config=self.config, logger=self.logger)
        self.gpio = Gpio(config=self.config, logger=self.logger)
        self.pollperm = Pollperm(logger=self.logger)
        self.decoder = Decoder(config=self.config, logger=self.logger, gpio=self.gpio)
        self.spi = SPI(config=self.config, logger=self.logger, decoder=self.decoder, pollperm=self.pollperm)
        self.codegen = Codegen(config=self.config, logger=self.logger, gpio=self.gpio, spi=self.spi)
        self.gui = Mainwindow(self, codegen=self.codegen, config=self.config, logger=self.logger, support=self.support)
        self.switches = Switches(config=self.config, logger=self.logger, spi=self.spi, gui=self.gui)
        self.currentsense = CurrentSense(logger=self.logger, spi=self.spi, decoder=self.decoder, gui=self.gui)
        self.pollvalues = Pollvalues(pollperm=self.pollperm, logger=logger, config=self.config,
                                     currentsense=self.currentsense, switches=self.switches)
        self.window = self.gui.window
        self.log = self.logger.log
        self.gain0_val = 0
        self.gain1_val = 0
        self.speed0_val = 0
        self.speed1_val = 0
        self.knob_values = 0
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
        self.speed0 = Speedgen(pollperm=self.pollperm, logger=self.logger, config=self.config, decoder=self.decoder,
                               spi=self.spi,
                               name=self.speed_0_name, shape=self.speed_0_shape,
                               spi_channel=self.speed_0_spi_channel,
                               chip_select=self.SPEED_0_CS,
                               pin_0=self.rotary_0_pins[0], pin_1=self.rotary_0_pins[1],
                               pin_0_debounce=self.rotary_0_pin_0_debounce,
                               pin_1_debounce=self.rotary_0_pin_1_debounce, thresholds=self.speed_0_thresholds,
                               callback=self.speed_callback,
                               commander_speed_move_callback=self.speed_move_callback)
        self.speed1 = Speedgen(pollperm=self.pollperm, logger=self.logger, config=self.config, decoder=self.decoder,
                               spi=self.spi,
                               name=self.speed_1_name, shape=self.speed_1_shape,
                               spi_channel=self.speed_1_spi_channel,
                               chip_select=self.SPEED_1_CS,
                               pin_0=self.rotary_1_pins[0], pin_1=self.rotary_1_pins[1],
                               pin_0_debounce=self.rotary_1_pin_0_debounce,
                               pin_1_debounce=self.rotary_1_pin_1_debounce, thresholds=self.speed_1_thresholds,
                               callback=self.speed_callback,
                               commander_speed_move_callback=self.speed_move_callback)
        self.gain0 = Gains(pollperm=self.pollperm, config=self.config, logger=self.logger, decoder=self.decoder,
                           spi=self.spi,
                           name=self.gain_0_name, spi_channel=self.gain_0_spi_channel,
                           chip_select=self.GAIN_0_CS,
                           pin_0=self.rotary_2_pins[0], pin_1=self.rotary_2_pins[1],
                           pin_0_debounce=self.rotary_2_pin_0_debounce,
                           pin_1_debounce=self.rotary_2_pin_1_debounce, thresholds=self.gain_0_thresholds,
                           callback=self.gains_callback,
                           commander_gain_move_callback=self.gain_move_callback)
        self.gain1 = Gains(pollperm=self.pollperm, config=self.config, logger=self.logger, decoder=self.decoder,
                           spi=self.spi,
                           name=self.gain_1_name, spi_channel=self.gain_1_spi_channel,
                           chip_select=self.GAIN_1_CS,
                           pin_0=self.rotary_3_pins[0], pin_1=self.rotary_3_pins[1],
                           pin_0_debounce=self.rotary_3_pin_0_debounce,
                           pin_1_debounce=self.rotary_3_pin_1_debounce, thresholds=self.gain_1_thresholds,
                           callback=self.gains_callback,
                           commander_gain_move_callback=self.gain_move_callback)
        self.startup_processes()

    # ****************************************************************************************************************
    def startup_processes(self):
        self.exit_signalling()
        self.log_level_first_start()
        self.speed_get_values()
        self.gains_get_values()
        self.shape_get_values()
        self.poll_timer_setup()

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

    # ******************************************************************************
    def exit_signalling(self):
        signal.signal(signal.SIGINT, self.exit_application)
        signal.signal(signal.SIGTERM, self.exit_application)
        self.log.debug("Setting up exit signaling...")

    # ****************************************************************************************************************
    def poll_timer_setup(self):
        self.poll_timer = QTimer()
        self.poll_timer.setObjectName("POLL TIMER")
        self.poll_timer.timeout.connect(self.pollvalues.poll_read_values)
        # self.pollvalues.switch_changedValue.connect(self.switch_changed_value)
        # self.pollvalues.sense_changedValue.connect(self.sense_changed_value)
        self.poll_timer.start(self.config.poll_timer_interval)

    # ****************************************************************************************************************
    # def poll_callback_change_value(self, counts, analog_digital_value, scaled_value, switch_value):
    # self.sense_callback_change_value(counts, analog_digital_value, scaled_value)
    # self.switches_callback_change_value(switch_value)

    # ****************************************************************************************************************
    def sense_callback(self, adc_average, display_amps, counts):
        self.window.LBL_display_adc.setText("{:4.2f}".format(adc_average))
        self.window.LBL_display_amps.setText("{:2.3f}".format(display_amps))
        self.window.LBL_loop_current_1.setText("{:2.3f}".format(display_amps))
        self.window.LBL_display_adc_counts.setText("{:5.0f}".format(counts))

    # ************************************************************************************
    # call back from switch_polling
    def switches_callback_change_value(self, value):
        self.log.debug("onSwitchChangeValues     :{:08b}".format(value))
        self.log.debug("knob values              :{:08b}".format(self.knob_values))
        value = (value | self.knob_values)
        self.log.debug("onSwitchChangeValues ORED:{:08b}".format(value))
        if value & 0b00000001:
            self.window.switch3_green.setVisible(True)
            self.window.switch3_red.setVisible(False)
        else:
            self.window.switch3_green.setVisible(False)
            self.window.switch3_red.setVisible(True)
        if value & 0b00000010:
            self.window.switch4_green.setVisible(True)
            self.window.switch4_red.setVisible(False)
        else:
            self.window.switch4_green.setVisible(False)
            self.window.switch4_red.setVisible(True)
        if value & 0b00000100:
            self.window.switch5_green.setVisible(True)
            self.window.switch5_red.setVisible(False)
        else:
            self.window.switch5_green.setVisible(False)
            self.window.switch5_red.setVisible(True)
        if value & 0b00001000:
            self.window.switch6_green.setVisible(True)
            self.window.switch6_red.setVisible(False)
        else:
            self.window.switch6_green.setVisible(False)
            self.window.switch6_red.setVisible(True)

        # if self.switches.primary_gain_pb_status == "ON":
        #     self.window.LBL_primary_gain_pb_status.setText("ON")
        #     self.digital_pots.gains_locked = False
        #     self.window.LBL_frequency_selected.setText("SEC")
        # if self.switches.primary_gain_pb_status == "OFF":
        #     self.window.LBL_primary_gain_pb_status.setText("OFF")
        #     self.digital_pots.gains_locked = False
        # if self.switches.primary_gain_pb_status == "CODERATE":
        #     self.window.LBL_primary_gain_pb_status.setText("CODERATE")
        #     self.digital_pots.gains_locked = False
        # if self.switches.primary_gain_pb_status == "LOCKED":
        #     self.window.LBL_primary_gain_pb_status.setText("LOCKED")
        #     self.digital_pots.gains_locked = True
        # self.primary_gain_pb_status = "NONE"
        #
        # if self.switches.secondary_gain_pb_status == "ON":
        #     self.window.LBL_secondary_gain_pb_status.setText("ON")
        # if self.switches.secondary_gain_pb_status == "OFF":
        #     self.window.LBL_secondary_gain_pb_status.setText("OFF")
        # if self.switches.secondary_gain_pb_status == "CODERATE":
        #     self.window.LBL_secondary_gain_pb_status.setText("CODERATE")
        # if self.switches.secondary_gain_pb_status == "LOCKED":
        #     self.window.LBL_secondary_gain_pb_status.setText("LOCKED")
        # self.secondary_gain_pb_status = "NONE"
        #
        # # self.lcd_switches.display(switch_value)
        # self.thread_info()

    # ****************************************************************************************************************
    def speed_buttonstate_change(self, name, value):
        if name == "SPEED0":
            self.speed0.update_shape(shape=value)
        elif name == "SPEED1":
            self.speed1.update_shape(shape=value)

    # ****************************************************************************************************************
    def speed_callback(self, name, frequency):
        """
        receives callback from the speed class to update screen
        :rtype: object
        """
        self.log.debug("Callback received from {} with value of {}".format(name, frequency))
        if name == "SPEED0":
            self.window.LBL_pri_tach_freq.setText("{:5.0f}".format(frequency))
        if name == "SPEED1":
            self.window.LBL_sec_tach_freq.setText("{:5.0f}".format(frequency))
        self.log.debug("updated GUI ")
        self.window.tabWidget.setCurrentIndex(3)

    # ****************************************************************************************************************
    def shape_get_values(self):
        shape0 = self.speed0.shape
        shape1 = self.speed1.shape
        self.shape_update_gui("SPEED0", shape0)
        self.shape_update_gui("SPEED1", shape1)

    # ****************************************************************************************************************
    def shape_update_gui(self, name, value):
        if name == "SPEED0":
            if value == self.config.FREQ_SHAPE_SINE:
                self.window.BUTTON_speed0_sine.setChecked(True)
            if value == self.config.FREQ_SHAPE_SQUARE:
                self.window.BUTTON_speed0_square.setChecked(True)
            if value == self.config.FREQ_SHAPE_TRIANGLE:
                self.window.BUTTON_speed0_triangle.setChecked(True)
        if name == "SPEED1":
            if value == self.config.FREQ_SHAPE_SINE:
                self.window.BUTTON_speed1_sine.setChecked(True)
            if value == self.config.FREQ_SHAPE_SQUARE:
                self.window.BUTTON_speed1_square.setChecked(True)
            if value == self.config.FREQ_SHAPE_TRIANGLE:
                self.window.BUTTON_speed1_triangle.setChecked(True)

    # ****************************************************************************************************************
    def gains_get_values(self):
        gain0 = self.gain0.wiper_total_percentage
        gain1 = self.gain1.wiper_total_percentage
        self.gains_gui_update("GAIN0", gain0)
        self.gains_gui_update("GAIN1", gain1)

    # ****************************************************************************************************************
    def speed_get_values(self):
        speed0 = self.speed0.speed_frequency
        speed1 = self.speed1.speed_frequency
        self.speed_gui_update("SPEED0", speed0)
        self.speed_gui_update("SPEED1", speed1)

    # ****************************************************************************************************************
    def gains_callback(self, name, gain):
        """
          receives callback from the speed class to update screen
          :rtype: object
          """
        self.log.debug("Callback received from {} with value of {}".format(name, gain))
        self.gains_gui_update(name, gain)
        self.window.tabWidget.setCurrentIndex(2)

    # ****************************************************************************************************************
    def gains_gui_update(self, name, gain):
        if name == "GAIN0":
            self.window.LBL_primary_gain_percent.setText("{0:.3%}".format(gain))
        if name == "GAIN1":
            self.window.LBL_secondary_gain_percent.setText("{0:.3%}".format(gain))

    # ****************************************************************************************************************
    def speed_gui_update(self, name, frequency):
        if name == "SPEED0":
            self.window.LBL_pri_tach_freq.setText("{:5.0f}".format(frequency))
        if name == "SPEED1":
            self.window.LBL_sec_tach_freq.setText("{:5.0f}".format(frequency))
        self.log.debug("updated GUI ")

    # ****************************************************************************************************************
    def speed_move_callback(self, name, direction, speed_increment):
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
        self.window.QDIAL_speed_1.setValue(self.speed0_val)
        if name == "SPEED1":
            if direction == 1:
                self.speed1_val = self.speed1_val + 1
            if direction == -1:
                self.speed1_val = self.speed1_val - 1
        self.window.QDIAL_speed_2.setValue(self.speed1_val)

    # ****************************************************************************************************************
    def gain_move_callback(self, name, direction, speed_increment):
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
        self.window.QDIAL_primary_gain.setValue(self.gain0_val)
        if name == "GAIN1":
            if direction == 1:
                self.gain1_val = self.gain1_val + 1
            if direction == -1:
                self.gain1_val = self.gain1_val - 1
        self.window.QDIAL_secondary_gain.setValue(self.gain1_val)

    # ****************************************************************************************************************
    def speed_simulate(self, name, sim_pins):
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

    # ****************************************************************************************************************
    def gain_simulate(self, name, sim_pins):
        """
        when the on screen dial is rotated, this routine is called to simulate the physical pot turning
        :param name:
        :param sim_pins:
        """
        self.log.debug("Simulating:{} PINS:{}".format(name, sim_pins))
        if name == "GAIN0":
            self.gain0.simulate(sim_pins)
        if name == "GAIN1":
            self.gain1.simulate(sim_pins)

    # ****************************************************************************************************************
    def log_level_PB_changed(self, value):
        self.log.debug("Log level PB pushed")
        Commander.set_level = Commander.set_level + 10
        self.log_level_set(Commander.set_level)
        txt_level = self.log_level_to_text(Commander.set_level)
        self.log_level_update_gui(txt_level)
        if Commander.set_level == 50:
            Commander.set_level = 0

    # ****************************************************************************************************************
    def log_level_set(self, setLevel):
        self.log.debug("Set log level:{}".format(setLevel))
        txt_level = self.log_level_to_text(setLevel)
        self.log.setLevel(txt_level)
        self.log.debug("Setting LOG LEVEL:{}".format(txt_level))

    # ****************************************************************************************************************
    def log_level_update_gui(self, value):
        self.log.debug("SLog level update gui:{}".format(value))
        self.window.PB_log_level.setText(value)

    # ****************************************************************************************************************
    def log_level_get(self):
        level = self.log.getEffectiveLevel()
        Commander.set_level = level
        self.log.debug("Get log level:{}".format(level))
        return level

    # ****************************************************************************************************************
    def log_level_first_start(self):
        self.log.debug("Log level first start:{}")
        level = self.log_level_get()
        txt_level = self.log_level_to_text(level)
        self.log_level_update_gui(txt_level)

    # ****************************************************************************************************************
    def log_level_to_text(self, value):
        txtlevel = None
        if value == 0:
            txtlevel = "NOTSET"
        elif value == 10:
            txtlevel = "DEBUG"
        elif value == 20:
            txtlevel = "INFO"
        elif value == 30:
            txtlevel = "WARNING"
        elif value == 40:
            txtlevel = "ERROR"
        elif value == 50:
            value = -10
            txtlevel = "CRITICAL"
        self.log.debug("Convert Log level:{} to text:{}".format(value, txtlevel))
        return txtlevel

    # *******************************************************************************************
    def exit_application(self, signum, frame):
        self.log.info("Starting shutdown")
        self.log.debug("Received signal from signum: {} with frame:{}".format(signum, frame))
        self.shutdown()

    # *******************************************************************************************
    def shutdown(self):
        # self.gains.setval_and_store(0)
        # self.gains.primary_gain_off()
        # self.gains.secondary_gain_off()
        # self.coderategenerator.coderate_stop()
        # self.speed_generator.speed_1_off()
        # self.speed_generator.speed_2_off()
        # self.local_timer.stop()
        # self.switch_timer.stop()
        # self.sense_timer.stop()
        try:
            self.server.server_close()
        except:
            print("Error")
        # self.log.info('Turning off screen saver forced on')
        # subprocess.call('xset dpms force off', shell=True)
        self.log.info("Goodbye...")
        # self.log.shutdown()
        sys.exit(0)
