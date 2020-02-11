import rotary
import speedgen
import codegen


class Commander(object):
    def __init__(self):
        self.rotary = rotary.Rotary()
        self.speed = speedgen.Speed()
        self.codegen = codegen.Codegen()
