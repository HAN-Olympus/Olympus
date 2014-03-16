# Acquisition base class 
# Abstract class that provides base classes and access to classes in the ../lib directory


# Add the ../lib directory to the system path
import os, sys
currentDir = os.path.dirname(__file__)
relLibDir = currentDir + "/../../lib"
absLibDir = os.path.abspath(relLibDir)
sys.path.insert(0, absLibDir)


# Library classes are now accessible
import Module

class AcquisitionModule(Module.Module):
	
	def __init__(self, arg1, arg2):
		pass