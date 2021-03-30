$(function () {
  var timeEffect = 1000;

  //GENERAL
  $(window).on("load", function (e) {
    $(".main_banner_images img").show(2000);
  });

  $("form:not(.ajax_off)").on("submit", function (e) {
    e.preventDefault();
    var form = $(this);
    var formData = $(this).serialize();
    $.ajax({
      url: form.attr("action"),
      type: "POST",
      data: formData,
      dataType: "JSON",
      beforeSend: function () {
        $("form")
          .find("button")
          .after("<span class='load' style='color: red'>Carregando...</span>");
      },
      success: function (response) {
        if (response.redirect) {
          window.location = response.redirect;
          return;
        }

        if (response.reload) {
          location.reload();
          return;
        }

        if (response.message) {
          $("form").prepend(response.message);
        }
      },
      complete: function () {
        $("body")
          .find(".load")
          .fadeOut(function () {
            $(this).remove();
            $("form").trigger("reset");
          });
        setTimeout(function () {
          $(".message").remove();
        }, 4000);
      },
    });
  });

  //*** HOME PAGE ***

  //MOBILE MENU
  var windowWidth = $(window).width();
  let headerNav = $(".main_header_nav");

  function closeMobile() {
    $(".main_header_nav_links").css("display", "none");
    $(".main_header_nav_mobile_menu").fadeIn("slow");
  }

  if (windowWidth <= 667) {
    //display mobile menu
    $(".main_header_nav_mobile_menu").on("click", function (e) {
      e.preventDefault();
      $(".main_header_nav_links")
        .css({
          display: "block",
          left: "auto",
        })
        .fadeIn(timeEffect / 10)
        .animate({ right: "0" }, 200);
      $(this).fadeOut("fast");
    });

    //hide mobile menu
    $(".main_header_nav_list_close").on("click", function (e) {
      e.preventDefault();
      closeMobile();
    });

    $(document).on("click", function (e) {
      e.preventDefault();
      var clicked = e.target;
      if ($(clicked).parents(".main_header").length === 0) {
        closeMobile();
      }
    });
  }

  //REFERENCE CID
  $(".main_highlights_list").css("display", "none");
  $(".main_highlight_button").on("click", function (e) {
    e.preventDefault();
    e.stopPropagation();
    $(this).toggleClass("icon-plus icon-minus");
    $(this)
      .next("ul")
      .stop()
      .slideToggle(timeEffect / 5);
  });

  //MAIN MODAL SEARCH
  $(".main_headline_alternative_search").cidModal();

  $(".main_modal_search_form input").on("keyup", function (e) {
    var input = $(this);
    if (!$(".main_modal_preview h4").length) {
      $(".main_modal_preview").prepend(
        "<h4>" + input.val().replace("\n/g", "").toUpperCase() + "</h4>"
      );
    } else {
      $(".main_modal_preview h4").text(
        input.val().replace("\n/g", "").toUpperCase()
      );
    }
  });

  //DISPLAY BUTTOM RETURN TO TOP
  $(window).on("scroll", function (e) {
    var positionTop = $(this).scrollTop();
  });

  //*** RESULT PAGE ***

  //DISPLAY RESULT TO USER
  $(".result_desc")
    .fadeIn(timeEffect * 4)
    .css("display", "inline-block");
});

//*** FEEDBACK PAGE ***
const auxiliarFeedback = (id) => {
  const auxInput = document.querySelector("#aux_feedback");
  const feedback = id == "result_feedback_positive" ? true : "";
  auxInput.value = feedback;
};

document
  .querySelector("#result_feedback_positive")
  .addEventListener("click", (e) => {
    auxiliarFeedback(e.target.id);
  });

document
  .querySelector("#result_feedback_negative")
  .addEventListener("click", (e) => {
    auxiliarFeedback(e.target.id);
  });
