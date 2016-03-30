function md_toggle_profiles() {
	return;
	var selected = $("#select_mdprofile option:selected");
	var action = 'get_html_iso';
	if (selected=="ISO") {
		action = 'get_html_iso';
	}
	 $.ajax({
		 method: "GET",
		 headers: {},
    	 url: "/api/action/"+action,
    	 context: document.body,
    	 
    	 //data: formData,
    	 cache: false,
    	 contentType: false,
    	 processData: false
    	}).done(function() {
//	    	  $(this).addClass( "done" );
    	}).success(function(response) {
    		$('#basic_fields').html(response.result);
    	}).error(function(xhr, status, thrownError) {
		console.log('file import request failed: ' + thrownError);
	});
	
}