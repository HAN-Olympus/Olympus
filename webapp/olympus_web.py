from flask import Flask, render_template, abort, Response
import os,re,sys


app = Flask(__name__)

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
	return Response(font, mimetype="application/javascript")	

@app.route("/<filename>")
def loadPage(filename):
	if os.path.isfile("template/%s" % filename):
		return render_template(filename, name=filename)
	else:
		abort(404)
		return False;

		
# TESTING #

def test_loadJs():
	assert loadJs("bootstrap.min.js"), "Could not load necessary JS file."
	
def test_loadCss():
	assert loadCss("style.css"), "Could not load necessary CSS file."

def test_loadFont():
	assert loadFont("glyphicons-halflings-regular.woff"), "Could not load necessary Font file."

	
if __name__ == "__main__":
    app.run()