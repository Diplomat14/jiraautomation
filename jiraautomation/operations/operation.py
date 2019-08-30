from xdev.core.logger import logger
from enum import Enum

class operations_register(object):

    def __init__(self):
        self.__operations = []

    def register(self,operation):
        assert isinstance(operation,type), "operation has to be a child of basic_operation type"
        if operation not in self.__operations:
            self.__operations.append(operation)

    @property
    def operations(self):
        return self.__operations

class basic_operation(object):

    __logger = None

    @staticmethod
    def name():
        return "Basic"

    @staticmethod
    def init_arguments(self,operation_group):
        # operations_group = parser.add_argument_group

        # Add your argparse parameters here
        # operations_group.add_argument('-param1', '--parameter1', required=True,
        #                                   help='Parameter1 Description')
        pass

    @staticmethod
    def parse_arguments(self,args):
        # You might want to prepare arguments somehow like:
        # args.operation = CoreOperation[args.operation]
        # TODO: Do i need to return? it is by reference actually
        return args

    def __init__(self,iLogger:logger):
        assert isinstance(iLogger,logger)
        self.__logger = iLogger

    @property
    def logger(self):
        return self.__logger

    def execute(self,container,args):
        return ""
