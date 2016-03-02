/* Image Upload
 * 
 */ 

this.ckan.module('ccca-image-upload', function($, _) {
  return {
    /* options object can be extended using data-module-* attributes */
    options: {
      is_url: true,
      is_upload: false,
      field_upload: 'image_upload',
      field_url: 'image_url',
      field_clear: 'clear_upload',
      upload_label: '',
      i18n: {
        upload: _('Upload'),
        url: _('Link'),
        remove: _('Remove'),
        upload_label: _('Image'),
        upload_tooltip: _('Upload a file on your computer'),
        url_tooltip: _('Link to a URL on the internet (you can also link to an API)')
      }
    },

    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      $.proxyAll(this, /_on/);
      var options = this.options;

      // firstly setup the fields
      var field_upload = 'input[name="' + options.field_upload + '"]';
      var field_url = 'input[name="' + options.field_url + '"]';
      var field_clear = 'input[name="' + options.field_clear + '"]';

      this.input = $(field_upload, this.el);
      this.field_url = $(field_url, this.el).parents('.control-group');
      this.field_image = this.input.parents('.control-group');
      this.field_image_sftp = this.input.parents('.control-group');
      this.field_url_input = $('input', this.field_url);

      // Is there a clear checkbox on the form already?
      var checkbox = $(field_clear, this.el);
      if (checkbox.length > 0) {
        options.is_upload = true;
        checkbox.parents('.control-group').remove();
      }

      // Adds the hidden clear input to the form
      this.field_clear = $('<input type="hidden" name="clear_upload">')
        .appendTo(this.el);
      
      // Adds the hidden text field for sftp upload
      this.div_sftp = $('<div id="div_sftp_upload" style="display: none;" name="sftp_upload">')
        .appendTo(this.el);

      // Adds an info string for SFTP upload
      this.info_sftp = $('<p>All files you upload to ​<a href="sftp://user@example.com">sftp://user@example.com</a> will appear here.<br>Please choose a file to upload to CKAN:</p>')
      .appendTo(this.div_sftp);
      
      this.fieldset_sftp = $('<fieldset id="fieldset_sftp">')
      .appendTo(this.div_sftp);
      
      // Button to refresh the file list from sftp import dir
      this.button_sftp_refresh = $('<a href="javascript:;" id="button_sftp_refresh" class="btn">Refresh</a>')
      .on('click', this._refreshSFTPFilelist)
      .appendTo(this.div_sftp);
      
      // Button to confirm the selected file to upload from sftp import dir
      this.button_sftp = $('<a href="javascript:;" id="button_sftp" class="btn" disabled>Upload</a>')
      .on('click', this._onInputChangeSFTP)
      .appendTo(this.div_sftp);
      
      // Button to set the field to be a URL
      this.button_url = $('<a href="javascript:;" class="btn"><i class="icon-globe"></i> '+this.i18n('url')+'</a>')
        .prop('title', this.i18n('url_tooltip'))
        .on('click', this._onFromWeb)
        .insertAfter(this.input);

      // Button to attach file from sftp to the form
      this.button_upload_sftp = $('<a href="javascript:;" class="btn"><i class="icon-cloud-upload"></i>Upload SFTP</a>')
      .prop('title', 'Upload file imported from SFTP directory')
      .on('click', this._onSFTP)
      .insertAfter(this.input);
      
      // Button to attach local file to the form
      this.button_upload = $('<a href="javascript:;" class="btn"><i class="icon-cloud-upload"></i>'+this.i18n('upload')+'</a>')
        .insertAfter(this.input);

      // Button for resetting the form when there is a URL set
      $('<a href="javascript:;" class="btn btn-danger btn-remove-url"><i class="icon-remove"></i></a>')
        .prop('title', this.i18n('remove'))
        .on('click', this._onRemove)
        .insertBefore(this.field_url_input);

      // Update the main label
      $('label[for="field-image-upload"]').text(options.upload_label || this.i18n('upload_label'));

      // Setup the file input
      this.input
        .on('mouseover', this._onInputMouseOver)
        .on('mouseout', this._onInputMouseOut)
        .on('change', this._onInputChange)
        .prop('title', this.i18n('upload_tooltip'))
        .css('width', this.button_upload.outerWidth());

      // Fields storage. Used in this.changeState
      this.fields = $('<i />')
        .add(this.button_upload)
        .add(this.button_upload_sftp)
        .add(this.button_url)
        .add(this.input)
        .add(this.field_url)
        .add(this.field_image)
        .add(this.field_image_sftp);

      if (options.is_url) {
        this._showOnlyFieldUrl();
      } else if (options.is_upload) {
        this._showOnlyFieldUrl();
        this.field_url_input.prop('readonly', true);
      } else {
        this._showOnlyButtons();
      }
    },
    
    /* Event listener 
    *
    * Returns nothing.
    */
   _onSFTP: function() {
	   if (this.div_sftp.css('display')=='none') {
		   this._refreshSFTPFilelist();
	   }
	  this.div_sftp.toggle();
   },
   
   _refreshSFTPFilelist: function() {
	   $('#fieldset_sftp').hide();
	   $.ajax({
	    	  url: "http://127.0.0.1:5000/sftp_filelist?apikey=4d4b762b-f696-49e4-be00-79aacfb6cd0b",
	    	  context: document.body
	    	}).done(function() {
	    	  $(this).addClass( "done" );
	    	}).success(function(json) {
	    		var parsed = JSON.parse(json);
	    		var filelist = [];
	    		for(var x in parsed){
	    			filelist.push(parsed[x]);
	    		}
	    		$('#fieldset_sftp').empty();
	    		for (var i=0; i < filelist.length; i++) {
	    			var id = 'file'+i;
	    			$('#fieldset_sftp').append('<input type="radio" id="'+id
	    				+'" name="file" class="filebutton" value="'+ filelist[i] 
	    				+'" onchange="$(&quot;#button_sftp&quot;).removeAttr(&quot;disabled&quot;);"/><label class="radio inline filelabel" for="'+id
	    				+'">'+ filelist[i] +'</label><br>');
	   	      }
	    		$('#fieldset_sftp').show();
	    		$('#button_sftp').attr('disabled', true);
	    	}).fail(function() {
	    		console.log('sftp list request failed!');
	    	});
   },
   
    /* Event listener for when someone sets the field to URL mode
     *
     * Returns nothing.
     */
    _onFromWeb: function() {
      this._showOnlyFieldUrl();
      this.field_url_input.focus();
      if (this.options.is_upload) {
        this.field_clear.val('true');
      }
      
    },

    /* Event listener for resetting the field back to the blank state
     *
     * Returns nothing.
     */
    _onRemove: function() {
      this._showOnlyButtons();
      this.field_url_input.val('');
      this.field_url_input.prop('readonly', false);
      this.field_clear.val('true');
    },

    /* Event listener for when someone chooses a file to upload
     *
     * Returns nothing.
     */
    _onInputChange: function() {
      var file_name = this.input.val().split(/^C:\\fakepath\\/).pop();
      this.field_url_input.val(file_name);
      this.field_url_input.prop('readonly', true);
      this.field_clear.val('');
      this._showOnlyFieldUrl();
    },
    
    _onInputChangeSFTP: function() {
    	var selected = $("#fieldset_sftp input[type='radio']:checked");
    	var obj = this;
    	if (selected.length>0) {
    		console.log("Importing file");
    		var formData=new FormData();
    		formData.append("apikey", "4d4b762b-f696-49e4-be00-79aacfb6cd0b");
    		formData.append("package_id", "726a89e6-72db-459e-8aae-d4f3d2ab4751");
    		formData.append("url", "/Users/ck/ckan/" + selected[0].value);
    		formData.append("name", "AUT");
    		
    		 $.ajax({
    			 method: "POST",
    			 headers: { 'Authorization': '4d4b762b-f696-49e4-be00-79aacfb6cd0b' },
	   	    	 url: "http://127.0.0.1:5000/sftp_upload",
	   	    	 context: document.body,
	   	    	 data: formData,
	   	    	 cache: false,
	   	    	 contentType: false,
	   	    	 processData: false
   	    	}).done(function() {
//   	    	  $(this).addClass( "done" );
   	    	}).success(function(json) {
//   	    		var package_id = response.result.package_id;
//   	    		var resource_id = response.result.id;
//   	    		var filename = "AUT.geojson";
   	    		var response = jQuery.parseJSON(json);
   	    		var url = response.result.url;
   	    		console.log(url);
	   	     	obj.field_url_input.val(url);
	   	     	obj.field_url_input.prop('readonly', true);
	   	     	obj.field_clear.val('');
			   	obj._showOnlyFieldUrl();
			   	obj.div_sftp.hide();
   	    	}).fail(function() {
   	    		console.log('sftp list request failed!');
   	    	});
    	}
    	
    },
    
//    _enterResourceURL: function() {
//   		var package_id = response.result.package_id;
//   		var resource_id = response.result.id;
//   		var filename = "AUT.geojson";
//   		var url = "http://127.0.0.1:5000/dataset/"+package_id+"/resource/"+resource_id+"/download/"+filename;
//   		console.log(url);
//    	this.field_url_input.val(url);
//    	this.field_url_input.prop('readonly', true);
//        this.field_clear.val('');
//        this._showOnlyFieldUrl();
//        this.div_sftp.hide();
//    },

    /* Show only the buttons, hiding all others
     *
     * Returns nothing.
     */
    _showOnlyButtons: function() {
      this.fields.hide();
      this.button_upload
        .add(this.field_image)
        .add(this.button_upload_sftp)
        .add(this.button_url)
        .add(this.input)
        .show();
    },

    /* Show only the URL field, hiding all others
     *
     * Returns nothing.
     */
    _showOnlyFieldUrl: function() {
      this.fields.hide();
      this.field_url.show();
    },

    /* Event listener for when a user mouseovers the hidden file input
     *
     * Returns nothing.
     */
    _onInputMouseOver: function() {
      this.button_upload.addClass('hover');
    },

    /* Event listener for when a user mouseouts the hidden file input
     *
     * Returns nothing.
     */
    _onInputMouseOut: function() {
      this.button_upload.removeClass('hover');
    }

  };
});
