$(function () {
	// Expanding the module descriptions
	$("body").on("click", ".expand-module-description", function () {
		var module = $(this).parents(".module-item").find(".panel-body")
		if (!module.attr('data-maxHeight')) {
			maxHeight = parseInt(module.css("max-height"));
		}
		normalHeight = module.css({
			"max-height": "none",
			"height": "auto"
		}).height();
		module.attr("data-maxHeight", maxHeight);
		module.css("height", maxHeight);
		module.animate({
			"height": normalHeight
		}, 300);
		$(this).addClass("contract-module-description");
		$(this).removeClass("expand-module-description");
	});

	// Contract the module descriptions
	$("body").on("click", ".contract-module-description", function () {
		var module = $(this).parents(".module-item").find(".panel-body")
		maxHeight = parseInt(module.attr("data-maxHeight"));
		module.animate({
			"height": maxHeight
		}, 300);
		$(this).removeClass("contract-module-description");
		$(this).addClass("expand-module-description");
	});


	$("body").on("click", ".enable-module", function () {
		$(this).removeClass("enable-module").addClass("disable-module");
		$(this).children(".glyphicon").removeClass("glyphicon-ok").addClass("glyphicon-remove");
		var module = $(this).parents(".panel").removeClass("panel-primary").addClass("panel-success");
		module.parents(".module-item").attr("data-enabled", "true");
	});

	$("body").on("click", ".disable-module", function () {
		$(this).addClass("enable-module").removeClass("disable-module");
		$(this).children(".glyphicon").addClass("glyphicon-ok").removeClass("glyphicon-remove");
		var module = $(this).parents(".panel").addClass("panel-primary").removeClass("panel-success");
		module.parents(".module-item").attr("data-enabled", "false");
	});

	$(".submit").click(function () {
		var enabled = [];
		$(".module-item[data-enabled=true]").each(function () {
			enabled.push($(this).find(".module-name").text().trim());
		});
		console.log(enabled);
		$.get("/moduleLoader/setEnabled?enabled=" + JSON.stringify(enabled), function (data) {
			if (data == "true") {
				alert("Module configuration set.");
			}
		});
	});
});