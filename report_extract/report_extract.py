# Module: Report Extract
#
# Extracts structured data from text reports.
#
# Author: Kelvin Ross, 2019
#


import pandas as pd
import re
import json
from pyparsing import *
from array import *
from MedicalReports.Cultures import Culture

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# List of regular expressions defining report types that will split microbiology value text into.
report_types = [
    "MULTI-RESISTANT ORGANISM SCREEN",
    "BODY FLUID EXAMINATION",
    "Bacterial Antigens",
    "C difficile screening",
    "Group B Streptococcus Screen",
    "COMPLETE",
    "Deleted",
    "MYCOLOGY",
    "MYCOBACTERIOLOGY",
    "CERVICAL SCREENING: LOW RISK",
    "GeneXpert Norovirus PCR",
    "BROAD RANGE BACTERIAL",
    "C. diphtheriae gene toxin detection",
    "MINIMUM INHIBITORY CONCENTRATIONS\(MIC\)",
    "[\w+ ]*REFERENCE LABORATORY",
    "EYE, EAR, NOSE, THROAT MICROBIOLOGY",
    # "NEISSERIA MENINGITIS REFERENCE LABORATORY",
    # "PNEUMOCOCCAL REFERENCE LABORATORY",
    "MICROBIOLOGY FROM SUPERFICIAL SITES",
    "MICROBIOLOGY FROM[ \w+/]*",
    "[\w+ ]*MICROBIOLOGY",
    "RESPIRATORY MICROBIOLOGY"
]

report_pattern = '|'.join(report_types)


# Splits the value text into its sections for each report found.
def split_sections(value):
    # Find the matching reports and their start location in the text
    p = re.compile(report_pattern)
    matches = []
    for m in p.finditer(value):
        matches.append((m.group(), m.start()))

    # reports = re.findall(report_pattern, value)

    if len(matches) == 0:
        # No match, include the whole thing
        return [value]
    elif len(matches) == 1:
        # There is only one report, include the whole thing
        return [value]
    else:
        # Split where the report tags are found
        matches = matches[1:]  # Ignore the first match
        # print(matches)

        start = 0
        sections = []
        for (group, loc) in matches:
            # print(group,loc)
            sections.append(value[start:loc])  # Add text between start and loc as a new section
            start = loc

        # Then add the last section
        sections.append(value[loc:])

        return sections


# Routine to return text between two regex patterns
def text_between_patterns(p1, p2, text):
    m1 = re.search(p1, text)
    if not (m1):
        # No p1 match found in text
        return ""
    else:
        # Start match found
        from_m1 = m1.end()
        remaining_text = text[from_m1:]

        m2 = re.search(p2, remaining_text)
        if not (m2):
            # No p2 match found in remaining
            return remaining_text.rstrip().strip()
        else:
            # Only return remaining up until match
            to_m2 = m2.start()
            return remaining_text[:to_m2].rstrip().strip()

# will match text between 2 patters and also return the initial p1 match with the remaining text
def text_between_patterns_including_header(p1,p2,text):
    m1 = re.search(p1, text)

    if not (m1):
        # No p1 match found in text
        return ""
    else:
        # Start match found
        from_m1 = m1.end()
        remaining_text = text[from_m1:]

        m2 = re.search(p2, remaining_text)
        if not (m2):
            # No p2 match found in remaining
            startText = text[m1.start():]
            return startText
        else:
            # Only return remaining up until match
            startText = text[m1.start():]
            to_m2 = startText.index(m2.group(0))
            return startText[:to_m2].rstrip().strip()

# Routine to split text after a pattern
def split_text_after_pattern(p, text):
    m = re.search(p, text)

    if not (m):
        # No p1 match found in text
        return text, ""
    else:
        # Start match found
        from_m = m.end()
        return text[:from_m].strip(), text[from_m:].strip()

class NotFound(Exception):
    def __init__(self,message):
        self.message = message

