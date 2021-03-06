# libraries
import os
import ast
import pigpio
import threading
import configparser

# my libraries
from logger import Logger


class Codegen():
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, config, logger, gpio, spi):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.logger = logger
        self.log = self.logger.log
        self.log.info('Starting up Coderate Generator...')
        self.gpio = gpio
        self.pi_gpio = self.gpio.gpio
        self.spi = spi
        self.config = config
        self.speed_generation_shape_override = None
        self.coded_carrier_pin_state = None
        self.coderate_ppm = None
        self.primary_frequency = None
        self.secondary_frequency = None
        self.primary_channel_chip_select_pin = None
        self.secondary_channel_chip_select_pin = None
        self.primary_source_frequency = None
        self.secondary_source_frequency = None
        self.shape_sine = None
        self.shape_sine_word = None
        self.shape_square = None
        self.shape_square_word = None
        self.shape_triangle = None
        self.shape_triangle_word = None
        self.duty_cycle = None
        self.pulses_per_second_default = None
        self.primary_channel_mux_pin = None
        self.secondary_channel_mux_pin = None
        self.coded_carrier_pin = None
        self.coderate_ppm = None
        self.pulses_per_second = None
        self.startup_processes()
        self.log.info("{} init complete...".format(__name__))

    # **************************************************************************************************
    def startup_processes(self):
        self.load_from_config()
        self.load_from_coderate()
        self.setup_gpio()
        self.coderate_stop()

    # **************************************************************************************************
    def setup_gpio(self):
        try:
            self.pi_gpio.set_mode(self.coded_carrier_pin, pigpio.OUTPUT)
        except:
            self.log.exception("EXCEPTION in coderate_initialization")

    # **************************************************************************************************
    def load_from_coderate(self):
        cwd = os.getcwd()
        self.log.info("CWD: {}".format(cwd))
        config_file_path = "config/coderates.ini"
        self.log.info('Loading coderate template configuration from ' + str(config_file_path))
        config_coderates = configparser.ConfigParser()
        config_coderates.sections()
        config_coderates.read_file(open(config_file_path))
        self.frequencies = config_coderates.get('FREQUENCIES', 'frequencies')
        self.frequencies = ast.literal_eval(self.frequencies)
        self.coderates = config_coderates.get('CODERATES', 'coderates')
        self.coderates = ast.literal_eval(self.coderates)
        self.shape_default = self.shape_sine

    # **************************************************************************************************
    def load_from_config(self):
        # todo: need to open made config ini file
        self.primary_channel_chip_select_pin = self.config.primary_channel_chip_select_pin
        self.secondary_channel_chip_select_pin = self.config.secondary_channel_chip_select_pin
        self.primary_source_frequency = self.config.primary_source_frequency
        self.secondary_source_frequency = self.config.secondary_source_frequency
        self.shape_sine = self.config.shape_sine
        self.shape_square = self.config.shape_square
        self.shape_triangle = self.config.shape_triangle
        self.duty_cycle = self.config.duty_cycle
        self.pulses_per_second = self.config.pulses_per_second
        self.primary_channel_mux_pin = self.config.primary_channel_mux_pin
        self.secondary_channel_mux_pin = self.config.secondary_channel_mux_pin
        self.coded_carrier_pin = self.config.coded_carrier_pin
        self.shape_sine_word = self.config.shape_sine_word
        self.shape_sine_word = int(self.shape_sine_word, 16)
        self.shape_square_word = self.config.shape_square_word
        self.shape_square_word = int(self.shape_square_word, 16)
        self.shape_triangle_word = self.config.shape_triangle_word
        self.shape_triangle_word = int(self.shape_triangle_word, 16)

    # **************************************************************************************************
    def coderate_generate(self):
        """ coderate selection will send the appropriate coderate to be generated.  to generate a coderate we must
        program both the primary and secondary carrier frequency generators with the appropriate frequency.  then
        we must select between the 2 frequencies at the coderate passed to us
        generates code rate frquency which drives 4 channel multiplexer which is used to select between
        the code rate signal frequency and the carrier frequency at the appropriate rate.
        utilizing the PIGPIO library,we build a pulse of desired frequency and duty cycle and send
        out repeatedly"""
        coderate_ppm = self.coderate_ppm
        primary_freq = self.primary_frequency
        secondary_freq = self.secondary_frequency

        if coderate_ppm is not None and primary_freq is not None and secondary_freq is not None:
            self.log.info(
                "GENERATING CODERATE :{}ppm  FREQUENCY 0: {}hz   FREQUENCY 0:  {}hz ".format(coderate_ppm, primary_freq,
                                                                                             secondary_freq))
            if primary_freq is not 0:
                self.primary_frequency_generate(frequency=primary_freq)
            if secondary_freq is not 0:
                self.secondary_frequency_generate(frequency=secondary_freq)
            if coderate_ppm is not 0:
                self.coded_carrier_generate(coderate_ppm=coderate_ppm)
        else:
            self.log.info("Cound not generate coderate")

    # **************************************************************************************************
    def primary_frequency_generate(self, frequency=None, source_frequency=None, chip_select_pin=None,
                                   coded_carrier_pin=None, shape=None):
        """
        generates primary carrier frequency.  if frequency is greater than 1, then turn on the pin to the mux
        so that this is the only frequency passed through.  if both frequencies are present then the coded
        carrier will take over
        :param frequency:
        :param source_frequency:
        :param chip_select_pin:
        """
        if frequency is None:
            frequency = self.primary_frequency
        else:
            self.primary_frequency = frequency
        if frequency is not None:
            if source_frequency is None:
                source_frequency = self.primary_source_frequency
            if chip_select_pin is None:
                chip_select_pin = self.primary_channel_chip_select_pin
            if coded_carrier_pin is None:
                coded_carrier_pin = self.coded_carrier_pin
            if shape is None:
                shape = self.shape_default
            self.log.info(
                "PRI FREQ:{}  SOURCE FREQ:{}  CHIP_SELECT:{}  CODED CARRIER PIN:{}  SHAPE:{}".format(frequency,
                                                                                                     source_frequency,
                                                                                                     chip_select_pin,
                                                                                                     coded_carrier_pin,
                                                                                                     shape))
            self.frequency_to_registers(frequency=frequency, source_frequency=source_frequency, shape=shape,
                                        chip_select=chip_select_pin)
            self.pi_gpio.write(coded_carrier_pin, self.primary_channel_mux_pin)
        else:
            self.log.info("Setting PRIMARY FREQUENCY OFF")

    # **************************************************************************************************
    def secondary_frequency_generate(self, frequency=None, source_frequency=None, chip_select_pin=None,
                                     coded_carrier_pin=None, shape=None):
        """
        generates primary carrier frequency.  if frequency is greater than 1, then turn on the pin to the mux
        so that this is the only frequency passed through.  if both frequencies are present then the coded
        carrier will take over
        :param frequency:
        :param source_frequency:
        :param chip_select_pin:
        """
        if frequency is None:
            frequency = self.secondary_frequency
        else:
            self.secondary_frequency = frequency
        if frequency is not None:
            if source_frequency is None:
                source_frequency = self.primary_source_frequency
            if chip_select_pin is None:
                chip_select_pin = self.primary_channel_chip_select_pin
            if coded_carrier_pin is None:
                coded_carrier_pin = self.coded_carrier_pin
            if shape is None:
                shape = self.shape_default
            self.log.info(
                "SEC FREQ:{} SOURCE FREQ:{}  CHIP_SELECT:{}  CODED CARRIER PIN:{}  SHAPE:{}".format(frequency,
                                                                                                    source_frequency,
                                                                                                    chip_select_pin,
                                                                                                    coded_carrier_pin,
                                                                                                    shape))
            self.frequency_to_registers(frequency=frequency, source_frequency=source_frequency, shape=shape,
                                        chip_select=chip_select_pin)
            self.pi_gpio.write(coded_carrier_pin, self.secondary_channel_mux_pin)

        else:
            self.log.info("Setting SECONDARY FREQUENCY OFF")

    # **************************************************************************************************
    def coded_carrier_generate(self, coderate_ppm=None, duty_cycle=None):
        if coderate_ppm is None:
            coderate_ppm = self.coderate_ppm
        else:
            self.coderate_ppm = coderate_ppm
        if duty_cycle is None:
            duty_cycle = self.duty_cycle
        else:
            self.duty_cycle = duty_cycle
        self.pi_gpio.wave_clear()
        pulse = []
        if (coderate_ppm is not 0 and coderate_ppm is not None) and duty_cycle is not None:
            coderate_period_in_microseconds = int((1 / (coderate_ppm / 60.0)) * self.pulses_per_second)
            coderate_positive_pulse = int(coderate_period_in_microseconds * (duty_cycle / 100))
            coderate_negative_pulse = int(coderate_period_in_microseconds * (1 - (duty_cycle / 100)))
            pulse.append(pigpio.pulse(1 << self.coded_carrier_pin, 0, coderate_positive_pulse))
            pulse.append(pigpio.pulse(0, 1 << self.coded_carrier_pin, coderate_negative_pulse))
            self.pi_gpio.wave_add_generic(pulse)  # add waveform
            self.waveform1 = self.pi_gpio.wave_create()
            self.pi_gpio.wave_send_repeat(self.waveform1)
            self.log.info('Starting code rate  DUTY CYCLE:{}   PPM:{}'.format(duty_cycle, coderate_ppm))
            val = threading.current_thread(), threading.current_thread().name
            self.log.info("THREAD " + str(val))
        # elif coderate_ppm is 0:
        #     self.coderate_stop()
        else:
            self.log.info("COULD NOT GENERATE CODERATE")

    # **************************************************************************************************
    def off(self):
        self.coderate_stop()
        self.coderate_ppm = 0
        self.primary_frequency = 0
        self.secondary_frequency = 0
        self.coderate_generate()

    # **************************************************************************************************
    def coderate_stop(self):
        self.log.info("Stopping CODERATE")
        if self.pi_gpio.wave_tx_busy():
            self.pi_gpio.wave_tx_stop()
            # self.pi_gpio.wave_clear()

    # **************************************************************************************************
    def frequency_to_registers(self, frequency, source_frequency, shape, chip_select):

        self.spi_msg = []
        self.log.info(
            "FREQ TO REG running with FREQ:{} CLK FREQ:{} SHAPE:{}  CS:{}".format(frequency,
                                                                                  source_frequency, shape,
                                                                                  chip_select))
        word = hex(int(round((frequency * 2 ** 28) / source_frequency)))  # Calculate frequency word to send
        if shape == self.shape_square:  # square
            shape_word = self.shape_square_word
        elif shape == self.shape_triangle:  # triangle
            shape_word = self.shape_triangle_word
        else:
            shape_word = self.shape_sine_word  # sine
        MSB = (int(word, 16) & 0xFFFC000) >> 14  # Split frequency word onto its separate bytes
        LSB = int(word, 16) & 0x3FFF
        MSB |= 0x4000  # Set control bits DB15 = 0 and DB14 = 1; for frequency register 0
        LSB |= 0x4000
        self._ad9833_append(0x2100)
        self._ad9833_append(LSB)  # lower 14 bits
        self._ad9833_append(MSB)  # Upper 14 bits
        self._ad9833_append(shape_word)
        return (self.spi_msg, chip_select)

    # **************************************************************************************************
    def _ad9833_append(self, integer):
        high, low = divmod(integer, 0x100)
        self.spi_msg.append(high)
        self.spi_msg.append(low)

    # **************************************************************************************************
    def code_rate_toggle(self):
        self.coded_carrier_pin_state = not self.coded_carrier_pin_state
        self.pi_gpio.write(self.coded_carrier_pin, self.coded_carrier_pin_state)

    # **************************************************************************************************
    # # CURRENTLY NOT USED
    # def pulse_codes_from_company(self, company):
    #     self.log.info("Reading pulsecode data from INI file for company  {}".format(company))
    #     good_list = []
    #     values = []
    #     company_data = self.config_coderates.items(company)
    #     company_pulsecodes = filter(lambda x: x[0].startswith('pulsecode'), company_data)
    #     data = list(company_pulsecodes)
    #     for k in data:
    #         # print(k[0])
    #         # print(k[1])
    #         coderate_list = k[1].split(",")
    #         # print("Coderate list {}".format(coderate_list))
    #         for x in coderate_list:
    #             # print('x={}'.format(x))
    #             for y in self.coderates:
    #                 # print('y={}'.format(y))
    #                 if x == y[0]:
    #                     good_list.append(y[1])
    #             for y in self.carrier_freq:
    #                 # print('y={}'.format(y))
    #                 if x == y[0]:
    #                     good_list.append(y[1])
    #         values.append(good_list)
    #         good_list = []
    #     # print(values)
    #     # print(values[0])
    #     # print(values[1])
    #     # print(values[2])
    #     return values

    # **************************************************************************************************
    # def generate_test_pulse(self, values):
    #     # This is used to generate the pulses from RPI pins.  This is not implemented currently.  We are using a
    #     # freq generator for each carrier and then switching between them to generate the coderate.
    #     # TODO  when we talk about shifting the duty cycle, are we shifting the duty cycle for each carriers freqeuency
    #     # TODO or are we shiting the carrier for the code rate, meaning less or more of each carrier?
    #
    #     # we are passed a coderate (in pulses per miunute) and a frequency for one or two of the carrier frequencies.
    #     # the pulse train is generated by taking the coderate frequency (in hertz) and then switching on an euen portion
    #     # of each carrier.  if a carrier is missing, it will be turned off for that portion.
    #     # if we are sent a 180 coderate with a 100hz primary freq and a 250hz secondary freq, the pulse waveform would
    #     # look like this:  180 coderate = 180 pulses per minute or 3 pulses per second (3hz). each period is 333ms.
    #     # that means each positive wave is 1/2 of that at 50 % duty cycle, or 166.66 ms.
    #     # next we have to generate so many pulses of each waveform for the amount of the pos and neg time so since
    #     # the pos period is 166.66ms we take the primary freq period (100hz at 1/100 = 0.010 or 10 ms. so dividing the
    #     # pos period of 166.66 / 10ms we get 16.66 waveforms we need to make.  each positive will be 1/2 that for 50%
    #     # duty cycle, or 8.33ms for each positive and 8.33ms for each negative.
    #     duty_cycle = 50
    #     pulses_per_second = 1000000.0
    #     primary_code_rate_generator_toggle_pin = 27
    #     secondary_code_rate_generator_toggle_pin = 22
    #
    #     self.log.info("Generating Test Pulse")
    #     self.pi_gpio.wave_clear()
    #     coderate1_ppm = values[0]
    #     carrier_freq1 = values[1]
    #     coderate2_ppm = values[2]
    #     carrier_freq2 = values[3]
    #
    #     self.pi_gpio.set_mode(primary_code_rate_generator_toggle_pin, pigpio.OUTPUT)
    #     self.pi_gpio.set_mode(secondary_code_rate_generator_toggle_pin, pigpio.OUTPUT)
    #     self.pi_gpio.wave_tx_stop()
    #
    #     self.log.info(
    #         "Received values to generate waveform: CODERATE 1:{}ppm  FREQUENCY 1: {}hz   CODERATE 2: {}ppm  FREQUENCY 2:  {}hz ".format(
    #             coderate1_ppm, carrier_freq1, coderate2_ppm, carrier_freq2))
    #     coderate1_period_in_microseconds = int((1 / (coderate1_ppm / 60.0)) * pulses_per_second)
    #     coderate2_period_in_microseconds = int((1 / (coderate2_ppm / 60.0)) * pulses_per_second)
    #     self.log.info("Calculated CODERATE 1 PERIOD: {}usecs   CODERATE 2 PERIOD:  {}usecs".format(
    #         coderate1_period_in_microseconds, coderate2_period_in_microseconds))
    #     coderate1_positive_pulse = int(coderate1_period_in_microseconds * (duty_cycle / 100))
    #     coderate1_negative_pulse = int(coderate1_period_in_microseconds * (1 - (duty_cycle / 100)))
    #     coderate2_positive_pulse = int(coderate1_period_in_microseconds * (duty_cycle / 100))
    #     coderate2_negative_pulse = int(coderate1_period_in_microseconds * (1 - (duty_cycle / 100)))
    #     self.log.info(
    #         'CODERATE 1 POS PULSE:{}Usecs   CODERATE 1 NEG PULSE:{}uSecs   CODERATE 2 POS PULSE:{}Usecs   CODERATE 2 NEG PULSE"{}Usecs'.format(
    #             coderate1_positive_pulse, coderate1_negative_pulse, coderate2_positive_pulse, coderate2_negative_pulse))
    #     # generate primary carrier frequency
    #     # assuming 50% duty cycle
    #     primary_carrier_positive_pulse_microseconds = int(((1 / carrier_freq1) / 2) * pulses_per_second)
    #     primary_carrier_negative_pulse_microseconds = int(((1 / carrier_freq1) / 2) * pulses_per_second)
    #     secondary_carrier_positive_pulse_microseconds = int(((1 / carrier_freq2) / 2) * pulses_per_second)
    #     secondary_carrier_negative_pulse_microseconds = int(((1 / carrier_freq2) / 2) * pulses_per_second)
    #     self.log.info(
    #         "PRI CARRIER POS PULSE {}uSec PRI CARRIER NEG PULSE {}uSec   SEC CARRIER POS PULSE {}uSec SEC CARRIER NEG PULSE {}uSec".format(
    #             primary_carrier_positive_pulse_microseconds, primary_carrier_negative_pulse_microseconds,
    #             secondary_carrier_positive_pulse_microseconds, secondary_carrier_negative_pulse_microseconds))
    #
    #     pulse = []
    #     wavelength = coderate1_positive_pulse
    #     while wavelength is not 0:
    #         # prim car pos
    #         if wavelength > primary_carrier_positive_pulse_microseconds:
    #             pulse.append(
    #                 pigpio.pulse(1 << primary_code_rate_generator_toggle_pin, 0,
    #                              primary_carrier_positive_pulse_microseconds))
    #             wavelength = wavelength - primary_carrier_positive_pulse_microseconds
    #             self.log.info('ADDING  PRI CAR POS PULSE WITH LENGTH OF  {}USECS'.format(
    #                 primary_carrier_positive_pulse_microseconds))
    #         else:
    #             pulse.append(pigpio.pulse(1 << primary_code_rate_generator_toggle_pin, 0, wavelength))
    #             self.log.info('ADDING  PRI CAR POS PULSE WITH LENGTH OF  {}USECS'.format(wavelength))
    #             wavelength = wavelength - wavelength
    #
    #         # pri car neg
    #         if wavelength > primary_carrier_negative_pulse_microseconds:
    #             pulse.append(
    #                 pigpio.pulse(0, 1 << primary_code_rate_generator_toggle_pin,
    #                              primary_carrier_negative_pulse_microseconds))
    #             wavelength = wavelength - primary_carrier_negative_pulse_microseconds
    #             self.log.info('ADDING  PRI CAR NEG PULSE WITH LENGTH OF  {}USECS'.format(
    #                 primary_carrier_negative_pulse_microseconds))
    #         else:
    #             pulse.append(pigpio.pulse(0, 1 << primary_code_rate_generator_toggle_pin, wavelength))
    #             self.log.info('ADDING  PRI CAR NEG PULSE WITH LENGTH OF  {}USECS'.format(wavelength))
    #             wavelength = wavelength - wavelength
    #         self.log.info('Wavelength {}'.format(wavelength))
    #
    #     wavelength = coderate2_positive_pulse
    #     while wavelength is not 0:
    #         # sec car pos
    #         if wavelength > secondary_carrier_positive_pulse_microseconds:
    #             pulse.append(
    #                 pigpio.pulse(1 << secondary_code_rate_generator_toggle_pin, 0,
    #                              secondary_carrier_positive_pulse_microseconds))
    #             wavelength = wavelength - secondary_carrier_positive_pulse_microseconds
    #             self.log.info('ADDING  SEC CAR POS PULSE WITH LENGTH OF  {}Usecs'.format(
    #                 secondary_carrier_positive_pulse_microseconds))
    #         else:
    #             pulse.append(pigpio.pulse(1 << secondary_code_rate_generator_toggle_pin, 0, wavelength))
    #             self.log.info('ADDING  SEC CAR POS PULSE WITH LENGTH OF  {}Usecs'.format(wavelength))
    #             wavelength = wavelength - wavelength
    #
    #         # sec car neg
    #         if wavelength > secondary_carrier_negative_pulse_microseconds:
    #             pulse.append(
    #                 pigpio.pulse(0, 1 << secondary_code_rate_generator_toggle_pin,
    #                              secondary_carrier_negative_pulse_microseconds))
    #             wavelength = wavelength - secondary_carrier_negative_pulse_microseconds
    #             self.log.info('ADDING  SEC CAR NEG PULSE WITH LENGTH OF  {}Usecs'.format(
    #                 secondary_carrier_negative_pulse_microseconds))
    #         else:
    #             pulse.append(pigpio.pulse(0, 1 << secondary_code_rate_generator_toggle_pin, wavelength))
    #             self.log.info('ADDING  SEC CAR NEG PULSE WITH LENGTH OF  {}Usecs'.format(
    #                 wavelength))
    #             wavelength = wavelength - wavelength
    #         self.log.info('Wavelength {}'.format(wavelength))
    #     self.pi_gpio.wave_add_generic(pulse)  # add waveform
    #     pulses = self.pi_gpio.wave_get_pulses()
    #     micros = self.pi_gpio.wave_get_micros()
    #     self.log.info("Waveform PULSES {}   MICROS {}".format(pulses, micros))
    #     wf = self.pi_gpio.GPIO.wave_create()
    #     self.pi_gpio.GPIO.wave_send_repeat(wf)
