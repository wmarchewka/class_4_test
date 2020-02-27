from PySide2.QtGui import QWindow
from PySide2.QtCore import QFile
from PySide2.QtUiTools import QUiLoader


# ********************************************************************************
# TODO speed 1 and speed 2 need to be linked and scaled etc
class SecurityWindow(QWindow):

    def __init__(self, securitylevel, logger):
        super().__init__()
        self.securitylevel = securitylevel
        self.logger = logger
        self.log = self.logger.log
        self.security_code = ""
        self.window = None
        self.startup_processes()

    def startup_processes(self):
        self.loadscreen()
        self.signals()

    def signals(self):
        #self.window.pb_0.clicked.connect(self.gui_button_clicked)
        #self.button.released.connect(lambda idx=counter: self.coderate_pushbutton_change(idx))
        for x in range(9):
            button = getattr(self.window, 'pb_%s' % x)
            button.released.connect(lambda idx=x: self.pushbutton_change(idx))
        self.window.PB_enter.clicked.connect(self.gui_enter_pressed)
        self.window.PB_clear.clicked.connect(self.gui_clear_pressed)

    def loadscreen(self):
        guiname = "gui/SECURITY.ui"
        try:
            ui_file = QFile(guiname)
            ui_file.open(QFile.ReadOnly)
            loader = QUiLoader()
            self.window = loader.load(ui_file)
            ui_file.close()
            #self.window.show()
            self.log.debug('Loading screen:'.format(guiname))
        except FileNotFoundError:
            self.log.debug("Could not find {}".format(guiname))  # CATCHES EXIT SHUTDOWN

    def pushbutton_change(self, buttonid):
        self.log.debug("button pushed:{}".format(buttonid))
        self.security_code = self.security_code + str(buttonid)
        self.window.LBL_security_code.setText(self.security_code)
        if len(self.security_code) == 4:
            self.gui_enter_pressed()

    def gui_enter_pressed(self):
        level = None
        self.log.debug("Security code:{}".format(self.security_code))
        if self.security_code == "1111":
            level = "admin"
        if self.security_code == "2222":
            level = "factory"
        if self.security_code == "3333":
            level = "technician"
        if self.security_code == "4444":
            level = "customer"
        self.security_code = ""
        self.window.LBL_security_code.setText(self.security_code)
        self.securitylevel.set_security_level(level)
        self.securitylevel.update_gui()
        self.window.close()

    def gui_clear_pressed(self):
        self.security_code = ""
        self.window.LBL_security_code.setText(self.security_code)


    def close(self):
        pass