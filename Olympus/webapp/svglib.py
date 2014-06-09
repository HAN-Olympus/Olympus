""" SVG drawings library """

class Connection():
	def __init__(self, x1,y1,x2,y2,stroke="#FFFFFF", fill="#000000"):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.stroke = stroke
		self.fill = fill
		self.connectSize = 22
		self.width = abs(x1-x2) + self.connectSize
		self.height =  abs(y1-y2)  + self.connectSize
		self.svg = """<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
width="%spx" height="%spx" viewBox="0 0 %s %s" xml:space="preserve">
""" % (self.width, self.height, self.width, self.height)
	
	def isWholeNumber(self,n):
		return float(n).is_integer()
	
	def draw(self):
		
		line = "<path class=\"connection\" fill=\"#%s\" stroke=\"#%s\" d=\"" % (self.fill, self.stroke)
		
		if self.isWholeNumber(self.x1):
			self.x1-=0.5
		if self.isWholeNumber(self.x2):
			self.x2+=0.5
		
		line += "M%s,%s " % (self.x1, self.y1)
		ml = self.x1 + (abs(self.x1 - self.x2)*0.55)
		mr = self.x2 - (abs(self.x1 - self.x2)*0.55)
		line += "C %s %s, %s %s, %s %s" % (ml, self.y1, mr, self.y2, self.x2, self.y2)
		line += "L%s %s" % (self.x2,self.y2+self.connectSize)
		line += "C %s %s, %s %s, %s %s" % (mr, self.y2+self.connectSize, ml, self.y1+self.connectSize, self.x1, self.y1+self.connectSize)
		
		line += "Z"
		
		line += "\"></path>"
		
		self.svg += line + "</svg>"
		return self.svg