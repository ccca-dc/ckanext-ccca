/* Dataset visibility toggler
 * When no organization is selected in the org dropdown then set visibility to
 * public always and disable dropdown
 * Extended: same with field 'resource access'
 */
this.ckan.module('ccca-dataset-visibility', function ($, _) {
  return {
    currentValue: false,
    options: {
      organizations: $('#field-organizations'),
      visibility: $('#field-private'),
      res_access: $('#field-res_access'),
      currentValue: null
    },
    initialize: function() {
      $.proxyAll(this, /_on/);
      this.options.currentValue = this.options.visibility.val();
      this.options.organizations.on('change', this._onOrganizationChange);
      this._onOrganizationChange();
    },
    _onOrganizationChange: function() {
      var value = this.options.organizations.val();
      if (value) {
        this.options.visibility
          .prop('disabled', false)
          .val(this.options.currentValue);
        this.options.res_access
	      .prop('disabled', false)
	      .val(this.options.currentValue);
      } else {
        this.options.visibility
          .prop('disabled', true)
          .val('False');
        this.options.res_access
          .prop('disabled', true)
          .val('False');
      }
    }
  };
});
