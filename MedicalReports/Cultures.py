import json

class Culture():

    vals = {}
    other = []
    abbreviations = {}
    notes = ''
    repType = '' # In case it's needed.

    def __init__(self, jsonObj, reportType):
        # Do some processing.
        # Assign values
        self.vals = jsonObj['vals']
        self.other = jsonObj['other']
        self.abbreviations = jsonObj['abbreviations']
        self.notes = jsonObj['notes']

