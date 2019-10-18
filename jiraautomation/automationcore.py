from xdev.core.logger import logger
import jiraorm.BasicConfig as j_cfg


class automationcore(object):

    @staticmethod
    def set_register(register):
        automationcore.__register = register

    @staticmethod
    def get_operation_names():
        return automationcore.__register.operation_names

    @staticmethod
    def get_operation_class(name):
        return automationcore.__register.get_operation_class(name)

    @staticmethod
    def is_operation_loaded(name):
        return automationcore.__register.is_operation_loaded(name)

    @staticmethod
    def get_operations():
        return automationcore.__register.operations


    
    #def __init__(self, connectionCfg : j_cfg.ConnectionConfig, securityCfg : j_cfg.SecurityConfig, useMultithreading : bool, poolSize : int, parentLogger:LoggerClass):
    #    self.__logger = logger.from_parent('JIRAAutomationCore',parentLogger)

