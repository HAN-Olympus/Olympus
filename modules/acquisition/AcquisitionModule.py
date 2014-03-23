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
import datetime

class AcquisitionModule(Module.Module):
	
	def __init__(self):
		pass
		
	# Convert Pubmeds day, month, year notation to a python datetime object
	# @param day	: Numeric, the day (1-31)
	# @param month	: Numeric, the month (1-12)
	# @param year	: Numeric, the year
	# @returns		: A properly formed datetime object
	def convertDateToNative(self, day, month, year):
		dt = datetime.datetime(int(year), int(month), int(day))
		return dt