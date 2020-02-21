# libraries
import logging

# my libraries
from logger import Logger
from config import Config
from decoder import Decoder
from spi import SPI
from rotary_new import Rotary
from pollperm import Pollperm


class Speedgen():

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
    DIRECTION_ERROR = 0
    ERROR = 0
    SPEED_REG = 0
    FREQ_SHAPE = [FREQ_SHAPE_SINE, FREQ_SHAPE_SINE]
    rotaries = []

    def __init__(self):
        super().__init__()
        self.new_speed_increment = 0
        self.logger = Logger()
        self.log = self.logger
        self.log = logging.getLogger()
        self.config = Config()
        self.decoder = Decoder()
        self.pollperm = Pollperm()
        self.spi = SPI()
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
        self.rotary = None
        self.delta = 0
        self.direction = 0
        self.speed = 0
        self.speed_frequency = 0
        self.speed_increment = 0
        self.direction_text = None
        self.spi_msg = None
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    def simulate(self, sim_pins):
        """
        allows simulation of speed signal
        :param sim_pins: pin numbers to simulate
        """
        tick = self.rotary.gpio.get_current_tick()
        self.rotary.interrupt_callback(0, 0, tick, True, sim_pins)

    # **************************************************************************************************************
    def startup_processes(self):
        """
        run any process that you need to at startup
        """
        self.load_config()
        self.create_rotary()
        self.speed_off()

    # **************************************************************************************************************
    def create_rotary(self):
        """creates rotary instance and also create global list of rotary encoders create across instances
        so that we can disable or enable all callbacks
        """
        self.rotary = Rotary(self.name, self.interrupt_callback, self.pin_0, self.pin_1,
                                        self.pin_0_debounce, self.pin_1_debounce)
        Speedgen.rotaries.append(self.rotary)

    # ***************************************************************************************************************
    def threshold_check(self, delta):
        """
        converts the delta time between encode clicks into an amount to add/subtract from the speed value
        :rtype: object
        """
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
    def bounds_check(self, simulate, speed_increment, direction):
        direction_text = None
        if not simulate:
            # this callback will move the dial on the screen.
            self.commander_speed_move_callback(self.name, direction, speed_increment)
        if direction == Speedgen.CLOCKWISE:
            direction_text = "CLOCKWISE"
            self.speed_frequency = self.speed_frequency + speed_increment
            if self.speed_frequency > self.SPEED_FREQUENCY_MAX:
                self.speed_frequency = self.SPEED_FREQUENCY_MAX
        elif direction == Speedgen.ANTI_CLOCKWISE:
            direction_text = "ANTI CLOCKWISE"
            self.speed_frequency = self.speed_frequency - speed_increment
            if self.speed_frequency < self.SPEED_FREQUENCY_MIN:
                self.speed_frequency = self.SPEED_FREQUENCY_MIN
        else:
            self.direction_text = "ERROR"
        self.log.debug("Simulate:{}  Speed Increment:{}  Direction:{}".format(simulate, speed_increment, direction_text))
        return self.speed_frequency

    # **************************************************************************************************************
    def interrupt_callback(self, delta: int, direction=None, simulate=None):
        """
        This is the callback that is sent to the rotary class and will be called when the rotary pins are
        interrupted.  The simulate is included so that if in simulation mode, we will not cause the front
        panel dial to move.
        :param delta:
        :param direction:
        :param simulate:
        """
        if direction is not Speedgen.DIRECTION_ERROR:
            delta = delta / 1000
            self.log.debug("{} Delta:{}".format(self.name, self.delta))
            self.log.debug("Thresholds {}".format(self.thresholds))
            speed_increment = self.threshold_check(delta)
            self.log.debug("Speed threshold {}".format(speed_increment))
            value = self.bounds_check(simulate, speed_increment, direction)
            self.log.info("{}  FREQ:{}".format(self.name, value))
            self.callback(self.name, value)
            spi_msg = self.frequency_to_registers(self.speed_frequency, self.shape)
            self.spi_send(spi_msg)
        else:
            self.log.debug("Direction error received")

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
        """
        takes a frquency and creates the correct registers to send to the ad9833 freq generating ic
        :param frequency: frequency in
        :param shape: shape in
        :return: creates return msg to send to ad9833
        """
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
    @staticmethod
    def _ad9833_append(integer, msg):
        """
        support function
        :param integer:
        :param msg:
        :return:
        """
        high, low = divmod(integer, 0x100)
        msg.append(high)
        msg.append(low)
        return msg

    # **************************************************************************************************************
    def load_config(self):
        """
        loads configuration information from config file
        """
        Speedgen.PRIMARY_SOURCE_FREQUENCY = self.config.primary_source_frequency
        Speedgen.SECONDARY_SOURCE_FREQUENCY = self.config.secondary_source_frequency
        Speedgen.PRIMARY_FREQ_GEN_CONSTANT = self.config.primary_freq_gen_constant  # 268435456.00  # 2^28
        Speedgen.SECONDARY_FREQ_GEN_CONSTANT = self.config.secondary_freq_gen_constant  # 268435456.00  # 2^28
        Speedgen.SPEED_GENERATOR_SET_SPEED_SPI_HEADER = self.config.speed_generator_set_speed_spi_header  # [0x20, 0x00]
        Speedgen.SPEED_0_THRESHOLDS = self.config.SPEED_0_thresholds
        Speedgen.SPEED_1_THRESHOLDS = self.config.SPEED_1_thresholds
