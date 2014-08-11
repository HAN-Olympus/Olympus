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
import subprocess
from pprint import pprint as pp 
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
			conn.privmsg(self.channel, "Thank you, Travis.")
			if self.handle_travis_message(message):
				conn.privmsg(self.channel, "Will update.")
			else:
				conn.privmsg(self.channel, "Will not update.")
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
		
	def parseTravisBuildResult(self, message):
		""" This function parses message from Travis-CI. """ 
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
		
	def handle_travis_message(self, message):
		""" This should handle messages from Travis. """
		buildResult = self.parseTravisBuildResult(message)		
		if buildResult != None:
			return self.doUpdateIfAppropiate(buildResult)
		return False
		
	def doUpdateIfAppropiate(self, buildResult):
		""" Will pull the repo if an update is appropiate according to the channel. """
		u = Updater()
		args = ["", buildResult["branch"], buildResult["shorthash"], buildResult["state"]]
		print args
		print u.channel
		if u.checkAppropiateUpdateForChannel(*args):
			print u.checkAppropiateUpdateForChannel(*args)
			u.gitPull()
			u.restartServer()
			return True
		return False
		
	def makeUserName(self):
		""" Produces a hex username based on the MAC address of this machine. """
		mac = get_mac()
		return "".join(chr(int(l) + ord('a')) for l in str(mac))

# UPDATER #
		
