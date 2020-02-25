from PySide2.QtCore import QThread, Signal

#mylibraries

class Pollvalues(QThread):

    sense_changedValue = Signal(float)  # signal to send to awaiting slot
    switch_changedValue = Signal(int)  # signal to send to awaiting slot


    def __init__(self, pollperm, logger, config, switches, currentsense):
        super().__init__()
        self.pollperm = pollperm
        self.logger = logger
        self.config = config
        self.log = self.logger.log
        self.switches = switches
        self.currentsense = currentsense
        self.log.debug('Polling class initializing...')
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    # ********************************************************************************
    def startup_processes(self):
        self.sense_changedValue.connect(self.currentsense.sense_poll_callback)
        self.switch_changedValue.connect(self.switches.switch_poll_callback)

    # ********************************************************************************
    # runs both sense and switches polling
    def poll_read_values(self):
        if self.pollperm.polling_prohibited[0] is False:
            raw_analog_digital_value = self.sense_read_value()
            switch_value = self.switch_read_values()
            self.sense_changedValue.emit(raw_analog_digital_value)
            self.switch_changedValue.emit(switch_value)
        else:
            self.log.info("Sense Polling canceled due to polling prohibited... ")

    # ********************************************************************************
    # retrieves value from current sense A/D converter via spi (U25)
    def sense_read_value(self):
        # TODO get values from INI file
        self.log.debug('Running Sense Polling')
        data = self.currentsense.read_spi_value_register()
        raw_analog_digital_value = data[0] * 256 + data[1]
        self.log.debug("Data received {0:X}h {1:X}h".format(data[0], data[1]))
        self.log.debug("ADC Value:{}".format( raw_analog_digital_value))
        return raw_analog_digital_value

    # *********************************************************************************
    # retrieves value from switch mutiplexer via spi  (U20)
    def switch_read_values(self):
        self.log.debug('Running Switch Polling')
        returned_data = self.switches.spi_value_register()
        self.log.debug("Switch value:{}".format(returned_data))
        return returned_data



