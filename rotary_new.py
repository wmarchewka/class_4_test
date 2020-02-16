import logging
import logger
import time
import config
import gpio
import pigpio


class Rotary(object):
    logging.debug("Initiating {} class...".format(__qualname__))

    SPEED_FAST = 1
    SPEED_SLOW = 0
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    last_interrupt_time = 0
    first_pin = None
    second_pin = None

    def __init__(self, speedgen, callback, pin0, pin1, pin0_debounce, pin1_debounce, thresholds=None):

        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.config = config.Config()
        self.gpio = gpio.Gpio().gpio
        self.sg = speedgen
        self.callback = callback
        self.thresholds = thresholds
        self.pin0 = pin0
        self.pin1 = pin1
        self.cb0 = None
        self.cb1 = None
        self.cb0 = self.pin_setup(pin0, pin0_debounce)
        self.cb1 = self.pin_setup(pin1, pin1_debounce)


    def pin_setup(self, pin, pin_debounce):
        self.gpio.set_mode(pin, pigpio.INPUT)  # BCM4
        self.gpio.set_pull_up_down(pin, pigpio.PUD_OFF)
        self.gpio.set_glitch_filter(pin, pin_debounce)  # microseconds
        self.cb = self.gpio.callback(pin, pigpio.EITHER_EDGE, self.rotary_callback)
        return self.cb

    # *****************************************************************************************************
    # ENCODER SPEED 1				BCM4
    def rotary_callback(self, pin_num: int, level: int, tick: int, simulate: int = False, sim_pins: list = None) -> None:
        """receives callback from interrupt on pin pair for a decoder, calls a routine that is passed to the
        class as a callback
        :rtype: list
        :param pin_num: what pin caused the interrupt
        :param level: pin level that caused the interrupt (not used)
        :param tick: actual tick time the interrupt occurered
        :param simulate: do you want to simlulate the pins generating an interrupt
        :param sim_pins: waht pins to send simulate an interrupt occured
        """
        # self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        # self.pollperm.polling_prohitied = (True, __name__)
        self.log.debug("BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        if simulate:
            Rotary.first_pin = sim_pins[0]
            Rotary.second_pin = sim_pins[1]
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        if Rotary.first_pin is None:
            if simulate:
                Rotary.first_pin = sim_pins[0]
            else:
                Rotary.first_pin = pin_num
            self.log.debug("First pin set as {}".format(pin_num))
            pin_num = None
        if pin_num is not None and Rotary.first_pin:
            if simulate:
                Rotary.second_pin = sim_pins[1]
            else:
                Rotary.second_pin = pin_num
            self.log.debug("Second pin set as {}".format(Rotary.second_pin))
        if Rotary.first_pin and Rotary.second_pin:
            if Rotary.first_pin == self.pin0 and Rotary.second_pin == self.pin1:
                direction = Rotary.CLOCKWISE
                self.log.debug("Direction is CLOCKWISE")
            elif Rotary.first_pin == self.pin1 and Rotary.second_pin == self.pin0:
                direction = Rotary.ANTI_CLOCKWISE
                self.log.debug("Direction is ANTICLOCKWISE")
            else:
                direction = Rotary.DIRECTION_ERROR
            self.log.debug("Direction is {}".format(direction))
            Rotary.first_pin = None
            Rotary.second_pin = None
            delta = tick - Rotary.last_interrupt_time
            if Rotary.last_interrupt_time == 0:
                delta = 0
            Rotary.last_interrupt_time = tick
            speed = 0
            for t in reversed(self.thresholds):
                if (delta / 1000) > t:
                    speed = speed + 1
            self.log.debug("Speed threshold {}".format(speed))
            self.log.debug("Delta time : {} ms".format(delta / 1000))
            self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time))
            self.callback(self.sg, speed, direction)

    def disable_interrupts(self):
        self.cb0.cancel()
        self.cb1.cancel()
