from abc import ABCMeta, abstractmethod
from html import HTML

class Control(object):
	""" The abstract base class for all controls """	
	__metaclass__ = ABCMeta
	
	def __init__(self):
		self.name = None
		self.value = None
		self.html = HTML()
		pass
		
	def setValue(self, v):
		self.value = v
	
	def setName(self, n):
		self.name = n
	
	def wrapHTML(self):
		""" Wraps the HTML control in a control wrapper."""
		control = self.html.div(klass="control-wrapper")
		control.text(self.toHTML(), escape=False)
		return str(control)
	
	def toHTML(self):
		""" Representing the control as an HTML element. Take care to only define generic classes,
		preferably in line with the standing conventions. 
		No inline styles or other properties should be added here.
		Javascript etc. will be accepted, but is not recommended. 
		It is recommended that you use the `html` module wherever possible, to avoid mismatched tags, among others. An instance is provided by default: `self.html`. """
		return "This control cannot be represented as HTML"

# TESTING #

# Controls subclasses #
		
		
class Control_Text(Control):
	""" Plain text input control. """
	def setValue(self, v):
		self.value = unicode(v)
		
	def toHTML(self):
		value = self.value if self.value != None else ""
		input = self.html.input(klass="text-control", type="text", value=unicode(value), escape=False)
		return input

# TESTING #
		
def test_controlText():
	ct = Control_Text()
	print(ct.wrapHTML())
		
class Control_Number(Control):
	""" Float input control. HTML defaults to 0.1 steps. """
	def setValue(self, v):
		self.value = float(v)
		
	def toHTML(self):
		value = self.value if self.value != None else ""
		input = self.html.input(klass="number-control", type="number", step="0.1", value=str(value), escape=False)
		return input

# TESTING #

def test_controlNumber():
	cn = Control_Number()
	print(cn.wrapHTML())
		
class Control_Integer(Control):
	""" Integer input control. """
	def setValue(self,v):
		self.value = int(v)
		
	def toHTML(self):
		value = self.value if self.value != None else ""
		input = self.html.input(klass="int-control", type="number", step="1", value=str(value), escape=False)
		return input	

# TESTING #

def test_controlInteger():
	ci = Control_Integer()
	print(ci.wrapHTML())