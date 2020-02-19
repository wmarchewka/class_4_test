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
    logging.info("Instantiating {} class...".format(__qualname__))

    rotaries = []

    FINE_MAX_OHMS = 10070
    COARSE_MAX_OHMS = 50070
    TOTAL_MIN_OHMS = 0
    TOTAL_MAX_OHMS = COARSE_MAX_OHMS + FINE_MAX_OHMS
    FINE_MAX_BITS = 1023
    COARSE_MAX_BITS = 1023
    COARSE_DIVISOR = COARSE_MAX_OHMS / COARSE_MAX_BITS
    STARTING_RESISTANCE = 180
    SPEED_SLOW = 0
    SPEED_FAST = 1
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    DIRECTION_ERROR = 0
    SPI_WRITE_COMMAND = [0X00]
    SPI_WIPER_TO_NVRAM_COMMAND = [0b00100000]
    SPI_NVRAM_TO_WIPER_COMMAND = [0b00110000]
    FINE_DIVISOR = FINE_MAX_OHMS / FINE_MAX_BITS

    def __init__(self, name, spi_channel, chip_select, pin_0, pin_1, pin_0_debounce, pin_1_debounce,
                 thresholds, callback, commander_gain_move_callback):

        self.wiper_total_percentage = 0
        self.off = None
        self.wiper = None
        self.fine_wiper = None
        self.fine_wiper_ohms = None
        self.coarse_wiper = None
        self.coarse_wiper_ohms = None
        self.actual_ohms = None
        self.gains_locked = False
        self.speed = 0
        self.speed_value = 0
        self.value = 0
        self.name = name
        self.pin_0 = pin_0
        self.pin_1 = pin_1
        self.pin_0_debounce = pin_0_debounce
        self.pin_1_debounce = pin_1_debounce
        self.spi_channel = spi_channel
        self.chip_select = chip_select
        self.thresholds = thresholds
        self.callback = callback
        self.commander_gain_move_callback = commander_gain_move_callback
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

    # ***************************************************************************************************************
    def startup_processes(self):
        self.load_config()
        self.create_rotaries()
        # self.speed_off(0)
        # self.speed_off(1)

    # ***************************************************************************************************************
    def create_rotaries(self):
        self.log.debug("Creating {} Rotary...".format(self.name))
        Gains.rotaries.append(
            rotary_new.Rotary(self.name, self.value_change_callback, self.pin_0, self.pin_1, self.pin_0_debounce,
                              self.pin_1_debounce))

    # ***************************************************************************************************************
    def threshold_check(self, delta):
        speed = 0
        for t in self.thresholds:
            val = t[0]
            self.log.debug("Checking Threshold {}ms".format(val))
            if delta >= val:
                speed = speed + 1
        speed = speed - 1
        speed_increment = self.thresholds[speed][1]
        self.log.debug("Speed threshold:{} | Speed increment:{}".format(speed, speed_increment))
        return speed_increment

    # ***************************************************************************************************************
    def value_change_callback(self, delta, direction):
        self.log.debug('CHANGE WIPER:Speed:{}   Direction:{}'.format(delta, direction))
        if direction is not Gains.DIRECTION_ERROR:
            delta = delta / 1000
            self.log.debug("Delta:{}".format(delta))
            self.log.debug("Thresholds {}".format(self.thresholds))
            speed_increment = self.threshold_check(delta)
            speed_value = self.bounds_check(speed_increment, direction)
            coarse_hex, fine_hex = speed_value
            self.digitalpots_send_spi(coarse_hex, fine_hex)
        else:
            self.log.debug("Direction error received")

    # ***************************************************************************************************************
    def bounds_check(self, speed_increment, direction):
        """Each click of the encoder increases the value by approximately 9.7 ohms.  To figure out what values to send
        to each digital pot, i take the total ohms needed divided by the coarse ohms amount.  The remainder then gets
        divided by the fine ohms amount.  Example:  if 210 ohms is needed, then take 210 / 49.7 = 4 coarse bits.  Then
        subtract the coarse amount from the total, to get the fine amount, ie 210 - 200 = 10.  Then take the 10 ohms
        remaining and divide by fine amount of 10 and you get 1 bit needed for the fine digital pot.
        :param value:
        :param number:
        """
        if direction == Gains.CLOCKWISE:
            if self.gains_locked:
                self.value = self.value + speed_increment
            elif not self.gains_locked:
                self.value = self.value + speed_increment
        elif direction == Gains.ANTI_CLOCKWISE:
            if self.gains_locked:
                self.value = self.value - speed_increment
            elif not self.gains_locked:
                self.value = self.value - speed_increment
        elif direction == Gains.DIRECTION_ERROR:
            self.value = self.value
        self.commander_gain_move_callback(self.name, direction, speed_increment)
        self.log.debug("Gains Locked:{} Direction:{}".format(self.gains_locked, direction))
        self.log.debug("Speed Increment:{}  Value:{}".format(speed_increment, self.value))
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
        self.actual_ohms = int(self.fine_wiper_ohms + self.coarse_wiper_ohms)
        self.wiper_total_percentage = self.actual_ohms / Gains.TOTAL_MAX_OHMS
        self.callback(self.name, self.wiper_total_percentage)
        self.log.info("NAME:{}  TOTAL GAIN % {}".format(self.name, self.wiper_total_percentage * 100))
        self.log.info(
            "RAW:{} ohms ACTUAL:{} ohms COARSE bits:{} FINE bits:{} COARSE ohms:{} FINE ohms:{} ".format(
                self.value,
                self.actual_ohms,
                self.coarse_wiper,
                self.fine_wiper,
                self.coarse_wiper_ohms,
                self.fine_wiper_ohms))
        return coarse_hex,fine_hex
    # ***************************************************************************************************************
    def digitalpots_send_spi(self, coarse_hex, fine_hex):
        self.log.debug('Gain:{} Coarse HEX:{}  Fine HEX{}'.format(self.name, coarse_hex[0:2], fine_hex[0:2]))
        data = Gains.SPI_WRITE_COMMAND + fine_hex[0:2]
        self.log.debug('Data{}'.format(data))
        self.spi.write(self.spi_channel, data, self.decoder.chip_select_primary_fine_gain)
        # time.sleep(0.010)
        data = Gains.SPI_WRITE_COMMAND + coarse_hex[0:2]
        self.log.debug('Data{}'.format(data))
        self.spi.write(self.spi_channel, data, self.decoder.chip_select_primary_coarse_gain)

    # ***************************************************************************************************************
    # support routine to convert intergers to hex
    def int2hex(self, coarse_wiper, fine_wiper):
        self.log.debug("Received Coarse WIPER {} | Fine WIPER {}".format(coarse_wiper, fine_wiper))
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
