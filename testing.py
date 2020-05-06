import unittest
import csv
import pandas

from report_extract import *
from validators.json_validator import *

in_file = 'Data/Microbiology2_conv.csv'

class TestStringMethods(unittest.TestCase):

    self.validator = None
    self.info = None
    self.df = DataFrame()

    def setUp(self):
        self.df = pandas.read_csv(in_file, sep='\t')
        self.df['ValueNew'] = self.df['ValueNew'].apply(lambda x : x.replace("||", "\n"))
        self.validator = JsonValidator()
        self.info = ReportInfo()

    def test_general_report_parsing(self):
        row = df.iloc[27840]['ValueNew']
        separator = "\n"

        reportValue = MedicalReport(row,separator)

        json = extract_value_report_as_json(row)
        res = self.validator.doCheckAndReturnErrors(json[0],reportValue)
        self.assertEqual([],res,'Errors were found during the run')

    def find_minmax_report(self):
        repBySize = self.info.convertToSizeBasedDf(df['ValueNew'])
        max = self.info.getMaxSizeReport(repBySize,'MULTI-RESISTANT ORGANISM SCREEN')
        min = self.info.getMinSizeReport(repBySize,'MULTI-RESISTANT ORGANISM SCREEN')

        print(max)
        print(min)





if __name__ == '__main__':
    unittest.main()