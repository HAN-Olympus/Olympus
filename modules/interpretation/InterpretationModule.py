""" Interpretation base class.

Abstract class that provides base classes and access to classes in the ../lib directory
Uses part of the additionalImport script to allow access to the lib classes.
Refer to the page on Interpretation modules for a list of modules distributed with this version of Olympus.
"""

from Olympus.lib.Module import Module
import datetime

class InterpretationModule(Module):
	""" Base class for all interpretation modules. Provides some generic methods. """
	
	def __init__(self):
		""" Does nothing. """
		pass
