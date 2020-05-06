# Tests for Urine Microbiology report extraction


import unittest

# Features to test
from report_extract import extract_value_report_as_json



import pandas as pd
import re


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




urine_test_cases = {


###################################################################################################################
2 : {

        'PatientID' : 4,
        'ParameterID' : 12613,
        'Time' : '2013-09-27 00:00:00',
        'expected' : [{
                    'chemistry': {'text': '', 'vals': []},
                    "specimen": "Urine",
                    "red cell morphology": "",
                    "casts": "",
                    "microscopy": {
                      "vals": [
                        {"val": "< 10", "unit": "x10^6/L", "label": "Leucocytes", "rr": "RR ( < 10 )"},
                        {"val": "< 10", "unit": "x10^6/L", "label": "Erythrocytes", "rr": "RR ( < 10 )"},
                        {"val": "< 10", "unit": "x10^6/L", "label": "Epithelials", "rr": ""}
                      ],
                      "text": "Leucocytes     < 10     x10^6/L RR ( < 10 )\nErythrocytes   < 10     x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L",
                      "other": []
                    },
                    "ward": ["ICU~GCH"],
                    "micro_no": [],
                    "report": ["URINE MICROBIOLOGY"],
                    "collected": ["??:??  27-Sep-13"],
                    "registered": ["12:14  27-Sep-13"],
                    "lab_no": ["58089-5987"],
                    "comments": "",
                    "culture": {
                        "abbreviations": {},
                        "notes": "",
                        "text": "No growth",
                        "vals": {},
                        'other': ["No growth"],
                    },
                  }],

    },


###################################################################################################################
263 : {

        'PatientID' : 143,
        'ParameterID' : 12613,
        'Time' : '2013-11-05 20:30:00',
        'expected' : [{
                        'chemistry': {'text': '', 'vals': []},
                        "red cell morphology": "",
                        "casts": "",
                        "comments": "Specimen resembles frank pus. Unsuitable for cell count.\n          Culture only performed.",
                        "registered": ["21:28  05-Nov-13"],
                        "micro_no": [],
                        "lab_no": ["59507-4319"],
                        "collected": ["20:30  05-Nov-13"],
                    "culture": {
                        "abbreviations": {
                            'AMP': 'Ampi(amoxy)cillin',
                            'AUG': "Amox/Clavulanate",
                            'CFZ': 'Cefazolin',
                            'GEN': 'Gentamicin',
                            'NIT': 'Nitrofurantoin',
                            'TMP': 'Trimethoprim',
                            'TOB': 'Tobramycin',
                        },
                        "notes": "",
                        'other': [],
                        "text": "Mixed skin flora 10^7 - 10^8/L\n\n\n\n                                                           AMP AUG CFZ TMP\n                             Proteus vulgaris > 10^8/L      R   S   R   S\n                        Enterococcus faecalis > 10^8/L      S\n\n                                                           NIT GEN\n                             Proteus vulgaris > 10^8/L      R   S\n                        Enterococcus faecalis > 10^8/L      S\n\n\n\n     Antibiotic Abbreviations Guide:\n     AMP     Ampi(amoxy)cillin          AUG     Amox/Clavulanate\n     TMP     Trimethoprim               CFZ     Cefazolin\n     TOB     Tobramycin                 NIT     Nitrofurantoin\n                                        GEN     Gentamicin",
                        'vals': {
                            'Enterococcus faecalis > 10^8/L': {'resistance': {'AMP': 'S','NIT': 'S'}},
                            'Mixed skin flora 10^7 - 10^8/L': {'resistance': {}},
                            'Proteus vulgaris > 10^8/L': {'resistance': {'AMP': 'R', 'AUG': 'S', 'CFZ': 'R', 'GEN': 'S', 'NIT': 'R', 'TMP': 'S'}}},
                    },
                        "specimen": "Urine Nephrostomy",
                        "microscopy": {
                          "vals": [
                                    {'unit': 'x10^6/L', 'val': '>>500', 'label': 'Leucocytes', "rr": "RR ( < 10 )"},
                                    {'unit': 'x10^6/L', 'val': '>>500', 'label': 'Erythrocytes', "rr": "RR ( < 10 )"}
                                  ],
                          "other": [],
                          "text": "Leucocytes     >>500    x10^6/L RR ( < 10 )\nErythrocytes   >>500    x10^6/L RR ( < 10 )"
                        },
                        "report": ["URINE MICROBIOLOGY"],
                        "ward": ["GICU~GCUH"]
                    }],

    },


###################################################################################################################
309 : {

        'PatientID' : 168,
        'ParameterID' : 12613,
        'Time' : '2013-12-09 09:30:00',
        'expected' : [{
            'chemistry': {'text': '', 'vals': []},
            "red cell morphology": "",
            "microscopy": {
              "text": "",
              "vals": [],
              "other": []
            },
            "micro_no": [],
            "ward": ["GICU~GCUH"],
            "comments": "",
            "casts": "",
            "lab_no": ["60952-5021"],
            "registered": ["10:37  09-Dec-13"],
            "specimen": "Urine",
            "report": ["URINE MICROBIOLOGY"],
            "culture": {
                "abbreviations": {},
                "notes": "",
                'other': ["See lab #58467-8997 collected Dec. 8 for culture results."],
                "text": "See lab #58467-8997 collected Dec. 8 for culture results.",
                "vals": {}
            },
            "collected": ["09:30  09-Dec-13"]
          }],

    },


###################################################################################################################
575 : {

        'PatientID' : 38,
        'ParameterID' : 12613,
        'Time' : '2013-10-19 05:00:00',
        'expected' : [{
            'chemistry': {'text': '', 'vals': []},
            "red cell morphology": "",
            'micro_no': [],
            'collected': ['05:00  19-Oct-13'],
            'registered': ['05:42  19-Oct-13'],
            'ward': ['GICU~GCUH'],
            "casts": "",
            'report': ['URINE MICROBIOLOGY'],
            'specimen': 'Urine Catheter Collection',
            'comments': 'Probable catheter colonisation. Suggest removal of\n          catheter. Antibiotic therapy recommended only if\n          significant symptoms are present.',
            "culture": {
                "abbreviations": {
                    'TMP': 'Trimethoprim',
                    'NIT': 'Nitrofurantoin',
                    'GEN': 'Gentamicin',
                },
                "notes": "Isolate 1: Susceptibility to penicillins and first, second,\n            and third generation cephalosporins are not reported.\n            Clinically this isolate should be considered RESISTANT to\n            these agents due to its ability to produce broad spectrum\n            beta-lactamase.",
                "text": "TMP NIT GEN\n                                 Hafnia alvei > 10^8/L      S   S   S\n                                  Candida sp. 10^7 - 10^8/L\n\n\n     Antibiotic Abbreviations Guide:\n     TMP     Trimethoprim               NIT     Nitrofurantoin\n     GEN     Gentamicin\n\n\n\n            Isolate 1: Susceptibility to penicillins and first, second,\n            and third generation cephalosporins are not reported.\n            Clinically this isolate should be considered RESISTANT to\n            these agents due to its ability to produce broad spectrum\n            beta-lactamase.",
                'other': [],
                'vals': {'Candida sp. 10^7 - 10^8/L': {'resistance': {}},
                        'Hafnia alvei > 10^8/L': {'resistance': {'GEN': 'S', 'NIT': 'S', 'TMP': 'S'}}},
            },
            'lab_no': ['61009-2982'],
            'microscopy': {
                'vals': [
                    {'unit': 'x10^6/L', 'val': '70', 'label': 'Leucocytes', "rr": "RR ( < 10 )"},
                    {'unit': 'x10^6/L', 'val': '< 10', 'label': 'Erythrocytes', "rr": "RR ( < 10 )"},
                    {'unit': 'x10^6/L', 'val': '< 10', 'label': 'Epithelials', "rr": ""}],
                'text': 'Leucocytes       70     x10^6/L RR ( < 10 )\nErythrocytes   < 10     x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L\nOther:         Bacteria 3+\n-              Yeast 1+',
                'other': [
                    {'val': '3+', 'label': 'Bacteria'},
                    {'val': '1+', 'label': 'Yeast'}]}
        }]

    },


###################################################################################################################
596 : {

        'PatientID' : 74,
        'ParameterID' : 12613,
        'Time' : '2013-10-21 14:00:00',
        'expected' : [{
                "micro_no": [],
                "specimen": "Urine",
                "ward": ["GICU~GCUH"],
                "registered": ["14:39  21-Oct-13"],
                "lab_no": ["58041-0665"],
                "culture": {
                  "text": "PEN FLU AMP CFZ\n                        Staphylococcus aureus 10^7 - 10^8/L R   S   R   S\n           Streptococcus agalactiae (Group B) 10^6 - 10^7/L\n\n                                                           NIT\n                        Staphylococcus aureus 10^7 - 10^8/L S\n           Streptococcus agalactiae (Group B) 10^6 - 10^7/L\n\n\n\n     Antibiotic Abbreviations Guide:\n     PEN     Penicillin G               FLU     Di(Flu)cloxacillin\n     AMP     Ampi(amoxy)cillin          NIT     Nitrofurantoin\n     CFZ     Cefazolin\n\n\n\n            Isolate 1: Consider the possibility of staphylococcal\n            bacteraemia or complicated UTI (foreign body or\n            obstruction).  Isolate 2: Group B streptococci are\n            susceptible to penicillins and cephalosporins. If\n            susceptibility results for other agents are required,\n            please contact the laboratory within 24 hours.",
                  "abbreviations": {
                        "FLU": "Di(Flu)cloxacillin",
                        "NIT": "Nitrofurantoin",
                        "AMP": "Ampi(amoxy)cillin",
                        "PEN": "Penicillin",
                        "CFZ": "Cefazolin"
                  },
                  'other': [],
                  'vals': {'Staphylococcus aureus 10^7 - 10^8/L': {'resistance': {'AMP': 'R', 'CFZ': 'S', 'FLU': 'S', 'NIT': 'S', 'PEN': 'R'}},
                        'Streptococcus agalactiae (Group B) 10^6 - 10^7/L': {'resistance': {}}},
                  "notes": "Isolate 1: Consider the possibility of staphylococcal\n            bacteraemia or complicated UTI (foreign body or\n            obstruction).  Isolate 2: Group B streptococci are\n            susceptible to penicillins and cephalosporins. If\n            susceptibility results for other agents are required,\n            please contact the laboratory within 24 hours."
                },
                "collected": ["14:00  21-Oct-13"],
                "report": ["URINE MICROBIOLOGY"],
                "red cell morphology": "",
                "chemistry": {
                  "text": "",
                  "vals": []
                },
                "casts": "",
                "microscopy": {
                  "text": "Leucocytes      280     x10^6/L RR ( < 10 )\nErythrocytes   > 500    x10^6/L RR ( < 10 )\nEpithelials    <  10    x10^6/L",
                  "vals": [
                    { "rr": "RR ( < 10 )", "val": "280", "unit": "x10^6/L", "label": "Leucocytes" },
                    { "rr": "RR ( < 10 )", "val": "> 500", "unit": "x10^6/L", "label": "Erythrocytes" },
                    { "rr": "", "val": "<  10", "unit": "x10^6/L", "label": "Epithelials" }
                  ],
                  "other": []
                },
                "comments": ""
              }],

    },


###################################################################################################################
927 : {

    'PatientID' : 313,
    'ParameterID' : 12613,
    'Time' : '2013-12-23 10:46:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "microscopy": {
          "text": "Erythrocytes   >>500    x10^6/L\n                                RR ( < 10 )",
          "vals": [
            {"label": "Erythrocytes", "val": ">>500", "unit": "x10^6/L", "rr": "RR ( < 10 )"}
          ],
          "other": []
        },
        "micro_no": [],
        "ward": ["GICU~GCUH"],
        "comments": "Specimen resembles frank blood. Unsuitable for Cell Count.\n          Culture only.",
        "casts": "",
        "lab_no": ["61013-0546"],
        "registered": ["12:04  23-Dec-13"],
        "specimen": "Urine",
        "report": ["URINE MICROBIOLOGY"],
        "culture": {
            "abbreviations": {},
            "notes": "",
            'other': ["No growth"],
            "text": "No growth",
            "vals": {}
        },

        "collected": ["10:45  23-Dec-13"]
      }],

},


