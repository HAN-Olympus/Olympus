import InterfaceModule
from StringContainer import StringContainer
from html import HTML

class PlainHTML(InterfaceModule.InterfaceModule):
	""" This module generates a plain HTML document.
	It contains no styling by default and can be used to sequentially generate visualizations as HTML.
	"""

	def __init__(self, title="PlainHTML Generated Page"):
		""" Initializes a base HTML document with the html library.
		
		:param title: The title of the document under construction.
		"""
		contents = HTML()
		self.html = contents.html
		head = self.html.head
		head.title(title)
		self.body = self.html.body
		
	def appendToBody(self, html):
		""" Appends a piece of HTML to the body. 
		
		:param html: The HTML to append to the body element of the document that is currently being constructed.
		"""
		self.body.text(html, escape=False)
		
	def addVisualizations(self, visualizations):
		""" Takes a collection of visualizations and attempts to add them to the document as HTML.
		If the visualization does not have a proper toHTML() function the one in the VisualizationModule superclass will be used.
		
		:param visualizations: A collection of visualizations to be added to the body.
		"""
		for v in visualizations:
			vContainer = self.body.div(klass="visualization")
			vContainer.text(v.toHTML(), escape=False)
			
	def specifyInput(self):
		html = StringContainer("HTML")
				
		input = {
			"input":[html]
		}
		return input
		
	def specifyOutput(self):
		pass
		
	def start(self, input):
		if isinstance(input, list):
			self.addVisualizations(input)
		else:
			self.addVisualizations([input])
		
		return str(self.html)

# TESTING #
import difflib
		
def test_init():
	ph = PlainHTML()
	testString = "<html><head><title>PlainHTML Generated Page</title></head><body></html>"	
	assert str(ph.html) == testString
	
def test_appendToBody():
	ph = PlainHTML()
	appendText = "Hello world <br/>"
	testString = "<html><head><title>PlainHTML Generated Page</title></head><body>%s</body></html>" % appendText
	ph.appendToBody(appendText)
	assert str(ph.html) == testString
	
