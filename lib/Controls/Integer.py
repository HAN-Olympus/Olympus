from Olympus.lib.Control import Control

class Integer(Control):
	""" Integer input control. """
	def setValue(self,v):
		self.value = int(v)

	def toHTML(self):
		value = self.value if self.value != None else ""
		input = self.html.input(klass="int-control", type="number", step="1", value=str(value), escape=False)
		return input

# TESTING #

def test_controlInteger():
	ci = Integer()
	print(ci.wrapHTML())
