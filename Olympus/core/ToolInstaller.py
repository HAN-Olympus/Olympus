"""
@name ToolInstaller
@author Stephan Heijl
@module core
@version 0.0.3

This module installs a tool when it has been downloaded. It will appear in the root folder of the downloaded zip.
It requires only Python and pip.
"""
import os,sys

try:
	import pip
except ImportError:
	raise Exception, "Python 'pip' is required for this installer to work."

class ToolInstaller():
	""" This script installs the egg and all its dependencies in the current directory inside a virtualenv. """
	def __init__(self):
		""" Sets up the initial variables. Windows machines use a different directory then POSIX systems. """
		self.virtualEnvDir = "env"
		if os.name == "nt": # Use Windows variables
			self.virtualEnvBinPath = "Scripts"
			
		if os.name == "posix": # Use posix variables
			self.virtualEnvBinPath = "bin"
		
		self.virtualEnvActivationPath = "activate_this.py"
		self.requirementsFile = "requirements.txt"
	
	def installVirtualEnv(self):
		""" This will try to install virtualenv using pip. """
		pip.main(["install","virtualenv"])
		try:
			import virtualenv
			print "'virtualenv' was installed succesfully."
		except ImportError:
			raise Exception, "Python 'virtualenv' is required for this installer to work."
	
	def createVirtualEnv(self):
		""" Launches virtualenv and creates the virtualenv without system packages. """
		os.system("virtualenv --no-site " + self.virtualEnvDir)
	
	def activateVirtualEnv(self):
		""" Makes sure the following commands are run inside the virtualenv. """
		actthispath = os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, self.virtualEnvActivationPath)
		execfile(actthispath,dict(__file__=actthispath) )
	
	def installRequirements(self):
		""" Uses pip to install the requirements for this package. """
		pipPath = os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, "pip")
		os.system(pipPath + " install -r " + self.requirementsFile)
		# Also install PySide, which is not a requirement for the server package.
		print "Installing PySide. This will probably take a long time."
		pip.main(["install","pyside"])
		
	def installTool(self):
		""" Uses the easy_install provided by the virtualenv to install the dist file.. """
		easyInstallPath = os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, "easy_install")
		for file in os.listdir("."):
			if file.endswith(".egg"):
				os.system(easyInstallPath + " " + file)
	
	def createShortcuts(self):
		""" Creates a variety of shortcuts for the tool.
		
		* startServer.sh - starts a local webapp server (Done)
		* startTool.sh - starts the tool (WIP)
		
		"""
		params = {"activate": os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, "activate")}
		
		startServerScript = """
#!/bin/sh
source {activate}
python -m Olympus.webapp.start --tool
		""".format(**params)
		
		startToolScript = """
#!/bin/sh
source {activate}
python -m Olympus.core.ToolInterface --tool
		""".format(**params)
		
		with open("startServer.sh", "w") as startServerFile:
			startServerFile.write(startServerScript)
			
		with open("startTool.sh", "w") as startToolFile:
			startToolFile.write(startToolScript)	
	
	def start(self):
		""" Starts the installation procedure. """
		self.installVirtualEnv()
		self.createVirtualEnv()
		self.activateVirtualEnv()
		self.installRequirements()
		self.installTool()
		self.createShortcuts()
		
if __name__ == "__main__":
	ti = ToolInstaller()
	ti.start()
	
def test_installVirtualEnv():
	ti = ToolInstaller()
	ti.installVirtualEnv()
	
def test_createVirtualEnv():
	ti = ToolInstaller()
	ti.createVirtualEnv()
	assert os.path.isdir(ti.virtualEnvDir)
	# cleanup
	os.system("rm -r %s" % ti.virtualEnvDir)
	
def test_activateVirtualEnv():
	prevPATH = os.environ["PATH"]
	ti = ToolInstaller()
	ti.createVirtualEnv()
	ti.activateVirtualEnv()
	assert os.environ["PATH"] != prevPATH
	os.system("rm -r %s" % ti.virtualEnvDir)
	
def test_installRequirements():
	ti = ToolInstaller()
	if not os.path.isfile(ti.requirementsFile):
		from Olympus.lib.Config import Config
		ti.requirementsFile = os.path.join( Config().RootDirectory,"..","requirements.txt" )
	ti.createVirtualEnv()
	ti.activateVirtualEnv()
	# Get all the installed packages
	packages = os.popen('pip freeze').read()
	
	ti.installRequirements()
	
	newPackages = os.popen('pip freeze').read()
	
	assert len(packages) < len(newPackages)
	os.system("rm -r %s" % ti.virtualEnvDir)
	
def test_createShortcuts():
	ti = ToolInstaller()
	ti.createShortcuts()	
	assert os.path.isfile("startServer.sh")
	
	os.system("rm startServer.sh")
	