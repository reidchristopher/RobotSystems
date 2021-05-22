class PWM:
    def __init__(self, channel, debug="critical"):
        pass

    def i2c_write(self, reg, value):
        pass

    def freq(self, *freq):
        if len(freq) == 0:
            return 1
        else:
            pass

    def prescaler(self, *prescaler):
        if len(prescaler) == 0:
            return 1
        else:
            pass

    def period(self, *arr):
        if len(arr) == 0:
            return 1
        else:
            pass

    def pulse_width(self, *pulse_width):
        if len(pulse_width) == 0:
            return 1
        else:
            pass

    def pulse_width_percent(self, *pulse_width_percent):
        if len(pulse_width_percent) == 0:
            return 1
        else:
            pass