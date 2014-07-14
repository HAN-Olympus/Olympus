"""
@name PubMedIndex
@author Stephan Heijl
@module PubMed
@version 0.0.3
"""

from Olympus.lib.StoredObject import StoredObject

class PubMedIndex(StoredObject):
	def __init__(self):
		self.id = {}
		self.gene = {}
		
		super(PubMedIndex, self).__init__(database = "olympus", collection = "pubmedindexes")