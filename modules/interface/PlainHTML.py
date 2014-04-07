import InterfaceModule
from html import HTML

class PlainHTML(InterfaceModule.InterfaceModule):
	""" This module generates a plain HTML document.
	It contains no styling by default and will try to generate all the Visualizations as HTML, listing them sequentially.
	"""

	def __init__(self):
		contents = HTML()
		self.html = contents.html
		head = self.html.head
		head.title("PlainHTML Generated Page")
		self.body = self.html.body
		
	def appendToBody(self, html):
		self.body.text(html, escape=False)
		
	def addVisualizations(self, visualizations):
		for v in visualizations:
			vContainer = self.body.div(klass="visualization")
			vContainer.text(v.toHTML(), escape=False)

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
	

