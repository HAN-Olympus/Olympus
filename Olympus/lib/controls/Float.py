"""
@name Float
@author Stephan Heijl
@module core
@version 0.2.0
"""

from Olympus.lib.Control import Control

class Float(Control):
	""" Float input control. HTML defaults to 0.1 steps. """
	def setValue(self, v):
		self.value = float(v)

	def toHTML(self):
		value = self.value if self.value != None else ""
		input = self.html.input(klass="number-control", type="number", step="0.1", value=str(value), escape=False)
		return input

# TESTING #

def test_controlFloat():
	cf = Float()
	print(cf.wrapHTML())
