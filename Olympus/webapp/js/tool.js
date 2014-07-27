$(function () {
	$("fieldset").each(function () {
		setName = $(this).attr("class").substr(4);
		$(this).find("input,select").each(function () {
			newName = setName + "-" + $(this).attr("name");
			$(this).attr("name", newName);
			$(this).attr("id", "control-" + newName);
		});
		$(this).find("label").each(function () {
			newFor = "control-" + setName + "-" + $(this).attr("for").substr(8);
			$(this).attr("for", newFor);
		});
	});
});