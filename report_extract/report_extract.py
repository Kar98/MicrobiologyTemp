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
    # "NEISSERIA MENINGITIS REFERENCE LABORATORY",
    # "PNEUMOCOCCAL REFERENCE LABORATORY",
    "[\w+ ]*MICROBIOLOGY",
    # "MICROBIOLOGY FROM SUPERFICIAL SITES",
    "MICROBIOLOGY FROM[ \w+]*",
    # "RESPIRATORY MICROBIOLOGY",
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
            return remaining_text.rstrip().strip()
        else:
            # Only return remaining up until match
            to_m2 = m2.start()
            startText = text[m1.start():]
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

class CultureEncoder(json.JSONEncoder):
    def default(self,o):
        if isinstance(o,Culture):
            if o.indentItem is None:
                return {'name':o.name,'resistances':o.resistances}
            else:
                return {'name': o.name, 'resistances': o.resistances, 'indent': o.indentItem}
        else:
            return super().default(o)

class CultureParser:

    def getTableWidth(self,rows):
        length = 0
        for row in rows:
            if len(row) > length:
                length = len(row)
        return length

    def getTextInRow(self,row):
        """Row is text. cultureRow is bool, indicates if the row is expected to have a culture"""
        # Scan through the row. If text is found, then start adding to the return value. If 2 whitespace chars are found, exit.
        exceptionChars = ['>'] # If one of these are found, then stop
        start = True
        string = []
        for x in range(len(row)):
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
        pattern = ' [A-Z]{2,3}'
        matches = re.findall(pattern, rowtext)
        output = []
        for m in matches:
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

    def doesCultureExist(self,listofcultures,cultureName):
        """listofculture will be a list of Culture Objects"""
        for culture in listofcultures:
            if culture.name == cultureName:
                return True

        return False

    def getCultureFromList(self,listofcultures,cultureName):
        for culture in listofcultures:
            if culture.name == cultureName:
                return culture

        raise NotFound('Culture "{0}" does not exist'.format(cultureName))

    def cleanDict(self,dictionary):
        for key, value in dictionary.items():
            if value is None:
                del key[value]

    def cultureToJson(self, culturelist):
        jsonList = []
        for culture in culturelist:
            val = CultureEncoder().encode(culture)
            jsonList.append(self.cleanDict(val))
        return jsonList


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
        parentCultureName = ''
        parentCulture = Culture('')

        rows = cultureTextBlock.split('\n')

        for row in rows:
            text = self.getTextInRow(row)
            if self.isHeaderRow(row):
                expectCulture = True
                header = self.getHeaderRowValue(row)
                headerIndex = row.index(header)
                currentHeaderText = header
            elif len(text.strip()) == 0:
                # Newline/empty line hit, reset.
                expectCulture = False
                parentStartPos = 1000
            elif expectCulture:
                # Culture is expected on this line, load into obj.
                if parentStartPos < row.index(text):
                    # Then it's an indent
                    self.getCultureFromList(listofcultures,parentCultureName).indentItem = text
                else:
                    parentCultureName = text
                    values = self.getResistanceValues(headerIndex, row, currentHeaderText)
                    parentStartPos = row.index(text)

                    try:
                        culture = self.getCultureFromList(listofcultures,parentCultureName)
                        culture.resistances.update(values)
                        parentCulture = culture
                    except NotFound:
                        parentCulture = Culture(parentCultureName, values)
                        listofcultures.append(parentCulture)

            elif text.lower() == 'culture' or text.lower() == 'culture:':
                pass # Sometimes the header will get caught and this is to remove it. Not essential but makes it cleaner
            elif text.contains("Antibiotic Abbreviations Guide"):
                pass
            else:
                cultures['notes'].append(text)

        return CultureEncoder().encode(cultures)



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

    def get_culture(self): return self.get_section_from_text('(Culture\s*:\s*|^CULTURE|\nCULTURE\s+|CULTURE\s*:\s*)')

    def get_culture_with_header(self):
        return text_between_patterns_including_header('(Culture\s*:\s*|^CULTURE|\nCULTURE\s+|CULTURE\s*:\s*)', self.next_section_re, self.text)

    def get_ward(self):
        return re.findall(self.attr_pattern.format('Ward'),
                          self.text)  # Ward         :    Urol/Gyn/Head Neck C4E (GCUH)

    def get_json(self):
        section = self.text

        lab_no = re.findall(self.lab_pattern, section)

        collected = re.findall(self.attr_pattern.format('Collected'), section)  # Collected    :    23:15  23-Apr-14
        registered = re.findall(self.attr_pattern.format('Registered'), section)  # Registered   :    05:12  24-Apr-14
        volume = re.findall(self.attr_pattern.format('Volume'), section)  # Volume       :    3.5   mL
        appearance = re.findall(self.attr_pattern.format('Appearance'), section)  # Appearance   :  Bloodstained
        supernatant = re.findall(self.attr_pattern.format('Supernatant'), section)  # Supernatant  :  Yellow
        num_tubes = re.findall(self.attr_pattern.format('No\. of tubes'), section)  # No. of tubes :   4

        cell_count = self.get_section_from_text('Cell Count\s*:\s*')
        specimen = self.get_section_from_text('Specimen\s*:\s*')  # Specimen   :    Swab Wound Left,Hand\n\n\nCell Count
        gram_stain = self.get_section_from_text(
            'Gram Stain\s*:\s*')  # Gram Stain :    Gram pos. cocci scant\n\n\nCulture
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
        culture = super().get_culture()
        # print("Culture:", culture)

        # Split culture text using abbreviation
        abbrev_re = 'Antibiotic Abbreviations Guide\s*:\s*'

        val_text = text_between_patterns('^', abbrev_re, culture)
        abbrev_text = text_between_patterns(abbrev_re, '$', culture)

        def get_abbrev(text):
            abbrev_acronym = '[A-Z]{2,3}'
            abbrev_label = '[A-Za-z/\(\)]+'
            abbrev_re = '({})\s+({})'.format(abbrev_acronym, abbrev_label)
            split_re = '{}\s+{}\n\n\n'.format(abbrev_acronym, abbrev_label)

            # Split between the abbreviations and notes.  Notes are anything after the last abbreviation
            abbrev_text, notes_text = split_text_after_pattern(split_re, text)

            # List of matches
            abbrev = re.findall(abbrev_re, abbrev_text)

            # check the list matches the text, that way we will know if pattern match missed something.
            text_stripped = re.sub('\s+', ' ', text).strip()
            abbrev_stripped = ' '.join(['{} {}'.format(k, v) for (k, v) in abbrev])
            notes_stripped = re.sub('\s+', ' ', notes_text).strip()
            generated_stripped = abbrev_stripped + ((" " + notes_stripped) if notes_text != "" else "")
            # assert text_stripped == generated_stripped, "Antibiotic Abbreviations Guide text not extracted correctly."

            return dict(abbrev), notes_text

        abbrev_val, notes_val = get_abbrev(abbrev_text)

        # For the culture table, work out what type each line is
        def culture_line_type(line):
            if line == '':
                return {'type': 'empty'}

            # Header line contains 2 or 3 letter acronyms
            header_re = re.compile("^(\s*[A-Z]{2,3})+$")
            if header_re.match(line):
                cols = re.findall("([A-Z]{2,3})", line)
                return {'type': 'header', 'cols': cols}

            # Row line is a culture followed by resistance values R | S
            row_re = re.compile("^\s*.*/L")
            m = row_re.match(line)
            # row = re.findall("^\s*(.*/L)\s+([RS]\s*)*?$", line)
            if m:
                return {'type': 'row', 'culture': line[:m.end()].strip(), 'resistance': line[m.end():].strip()}

            return {'type': 'unknown', 'text': line}

        # Extract culture definitions from resistance table
        def extract_culture_table(s):
            lines = s.split('\n')

            antibiotics = []
            cultures = {}
            other = []
            for line in lines:
                lt = culture_line_type(line)

                if lt['type'] == 'header':
                    antibiotics = lt['cols']

                if lt['type'] == 'row':
                    resistance = dict(zip(antibiotics, re.findall("[RS]", lt['resistance'])))

                    if lt['culture'] not in cultures.keys():
                        cultures[lt['culture']] = {'resistance': resistance}
                    else:
                        resistance.update(cultures[lt['culture']]['resistance'])
                        cultures[lt['culture']] = {'resistance': resistance}

                if lt['type'] == 'unknown':
                    other.append(lt['text'])

            return cultures, other

        culture_val, other_val = extract_culture_table(val_text)

        return {
            'text': culture,
            'vals': culture_val,
            'other': other_val,
            'abbreviations': abbrev_val,
            'notes': notes_val,
        }

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

    def get_culture(self):
        culture = super().get_culture()
        # print("Culture:", culture)

        # Pyparser definitions used for parsing abbreviation texts
        LF = Suppress('||')

        abbrev = Word(alphas.upper(), min=2, max=3)
        abbrev_label = Word(alphas + '/-()', min=2)
        abbrev_tuple = Group(abbrev + abbrev_label + LF)('abbrev')
        abbrev_list = Group(ZeroOrMore(abbrev_tuple))('abbrev_list')

        header = Group(OneOrMore(abbrev))('header')
        culture_val = Group(OneOrMore(Word(alphas + '-', min=2)))('culture')
        resistance = Group(ZeroOrMore(Word("RS", exact=1)))('resistance')
        row = Group(culture_val + resistance)('row')
        # table = Group(header + OneOrMore(row))('table')
        table = Group(header + OneOrMore(LF + row))('table')

        other = Group(OneOrMore(Word(alphanums + '.-,()')))('other')
        other_block = Group(OneOrMore(ZeroOrMore(LF) + other))('other_block')

        abbrev_block = Group(abbrev_list + other_block)('abbrev_block')

        culture_block = MatchFirst([table, other])

        # Split culture text using abbreviation
        abbrev_re = 'Antibiotic Abbreviations Guide\s*:\s*'
        val_text = text_between_patterns('^', abbrev_re, culture)
        abbrev_text = text_between_patterns(abbrev_re, '$', culture)

        def get_abbrev(text):
            s = text.replace("\n", "||")
            # print("abbrev:", s)

            if s == '':
                return {}, ""

            parsed_text = abbrev_block.parseString(s)  # .asDict()
            abbrev = dict(parsed_text.abbrev_block.abbrev_list.asList())
            notes_text = ' '.join(sum(parsed_text.abbrev_block.other_block.asList(), []))

            # check the list matches the text, that way we will know if pattern match missed something.
            # text_stripped = re.sub('\s+', ' ', text).strip()
            # abbrev_stripped = ' '.join(['{} {}'.format(k,v) for (k,v) in abbrev])
            # notes_stripped = re.sub('\s+', ' ', notes_text).strip()
            # generated_stripped = abbrev_stripped + ((" " + notes_stripped) if notes_text != "" else "")
            # assert text_stripped == generated_stripped, "Antibiotic Abbreviations Guide text not extracted correctly."

            return dict(abbrev), notes_text

        abbrev_val, notes_val = get_abbrev(abbrev_text)

        # Extract culture definitions from resistance table - using parsing
        def extract_culture_table_parse(text):
            text = text.replace("\n", "||")
            # print("Text:", text)

            # Parse text using definitions above
            parsed_text = culture_block.parseString(text)

            antibiotics_vals = []
            culture_vals = {}
            other_vals = []

            if parsed_text.table != '':
                antibiotics_vals = list(parsed_text.table.header)
                culture_val = ' '.join(list(parsed_text.table.row.culture))
                resistance_vals = dict(zip(antibiotics_vals, parsed_text.table.row.resistance))
                culture_vals = {culture_val: {'resistance': resistance_vals}}

            if parsed_text.other != '':
                other_vals = [' '.join(list(parsed_text.other))]

            return culture_vals, other_vals

        culture_val, other_val = extract_culture_table_parse(culture)

        return {
            'text': culture,
            'vals': culture_val,
            'other': other_val,
            'abbreviations': abbrev_val,
            'notes': notes_val,
        }

class CatheterTipReportExtractor(MicrobiologyReportExtractor):

    def get_culture(self):
        culturetext = super().get_culture_with_header()
        parser = CultureParser()

        return parser.parseCulture(culturetext)

class UnknownReportExtractor(MicrobiologyReportExtractor):
    def get_json(self):
        # Return an object with the various attributes extracted from the section
        return {
            'report': "Unknown Report Type",
            'text': self.text
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
    else:
        raise Exception("Unrecognized report {}.".format(report[0]))


# Split each report into a list item containing the json elements identifying the structured data.
def extract_value_section_as_json(section):
    try:
        extractor = report_extractor_factory(section)
        return extractor.get_json()

    except Exception as err:
        result = {
            'error': "Exception",
            'exception': err.args[0],
            'text': section,
        }
        logger.exception(err)
        return result


def extract_value_report_as_json(text):
    return [extract_value_section_as_json(s) for s in split_sections(text)]
