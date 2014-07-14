"""
@name Integer
@author Stephan Heijl
@module core
@version 0.0.3
"""

from Olympus.lib.Control import Control

class Integer(Control):
	""" Integer input control. """
	def setValue(self,v):
		self.value = int(v)
	
	def toHTML(self):
		value = self.value if self.value != None else ""
		
		name = self.name
		if self.name == None:
			name = "undefined"
		
		input = self.html.input(klass="form-control int-control", 
								type="number",
								value=str(value),
								escape=False,
								name=name,
								step=str(1),
								id="control-"+name)
		return input

# TESTING #

def test_controlInteger():
	ci = Integer()
	print(ci.wrapHTML())
