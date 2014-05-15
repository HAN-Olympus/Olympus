import InterpretationModule
from Olympus.lib.Log import Log
from Olympus.lib.StringContainer import StringContainer

class Tail(InterpretationModule.InterpretationModule):
	""" This module sorts only shows the latest 50 lines of a Log."""
	
	def __init__(self):
		# TODO: Configuration 
		pass
		
	def specifyInput(self):
		log = Log()
				
		input = {
			"input":[log]
		}
		return input
		
	def specifyOutput(self):
		plainText = StringContainer("plain")
				
		output = {
			"result":[plainText]
		}
		return output
		
	def start(self, **kwargs):
		pass
