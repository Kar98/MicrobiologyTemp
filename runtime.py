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

def readFile(filepath):
    f = open(filepath, 'r')
    str = f.read()
    f.close()
    return str

def getReport(list):
    for l in list:
        if l.culture.hasCultures():
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
        if r.culture.hasCultures():
            matchesFound += 1
            if(matchesFound == match):
                return r

wordFreqDic = {
    "Hello": 56,
    "at" : 23 ,
    "test" : 43,
    "this" : 43
    }



df = loadFile()
reptypes = ReportTypes().cultureStruct
validator = JsonValidator()
urineName = 'URINE MICROBIOLOGY'
bloodName = 'BLOOD CULTURE MICROBIOLOGY'
catherName = 'CATHETER TIP MICROBIOLOGY'

bloodId = 4
catherId = 445

reportList = df['ValueNew'].head(10000)
tmp = reportList[0]
ri = ReportInfo()

#print(ri.generateSingleReport(reportList,79).toJson())



reports = ri.generateLimitedReportList(reportList,bloodName)
print('total parsed reports {0}'.format(len(reports)))
#reports = ri.generateReportList(reportList)

clearFile('myjson.txt')
clearFile('myraw.txt')
clearFile('jsonoutput.txt')

written = False
with open('jsonoutput.txt','a') as f:
    for r in reports:
        if 'No growth' in r.culture.notes:
            if written == False:
                writeFile('myjson.txt',r.toJson())
                writeFile('myraw.txt',r.rawdata)
                written = True

        f.write('{0}\n'.format(r.toJson()))



print('done')