from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import os

def checkWorkingDirectory():
	print ("Current working directory: '%s'" % os.getcwd())
	startScriptDir = os.path.dirname(os.path.realpath(__file__))
	print ("Desired working directory: '%s'" % startScriptDir)
	if (os.getcwd() != startScriptDir):
		print("Changing working directory to: '%s'" % startScriptDir)
		os.chdir(startScriptDir)

def start():
	print ("Starting Olympus Tornado HTTP Server")
	print ("------------------------------------")
	checkWorkingDirectory()
	
	from Olympus.lib.Config import Config
	from Olympus.webapp import svglib
	
	print globals()
	

	PORT = 5000
	print ("Starting on port %s..." % PORT)

	http_server = HTTPServer(WSGIContainer(app))
	http_server.listen(PORT)
	IOLoop.instance().start()

	
if __name__ == "__main__":
	start()
	
	
# TESTS #

def test_checkWorkingDirectory():
	checkWorkingDirectory()
	startScriptDir = os.path.dirname(os.path.realpath(__file__))
	assert startScriptDir == os.getcwd() , "Something went wrong whilst changing working directories."