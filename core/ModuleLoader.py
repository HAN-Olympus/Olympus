""" ModuleLoader provides an interface to select which modules will be enabled in the next instance of the Olympus Core. 
The selected modules will be stored in the config file through Config.
Starting this script from the commandline will automatically open the interface. This interface uses `curses` and is therefor
not available on Microsoft Windows.
"""

# ModuleLoader
import additionalImports
import Config
import os

class ModuleLoader():
	""" The base class for the loading of modules. This class provides all the functionality for actually adding, removing and finding modules.	"""
	def __init__(self):
		pass
		
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

		
import curses
		
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
		:param stdscr: An instnace of a curses screen.
		"""
		
		height, width = stdscr.getmaxyx()
		
		curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
		
		self.addCenteredString(width, 1, " Welcome to the Olympus Module Loader ",stdscr,color_pair=curses.color_pair(1))
		modules = self.moduleloader.getAllAvailableModules()
		
		line = 3
		for category in modules:
			stdscr.addstr(line, 1, category.capitalize())
			line+=1
			stdscr.addstr(line, 1, "="*len(category))
			for module in modules[category]:
				line+=1
				stdscr.addstr(line, 3, module)
				
			if len(modules[category]) == 0:
				line+=1
				stdscr.addstr(line, 3, "<no modules available>")
			
			line+=2
		stdscr.refresh()

def test_getAllAvailableModules():
	ml = ModuleLoader()
	modules = ml.getAllAvailableModules()
	assert "interface" in modules
	assert "acquisition" in modules
	assert "interpretation" in modules
	assert "visualization" in modules
		
if __name__ == "__main__":
	mli = ModuleLoaderInterface()
	mli.start()