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
    jQuery(document).ajaxStart(jQuery.blockUI).ajaxStop(jQuery.unblockUI);

    auto_refresh_tables();

    jQuery('.table-filter .values').hide();

    jQuery('#table-filter-form input').change(update_tables);
    jQuery('#table-filter-form select').change(update_tables);
    jQuery('#submit-filter').hide();
});


function attach_behaviors(c) {
  jQuery(".popup-window", c).popupwindow(table_profile);

  jQuery("a.confirm", c).click(function() {
    if (! confirm('Are you sure?')) {
      return false;
    }
  });
}

function update_range(event, ui) {
    var p = jQuery(event.target).parent();
    p.find('span.value').text(ui.values[0] + ' - ' + ui.values[1]);
    p.find('input.min').val(ui.values[0]);
    p.find('input.max').val(ui.values[1]);
};

function update_tables(e, background) {
  var values = jQuery('#table-filter-form').serialize();

  if (values) {
    jQuery.ajax({
      url: '/tables',
      global: !background,
      data: values + '&ajax=1',
      error: function(jqXHR, textStatus, errorThrown) {
      },
      success: function(data, textStatus, jqXHR) {
        jQuery('.tables').html(data);        
        attach_behaviors(jQuery("div.tables-list-wrapper"));
      }
    });
  }
};

function auto_refresh_tables() {
  setTimeout(function() {
    update_tables(false, true);
    auto_refresh_tables();
  }, 5000);
};

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
    url: 'https://posterous.com/api/2/sites/betcoin/posts/public',
    dataType: 'jsonp',
    success: function (data) {
      var entries = data;
      jQuery("#blog-posts").html('<ul></ul>');

      var len = entries.length;
      if (len > 3) { 
        len = 3;
      }
      
      for (var i=0; i < len; i++) {
        var date = new Date(entries[i].display_date);
        var date_str = date.format("mmmm d, yyyy");
        var href = entries[i].full_url;
        var title = entries[i].title;
        var comments_href = entries[i].full_url;
        var comments_title = entries[i].number_of_comments + ' comments';

        jQuery("#blog-posts ul").append(
          "<li><a href='" + href + "' target='_blank'>" + title + "</a>" +
          "<p>" + date_str + ", <a href='" + comments_href + "' target='_blank'>" +
          comments_title + "</a></p></li>" 
        );
      }
    }
  });
})