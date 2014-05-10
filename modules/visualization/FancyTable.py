import Table

class FancyTable(Table.Table):
	""" This module is a fancier, jQuery enhanced version of the normal table. 
		FancyTable will only differ in output if HTML is requested, other operations are performed in the same way as the Table Module.
		It should be noted that, in addition to adding extra styles to the table, it will also include Jinja2 templating code to achieve better integration with StyledHTML. 
		You should therefore not use this with any interface module that will render this as HTML without processing it as a template.
	"""		
	
	def convertDictionaryToHTMLTable(self, dictionary, empty="n/a"):
		"""Convert a two dimensional dictionary formatted like so: ::
		
		    {
		      "Subject 1" : { "variable 1" : "value", "variable 2" : "value" ... },
		      "Subject 2" : { "variable 1" : "value", "variable 2" : "value" ... },
		      ...
		    }
			
		Into an HTML table. If keys are do not exist in every dictionary, they will be filled with the `empty` value.
		This method will supplement the table with the necessary classes and properties to style them and allow interaction.
		
		:param dictionary: The dictionary to be formatted
		:param empty: The filler for cells in rows where a key has been ommitted. Use `None` to throw an exception when this occurs.
		:rtype: The dictionary formatted as a table
		"""
				
		html = [ "<style> @import url('http://cdn.datatables.net/plug-ins/e9421181788/integration/bootstrap/3/dataTables.bootstrap.css'); </style>", "<table class='table' id='fancytable'>", "<thead>","<tr>"]
		
		keys = []
		for subject, variables in dictionary.items():
			keys+=variables.keys()
		
		keys = list(set(keys))
		keys.sort()
		
		for key in keys:
			html.append("<td>%s</td>" % key)
		
		html+= ["</tr>", "</thead>", "<tbody>"]
		for subject, variables in dictionary.items():
			html+= ["<tr>"]
			for key in keys:
				if key in variables.keys():
					if variables[key] != None:
						html.append("<td>%s</td>" % variables[key])
					else:
						html.append("<td>%s</td>" % empty)
				else:
					if empty == None:
						raise KeyError, "Mismatch between the dictionaries' keys. (%s)" % key
					else:
						html.append("<td>%s</td>" % empty)
			html+= ["</tr>"]
		
		html += [ "</tbody>", "</table>"]
		
		# Javascript required for dataTables
		html += [	
					"<script src='https://code.jquery.com/jquery-1.10.2.min.js'></script>",
					"<script src='http://cdn.datatables.net/1.10.0/js/jquery.dataTables.min.js'></script>",
					"<script src='http://cdn.datatables.net/plug-ins/e9421181788/integration/bootstrap/3/dataTables.bootstrap.js'></script>",
					"<script>$(document).ready(function() { $('#fancytable').dataTable();} );</script>"
				]
		return "\n".join(html)		
		
	def toHTML(self):
		inputOne = self.inputOne
		inputTwo = self.inputTwo
		
		if not isinstance(inputOne, list):
			inputOne = [inputOne]
		if not isinstance(inputTwo, list):
			inputTwo = [inputTwo]
		
		#keys = self.determineKeyIntersect(inputOne, inputTwo)
		keys = self.getCumulativeKeys(inputOne, inputTwo)

		table = {}
		for input in inputOne:
			table[str(input)] = {}
			for key in keys:
				if hasattr(input,key):
					table[str(input)][key] = getattr(input, key)
				else:
					table[str(input)][key] = None
				 
		for input in inputTwo:
			table[str(input)] = {}
			for key in keys:
				if hasattr(input,key):
					table[str(input)][key] = getattr(input, key)
				else:
					table[str(input)][key] = None
				 
		return self.convertDictionaryToHTMLTable(table)
		
# TESTING #

from nose import tools as ntools
		
def test_convertDictionaryToHTMLTable():
	table = FancyTable(None)
	d = { "Subject 1" : { "variable 1" : "value", "variable 2" : "value" },"Subject 2" : { "variable 1" : "value", "variable 2" : "value", "variable 3" : "value"} }
	print table.convertDictionaryToHTMLTable(d)

@ntools.raises(KeyError)
def test_fail_convertDictionaryToHTMLTable():
	table = FancyTable(None)
	d = { "Subject 1" : { "variable 1" : "value", "variable 2" : "value" },"Subject 2" : { "variable 1" : "value", "variable 2" : "value", "variable 3" : "value"} }
	print table.convertDictionaryToHTMLTable(d, None)
	