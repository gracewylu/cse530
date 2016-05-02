$(document).ready(function() {
	$("#download").click(function(event) {
		$("#classSchedule").tableExport({type:'excel',escape:'false'});
	})
});