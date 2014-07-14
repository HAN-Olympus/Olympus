"""
@name Module
@author Stephan Heijl
@module core
@version 0.0.3

It is important for every Python file in your plugin to include a notation like the one above. 
This allows ModuleSeparator to distuingish your module from the others and wrap it up nicely for download.
Version can be any number, but Semantic version is preferred. This allows ModuleLoader to update separate
files if needed without user intervention.
"""

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
	def specifyControls():
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
	def specifyInput():
		""" This method should return a dictionary of classes of the type that should be inserted. 
		For example, if a module requires two inputs of any type, use:
		
		    collection = Collection()
		    
		    input = {
		    	"inputOne":[collection],
		    	"inputTwo":[collection]
		    }
		"""		
		pass
	
	@abstractmethod
	def specifyOutput():
		""" This method should return a dictionary of classes of the type that should be inserted. 
		For example, if a module outputs data in several formats, use:
		
		    html = StringContainer("HTML")
		    latex = StringContainer("LaTeX")
		    csv = StringContainer("CSV")
		    
		    output = {
		    	"HTML": [html],
		    	"LaTeX": [latex],
		    	"CSV": [csv]
		    }
		"""		
		pass
	
	@abstractmethod
	def start(self):
		""" Abstract method to start off functionality of the module as specified by `specifyInput()`."""
		pass
		