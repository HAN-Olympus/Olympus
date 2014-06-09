""" The Olympus Module Class. """
# Olympus Module Class

from abc import ABCMeta, abstractmethod

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
		