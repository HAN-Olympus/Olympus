import json, os, sys

class Config():
	def __init__(self):
		# Olympus.conf is the configuration file that is loaded for Olympus
		olympusConfName = "../olympus.conf"
		# Default.conf is loaded if Olympus.conf is not available.
		# It provides a safe fallback for testing purposes. If you are setting up your
		# own Olympus you should copy this and work from there.
		defaultConfName = "../default.conf"
		
		if os.path.exists(olympusConfName):
			self.conf = json.load( open(olympusConfName, "r") )
		else:
			try:
				self.conf = json.load( open(olympusConfName, "r") )
			except:
				raise IOError, "No default configuration file found, you need a configuration file to use this module."
		
		self.applyConfig()
		
	def applyConfig(self):
		for key,value in self.conf.items():
			setattr(self, key, value)
		

if "nosetests" not in sys.argv[0] :
	Config = Config()

def test_Config():
	c = Config()
	assert c.__dict__["username"] == c.username
	assert c.username == "default" or c.username == "olympus"