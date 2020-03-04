import faulthandler

faulthandler.enable()
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import QFile
from PySide2.QtGui import QFontDatabase, QFont, QWindow

# mylibraries
from logger import Logger
from signaling import Signaling
from gui.gui_coderates import Guicoderate
from gui.gui_frequencies import GuiFrequencies
from gui import QTResources

class Mainwindow(QWindow):

    Logger.log.info("Instantiating {} class...".format(__qualname__))
    guiname = None

    def __init__(self, commander, codegen, config, logger, support, securitylevel, *args, **kwargs):
        super().__init__(*args, **kwargs)
        Logger.log.debug('{} initializing....'.format(__name__))
        self.window = None
        self.config = config
        self.logger = logger
        self.support = support
        self.log = Logger.log
        self.commander = commander
        self.securitylevel = securitylevel
        self.startup_processes()
        self.guicode = Guicoderate(window=self.window, codegen=codegen, config=config, logger=logger)
        self.freqcode = GuiFrequencies(window=self.window, codegen=codegen, config=config, logger=logger)
        self.signaling = Signaling(window=self.window, commander=self.commander, config=self.config, logger=self.logger,
                                   support=self.support)
        self.log.debug("{} init complete...".format(__name__))

    # *****************************************************************************
    def startup_processes(self):
        self.config_file_load()
        self.loadscreen()
        self.screen_fullscreen()
        self.fonts_list()
        self.securitylevel.index_tab_pages(self.window)
        self.securitylevel.set_security_level("technician")
        self.securitylevel.update_gui(self.window)
    # *****************************************************************************
    def fonts_list(self):
        """
        list available fonts
        """
        self.fontDB = QFontDatabase()
        self.fontDB.addApplicationFont(":/FONTS/FONTS/digital-7.ttf")
        self.fontDB.addApplicationFont(":/FONTS/FONTS/SiemensSlab_Prof_BlackItalic.ttf")
        #self.siemensslab = QFont("Siemens Slab", 64, 1)
        #self.digital7font = QFont("Digital-7", 64, 1)
        #self.window.LBL_loop_current.setFont(self.digital7font)

    # *****************************************************************************
    def screen_fullscreen(self, fullscreen=None):
        if self.support.ostype == 'rpi' or fullscreen:
            self.window.showFullScreen()
            self.log.debug("Window set to fullscreen...")
        else:
            self.window.showNormal()

    # ******************************************************************************
    def config_file_load(self):
        Mainwindow.display_brightness = self.config.display_brightness
        Mainwindow.guiname = self.config.guiname
        Mainwindow.screen_brightness_max = self.config.screen_brightness_max
        Mainwindow.screen_brightness_min = self.config.screen_brightness_min

    # ******************************************************************************
    def loadscreen(self):
        try:
            ui_file = QFile(Mainwindow.guiname)
            ui_file.open(QFile.ReadOnly)
            loader = QUiLoader()
            self.window = loader.load(ui_file)
            ui_file.close()
            self.window.show()
            self.log.debug('Loading screen ' + self.guiname)
        except FileNotFoundError:
            self.log.debug("Could not find {}".format(self.guiname))  # CATCHES EXIT SHUTDOWN



    # ************************************************************************************
    # TODO: only allow items that have previsouly run. items here are running that havent been perfromed
    # TODO: try "ATEXIT"


