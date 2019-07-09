from jiraautomation.operations.operation import  basic_operation
from xdev.core.logger import logger

class linktofield_operation(basic_operation):

    #__poolSize = 0
    #__pool = None

    @staticmethod
    def name():
        return "LinkToField"

    @staticmethod
    def init_arguments(operation_group):
        operation_group.add_argument('-ltfFID', '--linktofield_fieldid', required=False,
                                          help='ID of the target field to write other side of link to')
        operation_group.add_argument('-ltfLN', '--linktofield_linkname', required=False,
                                          help='Name of the link connection')
        pass

    @staticmethod
    def parse_arguments(args):
        # You might want to prepare arguments somehow like:
        # args.operation = CoreOperation[args.operation]
        pass

    def __init__(self, iLogger):
        super(linktofield_operation,self).__init__(iLogger)

    #def __initMultithreading(self):
    #    if self.__poolSize > 0:
    #        self.__pool = ThreadPool(self.__poolSize)

    #def __deinitMultithreading(self):
    #    if self.__pool != None:
    #        self.__pool.close()
    #        self.__pool.join()

    def execute(self,container,args):
        l = self.logger

        try:
            #self.__poolSize = poolSize if useMultithreading == True else 0
            #self.__initMultithreading()

            issuesBasisQuery = args.query
            fieldParentIssueId = args.linktofield_fieldid
            linkName = args.linktofield_linkname
            jira = container.getJIRA()

            try:
                issues = jira.search_issues_nolim(issuesBasisQuery, 0, 200)
                l.msg(str(len(issues)) + " issues found")

                try:
                    preparedIssues = prepareOperationData(issues, fieldParentIssueId, linkName, l)

                    # if self.__poolSize > 0:
                    #    self.__pool.map(processIssueExt, preparedIssues)
                    # else:
                    for preparedData in preparedIssues:
                        processIssueExt(preparedData)
                except Exception as e:
                    l.error("Exception happened during pool processing " + str(e))
            except Exception as e:
                l.error("Exception happened issues search " + str(e))

            #self.persistContainer()
            #self.__deinitMultithreading()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))



class ConvertLinkToFieldOperationData(object):
    issue = None
    fieldName = ''
    logger = None
    linkName = ''

    def __init__( self, issue, fieldName : str, linkName : str, logger ):
        self.issue = issue
        self.fieldName = fieldName
        self.logger = logger
        self.linkName = linkName


def prepareOperationData(issues, fieldName: str, linkName : str, parentLogger):
    datas = []

    for issue in issues:
        datas.append(ConvertLinkToFieldOperationData(issue, fieldName, linkName,
                                                     logger.from_parent(issue.original.key, parentLogger)))

    return datas


def processIssueExt(data : ConvertLinkToFieldOperationData ):
    issue = data.issue
    logger = data.logger
    fieldName = data.fieldName
    linkName = data.linkName
    logger.msg(str("Processing issue [" + str(issue.original.key) + "] " + str(issue.original.fields.summary) + ""))

    try:
        processIssue(issue, fieldName, linkName, logger)
        logger.msg("Issue processed")
    except Exception as e:
        logger.msg("Exception occured:" + str(e))


def processIssue(issue, fieldName, linkName, logger):
    inwardConsistsOfLinks = issue.getLinksByType(linkName, True)

    if len(inwardConsistsOfLinks) > 1:
        logger.warning("Issue is part of " + str(len(inwardConsistsOfLinks)) + " issues. Setup parent manually")
    elif len(inwardConsistsOfLinks) == 1:
        if issue.isCustomFieldSet(fieldName) == True:
            logger.msg("Parent is already set")
        else:
            parentIssue = inwardConsistsOfLinks[0].inwardIssue
            logger.msg("Parent is empty. Setting parent to [" + parentIssue.key + "]")
            issue.original.update(fields={fieldName: str(parentIssue.key)})
            logger.msg("Updated")