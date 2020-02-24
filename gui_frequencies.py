from logger import Logger
from config import Config
from codegen import Codegen


class GuiFrequencies(object):
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, window, codegen, config, logger):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.config = config
        self.logger = logger
        self.codegen = codegen
        self.window = window
        self.log = Logger.log
        self.pb_frequencies_state = []
        self.max_frequencies_pb = 12
        self.pri_freq_pb = None
        self.sec_freq_pb = None
        self.pri_freq_value = None
        self.sec_freq_value = None
        self.startup_processes()

 # *******************************************************************************************
    def startup_processes(self):
        self.generate_frequency_pushbuttons()

    # *******************************************************************************************
    def generate_frequency_pushbuttons(self):

        """
        Turns on pre-created buttons on the screen for frequencies.  The list of buttons to be
        activated come from the coderate generator class.  button presses are caught by the
        frequency_pushbutton_change routine.
        """
        counter = 0
        self.log.debug("FREQUENCIES:{}".format(self.codegen.frequencies))
        for frequency in self.codegen.frequencies:
            button = getattr(self.window, 'PB_freq_%s' % counter)
            button.released.connect(lambda idx=counter: self.frequency_pushbutton_change(idx))
            button.setStyleSheet('background-color: red;border-radius:10px')
            button.setText(str(frequency))
            button.setVisible(True)
            self.pb_frequencies_state.append(0)
            counter = counter + 1
        for t in range(counter, self.max_frequencies_pb):
            button = getattr(self.window, 'PB_freq_%s' % t)
            button.setVisible(False)
        self.window.LBL_current_pri_carrier.setText("OFF")
        self.window.LBL_current_sec_carrier.setText("OFF")


    #  ***************************************************************************************
    def frequency_pushbutton_change(self, buttonid):
        button = getattr(self.window, 'PB_freq_%s' % buttonid)
        self.log.debug("FREQ PB changed BUTTON:{}".format(buttonid))
        if self.pb_frequencies_state[buttonid] == 1:
            self.pb_frequencies_state[buttonid] = 0
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "FALSE"))
            # button.setStyleSheet('background-color: red;border-radius:10px')
        elif self.pb_frequencies_state[buttonid] == 0:
            self.pb_frequencies_state[buttonid] = 1
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "TRUE"))
            # button.setStyleSheet('background-color: green;border-radius:10px')
        if self.pri_freq_pb is None and self.sec_freq_pb is None:
            button.setStyleSheet('background-color: green;border-radius:10px')
            self.pri_freq_pb = buttonid
            self.window.LBL_current_pri_carrier.setText(str(self.codegen.frequencies[buttonid]))
            self.pri_freq_value = self.codegen.frequencies[buttonid]
            self.log.debug("PRIMARY FEQ button set")
        elif self.pri_freq_pb is None and self.sec_freq_pb is not None:
            if buttonid is self.sec_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.sec_freq_pb = None
                self.window.LBL_current_sec_carrier.setText("OFF")
                self.sec_freq_value = 0
                self.log.debug("SECONDARY FEQ button unset")
            elif buttonid is not self.sec_freq_pb:
                button.setStyleSheet('background-color: green;border-radius:10px')
                self.pri_freq_pb = buttonid
                self.window.LBL_current_pri_carrier.setText(str(self.codegen.frequencies[buttonid]))
                self.pri_freq_value = self.codegen.frequencies[buttonid]
                self.log.debug("PRIMARY FREQ button set")
        elif self.pri_freq_pb is not None and self.sec_freq_pb is None:
            if buttonid is self.pri_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.pri_freq_pb = None
                self.window.LBL_current_pri_carrier.setText("OFF")
                self.pri_freq_value = 0
                self.log.debug("PRIMARY FREQ button unset")
            elif buttonid is not self.pri_freq_pb:
                button.setStyleSheet('background-color: yellow;border-radius:10px')
                self.sec_freq_pb = buttonid
                self.window.LBL_current_sec_carrier.setText(str(self.codegen.frequencies[buttonid]))
                self.sec_freq_value = self.codegen.frequencies[buttonid]
                self.log.debug("SECONDARY FREQ button Set")
        elif self.pri_freq_pb is not None and self.sec_freq_pb is not None:
            if buttonid is self.pri_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.pri_freq_pb = None
                self.window.LBL_current_pri_carrier.setText("OFF")
                self.pri_freq_value = 0
                self.log.debug("PRIMARY FREQ button unset")
            elif buttonid is self.sec_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.sec_freq_pb = None
                self.window.LBL_current_sec_carrier.setText("OFF")
                self.sec_freq_value = 0
                self.log.debug("SECONDARY FREQ button unset")
        elif self.sec_freq_pb is None and self.pri_freq_pb is None:
            self.log.debug("Sec freq is none: Pri freq is none")
        elif self.sec_freq_pb is None and self.pri_freq_pb is not None:
            self.log.debug("Sec freq is none: Pri freq is NOT none")
        elif self.sec_freq_pb is not None and self.pri_freq_pb is None:
            if buttonid is self.sec_freq_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.sec_freq_pb = None
                self.window.LBL_current_sec_carrier.setText("OFF")
                self.sec_freq_value = 0
                self.log.debug("SECONDARY FREQ button unset")
        elif self.sec_freq_pb is not None and self.pri_freq_pb is not None:
            self.log.debug("Sec freq is NOT none: Pri freq is NOT none")
        self.codegen.primary_frequency_generate(self.pri_freq_value)
        self.codegen.secondary_frequency_generate(self.sec_freq_value)
        self.codegen.coderate_generate()

    # *******************************************************************************************
    def load_from_config(self):
        pass
