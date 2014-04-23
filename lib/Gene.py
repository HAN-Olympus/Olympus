import StoredObject

class Gene(StoredObject.StoredObject):
	def __init__(self, **kwargs):
		for key, value in kwargs.items():
			setattr(self, key, value)
			
		super(Gene, self).__init__(database = "olympus", collection = "genes")