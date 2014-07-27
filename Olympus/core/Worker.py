"""
@name Worker
@author Stephan Heijl
@module core
@version 0.1.0
"""

import gearman
import subprocess
import json
import sys
import traceback
import pickle

from Olympus.lib.Config import Config
from Olympus.lib.Output import Output
from Olympus.lib.Procedure import Procedure

class PickleDataEncoder(gearman.DataEncoder):
    @classmethod
    def encode(cls, encodable_object):
        return pickle.dumps(encodable_object)

    @classmethod
    def decode(cls, decodable_string):
        return pickle.loads(decodable_string)

class Worker():
	""" This is the default worker for Olympus. This worker's job methods cannot rely on `self`, as that would impair them from functioning as a standalone task."""
	def job_runNewProcedure(worker, job):
		print job.unique
		data = json.loads(job.data)
		print "Starting"
		print data
		
		pc = Procedure()
		print "Procedure instantiated, creating graph"
				
		try:
			graph = pc.createFromJSON(data["nodes"], data["edges"], data["edgeAttributes"]) # Create the graph
		except Exception, e:
			traceback.print_exc(file=sys.stdout)
		
		print "Start traversing"
		try:
			output = pc.traverseGraph(graph)
		except Exception, e:
			traceback.print_exc(file=sys.stdout)
		print "Done traversing"
		
		try:
			out = Output()
		except Exception, e:
			print e
		
		out.job_id = job.unique
		
		for k,v in output.items():
			print k, len(v)
			if isinstance(v, list) and len(v)>0:
				out.addAttribute("output", str(k), str(v[0]))
			else:
				out.addAttribute("output", str(k), str(v))
			print k, len(v)
			try:
				out.save()
			except Exception, e:
				print e
		
		try:
			out.save()
		except Exception, e:
			print e
		return ""
	
def registerFunctions(workerClass, worker):
	"""  Assigns all functions starting with 'job\_' to the gearman worker, similar to how `nosetests` uses all methods starting with 'test'.
	
	:param workerClass: The instance containing the functions that need to be registered. The class should already be instantiated!
	:param worker: The GearmanWorker instance these functions need to be assigned to.
	"""
	for attribute in dir(workerClass):
		if attribute.startswith("job_"):
			method = getattr(workerClass,attribute)
			if hasattr(method, '__call__'): # Check if the attribute is a function
				worker.register_task(attribute[4:], method.__func__)
				print attribute, "registered as", attribute[4:]
			
def welcome():
	""" Displays a welcome message on screen. """
	msg = "Welcome to the Olympus Gearman Worker."
	print
	print msg
	print "="*len(msg)
	print 
	print "Gearman Queue:"
	print "-"*len(msg)
	print "name\tqueued\trunning\tworkers"
	gearadmin = subprocess.Popen("gearadmin --status", shell=True) # Shows the current Gearadmin output.
	gearadmin.communicate()
	print "-"*len(msg)
	print 	
	print "Working..."
	print
	
if __name__ == "__main__":	
	# Instantiate the worker and register all the appropiate functions.
	gm_worker = gearman.GearmanWorker(Config().GearmanServer) # Creates the worker on the default port.
	gm_worker.data_encoder = PickleDataEncoder
	
	# Print a welcome message
	if not "--silent" in sys.argv:
		welcome()
		
	gm_worker.work() # Enter the work loop
	
# TESTING #
def test_registerFunctions():
	gm_worker = gearman.GearmanWorker(Config().GearmanServer) # Creates the worker on the default port.
	registerFunctions(Worker(), gm_worker)
