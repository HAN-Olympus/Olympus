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
	
	// Start the Force Atlas Algorithm
	sigInst.startForceAtlas2();
	
	//
	$.getJSON("/compiler/"+window.location.search, function(response) {
		console.log(response);
		$(".btn.download").attr("disabled",false).attr("href", "/downloadCompiled/"+response["id"])
		$("h2").append("Done.")
		// We can stop drawing when we're done compiling.
		sigInst.stopForceAtlas2();
	});
	
	
});
