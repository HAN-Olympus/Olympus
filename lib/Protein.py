import StoredObject

class Protein(StoredObject.StoredObject):
	def __init__(self):
		self.id = {}
		self.name = {}
		self.genename = {}
		self.organism = {}
		self.sequence = {}
		self.sequencestatus = {}		
		
		super(Article, self).__init__(database = "olympus", collection = "proteins")