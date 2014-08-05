"""
@name WorkerMonitor
@author Stephan Heijl
@module core
@version 0.1.0
"""

import threading, time, gearman, subprocess
import sys, re
from Olympus.lib.Config import Config

# GUI parts #

disableGui = False
try:
	import PySide
	from PySide.QtGui import QApplication, QDesktopWidget
	from PySide.QtWebKit import *
	from PySide.QtCore import QSize, QUrl, Qt
except:
	disableGui = True


class WorkerMonitor(object):
	def __init__(self):
		""" Matches CLI arguments to commands and checks GearmanServer in Config. """
		self.commands = {
			"start" : self.startWorkers,
			"end" : self.endWorker,
			"status" : self.getGearmanStatus,
			"workers" : self.getGearmanWorkers,
			"ping" : self.getGearmanPing
		}
		
		try:
			Config().GearmanServer
		except:
			Config().addAttribute("GearmanServer", "localhost:4730")
			Config().save()

	def startServer(self, daemon=True):
		""" Launch the webapp server. This server is in a separate thread and is used to serve the interface pages. """
		from Olympus.webapp.start import Server
		serverDaemon = Server()
		serverDaemon.daemon = daemon
		self.serverDaemon = serverDaemon
		self.serverDaemon.start()
		
	def getGearmanStatus(self):
		""" Returns the Gearman Server status. """
		try:
			gac = gearman.admin_client.GearmanAdminClient(Config().GearmanServer)
			print gac.get_status()
			return gac.get_status()
		except gearman.admin_client.ServerUnavailable:
			return None
		
	def getGearmanWorkers(self):
		""" Returns the Gearman Server worker data. Only returns workers that have a task assigned to them. """
		print "Getting gearman workers"
		try:
			gac = gearman.admin_client.GearmanAdminClient(Config().GearmanServer)
			workers = filter(lambda w: len(w["tasks"]) > 0, gac.get_workers())
			print "Workers", workers
			return workers
		except gearman.admin_client.ServerUnavailable:
			return None
		
	def getGearmanPing(self):
		""" Returns the Gearman Server response times. """
		try:
			gac = gearman.admin_client.GearmanAdminClient(Config().GearmanServer)
			return gac.ping_server()
		except gearman.admin_client.ServerUnavailable:
			return None
	
	def GUI(self):
		if disableGui:
			return False
		app = QApplication([])
		
		# The Webview
		view = QWebView()
		view.setWindowTitle('Olympus WorkerMonitor')
		url = QUrl("http://127.0.0.1:5000/workermonitor/")
		view.load(url)

		# Set the size
		size = QSize(1024,600)
		view.setMinimumSize(size)
		
		# Set the view in the center of the desktop
		qr = view.frameGeometry()
		cp = QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		view.move(qr.topLeft())
		
		# And starting the app
		view.show()
		app.exec_()
		
	def startNewWorker(self):
		command = "cd %s; cd ..; python -m Olympus.core.Worker" % Config().RootDirectory
		worker = subprocess.Popen(command, shell=True)
		print worker.pid
		return {"pid" : worker.pid}

	def startWorkers(self, n):
		""" This starts `n` number of workers. """
		for w in range(int(n)):
			self.startNewWorker()

	def endWorker(self, id):
		pass

	def setGearmanServer(self, address, port):
		""" This sets the Gearman Server that needs to be monitored. """
		
		# Use default values on empty input
		if address == "":
			address = "localhost"
		if port == "":
			port = "4730"
		
		print "Setting server to %s:%s" % (address, port)
		Config().GearmanServer = ["%s:%s" % (address, port)]
		Config().save()
		return True

if __name__ == "__main__":
	wm = WorkerMonitor()
	if "--gui" in sys.argv:
		wm.startServer()
		wm.GUI()
	for arg in sys.argv[1:]:
		kvArg = re.search("--(\w+)?=(\d+)", arg)
		kArg = re.search("--(\w+)", arg)
		if kvArg != None:
			wm.commands[kvArg.group(1)](kvArg.group(2))
		elif kArg != None:
			print kArg.group(1)
		else:
			raise Exception, "argument '%s' not recognized" % arg


# TESTING #

def test_getGearmanWorkers():
	wm = WorkerMonitor()
	status = wm.getGearmanWorkers()
	assert status == None or isinstance(status, tuple)
	
def test_getGearmanStatus():
	wm = WorkerMonitor()
	status = wm.getGearmanStatus()
	assert status == None or isinstance(status, tuple)
	
def test_getGearmanPing():
	wm = WorkerMonitor()
	status = wm.getGearmanPing()
	assert status == None or status > 0
	
def test_startServer():
	currentCount = threading.activeCount()
	wm = WorkerMonitor()
	wm.startServer()
	time.sleep(5)
	assert threading.activeCount() == currentCount + 1
