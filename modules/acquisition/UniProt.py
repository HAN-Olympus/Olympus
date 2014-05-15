import AcquisitionModule
from Olympus.lib.Protein import Protein
try:
	from collections import OrderedDict
except ImportError:
	from ordereddict import OrderedDict
import requests, urllib
import xmltodict
import json

class UniProt(AcquisitionModule.AcquisitionModule):
	""" This module allows for retrieval of protein information from the Uniprot API."""
	
	def __init__(self):
		self.api_url = "http://www.uniprot.org/uniprot/"
		
	def composeQueryUrl(self, params):
		""" Composes a proper URL based on the given parameters.
		
		:param params: A dictionary with parameters
		:rtype: A string containing a URL to the API
		"""
		textparams = urllib.urlencode(params)
		return self.api_url + "?" + textparams		
	
	def getById(self, ids):
		"""Retreives one or more Uniprot proteins by their identification code and returns a list of Protein objects
		
		:param ids: A single ID or a list of IDs
		:rtype: A list of Protein objects, will insert None if no result was found for a given ID
		"""
		proteins = []
		ids = [ids] if isinstance(ids, str) else ids
		for id in ids:
			url = self.composeQueryUrl({'query': id, 'format':'xml'})
			r = requests.get(url)
			
			if len(r.text) > 0:
				protein = self.convertXmlToProtein(r.text)
			else:
				protein = None
			proteins.append(protein)
			
		return proteins
	
	def convertXmlToProtein(self, xml):
		"""Turns raw XML from Uniprot into a proper Protein object.
		
		:param xml: An XML string to be parsed.
		:rtype: A Protein object.
		"""
		# XML to dictionary
		proteinObject = Protein()
		
		dictionary = xmltodict.parse(xml)
		root = dictionary["uniprot"]
		entry = root["entry"]
		
		for element, value in entry.items():
			if element == "@accession":
				proteinObject.addAttribute("id", "uniprot", value)
				
			if element == "name":
				proteinObject.addAttribute("proteinShortName", "uniprot", value)
				
			if element == "protein":
				fullname = value["recommendedName"]["fullName"]
				proteinObject.addAttribute("proteinFullName", "uniprot", fullname)
				
			if element == "@created":
				year,month,day = value.split("-")
				proteinObject.addAttribute("creationDate", "uniprot", self.convertDateToNative(day,month,year) )
				
			if element == "@modified":
				year,month,day = value.split("-")
				proteinObject.addAttribute("modifiedDate", "uniprot", self.convertDateToNative(day,month,year) )
			
			if element == "comment":
				for comment in entry["comment"]:
					if "text" in comment:
						text = comment["text"]["#text"] if isinstance(comment["text"], OrderedDict) else comment["text"]
						proteinObject.addAttribute(comment["@type"], "uniprot",text)
					
			if element == "gene":
				genes = []
				for gene in value["name"]:
					if "#text" in gene and isinstance(gene, OrderedDict):
						genes.append(gene["#text"])
					
				proteinObject.addAttribute("geneName", "uniprot", genes)
					
			if element == "organism":
				if isinstance(value["name"], list):
					organisms = []
					for organism in value["name"]:
						organisms.append(organism["#text"])
					
				else:
					proteinObject.addAttribute("organism", "uniprot", value["name"]["#text"])
				
			
			if element == "sequence":
				proteinObject.addAttribute("sequence", "uniprot",value["#text"].replace("\n",""))
				proteinObject.addAttribute("sequencelength", "uniprot",value["@length"].replace("\n",""))


		return proteinObject
		
	def specifyInput(self):
		pass
		
	def specifyOutput(self):
		pass
		
	def start(self, **kwargs):
		pass
		
# TESTING #

def test_composeQueryUrl():
	u = UniProt()
	params = {
		'from':'ACC',
		'to':'P_REFSEQ_AC',
		'format':'tab',
		'query':'P13368 P20806 Q9UM73 P97793 Q17192'
	}
	desiredUrl = "http://www.uniprot.org/uniprot/?to=P_REFSEQ_AC&query=P13368+P20806+Q9UM73+P97793+Q17192&from=ACC&format=tab"
	url = u.composeQueryUrl(params)
	assert url == desiredUrl

def test_getByIdSingle():
	u = UniProt()
	results = u.getById('A0QSU3')

def test_getByIdList():
	u = UniProt()
	results = u.getById('P13368 P20806 Q9UM73 P97793 Q17192'.split(" "))
