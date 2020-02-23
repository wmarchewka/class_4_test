#my libraries
from logger import Logger

class Pollperm():

    Logger.log.info("Instantiating {} class...".format(__qualname__))

    def __new__(cls):
        if not hasattr(cls, 'instance') or not cls.instance:
            cls.instance = super().__new__(cls)
            #logger.log.debug("Creating new class {}".format(cls.instance))
        else:
            pass
            #logger.log.debug("Creating instance class {}".format(cls.instance))

        return cls.instance

    def __init__(self):
        self._polling_prohibited = False
        self.init = True
        self.logger = Logger()
        self.log = Logger.log
        self.polling_prohibited = (False, self.__class__)
        self.log.debug("{} init complete...".format(__name__))

    @property
    def polling_prohibited(self):
        self.log.debug("Polling Prohibited: {}".format(self._polling_prohibited))
        return self._polling_prohibited

    @polling_prohibited.setter
    def polling_prohibited(self, val):
        setval, caller = val
        self.log.debug("Setting Polling Prohibited to:{} from {}".format(setval, caller))
        self._polling_prohibited = val
