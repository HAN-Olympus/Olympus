import Collection
import json
import networkx as nx
import matplotlib.pyplot as plt
import cStringIO

class ProcedureCollection(Collection.Collection):
	""" A container for a set of Olympus Procedure. It uses `NetworkX` to create the Procedure Graphs """
	
	def createFromJSON(self, nodes, edges):
		""" Creates a Procedure from two JSON lists and formats them so they can be used directly in the `createProcedureGraph` function. 
		
		:param nodes: A JSON encoded list of nodes.
		:param edges: A JSON encoded list of lists containing the connections between the nodes. If a node is mentioned here but not in `nodes` it will be created.
		':returns: A networkx (Di)Graph object
		"""
		nodes = json.loads(nodes)
		edges = json.loads(edges)
		correctEdges = []
		for e in edges:
			correctEdges.append( tuple(e) )
		return self.createProcedureGraph(nodes,correctEdges)
		
	def createProcedureGraph(self, nodes, edges):
		""" Creates a directed graph from the nodes and edges provided. 
		
		:param nodes: A list of nodes.
		:param edges: A list of 2-tuples containing the edges. If a node is mentioned here but not in `nodes` it will be created.
		:returns: A networkx (Di)Graph object
		"""
		graph = nx.DiGraph()
		graph.add_nodes_from(nodes)
		graph.add_edges_from(edges)		
		return graph
		
	def createGraphPreviewSVG(self, graph):
		""" Uses matplotlib to create an image of the created graph and serves it as an SVG. 
		
		:param graph: A networkx graph object.
		:returns: An SVG of the graph.
		"""
		nx.draw(graph)
		fakeFile = cStringIO.StringIO()
		plt.savefig(fakeFile, format="svg")
		plt.clf()
		fakeFile.seek(0)
		return fakeFile.read().replace("fill:#ff0000;","fill:#ffffff;").replace("\n","").replace("\t","").replace("    ","")
		
# TESTING #

def test_drawing():
	nx.draw(nx.Graph())

def test_createFromJSON():
	PC = ProcedureCollection()
	nodes = '["start","PubMed","Tail","Sort","WormBase","Table","LaTeX","PlainHTML"]'
	edges = '[["start","PubMed"],["PubMed","Tail"],["start","PubMed"],["PubMed","Sort"],["start","WormBase"],["WormBase","Tail"],["start","WormBase"],["WormBase","Sort"],["Sort","Table"],["Table","LaTeX"],["Table","PlainHTML"]]'
	
	PC.createFromJSON(nodes,edges)
	
def test_createProcedureGraph():
	PC = ProcedureCollection()
	nodes = ["PubMed","Tail","Sort","WormBase","Table","LaTeX","PlainHTML"]
	edges = [("start","PubMed"),("start","WormBase"),("PubMed","Tail"),("PubMed","Sort"),("WormBase","Tail"),("WormBase","Sort"),("Sort","Table"),("Table","LaTeX"),("Table","PlainHTML")]
	
	PC.createProcedureGraph(nodes,edges)
	
def test_createGraphPreviewSVG():
	PC = ProcedureCollection()
	nodes = ["PubMed","Tail","Sort","WormBase"]
	edges = [("start","PubMed"),("start","WormBase"),("PubMed","Tail"),("PubMed","Sort"),("WormBase","Tail"),("WormBase","Sort")]
	
	graph = PC.createProcedureGraph(nodes,edges)
	PC.createGraphPreviewSVG(graph)