class TextParser:
    """Generic text parser that can be used to help build the JSON objects that the reports use."""

    def getKeyValuePair(self,textblock):
        # Generic function to get the key/value of the field. Pass in the raw text block from the csv.
        # It will handle key/value and cases where there is no value, instead just a row.
        # Expected format:
        # Leucocytes     Scant
        # Epithelials    Nil
        # Normal respiratory flora scant
        #
        vals = {'notes': []}
        for row in textblock.split('\n'):
            match = re.search('(\w[\w \.]+?) {2}(\w[\w ]*)', row)
            if match is not None:
                m1 = match.group(1)  # Name
                m2 = match.group(2)  # Value
                vals[m1.strip()] = m2
            else:
                val = row.strip()
                if len(val) > 0:
                    vals['notes'].append(val)
        return vals

    def getKeyValueNoNotes(self,textblock):
        # Generic function to get the key/value of the field. Pass in the raw text block from the csv.
        # It will handle key/value and cases only. if there is a case where there is no value, then it will be ignored
        # Expected format:
        # Leucocytes     Scant
        # Epithelials    Nil
        #
        vals = {}
        for row in textblock.split('\n'):
            match = re.search('(\w[\w ]+?) {2}(\w[\w+ ]*)', row)
            if match is not None:
                m1 = match.group(1)  # Name
                m2 = match.group(2)  # Value
                vals[m1.strip()] = m2

        return vals

