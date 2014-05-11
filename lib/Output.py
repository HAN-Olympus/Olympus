import StoredObject

class Output(StoredObject.StoredObject):
	def __init__(self):
		self.job_id = 0
		super(Output, self).__init__(database = "olympus", collection = "output")
		
	def getByJobId(self, id):
		print id
		results = self.getObjectsByKey("job_id", id)
		return results