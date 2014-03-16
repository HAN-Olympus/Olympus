# Olympus StoredObject Class
# This is a stored object, the base form of an object that can be stored in our database

from abc import ABCMeta, abstractmethod

class StoredObject():
	__metaclass__ = ABCMeta
		
	def __init__(self):
		pass