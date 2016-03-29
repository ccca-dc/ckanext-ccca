'use strict';

ckan.module('md_toggle_profiles', function ($, _) {
  return {
    data: {
      content: ''
    },
    initialize: function () {
        var module = this;
        $.proxyAll(this, /_on/);
        module.el.on('click', this._onClick);
        module._getContent(function (res) {
          if (res.success) {
            module.data.content = res.result;
          }
        });
      },
      _getContent: function (callback) {
        $.ajax({
          url: '/api/action/get_content',
          success: function (res) {
            if (res.success) {
              callback(res);
            }
          }
        })
      }
}});
