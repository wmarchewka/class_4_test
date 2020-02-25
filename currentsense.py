from logger import Logger


# **********************************************************************************************
class CurrentSense(object):
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, spi, decoder, logger, gui, config, sense_callback):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.spi = spi
        self.decoder = decoder
        self.logger = logger
        self.gui = gui
        self.config = config
        self.window = self.gui.window
        self.sense_callback = sense_callback
        self.log = self.logger.log
        self.log.debug('Current Sense initializing...')
        self.display_amps_template = None
        self.loop_current_template = None
        self.adc_counts_template = None
        self.adc_template = None
        self.adc_scale = None
        self.sense_amp_max_amps = None
        self.sense_ad_vin = None  # LM4128CQ1MF3.3/NOPB voltage reference
        self.sense_ad_max_bits = 0  # AD7940 ADC
        self.sense_scaling_factor_mv_amp = None # 110 milivolts per amp
        self.sense_ad_max_scaled_value = 2 ** self.sense_ad_max_bits
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    # **********************************************************************************************
    def startup_processes(self):
        self.read_from_config()
        self.device_present_check()

    # **********************************************************************************************
    def device_present_check(self):
        """the MCP23S08 register 1-1 (addr 0x00) will be 0xFF at starup.
        read this value to ensure the device is present.
        :rtype: object
        """
        self.log.debug("Performing Switches device present check...")
        ret = self.read_spi_register(0x00)
        if ret is not 0xFF:
            self.log.critical("SPI IO EXPANDER:DEVICE NOT PRESENT")
            return 0
        elif ret is 0xFF:
            self.log.critical("SPI IO EXPANDER:DEVICE PRESENT")
            return 1

    # **********************************************************************************************
    def sense_poll_callback(self, raw_analog_digital_value):
        self.log.debug('GUI received sense values...')
        analog_digital_volts, scaled_value = self.adc_process_values(raw_analog_digital_value)
        self.log.debug(
            "RAW A/D:{}  Volts:{}  Scaled:{}".format(raw_analog_digital_value, analog_digital_volts, scaled_value))
        display_amps = (self.adc_scale * analog_digital_volts)
        display_amps = display_amps / 1000
        self.window.LBL_display_amps.setText(self.display_amps_template.format(display_amps))
        self.window.LBL_loop_current.setText(self.loop_current_template.format(display_amps))
        self.window.LBL_display_adc_counts.setText(self.adc_counts_template.format(raw_analog_digital_value))
        self.window.LBL_display_adc.setText(self.adc_template.format(analog_digital_volts))
        self.sense_callback(raw_analog_digital_value, display_amps, raw_analog_digital_value)

    # **********************************************************************************************
    def read_spi_register(self, register):
       return_data = self.spi.read_message(channel=0, chip_select=self.decoder.chip_select_current_sense,
                                           data=[0xFF, 0xFF])
       return return_data

    # **********************************************************************************************
    def read_spi_value_register(self) -> list:
        """#need to send 2 bytes of dummy data to clock in 
        the data returned
        :return: 
        :return: 
        """
        return_data = self.spi.read_message(channel=0, chip_select=self.decoder.chip_select_current_sense, data=[0xFF, 0xFF])
        return return_data

    # **********************************************************************************************
    def adc_process_values(self, raw_analog_digital_value):

        analog_digital_volts = self.sense_ad_vin * (raw_analog_digital_value / self.sense_ad_max_scaled_value)
        scaled_value = ((analog_digital_volts - (self.sense_ad_vin / 2)) / self.sense_scaling_factor_mv_amp)
        self.log.debug(
            "Analog_Digital converter value: {} Scaled Value({})".format(analog_digital_volts, scaled_value))
        return analog_digital_volts, scaled_value

    # **********************************************************************************************
    def read_from_config(self):
        self.display_amps_template = self.config.display_amps_template
        self.loop_current_template = self.config.loop_current_template
        self.adc_counts_template = self.config.adc_counts_template
        self.adc_template = self.config.adc_template
        self.adc_scale = self.config.adc_scale
        self.sense_amp_max_amps = self.config.sense_amp_max_amps
        self.sense_ad_vin = self.config.sense_ad_vin
        self.sense_ad_max_bits = self.config.sense_ad_max_bits
        self.sense_scaling_factor_mv_amp = self.config.sense_scaling_factor_mv_amp