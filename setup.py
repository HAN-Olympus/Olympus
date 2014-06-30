from setuptools import setup, find_packages
from setuptools.command.install import install
from Olympus.core.Core import Core
from Olympus.lib.Config import Config
import os, sys, re
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
    
    def installPyQT4(self):
        """ We install PyQT4 for the user interface. """
        print "Installing PyQT4"
        
        if "python-qt4" in self.getInstalledPackages():
            return True
        
        installed = False
        try:
            import PyQT4
            # Might add some extra version validation here.
            installed = True
        except:           
            installed = False
            
        if not installed:
            if "--force" not in sys.argv:
                permission = raw_input("Install PyQT4? (Y/n): ")
            else:
                permission = True
            if permission == "n":
                return False
            try:
                # Perfom the actual PyQT4 install
                os.system("sudo apt-get install -y python-qt4")
                return True
            except:
                return False
        
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
            permission = raw_input("Install LibFreeType? (Y/n): ")
            if permission == "n" and "--force" not in sys.argv:
                return False
            try:
                # Perfom the actual PySide install
                os.system("sudo apt-get install libfreetype6-dev")
                return True
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
        
        print self.getInstalledPackages()
        
        if not self.installPyQT4():
            print "Not all dependencies installed."
            return False
        if not self.installLibFreeType():
            print "Not all dependencies installed."
            return False
        if not self.installGearman():
            print "Not all dependencies installed."
            return False
        
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