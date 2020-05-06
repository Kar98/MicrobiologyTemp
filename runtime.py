
from validators.json_validator import *
import logging
import pandas
from MedicalReports.Reports import Report
import matplotlib.pyplot as plt
from MedicalReports.Reporting import ReportInfo

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

jsonstr = '{"culture": {"text": "GEN TAZ CIP TIM\n             Pseudomonas aeruginosa               R   S   S   S\n\n\n\n\n\n     Antibiotic Abbreviations Guide:\n     GEN     Gentamicin                 CIP     Ciprofloxacin\n     TAZ     Pip/Tazobactam             TIM     Timentin","vals": {"Pseudomonas aeruginosa": {"resistance": {"GEN": "R","TAZ": "S","CIP": "S","TIM": "S"}}},"other": [],"abbreviations": {},"notes": "GEN Gentamicin CIP Ciprofloxacin TAZ Pip"}}'

file = 'Data/Microbiology2_conv.csv'
separator = "||"
df = pandas.read_csv(file, sep='\t')
separator = "\n"
df['ValueNew'] = df['ValueNew'].apply(lambda x : x.replace("||", "\n"))
df['CommentsNew'] = df['CommentsNew'].apply(lambda x : x.replace("||", "\n"))

validator = JsonValidator()
urineName = 'URINE MICROBIOLOGY'
bloodName = 'BLOOD CULTURE MICROBIOLOGY'

reportList = df['ValueNew'].head(1000)

cultureDF = pandas.DataFrame(columns=['reportindex','reportname','culture'])

reportIdx = 0

# Index , ReportIndex , Reportname , Culture

def appendCultureToDataframe(currentReportIndex, reportname, cultureList):
    cultureDF = pandas.DataFrame(columns=['reportindex', 'reportname', 'culture'])
    for culture in cultureList:
        cultureDF = cultureDF.append(
            {'reportindex': currentReportIndex, 'reportname': reportname, 'culture': culture},
            ignore_index=True)
    return cultureDF

for rep in reportList:
    jsonval = extract_value_report_as_json(rep)[0]
    report = Report(jsonval)
    if('error' not in report.jsonObj):
        cultureCounts = validator.getJsonFieldCounts(report.culture.vals)
        if(len(cultureCounts) > 0):
            cultures = report.getCultureVals()
            cultureDF = pandas.concat([cultureDF,appendCultureToDataframe(reportIdx,report.reportType,cultures)])
            reportIdx += 1

reports = []

for rep in reportList:
    jsonval = extract_value_report_as_json(rep)[0]
    reports.append(Report(jsonval))


info = ReportInfo()
cultureDF = info.generateCultureDataframe(reports)

dfCounts = cultureDF.groupby('culture').count().sort_index(ascending=False)
dfCounts[dfCounts.columns[0:1]].plot(kind='barh')
plt.show()
print(dfCounts[dfCounts.columns[0:1]])
#for key, item in aaa:
#    print(aaa.get_group(key),'\n')

#print(aaa)

#print(aaa[aaa.columns[0:1]])

print('done')