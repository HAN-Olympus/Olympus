$(function() {
	
	function checkGearmanState() {
		// Check the initial Gearman state.
		$.getJSON("/workermonitor/gearman-status", function(data) {
			if(!data) {
				// Hide the non-error state alerts
				$(".gearman-state.alert-success, .gearman-state.alert-warning").hide(0);
				$(".gearman-state.alert-danger").show(0);
				$(".btn.create").attr("disabled", true);
				return false;
			}
			if(data.length == 0 || data[0]["workers"] == 0) {
				// Gearman lives, but no workers.
				$(".gearman-state.alert-success, .gearman-state.alert-danger").hide(0);
				$(".gearman-state.alert-warning").show(0);
				return false;
			}
			// Gearman lives and there are workers.
			$(".gearman-state.alert-warning, .gearman-state.alert-danger").hide(0);
			$(".gearman-state.alert-success").show(0);
			$(".gearman-state.alert-success .worker-count").text( data[0]["workers"] )
			
			$.getJSON("/workermonitor/gearman-workers", function(data) {		
				createWorkerPanels(data);
			});
			
		});
		

		/* Get the ping */
		$.getJSON("/workermonitor/gearman-ping", function(data) {
			var width = (getPingRating(data*1000)*25) + "%";
			$(".signal").css("width", width );
		});

	}

	function createWorkerPanels(workers) {
		var wc = $(".worker-container");
		wc.find(".worker").not(".proto-worker").remove()
		$.each(workers, function(index, worker) {
			w = $(".proto-worker").clone()
			w.removeClass("proto-worker").appendTo(wc);
			w.find(".worker-id").text(worker.file_descriptor)
			w.find(".worker-task").text(worker.tasks)
			w.find(".worker-clientid").text(worker.client_id)
			w.find(".worker-ip").text(worker.ip)
		});
	}
	
	function getPingRating(ping) {
		rating = [10000,1000,100,10]
		if (!ping) {
			return 0;
		}
		for( r in rating ) {
			if( ping > rating[r] ) {
				return r;
			}
		}
		return 4
	}
	
	checkGearmanState();
	setInterval(checkGearmanState, 1000);

	$(".btn.create").click(function() {
		$.getJSON("/workermonitor/gearman-start-worker", function(data) {
			console.log(data)
		});
	});
		
	
});
