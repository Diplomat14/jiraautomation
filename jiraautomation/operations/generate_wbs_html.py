from jiraautomation.operations.operation import basic_operation
from jinja2.loaders import FileSystemLoader
from jinja2.environment import Environment
import os


class generate_wbs_html(basic_operation):

    @staticmethod
    def name():
        return "GenerateWBSHTML"

    @staticmethod
    def init_arguments(operation_group):
        pass

    @staticmethod
    def parse_arguments(args):
        pass

    def __init__(self, iLogger):
        super(generate_wbs_html, self).__init__(iLogger)

    def execute(self, container, args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                param_wbsentry = args.data

                env = Environment()

                templatepath = "%s/../data/%s" % (os.path.dirname(os.path.realpath(__file__)), "generate_wbs")
                l.msg("Loading template from path %s" % templatepath)
                loader = FileSystemLoader(templatepath)

                template = loader.load(env, 'wbs.jinja2')
                return template.render(param_wbsentry=param_wbsentry,
                                       param_serverbase=container.connectionConfig.server)


            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)
