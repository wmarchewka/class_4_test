# libraries
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
    # fine_wiper = [0, 0]
    # coarse_wiper = [0, 0]
    FINE_DIVISOR = FINE_MAX_OHMS / FINE_MAX_BITS
    TOTAL_MAX_OHMS = COARSE_MAX_OHMS + FINE_MAX_OHMS
    COARSE_DIVISOR = COARSE_MAX_OHMS / COARSE_MAX_BITS
    COARSE_WIPER_INCREMENT = None
    COARSE_WIPER_DECREMENT = None
    COARSE_WIPER_MAX_BITS = None
    COARSE_WIPER_MIN_BITS = None
    FINE_WIPER_INCREMENT = None
    FINE_WIPER_DECREMENT = None
    FINE_WIPER_MAX_BITS = None
    FINE_WIPER_MIN_BITS = None

    def __init__(self, name, spi_channel, chip_select, pin_0, pin_1, pin_0_debounce, pin_1_debounce,
                 thresholds):
        self.speed = 0
        self.delta = 0
        self.speed_increment = 0
        self.wiper_total_percentage = [0, 0]
        self.off = None
        self.actual_ohms = None
        self.coarse_wiper_ohms = None
        self.wiper = None
        self.coarse_wiper = None
        self.gains_locked = None
        self.value = None
        self.name = name
        self.pin_0 = pin_0
        self.pin_1 = pin_1
        self.pin_0_debounce = pin_0_debounce
        self.pin_1_debounce = pin_1_debounce
        self.spi_channel = spi_channel
        self.chip_select = chip_select
        self.thresholds = thresholds
        self.logger = logger.Logger()
        self.log = self.logger
        self.log = logging.getLogger()
        self.config = config.Config()
        self.decoder = decoder.Decoder()
        self.pollperm = pollperm.Pollperm()
        self.spi = spi.SPI()
        self.spi_channel = spi_channel
        self.polling_prohibited = (True, self.__class__)
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    #***************************************************************************************************************
    def startup_processes(self):
        self.load_config()
        self.create_rotaries()
        # self.speed_off(0)
        # self.speed_off(1)

    #***************************************************************************************************************
    def create_rotaries(self):
        self.log.debug("Creating {} Rotary...".format(self.name))
        Gains.rotaries.append(
            rotary_new.Rotary(self.name, self.value_change, self.pin_0, self.pin_1, self.pin_0_debounce,
                              self.pin_1_debounce))

    # ***************************************************************************************************************
    def threshold_check(self, delta):
        for t in self.thresholds:
            val = t[0]
            self.log.debug("Checking Threshold {}ms".format(val))
            if delta >= val:
                self.speed = self.speed + 1
        self.speed = self.speed - 1
        self.log.debug("Speed threshold {}".format(self.speed))
        self.speed_increment = self.thresholds[self.speed][1]
        self.log.debug("Speed increment {}".format(self.speed_increment))
        return self.speed_increment

    # ***************************************************************************************************************
    def value_change(self, delta, direction):
        self.log.debug('CHANGE WIPER:Speed:{}   Direction:{}'.format(delta, direction))
        delta = delta / 1000
        self.delta = delta
        self.log.debug("Delta:{}".format(self.delta))
        self.log.debug("Thresholds {}".format(self.thresholds))
        self.speed = 0
        self.speed_increment = self.threshold_check(delta)
        self.value = self.increment_decrement(direction)
        self.value_check(self.value)

    #***************************************************************************************************************
    def increment_decrement(self, direction):
        if direction == Gains.CLOCKWISE:
            if self.gains_locked:
                self.value = self.value + self.speed_increment
            elif not self.gains_locked:
                self.value = self.value + self.speed_increment
        elif direction == Gains.ANTI_CLOCKWISE:
            if self.gains_locked:
                self.value = self.value - self.speed_increment
            elif not self.gains_locked:
                self.value = self.value - self.speed_increment

    # ***************************************************************************************************************
    def value_check(self, val):
        """Each click of the encoder increases the value by approximately 9.7 ohms.  To figure out what values to send
        to each digital pot, i take the total ohms needed divided by the coarse ohms amount.  The remainder then gets
        divided by the fine ohms amount.  Example:  if 210 ohms is needed, then take 210 / 49.7 = 4 coarse bits.  Then
        subtract the coarse amount from the total, to get the fine amount, ie 210 - 200 = 10.  Then take the 10 ohms
        remaining and divide by fine amount of 10 and you get 1 bit needed for the fine digital pot.
        :param value:
        :param number:
        """
        self.value = val
        if self.value > Gains.TOTAL_MAX_OHMS:
            self.value = Gains.TOTAL_MAX_OHMS
            self.log.debug("POT {} reached MAX".format(self.name))
        elif self.value < Gains.TOTAL_MIN_OHMS:
            self.value = Gains.TOTAL_MIN_OHMS
            self.log.debug("POT {} reached MIN".format(self.name))
            self.coarse_wiper = 0
            self.fine_wiper = 0
            self.fine_wiper_ohms = 0
            self.coarse_wiper_ohms = 0
            self.actual_ohms = 0
            self.off = True
        else:
            if self.value < Gains.COARSE_MAX_OHMS:
                self.coarse_wiper = int(self.value / Gains.COARSE_DIVISOR)
                self.coarse_wiper_ohms = int(self.coarse_wiper * Gains.COARSE_DIVISOR)
                self.fine_wiper_ohms = self.value - self.coarse_wiper_ohms
                self.fine_wiper = int(self.fine_wiper_ohms / Gains.FINE_DIVISOR)
                self.fine_wiper_ohms = self.fine_wiper * Gains.FINE_DIVISOR
            if self.value > Gains.COARSE_MAX_OHMS:
                self.coarse_wiper = min(Gains.COARSE_MAX_BITS, (int(self.value / Gains.COARSE_DIVISOR)))
                self.coarse_wiper_ohms = int(self.coarse_wiper * Gains.COARSE_DIVISOR)
                self.fine_wiper_ohms = self.value - self.coarse_wiper_ohms
                self.fine_wiper = int(self.fine_wiper_ohms / Gains.FINE_DIVISOR)
                self.off = False
        coarse_hex, fine_hex = self.int2hex(self.coarse_wiper, self.fine_wiper)
        self.digitalpots_send_spi(coarse_hex, fine_hex)
        self.actual_ohms = int(self.fine_wiper_ohms + self.coarse_wiper_ohms)
        self.wiper_total_percentage = self.actual_ohms / Gains.TOTAL_MAX_OHMS
        self.log.info("{}  TOTAL GAIN % {}".format(self.name, self.wiper_total_percentage * 100))
        self.log.debug(
            "RAW: {} ohms   ACTUAL: {} ohms  COARSE bits: {}  FINE bits: {}  COARSE ohms: {}  FINE ohms: {} ".format(
                self.value,
                self.actual_ohms,
                self.coarse_wiper,
                self.fine_wiper,
                self.coarse_wiper_ohms,
                self.fine_wiper_ohms))

    # ***************************************************************************************************************
    def digitalpots_send_spi(self, coarse_hex, fine_hex):
        self.log.debug('Gain: {}' + str(self.name))
        data = Gains.SPI_WRITE_COMMAND + fine_hex[0:2]
        self.spi.write(self.spi_channel, data, self.decoder.chip_select_primary_fine_gain)
        # time.sleep(0.010)
        data = Gains.SPI_WRITE_COMMAND + coarse_hex[0:2]
        self.spi.write(self.spi_channel, data, self.decoder.chip_select_primary_coarse_gain)

    # ***************************************************************************************************************
    # support routine to convert intergers to hex
    def int2hex(self, coarse_wiper, fine_wiper):
        coarse_hex = [(coarse_wiper >> 2), (coarse_wiper & 0b11) << 6]
        fine_hex = [(fine_wiper >> 2), (fine_wiper & 0b11) << 6]
        self.log.debug("Coarse HEX {} | Fine HEX {}".format(coarse_hex, fine_hex))
        return coarse_hex, fine_hex

    # ***************************************************************************************************************
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

    # ***************************************************************************************************************
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

    # ***************************************************************************************************************
    def load_config(self):
        pass
