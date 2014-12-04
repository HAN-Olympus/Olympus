"""
@name File
@author Stephan Heijl
@module core
@version 0.1.0
"""

from Olympus.lib.Control import Control

class File(Control):
	""" Contains the contents of an uploaded file. """
	def setValue(self, v):
		self.value = unicode(v)

	def toHTML(self):
		value = self.value if self.value != None else ""
		
		name = self.name
		if self.name == None:
			name = "undefined"
		
		input = self.html.input(klass="form-control file-control", 
								type="file",
								escape=False,
								name=name,
								id="control-"+name)
		return input
