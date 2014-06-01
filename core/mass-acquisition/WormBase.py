from Olympus.lib.StoredObject import StoredObject
import ftputil
import os

class WormBase():

	def __init__(self):
		self.connection = None
		self.url = "ftp.wormbase.org"
		self.tmpPath = "/tmp/"
		self.currentReleasePath = "/pub/wormbase/releases/current-development-release"
		self.species = ["a_ceylanicum","c_elegans"]
		
	def checkConnection(self, function):
		if self.connection != None:
			return True
		else:
			raise ValueError
	
	def connect(self):
		connection = ftputil.FTPHost(self.url, "anonymous", "")
		self.connection = connection
	
	def getFile(self, file):
		self.checkConnection()
		
	def checkChecksums(self):
		pass
		
	def checkDownload(self):
		pass
	
	def downloadCurrentRelease(self):
		self.connection.chdir(self.currentReleasePath)
		
		tmpPath = os.path.join(self.tmpPath, "WormBaseCurrentRelease")
		
		speciesDir = self.connection.listdir("species")
		print speciesDir
		speciesCount = len(speciesDir)
		counter = 1
		
		# Download all the species specified
		for root, path, files in self.connection.walk("species"):
			
			if True in [s in root for s in self.species]:
				targetDir = os.path.join(tmpPath, root)
				if not os.path.exists(targetDir):
					os.makedirs(targetDir)

				for file in files:				
					target = os.path.join(tmpPath, root, file)
					print "Downloading %s to %s" % (file, target)

					self.connection.download( os.path.join(root, file) ,target)

				counter += 1
	
		
		
# TESTING # 

def test_connect():
	wb = WormBase()
	wb.connect()
	assert wb.connection != None
	
def test_downloadCurrentRelease():
	wb = WormBase()
	wb.connect()
	wb.downloadCurrentRelease()