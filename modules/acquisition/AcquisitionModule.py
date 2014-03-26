""" Acquisition base class 
Abstract class that provides base classes and access to classes in the ../lib directory
Uses part of the additionalImport script to allow access to the lib classes.
"""
# Add the ../lib directory to the system path
import os, sys
currentDir = os.path.dirname(__file__)
relLibDir = currentDir + "/../../lib"
absLibDir = os.path.abspath(relLibDir)
sys.path.insert(0, absLibDir)

# Library classes are now accessible
import Module
import datetime

class AcquisitionModule(Module.Module):
	""" Base class for all acquisition modules. Provides some generic methods. """
	
	def __init__(self):
		pass
	
	def convertDateToNative(self, day, month, year):
		"""Convert a day, month, year notation to a Python datetime object
		@param day	: Numeric, the day (1-31)
		@param month	: Numeric, the month (1-12)
		@param year	: Numeric, the year
		@returns		: A properly formed datetime object
		"""
		
		dt = datetime.datetime(int(year), int(month), int(day))
		return dt