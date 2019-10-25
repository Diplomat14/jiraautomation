from jiraautomation.operations.operation import  basic_operation
from xdev.types.algorithms.merge import merger, merge_object, merge_rules, resolve_conflict_t

class synchronize_issue(basic_operation):

    @staticmethod
    def name():
        return "SynchronizeIssue"

    @staticmethod
    def init_arguments(operation_group):
        operation_group.add_argument('-syncSK', '--synchronizeissue_source_key', required=False,
                                          help='Key of issue to use as source.')
        operation_group.add_argument('-syncTK', '--synchronizeissue_target_key', required=False,
                                     help='Key of issue to use as target')
        operation_group.add_argument('-syncSF', '--synchronizeissue_source_field', required=False,
                                     help='name of the field containing key of source issue')

    @staticmethod
    def parse_arguments(args):
        # You might want to prepare arguments somehow like:
        # args.operation = CoreOperation[args.operation]
        pass

    def __init__(self, iLogger):
        super(synchronize_issue,self).__init__(iLogger)

    def execute(self,container,args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                source_key = args.synchronizeissue_source_key
                target_key = args.synchronizeissue_target_key
                source_field = args.synchronizeissue_source_field

                source_issue = container.getIssueByKey(source_key,expand='changelog')
                target_issue = container.getIssueByKey(target_key,expand='changelog')

                l.msg("Found source issue with key %s and title '%s'" % (source_key, source_issue.getField('summary')))
                l.msg("Found source issue with key %s and title '%s'" % (target_key, target_issue.getField('summary')))

                merge_result = self.merge_issues(source_issue, target_issue,source_field)

                return None
            except Exception as e:
                l.error("Exception happened in main operation logic",e)
        except Exception as e:
            l.error("Exception happened during connection establishment",e)

    def merge_issues(self,src, trg,source_field):
        fields = ['summary','description']
        (src_obj, src_obj_updates) = self.obj_from_issue(src,fields)
        src_obj_key = src.getField('key')
        (trg_obj, trg_obj_updates) = self.obj_from_issue(trg,fields)
        trg_obj_key = trg.getField('key')
        trg_obj_source_key = trg.getField(source_field)

        if trg_obj_source_key == None:
            trg_obj.setField(source_field,src_obj_key)
        elif trg_obj_source_key[-len(src_obj_key):] != src_obj_key:
            self.logger.warning('Existing source reference of issue %s (source set to %s) differs from proposal to merge with %s' % (trg_obj_key, trg_obj_source_key, src_obj_key) )
        else:
            rules = merge_rules(resolve_conflict_t.LEFT)

            merge_result = merger.merge_objects(
                merge_object(src_obj,src_obj_updates),
                merge_object(trg_obj,trg_obj_updates),
                rules)

            for f in merge_result.left_changed_fields:
                newv = merge_result.merged_object.data_map[f]
                self.logger.msg('Updating issue %s, field %s to new value %s' % (src_obj_key, f, str(newv)) )
                src.setField(f, newv)
            for f in merge_result.right_changed_fields:
                newv = merge_result.merged_object.data_map[f]
                self.logger.msg('Updating issue %s, field %s to new value %s' % (trg_obj_key, f, str(newv)))
                trg.setField(f, newv)

    def obj_from_issue(self,issue, fields):
        obj = {}
        obj_update_time = {}
        obj_update_time[""] = issue.getField('updated')
        for f in fields:
            if issue.hasField(f):
                obj[f] = issue.getField(f)
                obj_update_time[f] = issue.getFieldUpdatesAsDT(f)

        return (obj, obj_update_time)
