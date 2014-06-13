from Olympus.modules.acquisition.AcquisitionModule import AcquisitionModule
from Olympus.lib.Chemical import Chemical
try:
	from collections import OrderedDict
except ImportError:
	from ordereddict import OrderedDict
import requests, urllib
import xmltodict
import json

class TOXNET(AcquisitionModule):
	""" This module allows for retrieval of chemicals from the TOXNET API.
	
	The TOXNET API envelops many toxicology databases, but does not not provide a lot of easily parsed information. Most of it is enclosed in text-heavy HTML documents. This module has a lot of potential for future development when large slabs of text are required for analysis. As of now, however, it will only provide a dictionary containing the query results.
	"""
	def __init__(self):
		self.api_url = "http://toxgate.nlm.nih.gov/cgi-bin/sis/search"	
		self.databases = ["hsdb","ccris","genetox","iris","iter","lact"]
	
	def findByQuery(self, query, dbs=[]):
		"""Retreives the ids or more TOXNET chemicals based on a query
	
		:param query: A single query or a list of queries.
		:param dbs: (optional) A list of databases to search in. Will search in ALL available databases if it is not defined.
		:rtype: Either a single dictionary or a list of dictionaries if a list of queries was inserted. No result will return None.
		"""
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
				chemicals.append( self.parseQueryResult(r.text) )
						
		if isinstance(query, str):
			return chemicals[0]
		elif isinstance(query, list):
			return chemicals
			
	def parseQueryResult(self, xml):
		"""Parses the XML result of a TOXNET Query
		
		:param xml: The XML returned by TOXNET
		:rtype: A dictionary with the results from the query.
		"""
		
		# The Query result will contain some HTML linebreaks, which do not count as correct XML
		xml = xml.replace("<br>","\n")
		dictionary = xmltodict.parse(xml)
		root = dictionary["QueryResult"]
		print json.dumps(root, sort_keys=True, indent=4, separators=(',', ': '))
		return root
	
	def specifyControls(self):
		pass
	
	def specifyInput(self):
		pass
		
	def specifyOutput(self):
		pass
		
	def start(self, **kwargs):
		pass
	
	
# TESTING #
def test_findByQuery():
	t = TOXNET()
	results = t.findByQuery('Zinc')
