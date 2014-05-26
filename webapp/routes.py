from flask import Flask, render_template, abort, Response, request
import os,re,sys
import pkgutil

from Olympus.lib.Config import Config
from Olympus.lib.ProcedureContainer import ProcedureCollection
from Olympus.lib.TemplateTools import TemplateTools
from Olympus.lib.Output import Output

import svglib
import gearman
import json

from Olympus.webapp import app, modules

# LOAD TEMPLATE TOOLS #
tools = TemplateTools()
for attribute in dir(tools):
	if not attribute.startswith("__") and hasattr(getattr(tools, attribute), "__call__"):
		print attribute
		app.jinja_env.globals[attribute] = getattr(tools, attribute)

# ROUTES #

@app.route("/")
def index():
	return render_template("index.html", name=index)
	
@app.route("/css/<filename>")
def loadCss(filename):
	if os.path.isfile("css/%s" % filename):
		cssFile = open("css/%s" % filename)
	elif os.path.isfile("bootstrap/css/%s" % filename):
		cssFile = open("bootstrap/css/%s" % filename)
	else:
		abort(404)

	css = cssFile.read()
	cssFile.close()
	return Response(css, mimetype="text/css")

@app.route("/js/<filename>")
def loadJs(filename):
	if os.path.isfile("js/%s" % filename):
		jsFile = open("js/%s" % filename)
	elif os.path.isfile("bootstrap/js/%s" % filename):
		jsFile = open("bootstrap/js/%s" % filename)
	else:
		abort(404)
		
	js = jsFile.read()
	jsFile.close()
	return Response(js, mimetype="application/javascript")
	
@app.route("/img/<filename>")
def loadImg(filename):
	if os.path.isfile("img/%s" % filename):
		imgFile = open("img/%s" % filename)
	elif os.path.isfile("bootstrap/img/%s" % filename):
		imgFile = open("bootstrap/img/%s" % filename)
	else:
		abort(404)
		
	img = imgFile.read()
	imgFile.close()
	return Response(img, mimetype="image/jpeg")	

@app.route("/fonts/<filename>")
def loadFont(filename):
	if os.path.isfile("fonts/%s" % filename):
		fontFile = open("fonts/%s" % filename)
	elif os.path.isfile("bootstrap/js/%s" % filename):
		fontFile = open("bootstrap/js/%s" % filename)
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
	
	print modules
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

@app.route("/svg/graph")
def graph():
	pc = ProcedureCollection()
	graph = pc.createFromJSON(request.args.get("nodes"), request.args.get("edges"), request.args.get("edgeAttributes"))
	return Response(pc.createGraphPreviewSVG(graph), mimetype="image/svg+xml")
	
@app.route("/gefx/graph")
def graphGefx():
	pc = ProcedureCollection()
	graph = pc.createFromJSON(request.args.get("nodes"), request.args.get("edges"), request.args.get("edgeAttributes"))
	return Response(pc.createGefxPreview(graph), mimetype="image/svg+xml")

@app.route("/execute/<viewType>")
def execute(viewType):	
	""" Puts the Procedure in the Gearman Queue. """
	data = json.dumps({"nodes":request.args.get("nodes"), "edges":request.args.get("edges"), "edgeAttributes":request.args.get("edgeAttributes")})
	
	gm_client = gearman.GearmanClient(['localhost:4730'])
	job = gm_client.submit_job("runProcedure", data, background=True)
	
	svgUrl = "/svg/graph?nodes="+request.args.get("nodes")+"&edges="+request.args.get("edges")+"&edgeAttributes="+request.args.get("edgeAttributes")
	return render_template("submitted.html", config=Config(), id=job.gearman_job.unique, svgUrl=svgUrl )

	
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
	
	
@app.route("/executeDirect/<viewType>")
def executeDirect(viewType):	
	""" Executes the given procedure directly. """
	pc = ProcedureCollection()
	graph = pc.createFromJSON(request.args.get("nodes"), request.args.get("edges"), request.args.get("edgeAttributes"))
	
	viewTypes = { "html":"PlainHTML", "latex":"LaTeX", "csv":"CSV"}
	output = pc.traverseGraph(graph)
	vt = viewTypes[viewType]
	
	names = [ str(key) for key in output.keys() ]
	i = names.index(vt)
	result = output[output.keys()[i]]
	
	return Response(result)
	
# TESTING #
def test_loadJs():
	assert loadJs("bootstrap.min.js"), "Could not load necessary JS file."
	
def test_loadCss():
	assert loadCss("style.css"), "Could not load necessary CSS file."

def test_loadFont():
	assert loadFont("glyphicons-halflings-regular.woff"), "Could not load necessary Font file."

	