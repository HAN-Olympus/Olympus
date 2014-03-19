import Singleton
from pymongo import MongoClient

class Storage(Singleton.Singleton):
	def __init__(self):
		self.__client = MongoClient()
		self.__currentCollection = None
		self.__currentDatabase = None
		
	def getHost(self):
		return self.__client.host
		
	def getPort(self):
		return self.__client.port
		
	def isAlive(self):
		return self.__client.alive()
	
	def getDatabase(self, database):
		self.__currentDatabase = self.__client[database]
		return self.__currentDatabase
		
	def dropDatabase(self, database):
		self.__client.drop_database(database)
		return True
	
	def getCollection(self, collection):
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
		
		self.__currentCollection = self.__currentDatabase[collection]
		return self.__currentCollection
		
	def dropCollection(self, collection):
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
		
		self.__currentDatabase[collection].drop()
		return True
		
	def insertDocuments(self, document):
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
			
		self.__currentCollection.insert( document )
		
	def removeDocuments(self, match):
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
			
		self.__currentCollection.remove(match)
		return True
		
	def getDocuments(self, match, limit=None):
		if self.__currentDatabase == None:
			raise ValueError, "There was no database selected"
			
		if self.__currentCollection == None:
			raise ValueError, "There was no collection selected"
		
		if limit is None:
			return self.__currentCollection.find(match)
		else:
			return self.__currentCollection.find(match).limit(limit)
			
	def __del__(self):
		self.__client.close()
		
def test_Storage():
	storage1 = Storage()
	storage2 = Storage()
	assert storage1 == storage2, "Storage is not a singleton"
	
def test_getHost():
	storage = Storage()
	storage.getHost()
	
def test_getPort():
	storage = Storage()
	storage.getPort()
	
def test_isAlive():
	storage = Storage()
	assert storage.isAlive(), "The connection has failed for some reason"
	
def test_getDatabase():
	storage = Storage()
	
def test_getCollection():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	
def test_insertDocuments():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.insertDocuments({"name":"test_document"})
	
def test_getDocuments():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	assert storage.getDocuments({"name":"test_document"}).count() > 0, "Document was not inserted."
	
def test_removeDocuments():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.removeDocuments({"name":"test_document"})
	
def test_dropCollection():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.getCollection("test_collection")
	storage.dropCollection("test_collection")
	
def test_dropDatabase():
	storage = Storage()
	storage.getDatabase("test_database")
	storage.dropDatabase("test_database")
	
	
	
	
	