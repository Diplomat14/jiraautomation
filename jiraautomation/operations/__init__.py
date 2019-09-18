
from .operation import operations_register
from .list_boards_operation import list_boards_operation
from .convert_linktofield_operation import linktofield_operation
from .planning_report_persprint_operation import planning_report_persprint_operation
from .planning_report_persprint_operation2 import planning_report_persprint_operation2
from .set_due_by_sprint import set_due_by_sprint
from .export_issues_as_json import export_issues_as_json
from .generate_wbs import generate_wbs
from .generate_issues_tree import generate_issues_tree

register = operations_register()

register.register(list_boards_operation)
register.register(linktofield_operation)
register.register(planning_report_persprint_operation)
register.register(planning_report_persprint_operation2)
register.register(set_due_by_sprint)
register.register(export_issues_as_json)
register.register(generate_wbs)
register.register(generate_issues_tree)