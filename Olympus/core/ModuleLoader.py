"""
@name ModuleLoader
@author Stephan Heijl
@module core
@version 0.2.0

ModuleLoader provides an interface to select which modules will be enabled in the next instance of the Olympus Core. 
The selected modules will be stored in the configuration file through Config.
"""

# ModuleLoader
from Olympus.lib.Config import Config
from Olympus.core.ModuleSeparator import ModuleSeparator
import os, time, tarfile, json, re, sys
import requests
from github import Github

class ModuleLoader():
	""" The base class for the loading of modules. This class provides all the functionality for actually adding, removing and finding modules.	"""
		
	def getAllAvailableModules(self):
		""" Returns a dictionary with every single available module in your distribution. The modules are divided up by their category."""
		modulesFolder = "modules"
		modulesFolderPath = os.path.abspath(os.path.join(Config().RootDirectory, modulesFolder))
		
		modules = {}
		
		for category in os.listdir(modulesFolderPath):
			if "." in category:
				continue
			modules[category] = []
			for file in os.listdir(modulesFolderPath + "/" + category):
				if file[-3:] != ".py":
					continue
				if file.startswith("__init__"):
					continue
				if file[:-3].lower().replace("module","") == category:
					continue
				modules[category].append(file[:-3])
				
		return modules
		
	def loadModule(self, name):
		""" Loads a module. 
		
		:param name: The name of the module that needs to be loaded.
		"""
		__import__(name)
	
	def enableModule(self, category, name):
		""" Enables a module based on the name and category. Saves automatically.
		
		:param category: The category the module it situated in.
		:param name: The name of the module to enable.
		"""
				
		c = Config()
		if "modules" not in c.getAttributes():
			c.modules = {}
		if "enabled" not in c.modules:
			c.modules["enabled"] = {}
		if category not in c.modules["enabled"]:
			c.modules["enabled"][category] = []
		if name not in c.modules["enabled"][category]:
			c.modules["enabled"][category].append(name)
		
		c.save()
		
	def disableModule(self, category, name):
		""" Disables a module based on the name and category. Saves automatically.
		
		:param category: The category the module it situated in.
		:param name: The name of the module to enable.
		"""
		c = Config()
		print c.configFileName
		
		if "modules" not in c.getAttributes():
			c.modules = {}
		if "enabled" not in c.modules:
			c.modules["enabled"] = {}
		if category not in c.modules["enabled"]:
			c.modules["enabled"][category] = []
		if name in c.modules["enabled"][category]:
			c.modules["enabled"][category].remove(name)
		
		c.save()
		
	def setModules(self, category, modules):
		""" Sets a series of a modules to enabled. This will disable any modules in this category that are not on the list.
		If you wish to retain the currently enabled modules use `enableModules()`. Saves automatically.
		
		:param category: The category the modules are situated in.
		:param modules: A list with the names of the modules to set as enabled.
		"""
		c = Config()
		
		if "modules" not in c.getAttributes():
			c.addAttribute("modules", None)
		if "enabled" not in c.modules:
			c.modules["enabled"] = {}
		if category not in c.modules["enabled"]:
			c.modules["enabled"][category] = []
		
		c.modules["enabled"][category]= modules
		
		c.save()
		
	def getEnabledModules(self):
		""" Finds all the enabled modules 
		
		:rtype: A dictionary of all the enabled modules.
		"""
		c = Config()
		if "modules" not in c.getAttributes():
			return {}
		if "enabled" not in c.modules:
			return {}
		return c.modules["enabled"]
	
	def __downloadFromGithub(self, user, repo):
		""" Downloads a packed module from GitHub. 
		
		:param user: The username for this repository.
		:param repo" The name of the repository.
		"""
