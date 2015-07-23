import os
import ConfigParser


class Config(ConfigParser.SafeConfigParser):
    _instance = None
    CONFIG_SECTION = 'config'

    def __new__(cls, *args, **kwargs):
        print args
        if not isinstance(cls._instance, cls):
            cls._instance = object.__new__(cls, *args, **kwargs)
        return cls._instance

    def fetch(self, key, default=None):
        try:
            # replace placeholder with dir of current script
            # before returning value
            return self.get(Config.CONFIG_SECTION, key).replace(
                '{{DIR}}',
                os.path.dirname(os.path.realpath(__file__)))
        except KeyError:
            return default