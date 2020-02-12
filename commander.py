import rotary
import speedgen
import codegen
import digpots

class Commander(object):
    def __init__(self):
        self.rotary = rotary.Rotary()
        self.speed = speedgen.Speed()
        self.codegen = codegen.Codegen()
        self.digpots = digpots.Digpots()
