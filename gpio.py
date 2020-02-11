import pigpio

class Gpio(object):
    def __init__(self):
        self.GPIO = pigpio.pi()
