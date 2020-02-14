import logging

#my imports
import rotary
import speedgen
import codegen
import digpots
import logger

class Commander(object):

    logging.debug("Initiating {} class...".format(__qualname__))

    def __init__(self):
        self.logger = logger.Logger()
        self.log = self.logger.log
        self.log = logging.getLogger(__name__)
        self.rotary = rotary.Rotary()
        self.speed = speedgen.Speedgen()
        self.codegen = codegen.Codegen()
        self.digpots = digpots.DigPots()
        self.log.debug("{} init complete...".format(__name__))
