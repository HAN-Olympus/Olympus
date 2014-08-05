$(function () {
	$(".server-form-submit").click(function () {
		var data = {};

		/* Mongo server */
		var mongAddr = $("input[name=mongo-addr]").val();
		var mongPort = $("input[name=mongo-port]").val();
		if (mongAddr.length == 0) {
			mongAddr = "localhost"
		}
		if (mongPort.length == 0) {
			mongPort = "27017"
		}

		var mongoServer = mongAddr + ":" + mongPort;

		/* Gearman servers */
		var gearmanServers = [];

		$(".gearman-server").each(function () {
			var gearAddr = $(this).find("input[name=gear-addr]").val();
			var gearPort = $(this).find("input[name=gear-port]").val();
			var gearmanServer = gearAddr + ":" + gearPort;
			if (gearmanServer.length > 1) {
				gearmanServers.push(gearmanServer);
			}
		});

		/* Assign data */
		data.mongoServer = mongoServer;
		data.gearmanServers = gearmanServers;

		$.getJSON("/select-server/submit", {
				"data": JSON.stringify(data)
			},
			function () {
				alert("Data was set.");
				location.reload(true);
			}
		);
	});
})