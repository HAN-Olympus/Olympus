from Olympus.lib.Control import Control

class Text(Control):
	""" Plain text input control. """
	def setValue(self, v):
		self.value = unicode(v)

	def toHTML(self):
		value = self.value if self.value != None else ""
		input = self.html.input(klass="text-control", type="text", value=unicode(value), escape=False)
		return input

# TESTING #

def test_controlText():
	ct = Text()
	print(ct.wrapHTML())