###################################################################################################################
933 : {

    'PatientID' : 313,
    'ParameterID' : 12613,
    'Time' : '2013-12-30 09:01:00',
    'expected' : [{
            "registered": ["10:49  30-Dec-13"],
            "chemistry": {
              "vals": [],
              "text": ""
            },
            "ward": ["GICU~GCUH"],
            "micro_no": [],
            "casts": "",
            "lab_no": ["60824-1382"],
            "specimen": "Urine Catheter Collection",
            "comments": "Probable catheter colonisation. Suggest removal of\n          catheter. Antibiotic therapy recommended only if\n          significant symptoms are present.",
            "microscopy": {
              "vals": [
                { "rr": "RR ( < 10 )", "unit": "x10^6/L", "val": "> 500", "label": "Leucocytes" },
                { "rr": "RR ( < 10 )", "unit": "x10^6/L", "val": "> 500", "label": "Erythrocytes" },
                { "rr": "", "unit": "x10^6/L", "val": "< 10", "label": "Epithelials" }
              ],
              "text": "Leucocytes     > 500    x10^6/L RR ( < 10 )\nErythrocytes   > 500    x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L\nOther:         Bacteria 3+",
              "other": [
                { "val": "3+", "label": "Bacteria" }
              ]
            },
            "collected": ["09:00  30-Dec-13"],
            "red cell morphology": "",
            "report": ["URINE MICROBIOLOGY"],
            "culture": {
              "vals": {
                "Klebsiella pneumoniae > 10^8/L": { "resistance": { "GEN": "S", "AMP": "R", "NIT": "R", "AUG": "S", "TMP": "S", "CFZ": "S" }
                }
              },
              "text": "AMP AUG CFZ TMP\n                        Klebsiella pneumoniae > 10^8/L      R   S   S   S\n\n                                                           NIT GEN\n                        Klebsiella pneumoniae > 10^8/L      R   S\n\n\n\n     Antibiotic Abbreviations Guide:\n     AMP     Ampi(amoxy)cillin          AUG     Amox/Clavulanate\n     TMP     Trimethoprim               CFZ     Cefazolin\n     GEN     Gentamicin                 NIT     Nitrofurantoin",
              "other": [],
              "abbreviations": {
                "GEN": "Gentamicin",
                "AMP": "Ampi(amoxy)cillin",
                "NIT": "Nitrofurantoin",
                "AUG": "Amox/Clavulanate",
                "TMP": "Trimethoprim",
                "CFZ": "Cefazolin"
              },
              "notes": ""
            }
          }],

},


