"""
@name ModuleSeparator
@author Stephan Heijl
@module core
@version 0.1.0
"""

from Olympus.lib.Config import Config
import os, importlib, random, pprint, sys
import tarfile, json

class ModuleSeparator(object):
	"""  Separates the current working version of Olympus into its constituent modules and allows developers to export them individually. """
	def __init__(self):
		self.modules = {}
		self.files = {}
		self.name = None
		
	def scanAll(self):
		""" Scans the entire root folder. """ 
		self.scanFolder(Config().RootDirectory)
	
	def scanFolder(self,name):
		""" Scans a directory recursively for Python files.
		
		:param name: The path of the folder.
		"""
		for root, dirs, files in os.walk( os.path.join( Config().RootDirectory, name )):
			for file in files:
				if file.endswith(".py"):
					path = os.path.join(root, file)
					module = self.importFile(path)
					doc = module.__doc__
					if doc != None:
						dc = self.parseDocString(doc)
						if dc != {}:
							self.addFile(path, dc)
						
						
	def addFile(self, path, dc):
		""" Adds a file to the index.
		
		:param path: The path of the file.
		:param dc: The parsed module docstring. 
		"""
		module = dc["module"]
		name = dc["name"]
		key = (module, dc["version"])
		if key not in self.files:
			self.modules[module] = dc
			self.files[key] = {}
		self.files[key][name] = path
						
					
	def convertPathToImport(self, path):
		""" Converts a path to a package location.
		
		:param path: A local system path.
		:rtype: A string representing the path as a package location
		"""
		normalPath = "Olympus." + path.replace(Config().RootDirectory, "").strip(os.path.sep).replace(os.path.sep, ".")
		if normalPath.endswith(".py"):
			normalPath = normalPath[:-3]
		return normalPath
	
	def importFile(self, name):
		""" Imports a file and returns the module object.
		
		:param name: The path of the file
		:rtype: A module object.
		"""
		modulePath = self.convertPathToImport(name)
		try:
			module = importlib.import_module(modulePath)
		except ImportError:
			return False
		
		return module
	
	def parseDocString(self,docstring):
		"""
			Parses a module docstring.
			:param docstring: A properly formatted docstring
			:rtype: A dict with all the parsed values.
		"""
		parsed = {}
		for line in docstring.split("\n"):
			if line.startswith("@"):
				key = line.split(" ")[0][1:]
				value = " ".join( line.split(" ")[1:] )
				parsed[key] = value
				
		return parsed
	
	def __package(self, files, dc, prefix=""):
		""" Packages a list of files into a tarball """
		name = dc["module"] + "-" + dc["version"] + ".tar"
		tar = tarfile.open(name=os.path.join(prefix, name), mode="w")
		for file in files:
			tar.add(file, arcname=file.replace(Config().RootDirectory, ""))
		tar.close()
		
	def __createBoltFile(self, dc, files, prefix=""):
		""" Creates a json file describing the module. """
		name = dc["module"] + "-" + dc["version"] + ".json"
		dc["files"] = [file.replace(Config().RootDirectory,"") for file in files]
		
		with open(os.path.join(prefix, name),"w") as bolt:
			bolt.write(json.dumps(dc))
			
	def packageModule(self,module, prefix=""):
		"""
			Packages an indexed module
			:param module: A tuple with the module and the version
		"""
		print module
		if module in self.files:
			self.__package(self.files[module].values(), self.modules[module[0]],prefix)
			self.__createBoltFile(self.modules[module[0]],self.files[module].values(),prefix)
			
	def listModule(self,module):
		"""
			Lists an indexed module
			:param module: A tuple with the module and the version
		"""
		print module
		if module in self.files:
			pprint.pprint(self.files[module].values())


if __name__ == "__main__":
	if len(sys.argv) < 4:
		print "Not enough arguments supplied."
		sys.exit()
	operation = sys.argv[1]
	
	if operation not in ["export", "list"]:
		print "I don't know how to '%s'. " % operation
	
	ms = ModuleSeparator()
	ms.scanAll()
	
	module = sys.argv[2]
	version = sys.argv[3]
	prefix = "."
	if len(sys.argv)>4:
		prefix = sys.argv[4]
	
	if operation == "export":
		ms.packageModule((module, version),prefix)
	if operation == "list":
		ms.listModule((module, version))
	
			
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
	assert len(ms.files) > 0
	assert len(ms.modules) > 0
	assert "core" in ms.modules.keys()
	
def test_convertPathToImport():
	ms = ModuleSeparator()
	testPathsTuples = [["test","one"],["test","two","three"],["test","test.py"]]
	testPaths = [os.path.join(Config().RootDirectory, p ) for p in  [os.path.join(*path) for path in testPathsTuples]]
	expected = ["Olympus.test.one","Olympus.test.two.three","Olympus.test.test"]
	for t in range(len(testPaths)):
		result = ms.convertPathToImport(testPaths[t])
		assert result == expected[t]
		
def test_parseDocString():
	ms = ModuleSeparator()
	docstring = "@name Test\n@author Test test"
	assert ms.parseDocString(docstring) == {"name":"Test", "author":"Test test"}
	
def test_packageModule():
	ms = ModuleSeparator()
	ms.scanAll()
	ms.packageModule(("PubMed","0.1.0"))
	
