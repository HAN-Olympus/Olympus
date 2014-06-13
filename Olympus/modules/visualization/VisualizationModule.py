""" Visualization base class.

Abstract class that provides base classes and access to classes in the ../lib directory
Uses part of the additionalImport script to allow access to the lib classes.
Refer to the page on Visualization modules for a list of modules distributed with this version of Olympus.
"""
from Olympus.lib.Module import Module
import datetime
from abc import ABCMeta, abstractmethod

class VisualizationModule(Module):
	""" Abstract base class for all visualization modules. Provides some generic methods. """
	__metaclass__ = ABCMeta
	
	def __init__(self):
		pass
		
	def toXML(self):
		""" Default XML conversion. This will display if the Visualization Module does not have a toXML function. """
		return "<VisualizationModule> <%s> <title> '%s' cannot be represented as XML. </title> </%s> </VisualizationModule>" % (self.__class__.__name__, self.__class__.__name__, self.__class__.__name__)
	
	def toLatex(self):
		""" Default LaTeX conversion. This will display if the Visualization Module does not have a toLatex function. """
		return "{\tt '%s'} cannot be represented as LaTeX." % (self.__class__.__name__)
	
	def toHTML(self):
		""" Default HTML conversion. This will display if the Visualization Module does not have a toHTML function. """
		return "<p> '%s' cannot be represented as HTML. </p>" % (self.__class__.__name__)
		
	@abstractmethod
	def toString(self):
		pass
		
# TESTING #

class TestModule(VisualizationModule):
	def toString(self):
		return "test"
	
	def specifyControls(self):
		pass
		
	def specifyInput(self):
		pass
		
	def specifyOutput(self):
		pass
		
	def start(self, **kwargs):
		pass
	
def test_toXML():
	tm = TestModule()
	testString = "<VisualizationModule> <TestModule> <title> 'TestModule' cannot be represented as XML. </title> </TestModule> </VisualizationModule>"
	assert tm.toXML() == testString
	
def test_toLatex():
	tm = TestModule()
	testString = "{\tt 'TestModule'} cannot be represented as LaTeX."
	assert tm.toLatex() == testString
	
def test_toHTML():
	tm = TestModule()
	testString = "<p> 'TestModule' cannot be represented as HTML. </p>"
	assert tm.toHTML() == testString
	