###################################################################################################################
3339 : {

    'PatientID' : 1001,
    'ParameterID' : 12613,
    'Time' : '2014-05-16 16:30:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "microscopy": {
          "text": "Erythrocytes   > 500    x10^6/L\n                                RR ( < 10 )",
          "vals": [
            { "label": "Erythrocytes", "val": "> 500", "unit": "x10^6/L", 'rr': 'RR ( < 10 )' }
          ],
          "other": []
        },
        "micro_no": [],
        "ward": ["GED~GCUH"],
        "comments": "Heavily blood stained specimen received. Unsuitable for\n          cell count. Culture only performed. \n          Coagulase negative staphylococcus rarely cause UTI; they\n          colonise in-dwelling\n          catheters and may be present transiently following\n          manipulation of the renal tract.",
        "lab_no": ["65238-5459"],
        "registered": ["18:58  16-May-14"],
        "specimen": "Urine",
        "report": ["URINE MICROBIOLOGY"],
        "casts": "",
        "culture": {
            "abbreviations": {
                'AMP': 'Ampi(amoxy)cillin',
                'CFZ': 'Cefazolin',
                'FLU': 'Di(Flu)cloxacillin',
                'NIT': 'Nitrofurantoin',
                'TEC': 'Teicoplanin',
                'VA': 'Vancomycin'
            },
            "notes": "",
            'other': [],
            "text": "FLU AMP CFZ NIT\n                       Staphylococcus capitis 10^7 - 10^8/L R   R   R   S\n\n                                                           VA\n                       Staphylococcus capitis 10^7 - 10^8/L S\n\n\n\n     Antibiotic Abbreviations Guide:\n     AMP     Ampi(amoxy)cillin          FLU     Di(Flu)cloxacillin\n     CFZ     Cefazolin                  VA      Vancomycin\n     NIT     Nitrofurantoin\n     TEC     Teicoplanin",
            'vals': {'Staphylococcus capitis 10^7 - 10^8/L': {'resistance': {'AMP': 'R','CFZ': 'R','FLU': 'R','NIT': 'S','VA': 'S'}}},
        },

        "collected": ["16:30  16-May-14"]
      }],

},



