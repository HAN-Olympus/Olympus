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
		""" Finds all the Gene objects with an alias in the database.

		:rtype: A list of Gene StoredObjects. """
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
		""" Creates a list of unique PubMed queries for every combination of organism and gene name, from every source in the protein.
		This allows us to match all the different pieces of information from any source.

		For example, were there to be a Gene with the following attributes:
		Gene.alias = { Wormbase : ABCD, UniProt : EFGH }
		Gene.organism = { Wormbase : IJKL, UniProt : MNOP }

		It would yield a list not unlike the following:

		['MNOP ABCD', 'IJKL EFGH', 'MNOP EFGH', 'IJKL ABCD']

		*Note that the order in which this list presents itself can differ*
		
		This way every permutation of search queries is tested.

		:param organism: The organism attribute of a gene. This can also be any dictionary containing organism names as a value.
		:param alias: The alias attribute of a gene. This can also be any dictionary containing gene names as a value.
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
	print "Generating PubMed Connections"
	print "============================="
	pmc = PubMedConnections()
	genes = pmc.getAllNamedGenes()
	pmc.parseGenes(genes)

def test_createQueries():
	pmc = PubMedConnections()
	queries = pmc.createQueries({ "Wormbase" : "ABCD", "UniProt" : "EFGH"},{ "Wormbase" : "IJKL", "UniProt" : "MNOP"})

	# Test if the queries are the same as the expected result. The order may differ, but this can be avoided by using sets.
	# A length test is added to make sure the the transformation into a set does not alter the actual resulting queries.
	assert len(queries) == len(set(queries))
	assert set(queries) == set(['MNOP ABCD', 'IJKL EFGH', 'MNOP EFGH', 'IJKL ABCD'])
