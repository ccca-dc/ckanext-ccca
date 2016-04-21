'use strict';

ckan.module('ccca-md-toggle-profiles', function ($, _) {
  return {
    initialize: function () {
      $.proxyAll(this, /_on/);
      this.el.on('change', this._onChange);
    },
    _onChange: function () {
    	var selected = $("#select_mdprofile option:selected").val();
    	var action = 'get_html_ccca';
    	if (selected=="iso") {
    		action = 'get_html_iso';
    	} else if (selected=="inspire") {
    		action = 'get_html_inspire';
    	}
    	$.ajax({
    		 method: "GET",
    		 headers: {},
        	 url: "/api/action/"+action+"?id="+this.options.pkg_id,
        	 context: document.body,
        	 
        	 cache: false,
        	 contentType: false,
        	 processData: false
    	}).success(function(response) {
    		$('#basic_fields').html(response.result);
    	}).error(function(xhr, status, thrownError) {
    		console.log('file import request failed: ' + thrownError);
    	});
    }
  }
});
