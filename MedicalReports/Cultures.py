
class Culture():

    name = '' # Name of the culture
    resistances = {} # Dict of resistance strings
    indentItem = '' # Subset item that sometimes appears. Not sure what it's for


class CultureBlock():
    """Dumb class to hold information about the Culture"""
    # Objects
    cultures = [] # List of Culture objects
    notes = [] # List of strings found that did not match any particular criteria

    def __init__(self, jsonObj):
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