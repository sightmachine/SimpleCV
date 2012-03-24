$(function() {
	$('#snapshot').bind('click', function() {
		$.getJSON($SCRIPT_ROOT + '/_snapshot',
		{},
		function(data) {
				//~ d = new Date();
				//~ $("#imgoutput").attr("src", "/myimg.jpg?"+d.getTime());
				$("#imgoutput").attr("src", data);
		});
		return false;
	});
});

