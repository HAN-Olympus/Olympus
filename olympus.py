from flask import Flask, render_template, abort, Response
import os,re,sys


app = Flask(__name__)
print __name__

# VIEWS

@app.route("/")
def index():
	return render_template("index.html", name=index)
	
@app.route("/css/<filename>")
def loadCss(filename):
	if os.path.isfile("css/%s" % filename):
		cssFile = open("css/%s" % filename)
	elif os.path.isfile("vendor/assets/stylesheets/%s" % filename):
		cssFile = open("vendor/assets/stylesheets/%s" % filename)
	else:
		abort(404)		
		
	css = cssFile.read()
	cssFile.close()
	return Response(css, mimetype="text/css")
	
@app.route("/js/<filename>")
def loadJs(filename):
	if os.path.isfile("js/%s" % filename):
		jsFile = open("js/%s" % filename)
	elif os.path.isfile("vendor/assets/javascripts/%s" % filename):
		jsFile = open("vendor/assets/javascripts/%s" % filename)
	else:
		abort(404)
		
	js = jsFile.read()
	jsFile.close()
	return Response(js, mimetype="application/javascript")
	
@app.route("/pdb/<filename>")
def loadPdb(filename):
	print filename

	if re.match("^[a-zA-Z0-9]{1,4}\.pdb$", filename):
		if os.path.isfile("pdb/%s" % filename):
			pdbFile = open("pdb/%s" % filename)
		else:
			abort(404)		
			
		pdb = pdbFile.read()
		pdbFile.close()
	
	elif re.match("^([^J][0-9BCOHNSOPrIFla@+\-\[\]\(\)\\\/%=#$,.~&!]{3,})$", filename, flags=re.IGNORECASE):
		pdb = convertSmilesToPDB(str(filename).strip("pdb/"))
		
	else:
		abort(404);
	
	return Response(pdb, mimetype="chemical/x-pdb")

@app.route("/<filename>")
def loadPage(filename):
	return render_template(filename, name=filename)
	
		
# TESTING #

def test_loadJs():
	assert loadJs("bootstrap.min.js"), "Could not load necessary JS file. There is something wrong with the loadJs method."
	
def test_loadCss():
	assert loadCss("style.css"), "Could not load necessary CSS file. There is something wrong with the loadCss method."

def test_loadPdb():
	assert loadPdb("I3.pdb"), "Could not load test PDB file. There is something wrong with the loadPdb method."
	assert loadPdb("CCc1nn(C)c2c(=O)[nH]c(nc12)c3cc(ccc3OCC)S(=O)(=O)N4CCN(C)CC4"), "Could not load SMILES sequence."
	
if __name__ == "__main__":
    app.run()