import Collection
import json
import networkx as nx
import matplotlib

""" Tell matplotlib not to try to output to the screen. We will only use it to generate images. """
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import cStringIO
from Module import Module
from networkx.algorithms import traversal
from pprint import pformat as pf

class ProcedureCollection(Collection.Collection):
	""" A container for a set of Olympus Procedure. It uses `NetworkX` to create the Procedure Graphs """
	
	def importModules(self, nodes):
		""" Imports all the given modules, instantiates the containing class and returns the collective result as a list.
			
			:param nodes: A list of module names. The names of the classes that should be imported should match the module names.
			:rtype: A list of freshly imported and instantiated objects.
		"""
		instantiatedNodes = []
		
		for module in nodes:
			if module == "start":
				continue
			importedModule = __import__(module)
			if module in importedModule.__dict__.keys():
				instantiatedNodes.append(__import__(module).__dict__[module]())
				
		return instantiatedNodes
	
	def createFromJSON(self, nodes, edges, edgeAttributes):
		""" Creates a Procedure from two JSON lists and formats them so they can be used directly in the `createProcedureGraph` function. 
		
		:param nodes: A JSON encoded list of nodes.
		:param edges: A JSON encoded list of lists containing the connections between the nodes. If a node is mentioned here but not in `nodes` it will be created.
		:param edgeAttributes: A JSON encoded list of attributes for each edge, should correspond in order with the edges list.
		:rtype: A networkx (Di)Graph object
		"""
		nodes = json.loads(nodes)
		edges = json.loads(edges)
		edgeAttributes = json.loads(edgeAttributes)
		correctEdges = []
		for e in edges:
			correctEdges.append( tuple(e) )
		return self.createProcedureGraph(nodes,correctEdges,edgeAttributes)
		
	def createProcedureGraph(self, nodes, edges, edgeAttributes):
		""" Creates a directed graph from the nodes and edges provided. Instead of the names, it will use instances of each of the modules
		
		:param nodes: A list of nodes.
		:param edges: A list of 2-tuples containing the edges. If a node is mentioned here but not in `nodes` it will be created.
		:param edgeAttributes: A dictionary of attributes for each edge, should correspond in order with the edges list.
		:rtype: A networkx (Di)Graph object
		"""		
		
		instantiatedNodes = self.importModules(nodes)
				
		instantiatedNodes.append("start")
		
		instantiatedEdges = []
		
		e = 0
		for edge in edges:
			newEdge = []
			for node in edge:
				if node in nodes:
					newEdge.append(instantiatedNodes[nodes.index(node)])
				else:
					newEdge.append(node)
			newEdge.append(edgeAttributes[e])	
			instantiatedEdges.append(tuple(newEdge))
			e+=1
				
		graph = nx.DiGraph()
		graph.add_nodes_from(instantiatedNodes)
		graph.add_edges_from(instantiatedEdges)
		return graph
		
	def bfs_edges(self, G,source):
		"""Produce edges in a breadth-first-search starting at source.
		Based on http://www.ics.uci.edu/~eppstein/PADS/BFS.py
		by D. Eppstein, July 2004.
		
		Edited to allow already visited nodes, makes it less efficient but allows this algorithm to be used in graphs that come back unto themselves.
		
		:param G: A networkx graph
		:param source: The starting point of the graph."""
		
		visited=set()
		stack = [(source,iter(G[source]))]
		while stack:
			parent,children = stack[0]
			try:
				child = next(children)
				if (parent,child) not in visited:
					yield parent,child, G.get_edge_data(parent, child)
					visited.add((parent,child))
					stack.append((child,iter(G[child])))
			except StopIteration:
				stack.pop(0)

		
	def traverseGraph(self, graph):
		""" Use a Breadth-first search to work through the graph. This should allow even more complex graphs to be completed successfully.
		
		:param graph: A graph containing classes to execute.
		"""
		
		output = {}
		storedOutput = {}
		
		for edge in self.bfs_edges(graph, "start"):
			parent = edge[0]
			child = edge[1]
			
			print "%s -> %s" % (parent, child)
			# Should contain an outputId, determining what exactly should be retrieved from the function call.
			attributes = edge[2]
			# Only start the node if it's actually a module...
			if not isinstance(child, Module):
				continue
			
			if not isinstance(parent, Module):
				output[child] = [child.start()]
			else:
				argcount = child.start.func_code.co_argcount
				
				if argcount == 2:
					if child in output and isinstance(output[child], list):
						for c in output[parent]:
							output[child].append(child.start(c))
					else:
						output[child] = [child.start(c) for c in output[parent]]
						
				elif argcount > 2:
					if len(output[parent]) == argcount -1:
						output[child] = [child.start(*output[parent])]
						
				else:
					output[child] = None
					
		return output
			
		
	def createGraphPreviewSVG(self, graph):
		""" Uses matplotlib to create an image of the created graph and serves it as an SVG. Uses a spring layout to deliver better visuals.
		
		:param graph: A networkx graph object.
		:rtype: An SVG of the graph.
		"""
		nx.draw_spring(graph)
		fakeFile = cStringIO.StringIO()
		plt.savefig(fakeFile, format="svg")
		plt.clf()
		fakeFile.seek(0)
		return fakeFile.read()
		
	def createGefxPreview(self, graph):
		fakeFile = cStringIO.StringIO()
		nx.write_gexf(graph,fakeFile)
		fakeFile.seek(0)
		return fakeFile.read()
		