class CultureParser:

    def getTextInRow(self,row, startPos = 0):
        """Row is the raw text row. StartPos is when the parser will start to expect text.. """
        # Scan through the row. If text is found, then start adding to the return value. If 2 whitespace chars are found, exit.
        exceptionChars = ['>'] # If one of these are found, then stop
        start = True
        string = []
        for x in range(startPos,len(row)):
            char = row[x]
            if char in exceptionChars:
                return ''.join(string).strip()
            elif char != ' ':
                start = False
                string.append(char)
            else:
                # If no text found yet, ignore the whitespace handling
                if start == False:
                    # Do lookahead for another whitespace char
                    try:
                        if row[x+1] == ' ':
                            # End hit
                            break
                        else:
                            # If next char is word char, then add the whitespace to string and continue
                            string.append(char)
                    except IndexError:
                        # End of line hit
                        break

        return ''.join(string)

    def isHeaderRow(self,rowtext):
        pattern = ' [A-Z]{2,3}'
        matches = re.findall(pattern,rowtext)
        if len(matches) > 0:
            return True
        else:
            return False

    def getHeaderRowValue(self, rowtext):
        # Potentially use a custom parser to find if it's a header row.
        pattern = ' [A-Z]{2,3}'
        matches = re.findall(pattern, rowtext)
        output = []
        for m in matches:
            # If it's only 2 chars, add an extra space to align the header correctly
            if len(m.strip()) == 2:
                m = m.strip()+' '
                output.append(m)
            else:
                output.append(m.strip())
        return ' '.join(output)

    def getResistanceValues(self, startHeaderPos, rowtext, headertext):
        # Row text has the culture and values on it
        # startHeaderPos is the index of the start position, of the header from previous row
        # Header text is only the valid header text (no whitespace)
        resistances = headertext.split(' ')
        cultureResistance = {}
        for res in resistances:
            resIdx = headertext.index(res) + startHeaderPos
            maxIdx = resIdx + len(res)
            resValue = []
            # Get the value underneath the header text
            try:
                for x in range(resIdx,maxIdx):
                    resValue.append(rowtext[x])
                cultureResistance[res] = ''.join(resValue).strip()
            except IndexError:
                # if the index is > length of string, no whitespace and load whatever is found
                cultureResistance[res] = ''.join(resValue).strip()

        return cultureResistance

    def getCultureFromList(self,listofcultures,cultureName):
        for culture in listofcultures:
            if culture.name == cultureName:
                return culture

        raise NotFound('Culture "{0}" does not exist'.format(cultureName))

    def isAbbrev(self,row,listofabbreviations):
        for abbr in listofabbreviations:
            if abbr in row:
                return True

        return False

    def getAbbrevInRow(self,row,listofabbreviations):
        abbres = []
        for abbr in listofabbreviations:
            if abbr in row:
                abbres.append(abbr)

        return abbres

    def parseAbbreviations(self,allrows,abbreviationList):
        abbreviationGuide = {}
        notes = [] # Catchall for any text found that does not match the abbreviation guide. Most likely bad user input
        abbrStart = 0
        rLen = len(allrows)
        for x in range(0,rLen):
            if "Antibiotic Abbreviations Guide" in allrows[x]:
                # If abbreviation header found, then get next row and start parsing the guide
                abbrStart = x + 1
                break

        for x in range(abbrStart,rLen):
            # Start from the guide list
            row = allrows[x]
            if len(abbreviationList) == 0:
                # If there are no abbreviations, then get any text found and add it to notes.
                text = row.strip()
                if len(text) > 0:
                    notes.append(text)
            else:
                abbrsFound = self.getAbbrevInRow(row,abbreviationList)
                for abbr in abbrsFound:
                    # For each abbreviation
                    try:
                        abbrIdx = row.index(abbr) + len(abbr)
                        matchedText = self.getTextInRow(row,abbrIdx)
                        abbreviationGuide[abbr] = matchedText
                    except ValueError:
                        if len(row.strip()) > 0 and not self.isAbbrev(row,abbreviationList):
                            # If row contains text and doesn't have any abbreviations, assume it's some other text
                            notes.append(row.strip())
                if len(abbrsFound) == 0 and len(row.strip()) > 0:
                    # if no abbreviation in row, then assume it's a note
                    notes.append(row.strip())


        if len(notes) == 0:
            abbreviationGuide['notes'] = []
        else:
            abbreviationGuide['notes'] = ';'.join(notes)
        return abbreviationGuide

    def parseCulture(self, cultureTextBlock):
        # Split rows
        # Scan for text in the row. If it's a header, do culture handling. If it's not add to notes
        # Mark the start position of the culture. If the culture below is indented (+4), then it is not a culture.

        expectCulture = False
        notes = []
        headerIndex = -1
        cultures = {'cultures': [], 'notes': []}
        listofcultures = cultures['cultures']
        currentHeaderText = ''
        parentStartPos = 1000  # High number to trigger first iteration
        parentCulture = Culture('') #POtentially convert this to a dict rather than Culture obj
        abbreviationList = []

        rows = cultureTextBlock.split('\n')

        for row in rows:
            text = self.getTextInRow(row)
            if 'Antibiotic Abbreviations Guide' in text:
                cultures['abbreviations'] = self.parseAbbreviations(rows,abbreviationList)
                break
            elif self.isHeaderRow(row):
                expectCulture = True
                header = self.getHeaderRowValue(row)
                headerIndex = row.index(header)
                currentHeaderText = header
                abbreviationList.extend(header.split(' '))
            elif len(row.strip()) == 0:
                # Newline/empty line hit, reset.
                expectCulture = False
                parentStartPos = 1000
            elif expectCulture:
                # Culture is expected on this line, load into obj.
                if parentStartPos < row.index(text):
                    # Then it's an indent
                    self.getCultureFromList(listofcultures,parentCulture.name).indentItem = text
                else:
                    # Get the resistances and add them to the cultures variable
                    values = self.getResistanceValues(headerIndex, row, currentHeaderText)
                    parentStartPos = row.index(text)
                    try:
                        culture = self.getCultureFromList(listofcultures,text)
                        culture.resistances.update(values)
                        parentCulture = culture
                    except NotFound:
                        parentCulture = Culture(text, values)
                        listofcultures.append(parentCulture)
            else:
                # If no culture expected and it's not a header, we can safely try to trim off the Culture field
                pattern = 'Culture\s*:?|CULTURE\s*:|CULTURE\s*'
                m1 = re.match(pattern,row)
                if m1 is not None:
                    text = self.getTextInRow(row[m1.end():])
                else:
                    text = self.getTextInRow(row)
                if len(text) > 0:
                    cultures['notes'].append(text)

        #return CultureEncoder().encode(cultures)
        # Convert list of cultures to a dict for json format
        tmpdict = []
        for cult in listofcultures:
            tmpdict.append(cult.toDict())

        try:
            return {'cultures': tmpdict, 'notes': cultures['notes'], 'abbreviations': cultures['abbreviations']}
        except KeyError:
            return {'cultures': tmpdict, 'notes': cultures['notes']}


