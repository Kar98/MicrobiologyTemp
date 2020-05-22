import unittest
import math
import json

from report_extract.report_extract import CultureParser
from validators.json_validator import *

# Features to test
from report_extract import report_pattern, split_sections, extract_value_report_as_json

import pandas as pd
import re

# Load data to be processed for report extraction.

# folder = '/Users/kjr/Desktop/MIMICQ/Athena/FreeTextSignalsMicrobiology'
folder = 'Data'
file = 'Microbiology2_conv'
ext = 'csv'
in_file = '{}/{}.{}'.format(folder, file, ext)

# Read in the input data that will have tests created for it.
df = pd.read_csv(in_file, sep='\t')

# Replace || for LFs
df['ValueNew'] = df['ValueNew'].apply(lambda x: x.replace("||", "\n"))
df['CommentsNew'] = df['CommentsNew'].apply(lambda x: x.replace("||", "\n"))

validator = JsonValidator()


class TestExtractBasics(unittest.TestCase):

    # def setUp(self):
    #     self.auth = 'test'

    def test_Report_Types_instance(self):
        # Test the report types contain a particular instance (checks loaded values).
        report_types = report_pattern.split('|')
        self.assertTrue('Deleted' in report_types)
        self.assertEquals(len(report_types), 17)

    def test_Report_Sections_Bacterial_Antigens(self):
        # Test the report unpacks particular report type.
        row = df.iloc[73]

        # Check row
        self.assertEquals(row['PatientID'], 21)
        self.assertEquals(row['ParameterID'], 12613)
        self.assertEquals(row['Time'], '2013-10-02 18:00:00')

        # Check reports
        self.assertEquals(re.findall(report_pattern, row['ValueNew']), ['Bacterial Antigens'])

        # Check sections extracted - as only one report we have one section same as Value
        sections = split_sections(row['ValueNew'])
        self.assertEquals(sections, [row['ValueNew']])

    def test_Report_Sections_Urine_Microbiology(self):
        # Test the report unpacks particular report type.
        row = df.iloc[575]

        # Check row
        self.assertEquals(row['PatientID'], 38)
        self.assertEquals(row['ParameterID'], 12613)
        self.assertEquals(row['Time'], '2013-10-19 05:00:00')

        # Check reports
        self.assertEquals(re.findall(report_pattern, row['ValueNew']), ['URINE MICROBIOLOGY'])

        # Check sections extracted - as only one report we have one section same as Value
        sections = split_sections(row['ValueNew'])
        sections(row['ValueNew'])
        self.assertEquals(sections, [row['ValueNew']])

    def test_Report_Sections_Multiple(self):
        # Test the report unpacks particular report type.
        row = df.iloc[4028]

        # Check row
        self.assertEquals(row['PatientID'], 1006)
        self.assertEquals(row['ParameterID'], 12613)
        self.assertEquals(row['Time'], '2014-05-02 13:30:00')

        # Check reports
        self.assertEquals(re.findall(report_pattern, row['ValueNew']),
                          ['CEREBROSPINAL FLUID MICROBIOLOGY', 'MISCELLANEOUS MICROBIOLOGY'])

        # Check sections extracted - value split into two report sections
        sections = split_sections(row['ValueNew'])
        self.assertEquals(sections,
                          [
                              "\nCEREBROSPINAL FLUID MICROBIOLOGY\n\nLab No.      :  63508-7495\nMicro No.    :  GC14M33542\n\nCollected    :  13:30  02-May-14\nWard         :  Childrens Critical Care (GCUH)\nRegistered   :  13:54  02-May-14\n\nSpecimen     :  CSF\n\nVolume       :    5.0   mL\nAppearance   :  Clear\nSupernatant  :  Colourless\n\n\nNo. of tubes :   9\n\nChemistry    :  Protein     250  mg/L    (150 - 500)\n                Glucose      3.6 mmol/L  (2.2 - 3.9)\n\n\nCell Count   :  Tube No:    5\n                WBC''s         57   x10^6/L\n                RBC''s     <     1  x10^6/L\n\n\nDifferential :  Polymorphs     0   %\n\n                Mononuclears  100  %\n                Eosinophils    0   %\n                Others         0   %\n\n\nGram Stain   :  No organisms seen\n\n\nCULTURE         No growth after 48 hrs incubation\n\n",
                              "MISCELLANEOUS MICROBIOLOGY\n\nLab No.      :    63508-7495\n\nCollected    :    13:30  02-May-14\nWard         :    Childrens Critical Care (GCUH)\nRegistered   :    13:54  02-May-14\n\nSpecimen     :    CSF\n\n\nTest        :     Respiratory PCR\n\nThis is a miscellaneous test. Please contact the lab for the results of the above test."
                              ])

    def test_general_report_parsing(self):
        for x in range(1):
            row = df.iloc[27840]['ValueNew']
            separator = "\n"

            reportValue = MedicalReport(row, separator)

            json = extract_value_report_as_json(row)
            res = validator.doCheckAndReturnErrors(json[0], reportValue)
            self.assertEqual([], res, 'Errors were found during the run')

    def test_large_reports(self):
        reportname = 'BLOOD CULTURE MICROBIOLOGY'
        repBySize = validator.convertToSizeBasedDf(df['ValueNew'])
        max = validator.getMaxSizeReport(repBySize, reportname)
        min = validator.getMinSizeReport(repBySize, reportname)
        print(min)
        print(max)

    def testCultureParser(self):
        s_basic = 'Culture    :\n                                                 PEN FLU CFZ VA\n         Staphylococcus epidermidis               R   S   S   S'
        r_basic = '{"cultures": [{"name": "Staphylococcus epidermidis", "resistances": {"PEN": "R", "FLU": "S", "CFZ": "S", "VA": "S"}}], "notes": []}'
        s_gt_character = 'Culture    :\n                                                 SXT GEN TIM CIP\n    Acinetobacter baumannii complex >= 15 cfu     S   S   S   S\n\n                                                 MER\n    Acinetobacter baumannii complex >= 15 cfu     S\n\n'
        r_gt_character = '{"cultures": [{"name": "Acinetobacter baumannii complex", "resistances": {"SXT": "S", "GEN": "S", "TIM": "S", "CIP": "S", "MER": "S"}}], "notes": []}'
        s_inlineheader = 'CULTURE:                                                   AMP CFZ TMP NIT\n                             Escherichia coli > 10^8/L      S   S   S   S\n\n                                                           GEN\n                             Escherichia coli > 10^8/L      S\n\n\n'
        r_inlineheader = '{"cultures": [{"name": "Escherichia coli", "resistances": {"AMP": "S", "CFZ": "S", "TMP": "S", "NIT": "S", "GEN": "S"}}], "notes": []}'
        s_indent_multiline_multires = 'Culture    :\n                                                       PEN FLU AMP AUG\n                   Staphylococcus aureus 3+             R   S\n                   Klebsiella pneumoniae 1+                     R   S\n                        Candida albicans scant\n\n                                                       CFZ ERY SXT GEN\n                   Staphylococcus aureus 3+             S   S   S\n                   Klebsiella pneumoniae 1+             S       S   S\n                        Candida albicans scant\n\n                                                       TET\n                   Staphylococcus aureus 3+             S\n                   Klebsiella pneumoniae 1+\n                        Candida albicans scant\n\n\n'
        r_indent_multiline_multires = '{"cultures": [{"name": "Staphylococcus aureus 3+", "resistances": {"PEN": "R", "FLU": "S", "AMP": "", "AUG": "", "CFZ": "S", "ERY": "S", "SXT": "S", "GEN": "", "TET": "S"}}, {"name": "Klebsiella pneumoniae 1+", "resistances": {"PEN": "", "FLU": "", "AMP": "R", "AUG": "S", "CFZ": "S", "ERY": "", "SXT": "S", "GEN": "S", "TET": ""}, "indent": "Candida albicans scant"}], "notes": []}'

        parser = CultureParser()

        expected = json.loads(r_basic)
        actual = json.loads(parser.parseCulture(s_basic))
        self.assertEqual(actual,expected)

        expected = json.loads(r_gt_character)
        actual = json.loads(parser.parseCulture(s_gt_character))
        self.assertEqual(expected,actual)

        expected = json.loads(r_inlineheader)
        actual = json.loads(parser.parseCulture(s_inlineheader))
        self.assertEqual(expected,actual)

        expected = json.loads(r_indent_multiline_multires)
        actual = json.loads(parser.parseCulture(s_indent_multiline_multires))
        self.assertEqual(expected,actual)

        print(expected)

    def testAbbreviationParser(self):
        blank_abbreviation = 'Culture    :\n\n      Coagulase Neg. Staphylococcus < 15 cfu\n\n     Antibiotic Abbreviations Guide:\n\n\n\nComments   :  Sub Galeal drain tip \nSpecimen: Tip-Drain-Head\n\n'
        str2 = ''
        parser = CultureParser()

        f = open('test.txt','r')
        text = f.read()
        f.close()
        print(parser.parseCulture(text))


class TestHighLevelScenarios(unittest.TestCase):

    def test_check_report_counts(self, fail=True):

        sizeBasedDf = validator.convertToSizeBasedDf(df['ValueNew'])
        # Get the counts of the reports
        counts = sizeBasedDf.groupby(['Report'])['Report'].count()
        print(counts)
        errors = []
        for index, value in counts.items():
            if (value < 10):
                errors.append('{0} has less than 10 results'.format(index))

        if (fail):
            self.assertEqual([], errors)
            return None
        else:
            return errors

    def test_check_assigned_fields(self):

        reportname = 'BLOOD CULTURE MICROBIOLOGY'
        totalStats = []
        reportList = df['ValueNew']
        for val in reportList:
            if (reportname in val):
                rep = extract_value_report_as_json(val)
                try:
                    if (rep[0]['report'][0] in reportname):
                        counts = validator.getJsonFieldCounts(rep[0])
                        # print(counts)
                        totalStats.append(counts)
                except:
                    print('Cannot parse report')
        ret = validator.getPercentageOfAssignedKeys(totalStats)

        print(ret)


if __name__ == '__main__':
    unittest.main()