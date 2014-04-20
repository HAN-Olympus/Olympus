import Collection
import json
import networkx as nx
import matplotlib.pyplot as plt
import time

class ProcedureCollection(Collection.Collection):
	""" A container for a set of Olympus Procedure. It uses `NetworkX` to create the Procedure Graphs """
	
	def createFromJSON(self, nodes, edges):
		""" Creates a Procedure from two JSON lists and formats them so they can be used directly in the `createProcedureGraph` function. 
		
		:param nodes: A JSON encoded list of nodes.
		:param edges: A JSON encoded list of lists containing the connections between the nodes. If a node is mentioned here but not in `nodes` it will be created.
		"""
		nodes = json.loads(nodes)
		edges = json.loads(edges)
		correctEdges = []
		for e in edges:
			correctEdges.append( tuple(e) )
		
		print nodes
		print correctEdges
		self.createProcedureGraph(nodes,correctEdges)
		
	def createProcedureGraph(self, nodes, edges):
		graph = nx.Graph()
		graph.add_nodes_from(nodes)
		graph.add_edges_from(edges)
		
		nx.draw(graph)
		fname = "graph_test"+str(time.time())+".png"
		plt.savefig(fname)
		print fname
		
# TESTING #

def test_drawing():
	nx.draw(nx.Graph())

def test_createFromJSON():
	PC = ProcedureCollection()
	nodes = '["start","PubMed","Tail","Sort","WormBase","Table","LaTeX","PlainHTML"]'
	edges = '[["PubMed","Tail"],["PubMed","Sort"],["WormBase","Tail"],["WormBase","Sort"],["Sort","Table"],["Table","LaTeX"],["Table","PlainHTML"]]'
	
	PC.createFromJSON(nodes,edges)
	
def test_createProcedureGraph():
	PC = ProcedureCollection()
	nodes = ["PubMed","Tail","Sort","WormBase","Table","LaTeX","PlainHTML"]
	edges = [("start","Pubmed"),("start","WormBase"),("PubMed","Tail"),("PubMed","Sort"),("WormBase","Tail"),("WormBase","Sort"),("Sort","Table"),("Table","LaTeX"),("Table","PlainHTML")]
	
	PC.createProcedureGraph(nodes,edges)