class MicrobiologyReportExtractor:
    # Handles extracting annotations from text based microbiology reports from AusLab

    # At the lowest level we are simply stripping out sections of the report and return as text fields
    # Subtypes, such as UrineMicrobiologyReportExtractor, provide deeper analysis of stripped out sections.

    lab_pattern = 'Lab No\.*\s*:*\s*(\d+[-/]\d+)'
    micro_pattern = 'Micro No\.*\s*:\s*([\w\d]+)'  # Micro No.  :    GC15M30506
    attr_pattern = '{}\s*: *(.*)'

    section_heads_colon = [
        'Gram Stain',
        'Differential',
        'Cell Count',
        'Culture',
        'MRSA Screen',
        'Volume',
        'Comments',
        'Red Cell Morphology',
    ]
    section_heads_caps = [
        'MICROSCOPY',
        'CASTS',
        'CULTURE',
        'COMMENT',
        'CHEMISTRY',
    ]
    next_section_re = '({}|{})'.format(
        '|'.join([(s + '\s*:\s*') for s in section_heads_colon]),
        '|'.join(section_heads_caps)
    )

    def __init__(self, text):
        self.text = text

    def print_text(self):
        print(self.text)

    def addSectionHeadColon(self, item):
        # When the match gets long, it can match partial matches. Eg there are 2 headers: Culture and Culture stuff.
        # The regex will match Culture if it's first since it's the easiest to match and the parser will get wrong info.
        # Ensure that the hardest to match regex, is at the front of the regex pattern.
        self.section_heads_colon.insert(0,item)
        # Recalculate the section heads
        self.next_section_re = '({}|{})'.format(
            '|'.join([(s + '\s*:\s*') for s in self.section_heads_colon]),
            '|'.join(self.section_heads_caps)
        )

    def addSectionHead(self,item):
        # When the match gets long, it can match partial matches. Eg there are 2 headers: Culture and Culture stuff.
        # The regex will match Culture if it's first since it's the easiest to match and the parser will get wrong info.
        # Ensure that the hardest to match regex, is at the front of the regex pattern.
        self.section_heads_caps.insert(0, item)
        # Recalculate the section heads
        self.next_section_re = '({}|{})'.format(
            '|'.join([(s + '\s*:\s*') for s in self.section_heads_colon]),
            '|'.join(self.section_heads_caps)
        )

    # Get the report type from the text.  Check only 1 report found.
    # TO DO: check report is right type
    def get_reports(self):
        reports = re.findall(report_pattern, self.text)
        assert len(reports) == 1, 'Expected one report type per section!'
        return reports

    def get_micro_no(self):
        return re.findall(self.micro_pattern, self.text)

    def get_section_from_text(self, heading_pattern):
        return text_between_patterns(heading_pattern, self.next_section_re, self.text)

    def get_microscopy(self): return self.get_section_from_text('MICROSCOPY')

    # MICROSCOPY\nLeucocytes     < 10     x10^6/L RR ( < 10 )\nErythrocytes   < 10     x10^6/L RR ( < 10 )\nEpithelials    < 10     x10^6/L\n\n\nCULTURE

    def get_chemistry(self): return self.get_section_from_text('(Chemistry\s*:\s*|CHEMISTRY)')

    def get_culture(self):
        culturetext = text_between_patterns_including_header('(Culture\s*:\s*|^CULTURE|\nCULTURE\s+|CULTURE\s*:\s*)', self.next_section_re, self.text)
        parser = CultureParser()

        return parser.parseCulture(culturetext)

    def get_culture_with_header(self):
        return text_between_patterns_including_header('(Culture\s*:\s*|^CULTURE|\nCULTURE\s+|CULTURE\s*:\s*)', self.next_section_re, self.text)

    def get_ward(self):
        return re.findall(self.attr_pattern.format('Ward'),
                          self.text)  # Ward         :    Urol/Gyn/Head Neck C4E (GCUH)

    def get_json(self):
        section = self.text
        parser = TextParser()

        lab_no = re.findall(self.lab_pattern, section)

        collected = re.findall(self.attr_pattern.format('Collected'), section)  # Collected    :    23:15  23-Apr-14
        registered = re.findall(self.attr_pattern.format('Registered'), section)  # Registered   :    05:12  24-Apr-14
        volume = re.findall(self.attr_pattern.format('Volume'), section)  # Volume       :    3.5   mL
        appearance = re.findall(self.attr_pattern.format('Appearance'), section)  # Appearance   :  Bloodstained
        supernatant = re.findall(self.attr_pattern.format('Supernatant'), section)  # Supernatant  :  Yellow
        num_tubes = re.findall(self.attr_pattern.format('No\. of tubes'), section)  # No. of tubes :   4

        cell_count = self.get_section_from_text('Cell Count\s*:\s*')
        specimen = self.get_section_from_text('Specimen\s*:\s*')  # Specimen   :    Swab Wound Left,Hand\n\n\nCell Count
        #gram_stain = self.get_section_from_text('Gram Stain\s*:\s*')  # Gram Stain :    Gram pos. cocci scant\n\n\nCulture
        gram_stain = parser.getKeyValuePair(self.get_section_from_text('Gram Stain\s*:\s*'))
        red_cell_morphology = self.get_section_from_text('Red Cell Morphology\s*:\s*')
        casts = self.get_section_from_text('CASTS\s*:\s*')
        mrsa_screen = self.get_section_from_text(
            'MRSA Screen\s*:\s*')  # MRSA Screen      : No MRSA isolated after 48hrs incubation\n\nCulture    :
        differential = self.get_section_from_text(
            'Differential\s*:\s*')  # Differential :  Polymorphs    91   %\n                Mononuclears   9   %\n                Eosinophils    0   %\n                Others         0   %\n\n\nGram Stain   :
        comments = self.get_section_from_text('(Comments|COMMENT)\s*:\s*')

        tmp = self.get_ward()

        # Return an object with the various attributes extracted from the section
        return {
            'report': self.get_reports(),
            'lab_no': lab_no,
            'micro_no': self.get_micro_no(),
            'collected': collected,
            'registered': registered,
            'gram_stain': gram_stain,
            'cell_count': cell_count,
            'specimen': specimen,
            'culture': self.get_culture(),
            'red cell morphology': red_cell_morphology,
            'casts': casts,
            'microscopy': self.get_microscopy(),
            'differential': differential,
            'chemistry': self.get_chemistry(),
            'mrsa_screen': mrsa_screen,
            'volume': volume,
            'appearance': appearance,
            'supernatant': supernatant,
            'num_tubes': num_tubes,
            'comments': comments,
            'ward': self.get_ward(),
            'text': section
        }

    def print_json(self):
        json_report = self.get_json()
        print(json.dumps(json_report, indent=2))

