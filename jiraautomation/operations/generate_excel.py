from jiraautomation.operations.operation import basic_operation
from openpyxl import load_workbook
import pandas as pd


class generate_excel(basic_operation):

    @staticmethod
    def name():
        return "GenerateExcel"

    @staticmethod
    def init_arguments(operation_group):
        pass

    @staticmethod
    def parse_arguments(args):
        pass

    def __init__(self, iLogger, data, sheet_name, row=0, index=True):
        super(generate_excel, self).__init__(iLogger)
        self.data = data
        self.sheet_name = sheet_name
        self.row = row
        self.index = index

    def execute(self, container, args):
        l = self.logger

        try:

            try:
                df = pd.DataFrame(self.data)
                if all(isinstance(clm, tuple) for clm in df.columns.values):
                    df.columns = pd.MultiIndex.from_tuples(df.columns)

                save_data_to_excel(args.output, df, self.sheet_name, self.row, self.index)

            except Exception as e:
                l.error("Exception happened boards search " + str(e), e)

        except Exception as e:
            l.error("Exception happened during connection establishment " + str(e), e)


def save_data_to_excel(file, data, sheet_name, startrow, index):
    with pd.ExcelWriter(file, engine='openpyxl') as writer:
        writer.book = load_workbook(file)
        writer.sheets = {ws.title: ws for ws in writer.book.worksheets}
        data.to_excel(writer, sheet_name=sheet_name, startrow=startrow, index=index)
