"""
@name ModuleLoader
@author Stephan Heijl
@module core
@version 0.1.0

ModuleLoader provides an interface to select which modules will be enabled in the next instance of the Olympus Core. 
The selected modules will be stored in the configuration file through Config.
Starting this script from the command line will automatically open the interface. This interface uses `curses` and is therefore
not available on Microsoft Windows.
"""

# ModuleLoader
from Olympus.lib.Config import Config
from Olympus.core.ModuleSeparator import ModuleSeparator
import os, time, tarfile, json, re
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
			
		
	def __unpackModule(self, tmpDir, tmpFileName):
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
			
			# Parse the bolt file
			with open(boltPath) as bolt:
				bolt = json.load(bolt)
				
				# Check every path before copying.
				for targetPath in bolt["files"].values():
					targetPath = os.path.join(Config().RootDirectory, targetPath.strip(os.path.sep))
					print targetPath
					# Handle files that already exist.
					if os.path.exists(targetPath):
						print "Conflict: This filename already exists."
						with open(targetPath) as conflictFile:
							pattern = '\"{3}.+?\"{3}'
							print re.findall(pattern, conflictFile.read(), flags=re.DOTALL)
							ModuleSeparator()
						return False;
				
				for tmpPath, targetPath in bolt["files"].items():
					targetPath = os.path.join(Config().RootDirectory, targetPath.strip(os.path.sep))
					print "Copying %s to %s" % (tmpPath, targetPath)
					
						
		
	def installFromGithub(self, user, repo):
		""" Installs a module from GitHub """
		tmpDir, tmpFileName = self.__downloadFromGithub(user, repo)
		self.__unpackModule( tmpDir, tmpFileName)
		

		
import curses,time,json
		
class ModuleLoaderInterface():
	""" The curses interface for the ModuleLoader. This is the fallback way of setting the available modules."""
	def __init__(self):
		self.moduleloader = ModuleLoader()
		
	def start(self):
		""" Starts the interface with help from the curses wrapper """
		curses.wrapper(self.welcome)
		
	def addCenteredString(self, width, y, string, screen, color_pair=None):
		""" Adds a string to center of the given screen.
		
		:param width: The width (int) of the screen you are adding the screen to.
		:param y: The y coordinate (int) of the text you are adding.
		:param string: The string to be added.
		:param sceen: The screen the text needs to be added to.
		:param color_pair: Optional, the color pair to be used when adding the string.
		"""
		length = len(string)
		
		offsetLeft = (width - length) /2
		if color_pair == None:
			screen.addstr(y, offsetLeft, string)
		else:
			screen.addstr(y, offsetLeft, string,color_pair)
		
	def welcome(self, stdscr):
		""" Shows the welcome display on the screen provided.
		
		:param stdscr: An instance of a curses screen.
		"""
		
		height, width = stdscr.getmaxyx()
		
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)
		
		self.addCenteredString(width, 1, " Welcome to the Olympus Module Loader ",stdscr)
		self.addCenteredString(width, 2, " Press enter or Q to exit and save your selected modules. ",stdscr)
		
		curses.curs_set(0)
		self.welcomeInputLoop(stdscr)
		
	def convertRegularSelectedToCursesSelected(self, modules, selected):
		#raise Exception, selected
		i = 0
		cSelected = []
		for category in modules:
			for module in modules[category]:
				if category not in selected:
					continue
				if unicode(module) in [str(s) for s in selected[category]]:
					cSelected.append(i)
				i+=1		
		
		return cSelected
	
	def welcomeInputLoop(self, stdscr):
		""" Loops over the input of the welcome screen and processes it.
		
		:param stdscr: A curses screen.
		"""
		height, width = stdscr.getmaxyx()
		modules = self.moduleloader.getAllAvailableModules()
		
		selected = self.convertRegularSelectedToCursesSelected(modules, self.moduleloader.getEnabledModules())
		
		hover = 0
		max = self.drawModuleList(stdscr, modules, hover, selected)
	
		while True:
			char = stdscr.getch()
			if char == curses.KEY_ENTER or char == ord("q"):
				break
			if char == ord(" "):
				if hover in selected:
					selected.remove(hover)
				else:
					selected.append(hover)
				self.drawModuleList(stdscr, modules, hover, selected)
			elif char == curses.KEY_UP:
				if hover > 0:
					hover -= 1
				self.drawModuleList(stdscr, modules, hover, selected)			
			elif char == curses.KEY_DOWN:
				if hover < max-1:
					hover += 1
				self.drawModuleList(stdscr, modules, hover, selected)	
			
			stdscr.refresh()
			time.sleep(0.1)
		
		self.addCenteredString(width, 30, " Are you sure? (Y/n) ",stdscr)
		response = stdscr.getch()
		if response == ord("n"):
			self.addCenteredString(width, 30, "                    ",stdscr)
			self.welcomeInputLoop(stdscr)
		
		self.saveModules( self.getSelectedModules(modules,selected) )
		
	def saveModules(self,selectedModules):
		for category,modules in selectedModules.items():
			self.moduleloader.setModules(category, modules)
		
	def getSelectedModules(self, modules, selected):
		""" Gets the modules that were selected based on the list generated by the curses program.
		
		:param modules: The dict with available modules.
		:param selected: A list of integers signifying the selected modules.
		"""
		i = 0
		names = {}
		for category in modules:
			names[category] = []
			for module in modules[category]:
				if i in selected:
					names[category].append(module)
				i+=1
		return names
			
	def drawModuleList(self, stdscr, modules, hover, selected):
		""" Draws a list of modules on the given screen, separated by their respective categories.
		This will probably need some refining for smaller screens.
		
		:param stdscr: A curses screen.
		:param modules: The dict with available modules.
		:param hover: The index of the module where the cursor is positioned.
		:param selected: The list of currently selected modules.
		"""
		
		i = 0
		line = 3
		for category in modules:
			stdscr.addstr(line, 1, category.capitalize())
			line+=1
			stdscr.hline(line, 1, curses.ACS_HLINE, len(category))
			for module in modules[category]:
				line+=1
				
				if i == hover:
					pair = 1
				else: 
					pair = 0
				
				if i in selected:
					stdscr.addstr(line, 1, "[*] " + module, curses.color_pair(pair))
				else:
					stdscr.addstr(line, 1, "[ ] " + module, curses.color_pair(pair))
				i+=1
				
				
			if len(modules[category]) == 0:
				line+=1
				stdscr.addstr(line, 1, "<no modules available>")
			
			line+=2
		stdscr.refresh()
		return i

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
	mli = ModuleLoaderInterface()
	mli.start()
