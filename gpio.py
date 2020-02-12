import pigpio
import sys


class Gpio(object):

    def __init__(self):
        print("gpio init")

    @classmethod
    def init_gpio(cls):
        cls.GPIO = None
        if sys.platform != 'win32':
            cls.GPIO = pigpio.pi()
        print("gpio class init")
        cls.init = True
        return cls.GPIO
