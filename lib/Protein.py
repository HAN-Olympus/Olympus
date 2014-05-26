import Olympus.lib.StoredObject

class Protein(StoredObject.StoredObject):
	def __init__(self):
		self.id = {}
		self.name = {}
		self.existence = {}
		self.creationDate = {}
		self.modifiedDate = {}
		self.geneName = {}
		self.organism = {}
		self.sequence = {}
		self.sequencelength = {}
		
		super(Protein, self).__init__(database = "olympus", collection = "proteins")