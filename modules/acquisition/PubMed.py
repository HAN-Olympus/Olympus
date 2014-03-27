import AcquisitionModule
from Bio import Entrez
from Bio import Medline
from Article import Article
import datetime, urllib

class PubMed(AcquisitionModule.AcquisitionModule):
	""" This module allows for retrieval of medical articles from the Entrez API."""
	def __init__(self):
		# TODO: Configuration should set this
		Entrez.email = "Your.Name.Here@example.org"
	
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
		if len(ids) == 0:
			return []
		
		handle = Entrez.efetch("pubmed", id=",".join(ids), retmode="xml", retmax=limit)
		records = Entrez.parse(handle)
		articles = []
		for record in records:
			articles.append( self.convertToArticle(record) )
			
		return articles
		
	
	def getById(self, id, limit=1):
		"""Get a pubmed article by ID
		
		:param id: Either a single ID or a list of IDs
		:param limit: The maximum amount of pubmed articles to be retreived
		:rtype: A list of articles, defaults to 1
		"""
		if isinstance(id, list):
			id = id.join(",")
		
		handle = Entrez.efetch("pubmed", id=id, retmode="xml", retmax=limit)
		records = Entrez.parse(handle)
		articles = []
		for record in records:
			articles.append( self.convertToArticle(record) )
			
		return articles
		
		
	
	def convertToArticle(self, article):
		"""Takes the parsed Pubmed article and converts it to our lightweight format.
		
		:param article: A parsed Pubmed article
		:rtype: A properly formatted Article Object ( Stored Object )
		"""
		articleObject = Article()
		
		# Loop over all the citation data
		medlineCitation = article["MedlineCitation"]
		for attr in medlineCitation:
			if attr == "PMID":
				articleObject.addAttribute("id","pubmed",str( medlineCitation["PMID"] ))
				
			if attr == "DateCreated":
				day = medlineCitation["DateCreated"]["Day"]
				month = medlineCitation["DateCreated"]["Month"]
				year = medlineCitation["DateCreated"]["Year"]
				dateCreated = self.convertDateToNative( day, month, year )
				articleObject.addAttribute("dateCreated","pubmed",dateCreated)
				
			if attr == "DateCompleted":
				day = medlineCitation["DateCompleted"]["Day"]
				month = medlineCitation["DateCompleted"]["Month"]
	