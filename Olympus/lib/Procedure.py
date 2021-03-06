"""
@name Procedure
@author Stephan Heijl
@module core
@version 0.1.0
"""

from Olympus.lib.Output import Output
from Olympus.lib.Module import Module

from pprint import pprint, isreadable
import importlib
import networkx as nx
import cStringIO
import cPickle
import sys
import traceback
import time
from html import XHTML

class Procedure():
	def __init__(self, nodes, edges, attributes):
		self.nodes = nodes
		self.edges = edges
		self.attributes = attributes
		self.graph = None
		self.instantiatedNodes = []
		
		self.generateProcedure(nodes, edges, attributes)
		
	def importModules( self, modules ):
		""" Imports all the modules needed. Will also instantiate the class inside this module with the module name. 
		
		:param module: A list of modules in the Olympus package. Having 'Olympus.modules.' in front of these names is optional. 
		:rtype: A list objects, each an instance of the class inside the module with the module's name. """
		
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
		""" Turns the currently processed graph into a GEXF file, if a graph has already been generated.
		
		:rtype: A NetworkX generated GEXF file describing the graph. None if the graph has not yet been generated."""
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
		
		# We only need to import modules if there aren't any instantiated nodes yet.
		if len(self.instantiatedNodes) == 0:
			instantiatedNodes = self.importModules(nodes)
			instantiatedNodes.append("start")
		else:
			instantiatedNodes = self.instantiatedNodes

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


	def traverseGraph(self, graph, arguments={}):
		""" Use a Breadth-first search to work through the graph. This should allow even more complex graphs to be completed successfully.
		
		:param graph: A graph containing classes to execute.
		:param arguments: The arguments for each module, if appropiate.
		"""

		output = {}
		storedOutput = {}
		edges = list(self.bfs_edges(graph, "start"))
		
		outputBuffer = {}

		for edge in edges:
			parent = edge[0]
			child = edge[1]

			print "%s -> %s" % (parent, child)
			# Should contain an outputId, determining what exactly should be retrieved from the function call.
			
			attributes = edge[2]
			# Only start the node if it's actually a module...
			if not isinstance(child, Module) and not issubclass(child, Module):
				continue

			if not isinstance(parent, Module):				
				if str(child) in arguments.keys():
					print "Using arguments for: ",arguments[str(child)]
					output[child] = [child.start(**arguments[str(child)])]
				else:
					output[child] = [child.start()]
			else:
				argcount = child.start.func_code.co_argcount
				print 
				print child, argcount
				
				if argcount == 2:
					if child in output and isinstance(output[child], list):
						for c in output[parent]:
							output[child].append(child.start(c))
					else:
						output[child] = [child.start(c) for c in output[parent]]

				elif argcount > 2:
					if child in outputBuffer.keys() and len(outputBuffer[child]) == argcount-1:
						output[child] = [child.start(*outputBuffer[child])]
					if len(output[parent]) == argcount -1:
						output[child] = [child.start(*output[parent])]
					elif len(output[parent]) < argcount -1:
						for e in edges:
							if e[0] != parent and e[1] == child:
								if child not in outputBuffer:
									outputBuffer[child] = []
								outputBuffer[child].append(output[parent])
						
						if child in outputBuffer.keys() and len(outputBuffer[child]) < argcount-1:
							continue
						elif child in outputBuffer.keys() and len(outputBuffer[child]) == argcount-1:
							output[child] = [child.start(*outputBuffer[child])]
							continue
						else:
							while(len(output[parent]) < argcount -1):
								output[parent].append(None)
							
						print output[parent]
						output[child] = [child.start(*output[parent])]
						
						
					elif len(output[parent]) > argcount -1:
						output[parent] = output[parent][:argcount-1]
						output[child] = [child.start(*output[parent])]
				else:
					output[child] = None

		return output
	
	def generateControls(self):
		""" A method that will generate an HTML representation of all the controls for all the modules, if they have already been instantiated. 
		A form container will also be generated, as well as fieldsets for every individual module.
		
		:rtype: A complete HTML form with every control for every available module inserted. 
		"""
		
		html = XHTML()
		form = html.form("", role="form", action="/toolStart", method="post", enctype="multipart/form-data")		
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
				name = control.name
				if control.name == None:
					name = "undefined"
					
				control.name = str(node)+"-"+control.name
					
				theControl = control.toHTML()
				
				label = group.label(control.label)
				label._attrs["for"] = "control-"+name;
				group += theControl
		
		form.input(type="submit",value="Submit", klass="btn btn-default")
				
		return str(form)
	
	def generateProcedureInterface(self):
		""" Generates the interface for the procedure. """
		
		html = """ {% extends \"main.html\" %} {% block index %} <br/> <div class="container"> <div class='col-md-12'> """
		html += self.generateControls()
		html += """ </div></div> {% endblock %} """
		return html
	
	
	def run(self, arguments={}):
		print "Start traversing"
		try:
			output = self.traverseGraph(self.graph,arguments)
		except Exception, e:
			traceback.print_exc(file=sys.stdout)
		print "Done traversing"
		
		try:
			out = Output()
		except Exception, e:
			return False, traceback.print_exc(file=sys.stdout)
		
		out.job_id = str(int(time.time()))
		
		print output.items()
		
		for k,v in output.items():
			print k, len(v)
			if isinstance(v, list) and len(v)>0:
				out.addAttribute("output", unicode(k), unicode(v[0]))
			else:
				out.addAttribute("output", unicode(k), unicode(v))
			print k, len(v)
			try:
				out.save()
			except Exception, e:
				return False, traceback.print_exc(file=sys.stdout)
		try:
			out.save()
			return out.job_id
		
		except Exception, e:
			return False, traceback.print_exc(file=sys.stdout)
	
	def save(self, filename=None):
		""" Saves the procedure, with instantiated nodes. 
		
		:param filename: Optional. 
		:rtype: True if filename was provided and save was successful. A string containing the pickled document if no filename was provided.
		"""
		
		if filename:
			with open(filename,"wb") as f:
				cPickle.dump(self,f)
			return True
		else:
			return cPickle.dumps(self)
		
	@staticmethod
	def load(filename):
		""" Loads a procedure from a file. """
		print filename
		with open(filename,"rb") as f:
			procedure = cPickle.load(f)
		return procedure
	
def test_save():
	modules = ["acquisition.PubMed","interpretation.Sort"]
	p = Procedure(modules, [("acquisition.PubMed","interpretation.Sort")], [{}])
	p.importModules(modules)
	p.save()