class Updater():
	""" This class is responsible for updating the Olympus app. 
		It can be run as a service or used periodically.
		Running it as a service means that it will update the proper channel every time a matching commit has been pushed.
		It will listen on an Updater IRC Channel
	"""
	def __init__(self):
		self.channel = Config().UpdateChannel
		self.travisBuilds = None
		self.travisCommits = None
		self.commits = None
	
	def setChannel(self, channel):
		""" Sets the updating channel for this distribution of Olympus.
		
		:param channel: A string that defines the channel. Should be one of the following: Mirror, Commit, Nightly, Milestone, Release
		"""
		if not isinstance(channel, str):
			raise TypeError, "Must be a string"
		allowedChannels = [
			"Mirror", # This channel will update on ANY commit, even if it does not pass the Travis-CI inspection.
			"Commit", # This channel will update on every passing commit
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
		self.travisBuilds = result['builds']
		self.travisCommits = result['commits']
			
	def getTravisBuilds(self):
		""" Gets the latest commit details for this Olympus distrubution. """
		if self.travisBuilds == None:
			self.__queryTravisBuilds()
		return self.travisBuilds
	
	def getTravisCommits(self):
		""" Gets the latest build details for this Olympus distrubution. """
		if self.travisCommits == None:
			self.__queryTravisBuilds()
		return self.travisCommits
	
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
	
	def getDataByHashTravis(self, hash):
		""" Retrieves data from Travis on the given hash. If it does not exist, the current version is at least 25 commits behind. """
		commits = self.getTravisCommits()
		builds = self.getTravisBuilds()
		for c in range(len(commits)):
			commit = commits[c]
			if commit['sha'] == hash or commit['sha'].startswith(hash):
				result = dict( commit.items() + builds[c].items() )
				result["commits_behind"] = c
				return result
		return {"commits_behind":-1}
	
	def getAllCommitsGithub(self):
		""" Will attempt to retrieve all the GitHub commits. """
		if self.commits != None:
			return self.commits
		g = Github();
		repository = g.get_repo(Config().OlympusRepo)
		self.commits = repository.get_commits(since=datetime.datetime.now()-datetime.timedelta(days=1))
		return self.commits
	
	def getDataByHashGithub(self, hash):
		commits = self.getAllCommitsGithub() 
		for commit in commits:
			c = commit.commit
			if c.sha == hash or c.sha.startswith(hash):
				details = {
							"sha":c.sha,
							"author":c.author,
							"files":commit.files,
							"commit-message":c.message
							}
				return details
	
	def getAllDataForHash(self, hash):
		data = self.getDataByHashTravis(hash).items()
		data+= self.getDataByHashGithub(hash).items()
		return dict(data)
	
	def getCurrentCommitDetails(self):
		""" Retrieves data from Travis and Github on the current version of Olympus. """
		currentCommitHash = self.getCurrentCommitHash()
		return self.getAllDataForHash(currentCommitHash)
			
	def gitPull(self):
		""" Performs a git pull in the repo root. """
		gitDir = os.path.join(Config().RootDirectory, "..", ".git")
		if not os.path.exists(gitDir):
			raise Exception, "This is not a git repository. Cannot pull. "
		p = subprocess.Popen("cd %s; cd ..; git pull" % Config().RootDirectory, shell=True, stdout=subprocess.PIPE)
		print p.communicate()
		
	def restartServer(self):
		""" Restarts the server. Calls the stopServer and startServer scripts. """
		print "Stopping Olympus server."
		stopping = subprocess.Popen("cd %s; cd ..; bash stopServer.sh;" % Config().RootDirectory, shell="True")
		stopping.communicate()
		print "Starting Olympus server."
		stopping = subprocess.Popen("cd %s; cd ..; bash startServer.sh;" % Config().RootDirectory, shell="True")
		stopping.communicate()
		print "Restart successfull."
		return True
		
		
	def checkAppropiateUpdateForChannel(self, message, branch, hash, state):
		""" This function attempts to determine whether or not a given commit is appropiate for the set channel according to its properties. """
		if self.channel == "Mirror":
			# The mirror channel will always update.
			return True
		if self.channel == "Commit":
			# The Commit channel will pull any commit that passes the travis-ci build
			return state
		if self.channel == "Nightly":
			return True			
		if self.channel == "Milestone":
			# The Milestone channel will pull any working commit from a Milestone channel
			return state and ("milestone" in branch.lower() or "<milestone>" in message.lower())
		if self.channel == "Release":
			# The Milestone channel will pull any working commit from a Milestone channel
			return state and ("release" in branch.lower() or "<release>" in message.lower())
		
		
# TESTING UPDATER #
from nose.tools import raises

def test_setChannel():
	u = Updater()
	assert u.setChannel("Mirror")
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
	
def test_getDataByHashTravis():
	u = Updater()
	assert u.getDataByHashTravis("adwjdijaidjiawjdij")['commits_behind'] == -1
	
def test_getCurrentCommitDetails():
	u = Updater()
	u.getCurrentCommitDetails()['commits_behind']
	
def test_getAllCommitsGithub():
	u = Updater()
	u.getAllCommitsGithub()

def test_checkAppropiateUpdateForChannel():
	u = Updater()
	# Test data formatted like so:
	# ( Branch, (list of arguments for checkAppropiateUpdateForChannel() ), Expected Value)
	test_data = [
		( "Mirror", ("","","",True), True ),
		( "Mirror", ("","","",False), True ),
		( "Commit", ("","","",True), True ),
		( "Commit", ("","","",False), False ),

		# Make test cases for nightly
		( "Nightly", ("","","",False), True ),
		# //
		
		( "Milestone", ("","Milestone","",False), False ),
		( "Milestone", ("","Milestone","",True), True ),
		( "Milestone", ("","Regular","",True), False ),
		( "Milestone", ("<Milestone>","Milestone","",True), True ),
		( "Milestone", ("<Milestone>","Regular","",True), True ),
		( "Milestone", ("<milestone>","Regular","",True), True ),
		( "Milestone", ("<Milestone>","Regular","",False), False ),

		( "Release", ("","Release","",False), False ),
		( "Release", ("","Release","",True), True ),
		( "Release", ("","Regular","",True), False ),
		( "Release", ("<Release>","Release","",True), True ),
		( "Release", ("<Release>","Regular","",True), True ),
		( "Release", ("<Release>","Regular","",True), True ),
		( "Release", ("<Release>","Regular","",False), False ),
	]
	for channel, args, result in test_data:
		u.setChannel(channel)
		assert u.checkAppropiateUpdateForChannel(*args) == result

def test_gitPull():
	u = Updater()
	u.gitPull()

# TESTING IRC #

def test_makeUserName():
	i = IRCClient()
	assert re.match( "^[a-z]+$", i.makeUserName() )
	
def test_parseTravisBuildResult():
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
		response = i.parseTravisBuildResult(message)
		if expected:
			assert response['state']
		if expected == False:
			assert not response['state']
		if expected == None:
			assert response == None


# Start the Updater #
if __name__ == "__main__":
	bot = IRCClient().start()