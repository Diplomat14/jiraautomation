from jiraautomation.operations.operation import basic_operation
from jiraorm.JSWContainer import JSWContainer
from jiraorm.BasicConfig import ConnectionConfig, SecurityConfig
from xdev.core.logger import logger
import json
import requests
import ast


class init_jira(basic_operation):
    __logger = None

    @staticmethod
    def name():
        return "InitJira"

    @staticmethod
    def init_arguments(operation_group):
        pass

    @staticmethod
    def parse_arguments(args):
        pass

    def __init__(self, iLogger):
        super(init_jira, self).__init__(iLogger)

    def execute(self, autocontainer, args):
        l = self.logger

        try:
            c = containers()
            cont = c.create_container(l, args)

            return cont

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))


class containers:

    def __init__(self):
        self.__containers = []

    @property
    def containers(self):
        return self.__containers

    def add_container(self, container):
        self.__containers.append(container)

    def create_container(self, l: logger, args):
        options = get_cookies(l, args) if args.options else None
        ccfg = ConnectionConfig(args.server, options)
        scfg = SecurityConfig(args.username, args.access_token)
        c = JSWContainer(l, ccfg, scfg)
        l.msg("JIRA Container created")
        self.add_container(c)

        return c


def get_cookies(l: logger, args):
    session = requests.Session()

    data = {'username': args.username, 'password': args.access_token}
    opt = ast.literal_eval(args.options)
    if 'client_cert' not in opt:
        l.error("No certificate data provided")
    if 'server' not in opt:
        l.error("No login url provided")

    client_cert, server = opt.get('client_cert'), opt.get('server')
    response = session.post(server, data=data, cert=client_cert)
    if response.status_code != 200:
        l.error("Connection with certificate failed")

    cookies = dict(response.cookies.items())
    if not len(cookies) > 0:
        l.error("No cookies were generated")
    else:
        opt.update({'cookies': cookies})
        l.msg('Cookies were generated')

    return json.dumps(opt)


