from Olympus.lib.StoredObject import StoredObject
from Olympus.lib.PubMedIndex import PubMedIndex
from Olympus.lib.Gene import Gene
from Olympus.modules.acquisition.PubMed import PubMed

import pprint
import itertools

class PubMedConnections():
	""" This mass acquisition module tries to create indexes for connections between PubMed articles and genes. 
		It relies on the Entrez API and may therefor be pretty slow. 
		Functionality with PubMed is attained through the PubMed acquisition module.
	"""
	
	def __init__(self):
		self.pm = PubMed()
	
	def getAllNamedGenes(self):
		""" Finds all the Gene objects with an alias. """
		g = Gene()
		namedGenes = g.getObjectsByKey("alias", {"$ne": {}, "$exists": True}) # Get all the genes with an alias.
		
		return namedGenes
		
	def parseGenes(self, genes):
		""" Uses the specified genes to find links between the gene and articles in PubMed.
		
		:param genes: A list of Gene objects. These need to have the name, organism and alias attribute specified.
		"""
		
		total = len(genes)
		counter = 0
		
		for gene in genes:
			organism = gene.organism
			alias = gene.alias
			
			queries = self.createQueries(organism, alias)		
			ids = self.getArticles(queries)
			pmi = PubMedIndex()
			pmi.gene = gene.id
			pmi.articles = ids
			pmi.save()
			
			# This block is for timekeeping and reporting only.	
			percentage = float(counter)/float(total)*100
			print "%s%% done." % percentage
			counter += 1
			
	def createQueries(self, organism, alias):
		""" Creates a list of unique PubMed queries for 
		
		:param organism: The organism attribute of a gene.
		:param organism: The alias attribute of a gene.
		:rtype: A list of queries for the PubMed search engine.
		"""
		
		baseQuery = "%s %s"
		keys = organism.keys() + alias.keys()
		combinations = list(itertools.permutations(keys, 2))
		queries = set()

		for keyOne,keyTwo in combinations:
			queries.add(baseQuery % (alias[keyOne], organism[keyTwo].replace("_", ". ")))
			
		return list(queries)
	
	def getArticles(self,queries):
		""" Retrieves the articles for these queries with a default limit of 10. 
		The Article will actually be parsed to get extra data.
		
		:param queries: A list of queries for the PubMed search engine.
		:rtype: A list of Article ID attributes.
		"""
		ids = []
			
		for query in queries:				
			for article in self.pm.getBySearchTerm(query):
				ids.append( article.id )
		return ids
			
			
	
if __name__ == "__main__":
	pmc = PubMedConnections()
	genes = pmc.getAllNamedGenes()
	pmc.parseGenes(genes)