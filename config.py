import configparser
import ast

# my libraries
from logger import Logger


class Config():

    Logger.log.info("Instantiating {} class...".format(__qualname__))

    _init = None
    config_file_path = "config/config.ini"
    Logger.log.info("Logging config file path {}".format(config_file_path))
    Logger.log.info('Loading log configuration from {}'.format(config_file_path))
    config = configparser.ConfigParser()
    config.sections()
    config.read_file(open(config_file_path))

    @classmethod
    def read_from_ini(cls):
        # GPIO
        cls.ports = cls.config.get('GPIO', 'ports')  # read in from INI file
        cls.ports = ast.literal_eval(cls.ports)

        # ROTARY SECTION

        #CURRENT SENSE
        cls.adc_scale = cls.config.getfloat('CURRENTSENSE', 'adc_scale')
        cls.sense_amp_max_amps = cls.config.getint('CURRENTSENSE', 'sense_amp_max_amps')
        cls.sense_ad_vin = cls.config.getfloat('CURRENTSENSE', 'sense_ad_vin')  # LM4128CQ1MF3.3/NOPB voltage reference
        cls.sense_ad_max_bits = cls.config.getint('CURRENTSENSE', 'sense_ad_max_bits')  # AD7940 ADC
        cls.sense_scaling_factor_mv_amp = cls.config.getfloat('CURRENTSENSE', 'sense_scaling_factor_mv_amp')  # 110 milivolts per amp
        cls.display_amps_template = cls.config.get('CURRENTSENSE', 'display_amps_template')
        cls.loop_current_template = cls.config.get('CURRENTSENSE', 'loop_current_template')
        cls.adc_counts_template = cls.config.get('CURRENTSENSE', 'adc_counts_template')
        cls.adc_template = cls.config.get('CURRENTSENSE', 'adc_template')

        # SPEED GENERATOR SECTION
        cls.freq_regs_max = cls.config.getint('SPEEDGEN', 'freq_regs_max')
        cls.freq_regs_min = cls.config.getint('SPEEDGEN', 'freq_regs_min')
        cls.primary_source_frequency = cls.config.getfloat('SPEEDGEN', 'primary_source_frequency')
        cls.secondary_source_frequency = cls.config.getfloat('SPEEDGEN', 'secondary_source_frequency')
        cls.primary_freq_gen_constant = cls.config.getfloat('SPEEDGEN', 'primary_freq_gen_constant')
        cls.secondary_freq_gen_constant = cls.config.getfloat('SPEEDGEN', 'secondary_freq_gen_constant')
        cls.REG_OFF = cls.config.get('SPEEDGEN', 'REG_OFF')
        cls.REG_OFF = ast.literal_eval(cls.REG_OFF)
        cls.speed_generator_set_speed_spi_header = cls.config.get("SPEEDGEN", 'set_speed_spi_header')
        cls.speed_generator_set_speed_spi_header = list(ast.literal_eval(cls.speed_generator_set_speed_spi_header))
        cls.SPEED_0_CS = cls.config.getint('SPEEDGEN', 'SPEED_0_CS')
        cls.SPEED_1_CS = cls.config.getint('SPEEDGEN', 'SPEED_1_CS')
        cls.SPEED_0_thresholds = cls.config.get('SPEEDGEN', 'speed_0_thresholds')
        cls.SPEED_1_thresholds = cls.config.get('SPEEDGEN', 'speed_1_thresholds')
        cls.SPEED_0_thresholds = ast.literal_eval(cls.SPEED_0_thresholds)
        cls.SPEED_1_thresholds = ast.literal_eval(cls.SPEED_1_thresholds)
        cls.rotary_0_pins = cls.config.get('SPEEDGEN', 'rotary_0_pins')
        cls.rotary_0_pins = ast.literal_eval(cls.rotary_0_pins)
        cls.rotary_1_pins = cls.config.get('SPEEDGEN', 'rotary_1_pins')
        cls.rotary_1_pins = ast.literal_eval(cls.rotary_1_pins)
        cls.rotary_0_pin_0_debounce = cls.config.getint('SPEEDGEN', 'rotary_0_pin_0_debounce_microseconds')
        cls.rotary_0_pin_1_debounce = cls.config.getint('SPEEDGEN', 'rotary_0_pin_1_debounce_microseconds')
        cls.rotary_1_pin_0_debounce = cls.config.getint('SPEEDGEN', 'rotary_1_pin_0_debounce_microseconds')
        cls.rotary_1_pin_1_debounce = cls.config.getint('SPEEDGEN', 'rotary_1_pin_1_debounce_microseconds')
        cls.speed_0_shape = cls.config.getint('SPEEDGEN', 'speed_0_shape')
        cls.speed_1_shape = cls.config.getint('SPEEDGEN', 'speed_1_shape')
        cls.speed_0_spi_channel = cls.config.getint('SPEEDGEN', 'speed_0_spi_channel')
        cls.speed_1_spi_channel = cls.config.getint('SPEEDGEN', 'speed_1_spi_channel')
        cls.speed_0_name = cls.config.get('SPEEDGEN', 'speed_0_name')
        cls.speed_1_name = cls.config.get('SPEEDGEN', 'speed_1_name')
        cls.SPEED_FREQUENCY_MIN = cls.config.getint('SPEEDGEN', 'SPEED_FREQUENCY_MIN')
        cls.SPEED_FREQUENCY_MAX = cls.config.getint('SPEEDGEN', 'SPEED_FREQUENCY_MAX')
        cls.FREQ_SHAPE_SINE = cls.config.getint('SPEEDGEN', 'FREQ_SHAPE_SINE')
        cls.FREQ_SHAPE_SQUARE = cls.config.getint('SPEEDGEN', 'FREQ_SHAPE_SQUARE')
        cls.FREQ_SHAPE_TRIANGLE = cls.config.getint('SPEEDGEN', 'FREQ_SHAPE_TRIANGLE')
        cls.CLOCKWISE = cls.config.getint('SPEEDGEN', 'CLOCKWISE')
        cls.ANTI_CLOCKWISE = cls.config.getint('SPEEDGEN', 'ANTI_CLOCKWISE')
        cls.DIRECTION_ERROR = cls.config.getint('SPEEDGEN', 'DIRECTION_ERROR')
        cls.ERROR = cls.config.getint('SPEEDGEN', 'ERROR')
        cls.SPEED_REG = cls.config.getint('SPEEDGEN', 'SPEED_REG')
        cls.FREQ_SHAPE = cls.config.get('SPEEDGEN', 'FREQ_SHAPE')
        cls.FREQ_SHAPE = ast.literal_eval(cls.FREQ_SHAPE)

        # DECODER SECTION
        cls.decoder_pin_select = cls.config.get('DECODER', 'pin_select')
        cls.decoder_pin_select = ast.literal_eval(cls.decoder_pin_select)
        cls.decoder_pin_A = cls.config.get('DECODER', 'decoder_pin_A')
        cls.decoder_pin_A = ast.literal_eval(cls.decoder_pin_A)
        cls.decoder_pin_B = cls.config.get('DECODER', 'decoder_pin_B')
        cls.decoder_pin_B = ast.literal_eval(cls.decoder_pin_B)
        cls.decoder_pin_C = cls.config.get('DECODER', 'decoder_pin_C')
        cls.decoder_pin_C = ast.literal_eval(cls.decoder_pin_C)

        # SPI SECTION
        cls.spi_bus = cls.config.getint('SPI', 'spi_bus')
        cls.spi_chip_select = list(range(3))
        cls.spi_chip_select[0] = cls.config.getint('SPI', 'spi1_0_chip_select')
        cls.spi_chip_select[2] = cls.config.getint('SPI', 'spi1_2_chip_select')
        cls.spi1_0_max_speed_hz = cls.config.getint('SPI', 'spi1_0_max_speed_hz')
        cls.spi1_2_max_speed_hz = cls.config.getint('SPI', 'spi1_2_max_speed_hz')
        cls.spi1_0_mode = cls.config.getint('SPI', 'spi1_0_mode')
        cls.spi1_2_mode = cls.config.getint('SPI', 'spi1_2_mode')

        # CODEGEN
        cls.coded_carrier_pin = cls.config.getint('CODEGEN', 'coded_carrier_pin')
        cls.primary_channel_chip_select_pin = cls.config.getint('CODEGEN', 'primary_channel_chip_select_pin')
        cls.secondary_channel_chip_select_pin = cls.config.getint('CODEGEN', 'secondary_channel_chip_select_pin')
        cls.primary_source_frequency = cls.config.getint('CODEGEN', 'primary_source_frequency')
        cls.secondary_source_frequency = cls.config.getint('CODEGEN', 'secondary_source_frequency')
        cls.shape_sine = cls.config.getint('CODEGEN', 'shape_sine')
        cls.shape_square = cls.config.getint('CODEGEN', 'shape_square')
        cls.shape_triangle = cls.config.getint('CODEGEN', 'shape_triangle')
        cls.duty_cycle = cls.config.getfloat('CODEGEN', 'duty_cycle')
        cls.pulses_per_second = cls.config.getfloat('CODEGEN', 'pulses_per_second')
        cls.primary_channel_mux_pin = cls.config.getint('CODEGEN', 'primary_channel_mux_pin')
        cls.secondary_channel_mux_pin = cls.config.getint('CODEGEN', 'secondary_channel_mux_pin')
        cls.shape_sine_word = cls.config.get('CODEGEN', 'shape_sine_word')
        cls.shape_square_word = cls.config.get('CODEGEN', 'shape_square_word')
        cls.shape_triangle_word = cls.config.get('CODEGEN', 'shape_triangle_word')

        # GUI
        cls.display_brightness = cls.config.getint('MAIN', 'display_brightness')
        cls.guiname = cls.config.get('MAIN', 'guiname')
        cls.poll_timer_interval = cls.config.getint('MAIN', 'poll_timer_interval')
        cls.display_timer_interval = cls.config.getint('MAIN', 'display_timer_interval')
        cls.sense_timer_interval = cls.config.getfloat('MAIN', 'sense_timer_interval')
        cls.switch_timer_interval = cls.config.getint('MAIN', 'switch_timer_interval')
        cls.screen_brightness_max = cls.config.getint('MAIN', 'screen_brightness_max')
        cls.screen_brightness_min = cls.config.getint('MAIN', 'screen_brightness_min')

        # GAINS
        cls.rotary_2_pins = cls.config.get('GAINS', 'rotary_2_pins')
        cls.rotary_2_pins = ast.literal_eval(cls.rotary_2_pins)
        cls.rotary_3_pins = cls.config.get('GAINS', 'rotary_3_pins')
        cls.rotary_3_pins = ast.literal_eval(cls.rotary_3_pins)
        cls.rotary_2_pin_0_debounce = cls.config.getint('GAINS', 'rotary_2_pin_0_debounce_microseconds')
        cls.rotary_2_pin_1_debounce = cls.config.getint('GAINS', 'rotary_2_pin_1_debounce_microseconds')
        cls.rotary_3_pin_0_debounce = cls.config.getint('GAINS', 'rotary_3_pin_0_debounce_microseconds')
        cls.rotary_3_pin_1_debounce = cls.config.getint('GAINS', 'rotary_3_pin_1_debounce_microseconds')
        cls.gain_0_thresholds = cls.config.get('GAINS', 'gain_0_thresholds')
        cls.gain_1_thresholds = cls.config.get('GAINS', 'gain_1_thresholds')
        cls.gain_0_thresholds = ast.literal_eval(cls.gain_0_thresholds)
        cls.gain_1_thresholds = ast.literal_eval(cls.gain_1_thresholds)
        cls.GAIN_0_CS = cls.config.getint('GAINS', 'gain_0_cs')
        cls.GAIN_1_CS = cls.config.getint('GAINS', 'gain_1_cs')
        cls.gain_0_spi_channel = cls.config.getint('GAINS', 'gain_0_spi_channel')
        cls.gain_1_spi_channel = cls.config.getint('GAINS', 'gain_1_spi_channel')
        cls.gain_0_name = cls.config.get('GAINS', 'gain_0_name')
        cls.gain_1_name = cls.config.get('GAINS', 'gain_1_name')

        #SWITCHES
        cls.switch_chip_select = cls.config.getint('SWITCH', 'switch_chip_select')


    def __init__(self, logger):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.logger=logger
        self.log = self.logger.log
        Config.read_from_ini()
        self.log.debug("{} init complete...".format(__name__))

    # **************************************************************************
    def startup_processes(self):
        pass

    # **************************************************************************
    def configuration_save(self, section, key, value):
        self.config.set(section, key, value)
        with open(self.config_file_path, 'w') as cf:
            self.config.write(cf)
        cf.close()
        self.log.info(
            "Configuration.ini updated: SECTION:{}  KEY:{}  VALUE:{}".format(section, key, value))
