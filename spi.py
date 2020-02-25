import threading
import collections
import spidev
import time

# my libraries
from logger import Logger
from config import Config
from decoder import Decoder
from pollperm import Pollperm


# TODO need to make this so that i can instantiate a sperate clas for each channel ?

class SPI():
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, config, logger, decoder, pollperm):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.logger = logger
        self.config = config
        self.decoder = decoder
        self.log = Logger.log
        self.polling = pollperm
        self.log.debug('SPI initializing...')
        self.spi_log_count = 0
        self.last_time = 0
        self.log_data = True
        self.startup_processes()
        self.log.debug('Using SPI BUS: {}'.format(self.spi_bus))
        self.log.debug("{} init complete...".format(__name__))

    # ************************************************************************************************************
    def startup_processes(self):
        self.load_from_config()
        self.create_channels()
        self.setup_datalog()

    # ************************************************************************************************************
    def setup_datalog(self):
        self.data_log = collections.deque(maxlen=500)

    # ************************************************************************************************************
    def create_channels(self):
        # SPI1_0 uses SPI1 and CE0 (BCM18)
        self.spi1_0 = spidev.SpiDev()
        self.spi1_0.open(self.spi_bus, self.spi_chip_select[0])
        self.spi1_0.max_speed_hz = self.config.spi1_0_max_speed_hz
        self.spi1_0.mode = self.config.spi1_0_mode
        self.log.debug('SPI1_0 using CE0 as CS: Pin 18')

        # SPI1_2 uses SPI1 and CE2 (BCM16)
        self.spi1_2 = spidev.SpiDev()
        self.spi1_2.open(self.spi_bus, self.spi_chip_select[2])
        self.spi1_2.max_speed_hz = self.config.spi1_2_max_speed_hz
        self.spi1_2.mode = self.config.spi1_2_mode
        self.log.debug('SPI1_2 using CE2 as CS: Pin 16')

    # ************************************************************************************************************
    def send_message(self, channel, message, chip_select):
        self.log.debug("SPI Write received Channel:{}  MSG:{}  CHIP SELECT:{}".format(channel, message, chip_select))
        self.polling.polling_prohitied = (True, __name__)
        chip_select_name = self.decoder.chip_select_names[chip_select]
        try:
            self.decoder.chip_select(chip_select_pin=chip_select)
            if channel == 0:
                self.spi1_0.xfer2(message)
            elif channel == 2:
                self.spi1_2.xfer2(message)
        except Exception:
            self.log.exception("Exception in SPI write", exc_info=True)
        self.polling.polling_prohitied = (False, "SPI WRITE")

    # ************************************************************************************************************
    def write_debug_log(self, channel, msg, chip_select_name):
        hex_data = []
        val = threading.currentThread(), threading.current_thread().name
        thread_value = str(val)
        self.log.debug("SPI write thread: {}".format(thread_value))
        for item in msg:
            hex_data.append(format(item, '02x'))
        bin_data = []
        for item in msg:
            bin_data.append(format(item, '08b'))
        str_data = [channel, chip_select_name, msg, hex_data, bin_data]
        self.log.debug(
            "Writing SPI to Channel: {} | Chip Select: {} | DEC data: {} ".format(channel, chip_select_name, msg))
        self.log.debug("Writing SPI to Channel: {}| HEX data: {}".format(channel, hex_data))
        self.log.debug("Writing SPI to Channel: {}| BIN data: {}".format(channel, bin_data))
        self.data_logger(str_data)

    # ************************************************************************************************************
    def read_message(self, channel, chip_select, data=None):
        val = threading.currentThread(), threading.current_thread().name
        thread_value = str(val)
        self.log.debug("SPI read thread: {}".format(thread_value))
        # todo fix to allow no data to be sent, as if you were only doing a read instead of a transfer
        return_val = None
        self.polling.polling_prohitied = (True, "SPI READ")
        hex_data = []
        bin_data = []
        chip_select_name = self.decoder.chip_select_names[chip_select]
        if data is not None:
            for item in data:
                hex_data.append(format(item, '04x'))
            bin_data = []
            for item in data:
                bin_data.append(format(item, '08b'))
        str_data = [channel, chip_select_name, data, hex_data, bin_data]
        self.log.debug(
            "Reading SPI from Channel: {} | Chip Select: {} |"
            " DEC data: {}| HEX data: {}| BIN data: {}".format(
                channel,
                chip_select_name,
                data,
                hex_data,
                bin_data))
        self.data_logger(str_data)
        try:
            self.decoder.chip_select(chip_select_pin=chip_select)
            if channel == 0:
                return_val = self.spi1_0.xfer(data)
            elif channel == 2:
                return_val = self.spi1_2.xfer(data)
            hex_data = []
            for item in return_val:
                hex_data.append(format(item, '04x'))
            bin_data = []
            for item in return_val:
                bin_data.append(format(item, '08b'))
            self.log.debug(
                "Return SPI DEC data: {}| HEX data: {}| BIN data: {}".format(
                    data,
                    hex_data,
                    bin_data))
        except:
            self.log.exception("Exception in SPI write", exc_info=True)
        self.polling.polling_prohitied = (False, "SPI READ")
        return return_val

    # ************************************************************************************************************
    def data_logger(self, msg):
        if self.log_data:
            # TODO: NEED TO FIX THIS TO MAKE SURE IT ONLY LOGS SO MUCH DATA
            self.spi_log_count = self.spi_log_count + 1
            obj_data = ""
            time_data = (time.time() - self.last_time) * 1000
            self.last_time = time.time()
            for obj in msg:
                obj_data = obj_data + str(obj) + "\t"
            obj_data = str(self.spi_log_count) + "\t" + "{:4.3f} \t {:4.3f}".format(time.time(),
                                                                                    time_data) + "\t" + obj_data + "\n"
            data = str(obj_data) + "\n"
            # self.mainwindow.window.TE_spi_log.insertPlainText(str(data))
            # self.scrollbar = self.mainwindow.window.TE_spi_log.verticalScrollBar()
            # self.scrollbar.setValue(self.mainwindow.window.TE_spi_log.blockCount() - 25)

    # ************************************************************************************************************
    def load_from_config(self):
        self.spi_chip_select = self.config.spi_chip_select
        self.spi_bus = self.config.spi_bus
