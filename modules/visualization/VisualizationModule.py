""" Visualization base class 
Abstract class that provides base classes and access to classes in the ../lib directory
Uses part of the additionalImport script to allow access to the lib classes.
Refer to the page on Visualization modules for a list of modules distributed with this version of Olympus.
"""
# Add the ../lib directory to the system path
import os, sys
currentDir = os.path.dirname(__file__)
relLibDir = currentDir + "/../../lib"
absLibDir = os.path.abspath(relLibDir)
sys.path.insert(0, absLibDir)

# Library classes are now accessible
import Module
import datetime

class VisualizationModule(Module.Module):
	""" Base class for all visualization modules. Provides some generic methods. """
	
	def __init__(self):
		pass
	
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
				
		html = [ "<table>", "<thead>","<tr>"]
		
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
		
		
# Testing #

from nose import tools as ntools
		
def test_convertDictionaryToHTMLTable():
	vm = VisualizationModule()
	d = { "Subject 1" : { "variable 1" : "value", "variable 2" : "value" },"Subject 2" : { "variable 1" : "value", "variable 2" : "value", "variable 3" : "value"} }
	print vm.convertDictionaryToHTMLTable(d)

@ntools.raises(KeyError)
def test_fail_convertDictionaryToHTMLTable():
	vm = VisualizationModule()
	d = { "Subject 1" : { "variable 1" : "value", "variable 2" : "value" },"Subject 2" : { "variable 1" : "value", "variable 2" : "value", "variable 3" : "value"} }
	print vm.convertDictionaryToHTMLTable(d, None)