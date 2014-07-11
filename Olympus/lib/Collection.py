"""
@name Collection
@author Stephan Heijl
@module core
@version 0.0.3
"""

class Collection(object):
	""" A basic collection of results items, can be restricted to a certain type. """
	
	def __init__(self, restrict = None):
		self.__contents = []
		self.restrict = restrict
		self.__pointer = 0 # The internal pointer
		
	def append(self, object):
		if self.restrict != None and not isinstance(object, self.restrict):
			raise ValueError, "This object can not be added to this restricted Collection."
				
		self.__contents.append(object)
		
	def remove(self, object):
		if self.__pointer >= self.__contents.index(object):
			self.__pointer -= 1
		self.__contents.remove(object)
		
	def __iter__(self):
		return self
	
	def rewind(self):
		self.__pointer = 0
	
	def seek(self, i):
		self.__pointer = i
		
	def get(self, i=None):
		if i == None:
			i = self.__pointer
			
		if i >= len(self.__contents) or i < 0:
			raise IndexError, "Out of range"
		
		return self.__contents[i]
	
	def next(self):
		if self.__pointer == len(self.__contents):
			raise StopIteration
		value = self.get()
		self.__pointer +=1
		return value
		
	def __len__(self):
		return len(self.__contents)
		
	def equalsType(self, other):
		if isinstance(other, Collection) and other.restrict == this.restrict:
			return True
		return False
		
# Testing #
from nose.tools import *

def test_getappend():
	c = Collection()
	c.append("Hello")
	assert c.get() == "Hello"

@raises(ValueError)
def test_restriction():
	c = Collection(str)
	c.append("Hello")
	c.append(1)
	assert c.get() == "Hello"

def test_remove():
	c = Collection()
	c.append("Hello")
	c.append(1)
	c.remove(1)
	assert len(c) == 1
	assert c.get() == "Hello" # Check if the internal pointer was retained
	c.append(2)
	c.append(3)
	c.seek(2)
	c.remove(2)
	assert c.get() == 3 # Check if the internal pointer was reduced
	
def test_rewind():
	c = Collection()
	c.append(10)
	c.append(20)
	c.append(4)
	for n in c:
		pass
	c.rewind()
	assert c.get() == 10
	
def test_seek():
	c = Collection()
	c.append(10)
	c.append(20)
	c.append(4)
	for n in c:
		pass
	c.seek(1)
	assert c.get() == 20

def test_iter():
	c = Collection(int)
	sum = 0
	c.append(10)
	c.append(20)
	c.append(4)
	
	for n in c:
		sum += n
	
	assert sum == 34
	
	