import VisualizationModule
from Collection import Collection
from StringContainer import StringContainer
import json


class Table(VisualizationModule.VisualizationModule):
	""" This module has two operation modes.
	It either projects all the attributes of a single collection into a table or it converts two object collections into a table by presenting a Cartesian product of all the objects inside of them.
	It can also select which of the attributes to show.
	
	"""
	def __init__(self, collectionOne=None, collectionTwo = None, showOnly=[], showNoneOf=[] ):
		""" Initializes table conversion.
		
		:param collectionOne: A collection to convert into a table.
		:param collectionTwo: Optional. If this argument is given (not None) the secondary operation mode; It converts two object collections into a table by presenting a Cartesian product of all the objects inside of them.
		:param showOnly: A list of attributes that should ONLY be shown. This option will be selected by default if both `showOnly` and `showNoneOf` are defined, as they are mutually exclusive.
		:param showNoneOf: A list of attributes that will NOT be shown. This option will be overridden by showOnly if both are defined.
		"""		
		
	def toString(self):
		return self.__class__.__name__
		
	
	def convertDictionaryToHTMLTable(self, dictionary, empty="n/a"):
		"""Convert a two dimensional dictionary formatted like so: ::
		
		    {
		      "Subject 1" : { "variable 1" : "value", "variable 2" : "value" ... },
		      "Subject 2" : { "variable 1" : "value", "variable 2" : "value" ... },
		      ...
		    }
			
		Into an HTML table. If keys are do not exist in every dictionary, they will be filled with the `empty` value.
		
		:param dictionary: The dictionary to be formatted
		:param empty: The filler for cells in rows where a key has been ommitted. Use `None` to throw an exception when this occurs.
		:rtype: The dictionary formatted as a table
		"""
				
		html = [ "<table class='table'>", "<thead>","<tr>"]
		
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
					html.append("<td>%s</td>" % variables[key])
				else:
					if empty == None:
						raise KeyError, "Mismatch between the dictionaries' keys. (%s)" % key
					else:
						html.append("<td>%s</td>" % empty)
			html+= ["</tr>"]
					
		
		
		html += [ "</tbody>", "</table>"]
		return "\n".join(html)
		
	def specifyInput(self):
		collection = Collection()
				
		input = {
			"inputOne":[collection],
			"inputTwo":[collection]
		}
		return input
		
	def specifyOutput(self):
		html = StringContainer("HTML")
		latex = StringContainer("LaTeX")
		csv = StringContainer("CSV")
		
		output = {
			"HTML": [html],
			"LaTeX": [latex],
			"CSV": [csv]
		}
		return output
		
	def determineKeyIntersect(self, inputOne, inputTwo):
		""" Determines the intersection of the keys in two (lists of) objects and returns them. """
		xAxis = set()
		xValues = {}
		
		yAxis = set()
		yValues = {}
		
		for input in inputOne:
			for key,value in input.__dict__.items():
				xAxis.add(key)
				if key in xValues:
					xValues[key].append(value)
				else:
					xValues[key] = [value]
		
		for input in inputTwo:
			for key,value in input.__dict__.items():
				yAxis.add(key)
				if key in yValues:
					yValues[key].append(value)
				else:
					yValues[key] = [value]
					
		return xAxis.intersection(yAxis)
		
	def toHTML(self):
		inputOne = self.inputOne
		inputTwo = self.inputTwo
		
		if not isinstance(inputOne, list):
			inputOne = [inputOne]
		if not isinstance(inputTwo, list):
			inputTwo = [inputTwo]
		
		keys = self.determineKeyIntersect(inputOne, inputTwo)

		table = {}
		for input in inputOne:
			table[str(input)] = {}
			for key in keys:
				 table[str(input)][key] = getattr(input, key)
				 
		for input in inputTwo:
			table[str(input)] = {}
			for key in keys:
				 table[str(input)][key] = getattr(input, key)
				 
		return self.convertDictionaryToHTMLTable(table)	
		
	def start(self, inputOne, inputTwo):
		self.inputOne = inputOne
		self.inputTwo = inputTwo
		
		return self
		
# Testing #

from nose import tools as ntools
		
def test_convertDictionaryToHTMLTable():
	table = Table(None)
	d = { "Subject 1" : { "variable 1" : "value", "variable 2" : "value" },"Subject 2" : { "variable 1" : "value", "variable 2" : "value", "variable 3" : "value"} }
	print table.convertDictionaryToHTMLTable(d)

@ntools.raises(KeyError)
def test_fail_convertDictionaryToHTMLTable():
	table = Table(None)
	d = { "Subject 1" : { "variable 1" : "value", "variable 2" : "value" },"Subject 2" : { "variable 1" : "value", "variable 2" : "value", "variable 3" : "value"} }
	print table.convertDictionaryToHTMLTable(d, None)
	