
from .operation import operations_register

register = operations_register()

register.register_dynamic('ListBoards','list_boards_operation','.list_boards_operation','jiraautomation.operations')
register.register_dynamic('LinkToField','linktofield_operation','.convert_linktofield_operation','jiraautomation.operations')
register.register_dynamic('PlanningReportPerSprint','planning_report_persprint_operation','.planning_report_persprint_operation','jiraautomation.operations')
register.register_dynamic('PlanningReportPerSprint2','planning_report_persprint_operation2','.planning_report_persprint_operation2','jiraautomation.operations')
register.register_dynamic('SetDueBySprint','set_due_by_sprint','.set_due_by_sprint','jiraautomation.operations')
register.register_dynamic('ExportIssuesAsJson','export_issues_as_json','.export_issues_as_json','jiraautomation.operations')
register.register_dynamic('GenerateWBS','generate_wbs','.generate_wbs','jiraautomation.operations')
register.register_dynamic('GenerateWBSHTML','generate_wbs_html','.generate_wbs_html','jiraautomation.operations')
register.register_dynamic('GenerateWBSJson','generate_wbs_json','.generate_wbs_json','jiraautomation.operations')
register.register_dynamic('GenerateIssuesTree','generate_issues_tree','.generate_issues_tree','jiraautomation.operations')
register.register_dynamic('GetSharepointFiles','get_files_from_sharepoint','.get_files_from_sharepoint','jiraautomation.operations')
register.register_dynamic('SynchronizeIssue','synchronize_issue','.synchronize_issue','jiraautomation.operations')
register.register_dynamic('GenerateCustomJiraStr','generate_custom_jira_structure','.generate_custom_jira_structure','jiraautomation.operations')
register.register_dynamic('GenerateFROPbyLOM', 'generate_FROP_by_lom','.generate_FROP_by_lom', 'jiraautomation.operations')
register.register_dynamic('GenerateExcel', 'generate_excel','.generate_excel', 'jiraautomation.operations')
register.register_dynamic('InitJira', 'init_jira','.init_jira', 'jiraautomation.operations')
register.register_dynamic('UploadFilesToSharepoint','upload_files_to_sharepoint','.upload_files_to_sharepoint','jiraautomation.operations')
