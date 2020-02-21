from commander import Commander


class Portable(Commander):
    def __init__(self, name, shape, spi_channel, chip_select, pin_0, pin_1, pin_0_debounce, pin_1_debounce, thresholds,
                 callback, commander_speed_move_callback):
        super().__init__(name, shape, spi_channel, chip_select, pin_0, pin_1, pin_0_debounce, pin_1_debounce,
                         thresholds, callback, commander_speed_move_callback)


if __name__ == '__main__':
    p = Portable()


