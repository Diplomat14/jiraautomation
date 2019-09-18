from jiraautomation.operations.operation import  basic_operation
import os
from jinja2.loaders import FileSystemLoader
from jinja2.environment import Environment
from .generate_issues_tree import generate_issues_tree
from xdev.types.complex.tree import tree_type
from xdev.types.complex.tree import tree_node_type
from jiraorm.IssueExt import IssueExt
from jiraorm.EpicExt import EpicExt

class generate_wbs(basic_operation):

    @staticmethod
    def name():
        return "GenerateWBS"

    @staticmethod
    def init_arguments(operation_group):
        generate_issues_tree.init_arguments(operation_group)
        operation_group.add_argument('-gwbsEC', '--generatewbs_EpicCategory', required=True, help='Name of the Epic Category Field')
        operation_group.add_argument('-gwbsPERTO', '--generatewbs_PERTO', required=True, help='Name of the PERT Optimistic Field')
        operation_group.add_argument('-gwbsPERTR', '--generatewbs_PERTR', required=True, help='Name of the PERT Realistic Field')
        operation_group.add_argument('-gwbsPERTP', '--generatewbs_PERTP', required=True, help='Name of the PERT Pessimistic Field')
        operation_group.add_argument('-gwbsNWTM', '--generatewbs_NonWBSTypesMapping', required=False,
                                     help='List type mappings and CSS style to use for non non WBS grouping items (like features) in format: <issue_type>=<css_prefix_to_use>{[,<issue_type>=<css_prefix_to_use>]}')
        pass

    @staticmethod
    def parse_arguments(args):
        generate_issues_tree.parse_arguments(args)

        dict = {}
        if hasattr(args, 'generatewbs_NonWBSTypesMapping') and args.generatewbs_NonWBSTypesMapping != None:
            for s in args.generatewbs_NonWBSTypesMapping.split(","):
                splitted = s.split("=")
                if len(splitted) == 2:
                    dict[splitted[0]] = splitted[1]
                # TODO: Add logger
                # else:
                # self.logger.warning("Cannot parse sprint argument %s. Expected to be splitted by '=' in two pieces. Skippng" % s )
        args.generatewbs_NonWBSTypesMapping = dict

        pass

    def __init__(self, iLogger):
        super(generate_wbs,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                op = generate_issues_tree(l)
                resulting_tree = op.execute(container,args)

                nonwbstypesmapping = args.generatewbs_NonWBSTypesMapping

                epiccategoryname=args.generatewbs_EpicCategory
                pertoname=args.generatewbs_PERTO
                pertrname=args.generatewbs_PERTR
                pertpname=args.generatewbs_PERTP
                epiccategoryfield= container.getJIRA().getFieldIDString(epiccategoryname)
                perto_fieldid = container.getJIRA().getFieldIDString(pertoname)
                pertp_fieldid = container.getJIRA().getFieldIDString(pertrname)
                pertrm_fieldid = container.getJIRA().getFieldIDString(pertpname)

                resulting_list = self.issuesToTree(resulting_tree)

                env = Environment()

                templatepath = "%s/../data/%s" % (self.getDataDirectory(),"generate_wbs")
                l.msg("Loading template from path %s" % templatepath)
                loader = FileSystemLoader(templatepath)

                template = loader.load(env,'wbs.jinja2')
                return template.render(
                    param_wbslist=resulting_list,
                    param_serverbase=container.connectionConfig.server,
                    param_nonwbstypesmapping=nonwbstypesmapping,
                    param_epiccategoryfield=epiccategoryfield,
                    param_perto_fieldid=perto_fieldid,
                    param_pertp_fieldid=pertp_fieldid,
                    param_pertrm_fieldid=pertrm_fieldid,
                    param_FBSPathBuilder=FBSPathBuilder()
                )

            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

            #self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)

    def getDataDirectory(selfs):
        return os.path.dirname(os.path.realpath(__file__))

    def issuesToTree(self,tree):
        assert isinstance(tree, tree_type), "Tree shall be tree type"

        list = []

        roots = tree.roots
        for r in roots:
            self.processNode(r,list)

        return list

    def processNode(self,node,list):
        assert isinstance(node, tree_node_type), "Tree node shall be of node type"

        list.append(node)

        #self.expandIssues(node)

        for n in node.children:
            self.processNode(n,list)


    def expandIssues(self,node):
        assert isinstance(node, tree_node_type), "Tree node shall be of node type"
        if isinstance(node.data,EpicExt):
            issuesInEpic = node.data.getIssuesInEpic()
            self.logger.msg("Expanding WBS with %d issues for Epic %s" % ( len(issuesInEpic), node.data.getFieldAsString('summary')) )
            for i in issuesInEpic:
                node.add_child(tree_node_type(i))


class FBSPathBuilder(object):

    def __init__(self,field = 'summary', separator = ' / '):
        self.__separator = separator
        self.__field = field

    def build(self,node_tree):
        assert isinstance(node_tree,tree_node_type)
        assert isinstance(node_tree.data,IssueExt)

        path = ""

        currentparent = node_tree.parent
        while currentparent != None:
            assert isinstance(currentparent, tree_node_type)
            assert isinstance(currentparent.data, IssueExt)
            if path == "":
                path = currentparent.data.getFieldAsString(self.__field)
            else:
                path = "%s%s%s" % (currentparent.data.getFieldAsString(self.__field), self.__separator, path)
            currentparent = currentparent.parent

        if path == "":
            path = node_tree.data.getFieldAsString(self.__field)

        return path