#my libraries
from support.support import Support
from logger import Logger
from config import Config


class Simulation(object):
    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, support, config, logger):
        Logger.log.debug('{} initializing....'.format(__name__))
        self.logger = logger
        self.log = Logger.log
        self.log.info('Starting up simulation routine...')
        self.support = support
        self.config = config
        self.log.debug('Simulation initializing...')
        self.speed_0_last_value = 0
        self.speed_1_last_value = 0
        self.gain_0_last_value = 0
        self.gain_1_last_value = 0
        self.CLOCKWISE = 1
        self.ANTI_CLOCKWISE = 0
        self.sim_pins = []
        self.log.debug("{} init complete...".format(__name__))

    # **************************************************************************
    # **************************************************************************
    def gain_0_value_changed(self, value):
        direction = 0
        diff = value - self.gain_0_last_value
        self.log.debug("Diff:{}".format(diff))
        if diff == 1 or diff == -23:
            self.log.debug("GAIN 0 GUI Knob  CLOCKWISE")
            direction = self.CLOCKWISE
        elif diff == -1 or diff == 23:
            self.log.debug("GAIN 0 GUI Knob ANTI CLOCKWISE")
            direction = self.ANTI_CLOCKWISE
        sim_pins = self.change_gain_0(direction)
        self.gain_0_last_value = value
        return sim_pins

    # **************************************************************************
    def change_gain_0(self, direction):
        if direction == self.CLOCKWISE:
            sim_pins = self.config.rotary_2_pins
        elif direction == self.ANTI_CLOCKWISE:
            sim_pins = self.config.rotary_2_pins
            sim_pins = sim_pins[::-1]
        else:
            sim_pins = [0, 0]
        return sim_pins

    # **************************************************************************
    # **************************************************************************
    def gain_1_value_changed(self, value):
        direction = 0
        diff = value - self.gain_1_last_value
        self.log.debug("Diff:{}".format(diff))
        if diff == 1 or diff == -23:
            self.log.debug("GAIN 1 GUI Knob  CLOCKWISE")
            direction = self.CLOCKWISE
        elif diff == -1 or diff == 23:
            self.log.debug("GAIN 1 GUI Knob ANTI CLOCKWISE")
            direction = self.ANTI_CLOCKWISE
        sim_pins = self.change_gain_1(direction)
        self.gain_1_last_value = value
        return sim_pins

    # **************************************************************************
    def change_gain_1(self, direction):
        if direction == self.CLOCKWISE:
            sim_pins = self.config.rotary_3_pins
        elif direction == self.ANTI_CLOCKWISE:
            sim_pins = self.config.rotary_3_pins
            sim_pins = sim_pins[::-1]
        else:
            sim_pins = [0, 0]
        return sim_pins

    # **************************************************************************
    # **************************************************************************
    def speed_0_value_changed(self, value):
        direction = 0
        diff = value - self.speed_0_last_value
        self.log.debug("Diff:{}".format(diff))
        if diff == 1 or diff == -23:
            self.log.debug("SPEED0 GUI Knob  CLOCKWISE")
            direction = self.CLOCKWISE
        elif diff == -1  or diff == 23:
            self.log.debug("SPEED0 GUI Knob ANTI CLOCKWISE")
            direction = self.ANTI_CLOCKWISE
        sim_pins = self.change_speed_0(direction)
        self.speed_0_last_value = value
        return sim_pins

    # **************************************************************************
    def change_speed_0(self, direction):
        if direction == self.CLOCKWISE:
            sim_pins = self.config.rotary_0_pins
        elif direction == self.ANTI_CLOCKWISE:
            sim_pins = self.config.rotary_0_pins
            sim_pins = sim_pins[::-1]
        else:
            sim_pins = [0, 0]
        return sim_pins

    # **************************************************************************
    # **************************************************************************
    def speed_1_value_changed(self, value):
        direction = 0
        diff = value - self.speed_1_last_value
        self.log.debug("Diff:{}".format(diff))
        if diff == 1 or diff == -23:
            self.log.debug("SPEED0 1 GUI Knob  CLOCKWISE")
            direction = self.CLOCKWISE
        elif diff == -1  or diff == 23:
            self.log.debug("SPEED1 1 GUI Knob ANTI CLOCKWISE")
            direction = self.ANTI_CLOCKWISE
        sim_pins = self.change_speed_1(direction)
        self.speed_1_last_value = value
        return sim_pins

    # **************************************************************************
    def change_speed_1(self, direction):
        if direction == self.CLOCKWISE:
            sim_pins = self.config.rotary_1_pins
        elif direction == self.ANTI_CLOCKWISE:
            sim_pins = self.config.rotary_1_pins
            sim_pins = sim_pins[::-1]
        else:
            sim_pins = [0, 0]
        return sim_pins

    def __str__(self):
        return 'Simulation'


if __name__ == '__main__':
    sim = Simulation
