"""
@name Gene
@author Stephan Heijl
@module WormBase
@version 0.0.3
"""

from Olympus.lib.StoredObject import StoredObject

class Gene(StoredObject):
	def __init__(self, **kwargs):
		self.name = {}
		self.sequence = {}
		self.note = {}
		self.score = {}
		self.phase = {}
		self.wormbase = {}
		self.strand = {}
		self.position = {}
		
		for key, value in kwargs.items():
			setattr(self, key, value)
			
		super(Gene, self).__init__(database = "olympus", collection = "genes", name = self.name)