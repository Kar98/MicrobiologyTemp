import json
import re

from MedicalReports.Cultures import CultureBlock
from MedicalReports.Resistances import Resistance



class Report():
    """ Base MedicalReport that will be used as the main entry point to manipulate medical report data.
    If you want to create new functions for reporting on the reports, use the ReportingHelpers class """

    culture = None
    jsonObj = {}
    reportType = ''
    invalidChars = ['?', '#'] # List of chars that will be replaced by whitespace in the Culturename

    csvIndex = -1 #Used for debugging purposes

    def __init__(self, jsondata, csvIndex = -1):
        self.csvIndex = csvIndex
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
                if(self.culture.hasResistance()):
                    self.culture.resistances = self.getCultureResistance()


    def matchCultureName(self, cultureName):
        # Start from start of string. Will search for A-Z and () and space. Stops when it finds a character not part of the list.
        rgxPattern = '^([A-z \(\)\.]+)'
        rgx = re.compile(rgxPattern)
        return rgx.match(cultureName).group(1).strip()


    def getCultureVals(self):
        retList = []
        if(self.culture is None):
            return []
        for c in self.culture.vals:
            splits = c.split(' and ')
            if(len(splits) > 1):
                for split in splits:
                    retList.append(self.matchCultureName(split))
            else:
                retList.append(self.matchCultureName(c))
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
        resistances = {}
        for culturename, cultureval in self.culture.vals.items():
            culturename = self.cleanCultureName(culturename)
            if(len(cultureval) == 0):
                resistances[culturename] = None
            else:
                tmpResistanceList = []
                for subitem,subvalue in cultureval.items():
                    for resistancekey,resistanceval in subvalue.items():
                        tmpResistanceList.append(Resistance(resistancekey,resistanceval))
                try:
                    resistances[self.matchCultureName(culturename)] = tmpResistanceList
                except:
                    print(culturename)
                    print(self.jsonObj)
                    raise
        return resistances
