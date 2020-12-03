import unittest
import math
import json

from report_extract.report_extract import CultureParser
from validators.json_validator import *

from MedicalReports.Cultures import Culture
from MedicalReports.ReportingHelpers import ReportInfo

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

class CultureEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,Culture):
            if o.indentItem is None:
                return {'name':o.name,'resistances':o.resistances}
            else:
                return {'name': o.name, 'resistances': o.resistances, 'indent': o.indentItem}
        else:
            return super().default(o)



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
        """Will get the first report found in reportTypes then compare it against the MedicalReport checker that it
        applied all the values that it expected. """
        reportTypes = ['URINE MICROBIOLOGY',
                       'BLOOD CULTURE MICROBIOLOGY',
                       'CATHETER TIP MICROBIOLOGY',
                       'CEREBROSPINAL FLUID MICROBIOLOGY',
                       'MICROBIOLOGY FROM SUPERFICIAL SITES',
                       'MULTI-RESISTANT ORGANISM SCREEN',
                       'FAECES MICROBIOLOGY',
                       'RESPIRATORY MICROBIOLOGY',
                       'BODY FLUID EXAMINATION',
                       'C difficile screening',
                       'EYE, EAR, NOSE, THROAT MICROBIOLOGY']
        ri = ReportInfo()
        rows = df['ValueNew'].head(1000)

        for repType in reportTypes:
            parsedReport = ri.generateLimitedReportList(rows,repType)[0]
            baseReport = MedicalReport(parsedReport.rawdata, "\n")
            res = validator.doCheckAndReturnErrors(parsedReport, baseReport)
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
        r_basic = '{"cultures": [{"name": "Staphylococcus epidermidis", "resistances": {"PEN": "R", "FLU": "S", "CFZ": "S", "VA ": "S"}}], "notes": []}'
        s_gt_character = 'Culture    :\n                                                 SXT GEN TIM CIP\n    Acinetobacter baumannii complex >= 15 cfu     S   S   S   S\n\n                                                 MER\n    Acinetobacter baumannii complex >= 15 cfu     S\n\n'
        r_gt_character = '{"cultures": [{"name": "Acinetobacter baumannii complex", "resistances": {"SXT": "S", "GEN": "S", "TIM": "S", "CIP": "S", "MER": "S"}}], "notes": []}'
        s_inlineheader = 'CULTURE:                                                   AMP CFZ TMP NIT\n                             Escherichia coli > 10^8/L      S   S   S   S\n\n                                                           GEN\n                             Escherichia coli > 10^8/L      S\n\n\n'
        r_inlineheader = '{"cultures": [{"name": "Escherichia coli", "resistances": {"AMP": "S", "CFZ": "S", "TMP": "S", "NIT": "S", "GEN": "S"}}], "notes": []}'
        s_indent_multiline_multires = 'Culture    :\n                                                       PEN FLU AMP AUG\n                   Staphylococcus aureus 3+             R   S\n                   Klebsiella pneumoniae 1+                     R   S\n                        Candida albicans scant\n\n                                                       CFZ ERY SXT GEN\n                   Staphylococcus aureus 3+             S   S   S\n                   Klebsiella pneumoniae 1+             S       S   S\n                        Candida albicans scant\n\n                                                       TET\n                   Staphylococcus aureus 3+             S\n                   Klebsiella pneumoniae 1+\n                        Candida albicans scant\n\n\n'
        r_indent_multiline_multires = '{"cultures": [{"name": "Staphylococcus aureus 3+", "resistances": {"PEN": "R", "FLU": "S", "AMP": "", "AUG": "", "CFZ": "S", "ERY": "S", "SXT": "S", "GEN": "", "TET": "S"}, "indentItem": "Candida albicans scant"}, {"name": "Klebsiella pneumoniae 1+", "resistances": {"PEN": "", "FLU": "", "AMP": "R", "AUG": "S", "CFZ": "S", "ERY": "", "SXT": "S", "GEN": "S"}, "indentItem": "Candida albicans scant"}], "notes": []}'
        s_inline_notes = 'Culture      :      No growth after 5 days incubation'
        r_inline_notes = '{"cultures": [], "notes": ["No growth after 5 days incubation"]}'


        parser = CultureParser()

        expected = r_inline_notes
        actual = CultureEncoder().encode(parser.parseCulture(s_inline_notes))
        self.assertEqual(actual, expected)

        expected = r_basic
        actual = CultureEncoder().encode(parser.parseCulture(s_basic))
        self.assertEqual(actual,expected)

        expected = r_gt_character
        actual = CultureEncoder().encode(parser.parseCulture(s_gt_character))
        self.assertEqual(expected,actual)

        expected = r_inlineheader
        actual = CultureEncoder().encode(parser.parseCulture(s_inlineheader))
        self.assertEqual(expected,actual)

        expected = r_indent_multiline_multires
        actual = CultureEncoder().encode(parser.parseCulture(s_indent_multiline_multires))
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
        """Takes an input list (df) then will convert all the reports into the parsed result. It will then output a count of all the different repor types found. If the number of
        report is under 10, it's assumed that the parser chopped off a report."""
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
        """Outputs a percentage of reports that have a particular field assigned. Use this to find reports that are missing
        mandatory fields or suspiciously low assignment of fields (eg, only 1% assigned). Note it spams error messages if run in IDE.
        This is due to the way the json parser was initially built. Need to supress the errors to get usable output or
        reduce the size of the report list (.head(1000)"""
        reportname = 'BLOOD CULTURE MICROBIOLOGY' #Name of the report to filter on.
        totalStats = []
        reportList = df['ValueNew'].head(100)

        for val in reportList:
            if (reportname in val):
                rep = extract_value_report_as_json(val)
                try:
                    if (rep[0]['report'][0] in reportname):
                        counts = validator.getJsonFieldCounts(rep[0]) #0 if not assigned, >1 assigned
                        # print(counts)
                        totalStats.append(counts)
                except:
                    print('Cannot parse report')

        ret = validator.getPercentageOfAssignedKeys(totalStats)

        print(ret)


if __name__ == '__main__':
    unittest.main()