#		g = Github();
#		repository = g.get_repo("%s/%s" % (user,repo))
#		url = repository.get_archive_link("tarball")
		url = "https://codeload.github.com/HAN-Olympus/Olympus-PubMed/legacy.tar.gz/master"
		
		r = requests.get(url)
		
		# Create temporary copy of the module
		tmpDir = os.path.join(Config().RootDirectory, "tmp")
		if not os.path.isdir(tmpDir):
			os.mkdir(tmpDir)
		
		tmpFileName = "downloadedModule"+str(int(time.time()))+".tar"
		
		# Download the file in 1kb chunks
		with open(os.path.join(tmpDir, tmpFileName), "wb") as tarball:
			for block in r.iter_content(1024):
				if not block:
					break
				tarball.write(block)
				
		return tmpDir,tmpFileName
		
	def __getRequiredFiles(self, names):
		""" This function will return all the files in a list of filenames that
			have the same base name, but not necessarily the same extensions.
		
			:param names: A list of filesystem paths.
			:rtype: A dictionary with the basename of these files as key and a list with their full paths as a value.
		"""
		# We expect some files with the exact same name.
		expectedExtensions = ["json","tar"]
		probableFiles = []
		seen = {}
		intersect = {}
		
		for dirname, filename in names:
			basename = ".".join(filename.split(".")[:-1])
			extension = filename.split(".")[-1]
			
			if (expectedExtensions > 0) and extension in expectedExtensions:
				print filename
				probableFiles.append((dirname, filename, basename, extension))
				
		for dirname, filename, basename, extension in probableFiles:
			data = os.path.join(dirname, filename)
			if basename not in seen:
				seen[basename] = data
			else:
				if basename in intersect:
					intersect[basename].append(data)
				else:
					intersect[basename] = [seen[basename], data]
					
		return intersect
			
		
	def __unpackModules(self, tmpDir, tmpFileName):
		""" Unpacks the tarball from GitHub and places it the Olympus directory. 
		
		:param tmpDir: The directory where the tarball was stored
		:param tmpFileName: The name of the tarball.
		"""
		tarPath = os.path.join(tmpDir, tmpFileName)
		if not tarfile.is_tarfile(tarPath):
			return Exception, "The downloaded file was corrupt."

		tar = tarfile.open(tarPath)
			
		names = [os.path.split(n) for n in tar.getnames()]
		requiredFiles = self.__getRequiredFiles(names)
		tar.extractall(tmpDir)
		
		print requiredFiles.values()
		for paths in requiredFiles.values():
			# Installation paths
			boltPath = ""
			tarballPath = ""
			for path in paths:
				
				filename = os.path.basename(path)
				basename = ".".join(filename.split(".")[:-1])
				extension = filename.split(".")[-1]
				
				# We need to direct this path to the tmpDir
				path = os.path.join(tmpDir, path)
				if extension == "json":
					boltPath = path
				if extension == "tar":
					tarballPath = path
				
				if boltPath != "" and tarballPath != "":
					self.__unpackModule(tmpDir, boltPath, tarballPath)
					boltPath = ""
					tarballPath = ""
					
					
	def __unpackModule(self, tmpDir, boltPath, tarballPath):
		""" Unpacks a single module from a downloaded GitHub repo. """
		# Parse the bolt file
		print tarballPath
		with open(boltPath) as bolt:
			bolt = json.load(bolt)

			# Check every path before copying.
			for downloadedPath in bolt["files"].values():
				time.sleep(1)
				targetPath = os.path.join(Config().RootDirectory, downloadedPath.strip(os.path.sep))
				print targetPath
				# Handle files that already exist.
				if os.path.exists(targetPath):
					print "Conflict: This filename already exists."
					existingVersion = ""
					downloadedVersion = bolt["version"]
					pattern = '\"{3}.+?\"{3}'
					with open(targetPath) as conflictFile:
						doc = re.findall(pattern, conflictFile.read(), flags=re.DOTALL)[0]
						parsedDocs = ModuleSeparator().parseDocString(doc)
						existingVersion = parsedDocs["version"]
					
					# Compare the two version numbers
					if "".join(re.findall("([0-9]+)", existingVersion)) > "".join(re.findall("([0-9]+)", downloadedVersion)):
						return False																			 
			
			tarball = tarfile.open(tarballPath)
			for tmpPath, targetPath in bolt["files"].items():
				time.sleep(1)
				targetPath = os.path.join(Config().RootDirectory, targetPath.strip(os.path.sep))
				print "Copying %s to %s" % (tmpPath, targetPath)
				# Rename old files
				if os.path.exists(targetPath):
					oldPath = targetPath + ".%s.%s.old" % (existingVersion, int(time.time()))
					os.rename(targetPath, oldPath)
				tarball.extract(tmpPath.strip(os.path.sep), Config().RootDirectory)
				if os.path.exists(targetPath):
					print "Copied successfully!"
				
		
	def installFromGithub(self, user, repo):
		""" Installs a module from GitHub """
		tmpDir, tmpFileName = self.__downloadFromGithub(user, repo)
		self.__unpackModules( tmpDir, tmpFileName)
		
		
def test_setup():
	c = Config()
	currentDir = os.path.dirname(__file__)
	testConfPath = os.path.abspath(currentDir + "/../test.conf")
	c.configFileName = testConfPath
	c.save()
	
def test_getAllAvailableModules():
	ml = ModuleLoader()
	modules = ml.getAllAvailableModules()
	assert "interface" in modules
	assert "acquisition" in modules
	assert "interpretation" in modules
	assert "visualization" in modules
	
def test_enableModule():
	ml = ModuleLoader()
	ml.enableModule("acquisition","PubMed")
	
def test_getEnabledModules():
	ml = ModuleLoader()
	enabled = ml.getEnabledModules()
	assert "PubMed" in enabled["acquisition"]
	
def test_disableModule():
	ml = ModuleLoader()
	ml.disableModule("acquisition", "PubMed")
	
def test_teardown():
	handle = open(Config().configFileName)
	print "The TEST CONFIG (%s) follows." % Config().configFileName
	print handle.read()
	handle.close()
	os.remove(Config().configFileName)
	
def test_installFromGithub():
	ml = ModuleLoader()
	ml.installFromGithub("HAN-Olympus","Olympus-PubMed")
		
if __name__ == "__main__":
	# The default start now provides a way to auto install a module.
	ml = ModuleLoader()
	command = sys.argv[1]
	if command == "install":
		if len(sys.argv) == 3 and "/" in sys.argv[2]:
			# The user has submitted a user/repo pair with a slash
			ml.installFromGithub(*sys.argv[2].split("/"))
		elif len(sys.argv) == 4:
			# The user has submitted a user repo pair with a space
			ml.installFromGithub(sys.argv[2],sys.argv[3])
		else:
			print "Invalid arguments. Try submitting a user/repo pair like HAN-Olympus/Olympus-PubMed"
		print "Exited."
	else:
		print "Command not recognized."