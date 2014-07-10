"""
@name ModuleSeparator
@author Stephan Heijl
@module core
@version 0.0.3
"""

from Olympus.lib.Config import Config
import os, importlib, random

class ModuleSeparator(object):
	"""  """
	def __init__(self):
		self.packages = []
		self.files = {}
		
	def scanAll(self):
		for root, dirs, files in os.walk(Config().RootDirectory):
			self.scanFolder(root)
	
	def scanFolder(self,name):
		for root, dirs, files in os.walk( os.path.join( Config().RootDirectory, name )):
			for file in files:
				if file.endswith(".py"):
					module = self.importFile(os.path.join(root, file))
					doc = module.__doc__
					if doc != None:
						self.parseDocString(doc)
					
	def convertPathToImport(self, path):
		normalPath = "Olympus." + path.replace(Config().RootDirectory, "").strip(os.path.sep).replace(os.path.sep, ".")
		if normalPath.endswith(".py"):
			normalPath = normalPath[:-3]
		return normalPath
	
	def importFile(self, name):
		modulePath = self.convertPathToImport(name)
		try:
			module = importlib.import_module(modulePath)
		except ImportError:
			return False
		
		return module		
	
	def parseDocString(self,docstring):
		for line in docstring.split("\n"):
			if line.startswith("@"):
				key = line.split(" ")[0]
				value = " ".join( line.split(" ")[1:] )
	
	def package(self, files):
		pass

# TESTING #

def test_importFile():
	ms = ModuleSeparator()
	corePath = os.path.join(Config().RootDirectory, "core","Core.py")
	assert "module" in str(type( ms.importFile(corePath) ))
	# This path should never exist lest this test should fail.
	# I reckon approximately 90 million bits of entropy ought to be sufficient
	nonExistantPath = os.path.join(Config().RootDirectory, str(random.randrange(10000000,99999999)),str(random.randrange(10000000,99999999)))
	assert not ms.importFile(nonExistantPath)

def test_scanFolder():
	ms = ModuleSeparator()
	ms.scanFolder("Olympus")
	
def test_scanAll():
	ms = ModuleSeparator()
	ms.scanAll()
	
def test_convertPathToImport():
	ms = ModuleSeparator()
	testPathsTuples = [["test","one"],["test","two","three"],["test","test.py"]]
	testPaths = [os.path.join(Config().RootDirectory, p ) for p in  [os.path.join(*path) for path in testPathsTuples]]
	expected = ["Olympus.test.one","Olympus.test.two.three","Olympus.test.test"]
	for t in range(len(testPaths)):
		result = ms.convertPathToImport(testPaths[t])
		assert result == expected[t]
