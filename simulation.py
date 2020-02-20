import logging
import support.support
import logger
import config

class Simulation(object):

    logging.info("Instantiating {} class...".format(__qualname__))

    def __init__(self, commander):
        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.log.info('Starting up simulation routine...')
        self.support = support.support.Support()
        self.config = config.Config()
        self.commander = commander
        self.log.debug('Simulation initializing...')
        self.primary_gain_last_value = 0
        self.secondary_gain_last_value = 0
        self.primary_gain_local_val = 0
        self.secondary_gain_local_val = 0
        self.primary_gain_direction = 0
        self.secondary_gain_direction = 0
        self.speed_1_last_value = 0
        self.speed_2_last_value = 0
        self.speed_1_local_value = 0
        self.speed_2_local_value = 0
        self.speed_1_direction = 0
        self.speed_2_direction = 0
        self.freq = 6
        self.cs = 0
        self.clockwise = 1
        self.anti_clockwise = 0
        self.level = 0
        self.tick = 0
        self.log.debug("{} init complete...".format(__name__))

    # **************************************************************************
    def change_primary_gain(self, value):
        if value > self.primary_gain_last_value:
            self.log.debug("Primary Gain GUI Knob ANTI CLOCKWISE")
            self.primary_gain_direction = self.anti_clockwise
        else:
            self.log.debug("Primary Gain GUI Knob CLOCKWISE")
            self.primary_gain_direction = self.clockwise
        self.primary_gain_change(self.primary_gain_direction)
        self.primary_gain_last_value = value

    # **************************************************************************
    def change_secondary_gain(self, value):
        # print('FREQ VALUE :' + str(value))
        if value > self.secondary_gain_last_value:
            self.log.debug("Secondary Gain GUI Knob ANTI CLOCKKWISE")
            direction = self.anti_clockwise
        else:
            self.log.debug("Secondary Gain GUI Knob CLOCKWISE")
            direction = self.clockwise
        self.secondary_gain_change(direction)
        self.secondary_gain_last_value = value

    # **************************************************************************
    def change_speed_1(self, value):
        if value > self.speed_1_last_value:
            self.log.debug("Speed 1 GUI Knob ANTI CLOCKWISE")
            direction = self.anti_clockwise
        else:
            self.log.debug("Speed 1 GUI Knob  CLOCKWISE")
            direction = self.clockwise
        self.speed_0_change(direction)
        self.speed_1_last_value = value

    # **************************************************************************
    def change_speed_2(self, value):
        if value > self.speed_2_last_value:
            self.log.debug("Speed 2 GUI Knob ANTI CLOCKWISE")
            direction = self.anti_clockwise
        else:
            self.log.debug("Speed 2 GUI Knob CLOCKWISE")
            direction = self.clockwise
        self.speed_1_change(direction)
        self.speed_2_last_value = value

    # **************************************************************************
    def primary_gain_change(self, direction):
        if direction == self.clockwise:
            self.sim_pins = self.config.rotary_2_pins
        elif direction == self.anti_clockwise:
            self.sim_pins = reversed(self.config.rotary_2_pins)
        self.commander.simulate_gain("GAIN0",self.sim_pins)

    # **************************************************************************
    def secondary_gain_change(self, direction):
        if direction == self.clockwise:
            self.sim_pins = self.config.rotary_3_pins
        elif direction == self.anti_clockwise:
            self.sim_pins = reversed(self.config.rotary_3_pins)
        self.commander.simulate_gain("GAIN1",self.sim_pins)


    # **************************************************************************
    def speed_0_change(self, direction):
        if direction == self.clockwise:
            self.sim_pins = self.config.rotary_0_pins
        elif direction == self.anti_clockwise:
            self.sim_pins = reversed(self.config.rotary_0_pins)
        self.commander.simulate_speed("SPEED0",self.sim_pins)

    # **************************************************************************
    def speed_1_change(self, direction):
        if direction == self.clockwise:
            self.sim_pins = self.config.rotary_1_pins
        elif direction == self.anti_clockwise:
            self.sim_pins = reversed(self.config.rotary_1_pins)
        self.commander.simulate_speed("SPEED1", self.sim_pins)

    # **************************************************************************
    def __str__(self):
        return 'Simulation'


if __name__ == '__main__':
    sim = Simulation

