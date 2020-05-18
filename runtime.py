from validators.json_validator import *
import logging
import pandas
#from MedicalReports.Reports import Report
from MedicalReports.ReportingHelpers import ReportTypes
import matplotlib.pyplot as plt
from MedicalReports.ReportingHelpers import ReportInfo

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

df = loadFile()
reptypes = ReportTypes().cultureStruct
validator = JsonValidator()
urineName = 'URINE MICROBIOLOGY'
bloodName = 'BLOOD CULTURE MICROBIOLOGY'

reportList = df['ValueNew'].head(1000)

cultureDF = pandas.DataFrame(columns=reptypes)

reportIdx = 0
reports = []


#for rep in reportList:
#    jsonval = extract_value_report_as_json(rep)[0]
#    reports.append(Report(jsonval))

info = ReportInfo()
reports = info.generateReportList(reportList)

resisDF = pandas.DataFrame(columns=ReportTypes().resistanceStruct)
resIndex = 0
for r in reports:
    if r.culture != None and len(r.culture.abbreviations) > 0:
        var = r.getCultureResistance()
        if len(var.values()) > 0:
            resisDF = pandas.concat([resisDF,info.flattenCulturesToDataframe(resIndex,var)])
            resIndex +=1

# Find the % of reports that have resistance - done
#repcount = len(reports)
#withResistanceCount = len(resisDF.groupby('resindex').count())
#print('Total : {0} With resistance : {1} As Percentage : {2}%'.format(repcount,withResistanceCount,math.trunc(withResistanceCount / repcount * 100)))

# Get the total count of resistances per report, and compare against another dataset - done
#print(reports[0].getCultureResistance())
# Need TotalReports, TotalCultures, TotalCulturesWithResistance
TotalReports = len(reports)
TotalCultures = 0
TotalCulturesWithResistance = 0

for r in reports:
    if r.culture is not None and len(r.culture.vals) > 0:
        TotalCultures += 1
        if r.culture.hasResistance():
            print(r.jsonObj)
            TotalCulturesWithResistance += 1
        else:
            print(r.jsonObj)
            pass
    else:
        #print(r.jsonObj)
        pass

print(TotalReports)
print(TotalCultures)
print(TotalCulturesWithResistance)

# Get the % of the Resistance value, and compare against the total

rCount = 0
sCount = 0
resisCount = 0

for r in reports:
    if r.culture.hasResistance:
        # Get dictionary of resistances
        for key, value in r.culture.resistances.items():
            for resistanceItem in value:
                resisCount += 1
                if resistanceItem.value == 'R':
                    rCount += 1
                elif resistanceItem.value == 'S':
                    sCount += 1

flat = pandas.DataFrame(columns=ReportTypes.reportStruct)
index = 0

for r in reports:
    val = info.flattenReport(index, r)
    flat = pandas.concat([flat,val])
    flat[ReportTypes().reportStruct].to_csv('flatten.csv')
    index += 1



print('done')