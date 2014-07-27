from flask import Flask
from Olympus.lib.Config import Config
from Olympus.core.ModuleLoader import ModuleLoader
import sys

# Check if this is not a sphinx-build:
if True not in ["sphinx-build" in arg for arg in sys.argv]:
	app = Flask(__name__)
	
	availableModules = ModuleLoader().getAllAvailableModules()
	# Load all the modules into a dictionary
	modules = {}
	for category in availableModules:	
		modules[category] = {}
		for module in availableModules[category]:
			moduleName = "Olympus.modules.%s.%s" % (category,module)
			importedModule = __import__(moduleName, fromlist=["Olympus.modules.%s" % category])
			if module in importedModule.__dict__.keys():
				modules[category][module] = importedModule.__dict__[module]

	import Olympus.webapp.routes