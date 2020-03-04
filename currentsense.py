from logger import Logger


# **********************************************************************************************
class CurrentSense(object):
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, spi, decoder, logger, gui, config):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.spi = spi
        self.decoder = decoder
        self.logger = logger
        self.gui = gui
        self.config = config
        self.window = self.gui.window
        #self.sense_callback = sense_callback
        self.log = self.logger.log
        self.log.debug('Current Sense initializing...')
        self.display_amps_template = None
        self.loop_current_template = None
        self.adc_counts_template = None
        self.adc_template = None

        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    # **********************************************************************************************
    def startup_processes(self):
        self.read_from_config()
        self.device_present_check()

    # **********************************************************************************************
    def device_present_check(self):
        """the MCP23S08 register 1-1 (addr 0x00) will be 0xFF at starup.
        read this switches_value to ensure the device is present.
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
    def read_spi_register(self, register):
       return_data = self.spi.read_message(channel=0, chip_select=self.decoder.chip_select_current_sense,
                                           data=[0xFF, 0xFF])
       return return_data

    # **********************************************************************************************
    def read_spi_value_register(self):
        """#need to send 2 bytes of dummy data to clock in 
        the data returned
        :return: 
        :return: 
        """
        return_data = self.spi.read_message(channel=0, chip_select=self.decoder.chip_select_current_sense, data=[0xFF, 0xFF])
        return return_data

    # **********************************************************************************************
    def read_from_config(self):
        pass