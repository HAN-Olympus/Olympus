""" Interface base class 
Abstract class that provides base classes and access to classes in the ../lib directory
Uses part of the additionalImport script to allow access to the lib classes.
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
import datetime

class InterfaceModule(Module.Module):
	""" Base class for all interface modules. Provides some generic methods. """
	
	def __init__(self):
		""" Does nothing. """
		pass
