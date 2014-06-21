from Olympus.lib.Control import Control

class Select(Control):
	""" A select item """
	
	def __init__(self, **kwargs):
		self.options = {}
		super(Select, self).__init__(**kwargs)
	
	def setValue(self, v):
		self.value = unicode(v)
		
	def addOption(self, key, value):
		self.options[key] = value

	def toHTML(self):
		value = self.value if self.value != None else ""
		
		name = self.name
		if self.name == None:
			name = "undefined"
		
		select = self.html.select(klass="form-control select-control", 
								escape=False,
								name=name,
								id="control-"+name)
		
		for key, value in self.options.items():
			select.option(value, value="key")
		
		return select

# TESTING #

def test_controlText():
	ct = Select()
	print(ct)