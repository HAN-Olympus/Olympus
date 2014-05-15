import InterfaceModule
from Olympus.lib.StringContainer import StringContainer

class LaTeX(InterfaceModule.InterfaceModule):
	""" This module generates a LaTeX document.	"""

	def __init__(self, title="Olympus Generated Page"):
		""" Initializes a base LaTeX document.
		
		:param title: The title of the document under construction.
		"""
		contents = ""
			
	def specifyInput(self):
		latex = StringContainer("LaTeX")
				
		input = {
			"input":[latex]
		}
		return input
		
	def specifyOutput(self):
		pass
		
	def start(self, **kwargs):
		pass
	
