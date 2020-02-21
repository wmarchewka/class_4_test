#libraries
import logging

#my libraries
# from config import Config
# from logger import  Logger
# from support.support import Support
from simulation import Simulation

class Signaling(Simulation):

    logging.debug("Instantiating {} class...".format(__qualname__))

    def __init__(self):
        super().__init__()
        #self.window = Mainwindow().window
        self.config = Config()
        self.logger = Logger()
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.support = Support()
        self.simulation = Simulation()
        #self.commander = Commander()
        self.startup_processes()
        self.log.debug("{} init complete...".format(__name__))


    def startup_processes(self):
        self.signaling()


    def signaling(self):
        # primary and secondary gain encoders value change
        self.window.QDIAL_primary_gain.valueChanged.connect(self.qdial_gain_0_value_changed)
        self.window.QDIAL_secondary_gain.valueChanged.connect(self.qdial_gain_1_value_changed)

        # speed 1 and speed2 value change
        self.window.QDIAL_speed_1.valueChanged.connect(self.qdial_speed_0_value_changed)
        self.window.QDIAL_speed_2.valueChanged.connect(self.qdial_speed_1_value_changed)

        
        self.logger = logger.Logger(level=logging.CRITICAL)


    def qdial_speed_0_value_changed(self, value):
        self.log.debug("Qdial Speed 0 changed:{}".format(value))
        ret_pins = self.simulation.speed_0_value_changed(value)
        self.commander.simulate_speed('SPEED0', ret_pins)

    def qdial_speed_1_value_changed(self, value):
        self.log.debug("Qdial Speed 1 changed:{}".format(value))
        ret_pins = self.simulation.speed_1_value_changed(value)
        self.commander.simulate_speed('SPEED1', ret_pins)

    def qdial_gain_0_value_changed(self, value):
        self.log.debug("Qdial Gain 0 changed:{}".format(value))
        ret_pins = self.simulation.gain_0_value_changed(value)
        self.commander.gains_callback('SPEED0', ret_pins)

    def qdial_gain_1_value_changed(self, value):
        self.log.debug("Qdial Gain 1 changed:{}".format(value))
        ret_pins = self.simulation.gain_1_value_changed(value)
        self.commander.gains_callback('SPEED1', ret_pins)
