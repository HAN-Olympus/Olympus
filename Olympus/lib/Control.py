"""
@name Control
@author Stephan Heijl
@module core
@version 0.1.0
"""

from abc import ABCMeta, abstractmethod
from html import XHTML

class Control(object):
	""" The abstract base class for all controls """
	__metaclass__ = ABCMeta

	def __init__(self, name=None, value=None, **kwargs):
		self.name = name
		self.value = value
		self.html = XHTML()
		self.attributes = {}
		self.data = {}
		self.allowedAttributes = None
		self.label = ""
		
		for k,v in kwargs.items():
			setattr(self, k, v)
		
		self.__disabledAttributes = ["value","name"]
		pass

	def checkDisabled(self):
		""" Returns whether or not this control is disabled. """
		if "disabled" in self.attributes.keys():
			return self.attributes["disabled"]
		return False

	def setValue(self, v):
		""" Sets the control value. Does not allow the disabled attribute to be bypassed.

		:param v: Sets the control value.
		:rtype: Whether or not the value was succesfully set.
		"""
		if not self.checkDisabled():
			self.value = v
			return True
		return False

	def getValue(self):
		""" Returns the current control value.

		:rtype: The control value.
		"""
		return self.value

	def setAttribute(self, key, value):
		""" Sets a control attribute. If Control.allowedAttributes is not None, it will only accept the attributes listed there.
		Will never accept attributes listed in Control.__disabledAttributes.

		:param key: The name of the attribute.
		:param value: The value of the attribute.
		:rtype: Whether or not the attribute was succesfully set.
		"""

		if (self.allowedAttributes == None or key in self.allowedAttributes) and key not in self.__disabledAttributes:
			self.attributes[key] = value
			return True
		return False

	def getAttribute(self, key):
		""" Attempts to retrieve an attribute of the control.

		:param key: The key of the attribute.
		:rtype: Either the value of the attribute or None if it was not set.
		"""
		try: # It's easier to ask for forgiveness...
			return self.attributes[key]
		except: # Than it is to get permission.
			return None
		# Also apparently better for performance.

	def setName(self, n):
		self.name = n

	def wrapHTML(self):
		""" Wraps the HTML control in a control wrapper."""
		control = self.html.div(klass="control-wrapper")
		control.text(self.toHTML(), escape=False)
		return str(control)
	
	@classmethod
	def toHTML(self):
		""" Representing the control as an HTML element. Take care to only define generic classes,
		preferably in line with the standing conventions.
		No inline styles or other properties should be added here.
		Javascript etc. will be accepted, but is not recommended.
		It is recommended that you use the `html` module wherever possible, to avoid mismatched tags, among others. An instance is provided by default: `self.html`. """


# TESTING #

class TestControl(Control):
	pass

def test_setgetAttribute():
	tc = TestControl()
	tc.setAttribute("key","value")
	assert tc.getAttribute("key") == "value"

	tc.allowedAttributes = ["attrOne"]
	assert tc.setAttribute("attrOne","test")
	assert not tc.setAttribute("attrTwo","test")

def test_checkDisabled():
	tc = TestControl()
	assert not tc.checkDisabled()
	tc.setAttribute("disabled",True)
	assert tc.checkDisabled()

def test_setgetValue():
	tc = TestControl()
	assert tc.setValue("TestOne")
	assert tc.getValue() == "TestOne"
	tc.setAttribute("disabled",True)
	assert not tc.setValue("TestTwo")
	assert tc.getValue() == "TestOne"
