import faulthandler
faulthandler.enable()
import logging
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
from commander import Commander

class PortableTester(object):
    def __init__(self):
        self.logger = Logger()
        self.log = Logger.log
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--debug', '-d', nargs="+", type=str)
        self.args = self.parser.parse_args()
        self.log.debug("Arguments passed into script: {}".format(self.args))
        self.logging_args = self.args.debug
        self.logging_level = logging.DEBUG
        if self.logging_args:
            self.level_config = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, "CRITICAL": logging.CRITICAL}  # etc.
            self.logging_level = self.level_config[self.logging_args[0]]
        Logger(level=self.logging_level)
        self.commander = Commander()


if __name__ == "__main__":
    app = QApplication(['PORTABLE TESTER'])
    app.setWheelScrollLines(1)
    # app.setStyle("fusion")
    porttest = PortableTester()
    # the timer calls itself every 100ms to allow to break in GUI
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # runs every 100ms
    timer.start(100)
    app.exit(app.exec_())