import cStringIO
import os,re, inspect
import Olympus.lib.ProcedureContainer

class Compiler():
	""" This class compiles the given modules and their dependencies into a single Python file. 
		The trick here is to insert them into their own classes to "fake" namespaces and retain the proper naming scheme in the modules.
		This will leave a single Python file with all the modules compiled into it without comments.
	"""
	
	def __init__(self):
		self.modules = {}
		self.externalModules = {}
		self.externalDependencies = set()
		self.addedModules = set()
		
		# Gets the name of the current package.
		self.currentPackage = inspect.getmodule(inspect.stack()[1][0]).__name__.split(".")[0]

		self.script = ""
		
	def convertModulesToHierarchy(self):
		""" To properly add all the modules they need to be represented as a hierarchy. This method will do so for all sources in the modules list dicationary.

		It yields a dictionary like this one:

		    {'Olympus': {'lib': {'Article': 'Article',
                         'Collection': 'Collection',
						 ...
                         'Singleton': 'Singleton',
                         'StoredObject': 'StoredObject'},
                 'modules': {'acquisition': {'AcquisitionModule': 'AcquisitionModule'}}}}

		"""
		hierarchy = {}
		
		# This could also be represented recursively, but in order to consolidate all this behaviour into one function I chose to represent it as a loop. Please enjoy these extra comments, as this might not be the most straightforward method.
		for source in self.modules.keys():
			names = source.split(".") # Split the module in its constituent parts
			for n in range(len(names)):
				currentLevel = hierarchy # Restart the hierachy at the root level for every module.
				for name in names[:n+1]: # Go through every submodule
					if name not in currentLevel.keys():
						# If this is the last module in the name, it follows that it will be the module name. Otherwise it will have children.
						if len(names) == n+1:
							currentLevel[name] = name
						else:
							currentLevel[name] = {}
					# Set the currentLevel to the new sublevel before restarting the loop.
					currentLevel = currentLevel[name]

		return hierarchy
	
	def retrieveModule(self,moduleName):
		""" Opens a module for reading from its proper path.

		:param moduleName: The name of the module as though it were written in an import statement. Not a filename.
		:rtype: The contents of the module file.
		"""
		self.addedModules.add(moduleName)
		if moduleName.startswith(self.currentPackage):
			moduleName = re.sub("^"+self.currentPackage+"\.", "",moduleName)
		
		path = moduleName.replace(".",os.sep) + ".py"
		currentDir = os.sep.join(__file__.split(os.sep)[:-2])
		absPath = os.path.join(currentDir,path)
		
		if os.path.exists(absPath):		
			return open(absPath).read()
		else:
			print "Can't find '%s' " % absPath
			return ""
		
	def minimizeModule(self, moduleCode):
		""" Removes all the unnecessary fluff from the Python scripts. This includes:

		* Unnessecary whitespace (insofar as this is possible with Python.
		* All regular comments starting with a hash. (#) Will not remove multiline comments (triple quotes) as these might represent actual pieces of code.

		:param moduleCode: The code contained in a python script.
		:rtype: The minimized code.
		"""
		# Remove comments
		moduleCode = re.sub("#.+", "", moduleCode)

		"""
		# Remove test methods
		testPattern = re.compile("def test_.+?:\n(\t+.+\n)+", re.MULTILINE)
		moduleCode = re.sub(testPattern, "", moduleCode)
		"""

		# Remove whitespace
		emptyPattern = re.compile("^[\t\n ]+$", re.MULTILINE)
		moduleCode = re.sub(emptyPattern, "", moduleCode)
		
		return moduleCode
	
	def scanDependencies(self,moduleCode):
		""" Scans a Python script for dependencies and records them for later import. Will reserve a special case for the current package.

		:param moduleCode: The code contained in a Python script.
		:rtype: All the imports contained within the code.
		"""
		imports = re.findall("(?:\t?from )?(.+)? ?import (.+)?", moduleCode)

		for source, modules in imports:
			if source == "":
				for module in re.split(", ?", modules):
					if module.startswith(self.currentPackage + "."):
						if "" in self.modules:
							self.modules[""].add(module.strip())
						else:
							self.modules[""] = set([module.strip()])
					else:
						self.externalDependencies.add(module.strip())
			else:
				source = source.strip()
				if source.startswith(self.currentPackage + "."):
					for module in re.split(", ?", modules):
						if source in self.modules:
							self.modules[source].add(module.strip())
						else:
							self.modules[source] = set([module.strip()])
				else:
					for module in re.split(", ?", modules):
						if source in self.modules:
							self.externalModules[source].add(module.strip())
						else:
							self.externalModules[source] = set([module.strip()])
						
	def processDependencies(self):
		""" Process all the dependencies currently in available and recursively solve them. """
		for source, modules in self.modules.items():
			if source not in self.addedModules:
				module = self.retrieveModule(source)
				self.scanDependencies(module)
				self.processDependencies()
		
	def printImports(self):
		""" Prints the current list of imports as valid import statements. """

		print "import %s " % ", ".join(self.externalDependencies)
		for source, modules in self.externalModules.items():
			if source == "":
				print "import %s" % ", ".join(modules)
			else:
				print "from %s import %s" % (source, ", ".join(modules))
	
	def walkHierarchy(self, parents, node):
		tabs = "\t" * len(parents)
		decoratorLine = "%s@matryoshka" % (tabs)
		for k, v in node.items():
			if isinstance(v, dict):
				classLine = "%sclass %s():" % (tabs, k)
				self.nameSpacedCode.append(decoratorLine)
				self.nameSpacedCode.append(classLine)
				self.walkHierarchy(parents+[k], v)
			else:
				code = self.retrieveModule(".".join(parents+[v]))
				code = self.minimizeModule(code)

				for line in code.split("\n"):
					if line.strip().startswith("class"):
						self.nameSpacedCode.append(decoratorLine)
					self.nameSpacedCode.append(tabs+line)
	
	def createNameSpaces(self, hierarchy):
		self.nameSpacedCode = []
		matryoshkaDecorator = """
def matryoshka(cls):

	# get types of classes
	class classtypes:
		pass
	classtypes = (type, type(classtypes))

	# get names of all public names in outer class
	directory = [n for n in dir(cls) if not n.startswith("_")]

	# get names of all non-callable attributes of outer class
	attributes = [n for n in directory if not callable(getattr(cls, n))]

	# get names of all inner classes
	innerclasses = [n for n in directory if isinstance(getattr(cls, n), classtypes)]

	# copy attributes from outer to inner classes (don't overwrite)
	for c in innerclasses:
		c = getattr(cls, c)
		setattr(c, cls.__name__, cls)
		for a in attributes:
			if not hasattr(c, a):
				setattr(c, a, getattr(cls, a))
	return cls
		"""
		self.nameSpacedCode.append(matryoshkaDecorator)
		self.walkHierarchy([], hierarchy)
		print "\n".join(self.nameSpacedCode)

	def compile(self):
		pass

# TESTING #

def test_retrieveModule():
	C = Compiler()
	C.retrieveModule("modules.acquisition.PubMed")
	
def test_minimizeModule():
	C = Compiler()
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.minimizeModule(module)
	
def test_scanDependencies():
	C = Compiler()
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	module = C.retrieveModule("modules.acquisition.WormBase")
	C.scanDependencies(module)
	module = C.retrieveModule("modules.acquisition.UniProt")
	C.scanDependencies(module)
	module = C.retrieveModule("modules.acquisition.GeneOntology")
	C.scanDependencies(module)
	#C.printImports()
	
def test_processDependencies():
	C = Compiler()
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	#C.printImports()
	
def test_convertModulesToHierarchy():
	C = Compiler()
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	import pprint
	pprint.pprint( C.convertModulesToHierarchy() )

def test_createNameSpaces():
	C = Compiler()
	C = Compiler()
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	hierarchy = C.convertModulesToHierarchy()

	print C.createNameSpaces(hierarchy)

