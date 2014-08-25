"""
@name ToolInstaller
@author Stephan Heijl, Tom Linssen
@module core
@version 0.2.0

This module installs a tool when it has been downloaded.
It will appear in the root folder of the downloaded zip.
"""
import os,sys, urllib2

	
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
	
	def installPip(self):
		"""Downloading latest version of pip from the internet and installing pip."""
		pipurl = "https://bootstrap.pypa.io/get-pip.py"
		response = urllib2.urlopen(pipurl)
		script = response.read()
		with open("getpip.py", "w") as f:
			f.write(script)
		execfile("getpip.py")
		try: 
			import pip
		except:
			raise ImportError, "Need pip to install"
	
	def warnBuildRequirementsPosix(self):
		requirements = "build-essential git cmake libqt4-dev libphonon-dev python2.7-dev libxml2-dev libxslt1-dev qtmobility-dev"
		print "To use this tool the following dependencies are required for your system:"
		for r in requirements.split(" "):
			print "  *", r
		print "Make sure your have these packages by running the following command:"
		print "sudo apt-get install", requirements
		print
		print "If you do not have installation rights on this computer, please contact your administrator."
		print "These packages are required for the full installation of this tool."
		print "Any other required packages do not need administration level permission to install."
		
	def warnBuildRequirementsNt(self):
		print "Many modules require the BioPython package. This cannot be retrieved from pip on Windows systems."
		print "Download the BioPython lib from the following url for your system:"
		print
		print "http://www.lfd.uci.edu/~gohlke/pythonlibs/#biopython"
		print 
		print "After it has been installed, install this tool with `--with-site-packages` command to use the installed library."
		print "In addition, a running MongoDB instance is required. MongoDB can be retrieved from the following link:"
		print 
		print "http://www.mongodb.org/downloads"

	
	def installVirtualEnv(self):
		""" This will try to install virtualenv using pip. """
		pip.main(["install","virtualenv"])
		try:
			import virtualenv
			print "'virtualenv' was installed succesfully."
		except ImportError:
			raise Exception, "Python 'virtualenv' is required for this installer to work."
	
	def createVirtualEnv(self):
		""" Launches virtualenv and creates the virtualenv without system packages.
		Site-packages are disabled by default, but can """
		if "--with-site-packages" in sys.argv:
			os.system("virtualenv --system-site-packages " + self.virtualEnvDir)
		else:
			os.system("virtualenv --no-site " + self.virtualEnvDir)
	
	def activateVirtualEnv(self):
		""" Makes sure the following commands are run inside the virtualenv. """
		actthispath = os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, self.virtualEnvActivationPath)
		print actthispath
		execfile(actthispath,dict(__file__=actthispath) )
	
	def installRequirements(self, installPySide=True):
		""" Uses pip to install the requirements for this package.
		
		:param installPySide: Installing PySide takes a LONG time, so installing it is optional. Enabled by default, disabled in tests.
		"""
		pipPath = os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, "pip")
		os.system(pipPath + " install -r " + self.requirementsFile)
		# Also install PySide, which is not a requirement for the server package.
		print "Installing PySide. This will probably take a long time."
		if installPySide:
			os.system(pipPath + " install pyside")
		
	def installTool(self):
		""" Uses the easy_install provided by the virtualenv to install the dist file.. """
		easyInstallPath = os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, "easy_install")
		for file in os.listdir("."):
			if file.endswith(".egg"):
				# We store the name of the OlympusTool egg, that way we can set the configuration details later.
				if "OlympusTool" in file:
					self.olympusToolPath = file
				os.system(easyInstallPath + " " + file)
	
	def createShortcutsWindows(self):
		""" Creates a variety of shortcuts for the tool on Windows systems.
		
		* startServer.bat - starts a local webapp server (Done)
		* startTool.bat - starts the tool (WIP)
		
		"""
		params = {"python": os.path.join(os.path.abspath(self.virtualEnvDir), self.virtualEnvBinPath, "python")}
		
		startServerScript = """
{python} -m Olympus.webapp.start --tool
		""".format(**params)
		
		startToolScript = """
{python} -m Olympus.core.ToolInterface --tool
		""".format(**params)
		
		with open("startServer.bat", "w") as startServerFile:
			startServerFile.write(startServerScript)
			
		with open("startTool.bat", "w") as startToolFile:
			startToolFile.write(startToolScript)
			
	def createShortcutsPosix(self):
		""" Creates a variety of shortcuts for the tool on Posix systems.
		
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
			
	def setInitialConfigs(self):
		""" Makes sure that the initial configuration for the tool is correct. This is mainly the directory settings. """
		libDir = os.path.abspath(os.path.join(self.virtualEnvDir, "lib"))
		versionDir = os.listdir(libDir)[0]
		sys.path.append(os.path.join(libDir, versionDir, "site-packages", self.olympusToolPath))
		sys.path.append(os.path.join(libDir, "site-packages", self.olympusToolPath))
		from Olympus.lib.Config import Config
		
		config = Config()
		if os.name == "posix":
			config.RootDirectory = os.path.join(libDir, versionDir, "site-packages", self.olympusToolPath, "Olympus")
		elif os.name == "nt":
			config.RootDirectory = os.path.join(libDir, "site-packages", self.olympusToolPath, "Olympus")
		config.WebAppDirectory = os.path.join(config.RootDirectory, "webapp")
		config.TemplatesDirectory = os.path.join(config.WebAppDirectory, "templates")
		config.save()
	
	def start(self):
		""" Starts the installation procedure. """
		self.installPip()
		self.installVirtualEnv()
		self.createVirtualEnv()
		self.activateVirtualEnv()
		self.installRequirements()
		self.installTool()
		self.setInitialConfigs()
		if os.name == "posix":
			self.createShortcutsPosix()
		if os.name == "nt":
			self.createShortcutsWindows()
		
	def help(self):
		print "This will install the Olympus tool. The following options are available:"
		print "    --help                    Will show this screen."
		print "    --with-site-packages      Will install this tool with virtualenv site packages."
		print "    --skip-warn               Skips waiting for user input after the warning."
		print "    This is useful if you are running multiple tools on this computer and some"
		print "    dependencies are already available."
		
if __name__ == "__main__":	
	ti = ToolInstaller()
	if "--help" in sys.argv:
		ti.help()
		sys.exit()
	
	print "-"*50
	if os.name == "posix":
		ti.warnBuildRequirementsPosix()
	if os.name == "nt":
		ti.warnBuildRequirementsNt()
	print "-"*50
	if "--skip-warn" not in sys.argv:
		raw_input("Press enter to continue.")
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
	
	ti.installRequirements(installPySide=False)
	
	newPackages = os.popen('pip freeze').read()
	
	assert len(packages) < len(newPackages)
	os.system("rm -r %s" % ti.virtualEnvDir)
	
def test_createShortcutsPosix():
	ti = ToolInstaller()
	ti.createShortcutsPosix()	
	assert os.path.isfile("startServer.sh")
	assert os.path.isfile("startTool.sh")
	os.system("rm startTool.sh")
	os.system("rm startServer.sh")
	
def test_installPip():
	ti = ToolInstaller()
	ti.installPip()
	assert os.path.isfile("getpip.py")
	import pip
	
	
	
	
