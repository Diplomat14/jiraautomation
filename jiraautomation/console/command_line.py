import argparse
import jiraautomation
import jiraorm.console.command_line
from jiraautomation.core import CoreOperation
from xdev.core.logger import logger

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

            c = None
            output = None

            # For most of operations we need connection to JIRA so coding it once
            #if args.operation == operation.Connect or args.operation == operation.Select:
            #    c = operation_connect(l, args)

            #if args.operation == operation.Select:
            #    output = operation_select(l, args, c)
            #else:
            #    if args.operation != operation.Connect:
            #        l.warning("Operation %s not implemented" % str(args.operation))

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
    parser = jiraorm.console.command_line.init_common_arguments()

    operations_group = parser.add_argument_group('Script operations options')
    ops = [op.name for op in list(CoreOperation)]
    operations_group.add_argument('-o', '--operation', required=True,
                                  help='Operation that is to be executed', choices=ops)

    # Reusing common arguments for operation (like query, fields) from orm console
    operations_group = jiraorm.console.command_line.init_common_operations_arguments(operations_group)

    return parser

def parse_arguments(parser:argparse.ArgumentParser):
    args = parser.parse_args()

    args.operation = CoreOperation[args.operation]

    return args

if __name__ == "__main__":
    main()