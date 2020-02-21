#libraries
import os
import pigpio
import threading
import logging

#my libraries
import logger
import config
import spi
import gpio
import configparser

class Codegen(object):

    logging.info("Instantiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.log.debug('Starting up Coderate Generator...')
        self.gpio = gpio.Gpio().gpio
        self.spi = spi.SPI()
        self.config = config.Config()
        self.speed_generation_shape_override = None
        self.coded_carrier_pin_state = 0
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    def startup_processes(self):
        self.coderate_stop()
        self.load_from_config()
        self.load_from_coderate()
        self.setup_gpio()

    def setup_gpio(self):
        try:
            self.gpio.set_mode(self.coded_carrier_pin, pigpio.OUTPUT)
        except:
            self.log.exception("EXCEPTION in coderate_initialization")

    def load_from_coderate(self):
        cwd = os.getcwd()
        self.log.debug("CWD: {}".format(cwd))
        config_file_path = "config/coderates.ini"
        self.log.debug('Loading coderate template configuration from ' + str(config_file_path))
        config_coderates = configparser.ConfigParser()
        config_coderates.sections()
        config_coderates.read_file(open(config_file_path))
        self.frequencies = config_coderates.items('CODERATES')
        self.coderates = config_coderates.items('FREQUENCIES')

    def load_from_config(self):
        # todo: need to open made config ini file
        self.primary_channel_chip_select_pin = 0
        self.secondary_channel_chip_select_pin = 2
        self.primary_source_frequency = 4915200
        self.secondary_source_frequency = 4915200
        self.shape_sine = 0
        self.shape_square = 1
        self.shape_triangle = 2
        self.duty_cycle_default = 50
        self.pulses_per_second_default = 1000000.0
        self.primary_channel_mux_pin = 0
        self.secondary_channel_mux_pin = 1
        self.shape_default = self.shape_sine
        self.coded_carrier_pin = self.config.code_rate_generator_toggle_pin

    def coderate_generate(self, coderate_data):
        # todo move to initializiation and place in INI
        """ coderate selection will send the appropriate coderate to be generated.  to generate a coderate we must
        program both the primary and secondary carrier frequency generators with the appropriate frequency.  then
        we must select between the 2 frequencies at the coderate passed to us
        generates code rate frquency which drives 4 channel multiplexer which is used to select between
        the code rate signal frequency and the carrier frequency at the appropriate rate.
        utilizing the PIGPIO library,we build a pulse of desired frequency and duty cycle and send
        out repeatedly"""
        coderate_ppm = int(coderate_data[0])
        primary_freq = int(coderate_data[1])
        secondary_freq = int(coderate_data[2])
        self.log.debug("CODERATE :{}ppm  FREQUENCY 1: {}hz   FREQUENCY 2:  {}hz ".format(coderate_ppm, primary_freq, secondary_freq))
        self.generate_primary_frequency(primary_freq)
        self.generate_secondary_frequency(secondary_freq)
        self.generate_coded_carrier(coderate_ppm)

    def generate_primary_frequency(self, frequency, source_frequency=None,chip_select_pin=None, coded_carrier_pin=None, shape=None):
        """
        generates primary carrier frequency.  if frequency is greater than 1, then turn on the pin to the mux
        so that this is the only frequency passed through.  if both frequencies are present then the coded
        carrier will take over
        :param frequency:
        :param source_frequency:
        :param chip_select_pin:
        """
        if source_frequency is None:
            source_frequency = self.primary_source_frequency
        if chip_select_pin is None:
            chip_select_pin = self.primary_channel_chip_select_pin
        if coded_carrier_pin is None:
            coded_carrier_pin = self.coded_carrier_pin
        if shape is None:
            shape = self.shape_default
        if frequency is not 0:
            self.frequency_to_registers(frequency, source_frequency, shape, chip_select_pin)
            self.gpio.write(coded_carrier_pin, self.primary_channel_mux_pin)

    def generate_secondary_frequency(self, frequency=None, source_frequency=None,chip_select_pin=None, coded_carrier_pin=None, shape=None):
        """
        generates primary carrier frequency.  if frequency is greater than 1, then turn on the pin to the mux
        so that this is the only frequency passed through.  if both frequencies are present then the coded
        carrier will take over
        :param frequency:
        :param source_frequency:
        :param chip_select_pin:
        """
        if source_frequency is None:
            source_frequency = self.primary_source_frequency
        if chip_select_pin is None:
            chip_select_pin = self.primary_channel_chip_select_pin
        if coded_carrier_pin is None:
            coded_carrier_pin = self.coded_carrier_pin
        if shape is None:
            shape = self.shape_default
        if frequency is not 0:
            self.frequency_to_registers(frequency, source_frequency, shape, chip_select_pin)
            self.gpio.write(coded_carrier_pin, self.secondary_channel_mux_pin)

    def generate_coded_carrier(self, coderate_ppm, duty_cycle=None, pulses_per_second=None):
        if duty_cycle is None:
            duty_cycle = self.duty_cycle_default
        if pulses_per_second is None:
            pulses_per_second = self.pulses_per_second_default
        self.gpio.wave_clear()
        pulse = []
        if coderate_ppm is not 0:
            coderate_period_in_microseconds = int((1 / (coderate_ppm / 60.0)) * pulses_per_second)
            coderate_positive_pulse = int(coderate_period_in_microseconds * (duty_cycle / 100))
            coderate_negative_pulse = int(coderate_period_in_microseconds * (1 - (duty_cycle / 100)))
            pulse.append(pigpio.pulse(1 << self.coded_carrier_pin, 0, coderate_positive_pulse))
            pulse.append(pigpio.pulse(0, 1 << self.coded_carrier_pin, coderate_negative_pulse))
            self.gpio.wave_add_generic(pulse)  # add waveform
            self.waveform1 = self.gpio.wave_create()
            self.gpio.wave_send_repeat(self.waveform1)
            self.log.debug('Starting code rate')
            val = threading.current_thread(), threading.current_thread().name
            self.log.debug("THREAD " + str(val))
        elif coderate_ppm is 0:
            self.coderate_stop()

    def coderate_stop(self):
        if self.gpio.wave_tx_busy():
            self.gpio.wave_tx_stop()
            self.gpio.wave_clear()

    def frequency_to_registers(self, frequency, clock_frequency, shape, cs):
        spi_channel = 2
        self.spi_msg = []
        self.log.debug(
            "FREQ TO REG running with FREQ:{} CLK FREQ:{} SHAPE:{}  CS:{}  SPI CH  {}".format(frequency, clock_frequency, shape,
                                                                                  cs, spi_channel))
        word = hex(int(round((frequency * 2 ** 28) / clock_frequency)))  # Calculate frequency word to send
        if self.speed_generation_shape_override is not None:
            shape = self.speed_generation_shape_override
        if shape == self.shape_square:  # square
            shape_word = 0x2020
        elif shape == self.shape_triangle:  # triangle
            shape_word = 0x2002
        else:
            shape_word = 0x2000  # sine
        MSB = (int(word, 16) & 0xFFFC000) >> 14  # Split frequency word onto its separate bytes
        LSB = int(word, 16) & 0x3FFF
        MSB |= 0x4000  # Set control bits DB15 = 0 and DB14 = 1; for frequency register 0
        LSB |= 0x4000
        self._ad9833_append(0x2100)
        # Set the frequency
        self._ad9833_append(LSB)  # lower 14 bits
        self._ad9833_append(MSB)  # Upper 14 bits
        self._ad9833_append(shape_word)
        return (spi_channel, self.spi_msg, cs)

    def _ad9833_append(self, integer):
        high, low = divmod(integer, 0x100)
        self.spi_msg.append(high)
        self.spi_msg.append(low)

    def code_rate_toggle(self):
        self.coded_carrier_pin_state = not self.coded_carrier_pin_state
        self.gpio.write(self.coded_carrier_pin, self.coded_carrier_pin_state)

    def pulse_codes_from_company(self, company):
        self.log.debug("Reading pulsecode data from INI file for company  {}".format(company))
        good_list = []
        values = []
        company_data = self.config_coderates.items(company)
        company_pulsecodes = filter(lambda x: x[0].startswith('pulsecode'), company_data)
        data = list(company_pulsecodes)
        for k in data:
            # print(k[0])
            # print(k[1])
            coderate_list = k[1].split(",")
            # print("Coderate list {}".format(coderate_list))
            for x in coderate_list:
                # print('x={}'.format(x))
                for y in self.coderates:
                    # print('y={}'.format(y))
                    if x == y[0]:
                        good_list.append(y[1])
                for y in self.carrier_freq:
                    # print('y={}'.format(y))
                    if x == y[0]:
                        good_list.append(y[1])
            values.append(good_list)
            good_list = []
        # print(values)
        # print(values[0])
        # print(values[1])
        # print(values[2])
        return values

    def generate_test_pulse(self, values):
        # This is used to generate the pulses from RPI pins.  This is not implemented currently.  We are using a
        # freq generator for each carrier and then switching between them to generate the coderate.
        # TODO  when we talk about shifting the duty cycle, are we shifting the duty cycle for each carriers freqeuency
        # TODO or are we shiting the carrier for the code rate, meaning less or more of each carrier?

        # we are passed a coderate (in pulses per miunute) and a frequency for one or two of the carrier frequencies.
        # the pulse train is generated by taking the coderate frequency (in hertz) and then switching on an euen portion
        # of each carrier.  if a carrier is missing, it will be turned off for that portion.
        # if we are sent a 180 coderate with a 100hz primary freq and a 250hz secondary freq, the pulse waveform would
        # look like this:  180 coderate = 180 pulses per minute or 3 pulses per second (3hz). each period is 333ms.
        # that means each positive wave is 1/2 of that at 50 % duty cycle, or 166.66 ms.
        # next we have to generate so many pulses of each waveform for the amount of the pos and neg time so since
        # the pos period is 166.66ms we take the primary freq period (100hz at 1/100 = 0.010 or 10 ms. so dividing the
        # pos period of 166.66 / 10ms we get 16.66 waveforms we need to make.  each positive will be 1/2 that for 50%
        # duty cycle, or 8.33ms for each positive and 8.33ms for each negative.
        duty_cycle = 50
        pulses_per_second = 1000000.0
        primary_code_rate_generator_toggle_pin = 27
        secondary_code_rate_generator_toggle_pin = 22

        self.log.debug("Generating Test Pulse")
        self.gpio.wave_clear()
        coderate1_ppm = values[0]
        carrier_freq1 = values[1]
        coderate2_ppm = values[2]
        carrier_freq2 = values[3]

        self.gpio.set_mode(primary_code_rate_generator_toggle_pin, pigpio.OUTPUT)
        self.gpio.set_mode(secondary_code_rate_generator_toggle_pin, pigpio.OUTPUT)
        self.gpio.wave_tx_stop()

        self.log.debug(
            "Received values to generate waveform: CODERATE 1:{}ppm  FREQUENCY 1: {}hz   CODERATE 2: {}ppm  FREQUENCY 2:  {}hz ".format(
                coderate1_ppm, carrier_freq1, coderate2_ppm, carrier_freq2))
        coderate1_period_in_microseconds = int((1 / (coderate1_ppm / 60.0)) * pulses_per_second)
        coderate2_period_in_microseconds = int((1 / (coderate2_ppm / 60.0)) * pulses_per_second)
        self.log.debug("Calculated CODERATE 1 PERIOD: {}usecs   CODERATE 2 PERIOD:  {}usecs".format(
            coderate1_period_in_microseconds, coderate2_period_in_microseconds))
        coderate1_positive_pulse = int(coderate1_period_in_microseconds * (duty_cycle / 100))
        coderate1_negative_pulse = int(coderate1_period_in_microseconds * (1 - (duty_cycle / 100)))
        coderate2_positive_pulse = int(coderate1_period_in_microseconds * (duty_cycle / 100))
        coderate2_negative_pulse = int(coderate1_period_in_microseconds * (1 - (duty_cycle / 100)))
        self.log.debug(
            'CODERATE 1 POS PULSE:{}Usecs   CODERATE 1 NEG PULSE:{}uSecs   CODERATE 2 POS PULSE:{}Usecs   CODERATE 2 NEG PULSE"{}Usecs'.format(
                coderate1_positive_pulse, coderate1_negative_pulse, coderate2_positive_pulse, coderate2_negative_pulse))
        # generate primary carrier frequency
        # assuming 50% duty cycle
        primary_carrier_positive_pulse_microseconds = int(((1 / carrier_freq1) / 2) * pulses_per_second)
        primary_carrier_negative_pulse_microseconds = int(((1 / carrier_freq1) / 2) * pulses_per_second)
        secondary_carrier_positive_pulse_microseconds = int(((1 / carrier_freq2) / 2) * pulses_per_second)
        secondary_carrier_negative_pulse_microseconds = int(((1 / carrier_freq2) / 2) * pulses_per_second)
        self.log.debug(
            "PRI CARRIER POS PULSE {}uSec PRI CARRIER NEG PULSE {}uSec   SEC CARRIER POS PULSE {}uSec SEC CARRIER NEG PULSE {}uSec".format(
                primary_carrier_positive_pulse_microseconds, primary_carrier_negative_pulse_microseconds,
                secondary_carrier_positive_pulse_microseconds, secondary_carrier_negative_pulse_microseconds))

        pulse = []
        wavelength = coderate1_positive_pulse
        while wavelength is not 0:
            # prim car pos
            if wavelength > primary_carrier_positive_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(1 << primary_code_rate_generator_toggle_pin, 0,
                                 primary_carrier_positive_pulse_microseconds))
                wavelength = wavelength - primary_carrier_positive_pulse_microseconds
                self.log.debug('ADDING  PRI CAR POS PULSE WITH LENGTH OF  {}USECS'.format(
                    primary_carrier_positive_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(1 << primary_code_rate_generator_toggle_pin, 0, wavelength))
                self.log.debug('ADDING  PRI CAR POS PULSE WITH LENGTH OF  {}USECS'.format(wavelength))
                wavelength = wavelength - wavelength

            # pri car neg
            if wavelength > primary_carrier_negative_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(0, 1 << primary_code_rate_generator_toggle_pin,
                                 primary_carrier_negative_pulse_microseconds))
                wavelength = wavelength - primary_carrier_negative_pulse_microseconds
                self.log.debug('ADDING  PRI CAR NEG PULSE WITH LENGTH OF  {}USECS'.format(
                    primary_carrier_negative_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(0, 1 << primary_code_rate_generator_toggle_pin, wavelength))
                self.log.debug('ADDING  PRI CAR NEG PULSE WITH LENGTH OF  {}USECS'.format(wavelength))
                wavelength = wavelength - wavelength
            self.log.debug('Wavelength {}'.format(wavelength))

        wavelength = coderate2_positive_pulse
        while wavelength is not 0:
            # sec car pos
            if wavelength > secondary_carrier_positive_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(1 << secondary_code_rate_generator_toggle_pin, 0,
                                 secondary_carrier_positive_pulse_microseconds))
                wavelength = wavelength - secondary_carrier_positive_pulse_microseconds
                self.log.debug('ADDING  SEC CAR POS PULSE WITH LENGTH OF  {}Usecs'.format(
                    secondary_carrier_positive_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(1 << secondary_code_rate_generator_toggle_pin, 0, wavelength))
                self.log.debug('ADDING  SEC CAR POS PULSE WITH LENGTH OF  {}Usecs'.format(wavelength))
                wavelength = wavelength - wavelength

            # sec car neg
            if wavelength > secondary_carrier_negative_pulse_microseconds:
                pulse.append(
                    pigpio.pulse(0, 1 << secondary_code_rate_generator_toggle_pin,
                                 secondary_carrier_negative_pulse_microseconds))
                wavelength = wavelength - secondary_carrier_negative_pulse_microseconds
                self.log.debug('ADDING  SEC CAR NEG PULSE WITH LENGTH OF  {}Usecs'.format(
                    secondary_carrier_negative_pulse_microseconds))
            else:
                pulse.append(pigpio.pulse(0, 1 << secondary_code_rate_generator_toggle_pin, wavelength))
                self.log.debug('ADDING  SEC CAR NEG PULSE WITH LENGTH OF  {}Usecs'.format(
                    wavelength))
                wavelength = wavelength - wavelength
            self.log.debug('Wavelength {}'.format(wavelength))
        self.gpio.wave_add_generic(pulse)  # add waveform
        pulses = self.gpio.wave_get_pulses()
        micros = self.gpio.wave_get_micros()
        self.log.debug("Waveform PULSES {}   MICROS {}".format(pulses, micros))
        wf = self.gpio.GPIO.wave_create()
        self.gpio.gpio.GPIO.wave_send_repeat(wf)

