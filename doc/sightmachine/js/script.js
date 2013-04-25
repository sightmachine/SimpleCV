$(function() {

  /**
   * Add the packages navigation.
   */
  $("#welcome-to-simplecv-s-documentation > .toctree-wrapper").html(
    "<div id=\"subnav\">\n Packages: \n      <ul>\n        <li><a href=\"SimpleCV.html\">SimpleCV</a></li> /\n        <li><a href=\"SimpleCV.Features.html\">Features</a></li> /\n        <li><a href=\"SimpleCV.MachineLearning.html\">MachineLearning</a></li> /\n        <li><a href=\"SimpleCV.Segmentation.html\">Segmentation</a></li>\n      </ul>\n      </div>"
  )

  /**
   * Check to see if we need to continue.
   */
  var validPage = false;
  var package = $(".body").find(":first:not(#simplecv-s-online-documentation)").attr("id");
  var validPages = ["/SimpleCV.html", "/SimpleCV.Features.html", "/SimpleCV.MachineLearning.html", "/SimpleCV.Segmentation.html"];
  for(var i=0; i<validPages.length; i++) {
    if(window.location.href.indexOf(validPages[i]) != -1) {
      validPage = true;
      break;
    }
  }
  if( package == null || validPage == false ) { return $(".body").show();; }

  /**
   * Do the work:
   */
  $(".document").css("margin-top", "20px");
  $("#" + package + " .section dl")
    .each(function() {
      $(this).data("clone", $(this).clone());

      count = 0
      list = $("<ul></ul>");
      $(this).find("dd dl").each(function() {

        count++;
        ele = $("<li>"+$(this).find("dt tt.descname").text()+( $(this).hasClass("method") ? "()" : "" )+"</li>")
          .click(function() {
            rpi.navigate("i/" + $(this).parent().parent().find("dt").attr("id") + "/" + $(this).text().replace(/\(\)$/g, ""), {trigger: true});
          });
        list.append(ele);

      });

      if( count == 0 ) { $(this).remove(); }
      $(this).append(list);
    })
    .css({
      "width": "190px",
      "margin-top": "0px",
      "margin-bottom": "10px"
    });

  $("#" + package + " .section").css({
    "width": "190px",
    "float": "left",
    "border": "1px solid #bbb",
    "background": "#f8f8f8",
    "border-radius": "3px",
    "box-sizing": "border-box",
    "padding": "10px",
    "margin-bottom": "10px",
    "margin-right": "10px",
  });

  $("#" + package + " .section dl ul")
    .css({
      "padding": "0px",
      "margin": "0px"
    })
    .find("li")
      .css({
        "text-decoration": "underline",
        "list-style-type": "none",
        "color": "#39C",
        "padding": "0px",
        "background": "none",
        "cursor": "pointer",
        "font": "11px verdana, geneva, arial, sans-serif",
      })
      .html(function(i, old) {
        if( old.length > 100 ) { return ""; }
        return old;
      })

  $("#" + package + " .section h2")
    .css({
      "font": "bold 11px verdana, geneva, arial, sans-serif",
      "color": "#444",
      "margin-bottom": "none",
      "margin": "0px",
      "overflow": "hidden",
      "white-space": "nowrap",
      "text-overflow": "ellipsis"
    })
    .each(function() {
      $(this).text($(this).find("tt").text());
    });

  $("#" + package + " .section dl dt")
    .click(function() {
      rpi.navigate("i/" + $(this).attr("id"), {trigger: true});
    })
    .each(function() {
      $(this).html($(this).html().replace(/\,/g, ""));
    });

  $("#" + package + " .section tt.descname").css({
      "display": "block",
      "width": "169px",
      "margin-top": "7px",
      "font": "italic 11px verdana, geneva, arial, sans-serif",
      "color": "#5a5a5a",
      "overflow": "hidden",
      "white-space": "nowrap",
      "text-overflow": "ellipsis"
  })

  $("#" + package + " .section dl dt .descclassname").css("display", "none");
  $("#" + package + " .section dl dt .descname")
  $("#" + package + " .section dl dt tt").css("cursor", "pointer");
  $("#" + package + " .section dl dt tt + big").css("margin-left", "10px");
  $("#" + package + " .section dl dt big").css("display", "none");
  $("#" + package + " .section dl dt em").css("display", "none")
  $("#" + package + " .section dl dd, #id1").remove();
  $(".headerlink, #" + package + " h1").remove();
  $($(".toctree-l1").parents(".section").get(0)).remove()

  $(".body").show();

  $("#" + package + "").masonry({itemSelector: '.section'});
  $("#" + package + " .section p").css("display", "none");

  /**
   * Router Stuff
   */
  var Workspace = Backbone.Router.extend({
    routes: {
      "i/:query":        "search",
      "i/:query/:page":  "searchy",
      '*path':  'defaultRoute'
    },

    search: function(query) { obj = document.getElementById(query); openModule(obj, $(obj).attr("id")); },
    searchy: function(query, page) { obj = document.getElementById(query);openModule(obj, $(obj).attr("id") + "." + page); },
    defaultRoute: function(path) { closeModule(); }
  });
  var rpi = new Workspace();

  function openModule(module, anch) {
    $(".body").hide();
    $("#doc_body").html($(module).parent().data("clone"))
    $("#doc_body").show();
    $('html, body').animate({scrollTop: $(document.getElementById(anch)).offset().top}, 1);
  }

  function closeModule() {
    $("#doc_body").hide();
    $(".body").show();
  }

  Backbone.history.start({root: "/docs/"});

});
