from jiraautomation.operations.operation import basic_operation
import re
from .generate_issues_tree import generate_issues_tree
from .generate_wbs import generate_wbs


class generate_custom_jira_structure(basic_operation):

    @staticmethod
    def name():
        return "GenerateCustomJiraStr"

    @staticmethod
    def init_arguments(operation_group):
        generate_wbs.init_arguments(operation_group)
        operation_group.add_argument('-gsPrName', '--generatestruct_ProjName', required=False,
                                     help='Desired project name')
        operation_group.add_argument('-gsAssignee', '--generatestruct_Assignee', required=False,
                                     help='Username for assignee filtering')
        operation_group.add_argument('-gsAssignTypes', '--generatestruct_TypeForAssign', required=False,
                                     help='Types that should be assign')
        operation_group.add_argument('-gsSumFilt', '--generatestruct_SummaryFilter', required=False,
                                     help='Expression for summary checking and filtering')
        pass

    @staticmethod
    def parse_arguments(args):
        generate_wbs.parse_arguments(args)
        return args

    def __init__(self, iLogger):
        super(generate_custom_jira_structure, self).__init__(iLogger)

    def execute(self, container, args):
        l = self.logger

        try:
            jira = container.getJIRA()
            try:

                op = generate_issues_tree(l)
                resulting_tree = op.execute(container, args)
                issues = self.issuesToTree(resulting_tree, l, args)
                assignees = get_all_assignee_by_filter(jira, args.generatestruct_ProjName,
                                                        args.generatestruct_Assignee)
                for i in issues:
                    check_if_issue_assign_to_specified(i, l, assignees, args)

                op2 = generate_wbs(l, issues)
                jira_structure = op2.execute(container, args)
                return jira_structure


            except Exception as e:
                l.error("Exception happened boards search " + str(e))

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))

    def issuesToTree(self, tree, l, args):
        issues_list = list()
        roots = tree.roots
        epics = get_all_arhud_epics(roots, args)
        for r in epics:
            check_if_depends_issues_exist(r, l, args)
            self.processNode(r, issues_list, l, args)
        return issues_list

    def processNode(self, node, node_list, l, args):
        node_list.append(node)
        for n in node.children:
            if get_child(n, l, args):
                self.processNode(n, node_list, l, args)


def get_all_arhud_epics(issues, args):
    for issue in issues:
        if re.search(args.generatestruct_SummaryFilter.split(' ')[0], issue.data.original.fields.summary):
            yield issue


def get_all_assignee_by_filter(jira, project_key, username, start=0, limit=50):
    assignees = list()
    url = 'user/assignable/search?project={project_key}&username={username}&startAt={start}&maxResults={limit}'.format(
        project_key=project_key,
        username=username,
        start=start,
        limit=limit)
    assignees_list = jira._get_json(url)
    for assignee in assignees_list:
        assignees.append(assignee['key'])
    return assignees


def modified_issues_summary(issue):
    summary = issue.data.original.fields.summary.split("] ")
    issue.data.original.fields.summary = summary[-1]
    return issue


def get_child(child, l, args):
    if re.search(args.generatestruct_SummaryFilter, child.data.original.fields.summary):
        return child
    elif re.search(' '.join(args.generatestruct_SummaryFilter.split(' ', 2)[:2]), child.data.original.fields.summary):
        l.error("{} task is not impl type".format(child.data.original.key))


def check_if_issue_assign_to_specified(issue, l, assignees, args):
    if issue.data.getFieldAsString('issuetype') in args.generatestruct_TypeForAssign:
        if issue.data.getFieldAsString('assignee') not in assignees:
            l.error("Wrong assignee in {}".format(issue.data.getFieldAsString('key')))


def check_if_depends_issues_exist(issue, l, args):
    links = issue.data.original.fields.issuelinks
    for link in links:
        if link.type.name != args.genisstree_LinkRule:
            linked_issue = link.inwardIssue if hasattr(link, 'inwardIssue') else link.outwardIssue
            l.error("Issue {} contains linked issue {} that potentially might be required to sync ".format(
                issue.data.original.key, linked_issue.key))
