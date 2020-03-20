from jiraautomation.operations.operation import basic_operation
import os
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
        # generate_issues_tree.init_arguments(operation_group)
        operation_group.add_argument('-gwbsEC', '--generatewbs_EpicCategory', required=False,
                                     help='Name of the Epic Category Field')
        operation_group.add_argument('-gwbsPERTO', '--generatewbs_PERTO', required=False,
                                     help='Name of the PERT Optimistic Field')
        operation_group.add_argument('-gwbsPERTR', '--generatewbs_PERTR', required=False,
                                     help='Name of the PERT Realistic Field')
        operation_group.add_argument('-gwbsPERTP', '--generatewbs_PERTP', required=False,
                                     help='Name of the PERT Pessimistic Field')
        operation_group.add_argument('-gwbsNWTM', '--generatewbs_NonWBSTypesMapping', required=False,
                                     help='List type mappings and CSS style to use for non non WBS grouping items (like features) in format: <issue_type>=<css_prefix_to_use>{[,<issue_type>=<css_prefix_to_use>]}')
        operation_group.add_argument('-gwbsC2T', '--generatewbs_Component2Teams', required=False,
                                     help='Path to YAML file containing dictionary of component : team mapping')
        operation_group.add_argument('-gwbsExpand', '--generatewbs_ExpandIssues', required=False,
                                     help='Specify if epics issues shall be expanded to issues')
        operation_group.add_argument('-gwbswt', '--generatewbs_WBSTypes', required=False,
                                     help='Types that could possibly be shown in FBS Level 4+')
        operation_group.add_argument('-gwbsCUSTLINK', '--generatewbs_CustJiraLink', required=False,
                                     help='Name of the Customer Link Field ')
        pass

    @staticmethod
    def parse_arguments(args):
        generate_issues_tree.parse_arguments(args)
        # generate_issues_tree.parse_arguments(args)
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

    def __init__(self, iLogger, tree=None):
        super(generate_wbs, self).__init__(iLogger)
        self.tree=tree

    def execute(self, container, args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                # Reading and preparing data from command line parameters
                nonwbstypesmapping = args.generatewbs_NonWBSTypesMapping
                epiccategoryfield = args.generatewbs_EpicCategory if hasattr(args, 'generatewbs_EpicCategory') else None
                perto_field_name = args.generatewbs_PERTO if hasattr(args, 'generatewbs_PERTO') else None
                pertp_field_name = args.generatewbs_PERTP if hasattr(args, 'generatewbs_PERTO') else None
                pertrm_field_name = args.generatewbs_PERTR if hasattr(args, 'generatewbs_PERTO') else None
                custjiralink_field_name = args.generatewbs_CustJiraLink if hasattr(args, 'generatewbs_CustJiraLink') else None

                with open(args.generatewbs_Component2Teams) as f:
                    c2tmap = yaml.load(f, Loader=yaml.Loader)

                # Generating hierarchy tree
                if self.tree is None:
                    op = generate_issues_tree(l)
                    resulting_tree = op.execute(container, args)

                    # Collapsing hierarchy tree to a list
                    expandIssues = False
                    if args.generatewbs_ExpandIssues is not None:
                        expandIssues = True
                    issues_list = self.issuesToTree(resulting_tree, expandIssues)
                else:
                    issues_list = self.tree

                entry_list = list()
                fbspathbuilder = FBSPathBuilder(args.generatewbs_WBSTypes)
                c2tconverter = ComponentToDomainConverter(c2tmap)
                for issue in issues_list:
                    entry_list.append(
                        WBS_Entry(issue, perto_field_name, pertrm_field_name, pertp_field_name, epiccategoryfield, c2tconverter,
                                  nonwbstypesmapping,fbspathbuilder,custjiralink_field_name))
                return entry_list

            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

            # self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)

    def getDataDirectory(selfs):
        return os.path.dirname(os.path.realpath(__file__))

    def issuesToTree(self, tree, expandIssues):
        assert isinstance(tree, tree_type), "Tree shall be tree type"

        list = []

        roots = tree.roots
        for r in roots:
            self.processNode(r, list, expandIssues)

        return list

    def processNode(self, node, list, expandIssues):
        assert isinstance(node, tree_node_type), "Tree node shall be of node type"

        list.append(node)

        if expandIssues == True:
            self.expandIssues(node)

        for n in node.children:
            self.processNode(n, list, expandIssues)

    def expandIssues(self, node):
        assert isinstance(node, tree_node_type), "Tree node shall be of node type"
        if isinstance(node.data, EpicExt):
            issuesInEpic = node.data.getIssuesInEpic()
            self.logger.msg(
                "Expanding WBS with %d issues for Epic %s" % (len(issuesInEpic), node.data.getFieldAsString('summary')))
            for i in issuesInEpic:
                node.add_child(tree_node_type(i))


class FBSPathBuilder(object):

    def __init__(self, wbs_types, field='summary', separator=' / '):
        self.__separator = separator
        self.__wbs_types = wbs_types
        self.__field = field
        self.__cache = {}

    def build(self, node_tree, cust_field):
        assert isinstance(node_tree, tree_node_type)
        #assert isinstance(node_tree.data, IssueExt)

        if node_tree not in self.__cache:
            parents = []

            currentparent = node_tree.parent

            while currentparent != None:
                assert isinstance(currentparent, tree_node_type)
                #assert isinstance(currentparent.data, IssueExt)
                parents.insert(0, currentparent)
                currentparent = currentparent.parent
            else:
                if cust_field:
                    parents.append(node_tree)


            path = self.__parentsToString(parents)
            self.__cache[node_tree] = (parents, path)

        return self.__cache[node_tree][1]


    def __parentsToString(self, parents):
        path = ""
        if parents is not None:
            for p in reversed(parents):
                if path == "":
                    path = self.__parentToString(p)
                else:
                    path = "%s%s%s" % (self.__parentToString(p), self.__separator, path)
        return path

    def __parentToString(self, parent):
        return parent.data.getFieldAsString(self.__field) if parent.data.getFieldAsString(
            'issuetype') in self.__wbs_types.split(',') else ""

    def __parentNode(self, parent):
        return parent.data if parent.data.getFieldAsString(
            'issuetype') in self.__wbs_types.split(',') else ""

    def level(self, node_tree, custom_field):
        if node_tree not in self.__cache:
            self.build(node_tree, custom_field)

        (parents, path) = self.__cache[node_tree]
        if path == "":
            return 1
        else:
            return path.count(self.__separator) + 2

    def parentAsString(self, node_tree, level, all_remaining, custom_field=False):
        if node_tree not in self.__cache:
            self.build(node_tree, custom_field)

        (parents, path) = self.__cache[node_tree]

        if len(parents) == 0:
            return ""
        elif level > len(parents):
            return ""
        else:
            if all_remaining == False:
                if custom_field:
                    return self.__parentNode(parents[level - 1])
                else:
                    return self.__parentToString(parents[level - 1])
            else:

                return self.__parentsToString(parents[level - 1:])


class WBS_Entry(object):
    def __init__(self, tree_node, perto_fieldid, pertrm_fieldid, pertp_fieldid, epiccategoryfield, c2dconverter,
                 nonwbstypesmapping, fbspathbuilder, custjiralink_field_name):
        self.__tree_node = tree_node
        self.__perto_fieldid = perto_fieldid
        self.__pertrm_fieldid = pertrm_fieldid
        self.__pertp_fieldid = pertp_fieldid
        self.__epiccategoryfield = epiccategoryfield
        self.__nonwbstypesmapping = nonwbstypesmapping
        self.__fbspathbuilder = fbspathbuilder
        self.__c2dconverter = c2dconverter
        self.__custjiralink_field = custjiralink_field_name

    def __eq__(self, other):
        return self.summary == other.summary

    @property
    def perto(self):
        if self.__tree_node.data != None:
            po = self.__tree_node.data.getFieldAsString(self.__perto_fieldid)
            return float(po) if po is not "" else None
        else:
            return None

    @property
    def pertrm(self):
        if self.__tree_node.data != None:
            pr = self.__tree_node.data.getFieldAsString(self.__pertrm_fieldid)
            return float(pr) if pr is not "" else None
        else:
            return None

    @property
    def pertp(self):
        if self.__tree_node.data != None:
            pp = self.__tree_node.data.getFieldAsString(self.__pertp_fieldid)
            return float(pp) if pp is not "" else None
        else:
            return None

    @property
    def pert_calculated(self):
        if self.perto is not None and self.pertrm is not None and self.pertp is not None:
            return (self.perto+(self.pertrm*4)+self.pertp)/6
        else:
            return None

    @property
    def epic_category(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString(self.__epiccategoryfield)
        else:
            return None

    @property
    def assignee(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('assignee')
        else:
            return None

    @property
    def components(self):
        if self.__tree_node.data != None:
            comps = self.__tree_node.data.getField('components')
            return ", ".join(c.name for c in comps) if isinstance(comps, Iterable) else ""
        else:
            return None

    @property
    def description(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('description')
        else:
            return None

    @property
    def issuetype(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('issuetype')
        else:
            return None

    @property
    def key(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('key')
        else:
            return None

    @property
    def lastsprint(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('lastsprint')
        else:
            return None

    @property
    def firstsprint(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('firstsprint')
        else:
            return None

    @property
    def sprints(self):
        if self.__tree_node.data != None:
            all_sprints = self.__tree_node.data.getField('sprints')
            return ", ".join(c.name for c in all_sprints) if isinstance(all_sprints, Iterable) else ""
        else:
            return None

    @property
    def status(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('status')
        else:
            return None

    @property
    def summary(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getFieldAsString('summary')
        else:
            return None

    @property
    # In seconds
    def timeestimate(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getField('timeestimate')
        else:
            return None

    @property
    # In seconds
    def timespent(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getField('timespent')
        else:
            return None

    @property
    # In seconds
    def original(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getField('timeoriginalestimate')
        else:
            return None

    def team(self, components):
        if self.__tree_node.data != None:
            return self.__c2dconverter.team(components)
        else:
            return None

    @property
    def path_builder_level(self):
        if self.__tree_node.data != None:
            return self.__fbspathbuilder.level(self.__tree_node, False)
        else:
            return None

    @property
    def path_builder_build(self):
        if self.__tree_node.data != None:
            return self.__fbspathbuilder.build(self.__tree_node, False)
        else:
            return None

    @property
    def path_builder_first(self):
        if self.__tree_node.data != None:
            return self.__fbspathbuilder.parentAsString(self.__tree_node, 1, False)
        else:
            return None

    @property
    def path_builder_second(self):
        return self.__fbspathbuilder.parentAsString(self.__tree_node, 2, False)

    @property
    def path_builder_third(self):
        return self.__fbspathbuilder.parentAsString(self.__tree_node, 3, False)

    @property
    def path_builder_fourth(self, includeNextLevels = True ):
        return self.__fbspathbuilder.parentAsString(self.__tree_node, 4, includeNextLevels)

    @property
    def non_wbstypes_mapping(self):
        return self.__nonwbstypesmapping

    @property
    def parent_id(self):
        if self.__tree_node.data != None and self.__tree_node.parent.data:
            return self.__tree_node.parent.data.getFieldAsString('key')
        else:
            return None

    @property
    def custjiralink_field(self):
        if self.__tree_node.data != None:
            return self.__tree_node.data.getField(self.__custjiralink_field)
        else:
            return None


class ComponentToDomainConverter(object):

    def __init__(self, components_map):
        self.__components_map = dict((v, k) for k in components_map for v in components_map[k])

    def team(self, components):
        if components is not None:
            for c in components.split():
                if c in self.__components_map:
                    return str(self.__components_map[c])

        return ""