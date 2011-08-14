(function($) {
  var table_profile = {
            table: {
              height: 532,
              width: 763,
              resizable: 0,
              status: 0,
              center: 1
            }
  };

  $(function() {
      attach_behaviors($("html"));

      return;

      if ($("div.tables-list-wrapper").length > 0) {
        setTimeout("refresh_tables()", 15000);
      }
  });


  var refresh_tables = function() {
      $.ajax({
        url: '/tables',
        success: function(data) {
          var tables_list = $(data).find('div.tables-list-wrapper').html();

          if (tables_list) {
            $("div.tables-list-wrapper").html(
              tables_list
            );
            attach_behaviors($("div.tables-list-wrapper"));
          }
          else {
            window.location = '/tables';
          }
        },
        error: function(req) {
          window.location = '/tables';
        }
      });
      setTimeout("refresh_tables()", 15000);
  }

  var attach_behaviors = function(c) {
    $(".popup-window", c).popupwindow(table_profile);

    $(".tables-categories a", c).click(function() {
      $(".tables .tables-list").hide();
      $($(this).attr('href')).show();
      $(".tables-categories *", c).removeClass('active');
      $(this).parent().addClass('active');
      return false;
    });

    $(".tables-categories li", c).click(function() {
      $(this).children('ul:visible').slideUp();
      $(this).children('ul:hidden').slideDown();
      return false;
    });

    $("a.confirm", c).click(function() {
      if (! confirm('Are you sure?')) {
        return false;
      }
    });

  }

  function popitup(link, game_id) {
    jQuery('<a rel="table" target="table_' + game_id + '" href="'+ link +'" />').popupwindow(table_profile).click();
  }
})(jQuery);