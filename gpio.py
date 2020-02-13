import pigpio
import sys


class Gpio(object):

    _class_property = None
    _name_inst = None

    def __init__(self):
        pass

    @classmethod
    def init_gpio(cls):
        cls.GPIO = None
        os = sys.platform
        if os == 'linux':
            cls.GPIO = pigpio.pi()
        print("pigpio init")
        print(cls.GPIO.get_pigpio_version())
        cls.init = True
        return cls.GPIO

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