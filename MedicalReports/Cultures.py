
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

    def toDict(self):
        if self.indentItem is None:
            return {'name': self.name, 'resistances': self.resistances}
        else:
            return {'name': self.name, 'resistances': self.resistances, 'indentItem': self.indentItem}

class CultureBlock():
    """Dumb class to hold information about the Culture"""
    # Objects
    cultures = [] # List of Culture objects
    notes = [] # List of strings found that did not match any particular criteria

    def __init__(self, parsedCultureDict = None):
        if parsedCultureDict is None:
            return
        try:
            self.cultures = parsedCultureDict['cultures']
            self.notes = parsedCultureDict['notes']
        except KeyError:
            pass


    def hasCultures(self):
        if len(self.cultures) > 0:
            return True
        else:
            return False

    def hasIndent(self):
        for culture in self.cultures:
            try:
                val = culture['indentItem']
            except KeyError:
                return False
            if len(val) > 0:
                return True

        return False

    def hasNotes(self):
        if len(self.notes) > 0:
            return True
        else:
            return False

    def toDict(self):
        tmplist = []
        for c in self.cultures:
            tmplist.append({'name': c.name, 'resistances': c.resistances, 'indentItem': c.indentItem})

        return tmplist
