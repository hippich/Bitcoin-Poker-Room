(function($) {

    $.ajax_queue = $.ajax,
    pendingRequests = {},
    synced = [],
    syncedData = [],
    ajaxRunning = [];

    var max_tries = 5;
    var try_timeout = 5000;
    var tries = [];
    var ajax_call_with_retries = function(settings) {
      tries[settings.url] = 0;
      var old_error_handle = settings.error;
      var old_success_handle = settings.success;
      
      settings.timeout = try_timeout;
      settings.error = function(req, status, error) {
        if (status == 'timeout') {
          tries[settings.url]++;
          if (tries[settings.url] > max_tries) {
            old_error_handle(req, status, error);
            settings.success = old_success_handle;
            settings.error = old_error_handle;
            return;
          }
          else {
            $.ajax_queue(settings);
          }
        }
        else {
          settings.success = old_success_handle;
          settings.error = old_error_handle;
          old_error_handle(req, status, error);
        }
      }
      settings.success = function(data, status, req) {
        settings.success = old_success_handle;
        settings.error = old_error_handle;
        old_success_handle(data, status, req);
      }
      
      $.ajax_queue(settings);
    }


    $.ajax = function(settings) {
        // create settings for compatibility with ajaxSetup
        settings = jQuery.extend(settings, jQuery.extend({}, jQuery.ajaxSettings, settings));

        var port = settings.port;
        switch (settings.mode) {
            case "abort":
                if (pendingRequests[port]) {
                    pendingRequests[port].abort();
                }
                return pendingRequests[port] = $.ajax_queue.apply(this, arguments);
                
            case "direct":
                ajax_call_with_retries(settings);
                return;
                
            case "queue":
                var _old = settings.complete;
                settings.complete = function() {
                    if (_old) {
                        _old.apply(this, arguments);
                    }
                    if (jQuery([$.ajax_queue]).queue("ajax" + port).length > 0) {
                        jQuery([$.ajax_queue]).dequeue("ajax" + port);
                    } else {
                        ajaxRunning[port] = false;
                    }
                };

                jQuery([$.ajax_queue]).queue("ajax" + port, function() {
                    $.ajax_queue(settings);
                });

                if (jQuery([$.ajax_queue]).queue("ajax" + port).length == 1 && !ajaxRunning[port]) {
                    ajaxRunning[port] = true;
                    jQuery([$.ajax_queue]).dequeue("ajax" + port);
                }

                return;
            case "sync":
                var pos = synced.length;

                synced[pos] = {
                    error: settings.error,
                    success: settings.success,
                    complete: settings.complete,
                    done: false
                };

                syncedData[pos] = {
                    error: [],
                    success: [],
                    complete: []
                };

                settings.error = function() { syncedData[pos].error = arguments; };
                settings.success = function() { syncedData[pos].success = arguments; };
                settings.complete = function() {
                    syncedData[pos].complete = arguments;
                    synced[pos].done = true;

                    if (pos == 0 || !synced[pos - 1])
                        for (var i = pos; i < synced.length && synced[i].done; i++) {
                        if (synced[i].error) synced[i].error.apply(jQuery, syncedData[i].error);
                        if (synced[i].success) synced[i].success.apply(jQuery, syncedData[i].success);
                        if (synced[i].complete) synced[i].complete.apply(jQuery, syncedData[i].complete);

                        synced[i] = null;
                        syncedData[i] = null;
                    }
                };
        }
        return $.ajax_queue.apply(this, arguments);
    };

})(jQuery);