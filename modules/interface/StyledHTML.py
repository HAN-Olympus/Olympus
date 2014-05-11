import PlainHTML
from flask import Flask, render_template

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
				

# TESTING #
	