###################################################################################################################
15105 : {

        'PatientID' : 3028,
        'ParameterID' : 12613,
        'Time' : '2015-03-26 08:20:00',
        'expected' : [{
            "comments": "Consistent with UTI if midstream (NOT CATHETER) collection.",
            "lab_no": ["69252-6454"],
            "report": ["URINE MICROBIOLOGY"],
            "culture": {
                "abbreviations": {
                    'AMP': 'Ampi(amoxy)cillin',
                    'NIT': 'Nitrofurantoin'
                },
                "notes": "Resistant to high level Gentamicin.",
                "text": "AMP NIT\n                        Enterococcus faecalis 10^6 - 10^7/L S   S\n\n\n     Antibiotic Abbreviations Guide:\n     AMP     Ampi(amoxy)cillin          NIT     Nitrofurantoin\n\n\n\n            Resistant to high level Gentamicin.",
                'other': [],
                "vals": {
                    'Enterococcus faecalis 10^6 - 10^7/L': {
                        'resistance': { 'AMP': 'S', 'NIT': 'S'}
                        }}
            },
            "collected": ["08:20  26-Mar-15"],
            "specimen": "Urine",
            "micro_no": [],
            "ward": ["GGMU~GCUH"],
            "casts": "No casts seen in centrifuged deposit",
            "red cell morphology": "Suggestive of NON-glomerular bleeding",
            "registered": ["08:46  26-Mar-15"],
            "microscopy": {
              "other": [
                { "label": "Bacteria", "val": "1+" }
              ],
              "vals": [
                { "unit": "x10^6/L", "label": "Leucocytes", "rr": "RR ( < 10 )", "val": "> 500" },
                { "unit": "x10^6/L", "label": "Erythrocytes", "rr": "RR ( < 10 )", "val": "> 500" },
                { "unit": "x10^6/L", "label": "Epithelials", "rr": "", "val": "<  10" }
              ],
              "text": "Leucocytes     > 500    x10^6/L RR ( < 10 )\nErythrocytes   > 500    x10^6/L RR ( < 10 )\nEpithelials    <  10    x10^6/L\nOther:         Bacteria 1+"
            },
            'chemistry': {'text': '', 'vals': []},
          }]

    },



###################################################################################################################
21415 : {

    'PatientID' : 4086,
    'ParameterID' : 12613,
    'Time' : '2015-09-11 14:25:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "microscopy": {
            "other": [
                { "label": "Yeast", "val": "2+" }
            ],
            "text": "Leucocytes     > 500    x10^6/L RR ( < 10 )\nErythrocytes   > 500    x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L\nOther:         Yeast 2+",
            "vals": [
                { "rr": "RR ( < 10 )", "unit": "x10^6/L", "label": "Leucocytes", "val": "> 500" },
                { "rr": "RR ( < 10 )", "unit": "x10^6/L", "label": "Erythrocytes", "val": "> 500" },
                { "rr": "", "unit": "x10^6/L", "label": "Epithelials", "val": "< 10" }
            ]
        },
        "comments": "",
        "casts": "Uncentrifuged\n        Hyaline       1       /lpf",
        "culture": {
            "abbreviations": {},
            "notes": "",
            'other': [],
            "text": "Candida sp. > 10^8/L",
            'vals': {'Candida sp. > 10^8/L': {'resistance': {}}},
        },
        "report": [ "URINE MICROBIOLOGY" ],
        "specimen": "Urine",
        "ward": ["GRESP~GCUH"],
        "registered": ["14:33  11-Sep-15"],
        "micro_no": [],
        "collected": ["14:25  11-Sep-15"],
        "lab_no": ["70668-7658"]
      }],

},



###################################################################################################################
26176 : {

    'PatientID' : 4869,
    'ParameterID' : 12613,
    'Time' : '2015-12-24 10:40:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "report": ["URINE MICROBIOLOGY"],
        "specimen": "Urine",
        "comments": "",
        "casts": "",
        "lab_no": ["73195-7286"],
        "microscopy": {
          "text": "",
          "vals": [],
          "other": []
        },
        "collected": ["10:40  24-Dec-15"],
        "micro_no": [],
        "culture": {
            "abbreviations": {},
            "notes": "",
            "text": "",
            "other": [],
            "vals": {}
        },
        "ward": ["GVSNS~GCUH"],
        "registered": ["11:08  24-Dec-15"]
              }],

},



