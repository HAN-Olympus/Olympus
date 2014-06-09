from Olympus.lib.StoredObject import StoredObject

class CodingSequence(StoredObject):
	def __init__(self):
		self.id = {}
		self.gene = {}
		self.sequence = {}
		
		super(CodingSequence, self).__init__(database = "olympus", collection = "codingsequences")