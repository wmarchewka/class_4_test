#libraries
import logging
import pigpio

#my libraries
import gpio
import logger
import config
import pollperm

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

    def __init__(self, name, speedgen, callback, pin0, pin1, pin0_debounce, pin1_debounce, thresholds=None):

        self.logger = logger.Logger()
        self.log = self.logger
        self.log = logging.getLogger(__name__)
        self.config = config.Config()
        self.gpio = gpio.Gpio().gpio
        self.pollperm = pollperm.Pollperm()
        self.sg = speedgen
        self.name = name
        self.callback = callback
        self.pin0 = pin0
        self.pin1 = pin1
        self.pin0_debounce = pin0_debounce
        self.pin1_debounce = pin1_debounce
        self.thresholds = thresholds
        self.rotary_callback_list = []
        self.callback_list = []
        self.create_rotary()

    def create_rotary(self):
        self.create_callback(self.pin0, self.pin1, self.pin0_debounce, self.pin1_debounce)

    def create_callback(self, pin0, pin1, pin0_debounce, pin1_debounce):
        """creates list of rotary callbacks so that all the callbacks can
        be disabled at once
        """
        self.rotary_callback_list.append(self.pin_setup(pin0, pin0_debounce))
        self.rotary_callback_list.append(self.pin_setup(pin1, pin1_debounce))

    def pin_setup(self, pin, pin_debounce):
        self.gpio.set_mode(pin, pigpio.INPUT)
        self.gpio.set_pull_up_down(pin, pigpio.PUD_OFF)
        self.gpio.set_glitch_filter(pin, pin_debounce)  # microseconds
        cb = self.gpio.callback(pin, pigpio.EITHER_EDGE, self.rotary_callback)
        self.callback_list.append((pin, pigpio.EITHER_EDGE, self.rotary_callback))
        self.log.debug("Setting up Rotary Pins BCM PIN:{}  DEBOUNCE:{}".format(pin, pin_debounce))
        return cb

    # *****************************************************************************************************
    def rotary_callback(self, pin_num: int, level: int, tick: int, simulate: int = False, sim_pins: list = None) -> None:
        """receives callback from interrupt on pin pair for a decoder, calls a routine that is passed to the
        class as a callback
        :rtype: list
        :param pin_num: what pin caused the interrupt
        :param level: pin level that caused the interrupt (not used)
        :param tick: actual tick time the interrupt occurered
        :param simulate: do you want to simlulate the pins generating an interrupt
        :param sim_pins: what pins to send simulate an interrupt occured
        """
        self.log.debug("#######################################################")
        self.pollperm.polling_prohitied = (True, __name__)
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
            #self.disable_interrupts()
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
            speed = -1
            for t in reversed(self.thresholds):
                if (delta / 1000) > t:
                    speed = speed + 1
            self.log.debug("Speed threshold {}".format(speed))
            self.log.debug("Delta time : {} ms".format(delta / 1000))
            self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time))
            self.callback(self.sg, speed, direction)

    def disable_interrupts(self):
        for r in self.rotary_callback_list:
            self.log.debug("Cancel Interrupts on {}".format(r))
            r.cancel()

    def enable_interrupts(self):
        pass
        # for cb in self.callback_list:
        #     self.gpio.callback(cb[0],cb[1],cb[2])

