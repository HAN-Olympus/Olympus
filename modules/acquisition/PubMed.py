import AcquisitionModule
from Bio import Entrez
from Bio import Medline
from Article import Article
import datetime, urllib

class PubMed(AcquisitionModule.AcquisitionModule):
	def __init__(self):
		# TODO: Configuration should set this
		Entrez.email = "Your.Name.Here@example.org"
	
	
	# Format a term to allow direct passing to Entrez.
	# @param term	: A string that will literally be matched
	# @param tAnd	: A list of strings that will be combined into an AND query
	# @param tOr		: A list of strings that will be combined into an OR query
	# @returns		: A string that is properly formatted for use with Entrez
	def formatTerm(self, term="", tAnd = [], tOr = [], **kwargs):
		q = [term]
		if len(tAnd) > 0:
			q.append( "(" + " AND ".join(tAnd) + ")" )
		if len(tOr) > 0:
			q.append( "(" + " OR ".join(tOr) + ")")
			
		for type,word in kwargs.items():
			q.append( "%s[%s]" % (word,type) )
		return  " ".join(q).strip(" ")
		
		
	# Get a pubmed article by a search term. Use formatTerm() to construct a pretty term.
	# @param term	: A search term, either made by formatTerm() or self-made.
	# @returns 		: A list of articles, defaults to 10
	def getBySearchTerm(self, term, limit=10):
		search = Entrez.esearch("pubmed", term=term, retmax=limit)
		ids = Entrez.read(search)["IdList"]
		if len(ids) == 0:
			return []
		
		handle = Entrez.efetch("pubmed", id=",".join(ids), retmode="xml", retmax=limit)
		records = Entrez.parse(handle)
		articles = []
		for record in records:
			articles.append( self.convertPubmedArticle(record) )
			
		return articles
		
	# Get a pubmed article by ID
	# @param id 	: Either a single ID or a list of IDs
	# @param limit	: The maximum amount of pubmed articles to be retreived
	# @returns 		: A list of articles, defaults to 1
	def getById(self, id, limit=1):
		if isinstance(id, list):
			id = id.join(",")
		
		handle = Entrez.efetch("pubmed", id=id, retmode="xml", retmax=limit)
		records = Entrez.parse(handle)
		articles = []
		for record in records:
			articles.append( self.convertPubmedArticle(record) )
			
		return articles
		
		
	# Convert Pubmeds day, month, year notation to a python datetime object
	# @param day	: Numeric, the day (1-31)
	# @param month	: Numeric, the month (1-12)
	# @param year	: Numeric, the year
	# @returns		: A properly formed datetime object
	def convertDateToNative(self, day, month, year):
		dt = datetime.datetime(int(year), int(month), int(day))
		return dt
		
	# Takes the parsed Pubmed article and converts it to our lightweight format.
	# @param article: A parsed Pubmed article
	# @returns		: A properly formatted Article Object ( Stored Object )
	def convertPubmedArticle(self, article):
		articleObject = Article()
		
		# Loop over all the citation data
		medlineCitation = article["MedlineCitation"]
		for attr in medlineCitation:
			if attr == "PMID":
				articleObject.id["pubmed"] = str( medlineCitation["PMID"] )
				
			if attr == "DateCreated":
				day = medlineCitation["DateCreated"]["Day"]
				month = medlineCitation["DateCreated"]["Month"]
				year = medlineCitation["DateCreated"]["Year"]
				dateCreated = self.convertDateToNative( day, month, year )
				articleObject.dateCreated["Pubmed"] = dateCreated
				
			if attr == "DateCompleted":
				day = medlineCitation["DateCompleted"]["Day"]
				month = medlineCitation["DateCompleted"]["Month"]
				year = medlineCitation["DateCompleted"]["Year"]
				dateCompleted = self.convertDateToNative( day, month, year )
				articleObject.dateCompleted["Pubmed"] = dateCompleted
				
			if attr == "Article":
				articleObject.title["pubmed"] = medlineCitation["Article"]["ArticleTitle"].encode('utf8')
				articleObject.abstract["pubmed"] = medlineCitation["Article"]["Abstract"]["AbstractText"][0].encode('utf8')
				
				articleObject.authors["pubmed"] = []
				for author in medlineCitation["Article"]["AuthorList"]:
					articleObject.authors["pubmed"].append( "%s %s" % (author["ForeName"], author["LastName"]))
				
				articleObject.source["pubmed"] = str(medlineCitation["Article"]["Journal"]["Title"])
		
		# Loop over all the aspects of the pubmed data
		for attr in article["PubmedData"]:
			if attr == "ArticleIdList":
				for id in article["PubmedData"]["ArticleIdList"]:
					articleObject.id[id.attributes["IdType"]] = str(id)
		
		return articleObject
		

# TESTING #

def test_formatTerm():
	pm = PubMed()
	assert pm.formatTerm(term="C. elegans") == "C. elegans"
	assert pm.formatTerm(term="C. elegans", tAnd = ["toxin","zinc"]) == "C. elegans (toxin AND zinc)"
	complexQuery = "C. elegans (toxin AND zinc) (Zebrafish OR C. elegans)"
	assert pm.formatTerm(term="C. elegans", tAnd = ["toxin","zinc"], tOr = ["Zebrafish", "C. elegans"]) == complexQuery
	assert pm.formatTerm(Orgn="C. elegans") == "C. elegans[Orgn]"
	
def test_getBySearchTerm():
	pm = PubMed()
	articles = pm.getBySearchTerm("zinc")
	assert len(articles) == 10

def test_convertDateToNative():
	dt = PubMed().convertDateToNative(1,1,2014)
	assert isinstance(dt, datetime.datetime)
	assert dt.year == 2014

def test_getById():
	pm = PubMed()
	id = "17284678"
	articles = pm.getById(id)
	assert articles is not None
	assert len(articles) == 1
	assert articles[0] is not None
	assert articles[0].id["pubmed"] == id
	
def test_saveArticle():
	pm = PubMed()
	id = "17284678"
	article = pm.getById(id)[0]
	article._database = "test_database"
	article._collection = "test_collection"
	article.save()
	article.remove()
	
	
