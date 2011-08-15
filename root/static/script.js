var table_profile = {
          table: {
            height: 532,
            width: 763,
            resizable: 0,
            status: 0,
            center: 1
          }
};

jQuery(function() {
    attach_behaviors(jQuery("html"));

    return;

    if (jQuery("div.tables-list-wrapper").length > 0) {
      setTimeout("refresh_tables()", 15000);
    }
});


var refresh_tables = function() {
    jQuery.ajax({
      url: '/tables',
      success: function(data) {
        var tables_list = jQuery(data).find('div.tables-list-wrapper').html();

        if (tables_list) {
          jQuery("div.tables-list-wrapper").html(
            tables_list
          );
          attach_behaviors(jQuery("div.tables-list-wrapper"));
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
  jQuery(".popup-window", c).popupwindow(table_profile);

  jQuery(".tables-categories a", c).click(function() {
    jQuery(".tables .tables-list").hide();
    jQuery(jQuery(this).attr('href')).show();
    jQuery(".tables-categories *", c).removeClass('active');
    jQuery(this).parent().addClass('active');
    return false;
  });

  jQuery(".tables-categories li", c).click(function() {
    jQuery(this).children('ul:visible').slideUp();
    jQuery(this).children('ul:hidden').slideDown();
    return false;
  });

  jQuery("a.confirm", c).click(function() {
    if (! confirm('Are you sure?')) {
      return false;
    }
  });

}


function popitup(link, game_id) {
  jQuery('<a rel="table" target="table_' + game_id + '" href="'+ link +'" />').popupwindow(table_profile).click();
}

jQuery(document).ready(function() { 
  jQuery(".tweet").tweet({
      username: "betcoin",
      join_text: null,
      avatar_size: null,/*AVATAR*/
      count: 1,/*NUMBER OF TWEETS*/
      auto_join_text_default: "we said,", 
      auto_join_text_ed: "we",
      auto_join_text_ing: "we were",
      auto_join_text_reply: "we replied to",
      auto_join_text_url: "we were checking out",
      loading_text: "loading tweets..."
  });
});

jQuery(document).ready(function() {
  jQuery.ajax({
    url: 'http://betcoin.blogspot.com/feeds/posts/default?alt=json-in-script',
    dataType: 'jsonp',
    success: function (data) {
      var entries = data.feed.entry;
      jQuery("#blogspot-posts").html('<ul></ul>');

      var len = entries.length;
      if (len > 2) { 
        len = 2;
      }
      
      for (var i=0; i < entries.length; i++) {
        var date = new Date(entries[i].published["$t"]);
        var date_str = date.format("mmmm d, yyyy");
        var href = entries[i].link[4].href;
        var title = entries[i].link[4].title;
        var comments_href = entries[i].link[1].href;
        var comments_title = entries[i].link[1].title;

        jQuery("#blogspot-posts ul").append(
          "<li><a href='" + href + "' target='_blank'>" + title + "</a>" +
          "<p>" + date_str + ", <a href='" + comments_href + "' target='_blank'>" +
          comments_title + "</a></p></li>" 
        );
      }
    }
  });
})