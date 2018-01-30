/* Media Grid
 * Super simple plugin that waits for all the images to be loaded in the media
 * grid and then applies the jQuery.masonry to then
 */
this.ckan.module('ccca-media-grid', function ($, _) {
  return {
    initialize: function () {
      var wrapper = this.el;
      wrapper.imagesLoaded(function() {
        wrapper.masonry({
          itemSelector: '.media-item'
        });
      });

      $('a[data-toggle="pill"]').on('shown.bs.tab', function (e) {
          var name = e.target.href.substr(e.target.href.indexOf("#") + 1);
          var wrapper = $('#' + name).find("ul");
          wrapper.imagesLoaded(function() {
            wrapper.masonry({
              itemSelector: '.media-item'
            });
          });
        });
    }
  };
});
