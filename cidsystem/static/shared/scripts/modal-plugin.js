(function ($) {
  $.fn.cidModal = function (options) {
    //settings
    var defaults = {
      time: 200,
      effect: "linear",
      modalClass: this.data("modal"),
      modalClassAdj: "main_modal",
    };

    //application
    $.extend(defaults, options);

    //methods
    var modal = {
      open: function () {
        $(defaults.modalClass).fadeIn(defaults.time).css("display", "flex");
      },

      close: function () {
        $(defaults.modalClass).fadeOut(defaults.time, defaults.effect);
      },
    };

    //execution

    //open modal
    this.stop().click(function (e) {
      e.preventDefault();
      modal.open();
      return this;
    });

    //close modal
    $("body").on("click", function (e) {
      if (e.target.className === defaults.modalClassAdj) {
        e.preventDefault();
        modal.close();
        return this;
      }
    });
  };
})(jQuery);
