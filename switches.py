from logger import Logger


class Switches(object):
    Logger.log.debug("Instantiating {} class...".format(__qualname__))

    def __init__(self, config, logger, spi, gui, switch_callback):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.logger = logger
        self.config = config
        self.spi = spi
        self.gui = gui
        self.window = gui.window
        self.log = logger.log
        self.switch_callback = switch_callback
        self.log.debug("Switches initializing...")
        self.switch_address = 0
        self.switch_address = self.switch_address << 1
        self.switch_spi_read = 0b00000001
        self.switch_spi_write = 0b00000000
        self.switch_op_code = 0b01000000
        self.switch_channel = 0
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    # cs9  address:0 0x00
    # reg 1-1    addr:00  leave as configured   Change this to 0b00001111 to set pin 0,1,2,3 as input and 4,5,6,7 as output
    # reg 1-2    addr:01  leave as set
    # reg 1-3    addr:02  not used
    # reg 1-4    addr:03  not used
    # reg 1-5    addr:04  not used
    # reg 1-6    addr:05  set bit 5 to 1 to disable seq operation, bit 3 to 1 enable address pins
    # reg 1-7    addr:06  leave as configured
    # reg 1-8    addr:07  not used
    # reg 1-9    addr:08  not used
    # reg 1-10   addr:09  reflects state of port, read this
    # reg 1-11   addr:0A  output latch, write to this to set pin values
    # **************************************************************************
    def startup_processes(self):
        self.read_from_config()
        self.device_present_check()

    # **************************************************************************
    def device_present_check(self):
        """the MCP23S08 register 1-1 (addr 0x00) will be 0xFF at starup.
        read this value to ensure the device is present.
        :rtype: object
        """
        self.log.debug("Performing Switches device present check...")
        ret=self.spi_read_values(0x00)
        if ret is not 0xFF:
            self.log.critical("SPI IO EXPANDER:DEVICE NOT PRESENT")
            return 0
        elif ret is 0xFF:
            self.log.critical("SPI IO EXPANDER:DEVICE PRESENT")
            return 1
    # **************************************************************************
    def register_setup_address_5(self):
        # disable sequential operation bit 5 on
        # hardware address enable bit 3 on
        switch_register_address = 0x05
        switch_sent_op_code = self.switch_op_code | self.switch_address | self.switch_spi_write
        switch_register_write_value = 0b00101000
        spi_msg = [switch_sent_op_code] + [switch_register_address] + [switch_register_write_value]
        ret = self.spi.write(self.switch_channel, spi_msg, self.config.switch_chip_select)
        self.log.debug("Returned value from SWITCH disable SEQUENTIAL READ {}".format(ret))

    # **************************************************************************
    # TODO make sure this is tested
    def spi_write_values(self, pinvalue):
        """
        the switch io expander ic has 8 pins configurable as input or output, the first
        4 (pins 0-3) are set as input and wired to the 4 rotary encoders push buttons.
        the last 4 (4-7) are set as outputs
        :param pinvalue:
        """
        # read switch register
        if pinvalue >= 0 and pinvalue <= 7:
            self.log.debug("Writing spi switch for values")
            switch_register_address = 0x0A
            number_of_bytes = 2
            switch_sent_op_code = self.switch_op_code | self.switch_address | self.switch_spi_write
            spi_msg = [switch_sent_op_code] + [switch_register_address] + [pinvalue]
            ret = self.spi.send_message(channel=self.switch_channel, chip_select=self.config.switch_chip_select,
                                        message=spi_msg)
        else:
            self.log.debug("SPI WRITE PINVALUE OUT OF RANGE")
            return 0

    # **************************************************************************
    def spi_value_register(self):
        self.spi_read_values(0x09)

    # **************************************************************************
    def spi_read_values(self, register_address):
        # read switch register
        self.log.debug("Polling spi switch for values")
        #switch_register_address = 0x09
        number_of_bytes = 2
        switch_sent_op_code = self.switch_op_code | self.switch_address | self.switch_spi_read
        spi_msg = [switch_sent_op_code] + [register_address] + [0x00]
        ret = self.spi.read_message(self.switch_channel, self.config.switch_chip_select, spi_msg)
        self.log.debug(
            "Returned value from SWITCH spi read{} | BITS {}".format(ret, bin(ret[2])))
        return ret[2]

    # **************************************************************************
    # call back from switch_polling
    def switch_poll_callback(self, value):
        self.knob_values = 0
        self.log.debug("onSwitchChangeValues     :{:08b}".format(value))
        self.log.debug("knob values              :{:08b}".format(value))
        value = (value | self.knob_values)
        self.log.debug("onSwitchChangeValues ORED:{:08b}".format(value))
        if value & 0b00000001:
            self.window.switch3_green.setVisible(True)
            self.window.switch3_red.setVisible(False)
            self.window.QDIAL_speed_1.setStyleSheet('background-color: red')
        else:
            self.window.switch3_green.setVisible(False)
            self.window.switch3_red.setVisible(True)
        if value & 0b00000010:
            self.window.switch4_green.setVisible(True)
            self.window.switch4_red.setVisible(False)
        else:
            self.window.switch4_green.setVisible(False)
            self.window.switch4_red.setVisible(True)
        if value & 0b00000100:
            self.window.switch5_green.setVisible(True)
            self.window.switch5_red.setVisible(False)
        else:
            self.window.switch5_green.setVisible(False)
            self.window.switch5_red.setVisible(True)
        if value & 0b00001000:
            self.window.switch6_green.setVisible(True)
            self.window.switch6_red.setVisible(False)
        else:
            self.window.switch6_green.setVisible(False)
            self.window.switch6_red.setVisible(True)
        self.switch_callback(value)

    # **************************************************************************
    def read_from_config(self):
        pass

        # self.register_setup_address_5()
        # self.speed1_start_time = 0
        # self.speed1_on = False
        # self.speed1_start = False
        # self.speed1_push_type = None
        # self.speed2_start_time = 0
        # self.speed2_on = False
        # self.speed2_start = False
        # self.speed2_push_type = None
        # self.primary_gain_start_time = 0
        # self.primary_gain_on = False
        # self.primary_gain_start = False
        # self.primary_gain_push_type = None
        # self.secondary_gain_start_time = 0
        # self.secondary_gain_on = False
        # self.secondary_gain_start = False
        # self.secondary_gain_push_type = None
        # self.fast_elapsed_min_secs = 0.2
        # self.fast_elapsed_max_secs = 2.0
        # self.slow_elapsed_min_secs = 3.0
        # self.slow_elasped_max_sec = 6.0
        # self.push_and_hold_secs = 3.0
        # self.primary_gain_pb_status_counter = 1
        # self.primary_gain_pb_status = ""
        # self.secondary_gain_pb_status_counter = 1
        # self.secondary_gain_pb_status = ""
        # # todo:need to add push and hold to both speed encoders
        # if self.speed1_on and self.speed1_start is False:
        #     self.speed1_start = True
        #     self.speed1_start_time = time.time()
        #     self.log.info("Speed 1 Start Time:{}".format(self.speed1_start_time))
        # if self.speed1_on is False and self.speed1_start:
        #     self.speed1_start = False
        #     speed1_elapsed = time.time() - self.speed1_start_time
        #     self.log.info("Speed 1 Button elasped time {}".format(speed1_elapsed))
        #     if speed1_elapsed > 0.2 and speed1_elapsed < 1.0:
        #         self.speed1_push_type = "FAST"
        #         self.log.info("SPEED 1 FAST")
        #     if speed1_elapsed > 3.0:
        #         self.speed1_push_type = "SLOW"
        #         self.log.info("SPEED 1 SLOW")
        #
        # if self.speed2_on and self.speed2_start is False:
        #     self.speed2_start = True
        #     self.speed2_start_time = time.time()
        #     self.log.info("Speed 2 Start Time:{}".format(self.speed2_start_time))
        # if self.speed2_on is False and self.speed2_start:
        #     self.speed2_start = False
        #     speed2_elapsed = time.time() - self.speed2_start_time
        #     self.log.info("Speed 2 Button elasped time {}".format(speed2_elapsed))
        #     if speed2_elapsed > 0.2 and speed2_elapsed < 1.0:
        #         self.speed2_push_type = "FAST"
        #         self.log.info("SPEED 2 FAST")
        #     if speed2_elapsed > 3.0:
        #         self.speed2_push_type = "SLOW"
        #         self.log.info("SPEED 2 SLOW")
        #
        # if self.primary_gain_on and self.primary_gain_start is False:
        #     self.primary_gain_start = True
        #     self.primary_gain_start_time = time.time()
        #     self.log.debug("Pri Gain Start Time:{}".format(self.primary_gain_start_time))
        # if self.primary_gain_on is False and self.primary_gain_start:
        #     self.primary_gain_start = False
        #     primary_gain_elapsed = time.time() - self.primary_gain_start_time
        #     self.log.debug("Pri Gain Button elasped time {}".format(primary_gain_elapsed))
        #     if primary_gain_elapsed > self.fast_elapsed_min_secs and primary_gain_elapsed < self.fast_elapsed_max_secs:
        #         self.primary_gain_push_type = "FAST"
        #         self.log.info("Pri Gain FAST")
        #     if primary_gain_elapsed > self.slow_elasped_max_sec:
        #         self.primary_gain_push_type = "SLOW"
        #         self.log.info("Pri Gain SLOW")
        # if self.primary_gain_start and (time.time() - self.primary_gain_start_time) > self.push_and_hold_secs:
        #     self.log.debug("Pri Gain PUSH and HOLD")
        #     self.primary_gain_start = False
        #
        # if self.secondary_gain_on and self.secondary_gain_start is False:
        #     self.secondary_gain_start = True
        #     self.secondary_gain_start_time = time.time()
        #     self.log.debug("Sec Gain Start Time:{}".format(self.secondary_gain_start_time))
        # if self.secondary_gain_on is False and self.secondary_gain_start:
        #     self.secondary_gain_start = False
        #     secondary_gain_elapsed = time.time() - self.secondary_gain_start_time
        #     self.log.debug("Sec Gain Button elasped time {}".format(secondary_gain_elapsed))
        #     if secondary_gain_elapsed > self.fast_elapsed_min_secs and secondary_gain_elapsed < self.fast_elapsed_max_secs:
        #         self.secondary_gain_push_type = "FAST"
        #         self.log.debug("Sec Gain FAST")
        #     if secondary_gain_elapsed > self.slow_elasped_max_sec:
        #         self.secondary_gain_push_type = "SLOW"
        #         self.log.info("Sec Gain SLOW")
        # if self.secondary_gain_start and (time.time() - self.secondary_gain_start_time) > self.push_and_hold_secs:
        #     self.log.info("Pri Gain PUSH and HOLD")
        #     self.secondary_gain_start = False
        #
        # if self.primary_gain_push_type == "FAST":
        #     if self.primary_gain_pb_status_counter == 1:
        #         self.digitalpots.gains_locked = False
        #         self.primary_gain_pb_status = "ON"
        #         self.gpio.GPIO.wave_tx_stop()
        #         self.gpio.GPIO.write(self.coderategenerator.toggle_pin, 0)
        #         self.secondary_gain_pb_status = "OFF"
        #         self.gains.secondary_gain_off()
        #     if self.primary_gain_pb_status_counter == 2:
        #         self.digitalpots.gains_locked = False
        #         self.primary_gain_pb_status = "OFF"
        #         self.gains.primary_gain_off()
        #     if self.primary_gain_pb_status_counter == 3:
        #         self.digitalpots.gains_locked = False
        #         self.primary_gain_pb_status = "CODERATE"
        #         self.secondary_gain_pb_status = "CODERATE"
        #         self.gpio.GPIO.wave_send_repeat(self.coderategenerator.waveform1)
        #         self.gains.primary_gain_set_ohms(self.gains.primary_gain_saved_value)
        #         self.gains.secondary_gain_set_ohms(self.gains.secondary_gain_saved_value)
        #     if self.primary_gain_pb_status_counter == 4:
        #         self.digitalpots.gains_locked = True
        #         self.primary_gain_pb_status = "LOCKED"
        #         self.secondary_gain_pb_status = "LOCKED"
        #     self.log.info("PRIMARY GAIN PB COUNTER:{}  STATUS: {}".format(self.primary_gain_pb_status_counter,
        #                                                                   self.primary_gain_pb_status))
        #     self.primary_gain_push_type = ""
        #     self.primary_gain_pb_status_counter = self.primary_gain_pb_status_counter + 1
        #     if self.primary_gain_pb_status_counter > 4:
        #         self.primary_gain_pb_status_counter = 1
        #
        # if self.secondary_gain_push_type == "FAST":
        #     if self.secondary_gain_pb_status_counter == 1:
        #         self.digitalpots.gains_locked = False
        #         self.secondary_gain_pb_status = "ON"
        #         self.gpio.GPIO.wave_tx_stop()
        #         self.gpio.GPIO.write(self.coderategenerator.toggle_pin, 1)
        #         self.primary_gain_pb_status = "OFF"
        #         self.gains.primary_gain_off()
        #     if self.secondary_gain_pb_status_counter == 2:
        #         self.digitalpots.gains_locked = False
        #         self.secondary_gain_pb_status = "OFF"
        #         self.gains.secondary_gain_off()
        #     if self.secondary_gain_pb_status_counter == 3:
        #         self.digitalpots.gains_locked = False
        #         self.secondary_gain_pb_status = "CODERATE"
        #         self.primary_gain_pb_status = "CODERATE"
        #         self.gpio.GPIO.wave_send_repeat(self.coderategenerator.waveform1)
        #         self.gains.primary_gain_set_ohms(self.gains.primary_gain_saved_value)
        #         self.gains.secondary_gain_set_ohms(self.gains.secondary_gain_saved_value)
        #     if self.secondary_gain_pb_status_counter == 4:
        #         self.digitalpots.gains_locked = True
        #         self.secondary_gain_pb_status = "LOCKED"
        #         self.primary_gain_pb_status = "LOCKED"
        #     self.log.info("SECONDARY GAIN PB COUNTER:{}  STATUS: {}".format(self.secondary_gain_pb_status_counter,
        #                                                                     self.secondary_gain_pb_status))
        #     self.secondary_gain_push_type = ""
        #     self.secondary_gain_pb_status_counter = self.secondary_gain_pb_status_counter + 1
        #     if self.secondary_gain_pb_status_counter > 4:
        #         self.secondary_gain_pb_status_counter = 1
