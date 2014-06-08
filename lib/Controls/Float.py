from Olympus.lib.Control import Control

class Number(Control):
	""" Float input control. HTML defaults to 0.1 steps. """
	def setValue(self, v):
		self.value = float(v)

	def toHTML(self):
		value = self.value if self.value != None else ""
		input = self.html.input(klass="number-control", type="number", step="0.1", value=str(value), escape=False)
		return input

# TESTING #

def test_controlNumber():
	cn = Number()
	print(cn.wrapHTML())
