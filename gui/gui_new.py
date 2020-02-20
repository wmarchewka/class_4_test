import faulthandler
faulthandler.enable()
import datetime
import logging
import os
import socket
import subprocess
import sys
import signal
import threading
import psutil
import numpy as np
from numpy import sin, pi
from PySide2.QtUiTools import QUiLoader
from PySide2 import QtCore
from PySide2.QtCore import QTimer, QFile
from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QMainWindow, QTableWidgetItem, QWidget

#mylibraries
import config
import logger
import support.support

class Mainwindow(QMainWindow):

    logging.debug("Instantiating {} class...".format(__qualname__))


    def __init__(self, commander, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.window = None
        self.config = config.Config()
        self.logger = logger.Logger()
        self.support = support.support.Support()
        self.commander = commander
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))


    def signaling(self):
        # primary and secondary gain encoders value change
        self.window.QDIAL_primary_gain.valueChanged.connect(self.commander.primary_gain_change)
        self.window.QDIAL_secondary_gain.valueChanged.connect(self.commander.secondary_gain_change)

        # speed 1 and speed2 value change
        self.window.QDIAL_speed_1.valueChanged.connect(self.commander.primary_gain_change)
        self.window.QDIAL_speed_2.valueChanged.connect(self.commander.primary_gain_change)

    def startup_processes(self):
        self.config_file_load()
        self.loadscreen()
        self.exit_signalling()
        self.screen_fullscreen()

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
        logging.shutdown()
        sys.exit(0)