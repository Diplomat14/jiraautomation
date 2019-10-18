from xdev.core.logger import logger
from enum import Enum
import importlib

class operations_register(object):

    def __init__(self):
        self.__operations = {}
        self.__operation_names = []
        self.__dynamic_operations = {}

    def register(self,operation):
        assert isinstance(operation,type), "operation has to be a child of basic_operation type"
        if operation not in self.__operations:
            self.__operations[operation.name()] = operation
            self.__operation_names.append(operation.name())

    def register_dynamic(self,user_name,class_name,module_path,package_path):
        self.__dynamic_operations[user_name] = {}
        self.__dynamic_operations[user_name]['class'] = class_name
        self.__dynamic_operations[user_name]['module'] = module_path
        self.__dynamic_operations[user_name]['package'] = package_path
        self.__dynamic_operations[user_name]['loaded'] = False
        self.__operation_names.append(user_name)

    def __load_operation(self,name):
        mod = importlib.import_module(self.__dynamic_operations[name]['module'],self.__dynamic_operations[name]['package'])
        self.__dynamic_operations[name]['loaded'] = True
        return getattr(mod,self.__dynamic_operations[name]['class'])

    def is_operation_loaded(self, name):
        if name in self.__dynamic_operations:
            return self.__dynamic_operations[name]['loaded']
        else:
            return True

    def get_operation_class(self, name):
        if name in self.__dynamic_operations:
            return self.__load_operation(name)
        else:
            return self.__operations[name]

    @property
    def operation_names(self):
        return self.__operation_names

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
        self.__logger = logger.from_parent(self.name(),iLogger)

    @property
    def logger(self):
        return self.__logger

    def execute(self,container,args):
        return ""