# TESTING #
def test_drawing():
	nx.draw(nx.Graph())

def test_createFromJSON():
	PC = ProcedureCollection()
	nodes = '["start","PubMed","Tail","Sort","WormBase","Table","LaTeX","PlainHTML"]'
	edges = '[["start","PubMed"],["PubMed","Tail"],["start","PubMed"],["PubMed","Sort"],["start","WormBase"],["WormBase","Tail"],["start","WormBase"],["WormBase","Sort"],["Sort","Table"],["Table","LaTeX"],["Table","PlainHTML"]]'
	edgeAttributes = '[{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":"Result"},{"outputId":"Latex"},{"outputId":"Html"}]'
	
	PC.createFromJSON(nodes,edges,edgeAttributes)
	
def test_createProcedureGraph():
	PC = ProcedureCollection()
	nodes = ["PubMed","Tail","Sort","WormBase","Table","LaTeX","PlainHTML"]
	edges = [("start","PubMed"),("start","WormBase"),("PubMed","Tail"),("PubMed","Sort"),("WormBase","Tail"),("WormBase","Sort"),("Sort","Table"),("Table","LaTeX"),("Table","PlainHTML")]
	edgeAttributes = [{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":"Result"},{"outputId":"Latex"},{"outputId":"Html"}]
	
	PC.createProcedureGraph(nodes,edges,edgeAttributes)
	
def test_createGraphPreviewSVG():
	PC = ProcedureCollection()
	nodes = ["PubMed","Tail","Sort","WormBase"]
	edges = [("start","PubMed"),("start","WormBase"),("PubMed","Tail"),("PubMed","Sort"),("WormBase","Tail"),("WormBase","Sort")]
	edgeAttributes = [{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":"Result"},{"outputId":"Latex"},{"outputId":"Html"}]
	
	graph = PC.createProcedureGraph(nodes,edges,edgeAttributes)
	PC.createGraphPreviewSVG(graph)
	
def test_traverseGraph():
	PC = ProcedureCollection()
	nodes = ["PubMed","Tail","Sort","WormBase","Table","LaTeX","PlainHTML"]
	edges = [("start","PubMed"),("start","WormBase"),("PubMed","Tail"),("PubMed","Sort"),("WormBase","Tail"),("WormBase","Sort"),("Sort","Table"),("Table","LaTeX"),("Table","PlainHTML")]
	edgeAttributes = [{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":""},{"outputId":"Errors"},{"outputId":""},{"outputId":"Result"},{"outputId":"Result"},{"outputId":"Latex"},{"outputId":"Html"}]
	
	graph = PC.createProcedureGraph(nodes,edges,edgeAttributes)
	PC.traverseGraph(graph)
	