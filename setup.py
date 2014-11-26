from setuptools import setup, find_packages
from setuptools.command.install import install
from Olympus.core.Core import Core
from Olympus.lib.Config import Config
import os, sys, re, subprocess
import pprint

class installNativeDependencies(install):
	""" We need some more stuff for the client to actually run. """
	
	def getInstalledPackages(self):
		try:
			self.packages
		except AttributeError:
			pass
		else:
			return self.packages
		self.packages = []
		packages = os.popen("dpkg -l").read()
		for line in packages.split("\n"):
			details = re.split(" +",line)
			if len(details) > 2:
				self.packages.append( details[1] )
		return self.packages
	
	def installPipRequirements(self):
		print "Installing Pip requirements"
		try:
			print subprocess.call("sudo pip install -r requirements.txt",shell=True)
			return True
		except Exception as e:
			print e
			try:
				# accounts for Travis
				os.popen("sudo pip install --use-mirrors -r requirements.txt")
			except Exception as e:
				return False
			return True
	
	def installPySide(self):
		""" We install PySide for the user interface. 
			PySide installation instructions were derived from http://pyside.readthedocs.org/en/latest/building/linux.html
		"""
		print "Installing PySide"
		
		if "python-pyside" in self.getInstalledPackages():
			return True
		
		installed = False
		try:
			import PySide
			# Might add some extra version validation here.
			installed = True
		except:		   
			installed = False
			
		if not installed:
			if "--force" not in sys.argv:
				permission = raw_input("Install Pyside? (Y/n): ")
			else:
				permission = True
			if permission == "n":
				return True
			try:				
				# Perfom the PySide install
				os.system("sudo add-apt-repository -y ppa:pyside")
				os.system("sudo apt-get -y update")
				os.system("sudo apt-get install -y python-pyside")
				
				installed = True
			except:
				installed = False
		
		# Final check
		try:
			import PySide
			print "PySide was installed and imported succesfully. Current PySide version is: " + PySide.__version__
			print "The current Python version is: " + sys.version
			# Might add some extra version validation here.
			installed = True
		except:
			print "PySide had troubles installing. "
			installed = False
		
		return installed
	
	def installLibFreeType(self):
		""" We need libfreetype for Flask. """
		
		if "libfreetype6-dev" in self.getInstalledPackages():
			return True
		
		if "--force" not in sys.argv:
			permission = raw_input("Install libfreetype6-dev? (Y/n): ")
		else:
			permission = True
		
		installed = False
		if not installed:
			if permission == "n" and "--force" not in sys.argv:
				return False
			try:
				if permission:
					# Perfom the actual libfreetype install
					os.system("sudo apt-get install libfreetype6-dev -y")
					return True
				return False
			except:
				return False
		
		return False
	
	def installGearman(self):
		""" Gearman is an integral part of the Server-Worker system. """
		
		if "gearman-job-server" in self.getInstalledPackages():
			return True
		
		print "Installing Gearman job server."		
		installed = False			
		if not installed:
			if "--force" not in sys.argv:
				permission = raw_input("Install Gearman job server? (Y/n): ")
			else:
				permission = True
			if permission == "n" and "--force" not in sys.argv:
				return False
			try:
				# Perfom the actual PySide install
				os.system("sudo apt-get install gearman-job-server")
				return True
			except:
				return False
		return False
	
	def checkIfRoot(self):
		""" Some packages require root privileges to install. """
		return os.geteuid() == 0		   
				
	def run(self):
		""" Overwrite the 'real' run method to install the packages we need. """
		if not self.checkIfRoot() and "--force" not in sys.argv:
			print "You need to be root to install this package, as some dependencies need to be installed."
			print "Run this install with --force as a parameter to try installing without root permissions."
			return False
		
		self.getInstalledPackages()
		
		if not self.installPipRequirements():
			raise Exception, "Not all dependencies installed."
			return False
			
		if "--skip-pyside" in sys.argv:
			if not self.installPySide():
				raise Exception, "Not all dependencies installed."
				return False
		if not self.installLibFreeType():
			raise Exception, "Not all dependencies installed."
			return False
		if not self.installGearman():
			print "Not all dependencies installed."
			raise Exception, "Not all dependencies installed."
		
		# Do the regular install stuff
		install.run(self)			


if __name__ == "__main__":
	# Set the root directory for Olympus
	Config().RootDirectory = os.path.join(os.path.sep.join(os.path.abspath(__file__).split(os.path.sep)[:-1]),"Olympus")
	Config().save()
	
	with open("requirements.txt") as requirements:
		requiredList = requirements.read().split("\n")

	setup(
		name = "Olympus",
		version = Core().getVersion(),
		author = "Stephan Heijl",
		install_requires = requiredList,
		packages=find_packages(),
		cmdclass={
			'install': installNativeDependencies,
		}
	)