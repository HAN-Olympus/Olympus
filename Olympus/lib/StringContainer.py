"""
@name StringContainer
@author Stephan Heijl
@module core
@version 0.2.0
"""

class StringContainer(object):
	def __init__(self, restrict = None):
		self.__contents = ""
		self.restrict = restrict
		
		
	