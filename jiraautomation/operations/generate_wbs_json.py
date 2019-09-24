from jiraautomation.operations.operation import basic_operation
from .generate_wbs import generate_wbs
import json


class generate_wbs_json(basic_operation):

    @staticmethod
    def name():
        return "GenerateWBSJson"

    @staticmethod
    def init_arguments(operation_group):
        pass

    @staticmethod
    def parse_arguments(args):
        pass

    def __init__(self, iLogger):
        super(generate_wbs_json, self).__init__(iLogger)

    def execute(self, container, args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                op = generate_wbs(l)
                param = op.execute(container, args)

                to_json = list()
                for d in param:
                    keys = ["Type", "ID", "Status", "FBS Level", "FBS Path", "FBS Level 1", "FBS Level 2",
                             "FBS Level 3", "FBS Level 4+", "FBS/WBS Title", "LOM Relation", "Team", "Components",
                             "Description", "PERT Opt", "PERT Real", "PERT Pess", "PERT Estimation (calculated)",
                             "Original est.", "Sprint", "Assignee", "Spent time", "Remaining est."]

                    values = [d.issuetype, d.key, d.status, d.path_builder_level, d.path_builder_build,
                           d.path_builder_first, d.path_builder_second, d.path_builder_third, d.path_builder_fourth,
                           d.summary, d.epic_category, d.team(d.components), d.components,
                           d.description, d.perto, d.pertrm, d.pertp, d.pert_calculated,
                           d.original, d.lastsprint, d.assignee, d.timespent, d.timeestimate]

                    d = dict(zip(keys, values))
                    to_json.append(d)

                return json.dumps(to_json)

            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)

    def serialize(self, obj):
        return obj.__dict__

    def to_json(self, data):
        """Converts object to JSON formatted string"""
        return json.dumps(data)
