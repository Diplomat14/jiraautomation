from jiraautomation.operations.operation import basic_operation
from jiraautomation.operations.generate_wbs import generate_wbs, WBS_Entry
from arcjiraautomation.operations.generate_excel import generate_excel
from arcjiraautomation.operations.FROP_config import get_loms_values, create_hyperlink, create_jira_url, \
    fields_mapping


class generate_FROP_by_lom(basic_operation):

    @staticmethod
    def name():
        return "GenerateFROPbyLOM"

    @staticmethod
    def init_arguments(operation_group):
        generate_wbs.init_arguments(operation_group)
        operation_group.add_argument('-gfropLOMs', '--generatefrop_LOMs', required=False,
                                     help='Path to YAML file containing dictionary of loms')
        operation_group.add_argument('-gfropStatuses', '--generatefrop_Statuses', required=False,
                                     help='Path to YAML file containing dictionary of statuses')
        operation_group.add_argument('-gfropLevels', '--generatefrop_LevelsQuantity', required=False,
                                     help='Quantity of lvl to generate')
        operation_group.add_argument('-gfropLvlNames', '--generatefrop_LevelsNames', required=False,
                                     help='List of level column names')
        operation_group.add_argument('-gfropAddColumns', '--generatefrop_AdditionalColumns', required=False,
                                     help='List of additional column names')

    @staticmethod
    def parse_arguments(args):
        generate_wbs.parse_arguments(args)
        pass

    def __init__(self, iLogger):
        super(generate_FROP_by_lom, self).__init__(iLogger)

    def execute(self, container, args):
        l = self.logger

        try:

            try:
                server = container.connectionConfig.server
                loms = args.generatefrop_LOMs if args.generatefrop_LOMs else {}
                statuses = args.generatefrop_Statuses if args.generatefrop_Statuses else {}
                lvl_names = args.generatefrop_LevelsNames.split(',') if args.generatefrop_LevelsNames else None

                op = generate_wbs(l)
                obj_list = op.execute(container, args)

                attributes = list(loms.keys())
                level = int(args.generatefrop_LevelsQuantity)
                lvl_names = [lvl.strip() for lvl in lvl_names if lvl_names]
                clms = args.generatefrop_AdditionalColumns.split(',') if args.generatefrop_AdditionalColumns else []

                columns = list()
                for clm in clms:
                    clm = clm.strip()
                    if not fields_mapping.get(clm):
                        l.error('Unknown column value: {}'.format(clm))
                    else:
                        columns.append(clm)

                issues = [FROP_Entry(issue, attributes) for issue in obj_list]

                l.msg("Generating FROP report")
                FROP = create_FROP_by_lom(issues, loms, statuses, server, level, lvl_names, columns)

                op3 = generate_excel(l, FROP, 'FROP (Eng view)', 1)
                return op3.execute(container, args)

            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)


class FROP_Entry(WBS_Entry):
    """
        Class extends WBS Entry with loms
    """

    def __init__(self, parent_instance, loms):
        super().__init__(*tuple(parent_instance.__dict__.values()))

        for lom in loms:
            issue = list(parent_instance.__dict__.values())[0].data
            value = issue.getCustomField(lom)
            setattr(self, lom, value)

    def __hash__(self):
        return hash(id(self))

    def __eq__(self, x):
        return x is self


def create_FROP_by_lom(obj_list, loms, statuses, server, level, lvl_names, columns):
    """
        Function creates FROP report by loms
    """

    FROP = list()

    for issue in obj_list:
        if issue.path_builder_level <= level:
            lvl_data = get_levels_data(issue, lvl_names, level, server)
            columns_data = additional_columns_data(issue, columns, statuses)
            loms_data = get_loms_data(issue, loms)

            data = {**lvl_data, **columns_data, **loms_data}
            FROP.append(data)

    return FROP


def additional_columns_data(issue, columns, statuses):
    values = [fields_mapping[column](issue, statuses) for column in columns]
    column_data = dict(zip(columns, values))

    return column_data


def get_loms_data(issue, loms):
    values = get_loms_values(issue, loms)
    loms_data = dict(zip(loms.values(), values))

    return loms_data


def get_levels_data(issue, lvl_columns, level, server):
    values = [value.strip() for value in issue.path_builder_build.split('/')]
    if len(values) < level:
        values.extend([''] * (level - len(values)))

    values[issue.path_builder_level - 1] = issue.summary

    if issue.path_builder_level == level:
        url = create_jira_url(server, issue.key)
        values[level - 1] = create_hyperlink(url, issue.summary.strip())

    level_data = dict(zip(lvl_columns, values))
    return level_data
