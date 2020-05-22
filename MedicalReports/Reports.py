import json
import re

from MedicalReports.Cultures import CultureBlock,Culture

class CultureEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,Culture):
            if o.indentItem is None:
                return {'name':o.name,'resistances':o.resistances}
            else:
                return {'name': o.name, 'resistances': o.resistances, 'indent': o.indentItem}
        else:
            return super().default(o)

class Report():
    """ Base MedicalReport that will be used as the main entry point to manipulate medical report data.
    If you want to create new functions for reporting on the reports, use the ReportingHelpers class """

    culture = None
    jsonObj = {}
    reportType = ''
    invalidChars = ['?', '#'] # List of chars that will be replaced by whitespace in the Culturename

    csvIndex = -1 #Used for debugging purposes
    rawdata = ''

    def __init__(self, jsondata, csvIndex = -1, rawdata = ''):
        self.csvIndex = csvIndex
        self.rawdata = rawdata
        try:
            self.jsonObj = json.loads(jsondata.replace('\n', ''))
            if('error' in self.jsonObj):
                self.reportType = 'error'
            else:
                self.reportType = self.jsonObj['report']
                self.culture = CultureBlock(self.jsonObj['culture'])
        except AttributeError:
            self.jsonObj = jsondata
            if('error' in self.jsonObj):
                self.reportType = 'error'
            else:
                self.reportType = jsondata['report'][0]
                self.culture = CultureBlock(self.jsonObj['culture'])

    def toJson(self):
        return CultureEncoder().encode(self.jsonObj)

    def toJson(self,jsonObj):
        return CultureEncoder().encode(jsonObj)


    def matchCultureName(self, cultureName):
        # Start from start of string. Will search for A-Z and () and space. Stops when it finds a character not part of the list.
        rgxPattern = '^([A-z \(\)\.]+)'
        rgx = re.compile(rgxPattern)
        return rgx.match(cultureName).group(1).strip()


    def getCultureVals(self):
        retList = []
        if(self.culture is None):
            return []
        for c in self.culture.cultures:
            retList.append(c.name)
        return retList

    def convertDataframeColToReportList(self,dataframeColumn):
        for text in dataframeColumn:
            pass
            #jsonval = extract_value_report_as_json(text)[0]

    def cleanCultureName(self, name):
        for char in self.invalidChars:
            name = name.replace(char,' ')
        return name


    def getCultureResistance(self):
        return self.culture.cultures
