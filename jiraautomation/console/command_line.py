import argparse
import traceback
import jiraorm.console.command_line
from jiraautomation.automationcore import automationcore
from xdev.core.logger import logger


#temp
import jiraautomation.operations

def main():
    l = logger("CL")
    l.msg("JIRA Automation Command Line tool started")

    try:
        # Adding operations
        for op in jiraautomation.operations.register.operations:
            automationcore.add_operation(op)

        # This shall prepare and parse all arguments so that we can easily work with them afterwards
        args = parse_arguments(init_arguments())
        if args.logoutput != None:
            l.set_path(args.logoutput)
        if args.debug != None:
            l.set_debug(args.debug)

        try:
            l.msg("Operation %s" % str(args.operation))

            container = None
            output = None

            # TODO: If need to connect
            container = jiraorm.console.command_line.operation_connect(l,args)

            found = False
            ops = automationcore.get_operations()
            for op in ops.values():
                if args.operation == op.name():
                    found = True
                    op_instance = op(l)
                    output = op_instance.execute(container, args)
            if found == False:
                l.warning("Operation %s not implemented" % str(args.operation))

            if output != None and args.output != None:
                with open(args.output, "w") as f:
                    return f.write(str(output))

        except Exception as e:
            l.error("Exception happened during operation processing: " + str(e), e)

    except Exception as e:
        l.error("Exception on commandline arguments parsing: " + str(e),e)


    l.msg("Command line tool finished")


def init_arguments():
    parser = argparse.ArgumentParser(description='JIRA Automation Command Line tool')

    # Reusing common arguments (like server, user, log, output, etc.) from orm console
    jiraorm.console.command_line.init_common_arguments(parser)

    operations_group = parser.add_argument_group('Script operations options')

    opnames = automationcore.get_operation_names()
    operations_group.add_argument('-o', '--operation', required=True,
                                  help='Operation that is to be executed', choices=opnames)
    # Reusing common arguments for operation (like query, fields) from orm console
    operations_group = jiraorm.console.command_line.init_common_operations_arguments(operations_group)

    ops = automationcore.get_operations()
    for op in ops.values():
        g = parser.add_argument_group('Options of operation ' + op.name())
        op.init_arguments(g)

    return parser

def parse_arguments(parser):
    args = parser.parse_args()

    ops = automationcore.get_operations()
    for op in ops.values():
        op.parse_arguments(args)

    jiraorm.console.command_line.parse_common_operations_arguments(args)

    return args


if __name__ == "__main__":
    main()