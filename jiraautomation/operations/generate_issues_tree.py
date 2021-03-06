from jiraautomation.operations.operation import  basic_operation
from xdev.types.complex.graph import graph_type
from xdev.types.complex.graph import graph_node_type
from xdev.types.complex.graph import graph_link_type
from xdev.types.complex.tree import tree_type
from xdev.types.complex.tree import tree_node_type
from xdev.types.algorithms.graph_to_tree_converter import conversionrules
from xdev.types.algorithms.graph_to_tree_converter import  graph_to_tree_converter

startingnodes = []
root_for_not_processed = None

class generate_issues_tree(basic_operation):

    @staticmethod
    def name():
        return "GenerateIssuesTree"

    @staticmethod
    def init_arguments(operation_group):
        operation_group.add_argument('-rfnpk', '--genisstree_NotProcessedKey', required=False,
                                     help='Root for not processed key')
        operation_group.add_argument('-sntype', '--genisstree_StartNodeType', required=False,
                                     help='Type of starting node')
        operation_group.add_argument('-lkrule', '--genisstree_LinkRule', required=False,
                                     help='Link of rule')
        operation_group.add_argument('-dtoget', '--genisstree_IssueDateToGet', required=False,
                                     help='Desired date to get issue data for')
        operation_group.add_argument('-dsortrules', '--genisstree_SortRules', required=False,
                                     help='Fields and types (asc, desc) by which data should be sorted')
        pass

    @staticmethod
    def parse_arguments(args):
        d = {}
        if hasattr(args,'genisstree_SortRules') and args.genisstree_SortRules != None:
            for s in args.genisstree_SortRules.split(","):
                splitted = s.split("=")
                if len(splitted) == 2:
                    assert splitted[1] in ['asc', 'desc', None], "Invalid value for sort type"
                    d[splitted[0]] = splitted[1]
                else:
                    d[splitted[0]] = ''

        args.genisstree_SortRules = d

    def __init__(self, iLogger):
        super(generate_issues_tree,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                root_for_not_processed_key = args.genisstree_NotProcessedKey
                startingnodestype = args.genisstree_StartNodeType
                linkrule = args.genisstree_LinkRule
                top_request_query = args.query
                sort_rules = args.genisstree_SortRules
                l.msg("Requesting issues by query: %s" % top_request_query)
                if args.genisstree_IssueDateToGet:
                    issues = jira.search_issues_nolim(top_request_query,maxResults=None,expand='changelog,editmeta',date=args.genisstree_IssueDateToGet)
                else:
                    issues = jira.search_issues_nolim(top_request_query,maxResults=None)
                l.msg(str(len(issues)) + " issues found")

                graph = convertissues_to_graph(issues,l,container,root_for_not_processed_key, startingnodestype)
                starting_nodes = getstartingnodes(graph)
                graph_root_for_not_processed_data = get_root_for_not_processed()
                rules = getrules(linkrule)

                l.msg("Outputting graph")
                print_grah(graph, l)

                converter = graph_to_tree_converter(l, issue_to_str, get_value_by_field)
                resulting_tree = converter.convert(graph, starting_nodes, graph_root_for_not_processed_data, rules, sort_rules)

                l.msg("Outputting tree")
                print_tree(resulting_tree, l)

                return resulting_tree

            except Exception as e:
                l.error("Exception happened" + str(e))

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))


#######################################################################################
#######################################################################################
#######################################################################################


def getstartingnodes(graph):
    global startingnodes
    return startingnodes

def get_root_for_not_processed():
    global root_for_not_processed
    return root_for_not_processed

def getrules(linkrule):
    rules = conversionrules()
    rules.add_link_rule(linkrule)

    return rules

#######################################################################################
#######################################################################################
#######################################################################################


def convertissues_to_graph(issues, l, c, root_for_not_processed_key, startingnodestype):
    global root_for_not_processed
    global startingnodes
    l.msg("Starting issues to graph convertion")

    graph = graph_type(l)
    id_to_node_map = {}

    # adding issues themselves
    l.msg("Adding " + str(len(issues)) + " issues")
    for issue in issues:
        issue_id = issue.getField("id")
        l.msg("Processing issue " + issue_to_str(issue))
        issue_node = graph_node_type(issue, l)
        graph.add_node(issue_node)
        id_to_node_map[issue_id] = issue_node
        type = issue.getField('issuetype')
        l.msg("Issue type is " + type.name)
        if type.name == startingnodestype:
            startingnodes.append(issue_node)
        if issue.getField("key") == root_for_not_processed_key:
            root_for_not_processed = issue

    # linking nodes
    l.msg("Adding links")
    for issue in issues:
        l.msg("processing issue " + issue_to_str(issue) + ". Searching its links")
        issue_id = issue.getField("id")
        issue_node = id_to_node_map[issue_id]
        links = issue.getLinks()
        l.msg("   It has " + str(len(links)) + " links")
        for link in links:
            name = link.type.name
            graph_link = graph_link_type(name, link)
            if hasattr(link, 'outwardIssue'):
                o_issue_id = link.outwardIssue.id
                l.msg("   Outward link " + name + " to " + str(link.outwardIssue.key))
                if o_issue_id in id_to_node_map.keys():
                    l.msg("      Adding")
                    graph.add_link(issue_node, id_to_node_map[o_issue_id], graph_link)
                else:
                    l.msg("   Issue was not in an initial select")
            elif hasattr(link, 'inwardIssue'):
                i_issue_id = link.inwardIssue.id
                l.msg("   Inward link " + name + " from " + str(link.inwardIssue.key))
                if i_issue_id in id_to_node_map.keys():
                    graph.add_link(id_to_node_map[i_issue_id], issue_node, graph_link)
                else:
                    l.msg("   Issue was not in an initial select")
            else:
                l.warning("   Unknown link direction")

    l.msg("Issues to graph convertion finished")
    return graph

def issue_to_str(issue):
    return "%s %s " % (str(issue.getField("key")), str(issue.getField("summary")))

def get_value_by_field(issue, field):
    if issue.hasField(field):
        return issue.getFieldAsString(field)
    else:
        Exception(
            ' Field {} for sorting not found for {} node'.format(field, issue))

#######################################################################################
#######################################################################################
#######################################################################################

def print_grah(graph,l):
    assert isinstance(graph, graph_type), "graph of wrong type"
    l.msg("Printing graph")

    nodes = graph.nodes
    l.msg("Nodes (%d):" % len(nodes))
    for n in nodes:
        assert isinstance(n, graph_node_type), "graph node of wrong type"
        l.msg("   " + issue_to_str(n.data))

    links = graph.outlinks
    l.msg("Links:")
    for link_trip in links.keys():
        (from_node,to_node, link) = link_trip
        l.msg("   %s >>> %s | %s" % (issue_to_str(from_node.data), issue_to_str(to_node.data), str(link.name)))


def print_tree(tree_data,l):
    assert isinstance(tree_data, tree_type), "tree_datais of wrong type"
    roots = tree_data.roots
    for root in roots:
        print_tree_node(root, "   ", l)



def print_tree_node(tnode, indent, l):
    assert isinstance(tnode, tree_node_type), "tnode is of wrong type"
    sdata = tnode.data
    if sdata != None:
        name = issue_to_str(sdata)
    else:
        name = "<Empty>"
    l.msg(indent + name)

    if tnode.has_children():
        children = tnode.children
        for child in children:
            print_tree_node(child, indent + "   ", l)
