"""
@name Compiler
@author Stephan Heijl
@module core
@version 0.0.3
"""

import cStringIO
import os,re, inspect,time,subprocess, pprint
from Olympus.lib.Procedure import Procedure
from Olympus.lib.Config import Config
from Olympus.core.Core import Core

class Compiler():
	""" This class compiles the given modules and their dependencies into an egg file for redistribution. """
	
	def __init__(self, procedure):
		""" Initialize the compiler with a Procedure. """
		
		# Gets the name of the current package.
		self.currentPackage = __name__.split(".")[0]
		self.modules = {}
		self.externalModules = {}
		self.externalDependencies = set()
		self.addedModules = set()
		self.basics = ["Olympus.core.Worker", "Olympus.core.Core", "Olympus.core.Core"]
		self.procedure = procedure
		self.script = ""
		self.data = {}
		self.dataIgnore = [".less", ".scss"]
		
	def getDataFiles(self):
		""" The webapp portion of Olympus is required. 	"""
		for root, dirs, files in os.walk(Config().RootDirectory + os.sep + "webapp"):
			if os.path.sep + "tmp" + os.path.sep  in root: # Ignore tmp folders
				continue
			root = root.replace(Config().RootDirectory, "")
			root = str(self.currentPackage + root)
			self.data[root] = []
			for file in files:
				if True in [file.endswith(ext) for ext in self.dataIgnore]:
					# Filter ignored filetypes
					continue
				self.data[root].append( str( root + os.sep + file ) )
				
		self.data = self.data.items()
		
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
		
		# This could also be represented recursively, but in order to consolidate all this behaviour into one function I chose to represent it as a loop.
		# Please enjoy these extra comments, as this might not be the most straightforward method.
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
	
	def addModule(self, moduleName):
		""" Adds a module to the tool. 
		
		:param moduleName: The name of the module, not its path. Example: `Olympus.core.Core`. This module must be in this package.
		"""
		module = self.retrieveModule(moduleName)
		if not moduleName.startswith(self.currentPackage):
			moduleName = self.currentPackage + "." + moduleName
		self.modules[moduleName] = [moduleName.strip(".")[-1]]
		self.scanDependencies(module)
	
	def retrieveModule(self,moduleName):
		""" Opens a module for reading from its proper path.

		:param moduleName: The name of the module, not its path. Example: `Olympus.core.Core`. This module must be in this package.
		:rtype: The contents of the module file.
		"""
		self.addedModules.add(moduleName)
		if moduleName.startswith(self.currentPackage):
			moduleName = re.sub("^" + self.currentPackage + "\.", "", moduleName)
		
		path = moduleName.replace(".",os.sep) + ".py"
		absPath = os.path.join(Config().RootDirectory,path)
		
		if os.path.exists(absPath):		
			return open(absPath).read()
		else:
			print "Can't find '%s' " % absPath
			return ""
	
	def scanDependencies(self,moduleCode):
		""" Scans a Python script for dependencies and records them for later import. 
		Will reserve a special case for the current package.

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
				
	def createRequirementsFile(self):
		for requirement in self.externalModules:
			print requirement
			
	def getPackages(self):
		""" Retrieves the various packages used in this tool. """
		packages = set()
		for module in self.modules:
			packages.add( str(".".join(module.split(".")[:-1])) ) 
		return list(packages)

	def buildEgg(self):
		for node in self.procedure.nodes:
			print node
			self.addModule("Olympus.modules."+node)
			
		self.processDependencies()
		self.getDataFiles()
		
		# Create temporary directory
		id = int(time.time())
		tmpDir = os.path.abspath("tmp/build-%s" % id)
		try:
			os.mkdir("tmp")
		except:
			pass # Directory already exists
		try:
			os.mkdir(tmpDir)
		except:
			pass # Directory already exists
		
		# Create temporary setup file with required modules
		
		data = {
			"version": Core().getVersion(),
			"packages": pprint.pformat(self.getPackages() ),
			"modules": pprint.pformat([str(module) for module in self.modules.keys() + self.basics]),
			"data": str(self.data)
		}
		
		# We create a setup file.
		setup = """
from setuptools import setup
import os, sys

# Add the installation dir to the PYTHONPATH
if "install" in sys.argv:
	prefix = os.path.expanduser( sys.argv[-1].split("=")[-1] )
	version = "%s.%s" % (sys.version_info[0], sys.version_info[1])
	installDir = os.path.join( prefix, "lib", "python%s" % version, "site-packages" )
	print installDir
	if "PYTHONPATH" not in os.environ:
		os.environ["PYTHONPATH"] = ""
	if len(os.environ["PYTHONPATH"])>0 and os.environ["PYTHONPATH"][-1] != os.pathsep:
		os.environ += os.pathsep
	os.environ["PYTHONPATH"] += installDir
	try:
		os.makedirs(installDir)
	except: 
		pass
	for m in {packages}:
		try:
			os.makedirs(os.path.join(installDir, m.replace(".",os.path.sep)))
		except:
			pass

setup(
    name = "Olympus generated package",
    version = "{version}",
    author = "Stephan Heijl",
	packages = [],
	py_modules= {modules},
	data_files = {data}
)		
		""".format(**data)
		
		print [module for module in self.modules.keys() + self.basics]
		
		with open(os.path.join(tmpDir, "setup.py"),"w") as sfile:
			sfile.write(setup)
		
		# Run temporary setup file with temporary directory as output
		command = "cd %s ; cd .. ; echo pwd; python %s bdist_egg -d %s" % (Config().RootDirectory, os.path.join(tmpDir, "setup.py"), tmpDir)
		subprocess.Popen(command, shell=True, stdout=open(os.devnull, 'wb')).communicate()
		
		# Create a setup file with appropiate requirements
		
		
		# Compile this into some sort of package (zip/installer/deb?)
		# Return as a file.
		
		return id


# TESTING #

def test_retrieveModule():
	C = Compiler(Procedure([],[],[]))
	C.retrieveModule("modules.acquisition.PubMed")
	
def test_scanDependencies():
	C = Compiler(Procedure([],[],[]))
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
	C = Compiler(Procedure([],[],[]))
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	C.printImports()
	
def test_convertModulesToHierarchy():
	C = Compiler(Procedure([],[],[]))
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	import pprint
	pprint.pprint( C.convertModulesToHierarchy() )

	
def test_buildEgg():
	print "Building egg"
	C = Compiler(Procedure([],[],[]))
	C.addModule("modules.acquisition.PubMed")
	C.processDependencies()
	C.buildEgg()

def test_getPackage():
	C = Compiler(Procedure([],[],[]))
	C.addModule("modules.acquisition.PubMed")
	C.processDependencies()
	print C.getPackages()
