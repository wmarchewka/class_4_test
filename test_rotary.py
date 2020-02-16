#import basiclogger
import rotary_new
import logger
import time
import logging
import speedgen

class Testrotary(object):

    #logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):

        self.speedgen = speedgen.Speedgen()
        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.sg = 0
        self.thresholds = (5, 15, 20, 50, 100, 1000)
        self.pin0 = 4
        self.pin1 = 14
        self.pin0_debounce = 1000
        self.pin1_debounce = 1000
        #self.speedgen.set_speed_signal(chip_select, speed, direction)
        self.r = rotary_new.Rotary(self.sg, self.speedgen.set_speed_signal,self.pin0,self.pin1,self.pin0_debounce, self.pin1_debounce, self.thresholds)
        #self.r.disable_interrupts()

    def rotary_cb(self, direction, speed):
        self.log.disabled = False
        self.log.debug("Callback  Direction:{}  Speed:{}".format(direction, speed))


if __name__ == "__main__":
    rn = Testrotary()
    while(True):
        time.sleep(1)
# self.rotary = 0
# pin = 1
# sim = True
# int_time = time.time()
# self.first_pin = 1
# self.second_pin = 2
# self.pin_level = 1
# self.thresholds = (0.010, 0.020, 0.030, 0.040, 0.050)
# ret = self.rotary_0(self.rotary, self.first_pin, self.pin_level, int_time, sim, self.thresholds,
#                     (self.first_pin, self.second_pin))
# self.log.debug(ret)
# sim = False
# int_time = time.time()
# ret = self.rotary_0(self.rotary, self.second_pin, self.pin_level, int_time, sim, self.thresholds,
#                     (self.first_pin, self.second_pin))
# self.log.debug(ret)
# time.sleep(0.010)
# int_time = time.time()
# ret = self.rotary_0(self.rotary, self.first_pin, self.pin_level, int_time, sim, self.thresholds,
#                     (self.first_pin, self.second_pin))
# self.log.debug(ret)
# int_time = time.time()
# ret = self.rotary_0(self.rotary, self.first_pin, self.pin_level, int_time, sim, self.thresholds,
#                     (self.first_pin, self.second_pin))
# self.log.debug(ret)
# time.sleep(0.030)
# int_time = time.time()
# ret = self.rotary_0(self.rotary, self.second_pin, self.pin_level, int_time, sim, self.thresholds,
#                     (self.first_pin, self.second_pin))
# self.log.debug(ret)
#
# time.sleep(0.030)
# int_time = time.time()
# ret = self.rotary_0(self.rotary, self.second_pin, self.pin_level, int_time, sim, self.thresholds,
#                     (self.first_pin, self.second_pin))
# self.log.debug(ret)
#
# time.sleep(0.045)
# int_time = time.time()
# ret = self.rotary_0(self.rotary, self.second_pin, self.pin_level, int_time, sim, self.thresholds,
#                     (self.first_pin, self.second_pin))
# self.log.debug(ret)
