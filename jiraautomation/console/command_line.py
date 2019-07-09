import argparse
import jiraautomation
import jiraorm.console.command_line
#from jiraautomation.core import CoreOperation
from xdev.core.logger import logger


#temp
from jiraautomation.list_boards_operation import list_boards_operation
from jiraautomation.convert_linktofield_operation import linktofield_operation


def main():
    l = logger("CL")
    l.msg("JIRA Automation Command Line tool started")

    try:
        # This shall prepare and parse all arguments so that we can easily work with them afterwards
        args = parse_arguments(init_arguments())
        if args.logoutput != None:
            l.set_path(args.logoutput)

        try:
            l.msg("Operation %s" % str(args.operation))

            container = None
            output = None

            # TODO: If need to connect
            container = jiraorm.console.command_line.operation_connect(l,args)

            if args.operation == list_boards_operation.name():
                op = list_boards_operation(l)
                output = op.execute(container,args)
            elif args.operation == linktofield_operation.name():
                op = linktofield_operation(l)
                output = op.execute(container,args)
            else:
                l.warning("Operation %s not implemented" % str(args.operation))

            if output != None and args.output != None:
                with open(args.output, "w") as f:
                    return f.write(output)

        except Exception as e:
            l.error("Exception happened during operation processing: " + str(e))

    except Exception as e:
        l.error("Exception on commandline arguments parsing: " + str(e))

    l.msg("Command line tool finished")


def init_arguments():
    parser = argparse.ArgumentParser(description='JIRA Automation Command Line tool')

    # Reusing common arguments (like server, user, log, output, etc.) from orm console
    jiraorm.console.command_line.init_common_arguments(parser)

    operations_group = parser.add_argument_group('Script operations options')

    ops = []
    ops.append(list_boards_operation.name())
    ops.append(linktofield_operation.name())

    operations_group.add_argument('-o', '--operation', required=True,
                                  help='Operation that is to be executed', choices=ops)
    # Reusing common arguments for operation (like query, fields) from orm console
    operations_group = jiraorm.console.command_line.init_common_operations_arguments(operations_group)

    boards_group = parser.add_argument_group('Options of operation ' + list_boards_operation.name())
    list_boards_operation.init_arguments(boards_group)

    converter_group = parser.add_argument_group('Options of operation ' + linktofield_operation.name())
    linktofield_operation.init_arguments(converter_group)

    return parser

def parse_arguments(parser):
    args = parser.parse_args()

    list_boards_operation.parse_arguments(args)

    return args


if __name__ == "__main__":
    main()