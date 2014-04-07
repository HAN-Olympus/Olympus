import AcquisitionModule
import requests, urllib
import json

class WormBase(AcquisitionModule.AcquisitionModule):
	""" This module allows for retrieval of chemicals from the WormBase REST API.
	
	WormBase provides a RESTful API via their webservers. All content can be accessed on three levels:
	
	* Field : A single key/value pair
	* Widget : A collection of fields
	* Page : The entire page
	"""
	def __init__(self):
		self.api_url = "http://api.wormbase.org/rest/"
	
	def findByField(self, field, value):
		return None
		
# TESTING #
