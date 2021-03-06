from datetime import datetime
from jiraorm.EpicExt import EpicExt


class DependencyAnalyzer:

    def __init__(self, l, tree_node):
        self.__logger = l
        self.__tree_node = tree_node

    def ascend(self, node):
        return node.parent

    def analyze_dependency(self, node, dates):
        parent = self.ascend(node)

        if not parent:
            return None

        if not parent.data:
            return None

        parent_d_field, child_d_field = dates.parent_date_field, dates.child_date_field
        if not parent.data.getField(parent_d_field):
            self.analyze_dependency(parent, dates)
        else:
            if self.__tree_node.data:
                child_date = dates.get_date(self.__tree_node.data.getField(child_d_field))
                parent_date = dates.get_date(parent.data.getField(parent_d_field))
                if child_date and parent_date:
                    if child_date > parent_date:
                        return 'Overdue'
                    elif child_date == parent_date:
                        return 'Due date approaching'

            return None

    def analyze_critical_path(self, connection_type, dates):
        val = None

        if self.__tree_node and isinstance(self.__tree_node.data, EpicExt):
            depend_issues = self.__tree_node.data.getChildren(connection_type, True)
            issue_date = dates.get_date(
                self.__tree_node.data.getField(dates.child_date_field))

            if depend_issues and issue_date:
                depend_dates = [dates.get_date(
                    issue.getField(dates.child_date_field)) for issue in depend_issues if dates.get_date(
                    issue.getField(dates.child_date_field))]

                if any(depend_date < issue_date for depend_date in depend_dates):
                    val = 'Due date later than due date(s) of dependent element(s)'
                elif any(depend_date == issue_date for depend_date in depend_dates):
                    val = 'Due date coincides with due date(s) of dependent element(s)'

        return val


class DateGetter:

    def __init__(self, l, mapping, parent_date_field, child_date_field):
        self.__logger = l
        self.__mapping = mapping
        self.__parent_date_field = parent_date_field
        self.__child_date_field = child_date_field
        self.__unknown = []

    @property
    def parent_date_field(self):
        return self.__parent_date_field

    @property
    def child_date_field(self):
        return self.__child_date_field

    @property
    def found_unknown(self):
        return self.__unknown

    def get_date(self, value):
        if hasattr(value, 'releaseDate'):
            return self.convert_to_datetime(value.releaseDate)
        if hasattr(value, 'name'):
            if value.name not in self.__mapping:
                if value.name not in self.__unknown:
                    self.__unknown.append(value.name)
                    self.__logger.msg('{} sprint is unknown'.format(value.name))
            else:
                return self.__mapping[value.name]

        return None

    def convert_to_datetime(self, value):
        return datetime.strptime(value, '%Y-%m-%d').date()
