import AcquisitionModule
from Protein import Protein
from collections import OrderedDict
import requests, urllib
import xmltodict
import json
import pprint

class Uniprot(AcquisitionModule.AcquisitionModule):
	def __init__(self):
		self.api_url = "http://www.uniprot.org/uniprot/"
		
	def composeQueryUrl(self, params):
		textparams = urllib.urlencode(params)
		return self.api_url + "?" + textparams		
	
	# Retreives one or more Uniprot proteins by their identification code and returns a list of Protein objects
	# @param ids	: A single ID or a list of IDs
	# @returns		: A list of Protein objects, will insert None if no result was found for a given ID
	
	def getById(self, ids):
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
	
	# Turns raw XML from Uniprot into a proper Protein object
	# @param xml	: An XML string to be parsed.
	# @returns		: A Protein object.	
	def convertXmlToProtein(self, xml):
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
# TESTING #

def test_composeQueryUrl():
	u = Uniprot()
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
	u = Uniprot()
	results = u.getById('A0QSU3')
	
def test_getByIdList():
	u = Uniprot()
	results = u.getById('P13368 P20806 Q9UM73 P97793 Q17192'.split(" "))
	
