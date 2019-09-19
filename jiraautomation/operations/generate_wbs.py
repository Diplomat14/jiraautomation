from jiraautomation.operations.operation import  basic_operation
import os
from jinja2.loaders import FileSystemLoader
from jinja2.environment import Environment
from .generate_issues_tree import generate_issues_tree
from xdev.types.complex.tree import tree_type
from xdev.types.complex.tree import tree_node_type
from jiraorm.IssueExt import IssueExt
from jiraorm.EpicExt import EpicExt
from collections.abc import Iterable
import yaml

class generate_wbs(basic_operation):

    @staticmethod
    def name():
        return "GenerateWBS"

    @staticmethod
    def init_arguments(operation_group):
        generate_issues_tree.init_arguments(operation_group)
        operation_group.add_argument('-gwbsEC', '--generatewbs_EpicCategory', required=False, help='Name of the Epic Category Field')
        operation_group.add_argument('-gwbsPERTO', '--generatewbs_PERTO', required=False, help='Name of the PERT Optimistic Field')
        operation_group.add_argument('-gwbsPERTR', '--generatewbs_PERTR', required=False, help='Name of the PERT Realistic Field')
        operation_group.add_argument('-gwbsPERTP', '--generatewbs_PERTP', required=False, help='Name of the PERT Pessimistic Field')
        operation_group.add_argument('-gwbsNWTM', '--generatewbs_NonWBSTypesMapping', required=False,
                                     help='List type mappings and CSS style to use for non non WBS grouping items (like features) in format: <issue_type>=<css_prefix_to_use>{[,<issue_type>=<css_prefix_to_use>]}')
        operation_group.add_argument('-gwbsC2T', '--generatewbs_Component2Teams', required=False,help='Path to YAML file containing dictionary of component : team mapping')
        operation_group.add_argument('-gwbsExpand', '--generatewbs_ExpandIssues', required=False,help='Specify if epics issues shall be expanded to issues')
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

                expandIssues = False
                if args.generatewbs_ExpandIssues is not None:
                    expandIssues = True
                resulting_list = self.issuesToTree(resulting_tree,expandIssues)

                env = Environment()

                templatepath = "%s/../data/%s" % (self.getDataDirectory(),"generate_wbs")
                l.msg("Loading template from path %s" % templatepath)
                loader = FileSystemLoader(templatepath)


                c2tmap = {}
                with open(args.generatewbs_Component2Teams) as f:
                    c2tmap = yaml.load(f, Loader=yaml.CLoader)

                template = loader.load(env,'wbs.jinja2')
                return template.render(
                    param_wbslist=resulting_list,
                    param_serverbase=container.connectionConfig.server,
                    param_nonwbstypesmapping=nonwbstypesmapping,
                    param_epiccategoryfield=epiccategoryfield,
                    param_perto_fieldid=perto_fieldid,
                    param_pertp_fieldid=pertp_fieldid,
                    param_pertrm_fieldid=pertrm_fieldid,
                    param_FBSPathBuilder=FBSPathBuilder(),
                    param_ComponentToDomainConverter=ComponentToDomainConverter(c2tmap)
                )

            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

            #self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)

    def getDataDirectory(selfs):
        return os.path.dirname(os.path.realpath(__file__))

    def issuesToTree(self,tree,expandIssues):
        assert isinstance(tree, tree_type), "Tree shall be tree type"

        list = []

        roots = tree.roots
        for r in roots:
            self.processNode(r,list,expandIssues)

        return list

    def processNode(self,node,list, expandIssues):
        assert isinstance(node, tree_node_type), "Tree node shall be of node type"

        list.append(node)

        if expandIssues == True:
            self.expandIssues(node)

        for n in node.children:
            self.processNode(n,list,expandIssues)


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
        self.__cache = {}

    def build(self,node_tree):
        assert isinstance(node_tree,tree_node_type)
        assert isinstance(node_tree.data,IssueExt)

        if node_tree not in self.__cache:
            parents = []

            currentparent = node_tree.parent
            while currentparent != None:
                assert isinstance(currentparent, tree_node_type)
                assert isinstance(currentparent.data, IssueExt)
                parents.insert(0,currentparent)
                currentparent = currentparent.parent

            path = self.__parentsToString(parents)
            self.__cache[node_tree] = (parents,path)

        return self.__cache[node_tree][1]

    def __parentsToString(self,parents):
        path = ""
        if parents is not None:
            for p in reversed(parents):
                if path == "":
                    path = self.__parentToString(p)
                else:
                    path = "%s%s%s" % (self.__parentToString(p), self.__separator, path)
        return path


    def __parentToString(self,parent):
        return parent.data.getFieldAsString(self.__field)

    def level(self,node_tree):
        if node_tree not in self.__cache:
            self.build(node_tree)

        (parents,path) = self.__cache[node_tree]
        if path == "":
            return 1
        else:
            return path.count(self.__separator)+2

    def parentAsString(self,node_tree,level,all_remaining):
        if node_tree not in self.__cache:
            self.build(node_tree)

        (parents,path) = self.__cache[node_tree]

        if len(parents) == 0:
            return ""
        elif level > len(parents):
            return ""
        else:
            if all_remaining == False:
                return self.__parentToString(parents[level - 1])
            else:
                return self.__parentsToString(parents[level - 1:])

class ComponentToDomainConverter(object):

    def __init__(self,components_map):
        self.__components_map = components_map

    def team(self,components):
        if components is not None and isinstance(components,Iterable):
            for c in components:
                if c.name in self.__components_map:
                    return str(self.__components_map[c.name])
        return ""