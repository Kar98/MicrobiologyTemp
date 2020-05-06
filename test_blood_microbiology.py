# Tests for Urine Microbiology report extraction

import unittest

# Features to test
from report_extract import extract_value_report_as_json

import pandas as pd
import re

print('test')

# Load data to be processed for report extraction.

folder = 'Data'
file = 'Microbiology2_conv'
ext = 'csv'
in_file = '{}/{}.{}'.format(folder, file, ext)

# Read in the input data that will have tests created for it.
df = pd.read_csv(in_file, sep='\t')

# Replace || for LFs
df['ValueNew'] = df['ValueNew'].apply(lambda x : x.replace("||", "\n"))
df['CommentsNew'] = df['CommentsNew'].apply(lambda x : x.replace("||", "\n"))




blood_test_cases = {


###################################################################################################################
0 : {

        'PatientID' : 3,
        'ParameterID' : 12613,
        'Time' : '2013-09-25 18:50:00',
        'expected' : {
                "microscopy": "",
                "report": ["BLOOD CULTURE MICROBIOLOGY"],
                "collected": ["18:50  25-Sep-13"],
                "text": "\nBLOOD CULTURE MICROBIOLOGY\n\nLab No.    :  60291-1169\nMicro No.  :  GC13M67471\n\nCollected  :  18:50  25-Sep-13\nWard       :  ICU-Intensive Care Unit (GCH)\nRegistered :  19:02  25-Sep-13\n\n\n\nCulture    :  No growth after 5 days incubation",
                "gram_stain": "",
                "mrsa_screen": "",
                "comments": "",
                "cell_count": "",
                "volume": [],
                "casts": "",
                "registered": ["19:02  25-Sep-13"],
                "red cell morphology": "",
                "lab_no": ["60291-1169"],
                "specimen": "",
                "num_tubes": [],
                "ward": ["ICU-Intensive Care Unit (GCH)"],
                "supernatant": [],
                "micro_no": ["GC13M67471"],
                'culture': {
                    'abbreviations': {},
                    'notes': '',
                    'other': ['No growth after 5 days incubation'],
                    'text': 'No growth after 5 days incubation',
                    'vals': {}
                },
                "chemistry": "",
                "differential": "",
                "appearance": []
              },

    },


# 1155
1155 : {

        'PatientID' : 418,
        'ParameterID' : 12613,
        'Time' : '2014-01-21 09:30:00',
        'expected' : {
                'text': '\nBLOOD CULTURE MICROBIOLOGY\n\nLab No.    :  60952-8957\nMicro No.  :  GC14M5328\n\nCollected  :  09:30  21-Jan-14\nWard       :  Intensive Care Unit D4 (GCUH)\nRegistered :  13:34  21-Jan-14\n\n\n\nPositive Bottles :  2 of 2\nGrowth After     :  17 Hours\n\nGram Stain :  Gm pos cocci resemb. Staphylococci\n\n\nCulture    :\n\n      Coagulase Neg. Staphylococcus\n\n     Antibiotic Abbreviations Guide:\n\n\n\n              Probable Contaminant.',
                'casts': '',
                'chemistry': '',
                'gram_stain': 'Gm pos cocci resemb. Staphylococci',
                'differential': '',
                'registered': ['13:34  21-Jan-14'],
                'cell_count': '',
                'collected': ['09:30  21-Jan-14'],
                'volume': [],
                'ward': ['Intensive Care Unit D4 (GCUH)'],
                'red cell morphology': '',
                'micro_no': ['GC14M5328'],
                'culture': {
                    'notes': 'Probable Contaminant.',
                    'text': 'Coagulase Neg. Staphylococcus\n\n     Antibiotic Abbreviations Guide:\n\n\n\n              Probable Contaminant.',
                    'abbreviations': {},
                    'vals': {},
                    'other': ['Coagulase Neg. Staphylococcus']
                    },
                'specimen': '',
                'microscopy': '',
                'num_tubes': [],
                'supernatant': [],
                'report': ['BLOOD CULTURE MICROBIOLOGY'],
                'mrsa_screen': '',
                'appearance': [],
                'comments': '',
                'lab_no': ['60952-8957']
                },

    },

# 1280
1280 : {
        'PatientID' : 303,
        'ParameterID' : 12613,
        'Time' : '2013-12-30 05:01:00',
        'expected' : {
                'num_tubes': [],
                'chemistry': '',
                'casts': '',
                'report': ['BLOOD CULTURE MICROBIOLOGY'],
                'differential': '',
                'text': '\nBLOOD CULTURE MICROBIOLOGY\n\nLab No.    :  58065-9888\nMicro No.  :  GC13M90722\n\nCollected  :  05:00  30-Dec-13\nWard       :  Intensive Care Unit D4 (GCUH)\nRegistered :  06:00  30-Dec-13\n\n\n\nPositive Bottles :  2 of 2\nGrowth After     :  23.1 hrs\n\nGram Stain :  Gm pos cocci resemb. Staphylococci\n\n\nCulture    :\n                                                 PEN FLU CFZ VA\n         Staphylococcus epidermidis               R   R   R   S\n\n\n\n\n\n     Antibiotic Abbreviations Guide:\n     PEN     Penicillin G               FLU     Di(Flu)cloxacillin\n                                        CFZ     Cefazolin\n                                        VA      Vancomycin',
                'collected': ['05:00  30-Dec-13'],
                'comments': '',
                'cell_count': '',
                'volume': [],
                'appearance': [],
                'culture': {
                    'notes': '',
                    'abbreviations': {
                        "PEN": "Penicillin G",
                        "FLU": "Di(Flu)cloxacillin",
                        "CFZ": "Cefazolin",
                        "VA": "Vancomycin"
                    },
                    'other': [],
                    'text': 'PEN FLU CFZ VA\n         Staphylococcus epidermidis               R   R   R   S\n\n\n\n\n\n     Antibiotic Abbreviations Guide:\n     PEN     Penicillin G               FLU     Di(Flu)cloxacillin\n                                        CFZ     Cefazolin\n                                        VA      Vancomycin',
                    'vals': {
                        'Staphylococcus epidermidis': {
                                'resistance': {'PEN': 'R', 'FLU': 'R', 'VA': 'S', 'CFZ': 'R'}
                                }
                            }
                        },
                    'specimen': '',
                    'red cell morphology': '',
                    'supernatant': [],
                    'gram_stain': 'Gm pos cocci resemb. Staphylococci',
                    'microscopy': '',
                    'mrsa_screen': '',
                    'lab_no': ['58065-9888'],
                    'ward': ['Intensive Care Unit D4 (GCUH)'],
                    'registered': ['06:00  30-Dec-13'],
                    'micro_no': ['GC13M90722']
                    },

    },

# 1474

# 1602

# 1632

# 1727

# 3538

# 3714

# 3993

###################################################################################################################
# No Antibiotics header row, and now abbreviation lines, hence gets confused with comments
5716 : {

        'PatientID' : 1410,
        'ParameterID' : 12613,
        'Time' : '2014-07-14 17:45:00',
        'expected' : {
                "chemistry": "",
                "lab_no": ["64950-3633"],
                "gram_stain": "Yeast",
                "red cell morphology": "",
                "text": "\nBLOOD CULTURE MICROBIOLOGY\n\nLab No.    :  64950-3633\nMicro No.  :  GC14M53749\n\nCollected  :  17:45  14-Jul-14\nWard       :  Intensive Care Unit D4 (GCUH)\nRegistered :  17:57  14-Jul-14\n\nSpecimen   :  Arterial Line\n\nPositive Bottles :  1 of 2\nGrowth After     :  70.9 hrs\n\nGram Stain :  Yeast\n\n\nCulture    :\n\n                   Candida albicans\n\n     Antibiotic Abbreviations Guide:\n\n\n\n              Please see MIC results for (additional) susceptibility data.\n\n",
                "comments": "",
                "mrsa_screen": "",
                "differential": "",
                "report": ["BLOOD CULTURE MICROBIOLOGY"],
                "collected": ["17:45  14-Jul-14"],
                "num_tubes": [],
                "casts": "",
                "ward": ["Intensive Care Unit D4 (GCUH)"],
                "registered": ["17:57  14-Jul-14"],
                "supernatant": [],
                "specimen": "Arterial Line\n\nPositive Bottles :  1 of 2\nGrowth After     :  70.9 hrs",
                "culture": {
                      "other": ["Candida albicans",],
                      "text": "Candida albicans\n\n     Antibiotic Abbreviations Guide:\n\n\n\n              Please see MIC results for (additional) susceptibility data.",
                      "abbreviations": {},
                      "notes": "Please see MIC results for (additional) susceptibility data.",
                      "vals": {}
                },
                "cell_count": "",
                "volume": [],
                "microscopy": "",
                "micro_no": ["GC14M53749"],
                "appearance": []
              },
    },


###################################################################################################################
6116 : {

        'PatientID' : 1489,
        'ParameterID' : 12613,
        'Time' : '2014-07-20 12:30:00',
        'expected' : {
                "microscopy": "",
                "report": ["BLOOD CULTURE MICROBIOLOGY"],
                "collected": ["12:30  20-Jul-14"],
                "text": "\nBLOOD CULTURE MICROBIOLOGY\n\nLab No.    :  64969-1892\nMicro No.  :  GC14M55295\n\nCollected  :  12:30  20-Jul-14\nWard       :  Intensive Care Unit D4 (GCUH)\nRegistered :  13:13  20-Jul-14\n\n\n\nPositive Bottles :  2 of 2\nGrowth After     :  13.6 hours\n\nGram Stain :  Gram neg. bacilli\n\n\nCulture    :\n                                                 SXT GEN CIP MER\n             Enterobacter aerogenes               S   S   S   S\n\n\n\n\n\n     Antibiotic Abbreviations Guide:\n     SXT     Co-trimoxazole\n     GEN     Gentamicin\n     CIP     Ciprofloxacin\n     MER     Meropenem\n\n\n\n              Susceptibility to penicillins and first, second, and third\n              generation cephalosporins are not reported. Clinically this\n              isolate should be considered RESISTANT to these agents due to\n              its ability to produce broad spectrum beta-lactamase.",
                "gram_stain": "Gram neg. bacilli",
                "mrsa_screen": "",
                "comments": "",
                "cell_count": "",
                "volume": [],
                "casts": "",
                "registered": ["13:13  20-Jul-14"],
                "red cell morphology": "",
                "lab_no": ["64969-1892"],
                "specimen": "",
                "num_tubes": [],
                "ward": ["Intensive Care Unit D4 (GCUH)"],
                "supernatant": [],
                "micro_no": ["GC14M55295"],
                "culture": {
                    "other": [],
                    "text": "SXT GEN CIP MER\n             Enterobacter aerogenes               S   S   S   S\n\n\n\n\n\n     Antibiotic Abbreviations Guide:\n     SXT     Co-trimoxazole\n     GEN     Gentamicin\n     CIP     Ciprofloxacin\n     MER     Meropenem\n\n\n\n              Susceptibility to penicillins and first, second, and third\n              generation cephalosporins are not reported. Clinically this\n              isolate should be considered RESISTANT to these agents due to\n              its ability to produce broad spectrum beta-lactamase.",
                    "abbreviations": {
                        "MER": "Meropenem",
                        "CIP": "Ciprofloxacin",
                        "GEN": "Gentamicin",
                        "SXT": "Co-trimoxazole"
                    },
                    "notes": "Susceptibility to penicillins and first, second, and third generation cephalosporins are not reported. Clinically this isolate should be considered RESISTANT to these agents due to its ability to produce broad spectrum beta-lactamase.",
                    'vals': {
                        'Enterobacter aerogenes': {'resistance': {'MER': 'S', 'CIP': 'S', 'GEN': 'S', 'SXT': 'S'}}
                        },
                },
                "chemistry": "",
                "differential": "",
                "appearance": []
              },
    },




}



