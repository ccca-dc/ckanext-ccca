/* Extends upload functionality by import from a local directory.
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
        url_tooltip: _('Link to a URL on the internet (you can also link to an API)'),
        no_files: _('No files found in import directory')
      }
    },

    /* Initialises the module setting up elements and event listeners.
     *
     * Returns nothing.
     */
    initialize: function () {
      $.proxyAll(this, /_on/);
      var options = this.options;
      var host_url = options.host_url.replace("http://", "");
      var username = options.username;

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

      // this.field_clear = $('<input id="input_sftp_apikey" type="hidden" name="input_sftp_apikey" value="'+this.options.apikey+'">')
      // .appendTo(this.el);

      // Adds the hidden text field for sftp upload
      this.div_sftp = $('<div id="div_sftp" style="display: none;" name="sftp_upload">')
        .appendTo(this.el);

      // Adds an info string for SFTP upload
      var sftp_link = username+'@'+'inp.ccca.ac.at';
      this.info_sftp = $('<p>All files you upload to ​<a id="a_sftplink" value='+sftp_link+' onclick="_copyLinkToClipboard()">'+sftp_link+'</a>'
    		  +' will appear here.<br>'
    		  +'Please select a file to import:</p>')
      .appendTo(this.div_sftp);

      // File selection
      this.select_sftp = $('<select id="select_sftp" size="5" onchange="$(&quot;#button_sftp&quot;).removeAttr(&quot;disabled&quot;);">')
      .append('<option id=0" name="file" class="filebutton" value="">'
	    				+ this.i18n('no_files') +'</option>')
      .appendTo(this.div_sftp);

      // Button to refresh the file list from sftp import dir
      this.button_sftp_refresh = $('<a href="javascript:;" id="button_sftp_refresh" apikey="'+ options.apikey + '" class="btn">Refresh</a>')
      .on('click', this._refreshSFTPFilelist)
      .appendTo(this.div_sftp);

      // Button to cancel sftp import
      this.button_sftp_cancel = $('<a href="javascript:;" id="button_sftp_cancel" class="btn">Cancel</a>')
      .on('click', function() {$('#div_sftp').animate( { "opacity": "hide", top:"100"} , 500 );})
      .appendTo(this.div_sftp);

      // Button to confirm the selected file to import from local import directory
      this.button_sftp = $('<a href="javascript:;" id="button_sftp" class="btn btn-primary" disabled>Import</a>')
      .on('click', this._onInputChangeSFTP)
      .appendTo(this.div_sftp);

      // Button to set the field to be a URL
      this.button_url = $('<a href="javascript:;" class="btn"><i class="icon-globe"></i> '+this.i18n('url')+'</a>')
        .prop('title', this.i18n('url_tooltip'))
        .on('click', this._onFromWeb)
        .on('click', function() {$('#div_sftp').animate( { "opacity": "hide", top:"100"} , 500 );})
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

      // set double click for file list
      $('#select_sftp')
        .on('dblclick', this._onInputChangeSFTP);

      // Setup the file input
      this.input
        .on('mouseover', this._onInputMouseOver)
        .on('mouseout', this._onInputMouseOut)
        .on('change', this._onInputChange)
        .on('click', function() {$('#div_sftp').animate( { "opacity": "hide", top:"100"} , 500 );})
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

   _onSFTP: function() {
	   if (this.div_sftp.css('display')=='none') {
		     this._refreshSFTPFilelist();
	   }
	   this.div_sftp.animate( { "opacity": "show", top:"100"} , 500 );
   },

   _refreshSFTPFilelist: function() {
     var apikey = this.options.apikey
	   console.log('apikey: ' + apikey);
	   console.log('_refreshSFTPFilelist()');
	   $.ajax({
	    	  url: "/sftp_filelist?apikey=" + apikey,
	    	  context: document.body
	    	}).done(function() {
	    	  $(this).addClass( "done" );
	    	}).success(function(json) {
	    		var parsed = JSON.parse(json);
	    		var filelist = [];
	    		for(var x in parsed){
	    			filelist.push(parsed[x]);
	    		}
	    		$('#select_sftp').empty();
	    		for (var i=0; i < filelist.length; i++) {
	    			var id = 'file'+i;
	    			$('#select_sftp').append('<option id="'+id
	    				+'" name="file" class="filebutton" value="'+ filelist[i]
	    				+'">' +filelist[i]+ '</option>');
	   	        }
	    		$('#button_sftp').attr('disabled', true);
	    	}).error(function(xhr, ajaxOptions, thrownError) {
	    		console.log('file list request failed: ' + xhr.responseText);
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
    	var selected = $("#select_sftp option:selected");
    	var obj = this;
    	if (selected.length>0) {
    		console.log("Importing file");
    		var loc = window.location.pathname;
    		var homeDir = loc.substring(0, loc.lastIndexOf('/'));
    		var paramString="?apikey=" + this.options.apikey
    		+ "&package_id=" + this.options.pkg_id
    		+ "&filename=" + selected[0].value;

    		 $.ajax({
    			 method: "GET",
    			 headers: {},
	   	    	 url: "/sftp_upload"+paramString,
	   	    	 context: document.body,
   	    	}).success(function(json) {
   	    		var response = jQuery.parseJSON(json);
   	    		var url = response.url;
   	    		console.log(url);
	   	     	obj.field_url_input.val(url);
	   	     	obj.field_url_input.prop('readonly', true);
	   	     	obj.field_clear.val('');
			   	obj._showOnlyFieldUrl();
			   	obj.div_sftp.hide();
			   	$('#upload_type').val('sftp');
			   	$('#res_id').val(response.id);
   	    	}).error(function(xhr, status, thrownError) {
	    		console.log('file import request failed: ' + thrownError);
	    	});
    	}

    },

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
