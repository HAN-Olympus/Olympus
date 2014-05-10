class TemplateTools():
	""" This class contains a variety of functions that are useful when rendering templates. """
	
	def __init__(self):
		self.deferredJavascript = []
		
	def deferJS(self, url, position=0):
		""" Defers loading a script to when the page has loaded, in the order defined by `position`. 
		
		:param url: The URL of the script.
		:param position: The position in the order of scripts to load. Use this to make sure libraries load later than scripts using them.
		"""
		self.deferredJavascript.append( ( url, position ) )
		
	def renderJS(self):
		""" Renders all the deferred Javascript scripts that were added by deferJS. 
		
		:rtype: A string of <script> tags in their defined order.
		"""
		html = []
		seen = set()
		dJS = []		
		for url, position in self.deferredJavascript:
			if url not in seen:
				dJS.append((url,position))
				seen.add(position)
		
		dJS.sort(key=lambda s: s[1])		
		
		for script in dJS:
			html.append( "<script src='%s' defer></script>" )
			
		return "\n".join(html)