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
        self.knob_values = 0
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
        self.window.QDIAL_speed_0.valueChanged.connect(self.qdial_speed_0_value_changed)
        self.window.QDIAL_speed_1.valueChanged.connect(self.qdial_speed_1_value_changed)

        # changes logging level
        self.window.PB_log_level.clicked.connect(self.commander.log_level_PB_changed)

        # BUTTONS TO CHHANGE SHAPE OF SPEED OUTPUTS
        self.window.BUTTON_speed0_sine.toggled.connect(
            lambda: self.speed0_shapestate_change(self.window.BUTTON_speed0_sine))
        self.window.BUTTON_speed0_square.toggled.connect(
            lambda: self.speed0_shapestate_change(self.window.BUTTON_speed0_square))
        self.window.BUTTON_speed0_triangle.toggled.connect(
            lambda: self.speed0_shapestate_change(self.window.BUTTON_speed0_triangle))
        self.window.BUTTON_speed1_sine.toggled.connect(
            lambda: self.speed1_shapestate_change(self.window.BUTTON_speed1_sine))
        self.window.BUTTON_speed1_square.toggled.connect(
            lambda: self.speed1_shapestate_change(self.window.BUTTON_speed1_square))
        self.window.BUTTON_speed1_triangle.toggled.connect(
            lambda: self.speed1_shapestate_change(self.window.BUTTON_speed1_triangle))

        # primary and secondary gain encoders slide pressed
        self.window.QDIAL_primary_gain.sliderPressed.connect(self.primary_gain_dial_pressed)
        self.window.QDIAL_secondary_gain.sliderPressed.connect(self.secondary_gain_dial_pressed)

        # primary and secondary gain encoders slide pressed
        self.window.QDIAL_primary_gain.sliderReleased.connect(self.primary_gain_dial_released)
        self.window.QDIAL_secondary_gain.sliderReleased.connect(self.secondary_gain_dial_released)

        # primary and secondary gain encoders slide pressed
        self.window.QDIAL_speed_0.sliderPressed.connect(self.speed_0_dial_pressed)
        self.window.QDIAL_speed_1.sliderPressed.connect(self.speed_1_dial_pressed)

        # primary and secondary gain encoders slide pressed
        self.window.QDIAL_speed_0.sliderReleased.connect(self.speed_0_dial_released)
        self.window.QDIAL_speed_1.sliderReleased.connect(self.speed_1_dial_released)

        self.window.PB_gpio_manual_toggle.toggled.connect(self.gpio_manual_toggled)

        self.window.PB_chip_select_manual_toggle.toggled.connect(self.commander.manual_chip_select_toggled)

        # set brightness value
        self.window.SPIN_brightness.valueChanged.connect(self.commander.brightness_changed)

        # set gain lock
        self.window.CHK_gain_lock_percent.stateChanged.connect(self.commander.gains_lock)

        self.window.SLIDER_duty_cycle.valueChanged.connect(self.commander.SLIDER_duty_cycle_changed)
    #  ***************************************************************************************
    def speed0_shapestate_change(self, button):
        freq_shape = None
        self.log.info("SPEED 0 button pushed{}".format(button.text()))
        if button.text() == "SINE":
            freq_shape = 0
        if button.text() == "SQUARE":
            freq_shape = 1
        if button.text() == "TRIANGLE":
            freq_shape = 2
        name ="SPEED0"
        self.commander.speed_buttonstate_change(name, freq_shape)

    #  ***************************************************************************************
    def speed1_shapestate_change(self, button):
        freq_shape = None
        self.log.info("SPEED 1 button pushed{}".format(button.text()))
        if button.text() == "SINE":
            freq_shape = 0
        if button.text() == "SQUARE":
            freq_shape = 1
        if button.text() == "TRIANGLE":
            freq_shape = 2
        name ="SPEED1"
        self.commander.speed_buttonstate_change(name, freq_shape)

    #  ***************************************************************************************
    def gpio_manual_toggled(self, value):
        self.commander.gpio_manual_toggled(value)

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
        self.commander.gain_simulate('GAIN0', ret_pins)

    #  ***************************************************************************************
    def qdial_gain_1_value_changed(self, value):
        self.log.debug("Qdial Gain 1 changed:{}".format(value))
        ret_pins = self.simulation.gain_1_value_changed(value)
        self.commander.gain_simulate('GAIN1', ret_pins)

    # ************************************************************************************
    # CATCHES SPEED 0 KNOB pressed
    def speed_0_dial_pressed(self):
        self.log.debug('Speed 0 GUI knob PRESSED')
        self.modifyBit(self.knob_values, 2, 1)

    # ************************************************************************************
    # CATCHES SPEED 0 KNOB released
    def speed_0_dial_released(self):
        self.log.debug('Speed 0 GUI knob RELEASED')
        self.modifyBit(self.knob_values, 2, 0)

    # ************************************************************************************
    # CATCHES SPEED 1 KNOB PUSHED
    def speed_1_dial_pressed(self):
        self.log.debug('Speed 1 GUI knob PRESSED')
        self.modifyBit(self.knob_values, 3, 1)

    # ************************************************************************************
    # CATCHES SPEED 1 KNOB released
    def speed_1_dial_released(self):
        self.log.debug('Speed 1 GUI knob RELEASED')
        self.modifyBit(self.knob_values, 3, 0)

    # ************************************************************************************
    # CATCHES PRIMARY KNOB PUSHED
    def primary_gain_dial_pressed(self):
        self.log.debug('Primary Gain GUI knob PRESSED')
        self.modifyBit(self.knob_values, 0, 1)

    # ************************************************************************************
    # CATCHES PRIMARY KNOB PUSHED
    def primary_gain_dial_released(self):
        self.log.debug('Primary Gain GUI knob RELEASED')
        self.modifyBit(self.knob_values, 0, 0)

    # ************************************************************************************
    # CATCHES SECONDARY KNOB PUSHED
    def secondary_gain_dial_pressed(self):
        self.log.debug('Secondary Gain GUI knob RELEASED')
        self.modifyBit(self.knob_values, 1, 1)

    # ************************************************************************************
    # CATCHES SECONDARY KNOB released
    def secondary_gain_dial_released(self):
        self.log.debug('Secondary Gain GUI knob RELEASED')
        self.modifyBit(self.knob_values, 1, 0)

    # ************************************************************************************
    # Returns modified n.
    def modifyBit(self, n, p, b):
        mask = 1 << p
        self.knob_values = (n & ~mask) | ((b << p) & mask)
        self.log.debug("ModifyBits value {:08b}".format(self.knob_values))
        self.commander.knob_values = self.knob_values
        #self.commander.switches_callback_change_value(0)
