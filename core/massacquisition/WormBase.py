from Olympus.lib.StoredObject import StoredObject
from Olympus.lib.Protein import Protein
from Olympus.lib.CodingSequence import CodingSequence
import ftputil
import os
import hashlib
import zlib
import re
import time
import datetime

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
		
		self.verbose = True
		
	def checkConnection(self):
		if self.connection != None:
			return True
		else:
			raise Exception, "The connection has not yet been initiated."
	
	def connect(self):
		connection = ftputil.FTPHost(self.url, "anonymous", "")
		self.connection = connection
	
	def createChunkyHash(self, f, blockSize=128**4):
		""" Returns the MD5 checksum of the given file, created by feeding the file in chunks to the hashlib module. 
			This reduces memory usage at the cost of some speed. blockSize can be increased to speed up this process. 
			
			:param f: A filelike object
			:param blockSize: The size of the chunks in which the file needs to be read. Defaults to 128MB chunks.
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
	
	def unpackFiles(self, chunkSize=2**18):
		""" Ungzips all files that have not already been ungzipped in chunks, by default in 32MB pieces. 
		
		:param chunkSize: The size of the chunks in which the file needs to be read. Defaults to 32MB chunks.
		"""
		tmpPath = os.path.join(self.tmpPath, "WormBaseCurrentRelease")
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
	
	# PARSING TO STOREDOBJECTS #
	
	def parseFiles(self):
		tmpPath = os.path.join(self.tmpPath, "WormBaseCurrentRelease")
		
		proteinMatch = re.compile("protein\.fa$")
		codingMatch = re.compile("coding_transcripts\.fa$")
		
		organismMatch = re.compile("^[\w_]+?\.")
		
		for root, path, files in os.walk(tmpPath):
			for file in files:
				organism = organismMatch.search(file).group(0)
				#if proteinMatch.search(file) != None:
				#	self.parseProtein(os.path.join(tmpPath, root, file), organism)
				
				#if codingMatch.search(file) != None:
				#	self.parseCodingSequence(os.path.join(tmpPath, root, file), organism)
					
	def saveProtein(self, annotation, sequence, organism):
		""" Takes the annotation and the sequence and converts them into a Protein StoredObject.
		Will check in the existing collection for proteins with the same ID from different sources (UniProt, YCR and ENA, in that order).
		
		:param annotation: The annotation from the proteins.fa (The line starting with ">" )
		:param sequence: The sequence of the protein
		:param organism: The organism this protein belongs to.
		:rtype: True if the Protein was saved succesfully
		"""
		seq = "".join(sequence)
		annotation = annotation.split("\t")
		if len(annotation) < 4:
			return None
		
		try:
			gene = annotation[0][1:]
			YCRID = annotation[1]
			WormBaseID = annotation[2]
			ENAID = annotation[-1].split(":")[1]
			UniProtID = annotation[-2].split(":")[1]
		except IndexError:
			print "Incomplete annotation."
			return False
		
		details = annotation[3:-2]
		
		p = Protein()
		p.addAttribute("gene", "WormBase", gene)
		p.addAttribute("organism", "WormBase", organism)
		p.addAttribute("id", "YCR", YCRID)
		p.addAttribute("id", "WormBase", WormBaseID)
		p.addAttribute("id", "ENA", ENAID)
		p.addAttribute("id", "UniProt", UniProtID)
		p.addAttribute("sequence", "WormBase", seq)
		p.addAttribute("sequencelength", "WormBase", len(seq))
		p.addAttribute("modificationdate", "WormBase", datetime.datetime.now())
		
		for detail in details:
			
			if ":" in detail:
				key, value = detail.split(":")
				p.addAttribute(key, "WormBase", value)
			else:
				if p.getAttribute("name") == "":
					p.setAttribute("name", "WormBase", detail)
				else:
					p.addAttribute("name", "WormBase", detail)
		
		# Check for existing matches
		UniProtMatch = p.getObjectsByKey("id.UniProt", UniProtID, limit=1)
		if len(UniProtMatch) > 0:
			mergedObject = UniProtMatch[0] + p
			mergedObject.save()
			return True
		
		YCRMatch = p.getObjectsByKey("id.YCR", YCRID, limit=1)
		if len(YCRMatch) > 0:
			mergedObject = YCRMatch[0] + p
			mergedObject.save()
			return True
		
		ENAMatch = p.getObjectsByKey("id.ENA", ENAID, limit=1)
		if len(ENAMatch) > 0:
			mergedObject = ENAMatch[0] + p
			mergedObject.save()
			return True
				
		p.save()
		return True
		
	
	def parseProtein(self, file, organism):
		""" Parses a proteins.fa file from WormBase.
		Reports progress and approximate time left (estimated by a moving average of delta t within between percentage). """
		print "Parsing (Protein) %s " % file
		f = open(file, "r")
		size = os.path.getsize(file)
		
		annotation = ""
		sequence = []
		
		counter = 0
		lastPercentage = 0
		
		start = time.time()
		times = []
		counts = []
		
		for line in f:		
			if line.startswith(">"):			
				if len(annotation) > 0:
					saved = self.saveProtein(annotation, sequence, organism)
					
					if saved and self.verbose:
						# This block is for timekeeping and reporting only.
						
						counter += 1
						current = f.tell()
						
						percentage = (float(current)/float(size))*100

						if round(percentage*2)/2 > lastPercentage:
							lastPercentage = round(percentage*2)/2
							deltat = time.time() - start
							start = time.time()
							
							timeleft = deltat * (100-lastPercentage)
							
							times.append(timeleft)
							counts.append(counter)
							if len(times) > 5:
								times.pop(0)
								counts.pop(0)
							
							avgTimeLeft = sum(times)/len(times)
							# Calculate the differences between the different counts
							countsDiff = ([ abs(counts[i] - counts[i-1]) for i in reversed(range(len(counts)-1))])
							# Calculate the approximate counts per second.
							if len(countsDiff) > 0 and deltat > 0:
								avgProteinsS = sum(countsDiff)/len(countsDiff)/deltat
							else:
								avgProteinsS = 0
														
							print "%s proteins saved. - %s %% done. Approx. %s seconds left until completion. ~%s proteins per second." % (counter, lastPercentage, int(avgTimeLeft), int(avgProteinsS))
				
				annotation = line.strip()				
				sequence = []
			else:
				sequence.append(line.strip())
				
				
	def saveCodingSequence(self, annotation, sequence, organism):
		""" Takes the annotation and the sequence and converts them into a CodingSequence StoredObject.
		Will check in the existing collection for proteins with the same ID from different sources (UniProt, YCR and ENA, in that order).
		
		:param annotation: The annotation from the proteins.fa (The line starting with ">" )
		:param sequence: The sequence of the protein
		:param organism: The organism this protein belongs to.
		:rtype: True if the Protein was saved succesfully
		"""
		seq = "".join(sequence)
		annotation = annotation.split(" ")
		if len(annotation) < 2:
			return None
		try:
			id = annotation[0][1:]
			gene = annotation[1][5:]
		except IndexError:
			print "Incomplete annotation."
			return False
		
		
		cds = CodingSequence()
		cds.addAttribute("gene", "WormBase", gene)
		cds.addAttribute("organism", "WormBase", organism)
		cds.addAttribute("id", "WormBase", id)
		cds.addAttribute("sequence", "WormBase", seq)
		cds.addAttribute("sequencelength", "WormBase", len(seq))
		cds.addAttribute("modificationdate", "WormBase", datetime.datetime.now())
		
		# Check for existing matches
		idMatch = cds.getObjectsByKey("id.WormBase", id, limit=1)
		if len(idMatch) > 0:
			mergedObject = idMatch[0] + p
			mergedObject.save()
			return True
				
		cds.save()
		return True
		
	def parseCodingSequence(self, file, organism):
		""" Parses a coding_transcripts.fa file from WormBase. 
		Reports progress and approximate time left (estimated by a moving average of delta t within between percentage). """
		
		print "Parsing (Coding) %s " % file
		f = open(file, "r")
		size = os.path.getsize(file)
		
		annotation = ""
		sequence = []
		
		counter = 0
		lastPercentage = 0
		
		start = time.time()
		times = []
		counts = []
		
		for line in f:		
			if line.startswith(">"):			
				if len(annotation) > 0:
					saved = self.saveCodingSequence(annotation, sequence, organism)
					if saved and self.verbose:
						# This block is for timekeeping and reporting only.
						
						counter += 1
						current = f.tell()
						
						percentage = (float(current)/float(size))*100
						if round(percentage*2)/2 > lastPercentage:
							lastPercentage = round(percentage*2)/2
							deltat = time.time() - start
							start = time.time()

							timeleft = deltat * (100-lastPercentage)

							times.append(timeleft)
							counts.append(counter)
							if len(times) > 5:
								times.pop(0)
								counts.pop(0)

							avgTimeLeft = sum(times)/len(times)
							# Calculate the differences between the different counts
							countsDiff = ([ abs(counts[i] - counts[i-1]) for i in reversed(range(len(counts)-1))])
							# Calculate the approximate counts per second.
							if len(countsDiff) > 0 and deltat > 0:
								avgSequencesS = sum(countsDiff)/len(countsDiff)/deltat
							else:
								avgSequencesS = 0

							print "%s coding sequences saved. - %s %% done. Approx. %s seconds left until completion. ~%s coding sequences per second." % (counter, lastPercentage, int(avgTimeLeft), int(avgSequencesS))
				
				annotation = line.strip()				
				sequence = []
			else:
				sequence.append(line.strip())
		
		
			
	

# Default module start #
if __name__ == "__main__":
	print "Welcome to the WormBase Mass Acquisition module."
	wb = WormBase()
	wb.connect()
	wb.downloadCurrentRelease()
	wb.unpackFiles()
	wb.parseFiles()
	
		
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
	wb.downloadCurrentRelease()
	
def test_unpackFiles():
	wb = WormBase()
	wb.unpackFiles()
	
def test_parseFiles():
	wb = WormBase()
	wb.parseFiles()
	
def test_saveProtein():
	wb = WormBase()
	annotation = ">2L52.1	CE32090	WBGene00007063	status:Partially_confirmed	UniProt:A4F336	protein_id:CCD61130.1"
	assert wb.saveProtein(annotation, "ACTG", "Sample")
	assert len(Protein().getObjectsByKey("id.UniProt", "A4F336", limit=10)) == 1
	# Test if doubles are merged
	assert wb.saveProtein(annotation, "ACTG", "Sample")
	assert len(Protein().getObjectsByKey("id.UniProt", "A4F336", limit=10)) == 1
	
def test_saveCodingSequence():
	wb = WormBase()
	annotation = ">2L52.1 WormBase:12345"
	assert wb.codingSequence(annotation, "ACTG", "Sample")
	assert len(CodingSequence().getObjectsByKey("id.WormBase", "2L52.1", limit=10)) == 1
	# Test if doubles are merged
	assert wb.saveProtein(annotation, "ACTG", "Sample")
	assert len(CodingSequence().getObjectsByKey("id.WormBase", "2L52.1", limit=10)) == 1