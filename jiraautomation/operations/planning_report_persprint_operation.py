from jiraautomation.operations.operation import  basic_operation
from jiraorm.EpicExt import EpicExt

class planning_report_persprint_operation(basic_operation):

    @staticmethod
    def name():
        return "PlanningReportPerSprint"

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
        super(planning_report_persprint_operation,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                top_request_query = args.query
                #top_request_query = 'project = %s AND issuetype = "%s" ORDER BY updated DESC' % (projectId, topIssueType)
                issues = jira.search_issues_nolim(top_request_query)
                l.msg(str(len(issues)) + " issues found")

                jsData = print_featuregroups_as_javascript_data(issues,container,l)

                return jsData

            except Exception as e:
                l.error("Exception happened boards search " + str(e))

            #self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))


def print_featuregroups_as_javascript_data(featuregroups,container,logger):
    fields=['id','summary','key','issuetype','status','timeestimate','timespent','timeoriginalestimate']
    arrayName = 'data'
    linkName = 'Consists of'
    linkInward = False

    jsString = ""
    jsTreeString = ""
    jsSprintsString = "var involvedSprints = {};\n"


    involvedSprints = []
    unique_id = 1
    for fgidx, fg in enumerate(featuregroups):
        logger.msg('Processing feature group [%s] %s (%d/%d)' % (str(fg.getField('key')),str(fg.getField('summary')),fgidx,len(featuregroups)))
        jsTreeString += print_issue_as_javascript_data(fg,fields,
                                                               {'id':unique_id},
                                                               arrayName)
        unique_id +=1
        hlfs = fg.getChildren(linkName,linkInward)
        for hlfidx, hlf in enumerate(hlfs):
            logger.msg('Processing HLF [%s] %s (%d/%d)' % (str(hlf.getField('key')),str(hlf.getField('summary')),hlfidx,len(hlfs)))
            jsTreeString += print_issue_as_javascript_data(hlf,fields,
                                                               {'fg':fg.getField('id'), 'id':unique_id},
                                                               arrayName)
            unique_id +=1
            features = hlf.getChildren(linkName,linkInward)
            for fidx, f in enumerate(features):
                logger.msg('Processing feature [%s] %s (%d/%d)' % (str(f.getField('key')),str(f.getField('summary')),fidx,len(features)))
                jsTreeString += print_issue_as_javascript_data(f,fields,
                                                               {'fg':fg.getField('id'),'hlf':hlf.getField('id'), 'id':unique_id},
                                                               arrayName)
                unique_id +=1
                epics = f.getChildren(linkName,linkInward)
                for epic in epics:
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
