import Table
import json

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
		html = [ "<style> @import url('/css/dataTables.bootstrap.css');</style>" ]
		html += [ "<table class='table' id='fancytable'>", "<thead>","<tr>"]
		
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
						html.append("<td>%s</td>" % self.formatValue(variables[key]) )
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
					"{{ deferJS('http://cdn.datatables.net/1.10.0/js/jquery.dataTables.min.js',4) }}",
					"{{ deferJS('http://cdn.datatables.net/plug-ins/e9421181788/integration/bootstrap/3/dataTables.bootstrap.js',4 ) }}",
					"{{ deferInlineJS('$(document).ready(function() {{ $(\"#fancytable\").dataTable({{ \"sScrollX\": \"100%\", \"bScrollCollapse\": true}}); }} );',4) }}"
				]
		return "\n".join(html)
	
	def formatValue(self, value):
		""" Check if a value can be formatted better. Also checks if a value is formatted as JSON. """
		try:
			v = json.loads(value)
		except:
			v = value
		
		if isinstance(v, list):
			return "<ul>" + "".join(["<li>%s</li>" % self.formatValue(i) for i in v]) + "</ul>"
		
		if isinstance(v, dict):
			return "<dl>" + "".join(["<dt>%s</dt><dd>%s</dd>" % (ik, self.formatValue(iv)) for ik, iv in v.items()]) + "</dl>"
		
		if isinstance(value, str):
			return unicode(value, errors='ignore')
		return value
		
		
		
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
			table[unicode(input)] = {}
			for key in keys:
				if hasattr(input,key):
					table[unicode(input)][key] = getattr(input, key)
				else:
					table[unicode(input)][key] = None
				 
		for input in inputTwo:
			table[unicode(input)] = {}
			for key in keys:
				if hasattr(input,key):
					table[unicode(input)][key] = getattr(input, key)
				else:
					table[unicode(input)][key] = None
				 
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
	
def test_formatValue():
	table = FancyTable(None)
	assert table.formatValue("string") == "string"
	assert table.formatValue("1") == "1"
	assert table.formatValue('["string"]') == "<ul><li>string</li></ul>"
	assert table.formatValue('["string","string2"]') == "<ul><li>string</li><li>string2</li></ul>"
	assert table.formatValue('{"string":"string2"}') == "<dl><dt>string</dt><dd>string2</dd></dl>"
	
	assert table.formatValue(["string"]) == "<ul><li>string</li></ul>"
	assert table.formatValue(["string","string2"]) == "<ul><li>string</li><li>string2</li></ul>"
	assert table.formatValue({"string":"string2"}) == "<dl><dt>string</dt><dd>string2</dd></dl>"