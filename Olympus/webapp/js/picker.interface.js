$(function () {

	// Bereken de overlap tussen twee arrays
	function intersect(a, b) {
		var t;
		if (b.length > a.length) t = b, b = a, a = t; // indexOf to loop over shorter
		for (ai in a) {
			aa = a[ai]
			for (bi in b) {
				bb = b[bi]
				if (aa.length == 0 || bb.length == 0) {
					return false
				}
				if (bb.indexOf(aa) !== -1) {
					return true
				} else if (aa.substr(0, aa.indexOf("[")) == bb.substr(0, bb.indexOf("["))) {
					// These are at least the same class
					if (aa[aa.indexOf("[") + 1] == "]" || bb[bb.indexOf("[") + 1] == "]") {
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

	function findConnections(e, removeValid) {

		if ($(e).parents(".row").is(".destination")) {
			redrawInputs(e);
			redrawOutputs(e);
		} else {
			$(e).find(".module-connection").remove();
			$(e).find(".module-output").addClass("no-destination")
		}

		if (removeValid) {
			$(e).find(".module-connection").remove();
			$(e).find(".module-output").addClass("no-destination")
		}

	}

	function redrawOutputs(e, removeValid) {
		// For every output
		$(e).find(".module-output").each(function () {
			output = $(this)
			output.removeClass("no-destination destination-found");
			outputs = $(this).data("accept").split(",");

			connections = $(this).find(".module-connection");
			if (connections.length == 0) {
				connection = $("<img>");
				var color = "428bca"
				connection.attr("class", "module-connection");
			} else {
				connection = connections.eq(0)
				var color = connection.attr("src").match(/\&fill=([\da-fA-F]{3,6})$/)[1];
				console.log(color);
			}

			$(this).find(".module-connection").remove()

			destinationFound = false;

			// Now find all the modules in the row next to this one
			$(e).parent().next().find(".module-item").each(function () {

				// Get all the accepting ports
				$(this).find(".module-accept").each(function () {
					// Get all the formats the port accepts
					inputs = $(this).data("accept").split(",");
					intersects = intersect(inputs, outputs);

					if (intersects) {
						// These modules can communicate with each other, draw a connection

						y = $(this).offset().top - output.offset().top + 10
						if (y > 0) {
							src = "/svg/connection?x1=0&y1=0&x2=55&y2=" + parseInt(y)
							connection.removeClass("connect-bottom")
							connection.addClass("connect-top")
						} else {
							src = "/svg/connection?x1=0&y1=" + Math.abs(parseInt(y)) + "&x2=55&y2=0"
							connection.removeClass("connect-top")
							connection.addClass("connect-bottom")
						}

						if (output.hasClass("connection-approved")) {
							src += "&fill=#dff0d8"
						} else {
							src += "&fill=" + color
						}

						// Change the source of the connection image
						connection.attr("src", src)
						destinationFound = true;

						console.log(src)
						output.append(connection)
						output.data("target", $(this))
					}

				});
			});

			if (!destinationFound) {
				output.addClass("no-destination");
			} else {
				output.addClass("destination-found");
			}
		});
	}

	function redrawInputs(e) {
		console.log($(e))
		console.log($(e).parent().prev().children(".module-container"))
		redrawOutputs($(e).parent().prev().children(".module-container"))
	}

	$(".module-container").each(function () {
		/* Match the containers with one another */
		sisterContainerName = "." + $(this).parent().attr("class").replace(/ /g, ".") + " .module-container"

		// jQuery UI sortable used to allow easy drag-and-drop interaction
		$(this).sortable({
			connectWith: sisterContainerName,
			placeholder: "panel panel-primary",
			axis: "y",
			handle: ".panel-heading",
			receive: function (event, ui) {
				findConnections(this, true);
			},
			change: function (event, ui) {
				findConnections(this, false);
			},
			stop: function (event, ui) {
				findConnections(this, false);
			}
		}).disableSelection();
	});

	function changeConnectionColor(connection, fill) {
		src = connection.attr("src")
		console.log(src)
		src = src.split("&fill=")[0]
		console.log(src)
		src += "&fill=" + fill
		console.log(src)
		connection.attr("src", src)
	}

	function changeConfirmedConnections(e, by) {
		if (e.data("confirmedConnections")) {
			cP = parseInt(e.data("confirmedConnections"))
			e.data("confirmedConnections", cP + by)
		} else {
			e.data("confirmedConnections", 0 + by)
		}
		return e.data("confirmedConnections")
	}

	$(".module-output").bind("click", function (event) {
		if ($(this).hasClass("no-destination")) {
			return false;
		}
		target = $(this).data("target").parent().find(".panel")
		current = $(this).parent().find(".panel")

		currentModuleItem = current.parents(".module-item")
		targetModuleItem = target.parents(".module-item")

		if ($(this).hasClass("destination-confirmed") || $(this).hasClass("destination-removed")) {
			// Switch to destination found - this will turn the modules blue
			$(this).removeClass("destination-confirmed");

			console.log(currentModuleItem.find(".destination-confirmed").length)

			changeConfirmedConnections(currentModuleItem, -1);
			if (currentModuleItem.data("confirmedConnections") == 0) {
				current.removeClass("panel-success");
				current.addClass("panel-primary");
			}
			changeConfirmedConnections(targetModuleItem, -1);
			if (targetModuleItem.data("confirmedConnections") == 0) {
				target.removeClass("panel-success");
				target.addClass("panel-primary");
			}

			bgcolor = $(".panel-primary .panel-heading").css("background-color");
			color = $(".panel-primary .panel-heading").css("color");

		} else {
			// Switch to destination confirmed - this will turn the modules green
			changeConfirmedConnections(currentModuleItem, 1);
			changeConfirmedConnections(targetModuleItem, 1);
			target.removeClass("panel-primary");
			current.removeClass("panel-primary");
			target.addClass("panel-success");
			current.addClass("panel-success");
			$(this).addClass("destination-confirmed");

			bgcolor = $(".panel-success .panel-heading").css("background-color")
			color = $(".panel-success .panel-heading").css("color")
		}

		$(this).css({
			"background-color": bgcolor,
			"color": color
		});
		changeConnectionColor($(this).find(".module-connection"), rgb2hex(bgcolor).substr(1));

	});

	// Moving the modules with the arrow
	$("body").on("click", ".move-module-down", function () {
		// Moves the module down
		listBelowClass = "." + $(this).parents(".col").attr("class").replace(/ /g, ".")
		listBelow = $(listBelowClass).last().find(".module-container")

		$(this).parents(".module-item").appendTo(listBelow);
		findConnections($(this).parents(".module-container"), false);
		$(this).removeClass("move-module-down").addClass("move-module-up");
		$(this).find(".glyphicon").removeClass("glyphicon-arrow-down").addClass("glyphicon-arrow-up")
	});

	$("body").on("click", ".move-module-up", function () {
		moduleItem = $(this).parents(".module-item")
		if (moduleItem.find(".panel").hasClass("panel-success")) {
			alert("This module is connected. It cannot be removed without disabling the connection.");
			return false;
		}

		// Moves the module back up
		currentList = $(this).parents(".module-container")
		listAboveClass = "." + $(this).parents(".col").attr("class").replace(/ /g, ".")
		listAbove = $(listAboveClass).first().find(".module-container")
		console.log(listAbove);

		moduleItem.appendTo(listAbove);
		findConnections(currentList, false);
		findConnections(moduleItem, true);

		moduleItem.data("confirmedConnections", 0)
		$(this).removeClass("move-module-up").addClass("move-module-down");
		$(this).find(".glyphicon").removeClass("glyphicon-arrow-up").addClass("glyphicon-arrow-down")
	});

	// Compiling the Procedure

	$("#btn-compile").click(function () {
		var nodes = [];
		var edges = [];
		var edgeAttributes = [];
		// Get all the found destinations columns
		$(".destination .module-output.destination-confirmed").each(function () {
			output = $(this).parents(".module-item")
			target = $(this).data("target").parent(".module-item")

			outputName = output.find(".module-name").text()
			targetName = target.find(".module-name").text()

			outputId = $(this).text();

			if ($.inArray(outputName, nodes) < 0) {
				nodes.push(outputName);
			}
			if ($.inArray(targetName, nodes) < 0) {
				nodes.push(targetName);
			}
			// Check if the output is in the first column
			if (output.parents(".destination .col").eq(0).index() == 0) {
				edgeAttributes.push({
					"outputId": ""
				});
				edges.push(["start", outputName])
			}

			edgeAttributes.push({
				"outputId": outputId.trim()
			});
			edges.push([outputName, targetName])

		});

		var nodes = JSON.stringify(nodes, null, "").replace(/(\\n|\\t| )/g,'')
		var edges = JSON.stringify(edges, null, "").replace(/(\\n|\\t| )/g,'')
		var edgeAttributes = JSON.stringify(edgeAttributes, null, "")
		console.log(nodes)
		console.log(edges)
		console.log(edgeAttributes)

		executeUrl = "/execute/html?nodes=" + nodes + "&edges=" + edges + "&edgeAttributes=" + edgeAttributes;
		window.open(executeUrl)
	});

});