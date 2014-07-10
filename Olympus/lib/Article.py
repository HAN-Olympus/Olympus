"""
@name Article
@author Stephan Heijl
@module PubMed
@version v1.0.0
"""

from Olympus.lib.StoredObject import StoredObject

class Article(StoredObject):
	def __init__(self):
		self.id = {}
		self.title = {}
		self.source = {}
		self.authors = {}
		self.abstract = {}
		self.dateCreated = {}
		self.dateCompleted = {}
		
		super(Article, self).__init__(database = "olympus", collection = "articles")