import gpio
import config
import pigpio
import logging
import time
import digpots
import decoder
import logger
import speedgen
import pollperm
import spi
import codegen

class Rotary(object):

    logging.debug("Initiating {} class...".format(__qualname__))

    SPEED_FAST = 1
    SPEED_SLOW = 0
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    last_interrupt_time_rotary0_pin0 = 0
    last_interrupt_time_rotary0_pin1 = 0
    last_interrupt_time_rotary1_pin0 = 0
    last_interrupt_time_rotary1_pin1 = 0
    last_interrupt_time_rotary2_pin0 = 0
    last_interrupt_time_rotary2_pin1 = 0
    last_interrupt_time_rotary3_pin0 = 0
    last_interrupt_time_rotary3_pin1 = 0
    zone = [0, 0, 0, 0]  # used to calculate direction
    prevZone = [0, 0, 0, 0]
    rotary_num = [0, 1, 2, 3]  # ID for each encoder
    DIGITAL_POT_0 = 0
    DIGITAL_POT_1 = 1

    def __init__(self):

        self.init = True
        self.config = config.Config()
        self.spi = spi.SPI()
        self.gpio = gpio.Gpio().gpio
        self.speedgen = speedgen.Speedgen()
        self.pollperm = pollperm.Pollperm()
        self.digpots = digpots.DigPots()
        self.decoder = decoder.Decoder()
        self.codegen = codegen.Codegen()
        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.rotary_interrupts(True)
        self.enable_callbacks()
        self.log.debug("{} init complete...".format(__name__))

    # *****************************************************************************************************
    def enable_interrupts(self):
        self.log.debug('ROTARY INTERRUPTS ENABLING...')
        try:
            # switch 3 ENCODER SPEED 1
            self.gpio.set_mode(self.config.rotary_0_pins[0], pigpio.INPUT)  # BCM4
            self.gpio.set_pull_up_down(self.config.rotary_0_pins[0], pigpio.PUD_OFF)
            # switch 3 ENCODER SPEED 1
            self.gpio.set_mode(self.config.rotary_0_pins[1], pigpio.INPUT)  # BCM14
            self.gpio.set_pull_up_down(self.config.rotary_0_pins[1], pigpio.PUD_OFF)

            # switch 4 ENCODER SPEED 2
            self.gpio.set_mode(self.config.rotary_1_pins[0], pigpio.INPUT)  # BMC15
            self.gpio.set_pull_up_down(self.config.rotary_1_pins[0], pigpio.PUD_OFF)
            # switch 4 ENCODER SPEED 2
            self.gpio.set_mode(self.config.rotary_1_pins[1], pigpio.INPUT)  # BMC22
            self.gpio.set_pull_up_down(self.config.rotary_1_pins[1], pigpio.PUD_OFF)

            # switch 5 PRIMARY GAIN
            self.gpio.set_mode(self.config.rotary_2_pins[0], pigpio.INPUT)  # BCM23
            self.gpio.set_pull_up_down(self.config.rotary_2_pins[0], pigpio.PUD_OFF)
            # switch 5 PRIMARY GAIN
            self.gpio.set_mode(self.config.rotary_2_pins[1], pigpio.INPUT)  # BCM24
            self.gpio.set_pull_up_down(self.config.rotary_2_pins[1], pigpio.PUD_OFF)

            # switch 6 SECONDARY GAIN
            self.gpio.set_mode(self.config.rotary_3_pins[0], pigpio.INPUT)  # BCM25
            self.gpio.set_pull_up_down(self.config.rotary_3_pins[0], pigpio.PUD_OFF)
            # switch 6 SECONDARY GAIN
            self.gpio.set_mode(self.config.rotary_3_pins[1], pigpio.INPUT)  # BCM12
            self.gpio.set_pull_up_down(self.config.rotary_3_pins[1], pigpio.PUD_OFF)
        except Exception as err:
            self.log.exception('Error in gpio setup {}'.format(err.args))

    # *****************************************************************************************************
    def enable_callbacks(self) -> bool:
        """routine to enable callbacks of the rotary interrupt pins
        :return:
        """
        try:
            # SW3-B ENCODER SPEED 1
            self.rotary_0_0_callback = self.gpio.callback(self.config.rotary_0_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_0_pin_0)
            self.rotary_0_1_callback = self.gpio.callback(self.config.rotary_0_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_0_pin_1)
            self.gpio.set_glitch_filter(self.config.rotary_0_pins[0],
                                        self.config.rotary_0_pin_0_debounce)  # microseconds
            self.gpio.set_glitch_filter(self.config.rotary_0_pins[1],
                                        self.config.rotary_0_pin_1_debounce)  # microseconds

            # SW4-B ENCODER SPEED 2
            self.rotary_1_0_callback = self.gpio.callback(self.config.rotary_1_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_1_pin_0)
            self.rotary_1_1_callback = self.gpio.callback(self.config.rotary_1_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_1_pin_1)
            self.gpio.set_glitch_filter(self.config.rotary_1_pins[0],
                                        self.config.rotary_1_pin_0_debounce)  # microseconds
            self.gpio.set_glitch_filter(self.config.rotary_1_pins[1],
                                        self.config.rotary_1_pin_1_debounce)  # microseconds

            # SW5-B PRIMARY CARRIER GAIN
            self.rotary_2_0_callback = self.gpio.callback(self.config.rotary_2_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_2_pin_0)
            self.rotary_2_1_callback = self.gpio.callback(self.config.rotary_2_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_2_pin_1)
            self.gpio.set_glitch_filter(self.config.rotary_2_pins[0],
                                        self.config.rotary_2_pin_0_debounce)  # microseconds
            self.gpio.set_glitch_filter(self.config.rotary_2_pins[1],
                                        self.config.rotary_2_pin_1_debounce)  # microseconds

            # SW6-B SECONDARY CARRIER GAIN
            self.rotary_3_0_callback = self.gpio.callback(self.config.rotary_3_pins[0], pigpio.EITHER_EDGE,
                                                          self.rotary_3_pin_0)
            self.rotary_3_1_callback = self.gpio.callback(self.config.rotary_3_pins[1], pigpio.EITHER_EDGE,
                                                          self.rotary_3_pin_1)
            self.gpio.set_glitch_filter(self.config.rotary_3_pins[0],
                                        self.config.rotary_3_pin_0_debounce)  # microseconds
            self.gpio.set_glitch_filter(self.config.rotary_3_pins[1],
                                        self.config.rotary_3_pin_1_debounce)  # microseconds

            return True
        except AttributeError:
            self.log.exception("Error setting up gpio callbacks", exc_info=True)
            return False

    # *****************************************************************************************************
    def disable_interrupts(self):
        # SW3-B ENCODER SPEED 1
        self.rotary_0_0_callback.cancel()
        self.rotary_0_1_callback.cancel()

        # SW4-B ENCODER SPEED 2
        self.rotary_1_0_callback.cancel()
        self.rotary_1_1_callback.cancel()

        # SW5-B PRIMARY CARRIER GAIN
        self.rotary_2_0_callback.cancel()
        self.rotary_2_1_callback.cancel()

        # SW6-B SECONDARY CARRIER GAIN
        self.rotary_3_0_callback.cancel()
        self.rotary_3_1_callback.cancel()

    # *****************************************************************************************************
    def rotary_interrupts(self, value: bool) -> None:
        """passing true will enable interrupts, false will disable
        :param value:
        """
        if value is False:
            self.log.debug('Disabling rotary interrupts')
            self.disable_interrupts()
        elif value is True:
            self.log.debug('Enabling rotary interrupts')
            self.enable_interrupts()
    # *****************************************************************************************************
    def get_speed(self, delta: float) -> int:
        #TODO make this have multiple levels 1 - 5 slow to fast
        """Pass in the delta from the interrupt routine and aaply a threshold to
        determine if encoder was turn fast or slow.
        :param delta: change in interrupt time
        :return: return fast=1 slow=0
        """
        if delta < self.config.speed_threshold:  # threshold for fast rotation xx ms between interrupts
            speed = Rotary.SPEED_FAST
            speed_text = 'FAST'
        else:
            speed = Rotary.SPEED_SLOW
            speed_text = 'SLOW'
        self.log.debug(
            'Speed:{}  Time:{}  Threshold:{} seconds'.format(speed_text, delta, self.config.speed_threshold))
        return speed

    # *****************************************************************************************************
    def get_direction(self, pins: list, rotary_number: int) -> int:
        """Pass in what the pin states are for the encoders and this determines
        what direction the encoders are turning clockwise or anticlockwise.
        :param pins: list of pin state
        :param rotary_number: rotary encoder number
        :return: direction: clk=1 anticlk =-1
        """
        str_direction = ""
        direction = 0  # zero is the default error value 1=CLOCKWISE -1=anticlockwise
        self.log.debug('Pins:{}  Rotary_num:{}'.format(pins, rotary_number))
        if pins == [0, 0]:  # determine direction from quadrature input
            Rotary.zone[rotary_number] = 0
            if Rotary.prevZone[rotary_number] == 1:  # done
                direction = Rotary.CLOCKWISE
            elif Rotary.prevZone[rotary_number] == 2:  # done
                direction = Rotary.ANTI_CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        elif pins == [0, 1]:
            Rotary.zone[rotary_number] = 1
            if Rotary.prevZone[rotary_number] == 3:  # done
                direction = Rotary.CLOCKWISE
            elif Rotary.prevZone[rotary_number] == 0:  # done
                direction = Rotary.ANTI_CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        elif pins == [1, 0]:
            Rotary.zone[rotary_number] = 2
            if Rotary.prevZone[rotary_number] == 0:  # done
                direction = Rotary.CLOCKWISE
            elif Rotary.prevZone[rotary_number] == 3:  # done
                direction = Rotary.ANTI_CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        elif pins == [1, 1]:
            Rotary.zone[rotary_number] = 3
            if Rotary.prevZone[rotary_number] == 1:  # done
                direction = Rotary.ANTI_CLOCKWISE
            elif Rotary.prevZone[rotary_number] == 2:  # done
                direction = Rotary.CLOCKWISE
            else:
                self.log.debug("ERROR in Rotary")
                direction = Rotary.DIRECTION_ERROR
        if direction == Rotary.CLOCKWISE:
            str_direction = "CLOCKWISE"
        elif direction == Rotary.ANTI_CLOCKWISE:
            str_direction = "ANTICLOCKWISE"
        elif direction == 0:
            str_direction = "ERROR"
        self.log.debug('ZONE:{}    PREVZONE:{}   DIRECTION:{}'.format(Rotary.zone[rotary_number],
                                                                      Rotary.prevZone[rotary_number],
                                                                      str_direction))
        Rotary.prevZone[rotary_number] = Rotary.zone[rotary_number]
        return direction

    #*****************************************************************************************************
    # ENCODER SPEED 1				BCM4
    def rotary_0_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 1 Rotary 0 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        self.log.debug("Interrupt Time : {}".format(interrupt_time))
        delta = interrupt_time - Rotary.last_interrupt_time_rotary0_pin0
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary0_pin0))
        if simulate:
            pins = sim_pins
            self.log.debug('self.simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_0_pins[0]), self.gpio.read(self.config.rotary_0_pins[1])]
            self.log.debug("Pin read time {}".format(time.time()))
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_0_pins[0], pins[0],
                                                               self.config.rotary_0_pins[1],
                                                               pins[1]))
        Rotary.last_interrupt_time_rotary0_pin0 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[0], self.speedgen.SPEED_0_CS)

    #*****************************************************************************************************
    # ENCODER SPEED 1				BCM14
    def rotary_0_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 1 Rotary 1 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        self.log.debug("Interrupt Time : {}".format(interrupt_time))
        delta = interrupt_time - Rotary.last_interrupt_time_rotary0_pin1
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary0_pin1))
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated Interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_0_pins[0]), self.gpio.read(self.config.rotary_0_pins[1])]
            self.log.debug("Pin read time {}".format(time.time()))
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_0_pins[0], pins[0],
                                                               self.config.rotary_0_pins[1],
                                                               pins[1]))
        Rotary.last_interrupt_time_rotary0_pin1 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[0], self.speedgen.SPEED_0_CS)

    #*****************************************************************************************************
    # ENCODER SPEED 2				BMC15
    def rotary_1_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 2 Rotary 1 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary1_pin0
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary1_pin0))
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_1_pins[0]), self.gpio.read(self.config.rotary_1_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_1_pins[0], pins[0],
                                                               self.config.rotary_1_pins[1],
                                                               pins[1]))
        Rotary.last_interrupt_time_rotary1_pin0 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[1], self.speedgen.SPEED_1_CS)

    # *****************************************************************************************************
    # ENCODER SPEED 2				BMC22
    def rotary_1_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("SPEED ENCODER 2 Rotary 1 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary1_pin1
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary1_pin1))
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_1_pins[0]), self.gpio.read(self.config.rotary_1_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_1_pins[0], pins[0],
                                                               self.config.rotary_1_pins[1],
                                                               pins[1]))
        Rotary.last_interrupt_time_rotary1_pin1 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[1], self.speedgen.SPEED_1_CS)

    # *****************************************************************************************************
    # ENCODER PRIMARY GAIN			BMC23
    def rotary_2_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 2 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary2_pin0
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary2_pin0))
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_2_pins[0]), self.gpio.read(self.config.rotary_2_pins[1])]
        self.log.debug(
            "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_2_pins[0], pins[0],
                                                           self.config.rotary_2_pins[1],
                                                           pins[1]))
        self.last_interrupt_time_rotary2_pin0 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[2], Rotary.DIGITAL_POT_0)

    # *****************************************************************************************************
    # ENCODER PRIMARY GAIN			BCM24
    def rotary_2_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 2 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary2_pin1
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary2_pin1))
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_2_pins[0]), self.gpio.read(self.config.rotary_2_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_2_pins[0], pins[0],
                                                               self.config.rotary_2_pins[1],
                                                               pins[1]))
        Rotary.last_interrupt_time_rotary2_pin1 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[2], Rotary.DIGITAL_POT_0)

    # *****************************************************************************************************
    # ENCODER SECONDARY GAIN			BCM25
    def rotary_3_pin_0(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 3 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary3_pin0
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary3_pin0))
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_3_pins[0]), self.gpio.read(self.config.rotary_3_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_3_pins[0], pins[0],
                                                               self.config.rotary_3_pins[1],
                                                               pins[1]))
        Rotary.last_interrupt_time_rotary3_pin0 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[3], Rotary.DIGITAL_POT_1)

    # *****************************************************************************************************
    # ENCODER SECONDARY GAIN			BCM12
    def rotary_3_pin_1(self, pin_num, level, tick, simulate=False, sim_pins=None):
        self.rotary_interrupts(False)
        self.log.debug("#######################################################")
        self.log.debug("PRIMARY GAIN Rotary 3 BCM PIN:{}  LEVEL:{}   TICK:{}".format(pin_num, level, tick))
        self.pollperm.polling_prohitied = (True, __name__)
        interrupt_time = time.time()
        delta = interrupt_time - Rotary.last_interrupt_time_rotary3_pin1
        self.log.debug("Last saved time : {}".format(Rotary.last_interrupt_time_rotary3_pin1))
        if simulate:
            pins = sim_pins
            self.log.debug('Simulated interrupt with PINS ' + str(sim_pins))
        else:
            pins = [self.gpio.read(self.config.rotary_3_pins[0]), self.gpio.read(self.config.rotary_3_pins[1])]
            self.log.debug(
                "PIN {}: Value:{}    PIN {}:  Value:{}".format(self.config.rotary_3_pins[0], pins[0],
                                                               self.config.rotary_3_pins[1],
                                                               pins[1]))
        Rotary.last_interrupt_time_rotary3_pin1 = interrupt_time
        self.rotary_actions(pins, delta, Rotary.rotary_num[3], Rotary.DIGITAL_POT_0)

    #*****************************************************************************************************
    #TODO make sure we are passing data correctly to this when something is missing
    def rotary_actions(self, pins, delta, rotary_num, chip_select=None, digital_pot=None):
        if rotary_num == 0 or rotary_num == 1:
            direction = self.get_direction(pins, Rotary.rotary_num[rotary_num])
            speed = self.get_speed(delta)
            self.speedgen.set_speed_signal(chip_select, speed, direction)
            channel, data, chip_select = self.codegen.frequency_to_registers(self.speedgen.SPEED_FREQUENCY[self.speedgen.speed_reg],
                                                          self.speedgen.primary_source_frequency,
                                                          self.speedgen.freq_shape[self.speedgen.speed_reg], chip_select)
            self.spi.write(channel, data, chip_select)

        if rotary_num == 2 or rotary_num == 3:
            direction = self.get_direction(pins, Rotary.rotary_num[rotary_num])
            speed = self.get_speed(delta)
            value = self.digpots.value_changed(speed, direction, digital_pot)
            # self.digitalpots_send_spi(potnumber, coarse_hex, fine_hex)
            if digpots.DigPots.gains_locked:
                value = self.digpots.value_check(digpots.DigPots.PRIMARY_GAIN_POT_NUMBER, digpots.DigPots.value)
                value = self.digpots.value_check(digpots.DigPots.SECONDARY_GAIN_POT_NUMBER, digpots.DigPots.value)
            else:
                self.digpots.value_check(digital_pot, value)
            self.send_spi(digital_pot)

    # *****************************************************************************************************
    def send_spi(self, pot_number):
        """depending on pot number, we first calculate the coarse and fine hex
         data.  then we send two spi packets one to each digital pot
        :param pot_number:
        """
        coarse_hex, fine_hex = self.int2hex()
        self.log.debug('WIPER WRITE pot_number:' + str(pot_number))
        if pot_number == digpots.DigPots.PRIMARY_GAIN_POT_NUMBER:
            data = digpots.DigPots.SPI_WRITE_COMMAND + fine_hex[0:2]
            self.spi.write(2, data, decoder.Decoder.chip_select_primary_fine_gain)
            data = digpots.DigPots.SPI_WRITE_COMMAND + coarse_hex[0:2]
            self.spi.write(2, data, decoder.Decoder.chip_select_primary_coarse_gain)
        elif pot_number == digpots.DigPots.SECONDARY_GAIN_POT_NUMBER:
            data = digpots.DigPots.SPI_WRITE_COMMAND + fine_hex[2:4]
            self.spi.write(2, data, decoder.Decoder.chip_select_secondary_fine_gain)
            data = digpots.DigPots.SPI_WRITE_COMMAND + coarse_hex[2:4]
            self.spi.write(2, data, decoder.Decoder.chip_select_secondary_coarse_gain)

    #*****************************************************************************************************
    # support routine to convert intergers to hex
    def int2hex(self):
        coarse_hex = [(digpots.DigPots.coarse_wiper[0] >> 2), (digpots.DigPots.coarse_wiper[0] & 0b11) << 6,
                      (digpots.DigPots.coarse_wiper[1] >> 2), (digpots.DigPots.coarse_wiper[1] & 0b11) << 6]
        fine_hex = [(digpots.DigPots.fine_wiper[0] >> 2), (digpots.DigPots.fine_wiper[0] & 0b11) << 6,
                    (digpots.DigPots.fine_wiper[1] >> 2), (digpots.DigPots.fine_wiper[1] & 0b11) << 6]
        self.log.debug("Coarse HEX {} | Fine HEX {}".format(coarse_hex, fine_hex))
        return coarse_hex, fine_hex
#

