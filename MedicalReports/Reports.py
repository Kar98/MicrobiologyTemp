import json
from MedicalReports.Cultures import Culture
import re

class Report():

    culture = None
    jsonObj = {}
    reportType = ''

    def __init__(self, jsondata):
        try:
            self.jsonObj = json.loads(jsondata.replace('\n', ''))
            if('error' in self.jsonObj):
                self.reportType = 'error'
            else:
                self.reportType = self.jsonObj['report']
                self.culture = Culture(self.jsonObj['culture'])
        except AttributeError:
            self.jsonObj = jsondata
            if('error' in self.jsonObj):
                self.reportType = 'error'
            else:
                self.reportType = jsondata['report'][0]
                self.culture = Culture(self.jsonObj['culture'],self.reportType)

    def getCultureVals(self):
        retList = []
        if(self.culture is None):
            return []
        for c in self.culture.vals:
            # Start from start of string. Will search for A-Z and () and space. Stops when it finds a character not part of the list.
            rgxPattern = '^([A-z \(\)\.]+)'
            rgx = re.compile(rgxPattern)

            splits = c.split(' and ')
            if(len(splits) > 1):
                for split in splits:
                    retList.append(rgx.match(split).group(1).strip())
            else:
                retList.append(rgx.match(c).group(1).strip())
        return retList