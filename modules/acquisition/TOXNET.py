import AcquisitionModule
from Chemical import Chemical
try:
	from collections import OrderedDict
except ImportError:
	from ordereddict import OrderedDict
import requests, urllib
import xmltodict
import json

class TOXNET(AcquisitionModule.AcquisitionModule):
	def __init__(self):
		self.api_url = "http://toxgate.nlm.nih.gov/cgi-bin/sis/search"	
		self.databases = ["hsdb","ccris","genetox","iris","iter","lact"]
	
	# Retreives the ids or more TOXNET chemicals based on a query
	# @param query	: A single query or a list of queries.
	# @param dbs	: (optional) A list of databases to search in. Will search in ALL available databases if it is not defined.
	# @returns		: Either a single Chemical object or a list of Chemical objects if a list of queries was inserted. No result will return None.
	def findByQuery(self, query, dbs=[]):
		chemicals = []		
		if isinstance(query, str):
			query = [query]
		
		# Make sure the databases that are being queried are currently supported
		dbs = [db for db in dbs if db in self.databases]
		
		if dbs == []:
			dbs = self.databases
		
		for q in query:
			for db in dbs:
				# The values set to 1 are not adjustable as per http://toxnet.nlm.nih.gov/toxnetapi/search_chemical.html
				payload = {"database":db, "queryxxx":q, "Stemming":1, "and":1, "chemsyn":1, "second_search":1,"gateway":1}
				r = requests.post(self.api_url,data=payload)
			
				print db
				self.parseQueryResult(r.text)
			
			raise Exception
			
		if isinstance(query, str):
			return chemicals[0]
		elif isinstance(query, list):
			return chemicals
			
	def parseQueryResult(self, xml):
		# The Query result will contain some HTML linebreaks, which do not count as correct XML
		xml = xml.replace("<br>","\n")
		dictionary = xmltodict.parse(xml)
		root = dictionary["QueryResult"]
		print json.dumps(root, sort_keys=True, indent=4, separators=(',', ': '))
		return root
		
	
	# Turns raw XML from TOXNET into a proper TOXNETResult object
	# @param xml	: An XML string to be parsed.
	# @returns		: A Chemical object.	
	def convertXmlToChemical(self, xml):
		chemicalObject = Chemical()			
		return chemicalObject
		
# TESTING #
def test_findByQuery():
	t = TOXNET()
	results = t.findByQuery('Zinc')
