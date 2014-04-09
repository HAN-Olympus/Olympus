import VisualizationModule
import json


class Table(VisualizationModule.VisualizationModule):
	""" This module has two operation modes.
	It either projects all the attributes of a single collection into a table or it converts two object collections into a table by presenting a Cartesian product of all the objects inside of them.
	It can also select which of the attributes to show.
	
	"""
	def __init__(self, collectionOne, collectionTwo = None, showOnly=[], showNoneOf=[] ):
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
			for key in keys:
				if key in variables.keys():
					html.append("<td>%s</td>" % variables[key])
				else:
					if empty == None:
						raise KeyError, "Mismatch between the dictionaries' keys. (%s)" % key
					else:
						html.append("<td>%s</td>" % empty)
					
		
		
		html += [ "</tbody>", "</table>"]
		return "\n".join(html)
		
	def specifyInput(self):
		pass
		
	def specifyOutput(self):
		pass
		
	def start(self, **kwargs):
		pass
		
		
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
	