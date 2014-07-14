"""
@name Text
@author Stephan Heijl
@module core
@version 0.0.3
"""

from Olympus.lib.Control import Control

class Text(Control):
	""" Plain text input control. """
	def setValue(self, v):
		self.value = unicode(v)

	def toHTML(self):
		value = self.value if self.value != None else ""
		
		name = self.name
		if self.name == None:
			name = "undefined"
		
		input = self.html.input(klass="form-control text-control", 
								type="text",
								value=unicode(value),
								escape=False,
								name=name,
								id="control-"+name)
		return input

# TESTING #

def test_controlText():
	ct = Text()
	print(ct.wrapHTML())
