"""
@name ToolInterface
@author Stephan Heijl
@module core
@version 0.2.0

This is a stripped down version of the WorkerMonitor, serving only the included tool interface.
"""

import threading, time, subprocess
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
	print "PySide was not installed."
	disableGui = True


class ToolInterface(object):
	def startServer(self, daemon=True):
		""" Launch the webapp server. This server is in a separate thread and is used to serve the interface pages. """
		from Olympus.webapp.start import Server
		serverDaemon = Server()
		serverDaemon.daemon = daemon
		self.serverDaemon = serverDaemon
		self.serverDaemon.start()
	
	def GUI(self):
		if disableGui:
			return False
		app = QApplication([])
		
		# The Webview
		view = QWebView()
		view.setWindowTitle('Olympus ToolInterface')
		url = QUrl("http://127.0.0.1:5000/tool")
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
	ti = ToolInterface()
	ti.startServer()
	ti.GUI()
	

# TESTING #
	
def test_startServer():
	currentCount = threading.activeCount()
	ti = ToolInterface()
	ti.startServer()
	time.sleep(5)
	assert threading.activeCount() == currentCount + 1
