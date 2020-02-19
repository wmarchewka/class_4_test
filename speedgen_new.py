# libraries
import logging

# my libraries
import basiclogger
import decoder
import spi
import rotary_new
import pollperm
import gui.gui
import speedgen_new
import gains
import logger
import config

class Speedgen(object):
    logging.info("Instantiating {} class...".format(__qualname__))

    PRIMARY_SOURCE_FREQUENCY = None
    SECONDARY_SOURCE_FREQUENCY = None
    PRIMARY_FREQ_GEN_CONSTANT = None  # 268435456.00  # 2^28
    SECONDARY_FREQ_GEN_CONSTANT = None  # 268435456.00  # 2^28
    SPEED_GENERATOR_SET_SPEED_SPI_HEADER = None  # [0X20, 0X00]
    SPEED_FREQUENCY_MIN = 0
    SPEED_FREQUENCY_MAX = 1000000
    FREQ_SHAPE_SINE = 0
    FREQ_SHAPE_SQUARE = 1
    FREQ_SHAPE_TRIANGLE = 2
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    ERROR = 0
    SPEED_REG = 0
    FREQ_SHAPE = [FREQ_SHAPE_SINE, FREQ_SHAPE_SINE]
    rotaries = []

    def __init__(self, name, shape, spi_channel, chip_select, pin_0, pin_1, pin_0_debounce, pin_1_debounce,
                 thresholds, callback, commander_speed_move_callback):

        self.new_speed_increment = 0
        self.logger = logger.Logger()
        self.log = self.logger
        self.log = logging.getLogger()
        self.config = config.Config()
        self.decoder = decoder.Decoder()
        self.pollperm = pollperm.Pollperm()
        self.spi = spi.SPI()
        self.polling_prohibited = (True, self.__class__)
        self.spi_channel = spi_channel
        self.chip_select = chip_select
        self.name = name
        self.shape = shape
        self.thresholds = thresholds
        self.pin_0 = pin_0
        self.pin_1 = pin_1
        self.pin_0_debounce = pin_0_debounce
        self.pin_1_debounce = pin_1_debounce
        self.callback = callback
        self.commander_speed_move_callback = commander_speed_move_callback

        self.delta = 0
        self.direction = 0
        self.speed = 0
        self.speed_frequency = 0
        self.speed_increment = 0
        self.direction_text = None
        self.spi_msg = None
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    # **************************************************************************************************************
    def startup_processes(self):
        self.load_config()
        self.create_rotary()
        self.speed_off()

    # **************************************************************************************************************
    def create_rotary(self):
        """create global list of rotary encoders create across instances so that we can
        disable or enable all callbacks"""
        Speedgen.rotaries.append(
            rotary_new.Rotary(self.name, self.set_speed_signal_callback, self.pin_0, self.pin_1,
                              self.pin_0_debounce, self.pin_1_debounce))

    # **************************************************************************************************************
    def set_speed_signal_callback(self, delta: int, direction=None):
        self.delta = delta / 1000
        self.new_speed_increment = round(50000 / self.delta)
        self.direction = direction
        self.log.debug("{} Delta:{}".format(self.name, self.delta))
        self.speed = 0
        self.log.debug("Thresholds {}".format(self.thresholds))
        for t in self.thresholds:
            val = t[0]
            self.log.debug("Checking Threshold {}ms".format(val))
            if self.delta >= val:
                self.speed = self.speed + 1
            else:
                break
        self.speed = self.speed - 1
        self.log.debug("Speed threshold {}".format(self.speed))
        self.speed_increment = self.thresholds[self.speed][1]
        self.log.debug("Speed increment:{}   New Speed Increment:{}".format(self.speed_increment, self.new_speed_increment ))
        self.commander_speed_move_callback(self.name, direction, self.speed_increment)
        if self.direction == Speedgen.CLOCKWISE:
            self.direction_text = "CLOCKWISE"
            self.speed_frequency = self.speed_frequency + self.speed_increment
            if self.speed_frequency > self.SPEED_FREQUENCY_MAX:
                self.speed_frequency = self.SPEED_FREQUENCY_MAX
        elif direction == Speedgen.ANTI_CLOCKWISE:
            self.direction_text = "ANTI CLOCKWISE"
            self.speed_frequency = self.speed_frequency - self.speed_increment
            if self.speed_frequency < self.SPEED_FREQUENCY_MIN:
                self.speed_frequency = self.SPEED_FREQUENCY_MIN
        else:
            self.direction_text = "ERROR"
        self.log.debug(
            'SIGGEN Setting speed of {}  with speed of:{}  direction:{} '.format(self.name, self.speed_frequency,
                                                                                 self.direction_text))
        self.log.info("{}  FREQ:{}".format(self.name,self.speed_frequency))
        self.callback(self.name, self.speed_frequency)
        self.spi_msg = self.frequency_to_registers(self.speed_frequency, self.shape)
        if self.direction is not 0:
            self.spi_send(self.spi_msg)

    # **************************************************************************************************************
    def disable_interrupts(self):
        pass

    # **************************************************************************************************************
    def enable_interrupts(self):
        pass

    # **************************************************************************************************************
    def spi_send(self, msg):
        self.log.debug("{} send SPI{}".format(self.name, msg))
        self.spi.write(self.spi_channel, msg, self.chip_select)

    # **************************************************************************************************************
    def speed_off(self):
        self.log.debug("{} to OFF".format(self.name))
        # self.set_speed_signal(0)
        return True

    # **************************************************************************************************************
    def frequency_to_registers(self, frequency, shape):
        msg = []
        self.log.debug(
            "FREQ TO REG running with FREQ:{} SHAPE:{}".format(frequency, shape))
        word = hex(
            int(round((frequency * 2 ** 28) / Speedgen.PRIMARY_SOURCE_FREQUENCY)))  # Calculate frequency word to send
        if shape == Speedgen.FREQ_SHAPE_SQUARE:  # square
            shape_word = 0x2020
        elif shape == Speedgen.FREQ_SHAPE_TRIANGLE:  # triangle
            shape_word = 0x2002
        else:
            shape_word = 0x2000  # sine
        MSB = (int(word, 16) & 0xFFFC000) >> 14  # Split frequency word onto its separate bytes
        LSB = int(word, 16) & 0x3FFF
        MSB |= 0x4000  # Set control bits DB15 = 0 and DB14 = 1; for frequency register 0
        LSB |= 0x4000
        msg = self._ad9833_append(0x2100, msg)
        msg = self._ad9833_append(LSB, msg)  # lower 14 bits
        msg = self._ad9833_append(MSB, msg)  # Upper 14 bits
        msg = self._ad9833_append(shape_word, msg)
        return msg

    # **************************************************************************************************************
    def _ad9833_append(self, integer, msg):
        high, low = divmod(integer, 0x100)
        msg.append(high)
        msg.append(low)
        return msg

    # **************************************************************************************************************
    def load_config(self):
        Speedgen.PRIMARY_SOURCE_FREQUENCY = self.config.primary_source_frequency
        Speedgen.SECONDARY_SOURCE_FREQUENCY = self.config.secondary_source_frequency
        Speedgen.PRIMARY_FREQ_GEN_CONSTANT = self.config.primary_freq_gen_constant  # 268435456.00  # 2^28
        Speedgen.SECONDARY_FREQ_GEN_CONSTANT = self.config.secondary_freq_gen_constant  # 268435456.00  # 2^28
        Speedgen.SPEED_GENERATOR_SET_SPEED_SPI_HEADER = self.config.speed_generator_set_speed_spi_header  # [0x20, 0x00]

        Speedgen.SPEED_0_THRESHOLDS = self.config.SPEED_0_thresholds
        Speedgen.SPEED_1_THRESHOLDS = self.config.SPEED_1_thresholds
