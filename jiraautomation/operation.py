from xdev.core.logger import logger
from enum import Enum,

class basic_operation:

    __logger = None

    def __init__(self,iLogger:logger):
        assert isinstance(iLogger,logger)

        self.__logger = iLogger

    @property
    def name(self,opstype:Enum):
        return "Basic"

    def execute(self):
        pass






class test_operation(basic_operation):

    @@property
    def name(self):
        return "Test"

    def execute(self):
        return "Test OK"