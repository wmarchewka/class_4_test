# libraries
import logging
import pigpio

# my libraries
from gpio import Gpio
from logger import Logger
from config import Config
from pollperm import Pollperm


class Rotary():
    logging.info("Instantiating {} class...".format(__qualname__))

    SPEED_FAST = 1
    SPEED_SLOW = 0
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    last_interrupt_time = 0
    first_pin = None
    second_pin = None

    def __init__(self, name, callback, pin_0, pin_1, pin_0_debounce, pin_1_debounce):
        super().__init__()
        self.logger = Logger()
        self.log = self.logger
        self.log = logging.getLogger()
        self.config = Config()
        self.gpio = Gpio().gpio
        self.pollperm = Pollperm()
        self.name = name
        self.callback = callback
        self.pin_0 = pin_0
        self.pin_1 = pin_1
        self.pin_0_debounce = pin_0_debounce
        self.pin_1_debounce = pin_1_debounce
        self.rotary_callback_list = []
        self.callback_list = []
        self.create_rotary()
        self.log.debug("Creating rotary encoder:{} BCM PIN0:{}  BCM PIN1:{}".format(self.name, self.pin_0, self.pin_1))
        self.log.debug("DEBOUNCE PIN 0:{}  DEBOUNCE PIN 1:{}".format(self.name, self.pin_0_debounce, self.pin_1_debounce))
        self.log.debug("Callback:{}".format(self.callback))
        self.log.debug("{} init complete...".format(__name__))

    # ********************************************************************************************************************
    def create_rotary(self):
        # creates a callback for both pins that points to same callback
        self.create_callback(self.pin_0, self.pin_1, self.pin_0_debounce, self.pin_1_debounce)

    # ********************************************************************************************************************
    def create_callback(self, pin0, pin1, pin0_debounce, pin1_debounce):
        """creates list of rotary callbacks so that all the callbacks can
        be disabled at once
        """
        self.rotary_callback_list.append(self.pin_setup(pin0, pin0_debounce))
        self.rotary_callback_list.append(self.pin_setup(pin1, pin1_debounce))

    # ********************************************************************************************************************
    def pin_setup(self, pin, pin_debounce):
        self.gpio.set_mode(pin, pigpio.INPUT)
        self.gpio.set_pull_up_down(pin, pigpio.PUD_OFF)
        self.gpio.set_glitch_filter(pin, pin_debounce)  # microseconds
        cb = self.gpio.callback(pin, pigpio.EITHER_EDGE, self.interrupt_callback)
        self.callback_list.append((pin, pigpio.EITHER_EDGE, self.interrupt_callback))
        return cb

    # *****************************************************************************************************
    def interrupt_callback(self, pin_num: int, level: int, tick: int, simulate: int = False,
                           sim_pins: list = None) -> None:
        """receives callback from interrupt on pin pair for a decoder, calls a routine that is passed to the
        class as a callback
        :rtype: list
        :param pin_num: what pin caused the interrupt
        :param level: pin level that caused the interrupt (not used)
        :param tick: actual tick time the interrupt occurered
        :param simulate: do you want to simlulate the pins generating an interrupt
        :param sim_pins: what pins to send simulate an interrupt occured
        """
        first_pin = 0
        second_pin = 0
        self.log.debug("#######################################################")
        self.pollperm.polling_prohitied = (True, __name__)
        self.log.debug("BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        if self.first_pin is None:
            if simulate:
                pin_num = sim_pins[0]
                first_pin = sim_pins[0]
                second_pin = sim_pins[1]
                self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
                pin_num = sim_pins[1]
            else:
                first_pin = pin_num
                pin_num = None
            self.log.debug("First pin set as {}".format(first_pin))
        if pin_num is not None and first_pin:
            if simulate:
                second_pin = sim_pins[1]
            else:
                second_pin = pin_num
            self.log.debug("Second pin set as {}".format(second_pin))
        if first_pin and second_pin:
            # self.disable_interrupts()
            if first_pin == self.pin_0 and second_pin == self.pin_1:
                direction = Rotary.CLOCKWISE
                self.log.debug("Direction is CLOCKWISE: {}".format(direction))
            elif first_pin == self.pin_1 and second_pin == self.pin_0:
                direction = Rotary.ANTI_CLOCKWISE
                self.log.debug("Direction is ANTICLOCKWISE: {}".format(direction))
            else:
                direction = Rotary.DIRECTION_ERROR
                self.log.debug("Direction is ERROR: {}".format(direction))
            first_pin = None
            second_pin = None
            delta = tick - self.last_interrupt_time
            if self.last_interrupt_time == 0:
                delta = 1000000  # since first value will have nothing to compare to set at 1000ms
            self.last_interrupt_time = tick
            self.log.debug("Delta time : {} ms".format(delta / 1000))
            self.log.debug("Last saved time : {}".format(self.last_interrupt_time))
            self.callback(delta, direction, simulate)

    # ********************************************************************************************************************
    def disable_interrupts(self):
        for r in self.rotary_callback_list:
            self.log.debug("Cancel Interrupts on {}".format(r))
            r.cancel()
    #********************************************************************************************************************
    def enable_interrupts(self):
        pass
        # for cb in self.callback_list:
        #     self.gpio.callback(cb[0],cb[1],cb[2])
