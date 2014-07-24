"""
@name ToolInstaller
@author Stephan Heijl
@module core
@version 0.0.3

This module installs a tool when it has been downloaded. It will appear in the root folder of the downloaded zip.
"""

class ToolInstaller():
	def __init__(self):
		try:
			import pip
		except ImportError:
			raise Exception, "Python 'pip' is required for this installer to work."
	