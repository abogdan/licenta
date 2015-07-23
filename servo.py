

class Servo(object):
    _instance = {}

    def __new__(cls, *args, **kwargs):
        gpio = args[0]
        try:
            if isinstance(cls._instance[gpio], cls):
                return cls._instance[gpio]
        except (KeyError, TypeError):
            cls._instance[gpio] = object.__new__(cls, *args, **kwargs)
            return cls._instance[gpio]

    def __init__(self, gpio, controller, limits=(70, 250)):
        self.gpio = gpio
        self.controller = controller
        self.max, self.min = limits

    def move(self, position):
        self.controller.write(
            '{0}={1}\n'.format(int(self.gpio), self.assure(position)))
        self.controller.flush()

    def assure(self, position):
        return min(int(self.max), max(int(position), int(self.min)))

