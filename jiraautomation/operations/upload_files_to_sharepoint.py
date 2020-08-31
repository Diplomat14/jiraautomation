from jiraautomation.operations.operation import basic_operation
from jiraautomation.operations.get_files_from_sharepoint import get_files_from_sharepoint
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.runtime.utilities.request_options import RequestOptions
from office365.runtime.utilities.http_method import HttpMethod
from office365.sharepoint.file import File
import os


class upload_files_to_sharepoint(basic_operation):
    __logger = None

    @staticmethod
    def name():
        return "UploadFilesToSharepoint"

    @staticmethod
    def init_arguments(operation_group):
        get_files_from_sharepoint.init_arguments(operation_group)
        operation_group.add_argument('-uplshr_checkin', '--uplshr_checkintype', required=False,
                                     help='Type of file check in ')

    @staticmethod
    def parse_arguments(args):
        get_files_from_sharepoint.parse_arguments(args)

    def __init__(self, iLogger):
        super(upload_files_to_sharepoint, self).__init__(iLogger)

    def execute(self, container, args):
        l = self.logger

        try:

            try:
                ctx_auth = AuthenticationContext(url=args.sharepointurl)
                if ctx_auth.acquire_token_for_user(username=args.sharepointusername,
                                                   password=args.sharepointpass):
                    ctx = ClientContext(args.sharepointurl, ctx_auth)
                    filename = args.output
                    path = args.sharepointfpath
                    checkin_type = args.uplshr_checkintype
                    return upload_data_to_sharepoint(path, filename, ctx, checkin_type, l)
                else:
                    print(ctx_auth.get_last_error())
                    return

            except Exception as e:
                l.error("Exception happened boards search " + str(e))

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))


def checkout_file(target_url, ctx, l):
    url = "{0}web/getfilebyserverrelativeurl('{1}')/" \
          "CheckOut()".format(ctx.service_root_url, target_url)
    try:
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        ctx.execute_request_direct(request)
    except Exception as e:
        l.error(e)


def checkin_file(target_url, ctx, checkin_type, l):
    url = "{0}web/getfilebyserverrelativeurl('{1}')/" \
          "CheckIn(comment='',checkintype={2})".format(ctx.service_root_url, target_url, checkin_type)
    try:
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        ctx.execute_request_direct(request)
    except Exception as e:
        l.error(e)


def upload_data_to_sharepoint(sharepointfpath, file, context, checkin_type, l):
    with open(file, 'rb') as content_file:
        file_content = content_file.read()
    target_url = os.path.join(os.path.dirname(sharepointfpath), os.path.basename(file))
    l.msg('Uploading file to {}'.format(sharepointfpath))
    File.save_binary(context, target_url, file_content)
    l.msg('Checking in {} file'.format(file))
    checkin_file(target_url, context, checkin_type, l)
    l.msg('Checking out {} file'.format(file))
    checkout_file(target_url, context, l)