class UrineMicrobiologyReportExtractor(MicrobiologyReportExtractor):

    def get_ward(self):
        return re.findall(self.attr_pattern.format('Ward of Collection'), self.text)  # Ward of Collection:  GICU~GCUH

    def get_micro_no(self):
        micro_no = super().get_micro_no()
        if micro_no == ['Collected']:
            # Didnt find a number, instead got 'Collected' as next heading.
            return []
        else:
            return micro_no

    def get_chemistry(self):
        chemistry_text = super().get_chemistry()

        chemistry_label = '([\w/]+)'
        chemistry_val = '([\d\.]+|Negative|Trace)'
        chemistry_re = '{}\s+{}'.format(chemistry_label, chemistry_val)
        chemistry_table = re.sub('\n', '|', chemistry_text).strip()
        chemistry_stripped = re.sub('\s+', ' ', chemistry_table).strip()

        chemistry = re.findall(chemistry_re, chemistry_stripped)

        chemistry_check = '|'.join(['{} {}'.format(l, v) for (l, v) in chemistry])

        assert chemistry_check == chemistry_stripped, "Chemistry extraction doesn't match"

        chemistry_json = [{'label': label, 'val': val} for (label, val) in chemistry]

        return {
            'text': chemistry_text,
            'vals': chemistry_json,
        }

    def get_microscopy(self):
        microscopy = super().get_microscopy()

        # Extract out the values and separate into their lines.
        val_text = text_between_patterns('^', '(Other\s*:\s*|CULTURE)', microscopy).split('\n')
        # Split into lines

        label_re = '(\w+)'
        val_re = '([\d<> ]+)'
        unit_re = '(x.*L)'
        rr_re = '([ R \(\)\d<\n]*)'
        microscopy_re = '{}\s+{}\s+{}{}'.format(label_re, val_re, unit_re, rr_re)
        # Leucocytes       70     x10^6/L RR ( < 10 )\n
        vals = re.findall(microscopy_re, microscopy)

        # Export out the vals as a dict object (json)
        val_json = [{'label': label.strip(), 'val': val.strip(), 'unit': unit.strip(), 'rr': rr.strip()} for
                    (label, val, unit, rr) in vals]

        # Extract out other values
        other_text = text_between_patterns('Other\s*:\s*', '\-\-\-EOR\-\-\-', microscopy)
        other_label = '(Yeast with hyphae|Yeast|Bacteria|Spermatozoa|Debris)'
        other_val = '([\d\+]+|scant)'
        other_re = '{}\s+{}'.format(other_label, other_val)
        other_text_stripped = re.sub('\s+', ' ', other_text).strip()
        others = re.findall(other_re, other_text_stripped)

        other_json = [{'label': label, 'val': val} for (label, val) in others]

        return {
            'text': microscopy,
            'vals': val_json,
            'other': other_json,
        }

    def get_culture(self):
        culturetext = super().get_culture_with_header()
        parser = CultureParser()

        return parser.parseCulture(culturetext)

    def get_json(self):
        json = super().get_json()

        # Normal ordering of report:
        #    -    'lab_no'
        #    -    'micro_no'
        #    -    'collected'
        #    -    'registered'
        #    -    'report'
        #    -    'ward'
        #    -    'specimen'
        #    -    'microscopy'
        #    -    'red cell morphology'
        #    -    'casts'
        #    -    'chemistry'
        #    -    'culture'
        #    -    'comments'

        # Drop unneeded attributes
        json.pop('text')
        json.pop('supernatant')
        json.pop('appearance')
        json.pop('cell_count')
        json.pop('volume')
        json.pop('num_tubes')
        json.pop('mrsa_screen')
        json.pop('gram_stain')
        json.pop('differential')

        return json

