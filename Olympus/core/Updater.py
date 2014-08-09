"""
@name Updater
@author Stephan Heijl
@module core
@version 0.3.0

The Updater relies on an IRC channel for the service portion.
You will not need to worry about this if you are only running the updater periodically.

If you have forked Olympus and do not wish to receive updates 
"""


class Updater():
	""" This class is responsible for updating the Olympus app. 
		It can be run as a service or used periodically.
		Running it as a service means that it will update the proper channel every time a matching commit has been pushed.
		It will listen on an Updater IRC Channel
	"""
	
	def setChannel(self, channel):
		allowedChannels = [
			"Commit", # This channel will mean an update on any commit
		]
