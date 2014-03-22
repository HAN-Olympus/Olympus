# Olympus StoredObject Class
# This is a stored object, the base form of an object that can be stored in our database

from abc import ABCMeta, abstractmethod
from Storage import Storage
import random, time

class StoredObject():
	__metaclass__ = ABCMeta
	
	def __init__(self, database=None, collection=None, name = ""):
		self._database = database
		self._collection = collection
		self.name = name
		self._className = self.__class__.__name__
	
	def setDatabase(self,database):
		self._database = database
		
	def setCollection(self, collection):
		self._collection = collection
	
	def save(self):
		print type(self)
		# Can't save without a database or a table
		if self._database is None:
			raise ValueError, "No database has been selected."
		if self._collection is None:
			raise ValueError, "No collection has been selected."
	
		# Check private variables. We probably shouldn't store these.
		document = {}	
		for key, value in self.__dict__.items():
			key = key.replace("_"+self._className, "")
			if key.startswith("__"):
				continue
			document[key] = value
		
		# Let's store this object
		storage = Storage()
		storage.getDatabase(self._database)
		storage.getCollection(self._collection)
		storage.insertDocuments(document)
		self._id = document["_id"]
	
	def loadFromRawData(self, data):
		newObject = self.__class__
		for key, value in data.items():
			setattr(newObject, key, value)
			
		return newObject
	
	def getObjectsByKey(self, key, value, limit=None):
		storage = Storage()
		database = self._database
		collection = self._collection
		
		if database is None or collection is None:
			raise ValueError, "The object needs to be assigned a database and a collection."
		
		storage.getDatabase(database)
		storage.getCollection(collection)
		documents = storage.getDocuments({key:value}, limit)
		
		objects = [ self.loadFromRawData( data ) for data in documents ]
		return objects
		
	def remove(self):
		storage = Storage()
		database = self._database
		collection = self._collection
		print type(self)
		
		if database is None or collection is None:
			raise ValueError, "The object needs to be assigned a database and a collection."
		
		storage.getDatabase(database)
		storage.getCollection(collection)
		documents = storage.removeDocuments({"_id":self._id})
					
		
# For testing purposes only #
		
class TestObject(StoredObject):
	def __init__(self):
		super(TestObject, self).__init__(database = "test_database", collection = "test_collection")
		
def test_createTestObject():
	r = 874549078556789
	tn = TestObject()
	tn.random = r
	tn.save()

def test_findTestObject():
	r = 874549078556789
	t = TestObject().getObjectsByKey("random",r)
	assert len(t) > 0
	assert t[0].random == r
	
def test_removeObject():
	r = 874549078556789
	t = TestObject().getObjectsByKey("random",r)
	print t
	print type(t[0])
	t[0]().remove()
	
def test_loadFromRawData():
	r = 984598324040348
	t = TestObject().loadFromRawData({"r":r})
	assert t.r == r