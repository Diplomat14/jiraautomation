from jiraautomation.automationcore import automationcore
from xdev.core.logger import logger


class AutoContainer:
    __logger = None

    @staticmethod
    def name():
        return "AutoContainer"

    def __init__(self, iLogger:logger):
        assert isinstance(iLogger, logger)
        self.__logger = iLogger

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, state):
        self.__logger = state['__logger']

    def init_jira(self, args):
        op = 'InitJira'
        op_class = automationcore.get_operation_class(op)
        op_instance = op_class(self.__logger)
        container = op_instance.execute(self, args)
        return container