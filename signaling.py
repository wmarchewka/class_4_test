#libraries

#my libraries
from logger import Logger
from simulation import Simulation

class Signaling():

    Logger.log.debug("Instantiating {} class...".format(__qualname__))

    def __init__(self, window, commander, config, logger, support):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.window = window
        self.config = config
        self.logger = logger
        self.log = Logger.log
        self.support = support
        self.simulation = Simulation(config=self.config, support = self.support, logger=self.logger)
        self.commander = commander
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))

    #  ***************************************************************************************
    def startup_processes(self):
        self.signaling()

    #  ***************************************************************************************
    def signaling(self):
        # primary and secondary gain encoders value change
        self.window.QDIAL_primary_gain.valueChanged.connect(self.qdial_gain_0_value_changed)
        self.window.QDIAL_secondary_gain.valueChanged.connect(self.qdial_gain_1_value_changed)

        # speed 1 and speed2 value change
        self.window.QDIAL_speed_1.valueChanged.connect(self.qdial_speed_0_value_changed)
        self.window.QDIAL_speed_2.valueChanged.connect(self.qdial_speed_1_value_changed)

        # changes logging level
        self.window.PB_log_level.clicked.connect(self.commander.log_level_PB_changed)

        # BUTTONS TO CHHANGE SHAPE OF SPEED OUTPUTS
        self.window.BUTTON_speed0_sine.toggled.connect(
            lambda: self.speed0_buttonstate_change(self.window.BUTTON_speed0_sine))
        self.window.BUTTON_speed0_square.toggled.connect(
            lambda: self.speed0_buttonstate_change(self.window.BUTTON_speed0_square))
        self.window.BUTTON_speed0_triangle.toggled.connect(
            lambda: self.speed0_buttonstate_change(self.window.BUTTON_speed0_triangle))
        self.window.BUTTON_speed1_sine.toggled.connect(
            lambda: self.speed1_buttonstate_change(self.window.BUTTON_speed1_sine))
        self.window.BUTTON_speed1_square.toggled.connect(
            lambda: self.speed1_buttonstate_change(self.window.BUTTON_speed1_square))
        self.window.BUTTON_speed1_triangle.toggled.connect(
            lambda: self.speed1_buttonstate_change(self.window.BUTTON_speed1_triangle))


    #  ***************************************************************************************
    def speed0_buttonstate_change(self, button):
        freq_shape = None
        self.log.info(button.text())
        if button.text() == "SINE":
            freq_shape = 0
        if button.text() == "SQUARE":
            freq_shape = 1
        if button.text() == "TRIANGLE":
            freq_shape = 2
        name ="SPEED0"
        self.commander.speed_buttonstate_change(name, freq_shape)

    #  ***************************************************************************************
    def speed1_buttonstate_change(self, button):
        freq_shape = None
        self.log.info(button.text())
        if button.text() == "SINE":
            freq_shape = 0
        if button.text() == "SQUARE":
            freq_shape = 1
        if button.text() == "TRIANGLE":
            freq_shape = 2
        name ="SPEED1"
        self.commander.speed_buttonstate_change(name, freq_shape)

    #  ***************************************************************************************
    def qdial_speed_0_value_changed(self, value):
        self.log.debug("Qdial Speed 0 changed:{}".format(value))
        ret_pins = self.simulation.speed_0_value_changed(value)
        self.commander.speed_simulate('SPEED0', ret_pins)

    #  ***************************************************************************************
    def qdial_speed_1_value_changed(self, value):
        self.log.debug("Qdial Speed 1 changed:{}".format(value))
        ret_pins = self.simulation.speed_1_value_changed(value)
        self.commander.speed_simulate('SPEED1', ret_pins)

    #  ***************************************************************************************
    def qdial_gain_0_value_changed(self, value):
        self.log.debug("Qdial Gain 0 changed:{}".format(value))
        ret_pins = self.simulation.gain_0_value_changed(value)
        self.commander.gain_simulate('SPEED0', ret_pins)

    #  ***************************************************************************************
    def qdial_gain_1_value_changed(self, value):
        self.log.debug("Qdial Gain 1 changed:{}".format(value))
        ret_pins = self.simulation.gain_1_value_changed(value)
        self.commander.gain_simulate('SPEED1', ret_pins)