###################################################################################################################
32725 : {

    'PatientID' : 6009,
    'ParameterID' : 12613,
    'Time' : '2016-07-08 17:00:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "micro_no": [],
        "lab_no": ["77399-1566"],
        "report": ["URINE MICROBIOLOGY"],
        "microscopy": {
          "text": "Leucocytes      170     x10^6/L RR ( < 10 )\nErythrocytes     10     x10^6/L RR ( < 10 )\nEpithelials      10     x10^6/L\nOther:         Debris 2+",
          "vals": [
            { "unit": "x10^6/L", "rr": "RR ( < 10 )", "val": "170", "label": "Leucocytes" },
            { "unit": "x10^6/L", "rr": "RR ( < 10 )", "val": "10", "label": "Erythrocytes" },
            { "unit": "x10^6/L", "rr": "", "val": "10", "label": "Epithelials" }
          ],
          "other": [
            { "val": "2+", "label": "Debris" }
          ]
        },
        "casts": "",
        "comments": "Possible UTI, note raised epithelial cells indicating\n          contamination.",
        "specimen": "Urine ? Collection",
        "ward": ["RICU~ROH"],
        "registered": ["17:27  08-Jul-16"],
        "collected": ["17:00  08-Jul-16"],
        "culture": {
            "abbreviations": {
                'AMP': 'Ampi(amoxy)cillin',
                'AUG': 'Amox/Clavulanate',
                'CFZ': 'Cefazolin',
                'CIP': 'Ciprofloxacin',
                'GEN': 'Gentamicin',
                'NIT': 'Nitrofurantoin',
                'NOR': 'Norfloxacin',
                'TMP': 'Trimethoprim',
                'TOB': 'Tobramycin'
            },
            "other": [],
            "notes": "",
            "text": "AMP AUG CFZ TMP\n                        Escherichia coli > 10^8/L       R   R   S   R\n\n                                                       NIT GEN TOB CIP\n                        Escherichia coli > 10^8/L       S   R   S   R\n\n                                                       NOR\n                        Escherichia coli > 10^8/L       R\n\n\n\n\n     Antibiotic Abbreviations Guide:\n     AMP     Ampi(amoxy)cillin          AUG     Amox/Clavulanate\n     TMP     Trimethoprim               CFZ     Cefazolin\n     GEN     Gentamicin                 NIT     Nitrofurantoin\n     CIP     Ciprofloxacin              TOB     Tobramycin\n                                        NOR     Norfloxacin",
            'vals': {'Escherichia coli > 10^8/L': {'resistance': {'AMP': 'R', 'AUG': 'R', 'CFZ': 'S', 'CIP': 'R', 'GEN': 'R', 'NIT': 'S', 'NOR': 'R', 'TMP': 'R','TOB': 'S'}}},
        },
      }],

},



###################################################################################################################
47981 : {

    'PatientID' : 8948,
    'ParameterID' : 12613,
    'Time' : '2017-06-16 14:05:00',
    'expected' : [{
        "microscopy": {
          "other": [
            { "val": "3+", "label": "Bacteria" },
            { "val": "scant", "label": "Yeast" }
          ],
          "vals": [
            { "unit": "x10^6/L", "val": "120", "label": "Leucocytes", "rr": "RR ( < 10 )" },
            { "unit": "x10^6/L", "val": "<  10", "label": "Erythrocytes", "rr": "RR ( < 10 )" },
            { "unit": "x10^6/L", "val": "10", "label": "Epithelials", "rr": "" }
          ],
          "text": "Leucocytes      120     x10^6/L RR ( < 10 )\nErythrocytes   <  10    x10^6/L RR ( < 10 )\nEpithelials      10     x10^6/L\nOther:         Bacteria 3+\n-              Yeast scant"
        },
        "ward": ["GICU~GCUH"],
        "report": ["URINE MICROBIOLOGY"],
        "culture": {
            "abbreviations": {
                'AMP': 'Ampi(amoxy)cillin',
                'NIT': 'Nitrofurantoin'
            },
            "notes": "",
            "other": [],
            "text": "AMP NIT\n                   Enterococcus faecalis > 10^8/L       S   S\n                             Candida sp. 10^7 - 10^8/L\n\n\n     Antibiotic Abbreviations Guide:\n     AMP     Ampi(amoxy)cillin          NIT     Nitrofurantoin",
            'vals': {'Candida sp. 10^7 - 10^8/L': {'resistance': {}},
                    'Enterococcus faecalis > 10^8/L': {'resistance': {'AMP': 'S', 'NIT': 'S'}}},
        },
        "registered": ["15:02  16-Jun-17"],
        "red cell morphology": "",
        "collected": ["14:05  16-Jun-17"],
        "specimen": "Urine",
        'chemistry': {'text': '', 'vals': []},
        "casts": "",
        "comments": "",
        "lab_no": ["77284-5337"],
        "micro_no": []
      }],

},