class BloodMicrobiologyReportExtractor(MicrobiologyReportExtractor):
    pass

class CatheterTipReportExtractor(MicrobiologyReportExtractor):
    pass

class CerebrospinalFluidReportExtractor(MicrobiologyReportExtractor):
    pass

class SuperficialReportExtractor(MicrobiologyReportExtractor):

    def get_json(self):
        parser = TextParser()
        json = super().get_json()
        json['cell_count'] = parser.getKeyValueNoNotes(json['cell_count'])
        return json

class MultiResistanceReportExtractor(MicrobiologyReportExtractor):
    def __init__(self,text):
        super().__init__(text)
        super().addSectionHeadColon('VRE Screen')

    def get_json(self):
        json = super().get_json()
        vreScreen = re.findall(self.attr_pattern.format('VRE Screen'), self.text)
        json['Vre Screen'] = vreScreen
        return json

class FaecesReportExtractor(MicrobiologyReportExtractor):
    def __init__(self,text):
        super().__init__(text)
        super().addSectionHeadColon('Parasitology')

    def get_json(self):
        json = super().get_json()
        json['Parasitology'] = re.findall(self.attr_pattern.format('Parasitology'), self.text)
        json.pop('casts')
        json.pop('gram_stain')
        json.pop('cell_count')
        json.pop('chemistry')
        json['microscopy'] = self.get_microscopy()
        return json

    def get_microscopy(self):
        vals = []
        text = self.get_section_from_text('Microscopy\s*:')
        for row in text.split('\n'):
            match = re.search('(\w[\w ]+?) {2}(\w[\w+ ]*)',row)
            if match is not None:
                m1 = match.group(1) # Name
                m2 = match.group(2) # Value
                vals.append({'label': m1, 'val': m2, 'unit': '', 'rr': ''})
        return vals

