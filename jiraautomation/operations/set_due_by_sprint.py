from jiraautomation.operations.operation import  basic_operation


class set_due_by_sprint(basic_operation):

    @staticmethod
    def name():
        return "SetDueBySprint"

    @staticmethod
    def init_arguments(operation_group):
        operation_group.add_argument('-sdbsS', '--sdbs_sprints', required=False,
                                          help='List of end dates for sprints in format: <sprint_name>=<end_date>{[,<sprint_name>=<end_date>]}')
        pass

    @staticmethod
    def parse_arguments(args):
        dict = {}
        if hasattr(args,'sdbs_sprints') and args.sdbs_sprints != None:
            for s in args.sdbs_sprints.split(","):
                splitted = s.split("=")
                if len(splitted)==2:
                    dict[splitted[0]] = splitted[1]
                # TODO: Add logger
                #else:
                    #self.logger.warning("Cannot parse sprint argument %s. Expected to be splitted by '=' in two pieces. Skippng" % s )
        args.sdbs_sprints = dict

    def __init__(self, iLogger):
        super(set_due_by_sprint,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                l.msg("Requesting issues by JQL: %s" % args.query)
                issues = jira.search_issues_nolim(args.query)
                l.msg("Found %d issues" % len(issues))

                for i in issues:
                    l.msg("Processing issue %s" % self.issue_to_str(i))
                    sprint = i.getLastSprint()
                    l.msg("   Sprint is %s. Current due date is %s" % (sprint.name, str(i.getField('duedate'))))
                    if hasattr(sprint.original,'endDate') and sprint.original.endDate != None:
                        l.msg("   Setting due date as %s" % sprint.original.endDate)
                        i.setField('duedate',sprint.original.endDate)
                    else:
                        if sprint.name in args.sdbs_sprints:
                            l.msg("   Setting due date as %s" % args.sdbs_sprints[sprint.name])
                            i.setField('duedate', args.sdbs_sprints[sprint.name])
                        else:
                            l.warning("   End date of sprint %s is not set" % sprint.name)

            except Exception as e:
                l.error("Exception happened boards search " + str(e))
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))

    def issue_to_str(self,issue):
        return "%s %s " % (str(issue.getField("key")), str(issue.getField("summary")))