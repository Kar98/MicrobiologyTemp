from report_extract.report_extract import CultureParser, MultiResistanceReportExtractor, MicrobiologyReportExtractor
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


def getReport(reportlist, reportname: str) -> Report:
    for r in reportlist:
        if reportname in r.jsonObj['report']:
            return r

def test(reports):
    # Stats:
    uniques = ri.getUniqueReportTypes(reportList)
    print(uniques)

    stats = ri.getReportsForTesting(reports)
    print('min: {0}, max: {1}, colons: {2}'.format(stats[0].csvIndex, stats[1].csvIndex, stats[2].csvIndex))
    print(json.dumps(reports[0].jsonObj))
    writeFile('out.txt', reports[0].rawdata)

    min = ri.generateSingleReport(reportList, stats[0].csvIndex)
    max = ri.generateSingleReport(reportList, stats[1].csvIndex)
    colon = ri.generateSingleReport(reportList, stats[2].csvIndex)

    print(json.dumps(getReport(min, reportname).jsonObj))
    writeFile('min.txt', getReport(min, reportname).rawdata)
    print(json.dumps(getReport(max, reportname).jsonObj))
    writeFile('max.txt', getReport(max, reportname).rawdata)
    print(json.dumps(getReport(colon, reportname).jsonObj))
    writeFile('colon.txt', getReport(colon, reportname).rawdata)


df = loadFile()
reptypes = ReportTypes().cultureStruct
validator = JsonValidator()
urineName = 'URINE MICROBIOLOGY'
bloodName = 'BLOOD CULTURE MICROBIOLOGY'
catherName = 'CATHETER TIP MICROBIOLOGY'
cereName = 'CEREBROSPINAL FLUID MICROBIOLOGY'
superfiName = 'MICROBIOLOGY FROM SUPERFICIAL SITES'
multiName = 'MULTI-RESISTANT ORGANISM SCREEN'
faecesName = 'FAECES MICROBIOLOGY'
bodyName = 'BODY FLUID EXAMINATION'
diffName = 'C difficile screening'
eentName = 'EYE, EAR, NOSE, THROAT MICROBIOLOGY'
bacterialName = 'Bacterial Antigens'
mycologyName = 'MYCOLOGY'
mbactName = 'MYCOBACTERIOLOGY'
genName = 'GENITAL MICROBIOLOGY'
opName = 'MICROBIOLOGY FROM OPERATIVE/INVASIVE SPECIMENS'
reportname = diffName

#Load data
#reportList = df['ValueNew']
reportList = df['ValueNew'].head(10000)

ri = ReportInfo()

#tmp = ri.generateSingleReport(reportList,750)

us = ri.getUniqueReportTypes(reportList)
#print(us)


# TODO:
# - Create more report parsers for the rest of the reports
# - Redesign the structure of the base report extracter (MicrobiologyReportExtractor). Currently it pulls alot of info that the other reports don't have. It would be best to have it pull all the common data, then get the reports that need the extra data to use the addSectionHeadColon/addSectionHead functions to control the extra fields. Part of this redesign should be to have every field that gets extracted to be able to get overloaded.
# - Write some more unit tests for the different sections that get extracted (eg, gram stain, microscopy etc.)
# - Add in the pytyping syntax to make it clear what each function does. Currently it's very difficult based on the naming conventions (str vs list vs dict vs dataframe)
# - Ensure all fields are captured in a proper format, rather than a basic string. It causes some fields to be printed as ' texthere \n more text here '. New TextParser class can be used to help with this.(write unit test to check for this)



# main()
reports = ri.generateLimitedReportList(reportList,reportname)
#reports = ri.generateReportList(reportList)
print('total {0}'.format(len(reports)))
print(json.dumps(reports[0].jsonObj))

#test(reports)



#test
#test(reports)


print('done')