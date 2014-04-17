$(function() {
	
	// Bereken de overlap tussen twee arrays
	function intersect(a, b) {
		var t;
		if (b.length > a.length) t = b, b = a, a = t; // indexOf to loop over shorter
		for (ai in a){
			aa = a[ai]
			for( bi in b){
				bb = b[bi]
				if (aa.length == 0 || bb.length == 0) {
					return false
				}				
				if (bb.indexOf(aa) !== -1) {
					return true
				} else if (aa.substr(0, aa.indexOf("[")) == bb.substr(0, bb.indexOf("["))) {
					console.log("Same class")
					// These are at least the same class
					if( aa[aa.indexOf("[")+1] == "]" || bb[bb.indexOf("[")+1] == "]" ) {
						return true
					}
					
				}
			}
		}
	}
	
	function rgb2hex(rgb) {
		rgb = rgb.match(/^rgb\((\d+),\s*(\d+),\s*(\d+)\)$/);
		function hex(x) {
			return ("0" + parseInt(x).toString(16)).slice(-2);
		}
		return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
	}
	
	function findConnections( e , removeValid) {
		isLastRow = $(e).parent().parent().is(".row:last")
		if ( isLastRow ) {
			redrawInputs(e);
			redrawOutputs(e);
		} else {
			$(e).find(".module-connection").remove();
			$(e).find(".module-output").addClass("no-destination")
		}
	}
	
	function redrawOutputs( e, removeValid ) {
		console.log("Redrawing outputs")
		console.log(e)
		// For every output
		$(e).find(".module-output").each(function() {
			output = $(this)
			console.log(output)
			output.removeClass("no-destination destination-found");
			outputs = $(this).data("accept").split(",");
			connection = $("<img>");
			connection.attr("class","module-connection");
			
			// Remove all the current connections, we'll redraw them later
			$(this).find(".module-connection").remove()
			
			destinationFound = false;
			
			// Now find all the modules in the row next to this one
			$(e).parent().next().find(".module-item").each( function() {
				
				// Get all the accepting ports
				$(this).find(".module-accept").each(function() {
					// Get all the formats the port accepts
					inputs = $(this).data("accept").split(",");
					intersects = intersect( inputs,outputs);
					
					
					if( intersects ) {
						// These modules can communicate with each other, draw a connection
						y =  $(this).offset().top - output.offset().top + 10
						if( y > 0 ) {
							src = "/svg/connection?x1=0&y1=0&x2=55&y2="+parseInt(y)+"&fill=428bca"
							connection.addClass("connect-top")
						} else {
							src = "/svg/connection?x1=0&y1="+Math.abs(parseInt(y))+"&x2=55&y2=0"
							connection.addClass("connect-bottom")
						}
						
						if( output.hasClass("connection-approved") ) {
							src += "&fill=#dff0d8"
						} else {
							src += "&fill=428bca"
						}
						
						// Change the source of the connection image
						connection.attr("src",src)
						destinationFound = true;
						
						console.log(y, src)
						output.append(connection)
						output.data("target",$(this))
					}
					
				});
			});
			
			if(!destinationFound) {
				output.addClass("no-destination");
			} else {
				output.addClass("destination-found");
			}
		});
	}
	
	function redrawInputs( e ) {
		console.log($(e))
		console.log( $(e).parent().prev().children(".module-container") )
		redrawOutputs($(e).parent().prev().children(".module-container"))
	}
	
	$(".module-container").each(function() {
		/* Match the containers with one another */
		sisterContainerName = "." + $(this).parent().attr("class").replace(/ /g,".") + " .module-container"
		
		// jQuery UI sortable used to allow easy drag-and-drop interaction
		$(this).sortable({
			connectWith: sisterContainerName,
			placeholder: "panel panel-primary",
			axis : "y",
			handle : ".panel-heading",
			receive: function( event, ui ) {
				findConnections(this, true);
			},
			change: function( event, ui ) {
				findConnections(this, false);
			},
			update: function( event, ui ) {
				findConnections(this, false);
			}
		}).disableSelection();
	});
	
	function changeConnectionColor( connection, fill ) {
		src = connection.attr("src")
		console.log(src)
		src = src.split("&fill=")[0]
		console.log(src)
		src += "&fill=" + fill
		console.log(src)
		connection.attr("src", src)
	}
	
	$(".module-output").bind("click contextmenu", function(event) {
		if($(this).hasClass("no-destination")) {
			return false;
		}
		target = $(this).data("target").parent().find(".panel")
		current = $(this).parent().find(".panel")
		console.log(target)
		
		if(event.which == 1) {
			// Regular left mouse click
			if($(this).hasClass("destination-confirmed") || $(this).hasClass("destination-removed")) {
				// Switch to destination found - this will turn the modules blue
				target.removeClass("panel-success");
				target.removeClass("panel-danger");
				current.removeClass("panel-success");
				current.removeClass("panel-danger");
				target.addClass("panel-primary");
				current.addClass("panel-primary");
				$(this).removeClass("destination-confirmed");
				$(this).removeClass("destination-removed");
			} else  {
				// Switch to destination confirmed - this will turn the modules green
				target.removeClass("panel-primary");
				current.removeClass("panel-primary");
				target.addClass("panel-success");
				current.addClass("panel-success");
				$(this).addClass("destination-confirmed");
			}
		} else if (event.which == 3) {
			// Switch to destination removed - this will turn the modules red
			target.removeClass("panel-primary");
			current.removeClass("panel-primary");
			target.removeClass("panel-success");
			current.removeClass("panel-success");
			target.addClass("panel-danger");
			current.addClass("panel-danger");
			$(this).addClass("destination-removed");
		}
		
		bgcolor = current.find(".panel-heading").css("background-color")
		color = current.find(".panel-heading").css("color")
		
		$(this).css({"background-color": bgcolor, "color":color});
		changeConnectionColor( $(this).find(".module-connection"), rgb2hex(bgcolor).substr(1) );
		
	});
	
	
	$(".move-module-down").click(function() {
		// Moves the module down
		listBelowClass = "." + $(this).parents(".col").attr("class").replace(/ /g, ".")
		listBelow = $(listBelowClass).last().find(".module-container")
		
		console.log(listBelowClass)
		console.log(listBelow)
		$(this).parents(".module-item").appendTo(listBelow)		
		
	});
});
