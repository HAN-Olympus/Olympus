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
import datetime
import re
from irc.bot import SingleServerIRCBot, ServerSpec
from uuid import getnode as get_mac
from github import Github
from pprint import pprint as pp
from Olympus.lib.Config import Config
from threading import Timer


class IRCClient(SingleServerIRCBot):
	""" This class allows the updater to connect to IRC for live updates. It subclasses the irc SingleServerIRCBot """
	def __init__(self):
		""" This initializes the bot with Config values. """
		server, channel = Config().UpdateServer.split("#")
		host, port = server.split(":")
		SingleServerIRCBot.__init__(self, [(host,int(port))], self.makeUserName(), "OlympusIRCUpdater" )
		self.channel = "#" + channel
		self.connection.buffer_class.errors = 'replace'
		self.ping_interval = 60
		print "Connecting to the update server. This might take some time..."
		print "-------------------------------------------------------------"

	def on_welcome(self, conn, event):
		""" This is executed when the client connects and recieves the welcome message. """
		conn.join(self.channel)
		
	def on_join(self, conn, event):
		""" This is executed when the client joins the channel. """
		print "Succesfully joined %s." % self.channel
		
	def on_pubmsg(self, conn, event):
		""" Handles all the public messages sent to the channel. """
		message = event.arguments[0]
		source = event.source.split("!")[0] # Gets the username of the sender
		print source, message
		if source.lower() == "travis-ci":
			self.handle_travis_message(message)
			conn.privmsg(self.channel, "Thank you, Travis.")
			
	def on_disconnect(self, conn, event):
		self.routine_ping(first_run = True)
		self.__init__()
	
	def routine_ping(self, first_run = False):
		""" Ping server to know when try to reconnect to a new server. """
		global pinger
		if not first_run and not self.pong_received:
			print "Ping reply timeout, disconnecting from", self.connection.get_server_name()
			self.disconnect()
			return
		self.pong_received = False
		self.connection.ping(self.connection.get_server_name())
		pinger = Timer(self.ping_interval, self.routine_ping, ())
		pinger.start()
		
	def on_pong(self, connection, event):
		""" React to pong. """
		self.pong_received = True
		
	def handle_travis_message(self, message):
		""" This should handle and parse messages from Travis. """
		msg = message.split(" ")
		pattern = "([\w\-\/]+?)#(\d+?) \((\w+) - (\w+) : [\w ]+\): The build ([\w ]+)\.?"
		result = re.search(pattern, message)
		if result!=None:
			buildResult = {
				"repo":result.group(1),
				"build":result.group(2),
				"branch":result.group(3),
				"shorthash":result.group(4),
				"state": ("fixed" in result.group(5) or "passed" in result.group(5)) # True or false based on the contents of the state message
			}
		else:
			buildResult=None
		return buildResult
		
	def makeUserName(self):
		""" Produces a hex username based on the MAC address of this machine. """
		mac = get_mac()
		return "".join(chr(int(l) + ord('a')) for l in str(mac))
	
if __name__ == "__main__":
	bot = IRCClient().start()
	
# TESTING IRC #

def test_makeUserName():
	i = IRCClient()
	assert re.match( "^[a-z]+$", i.makeUserName() )
	
def test_handle_travis_message():
	messages = [
		("HAN-Olympus/Olympus#237 (master - c879119 : Stephan Heijl): The build was fixed.", True),
		("HAN-Olympus/Olympus#238 (master - 12d5201 : StephanHeijl): The build passed.", True),
		("HAN-Olympus/Olympus#236 (master - a96c4cb : Stephan Heijl): The build is still failing.", False),
		("Test message", None),
		("Change view : https://github.com/HAN-Olympus/Olympus/compare/ea638702475a...a96c4cb9fe9c ", None),
		("Build details : http://travis-ci.org/HAN-Olympus/Olympus/builds/32119430", None)
	]
	i = IRCClient()
	for message,expected in messages:
		response = i.handle_travis_message(message)
		if expected == True:
			assert response["state"]
		if expected == False:
			assert not response["state"]
		if expected == None:
			assert response == None

# UPDATER #
		
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
			contents = headFile.read().strip("\n")
		if os.path.sep in contents:
			refPath = os.path.join(gitDir,contents[5:])
			with open(refPath, "r") as ref:
				hash = ref.read().strip(" \n")
		else:
			hash = contents
		return hash
	
	def getDataByHash(self, hash):
		""" Retrieves data from Travis on the given hash. If it does not exist, the current version is at least 25 commits behind. """
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
	
	def getAllCommits(self):
		g = Github();
		repository = g.get_repo(Config().OlympusRepo)
		for commit in repository.get_commits(since=datetime.datetime.now()-datetime.timedelta(days=1)):
			print commit.sha
			pp(commit.commit.message)
			print "-"*20
	
# TESTING UPDATER #
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
	
def test_getDataByHash():
	u = Updater()
	assert u.getDataByHash("a")['commits_behind'] == -1
	
def test_getCurrentCommitDetails():
	u = Updater()
	u.getCurrentCommitDetails()['commits_behind']
	
def test_getAllCommits():
	u = Updater()
	u.getAllCommits()
