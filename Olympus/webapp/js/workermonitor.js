$(function() {
	
	function checkGearmanState() {
		// Check the initial Gearman state.
		$.getJSON("/workermonitor/gearman-status", function(data) {
			if(!data) {
				// Hide the non-error state alerts
				$(".gearman-state.alert-success, .gearman-state.alert-warning").hide(0);
				$(".btn").attr("disabled", true);
				return false;
			}
			if(data.length == 0 || data[0]["workers"] == 0) {
				// Gearman lives, but no workers.
				$(".gearman-state.alert-success, .gearman-state.alert-danger").hide(0);
				return false;
			}
			// Gearman lives, but no workers.
			$(".gearman-state.alert-warning, .gearman-state.alert-danger").hide(0);
			$(".gearman-state.alert-success .worker-count").text( data[0]["workers"] )
		});
		
		$.getJSON("/workermonitor/gearman-ping", function(data) {
			var width = (getPingRating(data*1000)*25) + "%";
			$(".signal").css("width", width );
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
	
	$.getJSON("/workermonitor/gearman-workers", function(data) {		
		
	});
		
	
});