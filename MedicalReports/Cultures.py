import json

class Culture():

    name = ''  # Name of the culture
    resistances = {}  # Dict of resistance strings
    indentItem = ''  # Subset item that sometimes appears. Not sure what it's for

    def __init__(self, name, resistance=None, indentItem = None):
        if resistance is None:
            resistance = {}
        self.name = name
        self.resistances = resistance
        self.indentItem = indentItem

class CultureBlock():
    """Dumb class to hold information about the Culture"""
    # Objects
    cultures = [] # List of Culture objects
    notes = [] # List of strings found that did not match any particular criteria

    def __init__(self, jsonStr):
        # Do some processing.
        # Assign values
        jsonObj = json.loads(jsonStr)
        try:
            self.cultures = jsonObj['cultures']
            self.notes = jsonObj['notes']
        except KeyError:
            pass


    def hasCultures(self):
        if len(self.cultures) > 0:
            return True
        else:
            return False