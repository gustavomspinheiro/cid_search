(function ($) {
  $.fn.normalize_h = function () {
    var heights = {};
    var element = this;

    $.each(element.parent(), function (i, e) {
      $(e).find(element).css("height", "auto");
      heights = $(e)
        .find(element)
        .map(function (i, el) {
          return $(el).height();
        });
      $(e).find(element).height(Math.max.apply(this, heights));
    });
  };
})(jQuery);
