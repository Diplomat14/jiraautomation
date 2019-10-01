from jiraautomation.operations.operation import basic_operation
from openpyxl import load_workbook

from .generate_wbs_json import generate_wbs_json
import pandas as pd

class generate_wbs_excel(basic_operation):

    @staticmethod
    def name():
        return "GenerateWBSExcel"

    @staticmethod
    def init_arguments(operation_group):
        pass

    @staticmethod
    def parse_arguments(args):
        pass

    def __init__(self, iLogger):
        super(generate_wbs_excel, self).__init__(iLogger)

    def execute(self, container, args):
        l = self.logger

        try:
            jira = container.getJIRA()

            try:
                op = generate_wbs_json(l)
                json_data = op.execute(container, args)
                df = pd.read_json(json_data)

                with pd.ExcelWriter(args.output, engine='openpyxl') as writer:
                    writer.book = load_workbook(args.output)
                    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
                    sheet = writer.book.sheetnames[0]
                    for row in writer.book[sheet]:
                        for cell in row:
                            cell.value = None

                    full_df = calculated_cols(df)
                    full_df.to_excel(writer, sheet_name=sheet, index=False)

            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)


def calculated_cols(df):
    df['Original hours'] = df['Original est.'] / 3600
    df['Original days'] = df['Original hours'] / 8
    df['Spent hours'] = df['Spent time'] / 3600
    df['Spent days'] = df['Spent hours'] / 8
    df['Remaining hours'] = df['Remaining est.'] / 3600
    df['Remaining days'] = df['Remaining hours'] / 8

    return df