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
    $("table.tables-list").load(
      "/tables table.tables-list > *",
      function() {
        attach_behaviors($("table.tables-list"));
      }
    );
    setTimeout("refresh_tables()", 15000);
}

var attach_behaviors = function(c) {
  $(".popup-window", c).popupwindow(table_profile);
}