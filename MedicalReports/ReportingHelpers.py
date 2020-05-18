import pandas
from validators.json_validator import JsonValidator
from report_extract import extract_value_report_as_json
from MedicalReports.Reports import Report
from array import *

class ReportTypes():
    cultureStruct = ['reportindex', 'reportname', 'culture']
    resistanceStruct = ['resindex','culture','resistance','value']
    reportStruct = ['index','reporttype','culture','resistance','value']

class ReportInfo():
    """ Class to get information about reports. """

    def generateReportList(self,dataframeColumn):
        """ Will accept a dataframe with a single column, then convert it into a list of Report objects. It will exclude
        the reports that 'error' out """
        reportList = dataframeColumn
        reports = []
        for rep in reportList:
            jsonval = extract_value_report_as_json(rep)
            for jsonreport in jsonval:
                if 'error' not in jsonreport:
                    reports.append(Report(jsonreport))
        return reports

    def appendCultureToDataframe(self,currentReportIndex, reportname, cultureList):
        cultureDF = pandas.DataFrame(columns=ReportTypes.cultureStruct)
        for culture in cultureList:
            cultureDF = cultureDF.append(
                {'reportindex': currentReportIndex, 'reportname': reportname, 'culture': culture},
                ignore_index=True)
        return cultureDF

    def appendResistanceToDataframe(self,currentResIndex, culturename, resistancelist):
        cultureDF = pandas.DataFrame(columns=ReportTypes.resistanceStruct)
        for resistance in resistancelist:
            cultureDF = cultureDF.append(
                {'resindex': currentResIndex, 'culture': culturename, 'resistance': resistance.abbreviation, 'value': resistance.value},
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

    def flattenCulturesToDataframe(self, index, cultureList):
        """Will flatten a Culture with resistances into a flat table"""
        #Format : str : List<Resistance>
        dataframe = pandas.DataFrame(columns=ReportTypes.resistanceStruct)
        for key,value in cultureList.items():
            newdf = self.appendResistanceToDataframe(index,key,value)
            dataframe = pandas.concat([dataframe,newdf])
        return dataframe

    def flattenReport(self,index,report):
        # Report type, Culture, Resistance, ResistanceValue

        if report.culture is None:
            var = [index,report.reportType, None, None, None]
            return pandas.DataFrame([var], columns=ReportTypes().reportStruct)
        elif len(report.culture.vals) == 0 :
            var = [index,report.reportType, None, None, None]
            return pandas.DataFrame([var], columns=ReportTypes().reportStruct)
        else:
            # reportindex,reportType, culturename, resistance, valueOfResistance
            # Can't get flattenCulturesToDataframe to work with to_csv. Column is printed in the wrong spot when insert.index is used
            # So this has been created to avoid that issue.
            output = [[]]
            for resistanceKey, resistanceVal in report.culture.resistances.items():
                # resistanceVal will be a list of Resistances()
                arrIdx = 0
                for resistance in resistanceVal:
                    output.insert(arrIdx,[index,report.reportType,resistanceKey,resistance.abbreviation,resistance.value])
                    arrIdx += 1
            leng = len(output)-1
            del output[leng] # Remove the trailing empty array section
            return pandas.DataFrame(output,columns=ReportTypes().reportStruct)
