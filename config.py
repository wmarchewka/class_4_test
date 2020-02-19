import configparser
import ast
import logging
import logger


class Config(object):

    logging.info("Instantiating {} class...".format(__qualname__))

    _init = None
    config_file_path = "config/config.ini"
    logging.info("Logging config file path {}".format(config_file_path))
    logging.info('Loading log configuration from {}'.format(config_file_path))
    config = configparser.ConfigParser()
    config.sections()
    config.read_file(open(config_file_path))

    @classmethod
    def read_from_ini(cls):    

        # GPIO
        cls.ports = cls.config.get('GPIO', 'ports')  # read in from INI file
        cls.ports = ast.literal_eval(cls.ports)

        # ROTARY SECTION

        # DIGITAL POT SECTION


        # SPEED GENERATOR SECTION
        cls.freq_regs_max = cls.config.getint('SPEED_GENERATOR', 'freq_regs_max')
        cls.freq_regs_min = cls.config.getint('SPEED_GENERATOR', 'freq_regs_min')
        cls.primary_source_frequency = cls.config.getfloat('SPEED_GENERATOR', 'primary_source_frequency')
        cls.secondary_source_frequency = cls.config.getfloat('SPEED_GENERATOR', 'secondary_source_frequency')
        cls.primary_freq_gen_constant = cls.config.getfloat('SPEED_GENERATOR', 'primary_freq_gen_constant')
        cls.secondary_freq_gen_constant = cls.config.getfloat('SPEED_GENERATOR', 'secondary_freq_gen_constant')
        cls.REG_OFF = cls.config.get('SPEED_GENERATOR', 'REG_OFF')
        cls.REG_OFF = ast.literal_eval(cls.REG_OFF)
        cls.speed_generator_set_speed_spi_header = cls.config.get("SPEED_GENERATOR", 'set_speed_spi_header')
        cls.speed_generator_set_speed_spi_header = list(ast.literal_eval(cls.speed_generator_set_speed_spi_header))

        cls.SPEED_0_CS = cls.config.getint('SPEED_GENERATOR', 'SPEED_0_CS')
        cls.SPEED_1_CS = cls.config.getint('SPEED_GENERATOR', 'SPEED_1_CS')
        cls.SPEED_0_thresholds = cls.config.get('SPEED_GENERATOR', 'speed_0_thresholds')
        cls.SPEED_1_thresholds = cls.config.get('SPEED_GENERATOR', 'speed_1_thresholds')
        cls.SPEED_0_thresholds = ast.literal_eval(cls.SPEED_0_thresholds)
        cls.SPEED_1_thresholds = ast.literal_eval(cls.SPEED_1_thresholds)
        cls.rotary_0_pins = cls.config.get('SPEED_GENERATOR', 'rotary_0_pins')
        cls.rotary_0_pins = ast.literal_eval(cls.rotary_0_pins)
        cls.rotary_1_pins = cls.config.get('SPEED_GENERATOR', 'rotary_1_pins')
        cls.rotary_1_pins = ast.literal_eval(cls.rotary_1_pins)
        cls.rotary_0_pin_0_debounce = cls.config.getint('SPEED_GENERATOR', 'rotary_0_pin_0_debounce_microseconds')
        cls.rotary_0_pin_1_debounce = cls.config.getint('SPEED_GENERATOR', 'rotary_0_pin_1_debounce_microseconds')
        cls.rotary_1_pin_0_debounce = cls.config.getint('SPEED_GENERATOR', 'rotary_1_pin_0_debounce_microseconds')
        cls.rotary_1_pin_1_debounce = cls.config.getint('SPEED_GENERATOR', 'rotary_1_pin_1_debounce_microseconds')
        cls.speed_0_shape = cls.config.getint('SPEED_GENERATOR', 'speed_0_shape')
        cls.speed_1_shape = cls.config.getint('SPEED_GENERATOR', 'speed_1_shape')
        cls.speed_0_spi_channel = cls.config.getint('SPEED_GENERATOR', 'speed_0_spi_channel')
        cls.speed_1_spi_channel = cls.config.getint('SPEED_GENERATOR', 'speed_1_spi_channel')
        cls.speed_0_name = cls.config.get('SPEED_GENERATOR', 'speed_0_name')
        cls.speed_1_name = cls.config.get('SPEED_GENERATOR', 'speed_1_name')

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

        # CODERATE
        cls.code_rate_generator_toggle_pin = cls.config.getint('CODE RATE', 'code_rate_mux_pin')

        #GUI
        cls.display_brightness = cls.config.getint('MAIN', 'screen_brightness')
        cls.guiname = cls.config.get('MAIN', 'gui')
        cls.poll_timer_interval = cls.config.getint('MAIN', 'poll_timer_interval')
        cls.local_timer_interval = cls.config.getint('MAIN', 'local_timer_interval')
        cls.sense_timer_interval = cls.config.getfloat('MAIN', 'sense_timer_interval')
        cls.switch_timer_interval = cls.config.getint('MAIN', 'switch_timer_interval')
        cls.screen_brightness_max = cls.config.getint('MAIN', 'screen_brightness_max')
        cls.screen_brightness_min = cls.config.getint('MAIN', 'screen_brightness_min')

        #GAINS
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


    def __init__(self):
        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger()
        if not Config._init:
            Config.read_from_ini()
            Config._init = True
            self.log.debug("FIRST SETUP OF CONFIG")
        self.log.debug("{} init complete...".format(__name__))

    # **************************************************************************
    def configuration_save(self, section, key, value):
        self.config.set(section, key, value)
        with open(self.config_file_path, 'w') as cf:
            self.config.write(cf)
        cf.close()
        self.log.info(
            "Configuration.ini updated: SECTION:{}  KEY:{}  VALUE:{}".format(section, key, value))
