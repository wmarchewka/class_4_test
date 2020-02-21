#libraries
import logging

#my libraries
import config
import logger
import support.support
class GuiUtilities(object):

    def __init__(self, window):
        self.window = window
        self.config = config.Config()
        self.logger = logger.Logger()
        self.support = support.support.Support()
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.startup_processes()

    def startup_processes(self):
        pass

    def generate_frequency_pushbuttons(self):
        """
        Turns on pre-created buttons on the screen for frequencies.  The list of buttons to be
        activated come from the coderate generator class.  button presses are caught by the
        frequency_pushbutton_change routine.
        """
        y = 0
        self.log.debug("CODERATES:{}".format(self.code_rate_generator.company_frequencies))
        # TODO figure out how to get this to work converted to Pyside from PyQt5
        for x in self.code_rate_generator.company_frequencies:
            button = getattr(self.window, 'PB_freq_%s' % y)
            button.released.connect(lambda idx=y: self.frequency_pushbutton_change(idx))
            button.setStyleSheet('background-color: red;border-radius:10px')
            button.setText(x)
            button.setVisible(True)
            self.pb_frequencies_state.append(0)
            y = y + 1
        for t in range(y, self.max_frequencies_pb):
            button = getattr(self.window, 'PB_freq_%s' % t)
            button.setVisible(False)
        self.window.LBL_current_pri_carrier.setText("OFF")
        self.window.LBL_current_sec_carrier.setText("OFF")