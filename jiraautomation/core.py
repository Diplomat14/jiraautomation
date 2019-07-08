from multiprocessing.dummy import Pool as ThreadPool


from xdev.core.logger import logger

from jiraorm.JSWContainer import JSWContainer
from jiraorm.JSWPersistence import JSWPersistence
import jiraorm.BasicConfig as j_cfg
#import JIRAOperations.ConvertLinkToField as j_op
#import JIRAOperations.ReportFeatures as j_op_rf

from enum import Enum, unique
from os.path import isfile

@unique
class CoreOperation(Enum):
    FixParents = 1
    CloneBoardSettings = 2
    ReportFeatures = 3


class JIRASimpleAutomationCore(object):
    __logger = None
    
    __poolSize = 0
    __pool = None

    __JSWContainer = None
    
    def __init__(self, connectionCfg : j_cfg.ConnectionConfig, securityCfg : j_cfg.SecurityConfig, useMultithreading : bool, poolSize : int, parentLogger:LoggerClass):
        self.__logger = logger.from_parent('JIRAAutomationCore',parentLogger)

        if isfile("pickledcontainer"):
            pers = JSWPersistence("pickledcontainer")
            self.__JSWContainer = pers.unpickle()
        if self.__JSWContainer == None: # if we were not able to unpickle
            self.__JSWContainer = JSWContainer(self.__logger,connectionCfg,securityCfg)

        self.__poolSize = poolSize if useMultithreading == True else 0
        self.__initMultithreading()

    def __del__(self):
        self.__deinitMultithreading()

    def persistContainer(self):
        pers = JSWPersistence("pickledcontainer")
        pers.pickle(self.__JSWContainer)
            
    def __initMultithreading(self):
        if self.__poolSize > 0:
            self.__pool = ThreadPool(self.__poolSize)

    def __deinitMultithreading(self):
        if self.__pool != None:
            self.__pool.close()
            self.__pool.join()


    def processOperation(self):



    def __processIssues(self,issues,fieldParentIssueId):
        l = self.__logger
        try:
            preparedIssues = j_op.prepareOperationData(issues,fieldParentIssueId,l)

            if self.__poolSize > 0:
                self.__pool.map(j_op.processIssueExt, preparedIssues)
            else:
                for preparedData in preparedIssues:
                    j_op.processIssueExt(preparedData)
        except Exception as e:
            l.error("Exception happened during pool processing " + str(e))


    def do(self,issuesBasisQuery, fieldParentIssueId):
        l = self.__logger
        
        try:
            jira = self.__JSWContainer.getJIRA()

            try:
                issues = jira.search_issues_nolim(issuesBasisQuery,0,200)
                l.msg(str(len(issues)) + " issues found")

                self.__processIssues(issues,fieldParentIssueId)
            except Exception as e:
                l.error("Exception happened issues search " + str(e))

            self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))

    def doboards(self, masterBoardName, boardNamePart = None):
        l = self.__logger

        try:
            jira = self.__JSWContainer.getJIRA()

            try:
                boards = jira.boards(0,50,'scrum',boardNamePart)
                l.msg( "Found " + str(len(boards)) + " boards" )

                masterBoard = None
                for board in boards:
                    if board.name == masterBoardName:
                        masterBoard = self.__JSWContainer.getBoardFromOriginal(board)
                        l.msg('Master board [' + str(masterBoard.id) + '] ' + masterBoardName + ' has been found')
                        break
                if masterBoard != None:
                    for board in boards:
                        if board.id != masterBoard.id:
                            currentBoard = self.__JSWContainer.getBoardFromOriginal(board)
                            l.msg('Processing board [' + str(currentBoard.id) + '] ' + currentBoard.name)
                            #currentBoard.setConfigColumns(masterBoard.configColumns, jira)
                            l.error('Updating of board configuration is not supported by JIRA')

                            
                else:
                    l.msg('Master board ' + masterBoardName + ' has not been found')
            except Exception as e:
                l.error("Exception happened boards search " + str(e))

            self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))
    
    def doReportFeatures(self, projectId:str, outputFile = "data.js", topIssueType:str = "Feature Group"):
        l = self.__logger

        try:
            jira = self.__JSWContainer.getJIRA()

            try:
                top_request_query = 'project = %s AND issuetype = "%s" ORDER BY updated DESC' % (projectId, topIssueType)
                issues = jira.search_issues_nolim(top_request_query)
                l.msg(str(len(issues)) + " issues found")

                jsData = j_op_rf.print_featuregroups_as_javascript_data(issues,self.__JSWContainer,l)

                output_file = open(outputFile, "w")
                output_file.write(jsData)
                output_file.close()

                #for i in issues:
                #    iExt = IssueExt(i,self.__jira)
                #    iExt.getChildren('Consists of',False)


                #self.__processIssues(issues,fieldParentIssueId)


            except Exception as e:
                l.error("Exception happened boards search " + str(e))

            self.persistContainer()
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))