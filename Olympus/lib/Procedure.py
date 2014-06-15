from pprint import pprint
import importlib
import networkx as nx
import cStringIO
from html import XHTML

class Procedure():
	def __init__(self):
		self.nodes = []
		self.edges = []
		self.attributes = []
		self.graph = None
		self.instantiatedNodes = []
		
	def importModules( self, modules ):
		""" Imports all the modules needed. """
		
		instantiatedNodes = []
		
		for module in modules:
			moduleName = "Olympus.modules." + module
			theModule = importlib.import_module(moduleName)
			# Instantiate the imported module
			className = moduleName.split(".")[-1]
			
			instantiatedNode = theModule.__dict__[className]()
			instantiatedNodes.append( instantiatedNode )
		
		self.instantiatedNodes = instantiatedNodes
		return instantiatedNodes
	
	
	def toGexf(self):
		""" Turns the currently processed graph into a GEXF file, if it exists. """
		if self.graph == None:
			return None
		else:
			# Since write_gexf does not output to a string, we will capture its output with a cStringIO instance.
			buffer = cStringIO.StringIO()
			nx.write_gexf(self.graph, buffer)
			value = buffer.getvalue()
			buffer.close()
			return value			
	
	def generateProcedure(self, nodes, edges, attributes):
		""" Creates a directed graph from the nodes and edges provided. Instead of the names, it will use instances of each of the modules
		
		:param nodes: A list of nodes.
		:param edges: A list of 2-tuples containing the edges. If a node is mentioned here but not in `nodes` it will be created.
		:param attributes: A dictionary of attributes for each edge, should correspond in order with the edges list.
		:rtype: A networkx (Di)Graph object
		"""		

		instantiatedNodes = self.importModules(nodes)
		instantiatedNodes.append("start")

		instantiatedEdges = []
		
		colors = []

		e = 0
		for edge in edges:
			newEdge = []
			for node in edge:
				if node in nodes:
					newEdge.append(instantiatedNodes[nodes.index(node)])
				else:
					newEdge.append(node)
			newEdge.append(attributes[e])	
			instantiatedEdges.append(tuple(newEdge))
			e+=1

		graph = nx.DiGraph()
		graph.add_nodes_from(instantiatedNodes)
		graph.add_edges_from(instantiatedEdges, color="blue")
		self.graph = graph
		return graph
	
	def generateInterface(self):
		html = XHTML()
		form = html.form("", role="form")
		
		for node in self.instantiatedNodes:
			if node == "start":
				continue;
			
			fieldset = form.fieldset("", klass="set-"+str(node))
			fieldset.legend(str(node))			
			
			controls = node.specifyControls()
			if controls == None:
				fieldset.p("No controls specified for this module.")
				continue;
				
				
			for key, control in controls.items():
				group = fieldset.div(klass="form-group")
				theControl = control.toHTML()
				
				name = control.name
				if control.name == None:
					name = "undefined"
				
				label = group.label(control.label)
				label._attrs["for"] = "control-"+name;
				group += theControl
		
		form.input(type="submit",value="Submit", klass="btn btn-default")
				
		return str(form)
	
