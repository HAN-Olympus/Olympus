"""
@name WormBase
@author Stephan Heijl
@module WormBase
@version 0.0.3
"""

from Olympus.modules.acquisition.AcquisitionModule import AcquisitionModule
from Olympus.lib.Collection import Collection
from Olympus.lib.Log import Log
from Olympus.lib.Gene import Gene
from Olympus.lib.Protein import Protein

from Olympus.lib.controls.Text import Text
from Olympus.lib.controls.Select import Select

import requests, urllib
import json,re

class WormBase(AcquisitionModule):
	""" This module allows for retrieval of chemicals from the WormBase REST API.
	
	WormBase provides a RESTful API via their webservers. All content can be accessed on three levels:
	
	* Field : A single key/value pair
	* Widget : A collection of fields
	* Page : The entire page
	"""
	def __init__(self):
		self.api_url = "http://api.wormbase.org/rest/"
	
	def findByField(self, type, value, field):
		""" Access the Wormbase database by field.
		
		:param type: The type of item you would like to access
		:param value: The value of the type you would like to access. (For example a gene id, like WBGene00006763)
		:param field: The field you would like to access.
		"""
		headers = {'content-type': 'application/json'}
		url = self.api_url + "field/" + type + "/" + value + "/" + field
		r = requests.get(url, headers=headers)
		response = r.text
		
		if "text/html" in r.headers.get('content-type'):
			errorResponse = re.match("Error Message:\n(.+?)<\/textarea>", r.text)
			
			print errorResponse
			
			if errorResponse == None:
				raise ValueError, "The server encountered an error but did not provide a reason."
			raise ValueError, "The server responded with an error: %s" % errorResponse.group(1)
		
		return json.loads(response)
	
	def specifyControls(self):
		controls = {
			"searchterm" : Text("searchterm", value="", label="Search term"),
			"type" : Select("searchtype", label="Search type")
		}
		
		controls["type"].addOption("gene","Gene")
		return controls
		
	def specifyInput(self):
		return None
		
	def specifyOutput(self):
		geneCollection = Collection(Gene)
		proteinCollection = Collection(Protein)
		log = Log()
		
		output = {
			"errors":[log],
			"result":[geneCollection, proteinCollection]
		}
		
		return output
		
	def start(self, **kwargs):
		# This is currently just test data!
		return Gene(**self.findByField("gene", "WBGene00006763", "cloned_by"))
		
# TESTING #

from nose.tools import *

def test_findByField():
	wb = WormBase()
	wb.findByField("gene", "WBGene00006763", "cloned_by")

@raises(ValueError)
def test_findByFieldError():
	wb = WormBase()
	wb.findByField("gene", "former_members", "cloned_by")
	