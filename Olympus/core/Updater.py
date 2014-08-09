"""
@name Updater
@author Stephan Heijl
@module core
@version 0.3.0

The Updater relies on an IRC channel for the service portion.
You will not need to worry about this if you are only running the updater periodically.

If you have forked Olympus and do not wish to receive updates 
"""

import os
import requests
import json
from pprint import pprint as pp
from Olympus.lib.Config import Config

class Updater():
	""" This class is responsible for updating the Olympus app. 
		It can be run as a service or used periodically.
		Running it as a service means that it will update the proper channel every time a matching commit has been pushed.
		It will listen on an Updater IRC Channel
	"""
	def __init__(self):
		self.channel = "Release"
		self.builds = None
		self.commits = None
	
	def setChannel(self, channel):
		""" Sets the updating channel for this distribution of Olympus.
		
		:param channel: A string that defines the channel. Should be one of the following: Commit, Nightly, Milestone, Release
		"""
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
			
	def __queryTravisBuilds(self):
		""" Queries Travis.ci for data on this repository. """
		buildsUrl = "https://api.travis-ci.org/repos/" + Config().OlympusRepo + "/builds"
		r = requests.get(buildsUrl,headers={"Accept":"application/vnd.travis-ci.2+json"})
		result = json.loads(r.text)
		self.builds = result['builds']
		self.commits = result['commits']
			
	def getTravisBuilds(self):
		""" Gets the latest commit details for this Olympus distrubution. """
		if self.builds == None:
			self.__queryTravisBuilds()
		return self.builds
	
	def getTravisCommits(self):
		""" Gets the latest build details for this Olympus distrubution. """
		if self.commits == None:
			self.__queryTravisBuilds()
		return self.commits
	
	def getCurrentCommitHash(self):
		""" Will retrieve the current commit hash from the .git directory. """
		gitDir = os.path.join(Config().RootDirectory, "..", ".git")
		headPath = os.path.join(gitDir, "HEAD")
		with open(headPath, "r") as headFile:
			refPath = headFile.read().strip("\n")[5:]
		
		refPath = os.path.join(gitDir,refPath)
		with open(refPath, "r") as ref:
			hash = ref.read().strip(" \n")
		return hash
	
	def getDataByHash(self, hash):
		""" Retrieves data from Travis on the given hash.  If this returns None, the current version is at least 25 commits behind. """
		commits = self.getTravisCommits()
		builds = self.getTravisBuilds()
		for c in range(len(commits)):
			commit = commits[c]
			if commit['sha'] == hash:
				result = dict( commit.items() + builds[c].items() )
				result["commits_behind"] = c
				return result
		return {"commits_behind":-1}
	
	def getCurrentCommitDetails(self):
		""" Retrieves data from Travis on the current version of Olympus. """
		currentCommitHash = self.getCurrentCommitHash()
		data = self.getDataByHash(currentCommitHash)
		print data
		return data		
		
	
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
	
def test_getCurrentCommitHash():
	u = Updater()
	assert len( u.getCurrentCommitHash() ) == 40
	
def test_getTravisBuilds():
	u = Updater()
	assert len( u.getTravisBuilds() ) == 25
	
def test_getTravisCommits():
	u = Updater()
	assert len( u.getTravisBuilds() ) == 25

def test_getCurrentCommitDetails():
	u = Updater()
	u.getCurrentCommitDetails()
	