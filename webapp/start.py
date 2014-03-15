from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from olympus_web import *

print ("Starting Olympus Tornado HTTP Server")
print ("------------------------------------")
PORT = 5000
print ("Starting on port %s..." % PORT)

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(PORT)
IOLoop.instance().start()