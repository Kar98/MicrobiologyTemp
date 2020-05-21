
class Resistance:
    """Dumb class to hold information about Resistance"""
    fullname = '' # Proper name of the resistance
    abbreviation = '' # Will be 3 letters
    value = '' # Either S or R

    def __init__(self,name,value):
        # Should always be 1
        self.abbreviation = name
        self.value = value