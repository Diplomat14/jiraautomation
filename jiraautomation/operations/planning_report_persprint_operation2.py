from jiraautomation.operations.operation import  basic_operation
from xdev.types.complex.graph import graph_type
from xdev.types.complex.graph import graph_node_type
from xdev.types.complex.graph import graph_link_type
from xdev.types.complex.tree import tree_type
from xdev.types.complex.tree import tree_node_type
from xdev.types.algorithms.graph_to_tree_converter import conversionrules
from xdev.types.algorithms.graph_to_tree_converter import  graph_to_tree_converter
from jiraorm.EpicExt import EpicExt
from .generate_issues_tree import generate_issues_tree

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
        generate_issues_tree.init_arguments(operation_group)
        #operation_group.add_argument('-lbNP', '--listboards_namepart', required=False,
        #                                  help='Part of the name to use as a filter searching for boards')
        pass

    @staticmethod
    def parse_arguments(args):
        generate_issues_tree.parse_arguments(args)
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
                op = generate_issues_tree()
                resulting_tree = op.execute(container,args)

                jsData = print_featuregroups_as_javascript_data(resulting_tree.roots, container, l)


                return jsData

            except Exception as e:
                l.error("Exception happened boards search " + str(e))

            #self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))




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
