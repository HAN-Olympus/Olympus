import os
from Olympus.lib.Config import Config
from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from Olympus.webapp import app
from flask.ext.compress import Compress

def checkWorkingDirectory():
	print ("Current working directory: '%s'" % os.getcwd())
	startScriptDir = os.path.dirname(os.path.realpath(__file__))
	print ("Desired working directory: '%s'" % startScriptDir)
	if (os.getcwd() != startScriptDir):
		print("Changing working directory to: '%s'" % startScriptDir)
		os.chdir(startScriptDir)
		
# STORE THE WEBAPP DIRECTORIES IN THE CONFIG #
def storeWebAppDirectories():
	Config().RootDirectory = os.path.abspath(os.getcwd())
	Config().WebAppDirectory = os.path.join(os.getcwd())
	Config().TemplatesDirectory = os.path.join(os.getcwd(), "templates") 
	Config().save()

def start():
	print ("Starting Olympus Tornado HTTP Server")
	print ("------------------------------------")
	Config() # Initialize the Config before switching to the webapp directory to make sure it gets loaded correctly.
		
	checkWorkingDirectory()	
	storeWebAppDirectories()	

	PORT = 5000
	print ("Starting on port %s..." % PORT)
	
	# Compress all plaintext communications
	Compress(app)
	app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/xml', 'application/json', 'application/javascript', 'image/svg+xml']
	app.config['COMPRESS_DEBUG'] = True

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
	
def test_storeWebAppDirectories():
	storeWebAppDirectories()
	assert hasattr(Config(), "RootDirectory")