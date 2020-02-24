import faulthandler

faulthandler.enable()
import sys
import signal
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QTimer, QFile
from PySide2.QtGui import QFontDatabase, QFont
from PySide2.QtWidgets import QMainWindow, QTableWidgetItem, QWidget

# mylibraries
from config import Config
from logger import Logger
from support.support import Support
from signaling import Signaling
from securitylevel import SecurityLevel
from gui_coderates import Guicoderate
from gui_frequencies import GuiFrequencies
from gui import QTResources  # do not remove this !!!


class Mainwindow(object):
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, commander, codegen, config, logger, support):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.window = None
        self.config = config
        self.logger = logger
        self.support = support
        self.securitylevel = SecurityLevel(logger=logger)
        self.log = Logger.log
        self.commander = commander
        self.startup_processes()
        self.guicode = Guicoderate(window=self.window, codegen=codegen, config=config, logger=logger)
        self.freqcode = GuiFrequencies(window=self.window, codegen=codegen, config=config, logger=logger)
        self.signaling = Signaling(window=self.window, commander=self.commander, config=self.config, logger=self.logger,
                                   support=self.support)
        self.log.debug("{} init complete...".format(__name__))

    # *****************************************************************************
    def startup_processes(self):
        self.config_file_load()
        self.loadscreen()
        self.exit_signalling()
        self.screen_fullscreen()
        self.fonts_list()
        self.securitylevel.set_security_level("technician", self.window)

    # *****************************************************************************
    def fonts_list(self):
        """
        list available fonts
        """
        self.fontDB = QFontDatabase()
        self.fontDB.addApplicationFont(":/FONTS/FONTS/digital-7.ttf")
        self.fontDB.addApplicationFont(":/FONTS/FONTS/SiemensSlab_Prof_BlackItalic.ttf")
        # self.siemensslab = QFont("Siemens Slab", 64, 1)
        # self.digital7font = QFont("Digital-7", 64, 1)
        # self.window.LBL_pri_tach_freq.setFont(self.digital7font)

    # *****************************************************************************
    def screen_fullscreen(self):
        if self.support.ostype == 'rpi':
            self.window.showFullScreen()
            self.log.debug("Window set to fullscreen...")

    # ******************************************************************************
    def config_file_load(self):
        Mainwindow.display_brightness = self.config.display_brightness
        Mainwindow.guiname = self.config.guiname
        Mainwindow.poll_timer_interval = self.config.poll_timer_interval
        Mainwindow.local_timer_interval = self.config.local_timer_interval
        Mainwindow.sense_timer_interval = self.config.sense_timer_interval
        Mainwindow.switch_timer_interval = self.config.switch_timer_interval
        Mainwindow.screen_brightness_max = self.config.screen_brightness_max
        Mainwindow.screen_brightness_min = self.config.screen_brightness_min

    # ******************************************************************************
    def exit_signalling(self):
        signal.signal(signal.SIGINT, self.exit_application)
        signal.signal(signal.SIGTERM, self.exit_application)
        self.log.debug("Setting up exit signaling...")

    # ******************************************************************************
    def loadscreen(self):
        try:
            ui_file = QFile(Mainwindow.guiname)
            ui_file.open(QFile.ReadOnly)
            loader = QUiLoader()
            self.window = loader.load(ui_file)
            ui_file.close()
            self.window.show()
            self.log.debug('Loading screen ' + self.guiname)
        except FileNotFoundError:
            self.log.debug("Could not find {}".format(self.guiname))  # CATCHES EXIT SHUTDOWN

    def exit_application(self, signum, frame):
        self.log.info("Starting shutdown")
        self.log.debug("Received signal from signum: {} with frame:{}".format(signum, frame))
        self.shutdown()

    # ************************************************************************************
    # TODO: only allow items that have previsouly run. items here are running that havent been perfromed
    # TODO: try "ATEXIT"

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
