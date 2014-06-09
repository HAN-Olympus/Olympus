from Olympus.lib.StoredObject import StoredObject

class TOXNETResult(StoredObject):
	def __init__(self):
		self.id = {}
		self.name = {}
		
		super(TOXNETResult, self).__init__(database = "olympus", collection = "chemicals")