class TestBloodMicrobiology(unittest.TestCase):


    def setUp(self):
        # Displays the object diff correctly
        self.maxDiff = None






    # Can run this test on its own:
        #    python3 test_blood_microbiology.py TestBloodMicrobiology.test_specific_report

    def test_specific_report(self):
        test = 1280
        test_data = blood_test_cases[test]

        row = df.iloc[test]

        # Check row data
        for f in ['PatientID', 'ParameterID', 'Time']:
            self.assertEqual(row[f], test_data[f])

        # check json result generated by extraction
        json = extract_value_report_as_json(row['ValueNew'])
        print("result:",json)
        self.assertEqual(json[0], test_data['expected'])








    # Can run this test on its own:
    #    python3 test_urine_microbiology.py TestUrineMicrobiology.test_extraction

    def test_extraction(self):
        for row in list(blood_test_cases.keys()):
            with self.subTest(row=row):
                test_data = blood_test_cases[row]
                row = df.iloc[row]

                # Check row data
                for f in ['PatientID', 'ParameterID', 'Time']:
                    self.assertEqual(row[f], test_data[f])

                # check json result generated by extraction
                json = extract_value_report_as_json(row['ValueNew'])

                self.assertEqual(json[0], test_data['expected'])









if __name__ == '__main__':
    unittest.main()
