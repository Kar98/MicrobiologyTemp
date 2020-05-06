import pandas
from validators.json_validator import JsonValidator

class ReportTypes():
    cultureStruct = ['reportindex', 'reportname', 'culture']

class ReportInfo():
    def appendCultureToDataframe(self,currentReportIndex, reportname, cultureList):
        cultureDF = pandas.DataFrame(columns=['reportindex', 'reportname', 'culture'])
        for culture in cultureList:
            cultureDF = cultureDF.append(
                {'reportindex': currentReportIndex, 'reportname': reportname, 'culture': culture},
                ignore_index=True)
        return cultureDF

    def generateCultureDataframe(self,listOfReportObjects):
        validator = JsonValidator()
        reportIdx = 0
        cultureDF = pandas.DataFrame(columns=ReportTypes.cultureStruct)

        for report in listOfReportObjects:
            if ('error' not in report.jsonObj):
                cultureCounts = validator.getJsonFieldCounts(report.culture.vals)
                if (len(cultureCounts) > 0):
                    cultures = report.getCultureVals()
                    cultureDF = pandas.concat([cultureDF, self.appendCultureToDataframe(reportIdx, report.reportType, cultures)])
                    reportIdx += 1

        return cultureDF