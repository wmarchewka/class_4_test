import pigpio
import logging
import subprocess
import time

#my libraries
from logger import Logger
from config import Config

class Gpio():

    log = None
    #logging.info("Instantiating {} class...".format(__qualname__))


    __gpio = None
    __mode_input = 0
    __mode_output = 1
    _class_property = None
    _init = None

    @classmethod
    def init_gpio(cls):
        cls.__gpio = pigpio.pi()
        cls.tmp_logger = logging.getLogger()
        cls.tmp_logger.log = cls.tmp_logger
        cls.tmp_logger.log = logging.getLogger()
        cls.tmp_logger.log.debug("Creating GPIO...")

    @property
    def class_property(self):
        return self._class_property

    @class_property.setter
    def class_property(self, value):
        type(self)._class_property = value

    @class_property.deleter
    def class_property(self):
        del type(self)._class_property

    @property
    def name_inst(self):
        return self._name_inst

    @name_inst.setter
    def name_inst(self, value):
        type(self)._name_inst = value

    def __init__(self):
        super().__init__()
        self.config = Config()
        self.logger = Logger()
        self.log = self.logger.log
        self.log = logging.getLogger()
        if not Gpio._init:
            __gpio = Gpio.init_gpio()
            Gpio._init = True
            self.log.debug("FIRST SETUP OF GPIO")
        self.gpio = Gpio.__gpio
        self.log.debug(self.gpio)
        self.startup_proccesses()
        self.log.debug("{} init complete...".format(__name__))

    # ****************************************************************************************************
    def startup_proccesses(self):
        self.check_connection()
        self.get_io_status()


    # ****************************************************************************************************
    def shutdown(self):
        if self.gpio.connected:
            self.gpio.wave_tx_stop()
            self.gpio.wave_clear()
            self.gpio.stop()
            self.log.debug("Shutting down PIGPIO...")

    # ****************************************************************************************************
    def set_chip_select(self, data):
        self.gpio.write(data[0][0], data[0][1])
        self.gpio.write(data[1][0], data[1][1])
        self.gpio.write(data[2][0], data[2][1])

    # ****************************************************************************************************
    def get_pin(self, pin):
        mode = self.gpio.get_mode(pin)
        if mode == Gpio.__mode_input:
            txtmode = "INPUT"
            return self.gpio.read(pin), txtmode
        elif mode == Gpio.__mode_output:
            txtmode = "OUTPUT"
            return self.gpio.read(pin), txtmode
        else:
            txtmode = "UNKNOWN mode " + str(mode)
            return 0, txtmode

    # ****************************************************************************************************
    def set_pin(self, pin, state):
        mode = self.gpio.get_mode(pin)
        if mode == Gpio.__mode_input:
            txtmode = "INPUT"
            return self.gpio.read(pin), txtmode
        elif mode == Gpio.__mode_output:
            txtmode = "OUTPUT"
            self.gpio.write(pin, state)
            return self.gpio.read(pin), txtmode
        else:
            txtmode = "UNKNOWN mode " + str(mode)
            return 0, txtmode

    # ****************************************************************************************************
    def check_connection(self):
        if not self.gpio.connected:
            self.log.debug("PIGPIO not connected, Checking Daemon....")
            self.pigpiod_daemon_status()

        else:
            self.log.debug('PIGPIO connected...')

    # ****************************************************************************************************
    def get_io_status(self):
        try:
            self.logger.log.debug('Getting IO status...')
            self.logger.log.debug("gpio STATUS: Pins(0-31) {}  Pins(32-54)  {}   ".format(bin(self.gpio.read_bank_1()),
                                                                                   bin(
                                                                                       self.gpio.read_bank_2())))
        except Exception:
            self.logger.log.exception("EXCEPTION in get_status", exc_info=True)

    # ****************************************************************************************************
    # @staticmethod
    def edge_to_string(edge):
        if edge == 1:
            return "RISING"
        elif edge == 0:
            return "FALLING"
        elif edge == 2:
            return "ERROR"

    # ****************************************************************************************************
    def pigpiod_daemon_status(self):
        try:
            self.log.info("Getting PIGPIO status...")
            del self.gpio
            self.log.debug("Deleting PIGPIO instance...")
            # TODO check into why this is taking a long time to run at times
            self.my_cmd = subprocess.call(["sudo", "systemctl", "stop", "pigpiod"])
            self.log.debug("Returned from shell command {}".format(self.my_cmd))
            time.sleep(0.1)
            if not self.my_cmd:
                self.log.info("Successful shutdown of PIGPIO DAEMON")
            else:
                self.log.info("Error in shutdown of PIGPIO DAEMON")
                raise NameError('Error in shutdown of PIGPIO DAEMON"')
            self.my_cmd = subprocess.call(["sudo", "systemctl", "start", "pigpiod"])
            self.log.debug("Returned from shell command {}".format(self.my_cmd))
            if not self.my_cmd:
                self.log.info("Successful start of PIGPIO DAEMON")
            else:
                self.log.info("Error in startup of PIGPIO DAEMON")
                raise NameError('Error in startup of PIGPIO DAEMON')
            time.sleep(0.1)
            gpio_version = self.gpio.get_pigpio_version()
            self.log.info("Using PIGPIO version: {}".format(gpio_version))
        except Exception:
            self.log.exception("Exception in pigiod_daemon_status", exc_info=True)
            return False
        else:
            return True