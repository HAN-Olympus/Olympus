import threading, time, gearman

# GUI parts #

disableGui = False
try:
	import PySide
	from PySide.QtGui import QApplication, QDesktopWidget
	from PySide.QtWebKit import *
	from PySide.QtCore import QSize, QUrl
except:
	disableGui = True


class WorkerMonitor(object):
	def __init__(self):
		pass	
		
	def startServer(self):
		""" Launch the webapp server. This server is in a separate thread and is used to serve the interface pages. """
		from Olympus.webapp.start import Server
		serverDaemon = Server()
		serverDaemon.daemon = True
		serverDaemon.start()
		
	def getGearmanStatus(self):
		""" Returns the Gearman Server status. """
		try:
			gac = gearman.admin_client.GearmanAdminClient(['localhost:4730'])
			return gac.get_status()
		except gearman.admin_client.ServerUnavailable:
			return None
		
	def getGearmanWorkers(self):
		""" Returns the Gearman Server worker data. """
		try:
			gac = gearman.admin_client.GearmanAdminClient(['localhost:4730'])
			return gac.get_workers()
		except gearman.admin_client.ServerUnavailable:
			return None
		
	def getGearmanPing(self):
		""" Returns the Gearman Server response times. """
		try:
			gac = gearman.admin_client.GearmanAdminClient(['localhost:4730'])
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
		
if __name__ == "__main__":
	wm = WorkerMonitor()
	wm.startServer()
	wm.GUI()

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
	assert threading.activeCount() == 1
	wm = WorkerMonitor()
	wm.startServer()
	time.sleep(5)
	assert threading.activeCount() == 2
