$(function() {
   // Instantiate sigma.js and customize rendering :
  var sigInst = sigma.init(document.getElementById('sigma-container')).drawingProperties({
    defaultLabelColor: '#fff',
    defaultLabelSize: 14,
    defaultLabelBGColor: '#fff',
    defaultLabelHoverColor: '#000',
    labelThreshold: 6,
    defaultEdgeType: 'direct',
    defaultEdgeArrow: 'target',
    defaultEdgeColor: 'default',
    defaultNodeColor: 'default'
  }).graphProperties({
    minNodeSize: 2,
    maxNodeSize: 7,
    minEdgeSize: 2,
    maxEdgeSize: 2
  }).mouseProperties({
    maxRatio: 32
  });
 
  // Parse a GEXF encoded file to fill the graph
  // (requires "sigma.parseGexf.js" to be included)
  sigInst.parseGexf('/gexf/'+window.location.search);
  
  sigInst.iterNodes(function (n) {
			n.size += (n.inDegree + n.outDegree)
		})
 
  // Draw the graph :
  sigInst.draw();
  
  sigInst.startForceAtlas2();
  
  setTimeout(function () {
		sigInst.stopForceAtlas2();
  },2500);
	
});