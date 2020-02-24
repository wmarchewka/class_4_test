import logging

# **********************************************************************************************
class CurrentSense(object):
    def __init__(self, spi,decoder,logger, gui):
        self.adc_scale = 10.83
        self.spi = spi
        self.decoder = decoder
        self.logger = logger
        self.gui = gui
        self.window = self.gui.window
        self.log = self.logger.log
        self.log.debug('Current Sense initializing...')
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    # **********************************************************************************************
    def startup_processes(self):
        pass
    # **********************************************************************************************
    def poll_callback_change_value(self, raw_analog_digital_value):
        self.log.debug('GUI received sense values...')
        analog_digital_volts, scaled_value = self.adc_process_values(raw_analog_digital_value)
        self.log.debug("RAW A/D:{}  Volts:{}  Scaled:{}".format(raw_analog_digital_value, analog_digital_volts, scaled_value))
        self.display_amps = (self.adc_scale * analog_digital_volts)
        self.display_amps = self.display_amps / 1000
        self.display_amps = self.display_amps / 1000
        self.window.LBL_display_amps.setText("{:2.3f}".format(self.display_amps))
        self.window.LBL_loop_current_1.setText("{:2.3f}".format(self.display_amps))
        self.window.LBL_display_adc_counts.setText("{:5.0f}".format(raw_analog_digital_value))

    # **********************************************************************************************
    def read_spi(self) -> list:
        """#need to send 2 bytes of dummy data to clock in 
        the data returned
        :return: 
        :return: 
        """
        return_data = self.spi.read_message(0, 2, self.decoder.chip_select_current_sense, [0xFF, 0xFF])
        return return_data

    # **********************************************************************************************
    def adc_process_values(self, raw_analog_digital_value):
        self.sense_amp_max_amps = 25
        self.sense_ad_vin = 3.299  # LM4128CQ1MF3.3/NOPB voltage reference
        self.sense_ad_max_bits = 14  # AD7940 ADC
        self.sense_ad_max_scaled_value = 2 ** self.sense_ad_max_bits
        self.sense_scaling_factor_mv_amp = 0.110  # 55 milivolts per amp
        analog_digital_volts = self.sense_ad_vin * (raw_analog_digital_value / self.sense_ad_max_scaled_value)
        scaled_value = ((analog_digital_volts - (self.sense_ad_vin / 2)) / self.sense_scaling_factor_mv_amp)
        self.log.debug(
            "Analog_Digital converter value: {} Scaled Value({})".format(analog_digital_volts, scaled_value))
        # self.sense_changedValue.emit(raw_analog_digital_value, analog_digital_volts, scaled_value)
        #val = QtCore.QThread.currentThreadId(), threading.current_thread().name
        #self.log.debug("THREAD " + str(val))
        return analog_digital_volts, scaled_value

    # **********************************************************************************************
    def read_from_config(self):
        # TODO these need to come from ini file
        self.sense_scaling_factor_mv_amp = 0.055  # 55 milivolts per amp
        self.sense_amp_max_amps = 25
        self.sense_ad_vin = 3.299  # LM4128CQ1MF3.3/NOPB voltage reference
        self.sense_ad_max_bits = 14  # AD7940 ADC
        self.sense_ad_max_scaled_value = 2 ** self.sense_ad_max_bits