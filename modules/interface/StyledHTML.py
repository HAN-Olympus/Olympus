import PlainHTML
from Config import Config
import os

class StyledHTML(PlainHTML.PlainHTML):
	""" This module generates an HTML document with styling. It renders the results in a more visually appealing environment
		at the cost of purity of data. As it inherits from PlainHTML it can be used in the same way.
		
		While default styling will be applied to most elements, very plain HTML generated elements will still look that way.
		Try looking for "fancy" versions of modules to receive results with better styling and/or interactivity.
		It uses Flask's/Jinja2's rendering engine to produce the HTML.
		
	"""

	def __init__(self, title="Olympus StyledHTML Generated Page"):
		""" Initializes a base HTML document with the html library.
		
		:param title: The title of the document under construction.
		"""
		
		self.html = ""
		self.visualizations = []
		
	def addVisualizations(self, visualizations):
		""" Takes a collection of visualizations and attempts to add them to the document as HTML.
		If the visualization does not have a proper toHTML() function the one in the VisualizationModule superclass will be used.
		
		:param visualizations: A collection of visualizations to be added to the body.
		"""
		for v in visualizations:
			self.visualizations.append( v.toHTML() )
		
	def appendToBody(self, html):
		""" Appends a piece of HTML to the body. 
		
		:param html: The HTML to append to the body element of the document that is currently being constructed.
		"""
		self.visualizations.append(html)
		
	def start(self, input):
		if isinstance(input, list):
			self.addVisualizations(input)
		else:
			self.addVisualizations([input])
		
		env = self.getJinjaEnvironment()
		env = self.loadTemplateTools(env)
		
		template = env.get_template("StyledHTML.html")
		return template.render(visualizations=self.visualizations, id="Job")

# TESTING #
	
