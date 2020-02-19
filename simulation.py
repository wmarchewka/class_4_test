import logging
import support.support
import rotary
import speedgen
import logger

class Simulation(object):

    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self, mainwindow):
        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger()
        self.log.info('Starting up simulation routine...')
        self.mainwindow = mainwindow
        self.support = support.support.Support()
        self.rotary = rotary.Rotary()
        if __name__ == '__main__':
            self.signal_generator = speedgen.Speedgen()
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
        self.speed_1_change(direction)
        self.speed_1_last_value = value

    # **************************************************************************
    def change_speed_2(self, value):
        if value > self.speed_2_last_value:
            self.log.debug("Speed 2 GUI Knob ANTI CLOCKWISE")
            direction = self.anti_clockwise
        else:
            self.log.debug("Speed 2 GUI Knob CLOCKWISE")
            direction = self.clockwise
        self.speed_2_change(direction)
        self.speed_2_last_value = value

    # **************************************************************************
    def primary_gain_change(self, direction):
        if direction == self.clockwise:
            self.primary_gain_local_val = self.primary_gain_local_val + 1
            if self.primary_gain_local_val > 4:
                self.primary_gain_local_val = 1
        else:
            self.primary_gain_local_val = self.primary_gain_local_val - 1
            if self.primary_gain_local_val < 1:
                self.primary_gain_local_val = 4
        self.log.debug('PRIMARY GAIN VAL:' + str(self.primary_gain_local_val))
        if self.primary_gain_local_val == 1:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 1]
            self.rotary.rotary_2_pin_0(23, self.level, self.tick)
            self.rotary.simulate = False
        if self.primary_gain_local_val == 2:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 1]
            self.rotary.rotary_2_pin_1(24, self.level, self.tick)
            self.rotary.simulate = False
        if self.primary_gain_local_val == 3:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 0]
            self.rotary.rotary_2_pin_0(23, self.level, self.tick)
            self.rotary.simulate = False
        if self.primary_gain_local_val == 4:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 0]
            self.rotary.rotary_2_pin_1(24, self.level, self.tick)
            self.rotary.simulate = False

    # **************************************************************************
    def secondary_gain_change(self, direction):
        if direction == self.clockwise:
            self.secondary_gain_local_val = self.secondary_gain_local_val + 1
            if self.secondary_gain_local_val > 4:
                self.secondary_gain_local_val = 1
        elif direction == self.anti_clockwise:
            self.secondary_gain_local_val = self.secondary_gain_local_val - 1
            if self.secondary_gain_local_val < 1:
                self.secondary_gain_local_val = 4
        self.log.debug('SECONDARY GAIN VAL:' + str(self.secondary_gain_local_val))
        if self.secondary_gain_local_val == 1:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 1]
            self.rotary.rotary_3_pin_0(25, self.level, self.tick)
            self.rotary.simulate = False
        if self.secondary_gain_local_val == 2:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 1]
            self.rotary.rotary_3_pin_1(12, self.level, self.tick)
            self.rotary.simulate = False
        if self.secondary_gain_local_val == 3:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 0]
            self.rotary.rotary_3_pin_0(25, self.level, self.tick)
            self.rotary.simulate = False
        if self.secondary_gain_local_val == 4:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 0]
            self.rotary.rotary_3_pin_1(12, self.level, self.tick)
            self.rotary.simulate = False

    # **************************************************************************
    def speed_1_change(self, direction):
        if direction == self.clockwise:
            self.speed_1_local_value = self.speed_1_local_value + 1
            if self.speed_1_local_value > 4:
                self.speed_1_local_value = 1
        elif direction == self.anti_clockwise:
            self.speed_1_local_value = self.speed_1_local_value - 1
            if self.speed_1_local_value < 1:
                self.speed_1_local_value = 4
        self.log.debug('SPEED 1 VAL:' + str(self.speed_1_local_value))
        if self.speed_1_local_value == 1:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 1]
            self.rotary.rotary_0_pin_0(4, self.level, self.tick)
            self.rotary.simulate = False
        if self.speed_1_local_value == 2:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 1]
            self.rotary.rotary_0_pin_1(14, self.level, self.tick)
            self.rotary.simulate = False
        if self.speed_1_local_value == 3:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 0]
            self.rotary.rotary_0_pin_0(4, self.level, self.tick)
            self.rotary.simulate = False
        if self.speed_1_local_value == 4:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 0]
            self.rotary.rotary_0_pin_1(14, self.level, self.tick)
            self.rotary.simulate = False

    # **************************************************************************
    def speed_2_change(self, direction):
        if direction == self.clockwise:
            self.speed_2_local_value = self.speed_2_local_value + 1
            if self.speed_2_local_value > 4:
                self.speed_2_local_value = 1
        elif direction == self.anti_clockwise:
            self.speed_2_local_value = self.speed_2_local_value - 1
            if self.speed_2_local_value < 1:
                self.speed_2_local_value = 4
        self.log.debug('SPEED 2 VAL:' + str(self.speed_2_local_value))
        if self.speed_2_local_value == 1:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 1]
            self.rotary.rotary_1_pin_0(15, self.level, self.tick)
            self.rotary.simulate = False
        if self.speed_2_local_value == 2:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 1]
            self.rotary.rotary_1_pin_1(22, self.level, self.tick)
            self.rotary.simulate = False
        if self.speed_2_local_value == 3:
            self.rotary.simulate = True
            self.rotary.sim_pins = [1, 0]
            self.rotary.rotary_1_pin_0(15, self.level, self.tick)
            self.rotary.simulate = False
        if self.speed_2_local_value == 4:
            self.rotary.simulate = True
            self.rotary.sim_pins = [0, 0]
            self.rotary.rotary_1_pin_1(22, self.level, self.tick)
            self.rotary.simulate = False
    # **************************************************************************
    def __str__(self):
        return 'Simulation'


if __name__ == '__main__':
    sim = Simulation

