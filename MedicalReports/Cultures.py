
class Culture():

    # Raw values
    vals = {}
    other = []
    abbreviations = {}
    notes = ''
    repType = '' # In case it's needed.

    # Objects
    resistances = {}

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