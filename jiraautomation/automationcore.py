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

    @staticmethod
    def execute_operations_chain(autocontainer, operations, args):
        l = autocontainer.logger
        container = autocontainer.init_jira(args)

        for operation in operations:
            if operation in automationcore.get_operation_names():
                op_class = automationcore.get_operation_class(operation)
                op_instance = op_class(l)
                output = op_instance.execute(container, args)
                args.data = output
            else:
                l.warning("Operation %s not implemented" % str(args.operation))
        return output


    #def __init__(self, connectionCfg : j_cfg.ConnectionConfig, securityCfg : j_cfg.SecurityConfig, useMultithreading : bool, poolSize : int, parentLogger:LoggerClass):
    #    self.__logger = logger.from_parent('JIRAAutomationCore',parentLogger)

