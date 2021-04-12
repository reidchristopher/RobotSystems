class Pin:
    def __init__(self, *value):
        pass
        
    def check_board_type(self):
        pass

    def init(self, mode, pull=1):
        pass

    def dict(self, *_dict):
        if len(_dict) == 0:
            return {"a": 0}
        else:
            pass

    def __call__(self, value):
        return 1

    def value(self, *value):
        return 1

    def on(self):
        return 1

    def off(self):
        return 0

    def high(self):
        return self.on()

    def low(self):
        return self.off()

    def mode(self, *value):
        if len(value) == 0:
            return (1, 1)
        else:
            pass

    def pull(self, *value):
        return 1

    def irq(self, handler=None, trigger=None, bouncetime=200):
        pass

    def name(self):
        return "GPIO_NULL"

    def names(self):
        return ["name", "board_name"]

    class cpu(object):

        def __init__(self):
            pass
