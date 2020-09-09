import argparse
import jiraorm.console.command_line
from jiraautomation.automationcore import automationcore
from jiraautomation.operations.init_jira import init_jira
from xdev.core.logger import logger
import yaml


#temp
import jiraautomation.operations

def main():
    l = logger("CL")
    l.msg("JIRA Automation Command Line tool started")

    try:
        logoutput =get_argument_value('log', 'logoutput')
        if logoutput != None:
            l.set_path(logoutput)
        debug = get_argument_value('dbg', 'debug')
        if debug != None:
            l.set_debug(True)

        # Adding operations
        automationcore.set_register(jiraautomation.operations.register)

        # This shall prepare and parse all arguments so that we can easily work with them afterwards
        args = parse_arguments(init_arguments())

        try:
            l.msg("Operation %s" % str(args.operation))

            container = jiraorm.console.command_line.create_jira_container(l, args)
            output = None

            available_operations = automationcore.get_operation_names()
            requested_operation_names = args.operation.split(',')
            for operation in requested_operation_names:
                if operation in available_operations:
                    op_class = automationcore.get_operation_class(operation)
                    op_instance = op_class(l)
                    output = op_instance.execute(container, args)
                    args.data = output
                else:
                    l.warning("Operation %s not implemented" % str(args.operation))

            if output != None and args.output != None:
                if isinstance(output, (bytes, bytearray)):
                    with open(args.output, "wb") as f:
                        return f.write(output)
                else:
                    with open(args.output, "w", encoding='utf-8') as f:
                        return f.write(str(output))


        except Exception as e:
            l.error("Exception happened during operation processing", e)

    except Exception as e:
        l.error("Exception on commandline arguments parsing",e)


    l.msg("Command line tool finished")


def init_arguments():
    parser = argparse.ArgumentParser(description='JIRA Automation Command Line tool', fromfile_prefix_chars='@')

    # Reusing common arguments (like server, user, log, output, etc.) from orm console
    jiraorm.console.command_line.init_common_arguments(parser)

    requested_operation_names = get_argument_value('o', 'operation')

    operations_group = parser.add_argument_group('Script operations options')
    #opnames = automationcore.get_operation_names()
    operations_group.add_argument('-o', '--operation', required=True,
                                  help='Operation that is to be executed')
    operations_group.add_argument('-data', '--data', required=False,
                                  help='Output data after operation execution')
    # Reusing common arguments for operation (like query, fields) from orm console
    operations_group = jiraorm.console.command_line.init_common_operations_arguments(operations_group)

    available_operations = automationcore.get_operation_names()
    if requested_operation_names != None:
        requested_operation_names = requested_operation_names.split(",")
    else:
        requested_operation_names = available_operations

    for requested_operation in requested_operation_names:
        # parsing only for requested operation
        assert requested_operation in available_operations,\
            "Requested operation not found althpugh argarse already checked this."
        op = automationcore.get_operation_class(requested_operation)
        g = parser.add_argument_group('Options of operation ' + op.name())
        op.init_arguments(g)

    return parser

def get_argument_value(name,fullname):
    parser = argparse.ArgumentParser(fromfile_prefix_chars='@')
    operations_group = parser.add_argument_group()
    operations_group.add_argument('-%s' % name, '--%s' % fullname, required=False)
    args,other = parser.parse_known_args()
    if hasattr(args,fullname) == True:
        return getattr(args,fullname)
    else:
        return None


def parse_yaml_files(args):
    for k, v in args.__dict__.items():
        if not v: continue

        if isinstance(v, str):
            if v.endswith('.yml') or v.endswith('.yaml'):
                data = yaml.load(open(v), Loader=yaml.Loader)
                setattr(args, k, data)

    return args


def parse_arguments(parser):
    args = parser.parse_args()
    requested_operation_names = args.operation.split(",")
    available_operations = automationcore.get_operation_names()
    for requested_operation in requested_operation_names:
        # parsing only for requested operation
        assert requested_operation in available_operations, \
            "Requested operation not found althpugh argarse already checked this."
        op = automationcore.get_operation_class(requested_operation)
        op.parse_arguments(args)

    jiraorm.console.command_line.parse_common_operations_arguments(args)
    parse_yaml_files(args)

    return args


if __name__ == "__main__":
    main()