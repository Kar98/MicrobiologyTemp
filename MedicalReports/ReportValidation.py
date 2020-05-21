import re

"""
List of report functions that can be used for validation. If true is returned then it's valid. If false is returned
then it has failed the validation. Add extra functions as required. 
"""
# list of regex to do a negative match
invalidRegex = ['\\?', '#']
warningRegex = ['\\?']


def validateWard(report):
    # Ensures that no invalid characters are part of the Registered field.
    valid = True
    invalidRegex = ['\\?', '#', ':']
    textToCheck = report.jsonObj['ward'][0]
    for regex in invalidRegex:
        if re.compile(regex).search(textToCheck) is not None:
            valid = False
    return valid

def validateRegistered(report):
    # Ensures that no invalid characters are part of the Registered field.
    valid = True
    textToCheck = report.jsonObj['registered'][0]
    for regex in invalidRegex:
        if re.compile(regex).search(textToCheck) is not None:
            valid = False
    if len(report.jsonObj['registered'][0]) == 0:
        raise Exception('Registered is blank')
    return valid

def validateCollected(report):
    # Ensures that no invalid characters are part of the Registered field.
    valid = True
    textToCheck = report.jsonObj['collected'][0]
    for regex in warningRegex:
        if re.compile(regex).search(textToCheck) is not None:
            raise Warning('Collected value : {1} , contained {0}'.format(regex,textToCheck))
    if len(report.jsonObj['collected'][0]) == 0:
        raise Exception('Collected is blank')
    return valid

def validateMicroNo(report):
    # Ensures that no invalid characters are part of the Registered field.
    valid = True
    if len(report.jsonObj['micro_no']) == 0:
        return valid
    textToCheck = report.jsonObj['micro_no'][0]
    for char in invalidRegex:
        if char in textToCheck:
            valid = False
    return valid

def validateLabNo(report):
    # Ensures that no invalid characters are part of the Registered field.
    valid = True
    textToCheck = report.jsonObj['lab_no'][0]
    for char in invalidRegex:
        if char in textToCheck:
            valid = False
    return valid


def validateAllReportFields(report):
    valid = True
    try:
        if not validateWard(report):
            raise Exception('Ward "{0}" contained invalid characters'.format(report.jsonObj['ward'][0]))
    except Warning as war:
        print(war)
    if not validateRegistered(report):
        raise Exception('Registered contained invalid characters')
    try:
        if not validateCollected(report):
            raise Exception('Collected contained invalid characters')
    except Warning as war:
        print(war)
    if not validateMicroNo(report):
        raise Exception('Micro No contained invalid characters')
    if not validateLabNo(report):
        raise Exception('Lab No contained invalid characters')
    return valid

