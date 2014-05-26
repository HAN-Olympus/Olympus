import Olympus.lib.StoredObject

class Article(StoredObject.StoredObject):
	def __init__(self):
		self.id = {}
		self.title = {}
		self.source = {}
		self.authors = {}
		self.abstract = {}
		self.dateCreated = {}
		self.dateCompleted = {}
		
		super(Article, self).__init__(database = "olympus", collection = "articles")