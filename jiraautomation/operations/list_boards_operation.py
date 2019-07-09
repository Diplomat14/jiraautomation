from jiraautomation.operations.operation import  basic_operation


class list_boards_operation(basic_operation):

    @staticmethod
    def name():
        return "ListBoards"

    @staticmethod
    def init_arguments(operation_group):
        operation_group.add_argument('-lbNP', '--listboards_namepart', required=False,
                                          help='Part of the name to use as a filter searching for boards')
        pass

    @staticmethod
    def parse_arguments(args):
        # You might want to prepare arguments somehow like:
        # args.operation = CoreOperation[args.operation]
        pass

    def __init__(self, iLogger):
        super(list_boards_operation,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                boardNamePart = args.listboards_namepart if args.listboards_namepart else None

                boards = jira.boards(0, 50, 'scrum', boardNamePart)
                l.msg("Found " + str(len(boards)) + " boards")

                boardsExt = []
                for board in boards:
                    board = container.getBoardFromOriginal(board)
                    l.msg('Board [' + str(board.id) + '] ' + board.name)
                    boardsExt.append(board)

                return boardsExt

                # masterBoard = None
                # for board in boards:
                #    if board.name == masterBoardName:
                #        masterBoard = self.__JSWContainer.getBoardFromOriginal(board)
                #        l.msg('Master board [' + str(masterBoard.id) + '] ' + masterBoardName + ' has been found')
                #        break
                # if masterBoard != None:
                #    for board in boards:
                #        if board.id != masterBoard.id:
                #            currentBoard = self.__JSWContainer.getBoardFromOriginal(board)
                #            l.msg('Processing board [' + str(currentBoard.id) + '] ' + currentBoard.name)
                #            # currentBoard.setConfigColumns(masterBoard.configColumns, jira)
                #            l.error('Updating of board configuration is not supported by JIRA')
                # else:
                #    l.msg('Master board ' + masterBoardName + ' has not been found')

            except Exception as e:
                l.error("Exception happened boards search " + str(e))
        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))