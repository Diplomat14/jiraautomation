from jiraautomation.operations.operation import basic_operation
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.file import File


class get_files_from_sharepoint(basic_operation):
    __logger = None

    @staticmethod
    def name():
        return "SharepointFiles"

    @staticmethod
    def init_arguments(operation_group):
        operation_group.add_argument('-spurl', '--sharepointurl', required=False,
                                     help='Sharepoint Url')
        operation_group.add_argument('-spun', '--sharepointusername', required=False,
                                     help='Sharepoint UserName')
        operation_group.add_argument('-sp', '--sharepointpass', required=False,
                                     help='Sharepoint Password')
        operation_group.add_argument('-spfpath', '--sharepointfpath', required=False,
                                     help='Sharepoint File Path')

    @staticmethod
    def parse_arguments(args):
        return args

    def __init__(self, iLogger):
        super(get_files_from_sharepoint, self).__init__(iLogger)

    def execute(self, container, args):
        l = self.logger

        try:
            pass
            try:
                ctx_auth = AuthenticationContext(url=args.sharepointurl)
                if ctx_auth.acquire_token_for_user(username=args.sharepointusername,
                                                   password=args.sharepointpass):
                    ctx = ClientContext(args.sharepointurl, ctx_auth)
                    download_data_from_sharepoint(args, ctx)
                else:
                    print(ctx_auth.get_last_error())

            except Exception as e:
                l.error("Exception happened boards search " + str(e))

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e))


def download_data_from_sharepoint(args, context):
    with open(args.output, "wb") as output_file:
        response = File.open_binary(context, args.sharepointfpath)
        output_file.write(response.content)




