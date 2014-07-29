"""
@name Routes
@author Stephan Heijl
@module core
@version 0.1.0
"""

from flask import Flask, render_template, abort, Response, request, redirect, url_for
import os,re,sys
import pkgutil

from Olympus.lib.Config import Config
from Olympus.lib.TemplateTools import TemplateTools
from Olympus.lib.Output import Output
from Olympus.lib.Procedure import Procedure
from Olympus.core.WorkerMonitor import WorkerMonitor
from Olympus.core.ModuleLoader import ModuleLoader

import svglib
import gearman
import json
import zipfile
import cStringIO
import requests

from Olympus.webapp import app, modules

# ONLY IMPORT THESE IF THE APP IS NOT IN TOOL MODE: #
if "--tool" not in sys.argv:
	from Olympus.core.Compiler import Compiler

# LOAD TEMPLATE TOOLS #
tools = TemplateTools()
for attribute in dir(tools):
	if not attribute.startswith("__") and hasattr(getattr(tools, attribute), "__call__"):
		app.jinja_env.globals[attribute] = getattr(tools, attribute)

# ROUTES #

@app.route("/")
def index():
	return render_template("index.html", name=index)
	
@app.route("/css/<filename>")
def loadCss(filename):
	path = os.path.join(Config().WebAppDirectory, "css", filename)
	pathBootstrap = os.path.join(Config().WebAppDirectory, "bootstrap", "css", filename)
	if os.path.isfile(path):
		cssFile = open(path)
	elif os.path.isfile(pathBootstrap):
		cssFile = open(pathBootstrap)
	else:
		abort(404)

	css = cssFile.read()
	cssFile.close()
	return Response(css, mimetype="text/css")

@app.route("/js/<filename>")
def loadJs(filename):
	path = os.path.join(Config().WebAppDirectory, "js", filename)
	pathBootstrap = os.path.join(Config().WebAppDirectory, "bootstrap", "js", filename)
	if os.path.isfile(path):
		jsFile = open(path)
	elif os.path.isfile(pathBootstrap):
		jsFile = open(pathBootstrap)
	else:
		abort(404)
		
	js = jsFile.read()
	jsFile.close()
	return Response(js, mimetype="application/javascript")
	
@app.route("/img/<filename>")
def loadImg(filename):
	path = os.path.join(Config().WebAppDirectory, "img", filename)
	pathBootstrap = os.path.join(Config().WebAppDirectory, "bootstrap", "img", filename)
	if os.path.isfile(path):
		imgFile = open(path)
	elif os.path.isfile(pathBootstrap):
		imgFile = open(pathBootstrap)
	else:
		abort(404)
		
	img = imgFile.read()
	imgFile.close()
	return Response(img, mimetype="image/jpeg")	

@app.route("/favicon")
def loadFavicon():
	# Loads the favicon based on the build status of according to Travis
	# Change this to get the results from another repository.
	
	travisUrl = "https://api.travis-ci.org/repositories/HAN-Olympus/Olympus.json"
	filename = "favicon.png"
	try:
		r = requests.get(travisUrl)
		data = r.json()

		if data["last_build_result"] == 1: # Something went wrong with the build.
			filename = "favicon-red.png"
		if data["last_build_result"] == 0: # Build passed
			filename = "favicon-green.png"
	except:
		pass # Ignore errors, just use the default icon.
	
	path = os.path.join(Config().WebAppDirectory, "img", filename)
	imgFile = open(path)
	img = imgFile.read()
	imgFile.close()
	return Response(img, mimetype="image/png")	

@app.route("/fonts/<filename>")
def loadFont(filename):
	path = os.path.join(Config().WebAppDirectory, "fonts", filename)
	pathBootstrap = os.path.join(Config().WebAppDirectory, "bootstrap", "fonts", filename)
	if os.path.isfile(path):
		fontFile = open(path)
	elif os.path.isfile(pathBootstrap):
		fontFile = open(pathBootstrap)
	else:
		abort(404)
		
	font = fontFile.read()
	fontFile.close()
	return Response(font, mimetype="font/ttf")	

@app.route("/<filename>")
def loadPage(filename):
	if os.path.isfile("templates/%s" % filename):
		return render_template(filename, name=filename)
	else:
		abort(404)
		return False;
	
@app.route("/interface")
def interface():	
	# Get all the enabled modules
	enabledModules = Config().modules["enabled"]
	# The amount of modules category columns
	colCount = len([ 1 for c in enabledModules if len(enabledModules[c]) > 0])
	return render_template("picker.html", config=Config(), name="picker", colCount=colCount, modules=modules )	
	
@app.route("/svg/connection")
def connection():
	x1 = int(request.args.get("x1"))
	y1 = int(request.args.get("y1"))
	x2 = int(request.args.get("x2"))
	y2 = int(request.args.get("y2"))
	fill = request.args.get("fill")
	stroke = request.args.get("stroke")
	
	connection = svglib.Connection(x1,y1,x2,y2, stroke, fill)
	
	return Response(connection.draw(), mimetype="image/svg+xml")
	
@app.route("/gexf/")
def graphGefx():
	nodes = json.loads( request.args.get("nodes") )
	edges = json.loads( request.args.get("edges") )
	attributes = json.loads( request.args.get("edgeAttributes") )
	
	p = Procedure( nodes, edges, attributes )
	return Response(p.toGexf())

@app.route("/compile/")
def compile():
	""" Shows the compilation page to the user. """
	nodes = json.loads( request.args.get("nodes") )
	edges = json.loads( request.args.get("edges") )
	attributes = json.loads( request.args.get("edgeAttributes") )
	
	p = Procedure( nodes, edges, attributes )
	
	return render_template("results.compiled.html", procedure=p)