###################################################################################################################
51352 : {

    'PatientID' : 9686,
    'ParameterID' : 12613,
    'Time' : '2017-07-03 13:35:00',
    'expected' : [{
        "red cell morphology": "",
        "chemistry": {
            "text": "pH        6.0\nGlucose   Negative\nProtein   Trace\nLeuc/Est  Negative\nNitrite   Negative\nBlood     Trace\nKetones   Negative",
            "vals": [{'label': 'pH', 'val': '6.0'},
                      {'label': 'Glucose', 'val': 'Negative'},
                      {'label': 'Protein', 'val': 'Trace'},
                      {'label': 'Leuc/Est', 'val': 'Negative'},
                      {'label': 'Nitrite', 'val': 'Negative'},
                      {'label': 'Blood', 'val': 'Trace'},
                      {'label': 'Ketones', 'val': 'Negative'}
                    ]
        },
        "micro_no": [],
        "lab_no": ["77285-6108"],
        "report": ["URINE MICROBIOLOGY"],
        "microscopy": {
          "text": "Leucocytes       20     x10^6/L RR ( < 10 )\nErythrocytes     10     x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L\nOther:         Yeast 2+",
          "vals": [
            { "unit": "x10^6/L", "rr": "RR ( < 10 )", "val": "20", "label": "Leucocytes" },
            { "unit": "x10^6/L", "rr": "RR ( < 10 )", "val": "10", "label": "Erythrocytes" },
            { "unit": "x10^6/L", "rr": "", "val": "< 10", "label": "Epithelials" }
          ],
          "other": [
            { "val": "2+", "label": "Yeast" }
          ]
        },
        "casts": "",
        "comments": "",
        "specimen": "Urine",
        "ward": ["GICU~GCUH"],
        "registered": ["13:55  03-Jul-17"],
        "collected": ["13:35  03-Jul-17"],
        "culture": {
            "abbreviations": {},
            "notes": "",
            'other': [],
            "text": "Candida sp. 10^7 - 10^8/L",
            'vals': {'Candida sp. 10^7 - 10^8/L': {'resistance': {}}},
        },
      }],

},



###################################################################################################################
52873 : {

    'PatientID' : 9850,
    'ParameterID' : 12613,
    'Time' : '2017-07-12 12:00:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "report": ["URINE MICROBIOLOGY"],
        "specimen": "Urine Nephrostomy",
        "comments": "Nephrostomy side not specified on specimen. Heavily blood\n          stained specimen received. Unsuitable for cell count.\n          Culture only performed.",
        "lab_no": ["91576-0882"],
        "microscopy": {
          "text": "Erythrocytes   > 500    x10^6/L\n                                RR ( < 10 )",
          "vals": [
            { "val": "> 500", "unit": "x10^6/L", "rr": "RR ( < 10 )", "label": "Erythrocytes" }
          ],
          "other": []
        },
        "collected": ["12:00  12-Jul-17"],
        "casts": "",
        "micro_no": [],
        "culture": {
            "abbreviations": {
                'AMP': 'Ampi(amoxy)cillin',
                'AUG': 'Amox/Clavulanate',
                'CFZ': 'Cefazolin',
                'GEN': 'Gentamicin',
                'NIT': 'Nitrofurantoin',
                'TMP': 'Trimethoprim'
            },
            "notes": "",
            'other': [],
            "text": "AMP AUG CFZ TMP\n                   Klebsiella pneumoniae 10^7 - 10^8/L  R   S   S   S\n\n                                                       NIT GEN\n                   Klebsiella pneumoniae 10^7 - 10^8/L  R   S\n\n\n\n     Antibiotic Abbreviations Guide:\n     AMP     Ampi(amoxy)cillin          AUG     Amox/Clavulanate\n     TMP     Trimethoprim               CFZ     Cefazolin\n     GEN     Gentamicin                 NIT     Nitrofurantoin",
            'vals': {'Klebsiella pneumoniae 10^7 - 10^8/L': {'resistance': {'AMP': 'R', 'AUG': 'S', 'CFZ': 'S', 'GEN': 'S', 'NIT': 'R', 'TMP': 'S'}}},
        },
        "ward": ["GICU~GCUH"],
        "registered": ["15:05  12-Jul-17"]
          }],

},



###################################################################################################################
65520 : {

    'PatientID' : 11517,
    'ParameterID' : 12613,
    'Time' : '2018-03-17 10:45:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "report": ["URINE MICROBIOLOGY"],
        "specimen": "Urine ? Collection",
        "comments": "",
        "casts": "",
        "lab_no": ["94652-4377"],
        "microscopy": {
          "text": "Leucocytes       40     x10^6/L RR ( < 10 )\nErythrocytes    490     x10^6/L RR ( < 10 )\nEpithelials    <  10    x10^6/L",
          "vals": [
            { "val": "40", "unit": "x10^6/L", "rr": "RR ( < 10 )", "label": "Leucocytes" },
            { "val": "490", "unit": "x10^6/L", "rr": "RR ( < 10 )", "label": "Erythrocytes" },
            { "val": "<  10", "unit": "x10^6/L", "rr": "", "label": "Epithelials" }
          ],
          "other": []
        },
        "collected": ["10:45  17-Mar-18"],
        "micro_no": [],
        "culture": {
                    "abbreviations": {},
                    "notes": "",
                    "text": "No growth",
                    'other': ["No growth"],
                    "vals": {}
                },
        "ward": ["GVSNS~GCUH"],
        "registered": ["11:12  17-Mar-18"]
          }],

},



