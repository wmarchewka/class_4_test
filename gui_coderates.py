from logger import Logger
from config import Config
from codegen import Codegen

class Guicoderate(object):
    
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, window):
        self.config = Config()
        self.logger = Logger()
        self.codegen = Codegen()
        self.window = window
        self.log = Logger.log
        self.pb_coderates_state = []
        self.max_coderates_pb = 12
        self.coderate_value = None
        self.coderate_pb = None
        self.startup_processes()

    #*******************************************************************************************
    def startup_processes(self):
        self.generate_coderate_pushbuttons()


    #*******************************************************************************************
    def generate_coderate_pushbuttons(self):
        """
        Turns on pre-created buttons on the screen for codrates.  The list of buttons to be
        activated come from the coderate generator class.  button presses are caught by the
        frequency_pushbutton_change routine.
        """
        counter = 0
        coderates = self.codegen.coderates
        self.log.debug("FREQUENCIES:{}".format(coderates))
        for coderate in coderates:
            button = getattr(self.window, 'PB_coderate_%s' % counter)
            button.released.connect(lambda idx=counter: self.coderate_pushbutton_change(idx))
            button.setStyleSheet('background-color: red;border-radius:10px')
            button.setText(str(coderate))
            button.setVisible(True)
            self.pb_coderates_state.append(0)
            counter = counter + 1
        for t in range(counter, self.max_coderates_pb):
            button = getattr(self.window, 'PB_coderate_%s' % t)
            button.setVisible(False)
        self.window.LBL_current_coderate.setText("OFF")

    # *******************************************************************************************
    def coderate_pushbutton_change(self, buttonid):
        button = getattr(self.window, 'PB_coderate_%s' % buttonid)
        self.log.debug("CODERATE PB changed BUTTON:{}".format(buttonid))
        if self.pb_coderates_state[buttonid] == 1:
            self.pb_coderates_state[buttonid] = 0
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "FALSE"))
            # button.setStyleSheet('background-color: red;border-radius:10px')
        elif self.pb_coderates_state[buttonid] == 0:
            self.pb_coderates_state[buttonid] = 1
            self.log.debug("Button: {} Set to: {} ".format(buttonid, "TRUE"))
            # button.setStyleSheet('background-color: green;border-radius:10px')
        if self.coderate_pb is None:
            button.setStyleSheet('background-color: green;border-radius:10px')
            self.window.LBL_current_coderate.setText(str(self.codegen.coderates[buttonid]))
            self.coderate_value = self.codegen.coderates[buttonid]
            self.coderate_pb = buttonid
        elif self.coderate_pb is not None:
            if buttonid is self.coderate_pb:
                button.setStyleSheet('background-color: red;border-radius:10px')
                self.window.LBL_current_coderate.setText("OFF")
                self.coderate_value = 1
                self.coderate_pb = None
            elif buttonid is not self.coderate_pb:
                last_button = getattr(self, 'PB_coderate_%s' % self.coderate_pb)
                last_button.setStyleSheet('background-color: red;border-radius:10px')
                button.setStyleSheet('background-color: green;border-radius:10px')
                self.window.LBL_current_coderate.setText(str(self.codegen.coderates[buttonid]))
                self.coderate_value = self.codegen.coderates[buttonid]
                self.coderate_pb = buttonid
        self.codegen.coderate_ppm = self.coderate_value
        self.codegen.coderate_generate()


    #*******************************************************************************************
    def load_from_config(self):
        pass
