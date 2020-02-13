import configparser
import logging
import logging.config
import os
import platform as pf
import sys
import time
import pigpio
from PyQt5.Qt import PYQT_VERSION_STR
from PyQt5.QtCore import QT_VERSION_STR
import subprocess
import logger

class Support(object):
    ostype = ""

    def __init__(self):
        # initialize logging
        cwd = os.getcwd()
        self.log_config_file_path = "config/logging.ini"
        try:
            logging.config.fileConfig(self.log_config_file_path)
        except FileNotFoundError:
            self.logging_error = "Could not find " + str(self.log_config_file_path)
        self.logger = logger.Logger()
        self.log = logging.getLogger(__name__)
        self.log.info('Starting up portable tester...')
        self.log.info("CWD: {}".format(cwd))
        #self.mainwindow = mainwindow

        # initialize config file
        self.config_file_path = "config/config.ini"
        self.log.info("Logging config file path {}".format(self.config_file_path))
        self.log.info('Loading log configuration from {}'.format(self.config_file_path))
        self.config = configparser.ConfigParser()
        self.config.sections()
        self.config.read_file(open(self.config_file_path))

        # other tests
        self.ostype = None
        self.operating_system_detect()
        self.qt_version_query()
        self.pyqt_version_query()
        self.rpi_touchscreen_status()
        self.spi_device_query()
        self.rpi_version_query()
        self.pigpiod_daemon_status()

    # **************************************************************************
    def configuration_save(self, section, key, value):
        self.config.set(section, key, value)
        with open(self.config_file_path, 'w') as cf:
            self.config.write(cf)
        cf.close()
        self.log.info(
            "Configuration.ini updated: SECTION:{}  KEY:{}  VALUE:{}".format(section, key, value))

    # **************************************************************************
    def operating_system_detect(self):
        self.log.info("Getting OS TYPE...")
        os_type = None
        platform = pf.system()
        if platform == 'Windows':
            os_type = 'Windows'
        elif platform == 'Linux':
            os_type = 'rpi'
        elif platform == "Darwin":
            os_type = 'MAC'
        self.log.info("OS type found  = {}".format(os_type))
        if os_type != 'rpi':
            self.log.debug('Using fake-rpi as gpio')
            import fake_rpi
            sys.modules['RPi'] = fake_rpi.RPi  # Fake RPi (gpio)
            sys.modules['smbus'] = fake_rpi.smbus  # Fake smbus (I2C)
            sys.modules['RPi.gpio'] = fake_rpi.RPi.GPIO
        else:
            self.log.info('Using pigpio as gpio')
        self.ostype = os_type

    def pigpiod_daemon_status(self):
        try:
            self.log.info("Getting PIGPIO status...")
            # TODO check into why this is taking a long time to run at times
            self.my_cmd  = subprocess.call(["sudo", "systemctl", "stop", "pigpiod"])
            self.log.debug("Returned from shell command {}".format(self.my_cmd))
            time.sleep(0.1)
            if not self.my_cmd:
                self.log.info("Successful shutdown of PIGPIO DAEMON")
            else:
                self.log.info("Error in shutdown of PIGPIO DAEMON")
                raise NameError('Error in shutdown of PIGPIO DAEMON"')
            self.my_cmd  = subprocess.call(["sudo", "systemctl", "start", "pigpiod"])
            self.log.debug("Returned from shell command {}".format(self.my_cmd))
            if not self.my_cmd:
                self.log.info("Successful start of PIGPIO DAEMON")
            else:
                self.log.info("Error in startup of PIGPIO DAEMON")
                raise NameError('Error in startup of PIGPIO DAEMON')
            time.sleep(0.1)
            pigpio.exceptions = False
            self.pi = pigpio.pi()
            gpio_version = self.pi.get_pigpio_version()
            self.log.info("Using PIGPIO version: {}".format(gpio_version))
        except:
            self.log.exception("Exception in pigiod_daemon_status", exc_info=True)

    def brightness_get(self):
        screen_brightness = self.brightness_query()
        return screen_brightness

    def qt_version_query(self):
        self.log.info("Qt version: {}".format(QT_VERSION_STR))

    def pyqt_version_query(self):
        self.log.info("PyQt version: {}".format(PYQT_VERSION_STR))

    def gen4_touchscreen_status(self):
        if self.ostype == 'rpi':
            self.log.info('Checking for Gen4 Touchscreen...')

    def rpi_touchscreen_status(self):
        if self.ostype == 'rpi':
            my_cmd = os.popen('sudo dmesg | grep -i ft5406').read()
            result = my_cmd.find('FT5406 memory based driver as /devices/virtual/input')
            if result:
                self.log.info('Found TOUCHSCREEN')
                self.configuration_save('DISPLAY', 'touchscreen', self.ostype)

    def rpi_version_query(self):
        try:
            if self.ostype == 'rpi':
                my_cmd = os.popen('sudo gpio -v').read()
                result = my_cmd.splitlines()
                self.log.info("Raspberry Pi Model:{}".format(result[8]))
        except:
            self.log.exception("EXCEPTION in rpi_version_query", exc_info=True)

    def spi_device_query(self):
        if self.ostype == 'rpi':
            try:
                list_of_files = os.listdir('/dev')
                spidevices = self.config.get('SPI', 'devices')
                spidevices = spidevices.split(',')
                for list in spidevices:
                    if list in list_of_files:
                        self.log.info('Found SPI device: {}'.format(list))
                    else:
                        self.log.info('Missing SPI device: {}'.format(list))
                        if list == 'spidev1.0' or list == 'spidev1.2':
                            self.log.error('ERROR:  Missing SPI Driver !!!')
            except Exception:
                self.log.error('ERROR')

    def brightness_set(self, value):
        try:
            if self.ostype == 'rpi':
                # sudo sh -c "echo 31 > /sys/class/backlight/4d-hats/brightness"
                os.popen("sudo sh -c 'echo " + str(value) + "  > /sys/class/backlight/4d-hats/brightness'")
                brightness = self.brightness_query()
                if brightness == "":
                    return None
                else:
                    return
        except Exception as inst:
            self.log.critical(inst)

    def brightness_query(self):
        try:
            if self.ostype == 'rpi':
                my_cmd = os.popen('sudo cat /sys/class/backlight/4d-hats/actual_brightness', 'r').read()
                my_cmd = my_cmd.rstrip()
                self.log.info('Brightness level returned as {}'.format(my_cmd))
                return my_cmd
            else:
                my_cmd = 15
                return my_cmd
        except Exception as inst:
            self.log.critical(inst)

    # called premade script to create ramdrive
    # TODO see why ramdrive is getting created upon reboot.
    def ram_drive_create(self):
        print("Creating RAMDRIVE")
        cwd = os.getcwd()
        path = cwd + "/scripts/ram_drive_create.sh"
        if os.path.exists("/var/ramdrive"):
            print("RAM DRIVE exists...")
        else:
            try:
                ret = subprocess.Popen(['sh', path])
            except:
                pass
