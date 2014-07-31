"""
@name Chemical
@author Stephan Heijl
@module TOXNET
@version 0.2.0
"""

from Olympus.lib.StoredObject import StoredObject

class Chemical(StoredObject):
	def __init__(self):
		self.id = {}
		self.name = {}
		
		super(Chemical, self).__init__(database = "olympus", collection = "chemicals")