import cStringIO
import os,re
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
		
		self.script = ""
		
	def convertModulesToHierarchy(self):
		hierarchy = {}
		
		for source in self.modules.keys():
			print source
			
		return hierarchy
	
	def retrieveModule(self,moduleName):
		""" Opens a module for reading from its proper path. """
		self.addedModules.add(moduleName)
		if moduleName.startswith("Olympus"):
			moduleName = re.sub("^Olympus\.", "",moduleName)		
		
		path = moduleName.replace(".",os.sep) + ".py"
		currentDir = os.sep.join(__file__.split(os.sep)[:-2])
		absPath = os.path.join(currentDir,path)
		
		if os.path.exists(absPath):		
			return open(absPath).read()
		else:
			print "Can't find '%s' " % absPath
			return ""
		
	def minimizeModule(self, moduleCode):
		""" Removes all the unnecessary fluff from the Python scripts. """
		# Remove comments
		moduleCode = re.sub("#.+", "", moduleCode)
		# Remove test methods
		testPattern = re.compile("def test_.+?:\n(\t+.+\n)+", re.MULTILINE)
		moduleCode = re.sub(testPattern, "", moduleCode)
		# Remove whitespace
		emptyPattern = re.compile("^[\t\n ]+$", re.MULTILINE)
		moduleCode = re.sub(emptyPattern, "", moduleCode)
		
		return moduleCode
	
	def scanDependencies(self,moduleCode):
		""" Scans a Python script for dependencies and records them for later import. """
		imports = re.findall("(?:\t?from )?(.+)? ?import (.+)?", moduleCode)	
		for source, modules in imports:
			if source == "":
				for module in re.split(", ?", modules):
					if module.startswith("Olympus."):				
						if "" in self.modules:
							self.modules[""].add(module.strip())
						else:
							self.modules[""] = set([module.strip()])
					else:
						self.externalDependencies.add(module.strip())
			else:
				source = source.strip()
				if source.startswith("Olympus."):
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
		print
		print "import %s " % ", ".join(self.externalDependencies)
		for source, modules in self.externalModules.items():
			if source == "":
				print "import %s" % ", ".join(modules)
			else:
				print "from %s import %s" % (source, ", ".join(modules))
				

	def openFile(self,filename):
		pass
	
	def writeFile(self,filename):
		pass
	
	def addToCompiledFile(self,module, namespace):
		pass
	
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
	C.printImports()
	
def test_processDependencies():
	C = Compiler()
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	C.printImports()
	
def test_convertModulesToHierarchy():
	C = Compiler()
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	print C.convertModulesToHierarchy()
	
	
	