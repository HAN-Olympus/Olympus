"""
@name Core
@author Stephan Heijl
@module core
@version 0.0.3
"""

# Olympus Core
from Olympus.lib.Config import Config
import os

class Core:
	""" The Olympus Core. This performs any and all backend tasks. 
		When a worker is launched, it will use Core to execute the actual tasks after setting the initial state.
	"""
	
	def getRootDirectory(self):
		pass
	
	def getVersion(self):
		""" Retrieves and returns the version of this Olympus instance. """
		with open(os.path.join( Config().RootDirectory, "core/VERSION" ) ) as v:
			return v.read()
		