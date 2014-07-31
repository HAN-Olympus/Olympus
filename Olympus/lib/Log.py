"""
@name Log
@author Stephan Heijl
@module core
@version 0.2.0
"""

class Log(object):
	def __init__(self):
		self.contents = []
		self.__pointer = 0
		
	def open(self, name="default", mode="w"):
		pass

	def read(self):
		return self.contents[self.__pointer:]
		
	def seek(self, n):
		self.__pointer = n
		
	def write(self, item):
		self.contents.append(item)