from basiclogger import Basiclogger
from config import Config
from logger import Logger

class ConfigLogger(Config, Logger, Basiclogger):
    def __init__(self):
        super().__init__()