"""
@name PubMed
@author Stephan Heijl
@module PubMed
@version 1.0.0
"""

from Olympus.modules.acquisition.AcquisitionModule import AcquisitionModule
from Bio import Entrez
from Bio import Medline

from Olympus.lib.Article import Article
from Olympus.lib.Collection import Collection
from Olympus.lib.Log import Log
from Olympus.lib.Config import Config

from Olympus.lib.controls.Float import Float
from Olympus.lib.controls.Integer import Integer
from Olympus.lib.controls.Text import Text

import datetime, urllib

class PubMed(AcquisitionModule):
	""" This module allows for retrieval of medical articles from the Entrez API."""
	
	def __init__(self):
		# TODO: Configuration should set this
		Entrez.email = Config().email
	
	def formatTerm(self, term="", tAnd = [], tOr = [], **kwargs):
		"""Format a term to allow direct passing to Entrez.
		
		:param term: A string that will literally be matched
		:param tAnd: A list of strings that will be combined into an AND query
		:param tOr: A list of strings that will be combined into an OR query
		:rtype: A string that is properly formatted for use with Entrez
		"""
		q = [term]
		if len(tAnd) > 0:
			q.append( "(" + " AND ".join(tAnd) + ")" )
		if len(tOr) > 0:
			q.append( "(" + " OR ".join(tOr) + ")")
			
		for type,word in kwargs.items():
			q.append( "%s[%s]" % (word,type) )
		return  " ".join(q).strip(" ")
		
		
	def getBySearchTerm(self, term, limit=10):
		"""Get a pubmed article by a search term. Use formatTerm() to construct a pretty term.
		
		:param term: A search term, either made by formatTerm() or self-made.
		:rtype: A list of articles, defaults to 10
		"""
		search = Entrez.esearch("pubmed", term=term, retmax=limit)
		ids = Entrez.read(search)["IdList"]
		print ids, len(ids)
		if len(ids) == 0:
			return []
					
		articles = self.getById(list(ids), limit=limit)
		print articles, len(articles)
			
		return articles
		
	
	def getById(self, id, limit=1):
		"""Get a pubmed article by ID
		
		:param id: Either a single ID or a list of IDs
		:param limit: The maximum amount of pubmed articles to be retreived
		:rtype: A list of articles, defaults to 1
		"""
		
		if len(id) == 0 or id==None:
			return []
		
		articles = []
		
		if isinstance(id, list):
			# Check if these ids already exist in the database.
			for i in id:
				results = Article().getObjectsByKey("id.pubmed", i )
				if len(results) > 0:
					articles.append( results[0] )
					id.remove(i)			
		
			id = ",".join(id)
			
		else:
			# Check if this article already exists in the database.
			results = Article().getObjectsByKey("id.pubmed", id )
			if len(results) > 0:
				return [results[0]]
			
		# Check if there are still articles to save.
		if id == "":
			return articles
		
		handle = Entrez.efetch("pubmed", id=id, retmode="xml", retmax=limit)
		records = Entrez.parse(handle)
		
		for record in records:
			article = self.convertToArticle(record)
			if article != None:
				articles.append( article )
				article.save()
			
		return articles		
	
	def convertToArticle(self, article):
		"""Takes the parsed Pubmed article and converts it to our lightweight format.
		
		:param article: A parsed Pubmed article
		:rtype: A properly formatted Article Object ( Stored Object ) or None if a parsing error occurred.
		"""
		
		articleObject = Article()
		
		# Loop over all the citation data
		if "MedlineCitation" not in article:
			return None
			
		medlineCitation = article["MedlineCitation"]
		for attr in medlineCitation:
			if attr == "PMID":
				articleObject.addAttribute("id","pubmed",unicode( medlineCitation["PMID"] ))
				
			if attr == "DateCreated":
				day = medlineCitation["DateCreated"]["Day"]
				month = medlineCitation["DateCreated"]["Month"]
				year = medlineCitation["DateCreated"]["Year"]
				dateCreated = self.convertDateToNative( day, month, year )
				articleObject.addAttribute("dateCreated","pubmed",dateCreated)
				
			if attr == "DateCompleted":
				day = medlineCitation["DateCompleted"]["Day"]
				month = medlineCitation["DateCompleted"]["Month"]
				year = medlineCitation["DateCompleted"]["Year"]
				dateCompleted = self.convertDateToNative( day, month, year )
				articleObject.addAttribute("dateCompleted","pubmed",dateCompleted)

			if attr == "Article":
				articleObject.addAttribute("title","pubmed", medlineCitation["Article"]["ArticleTitle"].encode('utf8') )
				
				try:
					articleObject.addAttribute("abstract","pubmed", medlineCitation["Article"]["Abstract"]["AbstractText"][0].encode('utf8') )
				except:
					articleObject.addAttribute("abstract","pubmed", "" )
					
				authors = []
				try:
					for author in medlineCitation["Article"]["AuthorList"]:
						authors.append( "%s %s" % (author["ForeName"], author["LastName"]))
				except:
					authors = ["Unknown"]
				articleObject.addAttribute("authors", "pubmed", authors)

				articleObject.addAttribute("source","pubmed",unicode(medlineCitation["Article"]["Journal"]["Title"]))

		# Loop over all the aspects of the pubmed data
		for attr in article["PubmedData"]:
			if attr == "ArticleIdList":
				for id in article["PubmedData"]["ArticleIdList"]:
					articleObject.addAttribute("id",id.attributes["IdType"],str(id))
		
		return articleObject
	
	def specifyControls(self):
		controls = {
			"searchterm" : Text("searchterm", value="", label="Search term"),
			"limit" : Integer("limit", value=0, label="Limit")
		}
		return controls
	
	def specifyInput(self):
		return None
		
	def specifyOutput(self):
		articleCollection = Collection(Article)
		
		log = Log()
		
		output = {
			"errors":[log],
			"result":[articleCollection]
		}
		return output
		
	def start(self, **kwargs):
		searchterm = kwargs.get("searchterm", "zinc")
		limit = kwargs.get("limit", 10)
		articles = self.getBySearchTerm(searchterm,limit=limit)
		return articles

# TESTING #

def test_specifyControls():
	pm = PubMed()
	pm.specifyControls()


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
	assert len(articles) > 5

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
	article.setDatabase("test_database")
	article.setCollection("test_collection")
	article.save()
	article.remove()