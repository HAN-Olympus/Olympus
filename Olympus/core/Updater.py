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
	def __init__(self):
		self.channel = "Release"
	
	def setChannel(self, channel):
		if not isinstance(channel, str):
			raise TypeError, "Must be a string"
		allowedChannels = [
			"Commit", # This channel will update on every commit
			"Nightly", # This channel will update to the latest passing build of the previous day.
			"Milestone", # This channel will update when a release with a milestone tag is added
			"Release" # This channel will update with every actual version release
		]
		if channel in allowedChannels:
			self.channel = channel
			return True
		else:
			raise ValueError, "Invalid channel '%s'. Pick one of the following: \n*%s" % (channel, "\n*".join(allowedChannels))
			
	def checkTravis(self):
		pass
	
# TESTING #
from nose.tools import raises
	
def test_setChannel():
	u = Updater()
	assert u.setChannel("Commit")
	assert u.setChannel("Nightly")
	assert u.setChannel("Milestone")
	assert u.setChannel("Release")

@raises(ValueError)
def test_setChannelValueFail():
	u = Updater()
	u.setChannel("NotAValidChannel")
	
@raises(TypeError)
def test_setChannelTypeFail():
	u = Updater()
	u.setChannel(1)
