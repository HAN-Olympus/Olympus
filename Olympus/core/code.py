{'Olympus': {'lib': {'Article': 'Article',
                     'Collection': 'Collection',
                     'Config': 'Config',
                     'Log': 'Log',
                     'Module': 'Module',
                     'Singleton': 'Singleton',
                     'Storage': 'Storage',
                     'StoredObject': 'StoredObject'},
             'modules': {'acquisition': {'AcquisitionModule': 'AcquisitionModule'}}}}

def matryoshka(cls):
	# get types of classes
	class classtypes:
		pass
	classtypes = (type, type(classtypes))

	# get names of all public names in outer class
	directory = [n for n in dir(cls) if not n.startswith("_")]

	# get names of all non-callable attributes of outer class
	attributes = [n for n in directory if not callable(getattr(cls, n))]

	# get names of all inner classes
	innerclasses = [n for n in directory if isinstance(getattr(cls, n), classtypes)]

	print cls.__name__
	print cls
	globals()[cls.__name__] = cls
	return cls
		
@matryoshka
class Olympus():
	@matryoshka
	class modules():
		def __init__(self):
			@matryoshka
			class acquisition(Olympus.lib.Module):
				""" Acquisition base class.

				Abstract class that provides base classes and access to classes in the ../lib directory
				Uses part of the additionalImport script to allow access to the lib classes.
				Refer to the page on Acquisition modules for a list of modules distributed with this version of Olympus.
				"""

				from Olympus.lib.Module import Module
				import datetime

				@matryoshka
				class AcquisitionModule(Module):
					""" Base class for all acquisition modules. Provides some generic methods. """

					def __init__(self):
						""" Does nothing. """
						pass

					def convertDateToNative(self, day, month, year):
						"""Convert a day, month, year notation to a Python datetime object

						:param day: Numeric, the day (1-31)
						:param month: Numeric, the month (1-12)
						:param year: Numeric, the year
						:rtype: A properly formed datetime object
						"""

						dt = datetime.datetime(int(year), int(month), int(day))
						return dt
			
	@matryoshka
	class lib():
		def __init__(self):
			@matryoshka
			class Singleton(object):
				""" The base singleton class for Olympus. """

				_instance = None
				def __new__(cls, *args, **kwargs):
					""" This returns the existing instance of the class every time an attempt is made to instantiate it. """
					if not cls._instance:
						cls._instance = super(Singleton, cls).__new__(
											cls, *args, **kwargs)

					cls.instantiated = False
					""" Is true if this object has already been instantiated once. """
					return cls._instance
			@matryoshka
			class Log(object):
				def __init__(self):
					self.contents = []
					self.__pointer = 0

				def open(self, name="default", mode="w"):
					pass

				def read(self):
					return self.contents[self.__pointer:]

				def seek(self, n):
					self.__pointer = n

				def write(self, item):
					self.contents.append(item)


			from abc import ABCMeta, abstractmethod
			from Olympus.lib.Storage import Storage
			import random, time, datetime, copy

			@matryoshka
			class StoredObject():
				""" This is a StoredObject, the base class of anything that is to be stored in our database.
				Inheriting from this in lieu of communicating directly with PyMongo or Storage() will allow you to instantaneously save, merge and remove your objects. As this is an abstract class it cannot be instantiated directly and must therefor be subclassed.
				"""
				__metaclass__ = ABCMeta

				def __init__(self, database=None, collection=None, name = ""):
					""" Sets up the object

					:param database: Optional, the database where this object is to be stored.
					:param collection: Optional, the collecion where this object is to be stored.
					:param name: The pretty name of this object.
					"""
					self._database = database
					self._collection = collection
					self.name = name
					self._created = datetime.datetime.now()
					self._type = self.__class__.__name__

				def setDatabase(self,database):
					"""Sets the database for this object."""
					self._database = database

				def setCollection(self, collection):
					"""Sets the collection for this object. This is analogous to a table in relational databases."""
					self._collection = collection

				def save(self):
					"""Save this object into the database with all its public attributes."""

					if self._database is None:
						raise ValueError, "No database has been selected."
					if self._collection is None:
						raise ValueError, "No collection has been selected."


					document = {}	
					for key, value in self.__dict__.items():
						key = key.replace("_"+self._type, "")
						if key.startswith("__"):
							continue
						document[key] = value


					storage = Storage()
					storage.getDatabase(self._database)
					storage.getCollection(self._collection)

					if hasattr(self, "_id"):
						storage.saveDocument(document)
					else:
						storage.insertDocuments(document)
						self._id = document["_id"]

				def loadFromRawData(self, data):
					""" This will create an object of the given class from a raw dictionary. Typically this would be what comes out of a the database, but it can also be used to initiate a whole new object from scratch.

					:param data: A dictionary containing the data to be set for this new object.
					:rtype: A new instance of this class with all the data specified pre set.
					"""
					newObject = self.__class__()
					for key, value in data.items():
						setattr(newObject, key, value)

					return newObject

				def getObjectsByKey(self, key, value, limit=None):
					""" This will retrieve documents from the database and collection specified by this object based on one of their keys and convert them to their proper Python object state.

					:param key: The key to select on.
					:param value: The value to search for.
					:param limit: The maximum amount of objects to return. Will return all results by default.
					:rtype: All the matching objects stored in the database.
					"""
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
					""" Removes this object from the database. It will still remain in memory, however, and can be resaved at a later time provided that the original reference is maintained."""
					storage = Storage()
					database = self._database
					collection = self._collection

					if database is None or collection is None:
						raise ValueError, "The object needs to be assigned a database and a collection."

					storage.getDatabase(database)
					storage.getCollection(collection)
					documents = storage.removeDocuments({"_id":self._id})

				def setAttribute(self, attr, source, value):
					""" Set the given attribute to this value. It will overwrite any previous data.

					:param attr: The name of the attribute.
					:param source: The source of data to be set.
					:param value: The value that should be set for this source.
					"""
					attribute = {}
					attribute[source] = value
					setattr(self,attr,attribute)

				def addAttribute(self, attr, source, value):
					""" Add the given attribute to this value. It will retain any other data from other sources, but will overwrite any data from the same source in this attribute.

					:param attr: The name of the attribute.
					:param source: The source of data to be set.
					:param value: The value that should be set for this source.
					"""
					attribute = getattr(self, attr, {})
					attribute[source] = value
					setattr(self,attr,attribute)

				def getAttribute(self, attr, source=None):
					""" Will return the data stored in this attribute from the given source.

					:param attr: The name of the attribute.
					:param source: The source of data to be set. (Optional)
					:rtype: The data stored in this attribute from this source.
					"""
					if not hasattr(self, attr):
						return None			
					attribute = getattr(self, attr, {})
					if source == None:
						return attribute
					return attribute.get(source, None)

				def __add__(self, other):
					""" Overloads the + (plus) operator and uses it to merge two objects. If there is a conflict for a key the value from the first object in the equation will be chosen.

					For example::

						ProteinOne = Protein()
						ProteinTwo = Protein()
						ProteinOne.setAttribute("attribute", "source", "ValueOne")
						ProteinOne.setAttribute("attribute", "source", "ValueTwo")

						ProteinMerged = ProteinOne + ProteinTwo
						ProteinMerged.getAttribute("attribute","source") == "ValueOne" 

					The original two objects will not be affected.

					:param other: The object that this object will be merged with.
					:rtype: A new object with the merged date from the two given objects.
					"""
					attributes = self.mergeObjects(self,other)
					newObject = self.__class__()
					newObject.__dict__ = attributes
					return newObject

				def mergeObjects(self, objectOne, objectTwo, path=None):
					""" Takes the attributes from two objects and attempts to merge them. If there is a conflict for a key the value from the first object in will be chosen.

					:param objectOne: The first object
					:param objectTwo: The second object
					:param path: The root of the merger.
					:rtype: A dictionary of merged values.
					"""
					a = copy.deepcopy(objectOne.__dict__)
					b = copy.deepcopy(objectTwo.__dict__)

					attributes = self.merge(a,b,path)
					return attributes

				def merge(self, a, b, path=None):
					""" Recursively merges two dictionaries. If there is a conflict for a key the value from the first object in will be chosen. All the changes are inserted into the first dictionary.

					:param a: The first dictionary.
					:param b: The second dictionary.
					:param path: The root of the merger.
					:rtype: A dictionary of merged values.
					"""
					if path is None: path = []
					for key in b:
						if key in a:
							if isinstance(a[key], dict) and isinstance(b[key], dict):
								self.merge(a[key], b[key], path + [str(key)])
							elif a[key] == b[key]:
								pass 
							else:

								pass

						else:
							a[key] = b[key]
					return a




			@matryoshka
			class TestObject(StoredObject):
				""" TestObject implements only the most basic of the StorageObject's methods for testing purposes. """
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
				if isinstance(t[0], TestObject):
					t[0].remove()
				else:
					t[0]().remove()

			def test_loadFromRawData():
				t = TestObject().loadFromRawData({"r":r})
				assert t.r == r

			def test_mergeObjects():
				t1 = TestObject()
				t2 = TestObject()

				t1.addAttribute("rand", "python", r)
				t2.addAttribute("rand", "lua", r+1)
				resultingAttributes = TestObject().mergeObjects(t1,t2)

				assert resultingAttributes["rand"]["python"] == r
				assert resultingAttributes["rand"]["lua"] == r+1

			def test_mergeByAddOperator():
				t1 = TestObject()
				t2 = TestObject()
				t1.addAttribute("rand", "python", r)
				t2.addAttribute("rand", "lua", r+1)

				t3 = t1+t2
				assert t3.getAttribute("rand", "python") == r
				assert t3.getAttribute("rand", "lua") == r+1

			from Olympus.lib.Singleton import Singleton
			from pymongo import MongoClient

			@matryoshka
			class Storage(Singleton):
				""" The storage module provides a layer of abstraction over PyMongo. 
					This will allow us to, if needed, exchange the databases without breaking countless modules 
					that are dependent on database access.
				"""
				def __init__(self):
					""" Initializes the connection with the Mongo database. 
					As this is a Singleton, this is only done `once` per instance of Olympus resulting in lower connection time overhead.
					This will pose problems if the ongoing connection is forcefully closed for whatever reason.
					"""
					self.__client = MongoClient()
					self.__currentCollection = None
					self.__currentDatabase = None

				def getHost(self):
					""" Returns the database host. """
					return self.__client.host

				def getPort(self):
					""" Returns the database port. """
					return self.__client.port

				def isAlive(self):
					""" Checks whether or not the connection to the database is alive.

					:rtype: Returns the state of the connection as a boolean.
					"""
					return self.__client.alive()

				def getDatabase(self, database):
					""" Sets the database to the one specified. If it does not yet exist, it will be created when a document is inserted.

					:param database: The name the database that is to be accessed.
					:rtype: The name of the database that is currently being accessed.
					"""
					self.__currentDatabase = self.__client[database]
					return self.__currentDatabase

				def dropDatabase(self, database):
					""" Drops the currently selected database.

					:rtype: True if the database was dropped succesfully.
					"""
					self.__client.drop_database(database)
					return True

				def getCollection(self, collection):
					""" Sets the collection to the one specified. If it does not yet exist, it will be created when a document is inserted.
					Will throw a ValueError if no database has been selected.

					:param collection: The name the collection that is to be accessed.
					:rtype: The name of the collection that is currently being accessed.
					"""
					if self.__currentDatabase == None:
						raise ValueError, "There was no database selected"

					self.__currentCollection = self.__currentDatabase[collection]
					return self.__currentCollection

				def dropCollection(self, collection):
					""" Drops the currently selected collection.
					Will throw a ValueError if no collection has been selected.

					:rtype: True if the collection was dropped succesfully.
					"""
					if self.__currentDatabase == None:
						raise ValueError, "There was no database selected"

					self.__currentDatabase[collection].drop()
					return True

				def insertDocuments(self, document):
					""" Inserts a document into the currently selected collection in the currently selected database.
					Will throw a ValueError if no database or collection has been selected.

					:param document: A dictionary that will be stored as a document. Its contents can include strings, numbers and several types of native objects, like `datetime`.
					"""
					if self.__currentDatabase == None:
						raise ValueError, "There was no database selected"

					if self.__currentCollection == None:
						raise ValueError, "There was no collection selected"

					self.__currentCollection.insert( document )

				def saveDocument(self, document):
					""" Inserts a document into the currently selected collection in the currently selected database.
					Will throw a ValueError if no database or collection has been selected.

					:param document: A dictionary that will be stored as a document. Its contents can include strings, numbers and several types of native objects, like `datetime`.
					"""

					if not hasattr(document, "_id") and "_id" not in document.keys():
						raise ValueError, "This document does not have a Mongo ID"

					if self.__currentDatabase == None:
						raise ValueError, "There was no database selected"

					if self.__currentCollection == None:
						raise ValueError, "There was no collection selected"

					self.__currentCollection.save( document )

				def removeDocuments(self, match):
					""" Removes all documents that match the give query. 
					Refer to the [MongoDB documentation](http://docs.mongodb.org/manual/tutorial/query-documents) on this subject for more information on queries.

					:param match: A query for the database to match documents to.
					"""
					if self.__currentDatabase == None:
						raise ValueError, "There was no database selected"

					if self.__currentCollection == None:
						raise ValueError, "There was no collection selected"

					self.__currentCollection.remove(match)
					return True

				def getDocuments(self, match, limit=None):
					""" Returns all documents that match the give query, up until `limit` is reached. By default, this will return every single result.
					Refer to the [MongoDB documentation](http://docs.mongodb.org/manual/tutorial/query-documents) on this subject for more information on queries.

					:param match: A query for the database to match documents to.
					:param limit: The maximum amount of documents to return.
					"""
					if self.__currentDatabase == None:
						raise ValueError, "There was no database selected"

					if self.__currentCollection == None:
						raise ValueError, "There was no collection selected"

					if limit is None:
						return self.__currentCollection.find(match)
					else:
						return self.__currentCollection.find(match).limit(limit)

				def __del__(self):
					""" Gracefully closes the connection to the server when this singleton is deleted. """
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

			def test_saveDocument():
				storage = Storage()
				storage.getDatabase("test_database")
				storage.getCollection("test_collection")

				doc = {"name":"test_document_save", "version":1}
				storage.insertDocuments(doc)
				ndoc = storage.getDocuments({"name":"test_document_save"})[0]
				ndoc["version"] = 2
				storage.saveDocument(ndoc)
				assert storage.getDocuments({"name":"test_document_save"}).count() == 1, "Document was duplicated."
				assert storage.getDocuments({"name":"test_document_save"})[0]["version"] == 2, "Document was not saved properly"

			def test_removeDocuments():
				storage = Storage()
				storage.getDatabase("test_database")
				storage.getCollection("test_collection")
				storage.removeDocuments({"name":"test_document"})
				storage.removeDocuments({"name":"test_document_save"})

			def test_dropCollection():
				storage = Storage()
				storage.getDatabase("test_database")
				storage.getCollection("test_collection")
				storage.dropCollection("test_collection")

			def test_dropDatabase():
				storage = Storage()
				storage.getDatabase("test_database")
				storage.dropDatabase("test_database")





			@matryoshka
			class Collection(object):
				""" A basic collection of results items, can be restricted to a certain type. """

				def __init__(self, restrict = None):
					self.__contents = []
					self.restrict = restrict
					self.__pointer = 0 

				def append(self, object):
					if self.restrict != None and not isinstance(object, self.restrict):
						raise ValueError, "This object can not be added to this restricted Collection."

					self.__contents.append(object)

				def remove(self, object):
					if self.__pointer >= self.__contents.index(object):
						self.__pointer -= 1
					self.__contents.remove(object)

				def __iter__(self):
					return self

				def rewind(self):
					self.__pointer = 0

				def seek(self, i):
					self.__pointer = i

				def get(self, i=None):
					if i == None:
						i = self.__pointer

					if i >= len(self.__contents) or i < 0:
						raise IndexError, "Out of range"

					return self.__contents[i]

				def next(self):
					if self.__pointer == len(self.__contents):
						raise StopIteration
					value = self.get()
					self.__pointer +=1
					return value

				def __len__(self):
					return len(self.__contents)

				def equalsType(self, other):
					if isinstance(other, Collection) and other.restrict == this.restrict:
						return True
					return False


			from nose.tools import raises

			def test_getappend():
				c = Collection()
				c.append("Hello")
				assert c.get() == "Hello"

			@raises(ValueError)
			def test_restriction():
				c = Collection(str)
				c.append("Hello")
				c.append(1)
				assert c.get() == "Hello"

			def test_remove():
				c = Collection()
				c.append("Hello")
				c.append(1)
				c.remove(1)
				assert len(c) == 1
				assert c.get() == "Hello" 
				c.append(2)
				c.append(3)
				c.seek(2)
				c.remove(2)
				assert c.get() == 3 

			def test_rewind():
				c = Collection()
				c.append(10)
				c.append(20)
				c.append(4)
				for n in c:
					pass
				c.rewind()
				assert c.get() == 10

			def test_seek():
				c = Collection()
				c.append(10)
				c.append(20)
				c.append(4)
				for n in c:
					pass
				c.seek(1)
				assert c.get() == 20

			def test_iter():
				c = Collection(int)
				sum = 0
				c.append(10)
				c.append(20)
				c.append(4)

				for n in c:
					sum += n

				assert sum == 34


			""" The Olympus Module Class. """


			from abc import ABCMeta, abstractmethod

			@matryoshka
			class Module(object):
				""" This abstract class is the basis for all modules. It does not as of yet implement any methods. """
				__metaclass__ = ABCMeta

				def __init__(self):
					pass

				def __repr__(self):
					""" Returns the class name as a basic representation of the module """
					return self.__class__.__name__

				def __str__(self):
					""" Returns the class name as a basic representation of the module """
					return self.__class__.__name__

				@abstractmethod
				def specifyInput():
					""" In order to determine what a module needs it needs to show the inputs it requires.
					Should return a dictionary with controls. The keys correspond to the keys that will passed into the start method.
					A dictionary like this: ::

					 {
					   "accessioncode" : Controls.Control_Text,
					   "limit" : Controls.Control_Integer,
					   "maxsize" : Controls.Control_Number
					 }

					Will, after the values have been gathered, result in a start call like this: ::

					 start(accessioncode="ABCDEF123", limit=20, maxsize=1.234)
					"""
					pass

				@abstractmethod
				def specifyOutput():
					""" This method should return a class (not an instance) of the type that should be returned. """
					pass

				@abstractmethod
				def start(self):
					""" Abstract method to start off functionality of the module as specified by `specifyInput()`."""
					pass

			from Olympus.lib.StoredObject import StoredObject

			@matryoshka
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
			from Olympus.lib.Singleton import Singleton
			import json, os, sys

			@matryoshka
			class Config(Singleton):
				""" Config is a Singleton that persistently stores settings and configurations for Olympus. 
				When called upon, it will export these to the configuration file for later retrieval.
				Among other things, it stores your username, your email for Entrez notifications and the enabled Olympus modules.
				The configuration files are set to be stored in a 'pretty' format, so as to be easily human-readable and -editable.
				"""

				def __init__(self):
					if self.instantiated:
						return 
					currentDir = os.path.dirname(__file__)

					olympusConfName = "../olympus.conf"
					olympusConfPath = os.path.abspath(currentDir + "/" + olympusConfName)

					defaultConfName = "../default.conf"
					defaultConfPath = os.path.abspath(currentDir + "/" + defaultConfName)

					self.configFileName = ""
					""" This attribute stores the location where the configuration is to be saved. """

					if os.path.exists(olympusConfPath):
						self.setConfig(json.load( open(olympusConfPath, "r") ))
						self.configFileName = olympusConfPath
					else:
						try:
							self.setConfig(json.load( open(defaultConfPath, "r") ))
							self.configFileName = defaultConfPath
						except:
							raise IOError, "No default configuration file found, you need a configuration file to use this module."

					self.applyConfig()
					self.instantiated = True
					""" Is true if this object has already been instantiated once. """

				def clear(self):
					""" Clears the Config instance from any and all attributes """
					self.__dict__ = {}

				def delete(self, key):
					""" Deletes a single key and its respective value from the Config

					:param key: The attribute that should be removed.
					"""
					delattr(self, key)

				def setConfig(self, config):
					""" Adds a while dictionary to set as a configuration file.
					After it has been set it should still be applied with `applyConfig()`.
					This will overwrite any attributes with the same key.

					:param config: The dictionary that should be set for the configuration. """
					self.conf = config

				def applyConfig(self):
					""" Applies the configuration dictionary that was set with `setConfig()`. 

					:rtype: returns True if the configuration was set successfully. False if otherwise."""
					if not hasattr(self, "conf"):
						return False

					for key,value in self.conf.items():
						setattr(self, key, value)

					del self.conf
					return True

				def addAttribute(self, key, value=None):
					""" Adds an attribute to the Config. 
					If the key does not yet exist, it will be added to the Config and placed in a list.
					If the key already exists and is not a list, it will be converted to a list containing the original value and the new value.

					:param key: The key of the attribute
					:param value: The value that will be added.
					"""

					if key not in self.__dict__:
						if value!=None:
							setattr(self, key, [value])
						else:
							setattr(self, key, {})
					else:
						if isinstance(self.key, list):
							self.key.append(value)
						else:
							self.key = [self.key, value]

				def getAttributes(self):
					""" Returns all the attributes currently in this Config.

					:rtype: A dictionary containing all the attributes in this Config.
					"""
					return self.__dict__

				def save(self):
					""" Saves the Config to the file it was initialized from. By default, this is `default.conf`. """
					confFile = open(self.configFileName, "w")

					configFileName = self.configFileName
					del self.configFileName
					json.dump(self.getAttributes(), confFile, sort_keys=True, indent=4, separators=(',', ': '))
					confFile.close()
					self.configFileName = configFileName

			def test_Config():
				c = Config()
				assert c.__dict__["username"] == c.username
				assert c.username == "default" or c.username == "olympus"

			def test_addAttribute():
				c = Config()
				c.addAttribute("a", "b")
				print c.a
				assert c.a == ["b"]

			def test_getAttributes():
				c = Config() 
				assert c.getAttributes()["a"] == ["b"]

			def test_save():
				c = Config()
				c.save()
				print c.configFileName
				assert False

			def test_clear():
				c = Config()
				c.clear()
				assert not hasattr(c, "a")

			def test_save():
				c = Config()
				oldName = c.configFileName
				nameParts = c.configFileName.split("/")
				newName = "/".join(nameParts[:-1]) + "/test.conf"
				c.configFileName = newName
				c.save()
				os.remove(newName)
				c.configFileName = oldName
		
if __name__ == "__main__":
	print Olympus.lib()
