from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from olympus_web import *
import os

print ("Starting Olympus Tornado HTTP Server")
print ("------------------------------------")
print ("Current working directory: '%s'" % os.getcwd())
startScriptDir = os.path.dirname(os.path.realpath(__file__))
print ("Desired working directory: '%s'" % startScriptDir)
if (os.getcwd() != startScriptDir):
	print("Changing working directory to: '%s'" % startScriptDir)
	os.chdir(startScriptDir)

PORT = 5000
print ("Starting on port %s..." % PORT)


http_server = HTTPServer(WSGIContainer(app))
http_server.listen(PORT)
IOLoop.instance().start()