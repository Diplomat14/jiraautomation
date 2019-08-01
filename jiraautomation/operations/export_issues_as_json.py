from jiraautomation.operations.operation import  basic_operation
from jiraorm.IssueExt import IssueExt
import json

class export_issues_as_json(basic_operation):

    @staticmethod
    def name():
        return "ExportIssuesAsJson"

    @staticmethod
    def init_arguments(operation_group):
        #operation_group.add_argument('-ej', '--listboards_namepart', required=False,
        #                                  help='Part of the name to use as a filter searching for boards')
        pass

    @staticmethod
    def parse_arguments(args):
        # You might want to prepare arguments somehow like:
        # args.operation = CoreOperation[args.operation]
        pass

    def __init__(self, iLogger):
        super(export_issues_as_json,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                request_query = args.query
                fields = args.fields
                #top_request_query = 'project = %s AND issuetype = "%s" ORDER BY updated DESC' % (projectId, topIssueType)
                issues = jira.search_issues_nolim(request_query)
                l.msg(str(len(issues)) + " issues found")

                json = self.issues_to_json(issues,fields)

                return json

            except Exception as e:
                l.error("Exception happened boards search " + str(e))

            #self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))


    def issues_to_json(self,issues,fields):
        assert isinstance(fields, list), "fields shall be a list of strings"

        issues_dicts = []

        self.logger.msg('Converting %d issues to json' % len(issues))
        for i in issues:
            assert isinstance(i, IssueExt), "issues in the list are of wrong type"
            issues_dicts.append(self.issue_to_dict(i,fields))

        return json.dumps(issues_dicts)

    def issue_to_dict(self,issue,fields):
        assert isinstance(issue, IssueExt), "issues in the list are of wrong type"
        issue_dict = {}

        for field in fields:
            if issue.hasField(field):
                # TODO: Process complex objects
                issue_dict[field] = str(issue.getField(field))
            else:
                self.logger.warning('Issue has no field %s' % field)

        return issue_dict