class RespiratoryReportExtract(MicrobiologyReportExtractor):
    def get_json(self):
        json = super().get_json()

        parser = TextParser()
        json['gram_stain'] = parser.getKeyValuePair(self.get_section_from_text('Gram Stain\s*:\s*'))

        return json

class BodyFluidReportExtractor(MicrobiologyReportExtractor):
    def __init__(self, text):
        super().__init__(text)
        super().addSectionHeadColon('Crystals')

    def get_json(self):
        json = super().get_json()
        json['crystals'] = re.findall(self.attr_pattern.format('Crystals'), self.text)

        return json

class DifficileScreeningReportExtractor(MicrobiologyReportExtractor):

    def __init__(self, text):
        super().__init__(text)
        super().addSectionHeadColon('C difficile Screen')

    def get_culture(self):
        pass

    def get_json(self):
        json = super().get_json()

        return {
            'report': json['report'],
            'lab_no': json['lab_no'],
            'micro_no': json['micro_no'],
            'collected': json['collected'],
            'registered': json['collected'],
            'ward': json['ward'],
            'specimen': json['specimen'],
            'c_difficile_screen': self.get_section_from_text('C difficile Screen\s*:\s*')
        }

class EENTReportExtractor(MicrobiologyReportExtractor):
    # Ear, eyes, nose, throat
    pass

class BacterialAntigensReportExtractor(MicrobiologyReportExtractor):

    def get_json(self):
        """Get first \n, get before \n and this will be the specimen. Everything after is some weird custome field"""
        parser = TextParser()

        json = super().get_json()
        idx = json['specimen'].index('\n')
        specimen = json['specimen'][0:idx]
        extraContent = json['specimen'][idx:]
        json['specimen'] = specimen
        json['extra_specimen'] = parser.getKeyValueNoNotes(extraContent)

        return json

class MycologyReportExtractor(MicrobiologyReportExtractor):
    pass

class MycobacteriologyReportExtractor(MicrobiologyReportExtractor):

    def __init__(self, text):
        super().__init__(text)
        super().addSectionHead('ACID - FAST MICROSCOPY - \[Standard Ziehl-Neelsen\]\nResult\s*:')
        super().addSectionHead('MYCOBACTERIAL CULTURE\nResult\s*:')

    def get_speciment(self):
        pass

    def get_json(self):
        """Get first \n, get before \n and this will be the specimen. Everything after is some weird custome field"""
        val = 'ACID - FAST MICROSCOPY - {0}\nResult\s*:'.format(re.escape('[Standard Ziehl-Neelsen]'))

        parser = TextParser()

        json = super().get_json()

        fast_microscopy = 'ACID - FAST MICROSCOPY - \[Standard Ziehl-Neelsen\]\nResult\s*:'
        mycobaterial_culture = 'MYCOBACTERIAL CULTURE\nResult\s*:'

        json['fast_microscopy'] = self.get_section_from_text(fast_microscopy)
        json['mycobaterial_culture'] = self.get_section_from_text(mycobaterial_culture)
        json['specimen'] = parser.getKeyValuePair(json['specimen'])
        json['microscopy'] = '' # No microscopy for this report. It will match the field name however.

        return json

