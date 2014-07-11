"""
@name Webapp start
@author Stephan Heijl
@module core
@version 0.0.3
"""

import os, threading
from Olympus.lib.Config import Config
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from Olympus.webapp import app
from flask.ext.compress import Compress

class Server(threading.Thread):
	def checkWorkingDirectory(self):
		""" Checks the working directory and sets it to the webapp directory if needed. """
		print ("Current working directory: '%s'" % os.getcwd())
		startScriptDir = os.path.dirname(os.path.realpath(__file__))
		print ("Desired working directory: '%s'" % startScriptDir)
		if (os.getcwd() != startScriptDir):
			print("Changing working directory to: '%s'" % startScriptDir)
			os.chdir(startScriptDir)
		
	
	def storeWebAppDirectories(self):
		""" Stores the webapp directories into the config. """
		Config().WebAppDirectory = os.path.join(os.getcwd())
		Config().TemplatesDirectory = os.path.join(os.getcwd(), "templates") 
		Config().save()

	def startCompressed(self):
		""" This is a version of the server optimized for remote ends. The plaintext data is compressed before it is sent out for better transfer speeds."""
		
		print ("Starting Olympus Tornado HTTP Server")
		print ("------------------------------------")
		Config() # Initialize the Config before switching to the webapp directory to make sure it gets loaded correctly.

		self.checkWorkingDirectory()	
		self.storeWebAppDirectories()	

		PORT = 5000
		print ("Starting on port %s..." % PORT)

		# Compress all plaintext communications
		Compress(app)
		app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript', 'image/svg+xml']
		app.config['COMPRESS_DEBUG'] = True

		http_server = HTTPServer(WSGIContainer(app))
		http_server.listen(PORT)
		IOLoop.instance().start()

	def startLocal(self):
		print ("Starting Olympus Tornado HTTP Server (LOCAL)")
		print ("--------------------------------------------")
		Config() # Initialize the Config before switching to the webapp directory to make sure it gets loaded correctly.

		self.checkWorkingDirectory()	
		self.storeWebAppDirectories()	

		PORT = 5000
		print ("Starting on port %s..." % PORT)

		http_server = HTTPServer(WSGIContainer(app))
		http_server.listen(PORT)
		IOLoop.instance().start()
		
	def run(self):
		self.startLocal()
	
if __name__ == "__main__":
	Server().startLocal()
	
	
# TESTS #

def test_checkWorkingDirectory():
	s = Server()
	s.checkWorkingDirectory()
	startScriptDir = os.path.dirname(os.path.realpath(__file__))
	assert startScriptDir == os.getcwd() , "Something went wrong whilst changing working directories."
	
def test_storeWebAppDirectories():
	s = Server()
	s.storeWebAppDirectories()
	assert hasattr(Config(), "RootDirectory")