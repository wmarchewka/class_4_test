import os.path, pkgutil
import commander
import logger
import gpio
import gui.gui
import rotary
from PySide2.QtWidgets import QApplication
from PySide2.QtCore import QTimer
#pkgpath = os.path.dirname(logger.__file__)
#a =  ([name for _, name, _ in pkgutil.iter_modules([pkgpath])])
#print(a)


if __name__ == '__main__':
    app = QApplication(['PORTABLE TESTER'])
    g = gpio.Gpio()
    w = gui.gui.Mainwindow()
    r = rotary.Rotary()
    #c = commander.Commander()

    # the timer calls itself every 100ms to allow to break in GUI
    timer = QTimer()
    timer.timeout.connect(lambda: None)  # runs every 100ms
    timer.start(100)
    app.exit(app.exec_())