class GenitalReportExtractor(MicrobiologyReportExtractor):

    # Clue Cells
    def __init__(self, text):
        super().__init__(text)
        super().addSectionHeadColon('Clue Cells')

    def get_json(self):
        json = super().get_json()
        json['clue_cells'] = self.get_section_from_text('clue_cells')

        return json

class OperativeInvasiveReportExtractor(MicrobiologyReportExtractor):
    pass

class UnknownReportExtractor(MicrobiologyReportExtractor):
    def get_json(self):
        # Return an object with the various attributes extracted from the section
        return {
            'report': "Unknown Report Type",
            'lab_no': self.text,
            'micro_no': ''
        }


# Factory to generate report extraction class
def report_extractor_factory(section):
    report = re.findall(report_pattern, section)

    assert (len(report) == 1), "Should be exactly one report type per section, found {}.".format(len(report))

    # if len(report) != 1:
    #     raise Exception("Invalid report, should be exactly one report type.")

    if report[0] == 'URINE MICROBIOLOGY':
        return UrineMicrobiologyReportExtractor(section)
    if report[0] == 'BLOOD CULTURE MICROBIOLOGY':
        return BloodMicrobiologyReportExtractor(section)
    if report[0] == 'CATHETER TIP MICROBIOLOGY':
        return CatheterTipReportExtractor(section)
    if report[0] == 'CEREBROSPINAL FLUID MICROBIOLOGY':
        return CerebrospinalFluidReportExtractor(section)
    if report[0] == 'MICROBIOLOGY FROM SUPERFICIAL SITES':
        return SuperficialReportExtractor(section)
    if report[0] == 'MULTI-RESISTANT ORGANISM SCREEN':
        return MultiResistanceReportExtractor(section)
    if report[0] == 'FAECES MICROBIOLOGY':
        return FaecesReportExtractor(section)
    if report[0] == 'RESPIRATORY MICROBIOLOGY':
        return RespiratoryReportExtract(section)
    if report[0] == 'BODY FLUID EXAMINATION':
        return BodyFluidReportExtractor(section)
    if report[0] == 'C difficile screening':
        return DifficileScreeningReportExtractor(section)
    if report[0] == 'EYE, EAR, NOSE, THROAT MICROBIOLOGY':
        return EENTReportExtractor(section)
    if report[0] == 'Bacterial Antigens':
        return BacterialAntigensReportExtractor(section)
    if report[0] == 'MYCOLOGY':
        return MycologyReportExtractor(section)
    if report[0] == 'MYCOBACTERIOLOGY':
        return MycobacteriologyReportExtractor(section)
    if report[0] == 'GENITAL MICROBIOLOGY':
        return GenitalReportExtractor(section)
    if report[0] == 'MICROBIOLOGY FROM OPERATIVE/INVASIVE SPECIMENS':
        return OperativeInvasiveReportExtractor(section)
    else:
        raise Exception("Unrecognized report {}.".format(report[0]))


# Split each report into a list item containing the json elements identifying the structured data.
def extract_value_section_as_json(section):
    extractor = None
    try:
        extractor = report_extractor_factory(section)
        val = extractor.get_json()
        return val

    except Exception as err:
        if 'Unrecognized report' not in err.__str__():
            print(section)
            raise Exception(err)
        result = {
            'error': "Exception",
            'exception': err.args[0],
            'text': section,
        }
        logger.exception(err)
        return result


def extract_value_report_as_json(text):
    return [extract_value_section_as_json(s) for s in split_sections(text)]
