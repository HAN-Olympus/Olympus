"""
@name AcquisitionModule
@author Stephan Heijl
@module core
@version 0.2.0

Acquisition base class.

Abstract class that provides base classes and access to classes in the ../lib directory
Uses part of the additionalImport script to allow access to the lib classes.
Refer to the page on Acquisition modules for a list of modules distributed with this version of Olympus.
"""

from Olympus.lib.Module import Module
import datetime

class AcquisitionModule(Module):
	""" Base class for all acquisition modules. Provides some generic methods. """
	
	def __init__(self):
		""" Does nothing. """
		pass
	
	def convertDateToNative(self, day, month, year):
		"""Convert a day, month, year notation to a Python datetime object
		
		:param day: Numeric, the day (1-31)
		:param month: Numeric, the month (1-12)
		:param year: Numeric, the year
		:rtype: A properly formed datetime object
		"""
		
		dt = datetime.datetime(int(year), int(month), int(day))
		return dt
