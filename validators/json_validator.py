

import re 
import pandas
import typing

from MedicalReports.Reports import Report
from report_extract import *
import math

file = 'Data/Microbiology2_conv.csv'
separator = '||'


# Goal:
# Load in a row from the CSV
# Get the JSON equivalent of that row
# Ensure that the JSON has the expected properties
# Ensure that the JSON has the expected fields


class MedicalReport():
	"""Auto parsed report using basic rules to try to find the key:value pairs from the csv file"""

	def __init__(self,rowString: str,separator: str) -> None:
		self.fields = {}
		self.properties = [] #Currently unused.
		self.rawValues = []
		
		rowSplits = rowString.split(separator)
		for row in rowSplits:
			if(len(row) > 0):
				match = re.search('([A-z]+(\s*[A-z\.]*\s?[A-z\.]*\s*)?):(.*)',row)
				if (match):
					field = match.group(1).strip()
					value = match.group(3).strip()
					if(len(value) > 0):
						self.fields[field] = value
						self.rawValues.append(value)

	def printReport(self):
		for key,value in self.fields.items():
			print("Key: '{0}' Value: '{1}'".format(key,value))


class JsonValidator():
	
	def __init__(self):
		self.dontMatch = ['text']
		self.report_types = ["MULTI-RESISTANT ORGANISM SCREEN", "BODY FLUID EXAMINATION", "Bacterial Antigens",
							 "C difficile screening", "Group B Streptococcus Screen", "COMPLETE", "Deleted", "MYCOLOGY",
							 "MYCOBACTERIOLOGY", "CERVICAL SCREENING: LOW RISK", "GeneXpert Norovirus PCR",
							 "BROAD RANGE BACTERIAL", "C. diphtheriae gene toxin detection",
							 "MINIMUM INHIBITORY CONCENTRATIONS\(MIC\)", "[\w+ ]*REFERENCE LABORATORY",
							 "[\w+ ]*MICROBIOLOGY", "MICROBIOLOGY FROM[ \w+]*"]

	def checker(self,item,list):
		for l in list:
			if(item in l):
				return True
		return False

	def getAllJsonValues(self,json):
		r = []
		for key,value in json.items():
			if(key not in self.dontMatch):
				if isinstance(value,list):
					if(len(value) > 0):
						r.extend(value)
				elif isinstance(value,dict):
					r.extend(self.getAllJsonValues(value))
				elif len(value) > 0:
						r.append(value)

		return r

	def getJsonFieldCounts(self,json):
		try:
			fields = json.items()
		except:
			fields = json[0].items()
		r = {}
		for key,value in fields:
			if(key not in self.dontMatch):
				if isinstance(value,list):
					if(len(value) > 0):
						r[key] = len(value)
					else:
						r[key] = 0
				elif isinstance(value,dict):
					if(len(value) > 0):
						r[key] = len(value)
					else:
						r[key] = 0
				else:
					if(len(value) > 0):
						r[key] = 1
					else:
						r[key] = 0

		return r

	def checkJsonAgainstReport(self,json: dict,report: MedicalReport):
		for key,value in report.fields.items():
			if(key not in self.dontMatch):
				if(self.checker(value,self.getAllJsonValues(json))):
					print(" '{0}' success".format(value))
				else:
					print(" '{0}' failed".format(value))

	def doCheckAndReturnErrors(self, reportExtractReport: Report, medReport: MedicalReport):
		errors = []
		if('error' in reportExtractReport.jsonObj.keys()):
			errors.append("{0} - {1}".format(reportExtractReport.jsonObj['error'], reportExtractReport.jsonObj['exception']))
			return errors
		for key,value in medReport.fields.items():
			if(key not in self.dontMatch):
				if(self.checker(value, self.getAllJsonValues(reportExtractReport.jsonObj))):
					pass
				else:
					errors.append(value)

		return errors

	def convertToSizeBasedDf(self,columnList):
		outdf = pandas.DataFrame()
		report_pattern = '|'.join(self.report_types)
		repLen = 0
		index = 0
		tuples = []
		for col in columnList:
			reports = re.findall(report_pattern, col)
			if(len(reports) > 1):
				index+=1
				continue
			repLen = len(col)
			tuples.append((index,reports[0],repLen))
			index+=1
		outdf = pandas.DataFrame(tuples,columns= ['Index','Report','Size'])
		return outdf

	def getMaxSizeReport(self,dataframe,groupname):
		groupby = dataframe.groupby('Report')

		for grpname,dfgroup in groupby:
			if(grpname == groupname):
				maxsize = 0
				index = 0
				for rowindex,row in dfgroup.iterrows():
					if(row['Size'] > maxsize):
						maxsize = row['Size']
						index = row['Index']
		return [(index,groupname,maxsize,"Notepad++ {0}".format(index+2))]

	def getMinSizeReport(self,dataframe,groupname):
		groupby = dataframe.groupby('Report')

		for grpname,dfgroup in groupby:
			if(grpname == groupname):
				minsize = 99999
				index = 0
				for rowindex,row in dfgroup.iterrows():
					if(row['Size'] < minsize):
						minsize = row['Size']
						index = row['Index']
		return [(index,groupname,minsize,"Notepad++ {0}".format(index+2))]

	def getPercentageForKey(self, keyname: str, listOfDicts: dict) -> float:
		has = 0
		for stat in listOfDicts:
			if (stat[keyname] >= 1):
				has += 1

		return has / len(listOfDicts) * 100

	# For each key, find what the percentage is.
	def getPercentageOfAssignedKeys(self, dictOfFieldValues: dict) -> dict:
		"""This will get the percentage of fields assigned. If there are 10 reports, 5 of them have LabNo assigned,
		then return values will be LabNo: 50% """
		try:
			keys = dictOfFieldValues.keys()
		except:
			keys = dictOfFieldValues[0].keys()
		listOfPerc = {}
		for k in keys:
			#listOfPerc[k] = '{0}%'.format(math.trunc(self.getPercentageForKey(k, dictOfFieldValues)))
			listOfPerc[k] = math.trunc(self.getPercentageForKey(k, dictOfFieldValues))
		return listOfPerc

	def getNumberOfJsonFieldsAssigned(self,dataframeColumn,reportName):
		totalStats = []
		for val in dataframeColumn:
			try:
				if (reportName in val):
					rep = extract_value_report_as_json(val)
					if(reportName in rep[0]['report']):
						counts = self.getJsonFieldCounts(rep[0])
						totalStats.append(counts)
			except:
				pass
		return totalStats

	def getPercentageOfTotalReports(self, commonFields, unionOfReports):
		# List of str, List of List[Dict]

		counts = {}
		total = 0
		for reportCollection in unionOfReports:
			total += len(reportCollection)
			print('Report len : {0}'.format(len(reportCollection)))

		print('total {0}'.format(total))

		# Get a union of the reports
		# For each key provided
		# Get a report, then count if the key has a value
		# Then divide the key value, by the total and return the %
		for field in commonFields:
			#Set the total count
			counts[field] = 0
			tmpCount = 0
			for reportCollection in unionOfReports:
				for key in reportCollection:
					if(key[field] > 0):
						tmpCount += 1
			counts[field] = math.trunc(tmpCount / total * 100)
		return counts

	def getCommonKeys(self,listOfDicts):
		retList = []
		# Get the first dictionary
		check = listOfDicts[0].keys()
		# For each key
		for c in check:
			exists = True
			for dic in listOfDicts:
				# If the key exists in all other dictionaries, then add to return list
				try:
					dic[c]
				except:
					exists = False
			if(exists):
				retList.append(c)
		return retList





#if __name__ == '__main__':
#	main()