import InterfaceModule
from Olympus.lib.StringContainer import StringContainer
from html import HTML

class PlainHTML(InterfaceModule.InterfaceModule):
	""" This module generates a plain HTML document.
	It contains no styling by default and can be used to sequentially generate visualizations as HTML.
	"""

	def __init__(self, title="PlainHTML Generated Page"):
		""" Initializes a base HTML document with the html library.
		
		:param title: The title of the document under construction.
		"""
		self.title = title
		
	def addVisualizations(self, body, visualizations):
		""" Takes a collection of visualizations and attempts to add them to the document as HTML.
		If the visualization does not have a proper toHTML() function the one in the VisualizationModule superclass will be used.
		
		:param visualizations: A collection of visualizations to be added to the body.
		"""
		for v in visualizations:
			vContainer = body.div(klass="visualization")
			vContainer.text(v.toHTML(), escape=False)
			
	def specifyControls(self):
		pass
			
	def specifyInput(self):
		html = StringContainer("HTML")
				
		input = {
			"input":[html]
		}
		return input
		
	def specifyOutput(self):
		pass
		
	def start(self, input):
		contents = HTML()
		html = contents.html
		head = html.head
		head.title(self.title)
		body = html.body
		
		if isinstance(input, list):
			self.addVisualizations(body, input)
		else:
			self.addVisualizations(body, [input])
		
		return str(html)

# TESTING #
import difflib
		
def test_init():
	ph = PlainHTML()
	testString = "<html><head><title>PlainHTML Generated Page</title></head><body></html>"
	result = ph.start([])
	print result
	assert result == testString
	
