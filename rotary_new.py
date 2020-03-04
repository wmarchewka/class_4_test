# libraries
import pigpio

# my libraries
from gpio import Gpio
from logger import Logger


class Rotary(object):

    Logger.log.info("Instantiating {} class...".format(__qualname__))

    SPEED_FAST = 1
    SPEED_SLOW = 0
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    last_interrupt_time = 0
    first_pin = None
    second_pin = None

    def __init__(self, config, logger, gpio, pollperm, name, callback, pin_0, pin_1, pin_0_debounce, pin_1_debounce):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.logger = logger
        self.log = Logger.log
        self.config = config
        self.gpio = gpio
        self.pi_gpio = self.gpio.gpio
        self.pollperm = pollperm
        self.name = name
        self.callback = callback
        self.pin_0 = pin_0
        self.pin_1 = pin_1
        self.pin_0_debounce = pin_0_debounce
        self.pin_1_debounce = pin_1_debounce
        self.rotary_callback_list = []
        self.callback_list = []
        self.create_rotary()
        self.log.debug("{} init complete...".format(__name__))

    # ********************************************************************************************************************
    def create_rotary(self):
        # creates a callback for both pins that points to same callback
        self.create_callback(pin0= self.pin_0, pin1= self.pin_1, pin0_debounce= self.pin_0_debounce, pin1_debounce= self.pin_1_debounce)
        self.log.debug("Creating rotary encoder:{} BCM PIN0:{}  BCM PIN1:{}".format(self.name, self.pin_0, self.pin_1))
        self.log.debug("DEBOUNCE PIN 0:{}  DEBOUNCE PIN 1:{}".format(self.pin_0_debounce, self.pin_1_debounce))
        self.log.debug("Callback:{}".format(self.callback))

    # ********************************************************************************************************************
    def create_callback(self, pin0, pin1, pin0_debounce, pin1_debounce):
        """creates list of rotary callbacks so that all the callbacks can
        be disabled at once
        """
        self.rotary_callback_list.append(self.pin_setup(pin0, pin0_debounce))
        self.rotary_callback_list.append(self.pin_setup(pin1, pin1_debounce))

    # ********************************************************************************************************************
    def pin_setup(self, pin, pin_debounce):
        self.pi_gpio.set_mode(pin, pigpio.INPUT)
        self.pi_gpio.set_pull_up_down(pin, pigpio.PUD_OFF)
        self.pi_gpio.set_glitch_filter(pin, pin_debounce)  # microseconds
        cb = self.pi_gpio.callback(pin, pigpio.EITHER_EDGE, self.interrupt_callback)
        self.callback_list.append((pin, pigpio.EITHER_EDGE, self.interrupt_callback))
        return cb

    # *****************************************************************************************************
    def interrupt_callback(self, pin_num, level, tick, simulate = False,
                           sim_pins = None):
        """receives callback from interrupt on pin pair for a decoder, calls a routine that is passed to the
        class as a callback
        :rtype: list
        :param pin_num: what pin caused the interrupt
        :param level: pin level that caused the interrupt (not used)
        :param tick: actual tick time the interrupt occurered
        :param simulate: do you want to simlulate the pins generating an interrupt
        :param sim_pins: what pins to send simulate an interrupt occured
        """
        self.pollperm.polling_prohibited = (True, __name__)
        if self.first_pin is None:
            if simulate:
                pin_num = sim_pins[0]
                self.first_pin = sim_pins[0]
                self.second_pin = sim_pins[1]
                self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
                pin_num = sim_pins[1]
            else:
                self.first_pin = pin_num
                pin_num = None
            self.log.debug("###########################################################################################")
            self.log.debug("BCM PIN:{}  LEVEL:{}   TICK:{}  SIMULATED:{}".format(pin_num, level, tick, simulate))
            self.log.debug("First pin set as {}".format(self.first_pin))
        if pin_num is not None and self.first_pin:
            if simulate:
                self.second_pin = sim_pins[1]
            else:
                self.second_pin = pin_num
            self.log.debug("#############################################")
            self.log.debug("BCM PIN:{}  LEVEL:{}   TICK:{}  SIMULATED:{}".format(pin_num, level, tick, simulate))
            self.log.debug("Second pin set as {}".format(self.second_pin))
        if self.first_pin and self.second_pin:
            # self.disable_interrupts()
            if self.first_pin == self.pin_0 and self.second_pin == self.pin_1:
                direction = Rotary.CLOCKWISE
                self.log.debug("Direction is CLOCKWISE: {}".format(direction))
            elif self.first_pin == self.pin_1 and self.second_pin == self.pin_0:
                direction = Rotary.ANTI_CLOCKWISE
                self.log.debug("Direction is ANTICLOCKWISE: {}".format(direction))
            else:
                direction = Rotary.DIRECTION_ERROR
                self.log.debug("Direction is ERROR: {}".format(direction))
            self.first_pin = None
            self.second_pin = None
            delta = tick - self.last_interrupt_time
            if self.last_interrupt_time == 0:
                delta = 1000000  # since first switches_value will have nothing to compare to set at 1000ms
            self.last_interrupt_time = tick
            self.log.debug("Delta time : {} ms".format(delta / 1000))
            self.log.debug("Last saved time : {}".format(self.last_interrupt_time))
            self.callback(delta=delta, direction=direction, simulate=simulate)

    # ********************************************************************************************************************
    def disable_interrupts(self):
        for r in self.rotary_callback_list:
            self.log.debug("Cancel Interrupts on {}".format(r))
            r.cancel()
    #********************************************************************************************************************
    def enable_interrupts(self):
        pass
        # for cb in self.callback_list:
        #     self.pi_pgio.callback(cb[0],cb[1],cb[2])
