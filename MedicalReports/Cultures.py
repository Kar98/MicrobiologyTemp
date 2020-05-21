
class Culture():

    name = '' # Name of the culture
    resistances = [] # List of Resistance objects
    indentItem = '' # Subset item that sometimes appears. Not sure what it's for


class CultureBlock():
    """Dumb class to hold information about the Culture"""
    # Raw values
    vals = {}
    other = []
    abbreviations = {}
    notes = ''
    repType = '' # In case it's needed.


    # Objects
    resistances = {}
    cultures = []

    def __init__(self, jsonObj, reportType):
        # Do some processing.
        # Assign values
        self.vals = jsonObj['vals']
        self.other = jsonObj['other']
        self.abbreviations = jsonObj['abbreviations']
        self.notes = jsonObj['notes']

    def hasResistance(self):
        if len(self.vals) > 0:
            return True
        else:
            return False