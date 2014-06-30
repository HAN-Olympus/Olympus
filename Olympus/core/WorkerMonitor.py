import threading, time
from Olympus.webapp.start import Server

# GUI parts #
import PyQt4
from PyQt4.QtGui import QApplication, QDesktopWidget
from PyQt4.QtWebKit import *
from PyQt4.QtCore import QSize, QUrl


class WorkerMonitor(object):
	def __init__(self):
		pass	
		
	def startServer(self):
		""" Launch the webapp server. This server is in a separate thread and is used to serve the interface pages. """
		serverDaemon = Server()
		serverDaemon.daemon = True
		serverDaemon.start()
		

	def GUI(self):
		app = QApplication([])
		
		# The Webview
		view = QWebView()
		view.setWindowTitle('Olympus WorkerMonitor')
		url = QUrl("http://127.0.0.1:5000/")
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
		
def test_startServer():
	assert threading.activeCount() == 1
	wm = WorkerMonitor()
	wm.startServer()
	time.sleep(5)
	assert threading.activeCount() == 2