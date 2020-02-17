# libraries
import logging

# my libraries
import logger
import config
import decoder
import spi
import rotary_new
import pollperm

class Speedgen(object):
    logging.debug("Initiating {} class...".format(__qualname__))

    PRIMARY_SOURCE_FREQUENCY = None
    SECONDARY_SOURCE_FREQUENCY = None
    PRIMARY_FREQ_GEN_CONSTANT = None  # 268435456.00  # 2^28
    SECONDARY_FREQ_GEN_CONSTANT = None  # 268435456.00  # 2^28
    SPEED_GENERATOR_SET_SPEED_SPI_HEADER = None  # [0X20, 0X00]
    SPEED_0_CS = None  # 6  # SPEED SIMULATION TACH 1
    SPEED_1_CS = None  # 7  # SPEED SIMULATION TACH 2
    SPEED1_ACTUAL_FREQ = 0
    SPEED2_ACTUAL_FREQ = 0
    SPEED_FREQUENCY = [0, 0]
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
    SPEED_0_THRESHOLDS = []
    SPEED_1_THRESHOLDS = []
    SPEED_0_INCREMENTS = []
    SPEED_1_INCREMENTS = []
    rotaries = []

    def __init__(self, spi_channel):

        self.shape = Speedgen.FREQ_SHAPE_SINE
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
        # self.speed_off(0)
        # self.speed_off(1)
        #self.disable_interrupts()
        #self.enable_interrupts()

    def create_rotaries(self):
        self.create_rotary("Speed0", 0, self.rotary_0_pins[0], self.rotary_0_pins[1], self.rotary_0_pin_0_debounce,
                           self.rotary_0_pin_1_debounce, self.SPEED_0_THRESHOLDS)
        self.create_rotary("Speed1", 1, self.rotary_1_pins[0], self.rotary_1_pins[1], self.rotary_1_pin_0_debounce,
                           self.rotary_1_pin_1_debounce, self.SPEED_1_THRESHOLDS)

    def create_rotary(self, name, sg, pin0, pin1, pin0_debounce, pin1_debounce, thresholds):
        """create global list of rotary encoders create across instances so that we can
        disable or enable all callbacks
        :param name:
        :param sg:
        :param pin0:
        :param pin1:
        :param pin0_debounce:
        :param pin1_debounce:
        :param thresholds:
        """
        Speedgen.rotaries.append(rotary_new.Rotary(name, sg, self.set_speed_signal, pin0, pin1, pin0_debounce, pin1_debounce, thresholds))

    def set_speed_signal(self, sg: int, speed: int, direction=None):
        global speed_text, direction_text, speed_increment, cs
        if sg == 0:
            cs = Speedgen.SPEED_0_CS
            speed_increment = self.SPEED_0_INCREMENTS[speed]
        if sg == 1:
            cs = Speedgen.SPEED_1_CS
            speed_increment = self.SPEED_1_INCREMENTS[speed]
        if direction == Speedgen.CLOCKWISE:
            direction_text = "CLOCKWISE"
            self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY[sg] + speed_increment
            if self.SPEED_FREQUENCY[sg] > self.SPEED_FREQUENCY_MAX:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY_MAX
        elif direction == Speedgen.ANTI_CLOCKWISE:
            direction_text = "ANTI CLOCKWISE"
            self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY[sg] - speed_increment
            if self.SPEED_FREQUENCY[sg] < self.SPEED_FREQUENCY_MIN:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY_MIN
        else:
            direction_text = "ERROR"
        self.log.debug(
            'SIGGEN Setting speed of SG:{}  with speed of:{}  direction:{} '.format(sg, speed, direction_text))
        self.speed1_actual_freq = self.SPEED_FREQUENCY[0]
        self.speed2_actual_freq = self.SPEED_FREQUENCY[1]
        self.log.debug('SIGGEN Speed 1 Actual Freq: {}'.format(self.speed1_actual_freq))
        self.log.debug('SIGGEN Speed 2 Actual Freq: {}'.format(self.speed2_actual_freq))
        spi_msg = self.frequency_to_registers(sg, Speedgen.SPEED_FREQUENCY[sg])
        if direction is not 0:
            self.spi_send(spi_msg, cs)

    def disable_interrupts(self):
        pass

    def enable_interrupts(self):
        pass

    def spi_send(self, msg, cs):
        self.log.debug("Speedgen SPI send {}".format(msg))
        self.spi.write(self.spi_channel, msg, cs)

    def speed_off(self, speed_generator: int) -> object:
        """pass speed generator 1 or 2
        :rtype:
        :param speed_generator:
        """
        cs = None
        self.log.debug("Speed {} frequency generator setting to OFF".format(speed_generator))
        if speed_generator == 1:
            cs = self.decoder.chip_select_speed_tach_1
        elif speed_generator == 2:
            cs = self.decoder.chip_select_speed_tach_2
        self.set_speed_signal(speed_generator, 0)
        return True

    def frequency_to_registers(self, frequency, shape):
        msg = []
        self.log.debug(
            "FREQ TO REG running with FREQ:{} SHAPE:{}".format(frequency, shape))
        word = hex(
            int(round((frequency * 2 ** 28) / Speedgen.PRIMARY_SOURCE_FREQUENCY)))  # Calculate frequency word to send
        shape = self.shape
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

    def _ad9833_append(self, integer, msg):
        high, low = divmod(integer, 0x100)
        msg.append(high)
        msg.append(low)
        return msg

    def load_config(self):
        self.primary_source_frequency = self.config.primary_source_frequency
        self.secondary_source_frequency = self.config.secondary_source_frequency
        self.primary_freq_gen_constant = self.config.primary_freq_gen_constant  # 268435456.00  # 2^28
        self.secondary_freq_gen_constant = self.config.secondary_freq_gen_constant  # 268435456.00  # 2^28
        self.speed_generator_set_speed_spi_header = self.config.speed_generator_set_speed_spi_header  # [0x20, 0x00]
        self.freq_shape = [self.FREQ_SHAPE_SINE, self.FREQ_SHAPE_SINE]
        self.SPEED_0_CS = self.config.SPEED_0_CS  # 6  # SPEED SIMULATION TACH 1
        self.SPEED_1_CS = self.config.SPEED_1_CS  # 7  # SPEED SIMULATION TACH 2
        Speedgen.PRIMARY_SOURCE_FREQUENCY = self.primary_source_frequency
        Speedgen.SECONDARY_SOURCE_FREQUENCY = self.secondary_source_frequency
        Speedgen.primary_freq_gen_constant = self.primary_freq_gen_constant  # 26
        Speedgen.secondary_freq_gen_constant = self.secondary_freq_gen_constant
        Speedgen.speed_generator_set_speed_spi_header = self.speed_generator_set_speed_spi_header
        Speedgen.SPEED_0_THRESHOLDS = self.config.SPEED_0_thresholds
        Speedgen.SPEED_1_THRESHOLDS = self.config.SPEED_1_thresholds
        Speedgen.SPEED_0_INCREMENTS = self.config.SPEED_0_increments
        Speedgen.SPEED_1_INCREMENTS = self.config.SPEED_1_increments
        Speedgen.SPEED_0_CS = self.SPEED_0_CS
        Speedgen.SPEED_1_CS = self.SPEED_1_CS
        self.rotary_0_pins = self.config.rotary_0_pins
        self.rotary_1_pins = self.config.rotary_1_pins
        self.rotary_0_pin_0_debounce = self.config.rotary_0_pin_0_debounce
        self.rotary_0_pin_1_debounce = self.config.rotary_0_pin_1_debounce
        self.rotary_1_pin_0_debounce = self.config.rotary_1_pin_0_debounce
        self.rotary_1_pin_1_debounce = self.config.rotary_1_pin_1_debounce
