from jiraautomation.operations.operation import  basic_operation
from xdev.types.complex.graph import graph_type
from xdev.types.complex.graph import graph_node_type
from xdev.types.complex.graph import graph_link_type
from xdev.types.complex.tree import tree_type
from xdev.types.complex.tree import tree_node_type
from xdev.types.algorithms.graph_to_tree_converter import conversionrules
from xdev.types.algorithms.graph_to_tree_converter import  graph_to_tree_converter
from jiraorm.EpicExt import EpicExt

startingnodes = []
root_for_not_processed_key = "ARCREATOR-6205"
root_for_not_processed = None
startingnodestype = "Feature Group"
linkrule = "Consists of"

class planning_report_persprint_operation2(basic_operation):

    @staticmethod
    def name():
        return "PlanningReportPerSprint2"

    @staticmethod
    def init_arguments(operation_group):
        #operation_group.add_argument('-lbNP', '--listboards_namepart', required=False,
        #                                  help='Part of the name to use as a filter searching for boards')
        pass

    @staticmethod
    def parse_arguments(args):
        # You might want to prepare arguments somehow like:
        # args.operation = CoreOperation[args.operation]
        pass

    def __init__(self, iLogger):
        super(planning_report_persprint_operation2,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                top_request_query = args.query
                issues = jira.search_issues_nolim(top_request_query,maxResults=None)
                l.msg(str(len(issues)) + " issues found")

                graph = convertissues_to_graph(issues,l,container)
                starting_nodes = getstartingnodes(graph)
                graph_root_for_not_processed_data = get_root_for_not_processed()
                rules = getrules()

                l.msg("Outputting graph")
                print_grah(graph, l)

                converter = graph_to_tree_converter(l, issue_to_str)
                resulting_tree = converter.convert(graph, starting_nodes, graph_root_for_not_processed_data, rules)

                l.msg("Outputting tree")
                print_tree(resulting_tree, l)


                jsData = print_featuregroups_as_javascript_data(resulting_tree.roots, container, l)


                return jsData

            except Exception as e:
                l.error("Exception happened boards search " + str(e))

            #self.persistContainer()
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

def getrules():
    global linkrule
    rules = conversionrules()
    rules.add_link_rule(linkrule)

    return rules

#######################################################################################
#######################################################################################
#######################################################################################


def convertissues_to_graph(issues, l, c):
    global root_for_not_processed
    global startingnodes
    global startingnodestype

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

    return graph

def issue_to_str(issue):
    return "%s %s " % (str(issue.getField("key")), str(issue.getField("summary")))

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
    name = issue_to_str(sdata)
    l.msg(indent + name)

    if tnode.has_children():
        children = tnode.children
        for child in children:
            print_tree_node(child, indent + "   ", l)



#######################################################################################
#######################################################################################
#######################################################################################

def print_featuregroups_as_javascript_data(featuregroup_tree_nodes, container, logger):
    global linkrule

    fields=['id','summary','key','issuetype','status']
    arrayName = 'data'
    linkName = linkrule
    linkInward = False

    jsString = ""
    jsTreeString = ""
    jsSprintsString = "var involvedSprints = {};\n"


    involvedSprints = []
    unique_id = 1
    fgidx = 1
    for fg_tree_node in featuregroup_tree_nodes:
        assert isinstance(fg_tree_node,tree_node_type), "feature groups list shall contain items of tree node type"
        fg = fg_tree_node.data
        logger.msg('Processing feature group [%s] %s (%d/%d)' % (str(fg.getField('key')),str(fg.getField('summary')),fgidx,len(featuregroup_tree_nodes)))
        fgidx += 1

        jsTreeString += print_issue_as_javascript_data(fg,fields,
                                                               {'id':unique_id},
                                                               arrayName)
        unique_id +=1
        hlfs = fg_tree_node.children
        hlfidx = 1
        for hlf_tree_node in hlfs:
            assert isinstance(hlf_tree_node, tree_node_type), "children of tree node shall be of tree node type"
            hlf = hlf_tree_node.data
            logger.msg('Processing HLF [%s] %s (%d/%d)' % (str(hlf.getField('key')),str(hlf.getField('summary')),hlfidx,len(hlfs)))
            hlfidx += 1
            jsTreeString += print_issue_as_javascript_data(hlf,fields,
                                                               {'fg':fg.getField('id'), 'id':unique_id},
                                                               arrayName)
            unique_id +=1
            features = hlf_tree_node.children
            fidx = 1
            for f_tree_node in features:
                assert isinstance(f_tree_node, tree_node_type), "children of tree node shall be of tree node type"
                f = f_tree_node.data
                logger.msg('Processing feature [%s] %s (%d/%d)' % (str(f.getField('key')),str(f.getField('summary')),fidx,len(features)))
                fidx += 1
                jsTreeString += print_issue_as_javascript_data(f,fields,
                                                               {'fg':fg.getField('id'),'hlf':hlf.getField('id'), 'id':unique_id},
                                                               arrayName)
                unique_id +=1
                epics = f_tree_node.children
                for epic_tree_node in epics:
                    assert isinstance(epic_tree_node, tree_node_type), "children of tree node shall be of tree node type"
                    epic = epic_tree_node.data
                    logger.msg('Processing epic [%s] %s %s' % (str(epic.getField('key')),str(epic.getField('issuetype')),str(epic.getField('summary'))))
                    issuesbysprint = {}
                    if isinstance(epic,EpicExt) == True:
                        issuesbysprint = get_epic_issues_by_sprint(epic,logger)
                    jsString += print_issue_as_javascript_data(epic,fields,
                                                               {'fg':fg.getField('id'),'hlf':hlf.getField('id'),'f':f.getField('id'), 'id':unique_id, 'sprint_tasks':issuesbysprint},
                                                               arrayName)
                    unique_id +=1
                    for sprid, issues in issuesbysprint.items():
                        if sprid not in involvedSprints:
                            sprname = container.getSprintById(sprid).name if sprid >= 0 else ""
                            jsSprintsString += "involvedSprints[%s] = \"%s\";\n" % (str(sprid),str(sprname))
                            involvedSprints.append(sprid)
                        for issue in issues:
                            jsString += print_issue_as_javascript_data(issue, fields,
                                                                   {'fg': fg.getField('id'), 'hlf': hlf.getField('id'),
                                                                    'f': f.getField('id'), 'id': unique_id, 'epic': epic.getField('id')},
                                                                   arrayName)
                            unique_id += 1


    return "var " + arrayName + " = [];\n" + jsTreeString + jsString + "\n" + jsSprintsString

def get_epic_issues_by_sprint(epic,logger):
    issues = epic.getIssuesInEpic()
    iPerSprint = {}
    iPerSprint[-1] = [] # no sprint
    for i in issues:
        sprint = i.getLastSprint()
        if sprint == None:
            sId = -1
        else:
            sId = sprint.original.id

        if sId not in iPerSprint:
            iPerSprint[sId] = []
        iPerSprint[sId].append(i)

    return iPerSprint

def escape_string(raw):
    s = str(raw)
    return s.translate(s.maketrans({'"':  r'\"'}))

def print_issue_as_javascript_data(issue,fields, extraFields, arrayName:str):
    jsString = ""

    jsString += '%s.push({' % arrayName

    for f in fields:
        if issue.hasField(f):
            if f != "id":
                jsString += '%s:"%s",' % (escape_string(f), escape_string(issue.getFieldAsString(f)))
            else:
                jsString += '%s_original:"%s",' % (escape_string(f), escape_string(issue.getFieldAsString(f)))
        else:
            print('Field %s not found' % f)

    for fn, fv in extraFields.items():
        if fn == "sprint_tasks":
            txt = "{"
            for sid, sissues in fv.items():
                txt += "'%d':[" % sid
                for issue in sissues:
                    txt += "%s," % escape_string(issue.getFieldAsString('id'))
                txt += "],"
            txt += "}"
            jsString += '%s:%s,' % (escape_string(fn), txt)
        else:
            jsString += '%s:"%s",' % (escape_string(fn), escape_string(fv))

    jsString += "});\n"

    return jsString
