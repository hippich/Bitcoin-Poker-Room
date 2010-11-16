var table_profile = {
          table:
          {
            height: 532,
            width: 763,
            resizable: 0,
            status: 0,
            center: 1
          }
};

$(function() {
    attach_behaviors($("html"));

    if ($("table.tables-list").length > 0) {
      setTimeout("refresh_tables()", 15000);
    }
});


var refresh_tables = function() {

    $.ajax({
      url: '/tables',
      success: function(data) {
        var tables_list = $(data).find('table.tables-list').html();

        if (tables_list) {
          $("table.tables-list").html(
            tables_list
          );
          attach_behaviors($("table.tables-list"));
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
}