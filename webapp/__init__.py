from flask import Flask
from Olympus.lib.Config import Config
import importlib

app = Flask(__name__)

# Get all the enabled modules
enabledModules = Config().modules["enabled"]

# Load all the enabled modules into a dictionary
modules = {}
for category in enabledModules:	
	modules[category] = {}
	for module in enabledModules[category]:
		moduleName = "Olympus.modules.%s.%s" % (category,module)
		importedModule = __import__(moduleName, fromlist=["Olympus.modules.%s" % category])
		if module in importedModule.__dict__.keys():
			modules[category][module] = importedModule.__dict__[module]
			
import Olympus.webapp.routes