import logger
import config
import logging
import decoder
import codegen


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
    FREQ_SLOW_INCREMENT = 1
    FREQ_FAST_INCREMENT = 100
    FREQ_SHAPE_SINE = 0
    FREQ_SHAPE_SQUARE = 1
    FREQ_SHAPE_TRIANGLE = 2
    SPEED_SLOW = 0
    SPEED_FAST = 1
    CLOCKWISE = 1
    ANTI_CLOCKWISE = -1
    ERROR = 0
    SPEED_REG = 0
    FREQ_TEXT = ''
    FREQ_SHAPE = [FREQ_SHAPE_SINE, FREQ_SHAPE_SINE]

    def __init__(self,):
        self.logger = logger.Logger()
        self.config = config.Config()
        self.decoder = decoder.Decoder()
        self.coderategenerator = codegen.Codegen()
        self.init = True
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    def startup_processes(self):
        self.load_config()
        self.polling_prohibited = (True, self.__class__)
        # self.set_speed_signal()

    def set_speed_signal(self, sg: int, speed: int, direction: int) -> int:
        """depending on speed and direction, speed will be incremented or
        decremeneted
        :rtype: int
        :param sg: speed signal generator 0 or 1
        :param speed: how fast did encoder turn?
        :param direction: direction determines incremeneting or decrementing
        :return: actual frequency or signal
        """
        global speed_text, direction_text
        if sg == 0:
            cs = Speedgen.SPEED_0_CS
        if sg == 1:
            cs = Speedgen.SPEED_1_CS
        if speed == Speedgen.SPEED_SLOW:
            speed_text = "SLOW"
        if speed == Speedgen.SPEED_FAST:
            speed_text = "FAST"
        if direction == Speedgen.CLOCKWISE:
            direction_text = "CLOCKWISE"
        if direction == Speedgen.ANTI_CLOCKWISE:
            direction_text = "ANTI CLOCKWISE"
        if direction == Speedgen.ERROR:
            direction_text = "ERROR"
        self.log.debug(
            'SIGGEN Setting speed of SG:{}  with speed of:{}  direction:{} '.format(sg, speed_text, direction_text))
        if direction == self.CLOCKWISE:
            if speed == self.SPEED_SLOW:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY[sg] + self.FREQ_SLOW_INCREMENT
            elif speed == self.SPEED_FAST:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY[sg] + self.FREQ_FAST_INCREMENT
            if self.SPEED_FREQUENCY[sg] > self.SPEED_FREQUENCY_MAX:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY_MAX
        elif direction == self.ANTI_CLOCKWISE:
            if speed == self.SPEED_SLOW:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY[
                                               sg] - self.FREQ_SLOW_INCREMENT
            elif speed == self.SPEED_FAST:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY[
                                               sg] - self.FREQ_FAST_INCREMENT
            if self.SPEED_FREQUENCY[sg] < self.SPEED_FREQUENCY_MIN:
                self.SPEED_FREQUENCY[sg] = self.SPEED_FREQUENCY_MIN
        self.speed1_actual_freq = self.SPEED_FREQUENCY[0]
        self.speed2_actual_freq = self.SPEED_FREQUENCY[1]
        self.log.debug('SIGGEN Speed 1 Actual Freq: {}'.format(self.speed1_actual_freq))
        self.log.debug('SIGGEN Speed 2 Actual Freq: {}'.format(self.speed2_actual_freq))
        if sg == 0:
            return self.speed1_actual_freq, cs
        if sg == 1:
            return self.speed2_actual_freq, cs

    def speed_off(self, speed_generator: int) -> object:
        """pass speed generator 1 or 2
        :rtype:
        :param speed_generator:
        """
        cs = None
        self.log.debug("Speed {} frequency generator setting to OFF".format(speed_generator))
        self.SPEED_FREQUENCY[speed_generator] = 0
        if speed_generator == 1:
            cs = self.decoder.chip_select_speed_tach_1
        elif speed_generator == 2:
            cs = self.decoder.chip_select_speed_tach_2
        self.set_speed_signal(cs, self.SPEED_SLOW,
                              self.ANTI_CLOCKWISE)
        return True

    def load_config(self):
        self.primary_source_frequency = self.config.primary_source_frequency
        self.secondary_source_frequency = self.config.secondary_source_frequency
        self.primary_freq_gen_constant = self.config.primary_freq_gen_constant  # 268435456.00  # 2^28
        self.secondary_freq_gen_constant = self.config.secondary_freq_gen_constant  # 268435456.00  # 2^28
        self.speed_generator_set_speed_spi_header = self.config.speed_generator_set_speed_spi_header  # [0x20, 0x00]
        self.freq_shape = [self.FREQ_SHAPE_SINE, self.FREQ_SHAPE_SINE]
        self.SPEED_0_CS = self.config.SPEED_0_CS  # 6  # SPEED SIMULATION TACH 1
        self.SPEED_1_CS = self.config.SPEED_1_CS  # 7  # SPEED SIMULATION TACH 2
        Speedgen.primary_source_frequency = self.primary_source_frequency
        Speedgen.secondary_source_frequency = self.secondary_source_frequency
        Speedgen.primary_freq_gen_constant = self.primary_freq_gen_constant  # 26
        Speedgen.secondary_freq_gen_constant = self.secondary_freq_gen_constant
        Speedgen.speed_generator_set_speed_spi_header = self.speed_generator_set_speed_spi_header