@app.route("/compiler/")
def compiler():
	""" Does the actual compiling. """
	nodes = json.loads( request.args.get("nodes") )
	edges = json.loads( request.args.get("edges") )
	attributes = json.loads( request.args.get("edgeAttributes") )
	
	p = Procedure( nodes, edges, attributes )
	C = Compiler(p)
	module = C.retrieveModule("modules.acquisition.PubMed")
	C.scanDependencies(module)
	C.processDependencies()
	id = C.buildDist()
	return Response(json.dumps({"id":id}))

@app.route("/downloadCompiled/<id>")
def downloadCompiled(id):
	""" Zips the Build directory for this distribution and allows the user to download it. """
	f = cStringIO.StringIO() # We want to read the pure contents of this file, so we load it in memory.
	z = zipfile.ZipFile(f, 'w')
	
	directory = os.path.join( Config().WebAppDirectory, "tmp", "build-%s" % id )
	for root, dirs, files in os.walk(directory):
		for file in files:
			if file.endswith(".egg"): # Just add the .egg
				path = os.path.join(root, file)
				z.write(path, path.replace(directory, ""))
	
	# Add ToolInstaller.py as install.py
	installer = os.path.join(Config().RootDirectory,"core", "ToolInstaller.py")
	z.write(installer, "install.py")
	
	# And include the requirements.
	requirements = os.path.join(Config().RootDirectory,"..", "requirements.txt")
	z.write(requirements, "requirements.txt")

	z.close()

	return Response(f.getvalue(), mimetype="application/zip")

	
@app.route("/results/<job>/")
def resultsOverview(job):
	""" Shows a list of all the available outputs of this job. """
	
	out = Output().getByJobId(str(job))
	if len(out) > 0:
		return render_template("results.list.html", config=Config(), outputs=out[0].output.keys())
	else:
		return render_template("results.notfound.html", config=Config())
	
@app.route("/results/<job>/<output>")
def results(job, output):
	""" Show the output of a job in a given format. """
	
	out = Output().getByJobId(str(job))
	if len(out) > 0:
		#return Response(str(out))
		return Response(out[0].getAttribute("output",output))
	else:
		return render_template("results.notfound.html", config=Config())


# This is for the ModuleLoader interface #
@app.route("/moduleLoader")
def moduleLoader():
	""" Renders the ModuleLoader interface """
	return render_template("moduleloader.html", config=Config(), loader=ModuleLoader(), modules=modules)

@app.route("/moduleLoader/setEnabled")
def setEnabledModules():
	""" Sets the modules that are enabled. """
	modules = {}
	for module in json.loads(request.args.get("enabled")):
		category, name = module.split(".")
		if category not in modules:
			modules[category] = []
		modules[category].append(name)
	
	# If currently available category has not been sent, remember tot disable it fully.
	for cat in Config().modules["enabled"]:
		if cat not in modules.keys():
			modules[cat] = []
	
	for category, names in modules.items():
		print category, names
		ModuleLoader().setModules(category, names);
	
	return Response(json.dumps(True));
	
# This is for the Tool interface #
@app.route("/tool")
def tool():
	""" Renders the tool interface. """
	return render_template("tool.html", config=Config())

@app.route("/toolStart", methods=['GET', 'POST'])
def toolStart():
	""" Starts the tool locally. """
	procedure = Procedure.load( os.path.join( Config().RootDirectory, "tool.prc") )
	
	# Parse the arguments
	arguments = {}
	for key, value in dict(request.form).items():
		moduleName = key.split("-")[0]
		keyName = "-".join(key.split("-")[1:])
		if isinstance(value,list):
			value = value[0]
		
		if moduleName in arguments:
			arguments[moduleName][keyName] = value
		else:
			arguments[moduleName] = {keyName:value}
	
	print arguments
	id = procedure.run(arguments=arguments)
	return redirect("/results/%s/" % id)

@app.route("/toolQueue", methods=['GET', 'POST'])
def toolQueue(viewType):	
 	""" Puts the Procedure in the Gearman Queue. """
 	data = json.dumps({"nodes":request.args.get("nodes"), "edges":request.args.get("edges"), "edgeAttributes":request.args.get("edgeAttributes")})
	gm_client = gearman.GearmanClient(['localhost:4730'])
	job = gm_client.submit_job("runNewProcedure", data, background=True)
	
	return render_template("submitted.html", config=Config(), id=job.gearman_job.unique )
	
# This is for the WorkerMonitor interface #

@app.route("/workermonitor/")
def workermonitor():
	return render_template("wmonitor.html", config=Config())

@app.route("/workermonitor/gearman-status")
def wmGearmanStatus():
	return Response( json.dumps( WorkerMonitor().getGearmanStatus() ) )

@app.route("/workermonitor/gearman-workers")
def wmGearmanWorkers():
	return Response( json.dumps( WorkerMonitor().getGearmanWorkers() ) )

@app.route("/workermonitor/gearman-ping")
def wmGearmanPing():
	return Response( json.dumps( WorkerMonitor().getGearmanPing() ) )

@app.route("/workermonitor/gearman-start-worker")
def wmGearmanStartWorker():
	return Response( json.dumps( WorkerMonitor().startNewWorker() ) )

@app.route("/workermonitor/change-server/")
def wmChangeServer():
	ip = request.args.get("serverIP")
	if ip == "":
		ip = "localhost"
	WorkerMonitor().setGearmanServer(ip,request.args.get("serverPort"))
	return redirect(url_for("workermonitor"))

# TESTING #
def test_loadJs():
	assert loadJs("bootstrap.min.js"), "Could not load necessary JS file."
	
def test_loadCss():
	assert loadCss("style.css"), "Could not load necessary CSS file."

def test_loadFont():
	assert loadFont("glyphicons-halflings-regular.woff"), "Could not load necessary Font file."

