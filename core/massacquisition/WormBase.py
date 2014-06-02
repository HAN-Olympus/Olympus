from Olympus.lib.StoredObject import StoredObject
import ftputil
import os
import hashlib

class WormBase(object):
	""" A mass acquisition class for WormBase. """
	
	# DOWNLOADING #
	
	def __init__(self):
		""" Sets some instance wide variables. """
		self.connection = None
		self.url = "ftp.wormbase.org"
		self.tmpPath = "/tmp/"
		self.currentReleasePath = "/pub/wormbase/releases/current-development-release"
		self.checksumPath = "/pub/wormbase/releases/current-development-release/CHECKSUMS"
		#self.species = ["a_ceylanicum","c_elegans"]
		self.species = ["c_elegans"]
		self.dryrun = False
		self.checksums = None
		
	def checkConnection(self):
		if self.connection != None:
			return True
		else:
			raise Exception, "The connection has not yet been initiated."
	
	def connect(self):
		connection = ftputil.FTPHost(self.url, "anonymous", "")
		self.connection = connection
	
	def createChunkyHash(self, f, blockSize=2**20):
		""" Returns the MD5 checksum of the given file, created by feeding the file in chunks to the hashlib module. 
			This reduces memory usage at the cost of some speed. blockSize can be increased to speed up this process. 
			
			:param f: A filelike object
			:param blockSize: The size of the chunks in which the file needs to be read. Defaults to 1MB chunks.
			:rtype: An MD5 checksum.
			"""
		md5 = hashlib.md5()
		while True:
			data = f.read(blockSize)
			if not data:
				break
			md5.update(data)
		return md5.hexdigest()

	def retreiveChecksums(self):
		""" Retreives the most current CHECKSUMS file and returns it as a dictionary mapped as {file:checksum, ... }.
		Will only retrieve a new version if it hasn't already checked for this instance. """
		
		if self.checksums != None:
			return self.checksums
		
		self.checkConnection()
		CHECKSUMSFILE = self.connection.open(self.checksumPath)
		checksums = {}
		line = CHECKSUMSFILE.readline()
		while line:
			value, key = str(line).strip().split("  ")
			checksums[key] = value
			line = CHECKSUMSFILE.readline()
		
		self.checksums = checksums
		
		return checksums
		

	def checkChecksum(self, file, local=None):
		""" Checks the checksum of a file from FTP with the latest CHECKSUMS file by creating a checksum for the given file and comparing it.
		
		:param file: The file in the FTP structure
		:param local: Optional, the location of the file in the local filesystem. Defaults to the temporary directory joined with the given file.
		:rtype: Boolean. Returns True if the file's checksums match. Returns False if they don't or if the file specified could not be found in the checksums file.
		"""
		if local == None:
			local = os.path.join(self.tmpPath, file)	
		
		f = open(local, "rb")
		checksum = self.createChunkyHash(f)
		
		try:
			expectedChecksum = self.retreiveChecksums()[file]
		except KeyError:
			return False
		return checksum == expectedChecksum
	
	def downloadCurrentRelease(self):
		""" Downloads the most current release of the WormBase directory. 
		Will only download species from the `species` folder that are given in `WormBase.species`. 
		Downloads will be written to `WormBase.tmpPath/WormBaseCurrentRelease`. 
		Skips files that already exist and who's checksums are successfully matched to the remote checksums.
		"""
		
		self.checkConnection()
		
		self.connection.chdir(self.currentReleasePath)
		
		tmpPath = os.path.join(self.tmpPath, "WormBaseCurrentRelease")
		
		speciesDir = self.connection.listdir("species")
		speciesCount = len(speciesDir)
		
		# Check and download all the species specified
		for root, path, files in self.connection.walk("species"):
			if True in [s in root for s in self.species]:
				targetDir = os.path.join(tmpPath, root)
				if not os.path.exists(targetDir):
					os.makedirs(targetDir)

				for file in files:				
					target = os.path.join(tmpPath, root, file)
					
					if ( os.path.exists(target) and self.checkChecksum( os.path.join(root, file),target ) ) or self.dryrun:
						# Skip files that have already downloaded correctly
						print "Skipping %s" % (file)
						continue
						
					print "Downloading %s to %s" % (file, target)
					self.connection.download( os.path.join(root, file) , target)
					
	# UNPACKING #
	
	def unpackFiles(self):
		pass
	
	# PARSING TO STOREDOBJECTS #
	
	
		
		
# TESTING # 
from nose.tools import raises

def test_connect():
	wb = WormBase()
	wb.connect()
	assert wb.connection != None

def test_checkConnection():
	wb = WormBase()
	wb.connect()
	assert wb.checkConnection()
	
@raises(Exception)
def test_checkConnection_failure():
	wb = WormBase()
	wb.checkConnection()
	
def test_retreiveChecksums():
	wb = WormBase()
	wb.connect()
	wb.retreiveChecksums()

def test_createChunkyHash():
	# Create a test file
	tfpath = "/tmp/testfile.tmp"
	tf = open(tfpath , "w")
	tf.write("testfile")
	tf.close()
	
	wb = WormBase()
	expectedChecksum = "8bc944dbd052ef51652e70a5104492e3" 
	checksum = wb.createChunkyHash( open(tfpath, "rb") )
	assert checksum == expectedChecksum
	
def test_checkChecksum():
	wb = WormBase()
	
	# Create a test file
	tfpath = os.path.join( "/tmp/testfile.tmp")	
	tf = open(tfpath , "w")
	tf.write("testfile")
	tf.close()
	
	wb.checksums = {"testfile.tmp":"8bc944dbd052ef51652e70a5104492e3"}
	assert wb.checkChecksum("testfile.tmp")
	
def test_downloadCurrentRelease():
	wb = WormBase()
	wb.connect()
	wb.dryrun = True
	#wb.downloadCurrentRelease()