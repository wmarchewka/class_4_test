import os.path, pkgutil
import commander
import basiclogger
import logging
import gui.gui
import sys
import rotary
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer
#pkgpath = os.path.dirname(logger.__file__)
#a =  ([name for _, name, _ in pkgutil.iter_modules([pkgpath])])
#print(a)


if __name__ == '__main__':

    logging.debug("Initiating {} class...".format(__name__))

    app = QApplication(['PORTABLE TESTER'])
    w = gui.gui.Mainwindow()
    r = rotary.Rotary()
    c = commander.Commander()

    # the timer calls itself every 100ms to allow to break in GUI
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # runs every 100ms
    timer.start(100)
    sys.exit(app.exec_())


