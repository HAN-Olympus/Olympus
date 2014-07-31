"""
@name Output
@author Stephan Heijl
@module core
@version 0.2.0
"""

from Olympus.lib.StoredObject import StoredObject

class Output(StoredObject):
	def __init__(self):
		self.job_id = 0
		super(Output, self).__init__(database="olympus", collection = "output")
		
	def getByJobId(self, id):
		print id
		results = self.getObjectsByKey("job_id", id)
		return results