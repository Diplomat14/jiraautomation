from xdev.core.logger import logger
import jiraorm.BasicConfig as j_cfg


class automationcore(object):
    __logger = None

    __operations = {}

    @staticmethod
    def add_operation(operation):
        automationcore.__operations[operation.name()] = operation

    @staticmethod
    def get_operation_names():
        return automationcore.__operations.keys()

    @staticmethod
    def get_operations():
        return automationcore.__operations


    
    #def __init__(self, connectionCfg : j_cfg.ConnectionConfig, securityCfg : j_cfg.SecurityConfig, useMultithreading : bool, poolSize : int, parentLogger:LoggerClass):
    #    self.__logger = logger.from_parent('JIRAAutomationCore',parentLogger)

