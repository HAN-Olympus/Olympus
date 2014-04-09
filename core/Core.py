"""Core"""

# Olympus Core
import additionalImports
import Config

class Core:
	""" The Olympus Core. This performs any and all backend tasks. 
		When a worker is launched, it will use Core to execute the actual tasks after setting the initial state.
	"""
	
	