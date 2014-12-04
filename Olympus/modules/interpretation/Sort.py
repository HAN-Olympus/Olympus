import InterpretationModule
from Olympus.lib.Module import Module
from Olympus.lib.Collection import Collection

class Sort(InterpretationModule.InterpretationModule):
	""" This module sorts a collection on a given attribute."""
	
	def __init__(self):
		# TODO: Configuration 
		pass
	
	def specifyControls(self):
		pass
		
	def specifyInput(self):
		collection = Collection()
				
		input = {
			"input":[collection]
		}
		return input
		
	def specifyOutput(self):
		collection = Collection()
				
		output = {
			"result":[collection]
		}
		return output
		
	def start(self, input):
		return input
