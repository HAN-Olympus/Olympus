""" ModuleLoader provides an interface to select which modules will be enabled in the next instance of the Olympus Core. 
The selected modules will be stored in the configuration file through Config.
Starting this script from the command line will automatically open the interface. This interface uses `curses` and is therefore
not available on Microsoft Windows.
"""

# ModuleLoader
import additionalImports
from Config import Config
import os

class ModuleLoader():
	""" The base class for the loading of modules. This class provides all the functionality for actually adding, removing and finding modules.	"""
		
	def getAllAvailableModules(self):
		""" Returns a dictionary with every single available module in your distribution. The modules are divided up by their category."""
		currentDir = os.path.dirname(__file__)
		modulesFolder = "../modules"
		modulesFolderPath = os.path.abspath(currentDir + "/" + modulesFolder)
		
		modules = {}
		
		for category in os.listdir(modulesFolderPath):
			modules[category] = []
			for file in os.listdir(modulesFolderPath + "/" + category):
				if file[-3:] != ".py":
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
			c.addAttribute("modules", {})
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
			c.addAttribute("modules", {})
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
			c.addAttribute("modules", {})
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
		return c.modules["enabled"]
		
import curses,time, json
		
class ModuleLoaderInterface():
	""" The curses interface for the ModuleLoader. This is the default way of setting the available modules."""
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
	
	def welcomeInputLoop(self, stdscr):
		""" Loops over the input of the welcome screen and processes it.
		
		:param stdscr: A curses screen.
		"""
		height, width = stdscr.getmaxyx()
		modules = self.moduleloader.getAllAvailableModules()
		
		selected = []
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
			for module in modules:
				self.moduleloader.enableModule(category, module)
		
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
	os.remove(Config().configFileName)
		
if __name__ == "__main__":
	mli = ModuleLoaderInterface()
	mli.start()