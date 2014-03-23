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
		self._type = self.__class__.__name__
	
	def setDatabase(self,database):
		self._database = database
		
	def setCollection(self, collection):
		self._collection = collection
	
	def save(self):
		# Can't save without a database or a table
		if self._database is None:
			raise ValueError, "No database has been selected."
		if self._collection is None:
			raise ValueError, "No collection has been selected."
	
		# Check private variables. We probably shouldn't store these.
		document = {}	
		for key, value in self.__dict__.items():
			key = key.replace("_"+self._type, "")
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
		
		if database is None or collection is None:
			raise ValueError, "The object needs to be assigned a database and a collection."
		
		storage.getDatabase(database)
		storage.getCollection(collection)
		documents = storage.removeDocuments({"_id":self._id})
		
	def setAttribute(self, attr, source, value):
		attribute = {}
		attribute[source] = value
		setattr(self,attr,attribute)
		
	def addAttribute(self, attr, source, value):
		attribute = getattr(self, attr, {})
		attribute[source] = value
		setattr(self,attr,attribute)

	def getAttribute(self, attr, source):
		if not hasattr(self, attr):
			return None			
		attribute = getattr(self, attr, {})
		return attribute.get(source, None)
		
		
# For testing purposes only #
		
class TestObject(StoredObject):
	def __init__(self):
		super(TestObject, self).__init__(database = "test_database", collection = "test_collection")

import random
r = random.randrange(1000000000,9999999999)
		
def test_setAttribute():
	t = TestObject()
	t.setAttribute("random", "python", r)
	assert t.random["python"] == r
	
def test_addAttribute():
	t = TestObject()
	t.addAttribute("random", "python", r)
	t.addAttribute("random", "lua", r+1)
	assert t.random["python"] == r
	assert t.random["lua"] == r+1
	
def test_getAttribute():
	t = TestObject()
	t.addAttribute("random", "python", r)
	assert t.getAttribute("random", "python") == r
		
def test_createTestObject():
	t = TestObject()
	t.random = r
	t.save()

def test_findTestObject():
	t = TestObject().getObjectsByKey("random",r)
	assert len(t) > 0
	assert t[0].random == r
	
def test_removeObject():
	t = TestObject().getObjectsByKey("random",r)
	t[0]().remove()
	
def test_loadFromRawData():
	t = TestObject().loadFromRawData({"r":r})
	assert t.r == r