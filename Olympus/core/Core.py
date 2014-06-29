"""Core"""

# Olympus Core
from Olympus.lib.Config import Config
import os

class Core:
	""" The Olympus Core. This performs any and all backend tasks. 
		When a worker is launched, it will use Core to execute the actual tasks after setting the initial state.
	"""
	
	def getVersion(self):
		with open(os.path.join( Config().RootDirectory, "core/VERSION" ) ) as v:
			return v.read()
		