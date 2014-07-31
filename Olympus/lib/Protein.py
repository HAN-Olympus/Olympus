"""
@name Protein
@author Stephan Heijl
@module WormBase
@version 0.2.0
"""

from Olympus.lib.StoredObject import StoredObject

class Protein(StoredObject):
	def __init__(self):
		self.id = {}
		self.name = {}
		self.existence = {}
		self.creationDate = {}
		self.modifiedDate = {}
		self.gene = {}
		self.organism = {}
		self.sequence = {}
		self.sequencelength = {}
		
		super(Protein, self).__init__(database = "olympus", collection = "proteins")