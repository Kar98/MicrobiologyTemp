from report_extract.report_extract import CultureParser
from validators.json_validator import *
import logging
import pandas
import json
import MedicalReports.ReportValidation as rv
from MedicalReports.ReportingHelpers import ReportTypes
import matplotlib.pyplot as plt
from MedicalReports.ReportingHelpers import ReportInfo
from MedicalReports.Reports import Report
from test_report_extract import TestHighLevelScenarios


logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)
pandas.set_option('display.max_rows', None)
pandas.set_option('display.max_columns', None)

def loadFile():
    file = 'Data/Microbiology2_conv.csv'
    df = pandas.read_csv(file, sep='\t')
    df['ValueNew'] = df['ValueNew'].apply(lambda x: x.replace("||", "\n"))
    df['CommentsNew'] = df['CommentsNew'].apply(lambda x: x.replace("||", "\n"))
    return df

def getReport(list):
    for l in list:
        if l.culture.hasResistance():
            return l

def clearFile(file):
    f = open(file,"w")
    f.write('')
    f.close()

def writeFile(file,text):
    f = open(file,"a")
    f.write(text)
    f.close()

def makeUnique(arg):
    newset = set(arg)
    return list(newset)

def getReportWithResis(listOfReports, match = -1):
    matchesFound = 0
    if match == -1:
        matchesFound = 1
    for r in listOfReports:
        if r.culture.hasResistance():
            matchesFound += 1
            if(matchesFound == match):
                return r



df = loadFile()
reptypes = ReportTypes().cultureStruct
validator = JsonValidator()
urineName = 'URINE MICROBIOLOGY'
bloodName = 'BLOOD CULTURE MICROBIOLOGY'
catherName = 'CATHETER TIP MICROBIOLOGY'

bloodId = 4
catherId = 1161

reportList = df['ValueNew'].head(10000)

f = open('test.txt','r')
tblParser = CultureParser()
tblParser.getCulture(f.read())
f.close()

clearFile('output.txt')

print('done')