###################################################################################################################
73509 : {

    'PatientID' : 12668,
    'ParameterID' : 12613,
    'Time' : '2018-09-21 21:00:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "micro_no": [],
        "lab_no": ["20049-00492"],
        "report": ["URINE MICROBIOLOGY"],
        "microscopy": {
          "text": "Leucocytes     > 500    x10^6/L RR ( < 10 )\nErythrocytes     60     x10^6/L RR ( < 10 )\nEpithelials    <  10    x10^6/L\nOther:         Yeast 1+\n-              Spermatozoa 1+",
          "vals": [
            { "unit": "x10^6/L", "rr": "RR ( < 10 )", "val": "> 500", "label": "Leucocytes" },
            { "unit": "x10^6/L", "rr": "RR ( < 10 )", "val": "60", "label": "Erythrocytes" },
            { "unit": "x10^6/L", "rr": "", "val": "<  10", "label": "Epithelials" }
          ],
          "other": [
            { "val": "1+", "label": "Yeast" },
            { "val": "1+", "label": "Spermatozoa"  }
          ]
        },
        "casts": "",
        "comments": "",
        "specimen": "Urine Catheter Collection",
        "ward": [ "GNEUR~GCUH" ],
        "registered": ["22:04  21-Sep-18"],
        "collected": ["21:00  21-Sep-18"],
        "culture": {
            "abbreviations": {},
            "notes": "",
            "text": "Candida sp. 10^7 - 10^8/L",
            'other': [],
            'vals': {'Candida sp. 10^7 - 10^8/L': {'resistance': {}}},
        },
      }],

},


###################################################################################################################
86399 : {

    'PatientID' : 14793,
    'ParameterID' : 12613,
    'Time' : '2019-07-11 18:45:00',
    'expected' : [{
        'chemistry': {'text': '', 'vals': []},
        "red cell morphology": "",
        "microscopy": {
          "other": [
            { "label": "Yeast with hyphae", "val": "2+" }
          ],
          "text": "Leucocytes      350     x10^6/L RR ( < 10 )\nErythrocytes    390     x10^6/L RR ( < 10 )\nEpithelials    <  10    x10^6/L\nOther:         Yeast with\n               hyphae 2+",
          "vals": [
            { "rr": "RR ( < 10 )", "unit": "x10^6/L", "label": "Leucocytes", "val": "350" },
            { "rr": "RR ( < 10 )", "unit": "x10^6/L", "label": "Erythrocytes", "val": "390" },
            { "rr": "", "unit": "x10^6/L", "label": "Epithelials", "val": "<  10" }
          ]
        },
        "comments": "",
        "culture": {
            "abbreviations": {},
            "notes": "",
            "text": "Candida sp. 10^7 - 10^8/L",
            'other': [],
            'vals': {'Candida sp. 10^7 - 10^8/L': {'resistance': {}}},
        },
        "casts": "",
        "report": ["URINE MICROBIOLOGY"],
        "specimen": "Urine",
        "ward": ["GIMMU~GCUH"],
        "registered": ["18:50  11-Jul-19"],
        "micro_no": [],
        "collected": ["18:45  11-Jul-19"],
        "lab_no": ["20628-18348"]
      }],

},



}



