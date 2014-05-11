""" Interface base class.

Abstract class that provides base classes and access to classes in the ../lib directory
Uses part of the additionalImport script to allow access to the lib classes.
This type of module allows for "interfacing", that is, making the connection between the generated data and humans, through a unified format.
Refer to the page on Interface modules for a list of modules distributed with this version of Olympus.
"""
# Add the ../lib directory to the system path
import os, sys
currentDir = os.path.dirname(__file__)
relLibDir = currentDir + "/../../lib"
absLibDir = os.path.abspath(relLibDir)
sys.path.insert(0, absLibDir)

# Library classes are now accessible
import Module
from Config import Config
from jinja2 import Environment, FileSystemLoader
from TemplateTools import TemplateTools


class InterfaceModule(Module.Module):
	""" Base class for all interface modules. Provides some generic methods. """
	
	def __init__(self):
		""" Does nothing. """
		pass
		
	def getJinjaEnvironment(self, templates=None):
		""" Allows a module to make use of a Jinja2 environment for template rendering. 
			
			:param templates: The relative directory where the templates are situated in. Will default to the webapp's templates directory, if it is defined.
			:rtype: A Jinja2 Environment object.
		"""
		
		if templates == None:
			try:
				templates = Config().TemplatesDirectory
			except:
				templates = ""
		
		print "Templates: ", templates
		env = Environment(loader=FileSystemLoader(templates))
		return env
	
	def loadTemplateTools(self, env):
		tools = TemplateTools()
		for attribute in dir(tools):
			if not attribute.startswith("__") and hasattr(getattr(tools, attribute), "__call__"):
				print attribute
				env.globals[attribute] = getattr(tools, attribute)
		
		return env