"""
@name PFAM
@author Stephan Heijl
@module PFAM
@version 0.1.0
"""

from Olympus.lib.StoredObject import StoredObject
from Olympus.lib.Protein import Protein
from Olympus.lib.CodingSequence import CodingSequence
import ftputil

class PFAM(object):
	""" A mass acquisition class for WormBase. """
	
	# DOWNLOADING #
	
	def __init__(self):
		""" Sets some instance wide variables. """
		self.connection = None
		self.url = "ftp.ebi.ac.uk/pub/databases/Pfam/"
		self.tmpPath = "/tmp/"
		self.currentReleasePath = "/pub/databases/Pfam/current_release"
		self.dryrun = False
		
		self.verbose = True
		
	def checkConnection(self):
		""" Checks whether or not a connection with the FTP server has been established. """
		if self.connection != None:
			return True
		else:
			raise Exception, "The connection has not yet been initiated."
	
	def connect(self):
		""" Connects to the FTP server as specified by `self.url`. """
		connection = ftputil.FTPHost(self.url, "anonymous", "")
		self.connection = connection
		
	def downloadCurrentRelease(self):
		""" Downloads the most current release of the PFAM database. 
		Will download the full 'Pfam-A.full.gz' database file.
		Downloads will be written to `PFAM.tmpPath/PFAMCurrentRelease`.
		"""
		
		self.checkConnection()
		
		self.connection.chdir(self.currentReleasePath)
		
		tmpPath = os.path.join(self.tmpPath, "PFAMCurrentRelease")
		
	
		# Download the full file.
		if os.path.exists(target) or self.dryrun:
			# Skip files that have already downloaded correctly
			print "Skipping %s" % (file)
			return True
						
		self.connection.download( os.path.join(root, file) , target)
					
					
	# UNPACKING #
	
	def unpackFiles(self, chunkSize=2**18):
		""" Ungzips all files that have not already been ungzipped in chunks, by default in 32MB pieces. Will only look in the PFAMCurrentRelease folder.
		
		:param chunkSize: The size of the chunks in which the file needs to be read. Defaults to 32MB chunks.
		"""
		tmpPath = os.path.join(self.tmpPath, "PFAMCurrentRelease")
		for root, path, files in os.walk(tmpPath):
			for file in files:
				filePath = os.path.join(tmpPath, root, file)
				normalPath = re.sub("\.gz$", "", filePath)
				if not os.path.exists(normalPath) or os.path.getsize(normalPath) == 0:
					# Ungzip files in 1MB chunks
					
					gz = open(filePath, "rb")
					dc = zlib.decompressobj(16+zlib.MAX_WBITS)
					uz = open(normalPath, "wb")
										
					buffer=gz.read(chunkSize)

					while buffer:
						data = dc.decompress(buffer)
						uz.write(data)
						buffer=gz.read(chunkSize)
						
					data = dc.flush()
					uz.write(data)
					
					gz.close()
					uz.close()
				else:
					print "Skipping %s" % file