class TestUrineMicrobiology(unittest.TestCase):


    def setUp(self):
        # Displays the object diff correctly
        self.maxDiff = None

    def test_Report_Unknown(self):
        # Test that a unknown eport is generated for particular text
        # row = df.iloc[575]
        text = "\nCould be anything unexpected here!\n\n"

        # result to be tested
        json = extract_value_report_as_json(text)

        # Checks
        expected = [{
            'error': 'Exception',
            'exception': 'Should be exactly one report type per section, found 0.',
            'text': '\nCould be anything unexpected here!\n\n',
        }]

        self.assertEqual(json, expected)





    def test_Report_text(self):
        # Test that a report is generated for particular text
        # row = df.iloc[575]
        text = "\nLab No : 61009-2982    Micro No :            Collected  : 05:00  19-Oct-13\n                                             Registered : 05:42  19-Oct-13\nURINE MICROBIOLOGY                           Ward of Collection:  GICU~GCUH\n\nSpecimen : Urine Catheter Collection\n\n\nMICROSCOPY\nLeucocytes       70     x10^6/L RR ( < 10 )\nErythrocytes   < 10     x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L\nOther:         Bacteria 3+\n-              Yeast 1+\n\n\n\n\nCULTURE:                                                   TMP NIT GEN\n                                 Hafnia alvei > 10^8/L      S   S   S\n                                  Candida sp. 10^7 - 10^8/L\n\n\n     Antibiotic Abbreviations Guide:\n     TMP     Trimethoprim               NIT     Nitrofurantoin\n     GEN     Gentamicin\n\n\n\n            Isolate 1: Susceptibility to penicillins and first, second,\n            and third generation cephalosporins are not reported.\n            Clinically this isolate should be considered RESISTANT to\n            these agents due to its ability to produce broad spectrum\n            beta-lactamase.\nCOMMENT:  Probable catheter colonisation. Suggest removal of\n          catheter. Antibiotic therapy recommended only if\n          significant symptoms are present."

        # result to be tested
        json = extract_value_report_as_json(text)

        # Checks
        expected = [{
            'chemistry': {'text': '', 'vals': []},
            "red cell morphology": "",
            'micro_no': [],
            "casts": "",
            'collected': ['05:00  19-Oct-13'],
            'registered': ['05:42  19-Oct-13'],
            'ward': ['GICU~GCUH'],
            'report': ['URINE MICROBIOLOGY'],
            'specimen': 'Urine Catheter Collection',
            'comments': 'Probable catheter colonisation. Suggest removal of\n          catheter. Antibiotic therapy recommended only if\n          significant symptoms are present.',
            "culture": {
                "abbreviations": {
                    "TMP": "Trimethoprim",
                    "NIT": "Nitrofurantoin",
                    "GEN": "Gentamicin",
                },
                "notes": "Isolate 1: Susceptibility to penicillins and first, second,\n            and third generation cephalosporins are not reported.\n            Clinically this isolate should be considered RESISTANT to\n            these agents due to its ability to produce broad spectrum\n            beta-lactamase.",
                "text": "TMP NIT GEN\n                                 Hafnia alvei > 10^8/L      S   S   S\n                                  Candida sp. 10^7 - 10^8/L\n\n\n     Antibiotic Abbreviations Guide:\n     TMP     Trimethoprim               NIT     Nitrofurantoin\n     GEN     Gentamicin\n\n\n\n            Isolate 1: Susceptibility to penicillins and first, second,\n            and third generation cephalosporins are not reported.\n            Clinically this isolate should be considered RESISTANT to\n            these agents due to its ability to produce broad spectrum\n            beta-lactamase.",
                "other": [],
                'vals': {
                    'Candida sp. 10^7 - 10^8/L': {'resistance': {}},
                    'Hafnia alvei > 10^8/L': {'resistance': {'GEN': 'S', 'NIT': 'S', 'TMP': 'S'}}
                    },
            },
            'lab_no': ['61009-2982'],
            'microscopy': {
                'text': 'Leucocytes       70     x10^6/L RR ( < 10 )\nErythrocytes   < 10     x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L\nOther:         Bacteria 3+\n-              Yeast 1+',
                'vals': [
                    {'unit': 'x10^6/L', 'val': '70', 'label': 'Leucocytes', "rr": "RR ( < 10 )"},
                    {'unit': 'x10^6/L', 'val': '< 10', 'label': 'Erythrocytes', "rr": "RR ( < 10 )"},
                    {'unit': 'x10^6/L', 'val': '< 10', 'label': 'Epithelials', "rr": ""}],
                'other': [
                    {'val': '3+', 'label': 'Bacteria'},
                    {'val': '1+', 'label': 'Yeast'}]}
        }]

        self.assertEqual(json, expected)












    # Can run this test on its own:
    #    python3 test_urine_microbiology.py TestUrineMicrobiology.test_specific_report

    def test_specific_report(self):
        test = 15105
        test_data = urine_test_cases[test]

        row = df.iloc[test]

        # Check row data
        for f in ['PatientID', 'ParameterID', 'Time']:
            self.assertEqual(row[f], test_data[f])

        # check json result generated by extraction
        json = extract_value_report_as_json(row['ValueNew'])
        self.assertEqual(json, test_data['expected'])








    # Can run this test on its own:
    #    python3 test_urine_microbiology.py TestUrineMicrobiology.test_extraction

    def test_extraction(self):
        for row in list(urine_test_cases.keys()):
            with self.subTest(row=row):
                test_data = urine_test_cases[row]
                row = df.iloc[row]

                # Check row data
                for f in ['PatientID', 'ParameterID', 'Time']:
                    self.assertEqual(row[f], test_data[f])

                # check json result generated by extraction
                json = extract_value_report_as_json(row['ValueNew'])
                self.assertEqual(json, test_data['expected'])













    def test_Report_41604(self):
        # Picked as has high Erythrocytes

        # Labels verified by Kelvin Ross

        row = df.iloc[41604]


        # Check row
        self.assertEqual(row['PatientID'], 8286)
        self.assertEqual(row['ParameterID'], 12613)
        self.assertEqual(row['Time'], '2016-12-15 20:55:00')

        # result to be tested
        json = extract_value_report_as_json(row['ValueNew'])

        # Checks
        expected = {
            'chemistry': {'text': '', 'vals': []},
            "red cell morphology": "",
            "report": ["URINE MICROBIOLOGY"],
            "specimen": "Urine",
            "comments": "Resembles frank pus",
            "lab_no": ["79439-5062"],
            "microscopy": {
              "text": "Leucocytes     >>       x10^6/L RR ( < 10 )\nOther:         Yeast 3+",
              "vals": [
                { "val": ">>", "unit": "x10^6/L", "rr": "RR ( < 10 )", "label": "Leucocytes" }
              ],
              "other": [
                { "val": "3+", "label": "Yeast" }
              ]
            },
            "collected": [ "20:55  15-Dec-16" ],
            "micro_no": [],
            "casts": "",
            "culture": {
                "abbreviations": {},
                "notes": "",
                "other": ["            Please see MIC results for (additional) susceptibility","            data."],
                "text": "Candida albicans > 10^8/L\n\n\n\n\n\n\n            Please see MIC results for (additional) susceptibility\n            data.",
                'vals': {'Candida albicans > 10^8/L': {'resistance': {}}},
            },
            "ward": ["GREN~GCUH"],
            "registered": ["06:53  16-Dec-16"]
              }

        self.assertEqual(json[0], expected)












if __name__ == '__main__':
    unittest.main()
