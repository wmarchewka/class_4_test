#libraries
import logging
import time

# my libraries
import logger
import config
import decoder
import spi
import rotary_new
import pollperm

class Gains(object):

    logging.debug("Initiating {} class...".format(__qualname__))

    rotaries = []
    GAIN_0_CS = None
    GAIN_1_CS = None
    GAIN_0_THRESHOLDS = []
    GAIN_1_THRESHOLDS = []
    PRIMARY_GAIN_POT_NUMBER = 0
    SECONDARY_GAIN_POT_NUMBER = 1
    COARSE_MAX_OHMS = 50070
    COARSE_MAX_BITS = 1023
    STARTING_RESISTANCE = 180
    SPEED_SLOW = 0
    SPEED_FAST = 1
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    SLOW_STEP_AMOUNT = 5  # since each endcoder interrupts twice per click, i changed this to 5
    FAST_STEP_AMOUNT = 500
    SPI_WRITE_COMMAND = [0X00]
    SPI_WIPER_TO_NVRAM_COMMAND = [0b00100000]
    SPI_NVRAM_TO_WIPER_COMMAND = [0b00110000]
    FINE_MAX_OHMS = 10070
    FINE_MAX_BITS = 1023
    TOTAL_MIN_OHMS = 0
    fine_wiper = [0, 0]
    coarse_wiper = [0, 0]
    fine_divisor = FINE_MAX_OHMS / FINE_MAX_BITS
    total_max_ohms = COARSE_MAX_OHMS + FINE_MAX_OHMS
    coarse_divisor = COARSE_MAX_OHMS / COARSE_MAX_BITS
    coarse_wiper_percentage = [0, 0]
    coarse_wiper_resistance = [0, 0]
    coarse_wiper_ohms = [0, 0]
    fine_wiper_percentage = [0, 0]
    fine_wiper_resistance = [0, 0]
    fine_wiper_ohms = [0, 0]
    wiper_total_percentage = [0, 0]
    actual_ohms = [0, 0]
    off = [None, None]
    value = [0,0,0,0]
    COARSE_WIPER_INCREMENT = None
    COARSE_WIPER_DECREMENT = None
    COARSE_WIPER_MAX_BITS = None
    COARSE_WIPER_MIN_BITS = None
    FINE_WIPER_INCREMENT = None
    FINE_WIPER_DECREMENT = None
    FINE_WIPER_MAX_BITS = None
    FINE_WIPER_MIN_BITS = None
    gains_locked = False

    def __init__(self, spi_channel):
        self.logger = logger.Logger()
        self.log = self.logger
        self.log = logging.getLogger(__name__)
        self.config = config.Config()
        self.decoder = decoder.Decoder()
        self.pollperm = pollperm.Pollperm()
        self.spi = spi.SPI()
        self.spi_channel = spi_channel
        self.polling_prohibited = (True, self.__class__)
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    def startup_processes(self):
        self.load_config()
        self.create_rotaries()
        #self.speed_off(0)
        #self.speed_off(1)

    def create_rotaries(self):
        self.log.debug("Creating Speed rotaties...")
        self.create_rotary("Gain0", 0, self.rotary_2_pins[0], self.rotary_2_pins[1], self.rotary_2_pin_0_debounce,
                           self.rotary_2_pin_1_debounce, self.GAIN_0_THRESHOLDS)
        self.create_rotary("Gain1", 1, self.rotary_3_pins[0], self.rotary_3_pins[1], self.rotary_3_pin_0_debounce,
                           self.rotary_3_pin_1_debounce, self.GAIN_1_THRESHOLDS)

    def create_rotary(self, name, number, pin0, pin1, pin0_debounce, pin1_debounce, thresholds):
        """create global list of rotary encoders create across instances so that we can
        disable or enable all callbacks
        :param name:
        :param number:
        :param pin0:
        :param pin1:
        :param pin0_debounce:
        :param pin1_debounce:
        :param thresholds:
        """
        Gains.rotaries.append(rotary_new.Rotary(name, number, self.value_change, pin0, pin1, pin0_debounce, pin1_debounce))

    def value_change(self, number, delta, direction):
        global thresholds, speed_increment
        self.log.debug('CHANGE WIPER:Speed:{}   Direction:{}   Pot_Number:{}'.format(delta, direction, number))
        delta = delta / 1000
        self.log.debug("Delta:{}".format(delta))
        speed = 0
        if number == 0:
            thresholds = Gains.GAIN_0_THRESHOLDS
        if number == 1:
            thresholds = Gains.GAIN_1_THRESHOLDS
        self.log.debug("Thresholds {}".format(thresholds))
        for t in thresholds:
            val = t[0]
            self.log.debug("Checking Threshold {}ms".format(val))
            if delta >= val:
                speed = speed + 1
        speed = speed - 1
        self.log.debug("Speed threshold {}".format(speed))
        inc = thresholds[speed][1]
        self.log.debug("Speed increment {}".format(inc))
        if number == 0:
            cs = Gains.GAIN_0_CS
            speed_increment = inc
        if number == 1:
            cs = Gains.GAIN_1_CS
            speed_increment = inc
        if direction == Gains.CLOCKWISE:
            if Gains.gains_locked:
                Gains.value[Gains.PRIMARY_GAIN_POT_NUMBER] = Gains.value[
                                                                             Gains.PRIMARY_GAIN_POT_NUMBER] + speed_increment
                Gains.value[Gains.SECONDARY_GAIN_POT_NUMBER] = Gains.value[
                    Gains.PRIMARY_GAIN_POT_NUMBER]
            elif not Gains.gains_locked:
                Gains.value[number] = Gains.value[number] + speed_increment
        elif direction == Gains.ANTI_CLOCKWISE:
            if Gains.gains_locked:
                Gains.value[Gains.PRIMARY_GAIN_POT_NUMBER] = Gains.value[
                                                                             Gains.PRIMARY_GAIN_POT_NUMBER] - speed_increment
                Gains.value[Gains.SECONDARY_GAIN_POT_NUMBER] = Gains.value[
                    Gains.PRIMARY_GAIN_POT_NUMBER]
            elif not Gains.gains_locked:
                Gains.value[number] = Gains.value[number] - speed_increment
        if Gains.gains_locked:
            self.value_check(Gains.PRIMARY_GAIN_POT_NUMBER, Gains.value[0])
            self.value_check(Gains.SECONDARY_GAIN_POT_NUMBER, Gains.value[1])
        else:
            self.value_check(number, Gains.value[number])

    def value_check(self, number, val):
        """Each click of the encoder increases the value by approximately 9.7 ohms.  To figure out what values to send
        to each digital pot, i take the total ohms needed divided by the coarse ohms amount.  The remainder then gets
        divided by the fine ohms amount.  Example:  if 210 ohms is needed, then take 210 / 49.7 = 4 coarse bits.  Then
        subtract the coarse amount from the total, to get the fine amount, ie 210 - 200 = 10.  Then take the 10 ohms
        remaining and divide by fine amount of 10 and you get 1 bit needed for the fine digital pot.
        :param value:
        :param number:
        """
        Gains.value[number] = val
        if Gains.value[number] > Gains.total_max_ohms:
            Gains.value[number] = Gains.total_max_ohms
            self.log.debug("POT {} reached MAX".format(number))
        elif Gains.value[number] < Gains.TOTAL_MIN_OHMS:
            Gains.value[number] = Gains.TOTAL_MIN_OHMS
            self.log.debug("POT {} reached MIN".format(number))
            Gains.coarse_wiper[number] = 0
            Gains.fine_wiper[number] = 0
            Gains.fine_wiper_ohms[number] = 0
            Gains.coarse_wiper_ohms[number] = 0
            Gains.actual_ohms[number] = 0
            Gains.off[number] = True
        else:
            if Gains.value[number] < Gains.COARSE_MAX_OHMS:
                Gains.coarse_wiper[number] = int(Gains.value[number] / Gains.coarse_divisor)
                Gains.coarse_wiper_ohms[number] = int(
                    Gains.coarse_wiper[number] * Gains.coarse_divisor)
                Gains.fine_wiper_ohms[number] = Gains.value[number] - Gains.coarse_wiper_ohms[
                    number]
                Gains.fine_wiper[number] = int(
                    Gains.fine_wiper_ohms[number] / Gains.fine_divisor)
                Gains.fine_wiper_ohms[number] = Gains.fine_wiper[number] * Gains.fine_divisor
            if Gains.value[number] > Gains.COARSE_MAX_OHMS:
                Gains.coarse_wiper[number] = min(Gains.COARSE_MAX_BITS,
                                                          (int(Gains.value[
                                                                   number] / Gains.coarse_divisor)))
                Gains.coarse_wiper_ohms[number] = int(
                    Gains.coarse_wiper[number] * Gains.coarse_divisor)
                Gains.fine_wiper_ohms[number] = Gains.value[number] - Gains.coarse_wiper_ohms[
                    number]
                Gains.fine_wiper[number] = int(
                    Gains.fine_wiper_ohms[number] / Gains.fine_divisor)
                Gains.off[number] = False
        coarse_hex, fine_hex = self.int2hex(Gains.coarse_wiper, Gains.fine_wiper)
        self.digitalpots_send_spi(number, coarse_hex, fine_hex)
        Gains.actual_ohms[number] = int(
            Gains.fine_wiper_ohms[number] + Gains.coarse_wiper_ohms[number])
        Gains.wiper_total_percentage[number] = Gains.actual_ohms[
                                                            number] / Gains.total_max_ohms
        self.log.debug(
            "POT {} TOTAL GAIN % {}".format(number, Gains.wiper_total_percentage[number] * 100))
        self.log.debug(
            "RAW: {} ohms   ACTUAL: {} ohms  POT: {} COARSE bits: {}  FINE bits: {}  COARSE ohms: {}  FINE ohms: {} ".format(
                Gains.value[number],
                Gains.actual_ohms[number],
                number,
                Gains.coarse_wiper[number],
                Gains.fine_wiper[number],
                Gains.coarse_wiper_ohms[number],
                Gains.fine_wiper_ohms[number]))

    def digitalpots_send_spi(self, number, coarse_hex, fine_hex):
        self.log.debug('WIPER WRITE number:' + str(number))
        if number == Gains.SECONDARY_GAIN_POT_NUMBER:
            data = Gains.SPI_WRITE_COMMAND + fine_hex[0:2]
            self.spi.write(2, data, self.decoder.chip_select_primary_fine_gain)
            # time.sleep(0.010)
            data = Gains.SPI_WRITE_COMMAND + coarse_hex[0:2]
            self.spi.write(2, data, self.decoder.chip_select_primary_coarse_gain)
        elif number == Gains.SECONDARY_GAIN_POT_NUMBER:
            data = Gains.SPI_WRITE_COMMAND + fine_hex[2:4]
            self.spi.write(2, data, self.decoder.chip_select_secondary_fine_gain)
            # time.sleep(0.010)
            data = Gains.SPI_WRITE_COMMAND + coarse_hex[2:4]
            self.spi.write(2, data, self.decoder.chip_select_secondary_coarse_gain)

    # support routine to convert intergers to hex
    def int2hex(self, coarse_wiper, fine_wiper):
        coarse_hex = [(coarse_wiper[0] >> 2), (coarse_wiper[0] & 0b11) << 6,
                      (coarse_wiper[1] >> 2), (coarse_wiper[1] & 0b11) << 6]
        fine_hex = [(fine_wiper[0] >> 2), (fine_wiper[0] & 0b11) << 6,
                    (fine_wiper[1] >> 2), (fine_wiper[1] & 0b11) << 6]
        self.log.debug("Coarse HEX {} | Fine HEX {}".format(coarse_hex, fine_hex))
        return coarse_hex, fine_hex

    def nvram_to_wiper(self):
        # todo make sure this is working
        self.log.debug("COPY NVRAM TO WIPER")
        # this command when sent to the pots will copy wiper contents to the NV ram,
        # so that on power up the pots will go to the NV ram value.
        # i want that to be 0
        spi_msg = Gains.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_coarse_gain)
        time.sleep(0.020)  # delay per data sheet
        spi_msg = Gains.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_fine_gain)
        time.sleep(0.020)
        spi_msg = Gains.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_coarse_gain)
        time.sleep(0.020)
        spi_msg = Gains.SPI_NVRAM_TO_WIPER_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_fine_gain)
        time.sleep(0.020)

    # todo make sure this is working
    def wiper_to_nvram(self):
        """this command when sent to the pots will copy wiper contents to the NV ram,
        so that on power up the pots will go to the NV ram value.
        i want that to be 0
        """
        self.log.debug("COPY WIPER TO NVRAM")
        spi_msg = Gains.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_coarse_gain)
        time.sleep(0.020)
        spi_msg = Gains.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_primary_fine_gain)
        time.sleep(0.020)
        spi_msg = Gains.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_coarse_gain)
        time.sleep(0.020)
        spi_msg = Gains.SPI_WIPER_TO_NVRAM_COMMAND
        self.spi.write(2, spi_msg, self.decoder.chip_select_secondary_fine_gain)
        time.sleep(0.020)

    def load_config(self):
        #TODO CHANGE THIS TO PINS 2 AND 3 !!!!
        self.rotary_2_pins = self.config.rotary_0_pins
        self.rotary_3_pins = self.config.rotary_1_pins
        self.rotary_2_pin_0_debounce = self.config.rotary_2_pin_0_debounce
        self.rotary_2_pin_1_debounce = self.config.rotary_2_pin_1_debounce
        self.rotary_3_pin_0_debounce = self.config.rotary_3_pin_0_debounce
        self.rotary_3_pin_1_debounce = self.config.rotary_3_pin_1_debounce
        self.GAIN_0_CS = self.config.GAIN_0_CS  # 6  # SPEED SIMULATION TACH 1
        self.GAIN_1_CS = self.config.GAIN_1_CS  # 7  # SPEED SIMULATION TACH 2
        Gains.GAIN_0_CS = self.GAIN_0_CS
        Gains.GAIN_1_CS = self.GAIN_1_CS
        Gains.GAIN_0_THRESHOLDS = self.config.gain_0_thresholds
        Gains.GAIN_1_THRESHOLDS = self.config.gain_1_thresholds
