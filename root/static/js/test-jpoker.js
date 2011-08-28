//
//     Copyright (C) 2008 - 2010 Loic Dachary <loic@dachary.org>
//     Copyright (C) 2008 - 2010 Johan Euphrosine <proppy@aminche.com>
//
//     This program is free software: you can redistribute it and/or modify
//     it under the terms of the GNU General Public License as published by
//     the Free Software Foundation, either version 3 of the License, or
//     (at your option) any later version.
//
//     This program is distributed in the hope that it will be useful,
//     but WITHOUT ANY WARRANTY; without even the implied warranty of
//     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//     GNU General Public License for more details.
//
//     You should have received a copy of the GNU General Public License
//     along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
var TEST_TABLE_INFO = TEST_TABLE_INFO === undefined ? true : TEST_TABLE_INFO;
var TEST_AVATAR = TEST_AVATAR === undefined ? true : TEST_AVATAR;
var TEST_POWERED_BY = TEST_POWERED_BY === undefined ? true : TEST_POWERED_BY;
var TEST_RANK = TEST_RANK === undefined ? true : TEST_RANK;
var TEST_ACTION = TEST_ACTION === undefined ? true : TEST_ACTION;
var TEST_SIDE_POT = TEST_SIDE_POT === undefined ? true : TEST_SIDE_POT;

module("jpoker");

if (!window.ActiveXObject) {
  window.ActiveXObject = true;
}

var ActiveXObject = function (options) {
    //    window.console.log('activeXobject');
    $.extend(this, ActiveXObject.defaults, options);
    this.headers = [];
  };

ActiveXObject.defaults = {
  readyState: 4,
  timeout: false,
  status: 200
};

ActiveXObject.prototype = {

  responseText: "[]",

  open: function (type, url, async) {
    //        window.console.log('ActiveXObject ' + url);
  },

  setRequestHeader: function (header) {
    this.headers.push(header);
  },

  getResponseHeader: function (header) {
    if (header == "content-type") {
      return "text/plain";
    } else {
      return null;
    }
  },

  abort: function () {},

  send: function (data) {
    if ('server' in this && this.server && !this.timeout && this.status == 200) {
      this.server.handle(data);
      this.responseText = this.server.outgoing;
    }
  }
};

var kill_cookies = function () {
    $.cookie('JPOKER_AUTH_' + jpoker.url2hash('url'), null, {
      path: '/'
    });
    $.cookie('JPOKER_AUTH_' + jpoker.url2hash('url2'), null, {
      path: '/'
    });
  };

var cleanup = function (id) {
    if (id) {
      $("#" + id).remove();
    }
    if ('server' in ActiveXObject.prototype) {
      delete ActiveXObject.prototype.server;
    }
    var callbacks_left = [];
    $.each(jpoker.servers, function (key, server) {
      $.each(server.callbacks, function (key, callbacks) {
        callbacks_left.push([key, callbacks]);
        if (key == 'update') {
          if (callbacks.length !== 0) {
            ok(false, 'update callback should be cleared before cleanup: {count} callbacks left'.supplant({
              count: callbacks.length
            }));
            for (var i = 0; i < callbacks.length; ++i) {
              ok(false, callbacks[i].signature);
            }
          }
        }
      });
    });
    jpoker.uninit();
    $.cookie('jpoker_preferences_' + jpoker.url2hash('url'), null);
    $("#jpokerSoundAction, #jpokerSound, #jpokerSoundTable").remove();
    $('#jpokerDialog').dialog('close').remove();
    $('#jpokerRebuy').dialog('close').remove();
    $('#jpokerOptionsDialog').dialog('close').remove();
    $('#jpokerRankDialog').dialog('close').remove();
    $('#jpokerErrorDialog').dialog('close').remove();
  };

var start_and_cleanup = function (id) {
    setTimeout(function () {
      cleanup(id);
      start();
    }, 1);
  };

test("String.supplant", function () {
  expect(1);
  equals("{a}".supplant({
    'a': 'b'
  }), 'b');
});

var jpoker = $.jpoker;

jpoker.verbose = 1; // activate the code parts that depends on verbosity
jpoker.sound = 'span'; // using embed for test purposes triggers too many problems
jpoker.server.defaults.longPollFrequency = -1; // there must not be any interference of longPoll during the tests unless explicitly specified
jpoker.connection.defaults.longPollFrequency = -1; // there must not be any interference of longPoll during the tests unless explicitly specified
//
// jpoker
//
test("jpoker: get{Server,Table,Player}", function () {
  expect(15);
  // getServer
  equals(jpoker.getServer('url'), undefined, 'get non existent server');
  jpoker.servers.url = 'yes';
  equals(jpoker.getServer('url'), 'yes', 'get  existing server');
  // getTable
  jpoker.servers.url = {
    tables: {}
  };
  equals(jpoker.getTable('no url', 'game_id'), undefined, 'getTable non existing server');
  equals(jpoker.getTable('url', 'game_id'), undefined, 'getTable non existing table');
  jpoker.servers.url = {
    tables: {
      'game_id': 'yes'
    }
  };
  equals(jpoker.getTable('url', 'game_id'), 'yes', 'getTable existing table');
  // getPlayer
  equals(jpoker.getPlayer('no url', 'game_id'), undefined, 'getPlayer non existing server');
  equals(jpoker.getPlayer('url', 'no game_id'), undefined, 'getPlayer non existing table');
  jpoker.servers.url = {
    tables: {
      'game_id': {
        'serial2player': {}
      }
    }
  };
  equals(jpoker.getPlayer('url', 'game_id', 'player_id'), undefined, 'getPlayer non existing player');
  jpoker.servers.url = {
    tables: {
      'game_id': {
        'serial2player': {
          'player_id': 'player'
        }
      }
    }
  };
  equals(jpoker.getPlayer('url', 'game_id', 'player_id'), 'player', 'getPlayer non existing player');
  // getServerTablePlayer
  equals(jpoker.getServerTablePlayer('no url', 'game_id'), undefined, 'getServerTablePlayer non existing server');
  equals(jpoker.getServerTablePlayer('url', 'no game_id'), undefined, 'getServerTablePlayer existing table');
  jpoker.servers.url = {
    tables: {
      'game_id': {
        'serial2player': {}
      }
    }
  };
  equals(jpoker.getServerTablePlayer('url', 'game_id', 'player_id'), undefined, 'getServerTablePlayer non existing player');
  jpoker.servers.url = {
    tables: {
      'game_id': {
        'serial2player': {
          'player_id': 'player'
        }
      }
    }
  };
  var result = jpoker.getServerTablePlayer('url', 'game_id', 'player_id');
  equals('tables' in result.server, true, 'server has table');
  equals('serial2player' in result.table, true, 'table has players');
  equals(result.player, 'player', 'player is known');
  jpoker.servers = {};
});

test("jpoker.gettext", function () {
  expect(2);
  equals(_("login"), "test_gettext_override");
  equals(jpoker.gettext("login"), "login");
});

//
// jpoker.error
//
test("jpoker.error", function () {
  expect(4);
  var error_reason = "error reason";
  var jpokerMessage = jpoker.message;
  var jpokerConsole = jpoker.console;
  jpoker.console = function (reason) {};
  jpoker.message = function (string) {
    ok(/\(.*\)/.exec(string), "jpoker.message stack trace message");
    ok(string.indexOf(navigator.userAgent) >= 0, "jpoker.message userAgent");
  };
  jpokerUninit = jpoker.uninit;
  jpoker.uninit = function () {
    ok(true, "uninit called");
  };
  try {
    jpoker.error(error_reason);
  } catch (reason) {
    equals(reason, error_reason, "error_reason thrown");
  }
  jpoker.message = jpokerMessage;
  jpoker.console = jpokerConsole;
  jpoker.uninit = jpokerUninit;
});

test("jpoker.quit", function () {
  expect(2);
  stop();
  jpoker.serverCreate({
    url: 'url1'
  });
  jpoker.serverCreate({
    url: 'url2'
  });
  var quit = jpoker.server.prototype.quit;
  jpoker.server.prototype.quit = function (callback) {
    var server = this;
    setTimeout(function () {
      ok(true, 'quit called');
      callback(server);
    }, 50);
  };
  jpoker.quit(function () {
    for (var url in jpoker.servers) {
      ok(0, url + ' should not be here');
    }
    jpoker.server.prototype.quit = quit;
    start_and_cleanup();
  });
});

test("jpoker.error printStackTrace throw", function () {
  expect(2);
  var handler = jpoker.errorHandler;
  var p = printStackTrace;
  printStackTrace = function (args) {
    throw 'simulate printStackTrace error';
  };
  jpoker.errorHandler = function (reason, str) {
    ok(str.indexOf('stringify failed') >= 0, 'errorHandler');
    ok(str.indexOf('simulate printStackTrace error') >= 0, 'errorReason');
  };
  jpoker.error({});
  jpoker.errorHandler = handler;
  printStackTrace = p;
});

test("jpoker.error object", function () {
  expect(1);
  var error_reason = {
    message: "error reason",
    "xhr": {
      status: 500,
      foo: 'bar'
    }
  };
  try {
    jpoker.error(error_reason);
  } catch (reason) {
    equals(reason.message, error_reason.message, "error_reason thrown");
  }
});

test("jpoker.errorHandler", function () {
  expect(3);
  var jpokerConsole = jpoker.console;
  var error = 'error text';
  var reason = 'error reason';
  var reason_object = {
    message: reason,
    "xhr": {
      status: 500,
      foo: 'bar'
    }
  };
  jpoker.console = undefined;
  caught = false;
  try {
    jpoker.errorHandler(reason_object, error);
  } catch (e) {
    caught = true;
    equals(e.message, reason, e.message + ' contains ' + reason);
  }
  ok(caught, 'caught');
  var text = $('#jpokerErrorDialog').text();
  ok(text.indexOf(error) >= 0, text + ' contains ' + error);
  jpoker.console = jpokerConsole;
});

//
// jpoker.watchable
//
test("jpoker.watchable", function () {
  expect(22);
  var watchable = new jpoker.watchable({});
  var stone = 0;
  var callback_stone = 0;
  var callback = function (o, what, data, callback_data) {
      stone += data;
      callback_stone += callback_data;
      return true;
    };
  watchable.registerUpdate(callback, 100);
  watchable.registerDestroy(callback, 100);
  watchable.notifyUpdate(1);
  equals(stone, 1, "notifyUpdate");
  equals(callback_stone, 100, "notifyUpdate callback_data");
  watchable.notifyDestroy(1);
  equals(stone, 2, "notifyDestroy");
  equals(callback_stone, 200, "notifyDestroy callback_data");
  watchable.unregisterUpdate(callback);
  watchable.unregisterDestroy(callback);
  watchable.notifyUpdate(10);
  equals(stone, 2, "notifyUpdate (noop)");
  equals(callback_stone, 200, "notifyUpdate callback_data");
  watchable.notifyDestroy(20);
  equals(stone, 2, "notifyDestroy (noop)");
  equals(callback_stone, 200, "notifyDestroy callback_data");

  var callback_autoremove = function () {
      return false;
    };
  watchable.registerUpdate(callback_autoremove);
  watchable.notifyUpdate();
  equals(watchable.callbacks.update.length, 0, 'empty update');

  watchable.registerDestroy(callback_autoremove);
  watchable.notifyDestroy();
  equals(watchable.callbacks.destroy.length, 0, 'empty destroy');

  watchable.registerUpdate(callback_autoremove, 'callback_data', 'signature');
  equals(watchable.callbacks.update[0].signature, 'signature', 'signature update');
  watchable.unregisterUpdate('signature');
  equals('update' in watchable.callbacks, false, 'empty update (2)');

  watchable.registerDestroy(callback_autoremove, 'callback_data', 'signature');
  equals(watchable.callbacks.destroy[0].signature, 'signature', 'signature destroy');
  watchable.unregisterDestroy('signature');
  equals('destroy' in watchable.callbacks, false, 'empty destroy (2)');

  watchable = new jpoker.watchable({});
  var recurse = function () {
      caught = false;
      try {
        watchable.notifyUpdate(null);
      } catch (error) {
        caught = true;
        equals(error.indexOf('notify recursion') >= 0, true, 'recurse error');
      }
      equals(caught, true, 'caught');
    };
  watchable.registerUpdate(recurse);
  watchable.notifyUpdate();
  watchable.unregisterUpdate(recurse);
  var verified = false;
  var verify = function () {
      verified = true;
    };
  var notifyregister = function () {
      watchable.registerUpdate(verify);
    };
  watchable.registerUpdate(notifyregister);
  watchable.notifyUpdate(); // register
  watchable.notifyUpdate(); // call it
  equals(verified, true, 'verified');
  watchable.unregisterUpdate(notifyregister);
  watchable.notifyUpdate();

  watchable = new jpoker.watchable({});
  reinit_done = false;
  var notifyreinit = function (self, what, data) {
      equals(what, 'reinit');
      equals(data, 'data');
      reinit_done = true;
      return true;
    };
  watchable.registerReinit(notifyreinit, 'reinit');
  watchable.notifyReinit('data');
  equals(reinit_done, true, 'reinit done');
  equals(watchable.callbacks.reinit.length, 1, 'reinit in callbacks');
  watchable.unregisterReinit('reinit');
  equals('reinit' in watchable.callbacks, true, 'reinit has no callbacks');
});

//
// jpoker.chips
//
test("jpoker.chips: LONG", function () {
  expect(12);
  equals(jpoker.chips.LONG(10.101), '10.1');
  equals(jpoker.chips.LONG(10.111), '10.11');
  equals(jpoker.chips.LONG(10.001), '10');
  equals(jpoker.chips.LONG(0.101), '0.1');
  equals(jpoker.chips.LONG(0.011), '0.01');
  equals(jpoker.chips.LONG(100), '100');
  equals(jpoker.chips.LONG(1000), '1,000');
  equals(jpoker.chips.LONG(10000), '10,000');
  equals(jpoker.chips.LONG(100000), '100,000');
  equals(jpoker.chips.LONG(1000000), '1,000,000');
  equals(jpoker.chips.LONG(1000000.01), '1,000,000.01');
  equals(jpoker.chips.LONG(1000000.10), '1,000,000.1');
});

test("jpoker.chips: SHORT", function () {
  expect(16);
  equals(jpoker.chips.SHORT(123456789012.34), '123G');
  equals(jpoker.chips.SHORT(12345678901.23), '12.3G');
  equals(jpoker.chips.SHORT(1234567890.12), '1.23G');
  equals(jpoker.chips.SHORT(123456789.01), '123M');
  equals(jpoker.chips.SHORT(12345678.90), '12.3M');
  equals(jpoker.chips.SHORT(1234567.89), '1.23M');
  equals(jpoker.chips.SHORT(123456.78), '123K');
  equals(jpoker.chips.SHORT(12345.67), '12.3K');
  equals(jpoker.chips.SHORT(1234.56), '1.23K');
  equals(jpoker.chips.SHORT(123.45), '123');
  equals(jpoker.chips.SHORT(10.10), '10.1');
  equals(jpoker.chips.SHORT(10.11), '10.1');
  equals(jpoker.chips.SHORT(10.00), '10.0');
  equals(jpoker.chips.SHORT(1.11), '1.11');
  equals(jpoker.chips.SHORT(0.11), '0.11');
  equals(jpoker.chips.SHORT(0.01), '0.01');
});

test("jpoker.chips: chips2value", function () {
  expect(4);
  equals(jpoker.chips.chips2value([1, 2]) - 0.02 < jpoker.chips.epsilon, true, "0.02");
  equals(jpoker.chips.chips2value([1, 2, 10, 3]) - 0.32 < jpoker.chips.epsilon, true, "0.32");
  equals(jpoker.chips.chips2value([1, 2, 10, 3, 100, 5]) - 5.32 < jpoker.chips.epsilon, true, "5.32");
  equals(jpoker.chips.chips2value([10000, 5]) - 500 < jpoker.chips.epsilon, true, "500");
});

//
// jpoker
//
test("jpoker: unique id generation test", function () {
  expect(2);
  jpoker.serial = 1;
  equals(jpoker.uid(), "jpoker1");
  equals(jpoker.uid(), "jpoker2");
});

test("jpoker.url2hash", function () {
  expect(1);
  equals(jpoker.url2hash('url'), jpoker.url2hash('url'), "url2hash");
});

test("jpoker.url2server", function () {
  expect(1);
  jpoker.servers = {};
  var options = {
    url: 'url'
  };
  var server = jpoker.url2server(options);
  equals(server.url, options.url, "server created");
});

test("jpoker.dialog", function () {
  expect(1);
  var message = 'ZAAAZ';
  jpoker.dialog(message);
  equals($('#jpokerDialog').text().indexOf(message) >= 0, true, message);
  cleanup();
});

test("jpoker.dialog options title", function () {
  expect(1);
  var message = 'ZAAAZ';
  var jpokerDialogOptions = jpoker.dialog_options;
  jpokerDialogOptions.title = 'foo';
  jpoker.dialog(message);
  equals($('#jpokerDialog').text().indexOf(message) >= 0, true, message);
  cleanup();
});

test("jpoker.dialog options title undefined", function () {
  expect(1);
  var message = 'ZAAAZ';
  jpoker.dialog(message);
  equals($('#jpokerDialog').text().indexOf(message) >= 0, true, message);
  $('#jpokerDialog').dialog('close');
  cleanup();
});

test("jpoker.dialog msie", function () {
  expect(1);
  jpoker.msie_compatibility();
  var message = 'ZAAAZ';
  jpoker.dialog(message);
  equals($('#jpokerDialog').text().indexOf(message) >= 0, true, message);
  $('#jpokerDialog').dialog('close');
  jpoker.other_compatibility();
  cleanup();
});

test("jpoker.compatibility other", function () {
  expect(1);
  var other = jpoker.other_compatibility;
  jpoker.other_compatibility = function () {
    ok(true, 'other_compatibility called');
  };
  var msie = jpoker.msie_compatibility;
  jpoker.msie_compatibility = function () {
    ok(false, 'msie_compatibility not called');
  };
  jpoker.compatibility(false);
  jpoker.other_compatibility = other;
  jpoker.msie_compatibility = msie;
});

test("jpoker.compatibility msie", function () {
  expect(1);
  var other = jpoker.other_compatibility;
  jpoker.other_compatibility = function () {
    ok(false, 'other_compatibility not called');
  };
  var msie = jpoker.msie_compatibility;
  jpoker.msie_compatibility = function () {
    ok(true, 'msie_compatibility called');
  };
  jpoker.compatibility(true);
  jpoker.other_compatibility = other;
  jpoker.msie_compatibility = msie;
});

test("jpoker.copyright", function () {
  expect(0);
  cleanup();
});

test("jpoker.copyright msie", function () {
  expect(0);
  cleanup();
});

test("jpoker.refresh", function () {
  expect(2);

  kill_cookies();
  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '[{"type": "packet"}]',
    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var request_sent = false;
  var request = function (server) {
      server.sendPacket({
        'type': 'packet'
      });
    };
  var timerRequest = {
    timer: 0
  };
  var handler = function (server, packet) {
      equals(packet.type, 'packet');
      equals(timerRequest.timer !== 0, true, 'timer');
      window.clearInterval(timerRequest.timer);
      start_and_cleanup();
      return false;
    };
  jpoker.verbose = 1;
  timerRequest = jpoker.refresh(server, request, handler, 'state');
});

test("jpoker.refresh waiting", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.setInterval = function (id) {};
  var timerRequest = jpoker.refresh(server, function () {}, function () {}, 'state');
  jpoker.verbose = 1;
  var jpokerMessage = jpoker.message;
  jpoker.message = function (message) {
    jpoker.message = jpokerMessage;
    equals(message, 'refresh waiting', 'refresh waiting');
  };
  timerRequest.request();
});

test("jpoker.refresh requireSession", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });

  equals(jpoker.refresh(server, null, null, 'state', {
    requireSession: true
  }).timer, 0, 'requireSession');

  cleanup();
});

//
// jpoker.Crypto
//
test("jpoker.Crypto b32 str", function () {
  expect(1);
  equals(jpoker.Crypto.be32sToStr(jpoker.Crypto.strToBe32s("0123")), "0123", "str to be32 to str");
});

test("jpoker.serverDestroy", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  jpoker.serverDestroy('url');
  equals(jpoker.servers.url, undefined);
});

//
// jpoker.server
//
test("jpoker.server.uninit", function () {
  expect(2);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 42;
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  server.tables[game_id].uninit = function () {
    ok(true, "table uninit called");
  };
  server.uninit();
  var table_count = 0;
  for (var table in server.tables) {
    ++table_count;
  }
  equals(table_count, 0, "server.tables empty");
});

test("jpoker.table.handler PacketPokerMessage/GameMessage ", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var message = "AAA";
  server.handler(server, 0, {
    type: 'PacketPokerMessage',
    string: message
  });
  dialog = $("#jpokerDialog");
  equals(dialog.text().indexOf(message) >= 0, true, 'found (1)');
  message = "BBB";
  server.handler(server, 0, {
    type: 'PacketPokerGameMessage',
    string: message
  });
  equals(dialog.text().indexOf(message) >= 0, true, 'found (2)');
  dialog.dialog('destroy');
  cleanup();
});

test("jpoker.server.handler PacketPokerTourneyStart", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.tableJoin = function (table_serial) {
    equals(table_serial, 42);
    ok(true, 'spawnTable called');
  };
  server.handler(server, 0, {
    type: 'PacketPokerTourneyStart',
    table_serial: 42
  });
  cleanup();
});

test("jpoker.server.handler PacketPokerTable ", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.spawnTable = function () {
    ok(true, 'spawnTable called');
  };
  server.handler(server, 0, {
    type: 'PacketPokerTable',
    id: 42
  });
  cleanup();
});

test("jpoker.server.handler PacketPokerTable empty ", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var spawnTableCalled = false;
  var jpoker_message = jpoker.message;
  var messages = [];
  jpoker.message = function (msg) {
    messages.push(msg);
  };
  server.spawnTable = function (server, packet) {
    spawnTableCalled = true;
  };
  server.registerUpdate(function (server, what, packet) {
    equals(packet.id, 0);
  });
  server.handler(server, 0, {
    type: 'PacketPokerTable',
    id: 0
  });
  equals(spawnTableCalled, true);
  cleanup();
});

test("jpoker.server.{de,}queueRunning", function () {
  expect(5);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var called = 2;
  var callback = function (server) {
      called--;
    };
  server.setState('dummy');
  server.queueRunning(function (server) {
    callback();
    server.setState('dummy');
  });
  server.queueRunning(callback);
  server.setState(server.RUNNING);
  equals(called, 1, 'callback called');
  equals(server.stateQueue.length, 1, 'one callback to go');
  equals(server.state, 'dummy', 'callback changed state');
  server.setState(server.RUNNING);
  equals(called, 0, 'callback called twice');
  equals(server.stateQueue.length, 0, 'no more callbacks');
  cleanup();
});

test("jpoker.server.quit", function () {
  expect(6);
  stop();
  var PokerServer = function () {};

  var game_id = 6;
  PokerServer.prototype = {
    outgoing: '[]',

    handle: function (packet) {
      equals(packet, '{"type":"PacketQuit"}', 'packet quit');
    }
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  equals(server.getState(), server.RUNNING, 'running');
  equals(server.blocked, false, 'connection is not blocked');
  server.longPollFrequency = 1;
  server.quit(function (server) {
    equals(server.longPollFrequency, -1, 'long poll frequency');
    equals(server.getState(), server.RUNNING, 'running');
    equals(server.blocked, true, 'connection is blocked');
    start_and_cleanup();
  });
});

test("jpoker.server.init reconnect", function () {
  expect(3);
  $.cookie('JPOKER_AUTH_' + jpoker.url2hash('url'), 'authhash', {
    path: '/'
  });
  var server = jpoker.serverCreate({
    url: 'url'
  });

  equals(server.state, server.RECONNECT);
  equals(server.session_uid.indexOf('uid=') >= 0, true, 'session uid hash set');
  equals(server.auth.indexOf('auth=') >= 0, true, 'auth hash set');
  cleanup();
});

test("jpoker.server.init reconnect file: protocol", function () {
  expect(1);
  var server = jpoker.serverCreate({
    url: 'url',
    protocol: function () {
      return 'file:';
    }
  });

  equals(server.state, server.RECONNECT);
  cleanup();
});

test("jpoker.server.init reconnect doReconnect", function () {
  expect(1);
  var jpokerDoReconnect = jpoker.doReconnect;
  jpoker.doReconnect = false;
  var server = jpoker.serverCreate({
    url: 'url',
    cookie: function () {
      return this.sessionName();
    }
  });
  equals(server.state, server.RUNNING, 'no reconnection');
  jpoker.doReconnect = jpokerDoReconnect;
  cleanup();
});

test("jpoker.server.init reconnect doReconnectAlways", function () {
  expect(1);
  var jpokerDoReconnectAlways = jpoker.doReconnectAlways;
  jpoker.doReconnectAlways = true;
  var server = jpoker.serverCreate({
    url: 'url',
    cookie: function () {
      return 'NO';
    }
  });
  equals(server.state, server.RECONNECT, 'reconnect even though no cookie');
  jpoker.doReconnectAlways = jpokerDoReconnectAlways;
  cleanup();
});

test("jpoker.server.init reconnect doRejoin", function () {
  expect(3);
  var jpokerDoRejoin = jpoker.doRejoin;
  jpoker.doRejoin = false;
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.reconnect();
  equals(server.userInfo.serial, undefined, 'userInfo has no serial');
  var user_serial = 42;
  server.handle(0, {
    type: 'PacketPokerPlayerInfo',
    serial: user_serial
  });
  equals(server.userInfo.serial, user_serial, 'userInfo has serial ' + user_serial);
  equals(server.state, server.RUNNING, 'no rejoin');
  jpoker.doRejoin = jpokerDoRejoin;
  cleanup();
});

test("jpoker.server.reconnect success", function () {
  expect(3);
  stop();

  var player_serial = 43;
  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: '[{"type": "PacketPokerPlayerInfo", "serial": ' + player_serial + '}]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  var expected = server.RECONNECT;
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketState') {
      equals(server.state, expected);
      if (expected == server.RECONNECT) {
        expected = server.MY;
      } else if (expected == server.MY) {
        equals(server.serial, player_serial, 'player_serial');
        start_and_cleanup();
        return false;
      }
    }
    return true;
  });

  server.reconnect();
});

test("jpoker.server.reconnect failure", function () {
  expect(1);
  stop();

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: '[{"type": "PacketError", "code": ' + jpoker.packetName2Type.POKER_GET_PLAYER_INFO + '}]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  var expected = server.RECONNECT;
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketState') {
      equals(server.state, expected);
      if (expected == server.RECONNECT) {
        expected = server.RUNNING;
        start_and_cleanup();
        return false;
      }
    }
    return true;
  });

  server.reconnect();
});

test("jpoker.server.reconnect invalid error", function () {
  expect(1);
  stop();

  var code = 444;
  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: '[{"type": "PacketError", "code": ' + code + '}]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  var error = jpoker.error;
  jpoker.error = function (message) {
    jpoker.error = error;
    equals(message.indexOf(code) >= 0, true, 'invalid error code');
    start_and_cleanup();
  };
  server.reconnect();
});

test("jpoker.server.reconnect waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.callbacks[0] = [];
  server.reconnect();
  equals(server.callbacks[0].length, 1, 'reconnect callback registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'reconnect callback still in place');
});

test("jpoker.server.refreshTable waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.callbacks[0] = [];
  server.refreshTables('');
  equals(server.callbacks[0].length, 1, 'refreshTables callback registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'refreshTables callback still in place');
});

test("jpoker.server.refreshTourneys waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.callbacks[0] = [];
  server.refreshTourneys('');
  equals(server.callbacks[0].length, 1, 'refreshTourneys callback registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'refreshTourneys callback still in place');
});

test("jpoker.server.refreshTourneyDetails waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.callbacks[0] = [];
  server.refreshTourneyDetails(0);
  equals(server.callbacks[0].length, 1, 'refreshTourneyDetails callback registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'refreshTourneyDetails callback still in place');
});

test("jpoker.server.tableInformation", function () {
  expect(9);
  stop();
  var PokerServer = function () {};

  var game_id = 6;
  PokerServer.prototype = {
    outgoing: '[{"observers": 1, "name": "Paris", "waiting": 0, "percent_flop": 77, "average_pot": 304750, "skin": "default", "variant": "holdem", "hands_per_hour": 20, "betting_structure": "100-200-no-limit", "currency_serial": 1, "muck_timeout": 5, "players": 1, "reason": "TableJoin", "tourney_serial": 0, "seats": 10, "player_timeout": 60, "type": "PacketPokerTable", "id": 6}, {"count": 1, "game_ids": [6], "length": 9, "type": "PacketPokerCurrentGames"}, {"min": 200000, "max": 2000000, "rebuy_min": 30000, "length": 23, "game_id": 6, "type": "PacketPokerBuyInLimits", "best": 1000000}, {"game_id": 6, "serial": 0, "cookie": "", "type": "PacketPokerBatchMode"}, {"blind": true, "buy_in_payed": false, "wait_for": false, "name": "BOTyowtAc", "url": "random", "auto": false, "outfit": "random", "seat": 0, "cookie": "", "remove_next_turn": false, "sit_out": false, "game_id": 6, "serial": 90, "auto_blind_ante": true, "type": "PacketPokerPlayerArrive", "sit_out_next_turn": false}, {"game_id": 6, "type": "PacketPokerSeats", "seats": [90, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, {"cookie": "", "serial": 90, "percentile": null, "type": "PacketPokerPlayerStats", "rank": null}, {"money": 245000, "cookie": "", "game_id": 6, "serial": 90, "type": "PacketPokerPlayerChips", "bet": 0}, {"money": [1, 5000, 10000, 9, 25000, 4, 50000, 1], "length": 19, "game_id": 6, "serial": 90, "type": "PacketPokerClientPlayerChips", "bet": []}, {"game_id": 6, "serial": 90, "cookie": "", "type": "PacketPokerSit"}, {"game_id": 6, "serial": 0, "cookie": "", "type": "PacketPokerStreamMode"}]',

    handle: function (packet) {
      equals(packet, '{"type":"PacketPokerTableJoin","game_id":' + game_id + '}');
    }
  };

  ActiveXObject.prototype.server = new PokerServer();

  var callback = function (server, users) {
      equals(users[0].chips, 245000);
      equals(users[0].name, 'BOTyowtAc');
      equals(users[0].serial, 90);
      equals(users[0].seat, 0);
      equals(server.spawnTable, 'fake');
      equals(server.state, server.RUNNING);
      equals(JSON.stringify(server.tables), '{}');
      start_and_cleanup();
    };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.spawnTable = 'fake';
  server.tableInformation(game_id, callback);
  equals(server.state, server.TABLE_JOIN);
});

test("jpoker.server.rejoin", function () {
  expect(5);
  stop();

  var reconnectFinish = jpoker.server.defaults.reconnectFinish;
  jpoker.server.defaults.reconnectFinish = function (server) {
    jpoker.server.defaults.reconnectFinish = reconnectFinish;
    ok(true, 'reconnectFinish called');
    start_and_cleanup();
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: '[{"type": "PacketPokerPlayerPlaces", "tables": [' + game_id + '], "tourneys": []}]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  server.notifyUpdate(table_packet);

  var player_serial = 43;
  var player_seat = 2;
  var player_name = 'username';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];

  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });

  var destroyed = false;
  table.registerUpdate(function (table, what, packet) {
    if (packet.type == 'PacketPokerTableDestroy') {
      destroyed = true;
      return false;
    }
    return true;
  });
  var expected = server.MY;
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketState') {
      equals(server.state, expected);
      if (expected == server.MY) {
        expected = server.RUNNING;
      } else if (expected == server.RUNNING) {
        return false;
      }
    }
    return true;
  });
  server.tableJoin = function (other_game_id) {
    equals(other_game_id, game_id, 'rejoin same table');
  };

  server.getUserInfo = function () {
    equals(true, true, 'getUserInfo called');
  };

  server.rejoin();
});

test("jpoker.server.rejoin waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.callbacks[0] = [];
  server.rejoin(0);
  equals(server.callbacks[0].length, 1, 'rejoin callback registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'rejoin callback still in place');
});

test("jpoker.server.refresh clearInterval", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var oldTimer = 42;
  var newTimer = 43;
  jpokerRefresh = jpoker.refresh;
  jpoker.refresh = function () {
    jpoker.refresh = jpokerRefresh;
    return {
      timer: newTimer
    };
  };
  server.clearInterval = function (id) {
    equals(id, oldTimer, 'timer cleared');
  };
  server.timers.foo = {
    timer: oldTimer
  };
  server.refresh('foo');
  equals(server.timers.foo.timer, newTimer, 'timer updated');
});

test("jpoker.server.stopRefresh clearInterval", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var newTimer = 43;
  jpokerRefresh = jpoker.refresh;
  jpoker.refresh = function () {
    jpoker.refresh = jpokerRefresh;
    return {
      timer: newTimer
    };
  };
  server.clearInterval = function (id) {
    equals(id, newTimer, 'timer cleared');
  };
  server.refresh('foo');
  server.stopRefresh('foo');
  equals(server.timers.foo, undefined, 'timer tag cleared');
});

test("jpoker.server.login", function () {
  expect(7);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  equals(server.loggedIn(), false);

  var packets = [];
  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '[{"type": "PacketAuthOk"}, {"type": "PacketSerial", "serial": 1}]',

    handle: function (packet) {
      packets.push(packet);
    }
  };

  ActiveXObject.prototype.server = new PokerServer();

  var logname = "name";
  server.login(logname, "password");
  server.registerUpdate(function (server, what, packet) {
    switch (packet.type) {
    case "PacketSerial":
      equals(packets[0].indexOf('PacketLogin') >= 0, true, 'Login');
      equals(server.loggedIn(), true, "loggedIn");
      equals(server.userInfo.name, logname, "logname");
      equals(server.session != 'clear', true, "has session");
      equals(server.connected(), true, "connected");
      start_and_cleanup();
      return false;

    case "PacketConnectionState":
      equals(server.connected(), true, "connected");
      return true;

    default:
      throw "unexpected packet type " + packet.type;
    }
  });
});

test("jpoker.server.login: refused", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  var PokerServer = function () {};

  var refused = "not good";
  PokerServer.prototype = {
    outgoing: '[{"type": "PacketAuthRefused", "message": "' + refused + '"}]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf(refused) >= 0, true, "refused");
    jpoker.dialog = dialog;
    start_and_cleanup();
  };
  server.login("name", "password");
});

test("jpoker.server.login: already logged", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  var PokerServer = function () {};

  var refused = "not good";
  PokerServer.prototype = {
    outgoing: '[{"type": "PacketError", "other_type": ' + jpoker.packetName2Type.LOGIN + ' }]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf("already logged") >= 0, true, "already logged");
    jpoker.dialog = dialog;
    start_and_cleanup();
  };
  server.login("name", "password");
});

test("jpoker.server.login: serial is set", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 1;
  var caught = false;
  try {
    server.login("name", "password");
  } catch (error) {
    equals(error.indexOf("serial is") >= 0, true, "serial is set");
    caught = true;
  }
  equals(caught, true, "caught is true");

  server.serial = 0;

  cleanup();
});

test("jpoker.server.login waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.callbacks[0] = [];
  server.login(0);
  equals(server.callbacks[0].length, 1, 'login callback registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'login callback still in place');
});

test("jpoker.server.logout", function () {
  expect(4);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 1;
  server.serial = "logname";
  server.connectionState = "connected";
  server.session = 42;
  equals(server.loggedIn(), true);
  server.registerUpdate(function (server, what, packet) {
    equals(server.loggedIn(), false);
    equals(server.userInfo.name, null, "logname");
    equals(packet.type, "PacketLogout");
    start_and_cleanup();
  });
  server.logout();
});

test("jpoker.server.getUserInfo", function () {
  expect(2);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var serial = 43;
  server.serial = serial;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerGetUserInfo');
    equals(packet.serial, serial, 'player serial');
  };
  server.getUserInfo();
  cleanup();
});

test("jpoker.server.bankroll", function () {
  expect(5);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var money = 43;
  var in_game = 44;
  var points = 45;
  var currency_serial = 1;
  var packet = {
    type: 'PacketPokerUserInfo',
    'money': {}
  };
  var currency_key = 'X' + currency_serial;
  packet.money[currency_key] = [money * 100, in_game * 100, points];
  server.handler(server, 0, packet);
  equals(server.userInfo.money[currency_key][0], money * 100, 'money');
  equals(server.bankroll(currency_serial), 0, 'bankroll');
  var player_serial = 3;
  server.serial = player_serial;
  equals(server.bankroll(33333), 0, 'no bankroll for currency');
  equals(server.bankroll(currency_serial), money, 'bankroll');

  var game_id = 100;
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  table.currency_serial = currency_serial;
  server.handler(server, 0, packet);
  equals(table.buyIn.bankroll, money, 'table.buyIn.bankroll');

  cleanup();
});

test("jpoker.server.tourneyRegister", function () {
  expect(4);
  stop();

  var serial = 43;
  var game_id = 2;
  var TOURNEY_REGISTER_PACKET = {
    'type': 'PacketPokerTourneyRegister',
    'serial': serial,
    'game_id': game_id
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerTourneyRegister');
    equals(packet.serial, serial, 'player serial');
    equals(packet.game_id, game_id, 'tournament id');
    equals(server.getState(), server.TOURNEY_REGISTER);
    server.queueIncoming([TOURNEY_REGISTER_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerTourneyRegister') {
      server.timers = {
        'tourneyDetails': {
          timer: 0,
          request: start_and_cleanup
        }
      };
      return false;
    }
    return true;
  });
  server.tourneyRegister(game_id);
});

test("jpoker.server.tourneyRegister error", function () {
  expect(1);
  stop();

  var serial = 43;
  var game_id = 2;
  var ERROR_PACKET = {
    'message': 'server error message',
    'code': 2,
    'type': 'PacketError',
    'other_type': jpoker.packetName2Type.PACKET_POKER_TOURNEY_REGISTER
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;
  server.sendPacket = function (packet) {
    server.queueIncoming([ERROR_PACKET]);
  };
  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message, "Player {serial} already registered in tournament {game_id}".supplant({
      game_id: game_id,
      serial: serial
    }));
    jpoker.dialog = dialog;
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketError') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.tourneyRegister(game_id);
});

test("jpoker.server.tourneyRegister waiting", function () {
  expect(4);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;
  server.callbacks[0] = [];
  server.callbacks[game_id] = [];
  server.tourneyRegister(game_id);
  equals(server.callbacks[0].length, 1, 'tourneyRegister callbacks[0] registered');
  equals(server.callbacks[game_id].length, 1, 'tourneyRegister callbacks[game_id] registered');
  var callback = server.callbacks[0][0];
  var callback_game_id = server.callbacks[game_id][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'tourneyRegister callback still in place');
  server.notify(game_id, {
    type: 'Packet'
  });
  equals(server.callbacks[game_id][0], callback_game_id, 'tourneyRegister callback_game_id still in place');
  cleanup();
});

test("jpoker.server.tourneyUnregister", function () {
  expect(4);
  stop();

  var serial = 43;
  var game_id = 2;
  var TOURNEY_REGISTER_PACKET = {
    'type': 'PacketPokerTourneyUnregister',
    'serial': serial,
    'game_id': game_id
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerTourneyUnregister');
    equals(packet.serial, serial, 'player serial');
    equals(packet.game_id, game_id, 'tournament id');
    equals(server.getState(), server.TOURNEY_REGISTER);
    server.queueIncoming([TOURNEY_REGISTER_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerTourneyUnregister') {
      server.timers = {
        'tourneyDetails': {
          timer: 0,
          request: start_and_cleanup
        }
      };
      return false;
    }
    return true;
  });
  server.tourneyUnregister(game_id);
});

test("jpoker.server.tourneyUnregister error", function () {
  expect(1);
  stop();

  var serial = 43;
  var game_id = 2;
  var ERROR_PACKET = {
    'message': 'server error message',
    'code': 3,
    'type': 'PacketError',
    'other_type': 117
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;
  server.sendPacket = function (packet) {
    server.queueIncoming([ERROR_PACKET]);
  };
  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message, "It is too late to unregister player {serial} from tournament {game_id}".supplant({
      game_id: game_id,
      serial: serial
    }));
    jpoker.dialog = dialog;
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketError') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.tourneyUnregister(game_id);
});

test("jpoker.server.tourneyUnregister waiting", function () {
  expect(4);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;
  server.callbacks[0] = [];
  server.callbacks[game_id] = [];
  server.tourneyUnregister(game_id);
  equals(server.callbacks[0].length, 1, 'tourneyUnregister callbacks[0] registered');
  equals(server.callbacks[game_id].length, 1, 'tourneyUnregister callbacks[game_id] registered');
  var callback = server.callbacks[0][0];
  var callback_game_id = server.callbacks[game_id][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'tourneyUnregister callback still in place');
  server.notify(game_id, {
    type: 'Packet',
    id: game_id
  });
  equals(server.callbacks[game_id][0], callback_game_id, 'tourneyUnregister callback_game_id still in place');
  cleanup();
});

test("jpoker.server.getPersonalInfo", function () {
  expect(3);
  stop();

  var serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': '',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': serial,
    'password': '',
    'addr_country': '',
    'name': 'testuser',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': '',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerGetPersonalInfo');
    equals(packet.serial, serial, 'player serial');
    equals(server.getState(), server.PERSONAL_INFO);
    server.queueIncoming([PERSONAL_INFO_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerPersonalInfo') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.getPersonalInfo();
});

test("jpoker.server.getPersonalInfo not logged", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = 0;

  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf("must be logged in") >= 0, true, "should be logged");
    jpoker.dialog = dialog;
    start_and_cleanup();
  };
  server.getPersonalInfo();
});


test("jpoker.server.getPersonalInfo waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 42;
  var game_id = 100;
  server.callbacks[0] = [];
  server.getPersonalInfo(game_id);
  equals(server.callbacks[0].length, 1, 'getPersonalInfo callbacks[0] registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'getPersonalInfo callback still in place');
});

test("jpoker.server.getPlayerPlaces", function () {
  expect(5);
  stop();

  var serial = 42;
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    serial: 42,
    tables: [11, 12, 13],
    tourneys: [21, 22, 23]
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerGetPlayerPlaces');
    equals(packet.serial, serial, 'player serial');
    equals(server.getState(), server.PLACES);
    server.queueIncoming([PLAYER_PLACES_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerPlayerPlaces') {
      equals(packet.tables[0], 11, 'packet.tables');
      equals(packet.tourneys[0], 21, 'packet.tourneys');
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.getPlayerPlaces();
});

test("jpoker.server.getPlayerPlaces with serial argument", function () {
  expect(5);
  stop();

  var serial = 42;
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    serial: 42,
    tables: [11, 12, 13],
    tourneys: [21, 22, 23]
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerGetPlayerPlaces');
    equals(packet.serial, serial, 'player serial');
    equals(server.getState(), server.PLACES);
    server.queueIncoming([PLAYER_PLACES_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerPlayerPlaces') {
      equals(packet.tables[0], 11, 'packet.tables');
      equals(packet.tourneys[0], 21, 'packet.tourneys');
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.getPlayerPlaces(serial);
});

test("jpoker.server.getPlayerPlaces not logged", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = 0;

  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf("must be logged in") >= 0, true, "should be logged");
    jpoker.dialog = dialog;
    start_and_cleanup();
  };
  server.getPlayerPlaces();
});

test("jpoker.server.getPlayerPlaces waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 42;
  var game_id = 100;
  server.callbacks[0] = [];
  server.getPlayerPlaces();
  equals(server.callbacks[0].length, 1, 'getPlayerPlaces callbacks[0] registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'getPlayerPlaces callback still in place');
});

test("jpoker.server.getPlayerPlacesByName", function () {
  expect(5);
  stop();

  var name = 'user';
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    name: name,
    tables: [11, 12, 13],
    tourneys: [21, 22, 23]
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerGetPlayerPlaces');
    equals(packet.name, name, 'player name');
    equals(server.getState(), server.PLACES);
    server.queueIncoming([PLAYER_PLACES_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerPlayerPlaces') {
      equals(packet.tables[0], 11, 'places.tables');
      equals(packet.tourneys[0], 21, 'places.tourneys');
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.getPlayerPlacesByName(name);
});

test("jpoker.server.getPlayerPlacesByName waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 42;
  var game_id = 100;
  server.callbacks[0] = [];
  server.getPlayerPlacesByName('user');
  equals(server.callbacks[0].length, 1, 'getPlayerPlacesByName callbacks[0] registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'getPlayerPlacesByName callback still in place');
});

test("jpoker.server.getPlayerPlacesByName failed", function () {
  expect(4);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf("No such user: user999") >= 0, true, "no such user");
    jpoker.dialog = dialog;
  };
  equals(server.callbacks[0].length, 1, 'no getPlayerPlacesByName callback yet');
  server.getPlayerPlacesByName('user999');
  equals(server.callbacks[0].length, 2, 'no getPlayerPlacesByName callback yet');
  server.notify(0, {
    type: 'PacketError',
    other_type: jpoker.packetName2Type.PACKET_POKER_PLAYER_PLACES
  });
  equals(server.callbacks[0].length, 1, 'getPlayerPlacesByName callback cleared');
  start_and_cleanup();
});

test("jpoker.server.getPlayerPlacesByName failed no dialog", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    ok(false, 'dialog not called');
  };
  server.getPlayerPlacesByName('user999', {
    dialog: false
  });
  server.registerUpdate(function (server, what, packet) {
    equals(packet.type, 'PacketError', 'packer error update call');
  });
  server.notify(0, {
    type: 'PacketError',
    other_type: jpoker.packetName2Type.PACKET_POKER_PLAYER_PLACES
  });
  jpoker.dialog = dialog;
  start_and_cleanup();
});

test("jpoker.server.getPlayerStats", function () {
  expect(5);
  stop();

  var serial = 42;
  var PLAYER_STATS_PACKET = {
    type: 'PacketPokerPlayerStats',
    serial: serial,
    rank: 100,
    percentile: 75
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerGetPlayerStats');
    equals(packet.serial, serial, 'player serial');
    equals(server.getState(), server.STATS);
    server.queueIncoming([PLAYER_STATS_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerPlayerStats') {
      equals(packet.rank, 100, 'packet.rank');
      equals(packet.percentile, 75, 'packet.percentile');
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.getPlayerStats(serial);
});

test("jpoker.server.getPlayerStats waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;
  server.callbacks[0] = [];
  server.getPlayerStats(42);
  equals(server.callbacks[0].length, 1, 'getPlayerStats callbacks[0] registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'getPlayerStats callback still in place');
});

test("jpoker.server.selectTables", function () {
  expect(3);
  stop();

  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": [{
      "observers": 1,
      "name": "One",
      "percent_flop": 98,
      "average_pot": 1000,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 220,
      "betting_structure": "2-4-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 4,
      "waiting": 0,
      "skin": "default",
      "id": 100,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Two",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 101,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Three",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-pot-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 102,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }]
  };

  var string = 'dummy';
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerTableSelect');
    equals(packet.string, string);
    equals(server.getState(), server.TABLE_LIST);
    server.queueIncoming([TABLE_LIST_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerTableList') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.selectTables(string);
});

test("jpoker.server.selectTables waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 42;
  var game_id = 100;
  server.callbacks[0] = [];
  server.selectTables('');
  equals(server.callbacks[0].length, 1, 'selectTables callbacks[0] registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'selectTables callback still in place');
});


test("jpoker.server.setPersonalInfo", function () {
  expect(8);
  stop();

  var serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': serial,
    'password': '',
    'addr_country': '',
    'name': 'testuser',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerSetAccount');
    equals(packet.serial, serial, 'player serial');
    equals(packet.firstname, 'John', 'firstname');
    equals(packet.lastname, 'Doe', 'lastname');
    equals(packet.password, 'testpassword', 'password');
    equals(server.getState(), server.PERSONAL_INFO);
    server.queueIncoming([PERSONAL_INFO_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerPersonalInfo') {
      equals(packet.firstname, 'John');
      equals(packet.lastname, 'Doe');
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.setPersonalInfo({
    firstname: 'John',
    lastname: 'Doe',
    password: 'testpassword',
    password_confirmation: 'testpassword'
  });
});

test("jpoker.server.createAccount", function () {
  expect(8);
  stop();

  var serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': serial,
    'password': '',
    'addr_country': '',
    'name': 'john',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.sendPacket = function (packet) {
    if (packet.type == 'PacketPokerCreateAccount') {
      equals(packet.name, 'john', 'name');
      equals(packet.password, 'testpassword', 'password');
      equals(packet.email, 'john@doe.com', 'email');
      equals(server.getState(), server.CREATE_ACCOUNT);
    }
    server.queueIncoming([PERSONAL_INFO_PACKET]);
  };
  server.login = function (name, password) {
    equals(name, 'john');
    equals(password, 'testpassword');
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerPersonalInfo') {
      equals(packet.name, 'john');
      equals(packet.serial, 42);
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.createAccount({
    name: 'john',
    password: 'testpassword',
    password_confirmation: 'testpassword',
    email: 'john@doe.com'
  });
});

test("jpoker.server.createAccount PacketError", function () {
  expect(1);
  stop();

  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '[{"type": "Ignored"}, {"type": "PacketError", "message": "ERROR"}]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': serial,
    'password': '',
    'addr_country': '',
    'name': 'john',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketError') {
      equals($('#jpokerDialog').text().indexOf(packet.message) >= 0, true, 'error dialog does not contain message from server : ' + packet.message);
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.createAccount({
    name: 'john',
    password: 'testpassword',
    password_confirmation: 'testpassword',
    email: 'john@doe.com'
  });
});

test("jpoker.server.createAccount passwords do not match", function () {
  expect(1);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.createAccount({
    name: 'john',
    password: 'testpassword',
    password_confirmation: 'bad',
    email: 'john@doe.com'
  });
  equals($('#jpokerDialog').text().indexOf('confirmation does not match') >= 0, true, 'no match');
  cleanup();
});

test("jpoker.server.setPersonalInfo password confirmation failed", function () {
  expect(1);
  stop();

  var serial = 42;

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message, 'Password confirmation does not match');
    jpoker.dialog = dialog;
    start_and_cleanup();
  };
  server.setPersonalInfo({
    firstname: 'John',
    lastname: 'Doe',
    password: 'foo',
    password_confirmation: 'bar'
  });
});

test("jpoker.server.setPersonalInfo error", function () {
  expect(1);
  stop();

  var serial = 42;
  var ERROR_PACKET = {
    'message': 'server error message',
    'code': 2,
    'type': 'PacketError',
    'other_type': jpoker.packetName2Type.PACKET_POKER_SET_ACCOUNT
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  server.sendPacket = function (packet) {
    server.queueIncoming([ERROR_PACKET]);
  };
  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message, ERROR_PACKET.message);
    jpoker.dialog = dialog;
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketError') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.setPersonalInfo({
    firstname: 'John',
    lastname: 'Doe'
  });
});

test("jpoker.server.setLocale", function () {
  expect(5);
  stop();

  var serial = 42;
  var game_id = 12;

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  var locale = 'fr_FR.UTF-8';
  server.sendPacket = function (packet) {
    equals(server.getState(), server.LOCALE);
    equals(packet.type, 'PacketPokerSetLocale');
    equals(packet.serial, serial, 'player serial');
    equals(packet.locale, locale, 'fr locale');
    equals(packet.game_id, game_id, 'game_id');
    server.queueIncoming([{
      'type': 'PacketAck'
    }]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketAck') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.setLocale(locale, game_id);
});

test("jpoker.server.setLocale error", function () {
  expect(6);
  stop();

  var serial = 42;

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = serial;

  var locale = 'ja_JP.UTF-8';
  var ERROR_PACKET = {
    'type': 'PacketPokerError',
    'message': 'no ja translation',
    'other_type': jpoker.packetName2Type.PACKET_POKER_SET_LOCALE
  };
  server.sendPacket = function (packet) {
    equals(server.getState(), server.LOCALE);
    equals(packet.type, 'PacketPokerSetLocale');
    equals(packet.serial, serial, 'player serial');
    equals(packet.locale, locale, 'ja locale');
    server.queueIncoming([ERROR_PACKET]);
  };
  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    ok(message.indexOf('setLocale failed:') >= 0, 'setLocale failed');
    ok(message.indexOf(ERROR_PACKET.message) >= 0, ERROR_PACKET.message);
    jpoker.dialog = dialog;
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerError') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.setLocale(locale);
});

test("jpoker.server.setLocale waiting", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;
  server.callbacks[0] = [];
  server.setLocale('fr_FR.UTF-8');
  equals(server.callbacks[0].length, 1, 'setLocale callbacks[0] registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'setLocale callback still in place');
  cleanup();
});

test("jpoker.server.tablePick", function () {
  expect(5);
  stop();

  var TABLE_PACKET = {
    "type": "PacketPokerTable",
    "id": 100,
    "reason": "TablePicker"
  };

  var string = 'dummy';
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 42;
  var sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    if (packet.type == 'PacketPokerTablePicker') {
      equals(packet.variant, 'holdem');
      equals(packet.betting_structure, undefined, 'betting_structure');
      equals(packet.currency_serial, 10, 'currency_serial');
      equals(packet.auto_blind_ante, true, 'auto_blind_ante');
      equals(server.getState(), server.TABLE_PICK);
      server.queueIncoming([TABLE_PACKET]);
    }
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerTable') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.tablePick({
    variant: 'holdem',
    currency_serial: 10
  });
});

test("jpoker.server.tablePick default", function () {
  expect(6);
  stop();

  var TABLE_PACKET = {
    "type": "PacketPokerTable",
    "id": 100,
    "reason": "TablePicker"
  };

  var string = 'dummy';
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 42;
  var sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    server.sendPacket = sendPacket;
    equals(packet.type, 'PacketPokerTablePicker');
    equals(packet.variant, undefined, 'no variant');
    equals(packet.betting_structure, undefined, 'no betting_structure');
    equals(packet.currency_serial, undefined, 'no currency_serial');
    equals(packet.auto_blind_ante, true, 'auto_blind_ante');
    equals(server.getState(), server.TABLE_PICK);
    server.queueIncoming([TABLE_PACKET]);
  };
  server.registerUpdate(function (server, what, packet) {
    if (packet.type == 'PacketPokerTable') {
      server.queueRunning(start_and_cleanup);
      return false;
    }
    return true;
  });
  server.tablePick({});
});

test("jpoker.server.tablePick not logged", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = 0;

  var dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf("must be logged in") >= 0, true, "should be logged");
    jpoker.dialog = dialog;
    start_and_cleanup();
  };
  server.tablePick({});
});

test("jpoker.server.tablePick waiting", function () {
  expect(3);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = 42;
  var game_id = 100;
  server.callbacks[0] = [];
  server.tablePick({});
  equals(server.callbacks[0].length, 1, 'tablePick callbacks[0] registered');
  var callback = server.callbacks[0][0];
  server.notify(0, {
    type: 'Packet'
  });
  equals(server.callbacks[0][0], callback, 'tablePick callback still in place');
  server.notify(0, {
    type: 'PacketPokerTable',
    id: 100
  }); // no reason: TablePicker
  equals(server.callbacks[0][0], callback, 'tablePick callback still in place');
});


test("jpoker.server.tableQuit", function () {
  expect(3);
  stop();
  var player_serial = 42;
  var game_id = 100;

  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '[]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.serial = player_serial;
  var sendPacket = server.sendPacket;
  server.sendPacket = function (packet, callback) {
    if (packet.type == 'PacketPokerTableQuit') {
      equals(packet.game_id, game_id);
      equals(server.state, server.TABLE_QUIT);
      callback();
      equals(server.state, server.RUNNING);
      server.queueRunning(start_and_cleanup);
    }
  };
  server.tableQuit(game_id);
});

test("jpoker.server.tableQuit not logged", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });

  server.serial = 0;

  var dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf("must be logged in") >= 0, true, "should be logged");
    jpoker.dialog = dialog;
    start_and_cleanup();
  };
  server.tableQuit(100);
});

test("jpoker.server.setInterval", function () {
  expect(1);
  stop();
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var id = server.setInterval(function () {
    ok(true, "callback called");
    clearInterval(id);
    start();
  }, 0);
});

test("jpoker.server.setState", function () {
  expect(1);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var undefinedState = undefined;
  var error = jpoker.error;
  jpoker.error = function (reason) {
    jpoker.error = error;
    equals('undefined state', reason, 'error undefined state');
  };
  server.setState(undefined);
});

test("jpoker.server.urls", function () {
  expect(8);
  var url;
  url = 'http://host/POKER_REST';
  $.cookie('JPOKER_AUTH_' + jpoker.url2hash(url), 'hash', {
    path: '/'
  });
  var server = jpoker.serverCreate({
    url: url
  });
  equals(server.urls.avatar, 'http://host/AVATAR');
  equals(server.urls.upload, 'http://host/UPLOAD?auth=hash');

  url = '/POKER_REST';
  $.cookie('JPOKER_AUTH_' + jpoker.url2hash(url), 'hash', {
    path: '/'
  });
  server = jpoker.serverCreate({
    url: url
  });
  equals(server.urls.avatar, '/AVATAR');
  equals(server.urls.upload, '/UPLOAD?auth=hash');

  url = 'url';
  $.cookie('JPOKER_AUTH_' + jpoker.url2hash(url), 'hash', {
    path: '/'
  });
  server = jpoker.serverCreate({
    url: url
  });
  equals(server.urls.avatar, 'AVATAR');
  equals(server.urls.upload, 'UPLOAD?auth=hash');

  server = jpoker.serverCreate({
    url: 'url',
    urls: {
      avatar: 'avatar',
      upload: 'upload'
    }
  });
  equals(server.urls.avatar, 'avatar');
  equals(server.urls.upload, 'upload');
});

test("jpoker.server.error: throw correct exception", function () {
  expect(1);
  var jpokerConsole = jpoker.console;
  jpoker.console = undefined;
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.state = 'unknown';
  server.registerHandler(0, function () {
    server.notifyUpdate({});
  });
  server.registerUpdate(function () {
    throw 'dummy error';
  });
  try {
    server.handle(0, {});
  } catch (e) {
    equals(e, 'dummy error');
  }
  jpoker.console = jpokerConsole;
  cleanup();
});

test("jpoker.server.init/uninit: state running", function () {
  expect(2);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  equals(server.state, 'running');
  server.state = 'dummy';
  server.uninit();
  equals(server.state, 'running');
  cleanup();
});

test("jpoker.server.reset: call clearTimers", function () {
  expect(1);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.clearTimers = function () {
    ok(true, "clearTimers called");
  };
  server.reset();
  server.clearTimers = function () {};
  server.uninit();
  cleanup();
});

//
// jpoker.connection
//
test("jpoker.connection:longPoll", function () {
  expect(9);
  stop();
  var self = new jpoker.connection();
  equals(self.connectionState, 'disconnected');
  var longPoll_count = 0;
  self.registerUpdate(function (server, what, data) {
    ok(server.pendingLongPoll, 'pendingLongPoll');
    equals(server.longPollTimer, -1, 'longPollTimer');
    equals(data.type, 'PacketConnectionState');
    equals(server.connectionState, 'connected');
    if (++longPoll_count >= 2) {
      server.longPollFrequency = -1;
      server.reset();
      start();
    } else {
      server.connectionState = 'disconnected';
    }
    return true;
  });
  self.longPollFrequency = 100;
  self.sentTime = jpoker.now() - self.longPollFrequency;
  self.longPoll();
});

test("jpoker.connection:longPoll not if pending request", function () {
  expect(3);
  stop();
  var self = new jpoker.connection();
  equals(self.connectionState, 'disconnected');
  ActiveXObject.defaults.readyState = 5; // 5 is not 4 hence not ready
  jQuery.ajax({
    mode: 'queue',
    url: 'url',
    timeout: 1000
  }); // will block the ajaxQueue for one second
  ActiveXObject.defaults.readyState = 4;

  var longPoll_count = 0;
  self.registerUpdate(function (server, what, data) {
    equals(data.type, 'PacketConnectionState');
    equals(server.connectionState, 'connected');
    if (++longPoll_count >= 1) {
      server.longPollFrequency = -1;
      server.reset();
      start();
    } else {
      server.connectionState = 'disconnected';
    }
    return true;
  });
  self.longPollFrequency = 100;
  self.sentTime = 0; // longPoll should fire immediately
  sendPacket = self.sendPacket;
  self.sendPacket = function (packet) {
    ok(false, JSON.stringify(packet));
    start();
  };
  self.longPoll(); // but it will not because the ajaxQueue is not empty
  self.sendPacket = sendPacket;
});

test("jpoker.connection:longPoll PacketPokerLongPollReturn", function () {
  expect(3);

  var self = new jpoker.connection();
  self.sendPacketAjax = function (packet, mode) {};
  self.sendPacket({
    type: 'PacketPokerLongPoll'
  });
  ok(self.pendingLongPoll);
  self.sendPacketAjax = function (packet, mode) {
    if (mode == 'queue') {
      equals(packet.type, 'Packet');
    } else if (mode == 'direct') {
      equals(packet.type, 'PacketPokerLongPollReturn');
    } else {
      ok(false, 'should not reach this statment');
    }
  };
  self.sendPacket({
    type: 'Packet'
  });
  self.longPollFrequency = -1;
  self.reset();
});

test("jpoker.connection:longPoll PacketPokerLongPollReturn not received ", function () {
  expect(1);
  stop();
  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '[]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var self = new jpoker.connection();
  self.receivePacket = function (data) {
    ok(false, 'receive not called');
  };
  self.sendPacket({
    type: 'PacketPokerLongPollReturn'
  });
  self.receivePacket = function (data) {
    ok(true, 'receive called');
    start_and_cleanup();
  };
  self.sendPacket({
    type: 'Packet'
  });
});

test("jpoker.connection:longPoll frequency", function () {
  expect(8);
  now = jpoker.now;
  var clock = 1000;
  jpoker.now = function () {
    return clock++;
  };
  var self = new jpoker.connection();
  //
  // A longPoll is scheduled in longPollFrequency
  //
  self.longPollFrequency = 100;
  self.sendPacket = function () {
    equals(1, 0, 'sendPacket called');
  };
  sentTime = self.sentTime = clock;
  self.setTimeout = function (fun, when) {
    equals(when, self.longPollFrequency, 'timeout 1');
  };
  self.longPoll();
  equals(sentTime, self.sentTime, 'sentTime');
  //
  // A longPoll is scheduled in longPollFrequency - 10ms because
  // longPoll is called 10ms after the last packet was sent
  //
  sentTime = self.sentTime = clock - 10;
  self.setTimeout = function (fun, when) {
    equals(when, self.longPollFrequency - 10, 'timeout 2');
  };
  self.longPoll();
  equals(sentTime, self.sentTime, 'sentTime');
  //
  // A longPoll is scheduled in minLongPollFrequency because
  // longPoll is called more than longPollFrequency 
  // after the last packet was sent, i.e. the delay cannot be 
  // less than 30ms
  //
  sentTime = self.sentTime = clock - self.longPollFrequency + 10;
  self.setTimeout = function (fun, when) {
    equals(when, self.minLongPollFrequency, 'timeout 3');
  };
  self.longPoll();
  equals(sentTime, self.sentTime, 'sentTime');
  //
  // A longPoll is scheduled in longPollFrequency clicks
  //
  stop();
  self.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerLongPoll');
    this.sentTime = clock;
    start();
  };
  self.sentTime = 0;
  self.longPoll();
  self.longPollFrequency = -1;
  self.reset();
  equals(0, self.sentTime, 'sentTime reset');
  jpoker.now = now;
});

test("jpoker.connection:sendPacket error 404", function () {
  expect(1);
  stop();
  var self = new jpoker.connection();

  var error = jpoker.error;
  jpoker.error = function (reason) {
    jpoker.error = error;
    equals(reason.xhr.status, 404);
    start();
  };
  ActiveXObject.defaults.status = 404;
  self.sendPacket({
    type: 'type'
  });
  ActiveXObject.defaults.status = 200;
});

test("jpoker.connection:sendPacket error 500", function () {
  expect(1);
  stop();
  var self = new jpoker.connection();

  var error = jpoker.error;
  jpoker.error = function (reason) {
    jpoker.error = error;
    equals(reason.xhr.status, 500);
    start();
  };
  ActiveXObject.defaults.status = 500;
  self.sendPacket({
    type: 'type'
  });
  ActiveXObject.defaults.status = 200;
});

test("jpoker.connection:sendPacket abort ajax is ignored", function () {
  expect(2);
  stop();
  var self = new jpoker.connection();
  var _ajax = self.ajax;
  var jpokerError = jpoker.error;
  jpoker.error = function (reason) {
    ok(false, 'jpoker error must not be called called');
  };
  self.ajax = function (settings) {
    var _error = settings.error;
    settings.error = function (xhr, status, error) {
      var result = _error(xhr, status, error);
      ActiveXObject.defaults.status = 200;
      ok(true, 'error ignored');
      equals(result, undefined, 'do not retry');
      jpoker.error = jpokerError;
      start();
      return result;
    };
    settings.success = function () {
      ok(false, 'unexpected success');
      jpoker.error = jpokerError;
    };
    _ajax(settings);
  };
  ActiveXObject.defaults.status = 0;
  self.sendPacket({
    type: 'type'
  });
});

test("jpoker.connection:sendPacket retry 12152", function () {
  expect(2);
  stop();
  var self = new jpoker.connection();
  var _ajax = self.ajax;
  var jpokerError = jpoker.error;
  jpoker.error = function (reason) {
    ok(false, 'jpoker error not called');
  };
  self.ajax = function (settings) {
    var _error = settings.error;
    settings.error = function (xhr, status, error) {
      var result = _error(xhr, status, error);
      ActiveXObject.defaults.status = 200;
      ok(true, 'error');
      return result;
    };
    settings.success = function () {
      ok(true, 'retry success');
      jpoker.error = jpokerError;
      start();
    };
    _ajax(settings);
  };
  ActiveXObject.defaults.status = 12152;
  self.sendPacket({
    type: 'type'
  });
});

test("jpoker.connection:sendPacket retry 12030", function () {
  expect(2);
  stop();
  var self = new jpoker.connection();
  var _ajax = self.ajax;
  var jpokerError = jpoker.error;
  jpoker.error = function (reason) {
    ok(false, 'jpoker error not called');
  };
  self.ajax = function (settings) {
    var _error = settings.error;
    settings.error = function (xhr, status, error) {
      var result = _error(xhr, status, error);
      ActiveXObject.defaults.status = 200;
      ok(true, 'error');
      return result;
    };
    settings.success = function () {
      ok(true, 'retry success');
      jpoker.error = jpokerError;
      start();
    };
    _ajax(settings);
  };
  ActiveXObject.defaults.status = 12152;
  self.sendPacket({
    type: 'type'
  });
});

test("jpoker.connection:sendPacket retry 12031", function () {
  expect(2);
  stop();
  var self = new jpoker.connection();
  var _ajax = self.ajax;
  var jpokerError = jpoker.error;
  jpoker.error = function (reason) {
    ok(false, 'jpoker error not called');
  };
  self.ajax = function (settings) {
    var _error = settings.error;
    settings.error = function (xhr, status, error) {
      var result = _error(xhr, status, error);
      ActiveXObject.defaults.status = 200;
      ok(true, 'error');
      return result;
    };
    settings.success = function () {
      ok(true, 'retry success');
      jpoker.error = jpokerError;
      start();
    };
    _ajax(settings);
  };
  ActiveXObject.defaults.status = 12152;
  self.sendPacket({
    type: 'type'
  });
});

test("jpoker.connection:sendPacket retry count", function () {
  expect(3);
  stop();
  var self = new jpoker.connection();
  self.retryCount = 42;

  var error = jpoker.error;
  jpoker.error = function (reason) {
    jpoker.error = error;
    equals(reason.xhr.status, 12152);
    ok(reason.error.indexOf('retry') >= 0, 'retry error');
    ok(reason.error.indexOf(self.retryCount) >= 0, 'retryCount');
    ActiveXObject.defaults.status = 200;
    start_and_cleanup();
  };
  ActiveXObject.defaults.status = 12152;
  self.sendPacket({
    type: 'type'
  });
});

test("jquery ajaxQueue retry", function () {
  expect(3);
  stop();
  var ajaxQueue = $.ajax_queue;
  var retry = false;
  var settings = {
    mode: "queue",
    error: function () {
      ActiveXObject.defaults.status = 200;
      retry = true;
      return false; // retry
    },
    success: function () {
      ok(retry, 'retry');
      equals(jQuery([$.ajax_queue]).queue('ajax').length, 1, 'queue not cleared');
      setTimeout(function () {
        equals(jQuery([$.ajax_queue]).queue('ajax').length, 0, 'queue cleared');
        start_and_cleanup();
      }, 0);
    },
    data: 'foo'
  };
  ActiveXObject.defaults.status = 500;
  $.ajax(settings);
});

test("jpoker.connection:sendPacket timeout", function () {
  expect(1);
  stop();
  var self = new jpoker.connection({
    timeout: 1
  });

  self.reset = function () {
    equals(this.connectionState, 'disconnected');
    start();
  };
  self.connectionState = 'connected';
  ActiveXObject.defaults.timeout = true;
  self.sendPacket({
    type: 'type'
  });
  ActiveXObject.defaults.timeout = false;
});

test("jpoker.connection:sendPacket", function () {
  expect(7);
  var self = new jpoker.connection({
    async: false,
    mode: null
  });

  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '',

    handle: function (packet) {
      this.outgoing = "[ " + packet + " ]";
    }
  };

  ActiveXObject.prototype.server = new PokerServer();

  var clock = 1;
  jpoker.now = function () {
    return clock++;
  };
  self.clearTimeout = function (id) {};
  self.setTimeout = function (cb, delay) {
    return cb();
  };

  var handled;
  var handler = function (server, id, packet) {
      handled = [server, id, packet];
    };
  self.registerHandler(0, handler);

  var type = 'type1';
  var packet = {
    type: type
  };

  equals(self.connected(), false, "disconnected()");
  equals(self.sentTime, 0, "sentTime default");
  self.sendPacket(packet);

  equals(self.sentTime > 0, true, "sentTime updated");
  equals(handled[0], self);
  equals(handled[1], 0);
  equals(handled[2].type, type);
  equals(self.connected(), true, "connected()");
});

test("jpoker.connection:sendPacket callback", function () {
  expect(1);
  stop();
  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '[]',

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var self = new jpoker.connection();
  self.sendPacket({
    type: 'foo'
  }, function () {
    ok(true, 'callback called');
    start_and_cleanup();
  });
});

test("jpoker.connection:dequeueIncoming clearTimeout", function () {
  expect(1);
  var self = new jpoker.connection();

  var cleared = false;
  self.clearTimeout = function (id) {
    cleared = true;
  };
  self.setTimeout = function (cb, delay) {
    throw "setTimeout";
  };

  self.dequeueIncoming();

  ok(cleared, "cleared");
});

test("jpoker.connection:dequeueIncoming setTimeout", function () {
  expect(4);
  var self = new jpoker.connection();
  equals(self.dequeueFrequency, 100, 'dequeueFrequency default');

  var clock = 1;
  jpoker.now = function () {
    return clock++;
  };
  var timercalled = false;
  self.clearTimeout = function (id) {};
  self.setTimeout = function (cb, delay) {
    equals(delay, self.dequeueFrequency, 'setTimeout(dequeueFrequency)');
    timercalled = true;
  };

  // will not be deleted to preserve the delay
  self.queues[0] = {
    'high': {
      'packets': [],
      'delay': 500
    },
    'low': {
      'packets': [],
      'delay': 0
    }
  };
  // will be deleted because it is empty
  self.queues[1] = {
    'high': {
      'packets': [],
      'delay': 0
    },
    'low': {
      'packets': [],
      'delay': 0
    }
  };
  self.dequeueIncoming();

  ok(!(1 in self.queues));
  ok(timercalled);
});

test("jpoker.connection:dequeueIncoming handle", function () {
  expect(7);
  var self = new jpoker.connection();

  self.clearTimeout = function (id) {};

  var packet = {
    type: 'type1',
    time__: 1
  };
  self.queues[0] = {
    'high': {
      'packets': [],
      'delay': 0
    },
    'low': {
      'packets': [packet],
      'delay': 0
    }
  };
  var handled;
  var handler = function (com, id, packet) {
      handled = [com, id, packet];
      return true;
    };
  self.registerHandler(0, handler);
  jpoker.verbose = 2;
  jpokerMessage = jpoker.message;
  jpoker.message = function (message) {
    ok(message.indexOf('connection handle') >= 0, 'jpoker.message called');
    jpoker.message = jpokerMessage;
  };
  self.dequeueIncoming();
  self.unregisterHandler(0, handler);

  equals(self.queues[0], undefined);

  equals(handled[0], self);
  equals(handled[1], 0);
  equals(handled[2], packet);

  equals(0 in self.callbacks, false, 'not handlers for queue 0');

  equals(("time__" in packet), false);
});

test("jpoker.connection:dequeueIncoming no handler", function () {
  expect(1);
  var self = new jpoker.connection();

  var packet = {
    type: 'type1',
    time__: 1
  };
  self.queues[0] = {
    'high': {
      'packets': [],
      'delay': 0
    },
    'low': {
      'packets': [packet],
      'delay': 0
    }
  };
  self.dequeueIncoming();

  equals(self.queues[0] !== undefined, true, 'packet still in queue because no handler');
  self.queues = {};
});

test("jpoker.connection:dequeueIncoming handle error", function () {
  expect(1);
  stop();
  var self = new jpoker.connection();

  var packet = {
    type: 'type1',
    time__: 1
  };
  self.url = "jpoker.connection:dequeueIncoming handle error";
  self.queues[0] = {
    'high': {
      'packets': [],
      'delay': 0
    },
    'low': {
      'packets': [packet],
      'delay': 0
    }
  };
  var handler = function (com, id, packet) {
      throw "the error";
    };
  self.error = function (reason) {
    equals(reason, "the error");
    self.queues = {}; // prevent firing the incomingTimer
    start();
  };
  self.registerHandler(0, handler);
  self.dequeueIncoming();
});

test("jpoker.connection:dequeueIncoming delayed", function () {
  expect(6);
  var self = new jpoker.connection();

  var clock = 1;
  jpoker.now = function () {
    return clock++;
  };
  self.clearTimeout = function (id) {};

  var packet = {
    type: 'type1',
    time__: 1
  };
  var delay = 10;
  self.delayQueue(0, delay);
  equals(self.delays[0], delay);
  self.queues[0] = {
    'high': {
      'packets': [],
      'delay': 0
    },
    'low': {
      'packets': [packet],
      'delay': 0
    }
  };
  self.dequeueIncoming();
  equals(self.queues[0].low.packets[0], packet);
  equals(self.queues[0].low.delay, delay);

  var message = false;
  var message_function = jpoker.message;
  jpoker.message = function (str) {
    message = true;
  };
  self.dequeueIncoming();
  equals(self.queues[0].low.delay, delay);
  equals(message, true, "message");
  jpoker.message = message_function;

  self.noDelayQueue(0);
  equals(self.delays[0], undefined, "delays[0]");

  self.queues = {};
});

test("jpoker.connection:dequeueIncoming lagmax", function () {
  expect(4);
  var self = new jpoker.connection();

  var clock = 10;
  jpoker.now = function () {
    return clock++;
  };
  self.lagmax = 5;
  self.clearTimeout = function (id) {};

  var packet = {
    type: 'type1',
    time__: 1
  };
  self.queues[0] = {
    'high': {
      'packets': [],
      'delay': 0
    },
    'low': {
      'packets': [packet],
      'delay': 50
    }
  };
  var handled;
  var handler = function (com, id, packet) {
      handled = [com, id, packet];
      return true;
    };
  self.registerHandler(0, handler);
  self.dequeueIncoming();
  self.unregisterHandler(0, handler);
  equals(handled[0], self);
  equals(handled[1], 0);
  equals(handled[2], packet);

  equals(0 in self.callbacks, false, 'not handlers for queue 0');
});

test("jpoker.connection:queueIncoming", function () {
  expect(4);
  var self = new jpoker.connection();

  var high_type = self.high[0];
  var packets = [{
    'type': 'PacketType1'
  }, {
    'type': 'PacketType2',
    'session': 'TWISTED_SESION'
  }, {
    'type': 'PacketType3',
    'game_id': 1
  }, {
    'type': high_type,
    'game_id': 1
  }];
  self.queueIncoming(packets);
  equals(self.queues[0].low.packets[0].type, 'PacketType1');
  equals(self.queues[0].low.packets[1].type, 'PacketType2');
  equals(self.queues[1].low.packets[0].type, 'PacketType3');
  equals(self.queues[1].high.packets[0].type, high_type);

  self.queues = {};
  cleanup();
});

test("jpoker.connection: protocol", function () {
  expect(1);
  var connection = new jpoker.connection();
  equals(connection.protocol(), document.location.protocol, 'protocol');
});

test("jpoker.connection: ajax arguments", function () {
  expect(2);
  var server = new jpoker.connection({
    url: 'url'
  });
  server.ajax = function (options) {
    ok(options.url.indexOf("uid=") >= 0, 'uid');
    ok(options.url.indexOf("auth=") >= 0, 'auth');
  };
  server.sendPacket({});
  cleanup();
});

//
// jpoker.table
//
test("jpoker.table.init", function () {
  expect(4);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;

  var PokerServer = function () {};

  PokerServer.prototype = {
    outgoing: '[{"type": "PacketPokerTable", "id": ' + game_id + '}]',

    handle: function (packet) {
      equals(packet, '{"type":"PacketPokerTableJoin","game_id":' + game_id + '}');
    }
  };

  ActiveXObject.prototype.server = new PokerServer();

  var handler = function (server, what, packet) {
      if (packet.type == "PacketPokerTable") {
        equals(packet.id, game_id);
        equals(game_id in server.tables, true, game_id + " created");
        equals(server.tables[game_id].id, game_id, "id");
        start_and_cleanup();
        return false;
      }
      return true;
    };
  server.registerUpdate(handler);
  server.tableJoin(game_id);
});


test("jpoker.table.uninit", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;
  var table = new jpoker.table(server, {
    type: "PacketPokerTableJoin",
    game_id: game_id
  });
  server.tables[game_id] = table;
  var notified = false;
  var handler = function () {
      notified = true;
    };
  table.registerDestroy(handler);
  table.handler(server, game_id, {
    type: 'PacketPokerTableDestroy',
    game_id: game_id
  });
  equals(notified, true, 'destroy callback called');
  equals(game_id in server.tables, false, 'table removed from server');
});

test("jpoker.table.reinit", function () {
  expect(4);

  var url = 'url';
  var server = jpoker.serverCreate({
    url: url
  });

  var player_serial = 42;
  var player = new jpoker.player({
    url: url
  }, {
    serial: player_serial
  });
  var player_uninit_called = false;
  player.uninit = function () {
    player_uninit_called = true;
  };

  var game_id = 73;
  var thing = 'a';
  var other_thing = 'b';
  var table = new jpoker.table(server, {
    id: game_id,
    thing: thing
  });
  table.serial2player[player_serial] = player;

  var callback = function (table, what, packet) {
      equals(table.id, game_id, 'table id');
      equals(table.thing, other_thing, 'some thing changed');
      equals(player_serial in table.serial2player, false, 'serial2player is reset');
    };

  table.registerReinit(callback);
  table.reinit({
    id: game_id,
    thing: other_thing
  });
  equals(player_uninit_called, true, 'player was uninited');
});


test("jpoker.table or tourney table or not", function () {
  expect(2);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var table = new jpoker.table(server, {
    "type": "PacketPokerTable",
    "id": 101,
    "betting_structure": "15-30-no-limit"
  });
  equals(table.is_tourney, false);
  var tourney = new jpoker.table(server, {
    "type": "PacketPokerTable",
    "id": 101,
    "betting_structure": "level-15-30-no-limit"
  });
  equals(tourney.is_tourney, true);
});


test("jpoker.table.handler: PacketPokerState", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;

  // define table
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var state = 'pre-flop';
  var packet = {
    type: 'PacketPokerState',
    game_id: game_id,
    string: state
  };
  table.handler(server, game_id, packet);

  equals(table.state, state);
});

test("jpoker.table.handler: PacketPokerBetLimit", function () {
  expect(6);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;

  // define user & money
  var player_serial = 22;
  server.serial = player_serial;

  // define table
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var packet = {
    type: 'PacketPokerBetLimit',
    game_id: game_id,
    min: 500,
    max: 20000,
    step: 100,
    call: 1000,
    allin: 4000,
    pot: 2000
  };
  table.handler(server, game_id, packet);

  var keys = ['min', 'max', 'step', 'call', 'allin', 'pot'];
  for (var i = 0; i < keys.length; i++) {
    equals(table.betLimit[keys[i]] * 100, packet[keys[i]], keys[i]);
  }
});

test("jpoker.table.handler: PacketPokerTableDestroy", function () {
  expect(5);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
  jpoker.plugins.muck.sendAutoMuck = function () {};

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  var player_seat = 2;
  var player_name = 'username';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];

  equals($("#game_window" + id).size(), 1, 'game element exists');
  equals($("#seat" + player_seat + id).is(':visible'), true, 'seat visible');

  table.handler(server, game_id, {
    type: 'PacketPokerTableDestroy',
    game_id: game_id
  });

  equals(game_id in server.tables, false, 'table removed from server');
  equals(player_serial in table.serial2player, false, 'player removed from table');
  equals($("#game_window" + id).size(), 0, 'game element destroyed');

  jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
  cleanup();
});


test("jpoker.table.handler: PacketPokerInGame", function () {
  expect(7);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var player_serial = 43;
  var player_seat = 0;
  var player_name = 'username';

  for (var i = 0; i < 10; ++i) {
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      name: player_name + i,
      seat: player_seat + i,
      serial: player_serial + i,
      game_id: game_id
    });
  }
  equals(server.tables[game_id].serial2player[43].in_game, false);
  equals(server.tables[game_id].serial2player[44].in_game, false);
  equals(server.tables[game_id].serial2player[47].in_game, false);
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    players: [43, 47],
    game_id: game_id
  });
  equals(server.tables[game_id].serial2player[43].in_game, true);
  equals(server.tables[game_id].serial2player[44].in_game, false);
  equals(server.tables[game_id].serial2player[47].in_game, true);
  table.handler(server, game_id, {
    type: 'PacketPokerFold',
    serial: 43,
    game_id: game_id
  });
  equals(server.tables[game_id].serial2player[43].in_game, false);
  cleanup();
});

test("jpoker.table.handler: PacketPokerTable", function () {
  expect(6);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
  jpoker.plugins.muck.sendAutoMuck = function () {};

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  var player_seat = 2;
  var player_name = 'username';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];

  equals($("#game_window" + id).size(), 1, 'game element exists');
  equals($("#seat" + player_seat + id).is(':visible'), true, 'seat visible');

  //
  // table received and table already exists : reinit table
  //
  server.handler(server, game_id, {
    type: 'PacketPokerTable',
    game_id: game_id,
    id: game_id
  });

  equals(game_id in server.tables, true, 'table in server');
  equals(player_serial in table.serial2player, false, 'player removed from table');
  equals($("#game_window" + id).size(), 1, 'game element exists');
  equals($("#seat" + player_seat + id).is(':hidden'), true, 'seat hidden');

  jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
  cleanup();
});

test("jpoker.table.handler: PacketPokerBuyInLimits", function () {
  expect(5);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 100;

  // define user & money
  var player_serial = 22;
  server.serial = player_serial;
  var money = 43;
  var in_game = 44;
  var points = 45;
  var currency_serial = 440;
  var currency_key = 'X' + currency_serial;
  server.userInfo = {
    money: {}
  };
  server.userInfo.money[currency_key] = [money * 100, in_game * 100, points];

  // define table
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var min = 100;
  var max = 200;
  var best = 300;
  var rebuy_min = 400;
  var packet = {
    type: 'PacketPokerBuyInLimits',
    game_id: game_id,
    min: min,
    max: max,
    best: best,
    rebuy_min: rebuy_min
  };
  table.handler(server, game_id, packet);

  var keys = ['min', 'max', 'best', 'rebuy_min'];
  for (var i = 0; i < keys.length; i++) {
    equals(table.buyIn[keys[i]] * 100, packet[keys[i]], keys[i]);
  }
  equals(table.buyIn.bankroll, money, 'money');
});

test("jpoker.table.handler: PacketPokerBatchMode", function () {
  expect(1);
  var server = jpoker.serverCreate({
    url: 'url'
  });

  var game_id = 100;
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var packet = {
    'type': 'PacketPokerBatchMode',
    'game_id': game_id
  };

  table.handler(server, game_id, packet);
  ok(true, 'PacketPokerBatchMode');
});

test("jpoker.table.handler: PacketPokerStreamMode", function () {
  expect(1);
  var server = jpoker.serverCreate({
    url: 'url'
  });

  var game_id = 100;
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var packet = {
    'type': 'PacketPokerStreamMode',
    'game_id': game_id
  };

  server.state = 'unknown state';
  table.handler(server, game_id, packet);
  equals(server.getState(), 'running', 'state running');
});

test("jpoker.table.handler: unknown table", function () {
  expect(1);
  var server = jpoker.serverCreate({
    url: 'url'
  });

  var game_id = 100;
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var packet = {
    'type': 'Packet',
    'game_id': 101
  };

  jpokerMessage = jpoker.message;
  jpoker.message = function (message) {
    equals(message.indexOf("unknown table") >= 0, true, "unknown table");
    jpoker.message = jpokerMessage;
  };
  var verbose = jpoker.verbose;
  jpoker.verbose = 0;
  table.handler(server, game_id, packet);
  jpoker.verbose = verbose;
});

test("jpoker.table: max_player", function () {
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var table = new jpoker.table(server, {
    id: 42
  });
  equals(table.max_players, 10, 'max_players default');
  table = new jpoker.table(server, {
    id: 42,
    seats: 5
  });
  equals(table.max_players, 5, 'max_players frmo packet');
  cleanup();
});

test("jpoker.table.handler: PacketPokerShowdown", function () {
  expect(2);
  var server = jpoker.serverCreate({
    url: 'url'
  });

  var user_serial = 20;
  var game_id = 100;
  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  equals(table.delay.showdown, jpoker.table.defaults.delay.showdown);

  var packet = {
    'type': 'PacketPokerShowdown',
    'game_id': game_id
  };
  var jpokerNow = jpoker.now;
  jpoker.now = function () {
    return 42;
  };
  table.handler(server, game_id, packet);
  equals(server.delays[game_id], 42 + jpoker.table.defaults.delay.showdown, 'showdown delay');
  jpoker.now = jpokerNow;
  cleanup();
});

//
// player
//
test("jpoker.player.init", function () {
  expect(7);
  var player = new jpoker.player({
    url: url
  });
  equals(false, player.all_in);
  equals(true, player.broke);
  equals(0, player.bet);
  equals(0, player.money);
  equals(undefined, player.side_pot);
  equals(undefined, player.stats);
  equals(false, player.cards.dealt);
});

test("jpoker.player.handler PacketPokerPlayerChips", function () {
  expect(9);
  var player = new jpoker.player({
    url: url
  });
  equals(false, player.all_in, 'initial all_in');
  equals(true, player.broke, 'initial broke');
  player.handler(undefined, 0, {
    type: 'PacketPokerPlayerChips',
    money: 1,
    bet: 0
  });
  equals(false, player.all_in, 'buyin all_in');
  equals(false, player.broke, 'buyin broke');
  player.handler(undefined, 0, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 1
  });
  equals(true, player.all_in, 'go allin all_in');
  equals(false, player.broke, 'go allin broke');
  player.handler(undefined, 0, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 0
  });
  equals(true, player.all_in, 'no money/bet all_in'); // reset on PokerStart only
  equals(false, player.broke, 'no money/bet broke'); // all in + no money or bet means the money is in the pot
  player.all_in = false;
  player.handler(undefined, 0, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 0
  });
  equals(true, player.broke, 'go broke broke'); // when there is no money nor bet and the player is not all in, it means he is broke
});

test("jpoker.player.reinit", function () {
  expect(8);

  var serial = 42;
  var name = 'username';
  var url = 'url';
  var player = new jpoker.player({
    url: url
  }, {
    serial: serial,
    name: name
  });
  equals(player.url, url, 'player.url is set');
  equals(player.serial, serial, 'player.serial is set');
  equals(player.name, name, 'player.name is set');
  var money = 10;
  player.money = money;

  var callback = function (player, what, packet) {
      equals(player.serial, other_serial, 'player serial changed');
      equals(player.money, 0, 'money reset');
    };

  var other_serial = 74;
  player.registerReinit(callback);
  player.reinit({
    serial: other_serial
  });
  equals(player.serial, other_serial, 'player.serial is set');
  equals(player.name, name, 'player.name is set');
  equals(player.money, 0, 'player.money is reset');
});

test("jpoker.player.sidepot", function () {
  expect(6);

  var serial = 42;
  var name = 'username';
  var url = 'url';
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var game_id = 42;
  var player = new jpoker.player({
    url: url
  }, {
    serial: serial,
    name: name
  });
  player.handler(server, game_id, {
    'type': 'PacketPokerPlayerChips',
    'money': 0,
    'bet': 10000
  });
  var player2 = new jpoker.player({
    url: url
  }, {
    serial: serial + 1,
    name: name + '1'
  });
  player2.handler(server, game_id, {
    'type': 'PacketPokerPlayerChips',
    'money': 0,
    'bet': 10000
  });
  var player3 = new jpoker.player({
    url: url
  }, {
    serial: serial + 2,
    name: name + '2'
  });
  player3.handler(server, game_id, {
    'type': 'PacketPokerPlayerChips',
    'money': 100000,
    'bet': 10000
  });
  player.sit_out = false;
  player2.sit_out = false;
  player3.sit_out = false;

  var packet = {
    'type': 'PacketPokerPotChips',
    'index': 1,
    'bet': [1, 20000]
  };
  player.handler(server, game_id, packet);
  equals(player.side_pot.bet, 200, 'player side pot set');
  player2.handler(server, game_id, packet);
  equals(player2.side_pot.bet, 200, 'player2 side pot set');
  player3.handler(server, game_id, packet);
  equals(player3.side_pot, undefined, 'player3 side pot not set');

  player.handler(server, game_id, {
    'type': 'PacketPokerPotChips',
    'index': 2,
    'bet': [1, 40000]
  });
  equals(player.side_pot.bet, 200, 'player side pot not updated');

  player.handler(server, game_id, {
    'type': 'PacketPokerChipsPotReset'
  });
  equals(player.side_pot, undefined, 'side pot reset');

  player.sit_out = true;
  player.handler(server, game_id, {
    'type': 'PacketPokerPotChips',
    'index': 2,
    'bet': [1, 40000]
  });
  equals(player.side_pot, undefined, 'side pot reset');
});

test("jpoker.player.stats", function () {
  expect(4);
  var serial = 42;
  var name = 'username';
  var url = 'url';
  var server = jpoker.serverCreate({
    url: url
  });
  var game_id = 100;
  var packet = {
    "type": "PacketPokerTable",
    "id": 100
  };
  server.tables[packet.id] = new jpoker.table(server, packet);
  var player = new jpoker.player({
    url: url
  }, {
    serial: serial,
    name: name
  });
  equals(undefined, player.stats);
  server.tables[packet.id].serial2player[serial] = player;
  server.handler(server, 0, {
    type: 'PacketPokerPlayerStats',
    serial: serial,
    rank: 1,
    percentile: 99
  });
  equals(99, player.stats.percentile);
  equals(1, player.stats.rank);
  player.reset();
  equals(undefined, player.stats);
});

test("jpoker.player.cards", function () {
  expect(8);
  var serial = 42;
  var name = 'username';
  var url = 'url';
  var server = jpoker.serverCreate({
    url: url
  });
  var game_id = 100;
  var packet = {
    "type": "PacketPokerTable",
    "id": 100
  };
  server.tables[packet.id] = new jpoker.table(server, packet);
  var player = new jpoker.player({
    url: url
  }, {
    serial: serial,
    name: name
  });
  server.tables[packet.id].serial2player[serial] = player;
  server.tables[packet.id].handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: serial,
    game_id: game_id,
    cards: [1, 2]
  });
  equals(player.cards[0], 1, 'card 1');
  equals(player.cards[1], 2, 'card 2');
  equals(player.cards.dealt, true);
  server.tables[packet.id].handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: serial,
    game_id: game_id,
    cards: [1, 2]
  });
  equals(player.cards.dealt, false);
  server.tables[packet.id].handler(server, game_id, {
    type: 'PacketPokerStart',
    game_id: game_id
  });
  equals(player.cards[0], null, 'card 1 null');
  equals(player.cards[1], null, 'card 2 null');
  server.tables[packet.id].handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: serial,
    game_id: game_id,
    cards: [255, 255]
  });
  equals(player.cards.dealt, true);
  server.tables[packet.id].handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: serial,
    game_id: game_id,
    cards: [1, 2]
  });
  equals(player.cards.dealt, false);
});

//
// tableList
//
test("jpoker.plugins.tableList", function () {
  var expected = 11;
  var test_average_pot = jpoker.plugins.tableList.templates.rows.indexOf('{average_pot}');
  if (test_average_pot) {
    expected++;
  }
  expect(expected);
  stop();

  //
  // Mockup server that will always return TABLE_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var average_pot = 1535 / 100;
  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": [{
      "observers": 1,
      "name": "One",
      "percent_flop": 98,
      "average_pot": average_pot * 100,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 220,
      "betting_structure": "2-4-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 4,
      "waiting": 0,
      "skin": "default",
      "id": 100,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Two",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 101,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Three",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-pot-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 102,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }]
  };

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TABLE_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  equals('update' in server.callbacks, false, 'no update registered');
  var display_done = jpoker.plugins.tableList.callback.display_done;
  jpoker.plugins.tableList.callback.display_done = function (element) {
    jpoker.plugins.tableList.callback.display_done = display_done;
    equals($(".jpoker_table_list", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('tableList', 'url', {
    delay: 30
  });
  equals(server.callbacks.update.length, 1, 'tableList update registered');
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var tr = $("#" + id + " tr", place);
      equals(tr.length, 4);
      if (test_average_pot) {
        ok($(tr[1]).text().indexOf(average_pot) >= 0, 'average pot');
      }
      var row_id = TABLE_LIST_PACKET.packets[1].id + id;
      var row = $("#" + row_id, place);
      server.tableJoin = function (id) {
        equals(id, TABLE_LIST_PACKET.packets[1].id, 'tableJoin called');
      };
      row.click();
      row.trigger('mouseenter');
      equals(row.hasClass('hover'), true, 'hasClass hover');
      row.trigger('mouseleave');
      equals(row.hasClass('hover'), false, '!hasClass hover');
      $("#" + id).remove();
      return true;
    } else {
      equals(server.callbacks.update.length, 2, 'tableList and test update registered');
      equals('tableList' in server.timers, false, 'timer active');
      server.setTimeout = function (fun, delay) {};
      window.setTimeout(function () {
        start_and_cleanup();
      }, 30);
      return false;
    }
  });
  server.registerDestroy(function (server) {
    equals('tableList' in server.timers, false, 'timer killed');
    equals(server.callbacks.update.length, 0, 'update & destroy unregistered');
  });
});


test("jpoker.plugins.tableList link pattern", function () {
  expect(1);
  stop();

  //
  // Mockup server that will always return TABLE_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var average_pot = 1535 / 100;
  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": [{
      "observers": 1,
      "name": "One",
      "percent_flop": 98,
      "average_pot": average_pot * 100,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 220,
      "betting_structure": "2-4-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 4,
      "waiting": 0,
      "skin": "default",
      "id": 100,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Two",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 101,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Three",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-pot-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 102,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }]
  };

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TABLE_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  var link_pattern = 'http://foo.com/table?game_id={game_id}';
  place.jpoker('tableList', 'url', {
    delay: 30,
    link_pattern: link_pattern
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var game_id = TABLE_LIST_PACKET.packets[1].id;
      var row_id = game_id + id;
      var row = $("#" + row_id, element);
      server.tableJoin = function (id) {
        ok(false, 'tableJoin');
      };
      row.click();
      var link = link_pattern.supplant({
        game_id: TABLE_LIST_PACKET.packets[1].id
      });
      ok($('td:nth-child(1)', row).html().indexOf(link) >= 0, link);
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tableList pager", function () {
  expect(6);
  stop();

  //
  // Mockup server that will always return TABLE_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var average_pot = 1535 / 100;
  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": []
  };
  for (var i = 0; i < 200; ++i) {
    var name = "Table" + i;
    var game_id = 100 + i;
    var players = i % 11;
    var packet = {
      "observers": 0,
      "name": name,
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": players,
      "waiting": 0,
      "skin": "default",
      "id": game_id,
      "type": "PacketPokerTable",
      "player_timeout": 60
    };
    TABLE_LIST_PACKET.packets.push(packet);
  }

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TABLE_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  place.jpoker('tableList', 'url', {
    delay: 30
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($('.pager', element).length, 1, 'has pager');
      equals($('.pager .current', element).length, 1, 'has current page');
      ok($('.pager li:last a', element).text().indexOf('>>>') >= 0, 'has next page');
      $('.pager li:last a', element).click();
      ok($('.pager li:first a', element).text().indexOf('<<<') >= 0, 'has previous page');
      var row_id = TABLE_LIST_PACKET.packets[11].id + id;
      var row = $("#" + row_id, place);
      equals(row.length, 1, 'row element');
      server.tableJoin = function (id) {
        equals(id, TABLE_LIST_PACKET.packets[11].id, 'tableJoin called');
      };
      row.click();
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tableList pager 30 rows per page", function () {
  expect(2);
  stop();

  //
  // Mockup server that will always return TABLE_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var average_pot = 1535 / 100;
  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": []
  };
  for (var i = 0; i < 200; ++i) {
    var name = "Table" + i;
    var game_id = 100 + i;
    var players = i % 11;
    var packet = {
      "observers": 0,
      "name": name,
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": players,
      "waiting": 0,
      "skin": "default",
      "id": game_id,
      "type": "PacketPokerTable",
      "player_timeout": 60
    };
    TABLE_LIST_PACKET.packets.push(packet);
  }

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TABLE_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");

  jpoker.plugins.tableList.templates.pager = '<div class=\'pager\'><input class=\'pagesize\' value=\'30\'></input><ul class=\'pagelinks\'></ul></div>';
  place.jpoker('tableList', 'url', {
    delay: 10000
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($('.pager .pagesize', element).val(), 30, 'pagesize');
      equals($('table tbody tr', element).length, 30, 'tr count');
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tableList no table no tablesorter", function () {
  expect(1);
  stop();

  //
  // Mockup server that will always return TABLE_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var average_pot = 1535 / 100;
  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": []
  };

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TABLE_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  place.jpoker('tableList', 'url', {
    delay: 30
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($('.header', element).length, 0, 'no tablesorter');
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tableList getHTML should not list tourney table", function () {
  expect(2);

  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": []
  };
  TABLE_LIST_PACKET.packets.push({
    "observers": 0,
    "name": "Cayrryns",
    "percent_flop": 0,
    "average_pot": 0,
    "skin": "default",
    "variant": "holdem",
    "hands_per_hour": 0,
    "betting_structure": "100-200-no-limit",
    "currency_serial": 1,
    "muck_timeout": 5,
    "players": 0,
    "waiting": 0,
    "tourney_serial": 0,
    "seats": 10,
    "player_timeout": 60,
    "type": "PacketPokerTable",
    "id": 40
  });
  TABLE_LIST_PACKET.packets.push({
    "observers": 0,
    "name": "sitngo21",
    "percent_flop": 0,
    "average_pot": 0,
    "skin": "default",
    "variant": "holdem",
    "hands_per_hour": 0,
    "betting_structure": "level-15-30-no-limit",
    "currency_serial": 0,
    "muck_timeout": 5,
    "players": 2,
    "waiting": 0,
    "tourney_serial": 2,
    "seats": 2,
    "player_timeout": 60,
    "type": "PacketPokerTable",
    "id": 41
  });

  var id = jpoker.uid();
  var element = $('<div class=\'jpoker_table_list\' id=\'' + id + '\'></div>').appendTo("#main");
  element.html(jpoker.plugins.tableList.getHTML(id, TABLE_LIST_PACKET));
  equals($("table tbody tr", element).length, 1, 'one table');
  equals($("table tbody tr td").html(), "Cayrryns");
  cleanup(id);
});

test("jpoker.plugins.tableList getHTML add class for full and empty table", function () {
  expect(6);

  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": []
  };
  TABLE_LIST_PACKET.packets.push({
    "observers": 0,
    "name": "Cayrryns1",
    "percent_flop": 0,
    "average_pot": 0,
    "skin": "default",
    "variant": "holdem",
    "hands_per_hour": 0,
    "betting_structure": "100-200-no-limit",
    "currency_serial": 1,
    "muck_timeout": 5,
    "players": 0,
    "waiting": 0,
    "tourney_serial": 0,
    "seats": 10,
    "player_timeout": 60,
    "type": "PacketPokerTable",
    "id": 40
  });
  TABLE_LIST_PACKET.packets.push({
    "observers": 0,
    "name": "Cayrryns2",
    "percent_flop": 0,
    "average_pot": 0,
    "skin": "default",
    "variant": "holdem",
    "hands_per_hour": 0,
    "betting_structure": "100-200-no-limit",
    "currency_serial": 1,
    "muck_timeout": 5,
    "players": 10,
    "waiting": 0,
    "tourney_serial": 0,
    "seats": 10,
    "player_timeout": 60,
    "type": "PacketPokerTable",
    "id": 41
  });
  TABLE_LIST_PACKET.packets.push({
    "observers": 0,
    "name": "Cayrryns3",
    "percent_flop": 0,
    "average_pot": 0,
    "skin": "default",
    "variant": "holdem",
    "hands_per_hour": 0,
    "betting_structure": "100-200-no-limit",
    "currency_serial": 1,
    "muck_timeout": 5,
    "players": 5,
    "waiting": 0,
    "tourney_serial": 0,
    "seats": 10,
    "player_timeout": 60,
    "type": "PacketPokerTable",
    "id": 42
  });

  var id = jpoker.uid();
  var element = $('<div class=\'jpoker_table_list\' id=\'' + id + '\'></div>').appendTo("#main");
  element.html(jpoker.plugins.tableList.getHTML(id, TABLE_LIST_PACKET));
  equals($("table tbody tr", element).length, 3, '3 tables');
  equals($("table tbody tr").eq(0).hasClass('jpoker_table_list_table_empty'), true);
  equals($("table tbody tr").eq(0).hasClass('jpoker_table_list_table_full'), false);
  equals($("table tbody tr").eq(1).hasClass('jpoker_table_list_table_empty'), false);
  equals($("table tbody tr").eq(1).hasClass('jpoker_table_list_table_full'), true);
  equals($("table tbody tr").eq(2).attr('class'), '');
  cleanup(id);
});

//
// tourneyList
//
test("jpoker.plugins.tourneyList", function () {
  expect(18);
  stop();

  //
  // Mockup server that will always return TOURNEY_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var TOURNEY_LIST_PACKET = {
    "players": 0,
    "packets": [{
      "players_quota": 2,
      "breaks_first": 7200,
      "name": "sitngo2",
      "description_short": "Sit and Go 2 players, Holdem",
      "start_time": 0,
      "breaks_interval": 3600,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "registering",
      "buy_in": 300000,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 1111,
      "sit_n_go": "y",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "registering",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 39,
      "sit_n_go": "n",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "announced",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 40,
      "sit_n_go": "n",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "canceled",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 41,
      "sit_n_go": "n",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "canceled",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 42,
      "sit_n_go": "n",
      "registered": 0
    }],
    "tourneys": 5,
    "type": "PacketPokerTourneyList"
  };
  var start_time = new Date(TOURNEY_LIST_PACKET.packets[1].start_time * 1000).toLocaleString();
  var state = TOURNEY_LIST_PACKET.packets[1].state;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

    handle: function (packet) {
      if (packet.indexOf('PacketPokerTourneySelect') >= 0) {
        equals(packet.indexOf('"string":""') > 0, true, JSON.stringify(packet));
      }
    }
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var row_id = TOURNEY_LIST_PACKET.packets[1].serial + id;
  var place = $("#main");
  equals('update' in server.callbacks, false, 'no update registered');
  var display_done = jpoker.plugins.tourneyList.defaults.callback.display_done;
  jpoker.plugins.tourneyList.defaults.callback.display_done = function (element) {
    jpoker.plugins.tourneyList.defaults.callback.display_done = display_done;
    equals($(".jpoker_tourney_list", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('tourneyList', 'url', {
    delay: 30
  });
  equals(server.callbacks.update.length, 1, 'tourneyList update registered');
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var tr = $("#" + id + " tr", place);
      var row = $("#" + row_id, place);
      equals(tr.length, 5 + 1);
      equals($('td:nth-child(5)', row).text(), start_time, 'start_time');
      equals($('td:nth-child(6)', row).text(), state, 'state');
      equals($('.headerSortDown', tr[0]).text(), 'Description', "headerSortDown");
      server.tourneyRowClick = function (server, subpacket) {
        equals(subpacket.serial, TOURNEY_LIST_PACKET.packets[1].serial, 'tourneyRowClick called');
      };
      ok(tr.eq(1).hasClass('jpoker_tourney_state_registering'), 'registering css class');
      tr.eq(1).click();
      server.tourneyRowClick = function (server, subpacket) {
        ok(false, 'should not be called for announced|canceled tourney');
      };
      ok(tr.eq(2).hasClass('jpoker_tourney_state_announced'), 'announced css class');
      tr.eq(2).click();
      ok(tr.eq(3).hasClass('jpoker_tourney_state_canceled'), 'canceled css class');
      tr.eq(3).click();
      row.trigger('mouseenter');
      equals(row.hasClass('hover'), true, 'hasClass hover');
      row.trigger('mouseleave');
      equals(row.hasClass('hover'), false, '!hasClass hover');
      $("#" + id).remove();
      return true;
    } else {
      equals(server.callbacks.update.length, 2, 'tourneyList and test update registered');
      equals('tourneyList' in server.timers, false, 'timer active');
      server.setTimeout = function (fun, delay) {};
      window.setTimeout(function () {
        start_and_cleanup();
      }, 30);
      return false;
    }
  });
  server.registerDestroy(function (server) {
    equals('tourneyList' in server.timers, false, 'timer killed');
    equals(server.callbacks.update.length, 0, 'update & destroy unregistered');
  });
});

test("jpoker.plugins.tourneyList date template", function () {
  expect(1);
  stop();

  //
  // Mockup server that will always return TOURNEY_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var TOURNEY_LIST_PACKET = {
    "players": 0,
    "packets": [{
      "players_quota": 2,
      "breaks_first": 7200,
      "name": "sitngo2",
      "description_short": "Sit and Go 2 players, Holdem",
      "start_time": 0,
      "breaks_interval": 3600,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "registering",
      "buy_in": 300000,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 1111,
      "sit_n_go": "y",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "registering",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 39,
      "sit_n_go": "n",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "announced",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 40,
      "sit_n_go": "n",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "canceled",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 41,
      "sit_n_go": "n",
      "registered": 0
    }, {
      "players_quota": 1000,
      "breaks_first": 7200,
      "name": "regular1",
      "description_short": "Holdem No Limit Freeroll",
      "start_time": 1216201024,
      "breaks_interval": 60,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "canceled",
      "buy_in": 0,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": 42,
      "sit_n_go": "n",
      "registered": 0
    }],
    "tourneys": 5,
    "type": "PacketPokerTourneyList"
  };
  var date_format = "%Y/%m/%d %H:%M:%S";
  var start_time = $.strftime(date_format, new Date(TOURNEY_LIST_PACKET.packets[1].start_time * 1000));
  var state = TOURNEY_LIST_PACKET.packets[1].state;
  jpoker.plugins.tourneyList.defaults.templates.date = date_format;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var row_id = TOURNEY_LIST_PACKET.packets[1].serial + id;
  var place = $("#main");
  place.jpoker('tourneyList', 'url', {
    delay: 30
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var tr = $("#" + id + " tr", place);
      var row = $("#" + row_id, place);
      equals($('td:nth-child(5)', row).text(), start_time, 'start_time');
      $("#" + id).remove();
      return true;
    } else {
      server.setTimeout = function (fun, delay) {};
      window.setTimeout(function () {
        jpoker.plugins.tourneyList.defaults.templates.date = '';
        start_and_cleanup();
      }, 30);
      return false;
    }
  });
});

test("jpoker.plugins.tourneyList link pattern", function () {
  expect(1);
  stop();

  //
  // Mockup server that will always return TOURNEY_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var TOURNEY_LIST_PACKET = {
    "players": 0,
    "packets": [{
      "players_quota": 2,
      "breaks_first": 7200,
      "name": "sitngo2",
      "description_short": "Sit and Go 2 players, Holdem",
      "start_time": 0,
      "breaks_interval": 3600,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "registering",
      "buy_in": 300000,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "schedule_serial": 121,
      "serial": 1,
      "sit_n_go": "y",
      "registered": 0
    }],
    "tourneys": 1,
    "type": "PacketPokerTourneyList"
  };

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var row_id = TOURNEY_LIST_PACKET.packets[0].serial + id;
  var place = $("#main");
  var link_pattern = 'http://foo.com/tourney?tourney_serial={tourney_serial}+schedule_serial={schedule_serial}';
  place.jpoker('tourneyList', 'url', {
    delay: 30,
    link_pattern: link_pattern
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var row = $("#" + row_id, place);
      server.tourneyRowClick = function (server, subpacket) {
        ok(false, 'tourneyRowClick disabled');
      };
      row.click();
      var link = link_pattern.supplant({
        tourney_serial: TOURNEY_LIST_PACKET.packets[0].serial,
        schedule_serial: TOURNEY_LIST_PACKET.packets[0].schedule_serial
      });
      ok($('td:nth-child(1)', row).html().indexOf(link) >= 0, link);
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyList pager", function () {
  expect(6);
  stop();

  //
  // Mockup server that will always return TOURNEY_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var TOURNEY_LIST_PACKET = {
    "players": 0,
    "packets": [],
    "tourneys": 5,
    "type": "PacketPokerTourneyList"
  };
  for (var i = 0; i < 30; ++i) {
    var name = "Tourney" + i;
    var players = i % 11;
    var serial = i + 100;
    var packet = {
      "players_quota": players,
      "breaks_first": 7200,
      "name": name,
      "description_short": name,
      "start_time": 0,
      "breaks_interval": 3600,
      "variant": "holdem",
      "currency_serial": 1,
      "state": "registering",
      "buy_in": 300000,
      "type": "PacketPokerTourney",
      "breaks_duration": 300,
      "serial": serial,
      "sit_n_go": "y",
      "registered": 0
    };
    TOURNEY_LIST_PACKET.packets.push(packet);
  }

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  place.jpoker('tourneyList', 'url', {
    delay: 30
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($('.pager', element).length, 1, 'has pager');
      equals($('.pager .current', element).length, 1, 'has current page');
      ok($('.pager li:last', element).text().indexOf(">>>") >= 0, 'has next page');
      $('.pager li:last a', element).click();
      ok($('.pager li:first', element).text().indexOf("<<<") >= 0, 'has previous page');
      var row = $('table tr', place).eq(1);
      equals(row.length, 1, 'row element');
      server.tourneyRowClick = function (server, subpacket) {
        ok(true, 'tourneyRowClick called');
      };
      row.click();
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyList empty", function () {
  expect(2);
  stop();

  //
  // Mockup server that will always return TOURNEY_LIST_PACKET,
  // whatever is sent to it.
  //
  var PokerServer = function () {};

  var TOURNEY_LIST_PACKET = {
    "players": 0,
    "packets": [],
    "tourneys": 5,
    "type": "PacketPokerTourneyList"
  };

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  var templates = $.extend({}, jpoker.plugins.tourneyList.defaults.templates, {
    header: '<table><thead><tr><th>{description_short}</th></tr><tr><th>{registered}</th></tr></thead><tbody>'
  });
  place.jpoker('tourneyList', 'url', {
    delay: 30,
    templates: templates
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var tr = $("#" + id + " tr", place);
      equals(tr.length, 2);
      equals($(".header", element).length, 0, 'no tablesorter');
      $("#" + id).remove();
      return true;
    } else {
      window.setTimeout(function () {
        start_and_cleanup();
      }, 30);
      return false;
    }
  });
});

//
// sitngoTourneyList
//
test("jpoker.plugins.sitngoTourneyList", function () {
  expect(4);
  jpoker.plugins.sitngoTourneyList.callback.marker_for_test = true;
  var tourneyList = jpoker.plugins.tourneyList;
  jpoker.plugins.tourneyList = function (url, options) {
    equals(options.templates.header, jpoker.plugins.sitngoTourneyList.templates.header, 'header');
    ok('marker_for_test' in options.callback, 'callback');
    equals(options.css_tag, jpoker.plugins.sitngoTourneyList.defaults.css_tag, 'header');
    equals(options.string.split('\t')[1], 'sit_n_go', 'string');
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  $("#main").jpoker('sitngoTourneyList', 'url');
  jpoker.plugins.tourneyList = tourneyList;
  cleanup();
});

//
// regularTourneyList
//
test("jpoker.plugins.regularTourneyList", function () {
  expect(4);
  jpoker.plugins.regularTourneyList.callback.marker_for_test = true;
  var tourneyList = jpoker.plugins.tourneyList;
  jpoker.plugins.tourneyList = function (url, options) {
    equals(options.templates.header, jpoker.plugins.regularTourneyList.templates.header, 'header');
    ok('marker_for_test' in options.callback, 'callback');
    equals(options.css_tag, jpoker.plugins.regularTourneyList.defaults.css_tag, 'header');
    equals(options.string.split('\t')[1], 'regular', 'string');
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  $("#main").jpoker('regularTourneyList', 'url');
  jpoker.plugins.tourneyList = tourneyList;
  cleanup();
});

//
// tourneyDetails
//
test("jpoker.plugins.tourneyDetails", function () {
  expect(9);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 140,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  equals('update' in server.callbacks, false, 'no update registered');
  var display_done = jpoker.plugins.tourneyDetails.callback.display_done;
  jpoker.plugins.tourneyDetails.callback.display_done = function (element) {
    jpoker.plugins.tourneyDetails.callback.display_done = display_done;
    equals($(".jpoker_tourney_details_info", element).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  equals(server.callbacks.update.length, 1, 'tourneyDetails update registered');
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var tr = $("#" + id + " .jpoker_tourney_details_players tr", place);
      // +2 because 1 caption, 2 title
      equals(tr.length, players_count + 2, 'tourneyDetails players_count');
      var input = $("#" + id + " .jpoker_tourney_details_register input");
      equals(input.length, 0, 'no tourneyDetails register button');
      $("#" + id).remove();
      return true;
    } else {
      equals(server.callbacks.update.length, 2, 'tourneyDetails and test update registered');
      equals('tourneyDetails' in server.timers, false, 'timer active');
      server.setTimeout = function (fun, delay) {};
      window.setTimeout(function () {
        start_and_cleanup();
      }, 30);
      return false;
    }
  });
  server.registerDestroy(function (server) {
    equals('tourneyDetails' in server.timers, false, 'timer killed');
    equals(server.callbacks.update.length, 0, 'update & destroy unregistered');
  });
});

test("jpoker.plugins.tourneyDetails refresh should be < 10s", function () {
  expect(1);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 140,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  var options = {
    setInterval: function (fn, interval) {
      ok(interval <= 10000, 'interval <= 10000');
      setTimeout(function () {
        $('#' + id).remove();
        server.notifyUpdate({});
        start_and_cleanup();
      }, 0);
    }
  };
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString(), '', options);
});

test("jpoker.plugins.tourneyDetails pager", function () {
  expect(1);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {},
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };
  for (var i = 0; i < 200; ++i) {
    var player_money = 140 + i;
    var player_name = "user" + i;
    var player_serial = 'X' + i;
    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {
      "money": player_money,
      "table_serial": 606,
      "name": player_name,
      "rank": -1
    };
  }

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($('.pager', element).length, 0, 'has pager');
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyDetails no player no tablesorter", function () {
  expect(1);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {},
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {},
    "type": 149,
    "tourney": {
      "registered": 0,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($('.header', element).length, 0, 'no tablesorter');
      $("#" + id).remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyDetails templates no ranks no moneys", function () {
  expect(9);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": -1,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var is_logged = true;
  var is_registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, is_logged, is_registered));

  var name = $(" .jpoker_tourney_name", element);
  equals(name.html(), "Sit and Go 2 players, Holdem");

  var info = $(" .jpoker_tourney_details_info", element);
  var description = $(".jpoker_tourney_details_info_description", info);
  equals(description.html(), "Sit and Go 2 players");

  var registered = $(".jpoker_tourney_details_info_registered", info);
  equals(registered.html(), "1 players registered.");

  var seats_available = $(".jpoker_tourney_details_info_players_quota", info);
  equals(seats_available.html(), "2 players max.");

  var buy_in = $(".jpoker_tourney_details_info_buy_in", info);
  equals(buy_in.html(), "Buy in: 3000");

  var tr = $(".jpoker_tourney_details_players tr", element);
  // +2 because 1 caption, 2 title
  equals(tr.length, 3, 'tourneyDetails players_count');

  var player = tr.eq(2);
  var player_name = $("td", player).eq(0);
  equals(player_name.html(), "user1");

  var money = $("td", player).eq(1);
  equals(money.html(), "");

  var rank = $("td", player).eq(2);
  equals(rank.html(), "");
  cleanup();
});

test("jpoker.plugins.tourneyDetails templates sitngo registering", function () {
  expect(1);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": -1,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var is_logged = true;
  var is_registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, is_logged, is_registered));

  var info = $(" .jpoker_tourney_details_info", element);

  var start_time = $(".jpoker_tourney_details_info_start_time", info);
  equals(start_time.length, 0, 'no start_time');

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates regular registering", function () {
  expect(1);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": -1,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Regular",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Regular",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 1216201024,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "n",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var is_logged = true;
  var is_registered = true;
  var date = new Date(packet.tourney.start_time * 1000).toLocaleString();
  $(element).html(tourneyDetails.getHTML(id, packet, is_logged, is_registered));

  var info = $(" .jpoker_tourney_details_info", element);

  var start_time = $(".jpoker_tourney_details_info_start_time", info);
  equals(start_time.html(), "Start time: " + date);

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates regular registering date template", function () {
  expect(1);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": -1,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Regular",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Regular",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 1216201024,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "n",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var is_logged = true;
  var is_registered = true;
  var date_format = '%Y/%m/%d %H:%M:%S';
  var date = $.strftime(date_format, new Date(packet.tourney.start_time * 1000));
  tourneyDetails.templates.date = date_format;
  $(element).html(tourneyDetails.getHTML(id, packet, is_logged, is_registered));

  var info = $(" .jpoker_tourney_details_info", element);

  var start_time = $(".jpoker_tourney_details_info_start_time", info);
  equals(start_time.html(), "Start time: " + date);
  tourneyDetails.templates.date = '';

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates money and no ranks", function () {
  expect(4);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 100000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 2,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };
  $.each(TOURNEY_MANAGER_PACKET.user2properties, function (serial, player) {
    player.money /= 100;
  });

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  var moneys = $(".jpoker_tourney_details_players tr td:nth-child(2)", element);
  equals(moneys.eq(0).html(), "1000");
  equals(moneys.eq(1).html(), "1000");

  var ranks = $(".jpoker_tourney_details_players tr td:nth-child(3)", element);
  equals(ranks.eq(0).html(), "");
  equals(ranks.eq(1).html(), "");
  cleanup();
});

test("jpoker.plugins.tourneyDetails templates ranks and no money", function () {
  expect(4);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": -1,
        "table_serial": 606,
        "name": "user1",
        "rank": 1
      },
      "X5": {
        "money": -1,
        "table_serial": 606,
        "name": "user2",
        "rank": 2
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 2,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  var moneys = $(".jpoker_tourney_details_players tr td:nth-child(2)", element);
  equals(moneys.eq(0).html(), "");
  equals(moneys.eq(1).html(), "");

  var ranks = $(".jpoker_tourney_details_players tr td:nth-child(3)", element);
  equals(ranks.eq(0).html(), "1");
  equals(ranks.eq(1).html(), "2");
  cleanup();
});

test("jpoker.plugins.tourneyDetails templates players", function () {
  expect(4);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": -1,
        "table_serial": 606,
        "name": "user1",
        "rank": 1
      },
      "X5": {
        "money": -1,
        "table_serial": 606,
        "name": "user2",
        "rank": 2
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 2,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;

  packet.tourney.state = "registering";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_players tr:nth-child(2) td", element).length, 1, "player when registering");

  packet.tourney.state = "running";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_players tr:nth-child(2) th", element).length, 3, "player, money, ranks when running");

  packet.tourney.state = "complete";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_players tr:nth-child(2) th", element).length, 2, "player, ranks when complete");
  equals($(".jpoker_tourney_details_players tr:nth-child(2) th:nth-child(2)", element).html(), "Rank", "ranks shown");

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates tables", function () {
  expect(25);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user3",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };
  $.each(TOURNEY_MANAGER_PACKET.user2properties, function (serial, player) {
    player.money /= 100;
  });

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  equals($('.jpoker_tourney_details_info', element).hasClass('jpoker_tourney_details_running'), true, 'details_running');

  var headers = $(".jpoker_tourney_details_tables tr th", element);
  equals(headers.eq(0).html(), "Tables");
  equals(headers.eq(1).html(), "Table");
  equals(headers.eq(2).html(), "Players");
  equals(headers.eq(3).html(), "Max money");
  equals(headers.eq(4).html(), "Min money");
  equals(headers.eq(5).html(), "Go to table");

  var table1 = $(".jpoker_tourney_details_tables tr", element).eq(2);
  equals(table1.attr("id"), "X606");
  equals(table1.hasClass('even'), true);
  ok(table1.hasClass("jpoker_tourney_details_table"), "jpoker_tourney_details_table class");
  equals(table1.children().eq(0).html(), "606");
  equals(table1.children().eq(1).html(), "2");
  equals(table1.children().eq(2).html(), "2000");
  equals(table1.children().eq(3).html(), "1000");
  equals(table1.children().eq(4).find("input").attr("value"), "Go to table");

  var table2 = $(".jpoker_tourney_details_tables tr", element).eq(3);
  equals(table2.attr("id"), "X607");
  equals(table2.hasClass('odd'), true);
  ok(table2.hasClass("jpoker_tourney_details_table"), "jpoker_tourney_details_table class");
  equals(table2.children().eq(0).html(), "607");
  equals(table2.children().eq(1).html(), "3");
  equals(table2.children().eq(2).html(), "5000");
  equals(table2.children().eq(3).html(), "3000");
  equals(table2.children().eq(4).find("input").attr("value"), "Go to table");


  var link_pattern = "http://foo.com/tourneytable?game_id={game_id}+tourney_serial={serial}";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered, link_pattern));

  var table1_link = $(".jpoker_tourney_details_tables tr", element).eq(2);
  var link1 = link_pattern.supplant({
    game_id: 606,
    serial: 1
  });
  var link1_actual = table1_link.children().eq(4).html();
  ok(link1_actual.indexOf(link1) >= 0, "look for " + link1 + " in " + link1_actual);

  var table2_link = $(".jpoker_tourney_details_tables tr", element).eq(3);
  var link2 = link_pattern.supplant({
    game_id: 607,
    serial: 1
  });
  var link2_actual = table2_link.children().eq(4).html();
  ok(link2_actual.indexOf(link2) >= 0, "look for " + link2 + " in " + link2_actual);

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates tables registering", function () {
  expect(2);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": -1,
        "table_serial": -1,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {},
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  var tables = $(".jpoker_tourney_details_tables", element);
  equals(tables.length, 0);
  equals($('.jpoker_tourney_details_info', element).hasClass('jpoker_tourney_details_registering'), true, 'details_registering');
  cleanup();
});

test("jpoker.plugins.tourneyDetails templates tableDetails players", function () {
  expect(15);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user5",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };
  $.each(TOURNEY_MANAGER_PACKET.user2properties, function (serial, player) {
    player.money /= 100;
  });

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;

  $(element).html(tourneyDetails.getHTMLTableDetails(id, packet, "X606"));

  var headers = $(".jpoker_tourney_details_table_players tr th", element);
  equals(headers.eq(0).html(), "Table");
  equals(headers.eq(1).html(), "Player");
  equals(headers.eq(2).html(), "Money");

  var table1 = $(".jpoker_tourney_details_table_players tr td", element);
  equals(table1.eq(0).html(), "user1");
  equals(table1.eq(1).html(), "1000");
  equals(table1.eq(2).html(), "user2");
  equals(table1.eq(3).html(), "2000");

  $(element).html(tourneyDetails.getHTMLTableDetails(id, packet, "X606"));

  var table1b = $(".jpoker_tourney_details_table_players tr td", element);
  equals(table1b.eq(1).html(), "1000");
  equals(table1b.eq(3).html(), "2000");

  $(element).html(tourneyDetails.getHTMLTableDetails(id, packet, "X607"));

  var table2 = $(".jpoker_tourney_details_table_players tr td", element);
  equals(table2.eq(0).html(), "user3");
  equals(table2.eq(1).html(), "3000");
  equals(table2.eq(2).html(), "user4");
  equals(table2.eq(3).html(), "4000");
  equals(table2.eq(4).html(), "user5");
  equals(table2.eq(5).html(), "5000");

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates prizes", function () {
  expect(14);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user3",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0,
      "rank2prize": [1000000, 100000, 10000, 1000, 100]
    },
    "type": "PacketPokerTourneyManager"
  };
  $.each(TOURNEY_MANAGER_PACKET.user2properties, function (serial, player) {
    player.money /= 100;
  });
  $.each(TOURNEY_MANAGER_PACKET.tourney.rank2prize, function (i, prize) {
    TOURNEY_MANAGER_PACKET.tourney.rank2prize[i] /= 100;
  });

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  var headers = $(".jpoker_tourney_details_prizes tr th", element);
  equals(headers.eq(0).html(), "Prizes");
  equals(headers.eq(1).html(), "Rank");
  equals(headers.eq(2).html(), "Prize");

  equals($(".jpoker_tourney_details_prizes tbody tr:first").hasClass('even'), true, 'first row is even');

  var prizes = $(".jpoker_tourney_details_prizes tr td", element);
  equals(prizes.eq(0).html(), "1");
  equals(prizes.eq(1).html(), "10000");
  equals(prizes.eq(2).html(), "2");
  equals(prizes.eq(3).html(), "1000");
  equals(prizes.eq(4).html(), "3");
  equals(prizes.eq(5).html(), "100");
  equals(prizes.eq(6).html(), "4");
  equals(prizes.eq(7).html(), "10");
  equals(prizes.eq(8).html(), "5");
  equals(prizes.eq(9).html(), "1");

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates prizes complete", function () {
  expect(2);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6f": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user3",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "complete",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0,
      "rank2prize": [1000000, 100000, 10000, 1000, 100]
    },
    "type": "PacketPokerTourneyManager"
  };
  $.each(TOURNEY_MANAGER_PACKET.user2properties, function (serial, player) {
    player.money /= 100;
  });
  $.each(TOURNEY_MANAGER_PACKET.tourney.rank2prize, function (i, prize) {
    TOURNEY_MANAGER_PACKET.tourney.rank2prize[i] /= 100;
  });

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  equals($(".jpoker_tourney_details_prizes", element).length, 1);
  equals($('.jpoker_tourney_details_info', element).hasClass('jpoker_tourney_details_complete'), true, 'details_complete');

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates prizes sitngo registering", function () {
  expect(2);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6f": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user3",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0,
      "rank2prize": [1000000, 100000, 10000, 1000, 100]
    },
    "type": "PacketPokerTourneyManager"
  };
  $.each(TOURNEY_MANAGER_PACKET.user2properties, function (serial, player) {
    player.money /= 100;
  });
  $.each(TOURNEY_MANAGER_PACKET.tourney.rank2prize, function (i, prize) {
    TOURNEY_MANAGER_PACKET.tourney.rank2prize[i] /= 100;
  });

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  equals($(".jpoker_tourney_details_prizes", element).length, 1);
  equals($('.jpoker_tourney_details_info', element).hasClass('jpoker_tourney_details_registering'), true, 'details_registering');

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates prizes regular registering", function () {
  expect(2);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6f": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user3",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "n",
      "rebuy_delay": 0,
      "rank2prize": [1000000, 100000, 10000, 1000, 100]
    },
    "type": "PacketPokerTourneyManager"
  };
  $.each(TOURNEY_MANAGER_PACKET.user2properties, function (serial, player) {
    player.money /= 100;
  });
  $.each(TOURNEY_MANAGER_PACKET.tourney.rank2prize, function (i, prize) {
    TOURNEY_MANAGER_PACKET.tourney.rank2prize[i] /= 100;
  });

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));

  equals($(".jpoker_tourney_details_prizes", element).length, 1);
  equals($('.jpoker_tourney_details_info', element).hasClass('jpoker_tourney_details_registering'), true, 'details_registering');

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates register", function () {
  expect(2);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user3",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0,
      "rank2prize": [1000000, 100000, 10000, 1000, 100]
    },
    "type": "PacketPokerTourneyManager"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;

  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_register", element).length, 1);

  packet.tourney.state = "running";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_register", element).length, 0);

  cleanup();
});

test("jpoker.plugins.tourneyDetails templates buggy", function () {
  expect(1);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X26": {
        "money": 400000,
        "table_serial": 723,
        "name": "BOTBoSwoi",
        "rank": -1
      },
      "X27": {
        "money": -1,
        "table_serial": -1,
        "name": "BOTluhurs",
        "rank": 3
      },
      "X9": {
        "money": 400000,
        "table_serial": 723,
        "name": "proppy",
        "rank": -1
      },
      "X20": {
        "money": -1,
        "table_serial": -1,
        "name": "proppy2",
        "rank": 4
      }
    },
    "length": 3,
    "tourney_serial": 24,
    "table2serials": {
      "X723": [9, 26],
      "-1": [20, 27]
    },
    "type": "PacketPokerTourneyManager",
    "tourney": {
      "breaks_interval": 3600,
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "rank2prize": [840000, 360000],
      "serial": 24,
      "resthost_serial": 0,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "registered": 4,
      "players_quota": 4,
      "breaks_first": 7200,
      "add_on": 0,
      "start_time": 1222693571,
      "rake": 0,
      "variant": "holdem",
      "players_min": 4,
      "schedule_serial": 1,
      "betting_structure": "level-15-30-no-limit",
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "player_timeout": 60,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "uid__": "jpoker1222693551093"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = true;
  packet.tourney.state = "running";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals(1, $(".jpoker_tourney_details_tables tbody tr", element).length, 'one table');
  cleanup();
});

test("jpoker.plugins.tourneyDetails templates states announced break breakwait", function () {
  expect(12);

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X26": {
        "money": 400000,
        "table_serial": 723,
        "name": "BOTBoSwoi",
        "rank": -1
      },
      "X27": {
        "money": -1,
        "table_serial": -1,
        "name": "BOTluhurs",
        "rank": 3
      },
      "X9": {
        "money": 400000,
        "table_serial": 723,
        "name": "proppy",
        "rank": -1
      },
      "X20": {
        "money": -1,
        "table_serial": -1,
        "name": "proppy2",
        "rank": 4
      }
    },
    "length": 3,
    "tourney_serial": 24,
    "table2serials": {
      "X723": [9, 26],
      "-1": [20, 27]
    },
    "type": "PacketPokerTourneyManager",
    "tourney": {
      "breaks_interval": 3600,
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "rank2prize": [840000, 360000],
      "serial": 24,
      "resthost_serial": 0,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "registered": 4,
      "players_quota": 4,
      "breaks_first": 7200,
      "add_on": 0,
      "start_time": 1222693571,
      "rake": 0,
      "variant": "holdem",
      "players_min": 4,
      "schedule_serial": 1,
      "betting_structure": "level-15-30-no-limit",
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "player_timeout": 60,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "uid__": "jpoker1222693551093"
  };

  var id = jpoker.uid();
  $("#main").append('<div class=\'jpoker_tourney_details\' id=\'' + id + '\'></div>');
  var tourneyDetails = jpoker.plugins.tourneyDetails;
  var element = document.getElementById(id);
  var packet = TOURNEY_MANAGER_PACKET;
  var logged = true;
  var registered = false;
  packet.tourney.state = "announced";
  packet.tourney.sit_n_go = "n";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_tables", element).length, 0, 'tables');
  equals($(".jpoker_tourney_details_prizes", element).length, 0, 'prizes');
  equals($(".jpoker_tourney_details_players", element).length, 0, 'players');
  packet.tourney.state = "canceled";
  packet.tourney.sit_n_go = "n";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_tables", element).length, 0, 'tables');
  equals($(".jpoker_tourney_details_prizes", element).length, 0, 'prizes');
  equals($(".jpoker_tourney_details_players", element).length, 0, 'players');
  packet.tourney.state = "break";
  packet.tourney.sit_n_go = "n";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_tables", element).length, 1, 'tables');
  equals($(".jpoker_tourney_details_prizes", element).length, 1, 'prizes');
  equals($(".jpoker_tourney_details_players", element).length, 1, 'players');
  packet.tourney.state = "breakwait";
  packet.tourney.sit_n_go = "n";
  $(element).html(tourneyDetails.getHTML(id, packet, logged, registered));
  equals($(".jpoker_tourney_details_tables", element).length, 1, 'tables');
  equals($(".jpoker_tourney_details_prizes", element).length, 1, 'prizes');
  equals($(".jpoker_tourney_details_players", element).length, 1, 'players');
  cleanup();
});

test("jpoker.plugins.tourneyDetails table details", function () {
  expect(5);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user5",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.userInfo.name = "player10";
  server.serial = 42;
  var tourney_details_gethtml_table_details = jpoker.plugins.tourneyDetails.getHTMLTableDetails;
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, packet) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($(".jpoker_tourney_details_table_details", element).length, 1);
      var row = $(".jpoker_tourney_details_tables #X606", element);
      jpoker.plugins.tourneyDetails.getHTMLTableDetails = function (id, packet, table) {
        jpoker.plugins.tourneyDetails.getHTMLTableDetails = tourney_details_gethtml_table_details;
        equals(table, "X606");
        return "table details";
      };
      row.trigger('mouseenter');
      equals(row.hasClass('hover'), true, 'hasClass hover');
      row.trigger('mouseleave');
      equals(row.hasClass('hover'), false, '!hasClass hover');
      row.click();
      equals($(".jpoker_tourney_details_table_details").html(), "table details");
      element.remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyDetails goto table", function () {
  expect(3);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user5",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.userInfo.name = "player10";
  server.serial = 42;
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($(".jpoker_tourney_details_table_details", element).length, 1);
      var goto_table_element = $(".jpoker_tourney_details_tables #X606 .jpoker_tourney_details_tables_goto_table", element);
      equals(goto_table_element.length, 1, 'goto table element');
      server.tableJoin = function (game_id) {
        equals(game_id, 606, 'game_id 606');
      };
      goto_table_element.click();
      element.remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyDetails goto table link_pattern", function () {
  expect(2);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user5",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "running",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.userInfo.name = "player10";
  server.serial = 42;
  var link_pattern = 'http://foo.com/tourneytable?game_id={game_id}';
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString(), 'tourney', {
    link_pattern: link_pattern
  });
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      equals($(".jpoker_tourney_details_table_details", element).length, 1);
      var goto_table_element = $(".jpoker_tourney_details_tables #X606 .jpoker_tourney_details_tables_goto_table", element);
      equals(goto_table_element.length, 1, 'goto table element');
      server.tableJoin = function (game_id) {
        ok(false, 'tableJoin not bound');
      };
      goto_table_element.click();
      element.remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyDetails packet money update", function () {
  expect(2);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 100000,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      },
      "X5": {
        "money": 200000,
        "table_serial": 606,
        "name": "user2",
        "rank": -1
      },
      "X6f": {
        "money": 300000,
        "table_serial": 607,
        "name": "user3",
        "rank": -1
      },
      "X7": {
        "money": 400000,
        "table_serial": 608,
        "name": "user3",
        "rank": -1
      },
      "X8": {
        "money": 500000,
        "table_serial": 608,
        "name": "user4",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4, 5],
      "X607": [6, 7, 8]
    },
    "type": 149,
    "tourney": {
      "registered": 4,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "complete",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0,
      "rank2prize": [1000000, 100000, 10000, 1000, 100]
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.userInfo.name = "player10";
  server.serial = 42;
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var packet = data;
      equals(packet.user2properties.X4.money, 1000);
      equals(packet.tourney.rank2prize[0], 10000);
      element.remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyDetails.register", function () {
  expect(2);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 140,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.userInfo.name = "player10";
  server.serial = 42;
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var input = $("#" + id + " .jpoker_tourney_details_register input");
      equals(input.val(), "Register");
      server.tourneyRegister = function (game_id) {
        equals(tourney_serial, game_id);
      };
      input.click();
      element.remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tourneyDetails.unregister", function () {
  expect(2);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 140,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 0,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var players_count = 1;
  var player_serial = 4;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.userInfo.name = "player0";
  server.serial = player_serial;
  place.jpoker('tourneyDetails', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      var input = $("#" + id + " .jpoker_tourney_details_register input");
      equals(input.val(), "Unregister");
      server.tourneyUnregister = function (game_id) {
        equals(tourney_serial, game_id);
      };
      input.click();
      element.remove();
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

//
// tourneyPlaceholder
//
test("jpoker.plugins.tourneyPlaceholder", function () {
  expect(11);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 140,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 1220102053,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var tourney_starttime = TOURNEY_MANAGER_PACKET.tourney.start_time;
  var tourney_starttime_date = new Date(tourney_starttime * 1000);
  var players_count = 1;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  equals('update' in server.callbacks, false, 'no update registered');
  var display_done = jpoker.plugins.tourneyPlaceholder.callback.display_done;
  jpoker.plugins.tourneyPlaceholder.callback.display_done = function (element) {
    jpoker.plugins.tourneyPlaceholder.callback.display_done = display_done;
    equals($(".jpoker_tourney_placeholder", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('tourneyPlaceholder', 'url', tourney_serial.toString());
  equals(server.callbacks.update.length, 1, 'tourneyPlaceholder update registered');
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      ok(element.hasClass('jpoker_tourney_placeholder'), 'jpoker_tourney_placeholder');
      equals($('.jpoker_tourney_placeholder_table', element).length, 1, 'table');
      equals($('.jpoker_tourney_placeholder_starttime', element).length, 1, 'starttime');
      ok($('.jpoker_tourney_placeholder_starttime', element).html().indexOf(tourney_starttime_date.toLocaleString()) >= 0, $('.jpoker_tourney_placeholder_starttime', element).html());
      $("#" + id).remove();
      return true;
    } else {
      equals(server.callbacks.update.length, 2, 'tourneyPlaceholder and test update registered');
      equals('tourneyDetails' in server.timers, false, 'timer active');
      start_and_cleanup();
      return false;
    }
  });
  server.registerDestroy(function (server) {
    equals('tourneyPlaceholder' in server.timers, false, 'timer killed');
    equals(server.callbacks.update.length, 0, 'update & destroy unregistered');
  });
});

test("jpoker.plugins.tourneyPlaceholder date template", function () {
  expect(1);
  stop();

  var PokerServer = function () {};

  var TOURNEY_MANAGER_PACKET = {
    "user2properties": {
      "X4": {
        "money": 140,
        "table_serial": 606,
        "name": "user1",
        "rank": -1
      }
    },
    "length": 3,
    "tourney_serial": 1,
    "table2serials": {
      "X606": [4]
    },
    "type": 149,
    "tourney": {
      "registered": 1,
      "betting_structure": "level-15-30-no-limit",
      "currency_serial": 1,
      "description_long": "Sit and Go 2 players",
      "breaks_interval": 3600,
      "serial": 1,
      "rebuy_count": 0,
      "state": "registering",
      "buy_in": 300000,
      "add_on_count": 0,
      "description_short": "Sit and Go 2 players, Holdem",
      "player_timeout": 60,
      "players_quota": 2,
      "rake": 0,
      "add_on": 0,
      "start_time": 1220102053,
      "breaks_first": 7200,
      "variant": "holdem",
      "players_min": 2,
      "schedule_serial": 1,
      "add_on_delay": 60,
      "name": "sitngo2",
      "finish_time": 0,
      "prize_min": 0,
      "breaks_duration": 300,
      "seats_per_game": 2,
      "bailor_serial": 0,
      "sit_n_go": "y",
      "rebuy_delay": 0
    },
    "type": "PacketPokerTourneyManager"
  };

  var date_format = '%Y/%m/%d %H:%M:%S';
  var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
  var tourney_starttime = TOURNEY_MANAGER_PACKET.tourney.start_time;
  var tourney_starttime_date = $.strftime(date_format, new Date(tourney_starttime * 1000));
  var players_count = 1;
  jpoker.plugins.tourneyPlaceholder.templates.date = date_format;

  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

    handle: function (packet) {}
  };

  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  var display_done = jpoker.plugins.tourneyPlaceholder.callback.display_done;
  place.jpoker('tourneyPlaceholder', 'url', tourney_serial.toString());
  server.registerUpdate(function (server, what, data) {
    var element = $("#" + id);
    if (element.length > 0) {
      ok($('.jpoker_tourney_placeholder_starttime', element).html().indexOf(tourney_starttime_date) >= 0, $('.jpoker_tourney_placeholder_starttime', element).html());
      $("#" + id).remove();
      return true;
    } else {
      jpoker.plugins.tourneyPlaceholder.templates.date = '';
      start_and_cleanup();
      return false;
    }
  });
});

//
// featuredTable
//
test("jpoker.plugins.featuredTable", function () {
  expect(3);
  stop();

  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": [{
      "observers": 1,
      "name": "One",
      "percent_flop": 98,
      "average_pot": 1535,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 220,
      "betting_structure": "2-4-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 2,
      "waiting": 0,
      "skin": "default",
      "id": 100,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Two",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 101,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Three",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-pot-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 2,
      "waiting": 0,
      "skin": "default",
      "id": 102,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }]
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.selectTables = function (string) {
    equals(string, 'my', 'selectTables my');
    server.selectTables = function (string) {
      server.tableJoin = function (game_id) {
        equals(game_id, 100, 'game_id field');
        start_and_cleanup();
      };
      setTimeout(function () {
        server.notifyUpdate(TABLE_LIST_PACKET);
      }, 0);
    };
    setTimeout(function () {
      server.notifyUpdate({
        'type': 'PacketPokerTableList',
        'packets': []
      });
    }, 0);
    equals(server.callbacks.update.length, 1, 'callback registered');
  };
  place.jpoker('featuredTable', 'url');
});

test("jpoker.plugins.featuredTable selectTable(my) not empty", function () {
  expect(2);
  stop();

  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": [{
      "observers": 1,
      "name": "One",
      "percent_flop": 98,
      "average_pot": 1535,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 220,
      "betting_structure": "2-4-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 2,
      "waiting": 0,
      "skin": "default",
      "id": 100,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Two",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 101,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Three",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-pot-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 2,
      "waiting": 0,
      "skin": "default",
      "id": 102,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }]
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.selectTables = function (string) {
    equals(string, 'my', 'selectTables my');
    setTimeout(function () {
      server.notifyUpdate({
        'type': 'PacketPokerTableList',
        'packets': [TABLE_LIST_PACKET]
      });
      equals(server.callbacks.update.length, 0, 'no callback registered');
      start_and_cleanup();

    }, 0);
  };
  place.jpoker('featuredTable', 'url');
});

test("jpoker.plugins.featuredTable waiting", function () {
  expect(3);
  stop();

  var TABLE_LIST_PACKET = {
    "players": 4,
    "type": "PacketPokerTableList",
    "packets": [{
      "observers": 1,
      "name": "One",
      "percent_flop": 98,
      "average_pot": 1535,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 220,
      "betting_structure": "2-4-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 2,
      "waiting": 0,
      "skin": "default",
      "id": 100,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Two",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 0,
      "waiting": 0,
      "skin": "default",
      "id": 101,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }, {
      "observers": 0,
      "name": "Three",
      "percent_flop": 0,
      "average_pot": 0,
      "seats": 10,
      "variant": "holdem",
      "hands_per_hour": 0,
      "betting_structure": "10-20-pot-limit",
      "currency_serial": 1,
      "muck_timeout": 5,
      "players": 2,
      "waiting": 0,
      "skin": "default",
      "id": 102,
      "type": "PacketPokerTable",
      "player_timeout": 60
    }]
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");
  server.selectTables = function (string) {
    setTimeout(function () {
      server.notifyUpdate({
        'type': 'Packet'
      });
      equals(server.callbacks.update.length, 1, 'callback registered');
      server.selectTables = function (string) {
        setTimeout(function () {
          server.notifyUpdate({
            'type': 'Packet'
          });
          equals(server.callbacks.update.length, 1, 'callback registered');
          server.notifyUpdate(TABLE_LIST_PACKET);
          equals(server.callbacks.update.length, 0, 'callback registered');
          start_and_cleanup();
        }, 0);
      };
      server.notifyUpdate({
        'type': 'PacketPokerTableList',
        'packets': []
      });
    }, 0);
  };
  place.jpoker('featuredTable', 'url');
});

//
// serverStatus
//
test("jpoker.plugins.serverStatus", function () {
  expect(9);

  var server = jpoker.serverCreate({
    url: 'url'
  });

  var id = 'jpoker' + jpoker.serial;
  var place = $("#main");

  //
  // disconnected
  //
  var display_done = jpoker.plugins.serverStatus.callback.display_done;
  jpoker.plugins.serverStatus.callback.display_done = function (element) {
    jpoker.plugins.serverStatus.callback.display_done = display_done;
    equals($(".jpoker_server_status", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('serverStatus', 'url');
  var content = $("#" + id).text();
  equals(content.indexOf("disconnected") >= 0, true, "disconnected");

  //
  // connected
  //
  server.playersCount = 12;
  server.tablesCount = 23;
  server.playersTourneysCount = 11;
  server.tourneysCount = 22;
  server.connectionState = 'connected';
  server.notifyUpdate();
  equals($("#" + id + " .jpoker_server_status_connected").size(), 1, "connected");

  content = $("#" + id).text();
  equals(content.indexOf("12") >= 0, true, "12 players");
  equals(content.indexOf("23") >= 0, true, "23 tables");
  equals(content.indexOf("11") >= 0, true, "11 players tourneys");
  equals(content.indexOf("22") >= 0, true, "22 tourneys");
  //
  // element destroyed
  //
  $("#" + id).remove();
  equals(server.callbacks.update.length, 1, "1 update callback");
  server.notifyUpdate();
  equals(server.callbacks.update.length, 0, "0 update callback");

  jpoker.uninit();
});

//
// login
//
$.fn.triggerKeypress = function (keyCode) {
  return this.trigger("keypress", [$.event.fix({
    event: "keypress",
    keyCode: keyCode,
    target: this[0]
  })]);
};
$.fn.triggerKeydown = function (keyCode) {
  return this.trigger("keydown", [$.event.fix({
    event: "keydown",
    keyCode: keyCode,
    target: this[0]
  })]);
};

test("jpoker.plugins.login", function () {
  expect(12);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var display_done = jpoker.plugins.login.callback.display_done;
  jpoker.plugins.login.callback.display_done = function (element) {
    jpoker.plugins.login.callback.display_done = display_done;
    equals($(".jpoker_login", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('login', 'url');
  var content = null;

  content = $("#" + id).text();
  equals(content.indexOf("user:") >= 0, true, "user:");

  var dialog;

  var expected = {
    name: 'logname',
    password: 'password'
  };

  $(".jpoker_login_submit", place).click();
  dialog = $("#jpokerDialog");
  equals(dialog.text().indexOf('user name must not be empty') >= 0, true, 'empty user name');

  $(".jpoker_login_name", place).attr('value', expected.name);
  $(".jpoker_login_submit", place).click();

  equals(dialog.text().indexOf('password must not be empty') >= 0, true, 'empty password');
  dialog.dialog('destroy');

  $(".jpoker_login_password", place).attr('value', expected.password);

  var result = {
    name: null,
    password: null
  };
  server.login = function (name, password) {
    result.name = name;
    result.password = password;
  };
  $("#" + id).triggerKeypress("13");
  content = $("#" + id).text();
  equals(content.indexOf("login in progress") >= 0, true, "login in progress keypress");
  equals(result.name, expected.name, "login name");
  equals(result.password, expected.password, "login password");

  server.serial = 1;
  server.userInfo.name = 'logname';
  server.notifyUpdate();
  content = $("#" + id).text();
  equals(content.indexOf("logname logout") >= 0, true, "logout");
  equals(server.loggedIn(), true, "loggedIn");

  $("#" + id).click();
  equals(server.loggedIn(), false, "logged out");
  content = $("#" + id).text();
  equals(content.indexOf("user:") >= 0, true, "user:");

  $(".jpoker_login_name", place).attr('value', expected.name);
  server.notifyUpdate();
  equals($(".jpoker_login_name", place).attr('value'), expected.name);

  $("#" + id).remove();
  server.notifyUpdate();

  cleanup(id);
});

test("jpoker.plugins.login signup", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  place.jpoker('login', 'url');

  $(".jpoker_login_signup", place).click();
  ok($(".jpoker_signup").is(":visible"), 'signup visible');

  $("#" + id).remove();
  $(".jpoker_signup").remove();
  server.notifyUpdate();
  cleanup(id);
});

//
// table
//
test("jpoker.plugins.table", function () {
  expect(24);

  var packet = {
    "type": "PacketPokerTable",
    "id": 100
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.tables[packet.id] = new jpoker.table(server, packet);
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var game_id = 100;

  place.jpoker('table', 'url', game_id);
  content = $("#" + id).text();
  for (var seat = 0; seat < 10; seat++) {
    equals($("#seat" + seat + id).size(), 1, "seat " + seat);
  }
  var names = jpoker.plugins.playerSelf.names;
  for (var name = 0; name < names.length; name++) {
    equals($("#" + names[name] + id).css('display'), 'none', names[name]);
  }
  equals($('#jpokerSound').size(), 1, 'jpokerSound');
  equals($('#jpokerSoundAction').size(), 1, 'jpokerSoundAction');
  equals($('#jpokerSoundTable').size(), 1, 'jpokerSoundTable');
  content = $("#" + id).text();
});

if (TEST_TABLE_INFO) {
  test("jpoker.plugins.table: info", function () {
    expect(17);
    var packet = {
      "type": "PacketPokerTable",
      "id": 100,
      "name": "One",
      "variant": "holdem",
      "betting_structure": "15-30-no-limit",
      "seats": 10,
      "average_pot": 1000,
      "percent_flop": 98,
      "players": 10,
      "observers": 20,
      "waiting": 10,
      "player_timeout": 60,
      "muck_timeout": 30,
      "currency_serial": 1
    };
    var server = jpoker.serverCreate({
      url: 'url'
    });
    server.tables[packet.id] = new jpoker.table(server, packet);
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;

    var game_id = 100;

    place.jpoker('table', 'url', game_id);

    var table_info_element = $('#table_info' + id);
    equals(table_info_element.length, 1, 'table info');
    equals($('.jpoker_table_info_name', table_info_element).length, 1, 'table info name');
    equals($('.jpoker_table_info_name', table_info_element).text(), 'Name: One');
    equals($('.jpoker_table_info_variant', table_info_element).length, 1, 'table info variant');
    equals($('.jpoker_table_info_variant', table_info_element).text(), 'Variant: holdem');
    equals($('.jpoker_table_info_blind', table_info_element).length, 1, 'table info blind');
    equals($('.jpoker_table_info_blind', table_info_element).text(), 'Structure: 15-30-no-limit', 'table info blind');
    equals($('.jpoker_table_info_seats', table_info_element).length, 1, 'table info seats');
    equals($('.jpoker_table_info_seats', table_info_element).text(), 'Seats: 10', 'table info seats');
    equals($('.jpoker_table_info_flop', table_info_element).length, 1, 'table info flop');
    equals($('.jpoker_table_info_flop', table_info_element).text(), '98% Flop', 'table info flop');
    equals($('.jpoker_table_info_player_timeout', table_info_element).length, 1, 'table info player timeout');
    equals($('.jpoker_table_info_player_timeout', table_info_element).text(), 'Player timeout: 60', 'table info player timeout');
    equals($('.jpoker_table_info_muck_timeout', table_info_element).length, 1, 'table info muck timeout');
    equals($('.jpoker_table_info_muck_timeout', table_info_element).text(), 'Muck timeout: 30', 'table info muck timeout');
    equals($('.jpoker_table_info_level', table_info_element).length, 1, 'table info level');
    equals($('.jpoker_table_info_level', table_info_element).html(), '', 'table info level');

    cleanup();
  });

  test("jpoker.plugins.table: info tourney", function () {
    expect(4);
    var packet = {
      "type": "PacketPokerTable",
      "id": 100,
      "name": "One",
      "percent_flop": 98,
      "betting_structure": "level-15-30-no-limit"
    };
    var server = jpoker.serverCreate({
      url: 'url'
    });
    var table = new jpoker.table(server, packet);
    server.tables[packet.id] = table;
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;

    var game_id = 100;

    place.jpoker('table', 'url', game_id);

    var table_info_element = $('#table_info' + id);
    equals($('.jpoker_table_info_blind', table_info_element).length, 1, 'table info blind');
    equals($('.jpoker_table_info_blind', table_info_element).text(), 'Structure: level-15-30-no-limit', 'table info blind');
    equals($('.jpoker_table_info_level', table_info_element).length, 1, 'table info level');

    table.handler(server, game_id, {
      type: 'PacketPokerStart',
      game_id: game_id,
      level: 1
    });
    equals($('.jpoker_table_info_level', table_info_element).html(), '1', 'table info level');

    cleanup();
  });
} // TEST_TABLE_INFO
test("jpoker.plugins.table: PacketPokerStart callback.hand_start", function () {
  expect(1);
  stop();
  var packet = {
    "type": "PacketPokerTable",
    "id": 100,
    "name": "One",
    "percent_flop": 98,
    "betting_structure": "15-30-no-limit"
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var table = new jpoker.table(server, packet);
  server.tables[packet.id] = table;
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var game_id = 100;

  place.jpoker('table', 'url', game_id);

  var jpoker_table_callback_hand_start = jpoker.plugins.table.callback.hand_start;
  jpoker.plugins.table.callback.hand_start = function (packet) {
    equals(packet.hands_count, 10, 'hand start callback');
    jpoker.plugins.table.callback.hand_start = jpoker_table_callback_hand_start;
    start_and_cleanup();
  };
  table.handler(server, game_id, {
    type: 'PacketPokerStart',
    game_id: game_id,
    hands_count: 10
  });
});


test("jpoker.plugins.table: PacketPokerTourneyBreak callback.tourney_break/resume", function () {
  expect(2);
  stop();
  var packet = {
    "type": "PacketPokerTable",
    "id": 100,
    "name": "One",
    "percent_flop": 98,
    "betting_structure": "level-15-30-no-limit"
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var table = new jpoker.table(server, packet);
  server.tables[packet.id] = table;
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var game_id = 100;

  place.jpoker('table', 'url', game_id);

  var jpoker_table_callback_tourney_break = jpoker.plugins.table.callback.tourney_break;
  jpoker.plugins.table.callback.tourney_break = function (packet) {
    equals(packet.type, 'PacketPokerTableTourneyBreakBegin', 'tourney break callback');
    jpoker.plugins.table.callback.tourney_break = jpoker_table_callback_tourney_break;
  };
  table.handler(server, game_id, {
    type: 'PacketPokerTableTourneyBreakBegin',
    game_id: game_id
  });
  var jpoker_table_callback_tourney_resume = jpoker.plugins.table.callback.tourney_resume;
  jpoker.plugins.table.callback.tourney_resume = function (packet) {
    equals(packet.type, 'PacketPokerTableTourneyBreakDone', 'tourney resume callback');
    jpoker.plugins.table.callback.tourney_resume = jpoker_table_callback_tourney_resume;
    start_and_cleanup();
  };
  table.handler(server, game_id, {
    type: 'PacketPokerTableTourneyBreakDone',
    game_id: game_id
  });
});

test("jpoker.plugins.table: PacketPokerTourneyBreak callback.tourney_break/resume default", function () {
  expect(3);
  var packet = {
    "type": "PacketPokerTable",
    "id": 100,
    "name": "One",
    "percent_flop": 98,
    "betting_structure": "level-15-30-no-limit"
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var table = new jpoker.table(server, packet);
  server.tables[packet.id] = table;
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var game_id = 100;

  place.jpoker('table', 'url', game_id);

  var resume_time = 1220979087 * 1000;
  var date = new Date();
  date.setTime(resume_time);
  table.handler(server, game_id, {
    type: 'PacketPokerTableTourneyBreakBegin',
    game_id: game_id,
    resume_time: 1220979087
  });
  ok($("#jpokerDialog").parents().is(':visible'), 'jpoker dialog visible');
  ok($("#jpokerDialog").html().indexOf(date.toLocaleString()) >= 0, $("#jpokerDialog").html());
  table.handler(server, game_id, {
    type: 'PacketPokerTableTourneyBreakDone',
    game_id: game_id
  });
  ok($("#jpokerDialog").parents().is(':hidden'), 'jpoker dialog hidden');
  cleanup(id);
});

test("jpoker.plugins.table: PacketPokerTourneyBreak callback.tourney_break/resume default date template", function () {
  expect(1);
  var packet = {
    "type": "PacketPokerTable",
    "id": 100,
    "name": "One",
    "percent_flop": 98,
    "betting_structure": "level-15-30-no-limit"
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var table = new jpoker.table(server, packet);
  server.tables[packet.id] = table;
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var game_id = 100;
  var resume_time = 1220979087;
  var date = new Date(resume_time * 1000);
  var date_format = '%Y/%m/%d %H:%M:%S';
  var date_string = $.strftime(date_format, date);
  jpoker.plugins.table.templates.date = date_format;

  place.jpoker('table', 'url', game_id);

  table.handler(server, game_id, {
    type: 'PacketPokerTableTourneyBreakBegin',
    game_id: game_id,
    resume_time: resume_time
  });
  ok($("#jpokerDialog").html().indexOf(date_string) >= 0, $("#jpokerDialog").html());
  table.handler(server, game_id, {
    type: 'PacketPokerTableTourneyBreakDone',
    game_id: game_id
  });
  cleanup(id);
});

test("jpoker.plugins.table: PacketPokerTourneyRank", function () {
  expect(3);
  var game_id = 100;
  var packet = {
    "type": "PacketPokerTable",
    "id": game_id,
    "name": "One",
    "percent_flop": 98,
    "betting_structure": "level-15-30-no-limit"
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var table = new jpoker.table(server, packet);
  server.tables[packet.id] = table;
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var money = 5501;
  var rank_packet = {
    type: 'PacketPokerTourneyRank',
    game_id: game_id,
    serial: 1010,
    rank: 22,
    players: 44,
    money: money
  };

  place.jpoker('table', 'url', game_id);

  server.rankClick = function (server, tourney_serial) {
    equals(rank_packet.serial, tourney_serial);
  };
  table.handler(server, game_id, rank_packet);
  equals($('#jpokerRankDialog').text().indexOf(money / 100.0) >= 0, true, 'rank money properly formated ' + money + ' is ' + money / 100.0);
  equals($('.ui-dialog').hasClass('jpoker_dialog_rank'), true);
  $('#jpokerRankDialog .jpoker_tournament_details').click();

  cleanup(id);
});

test("jpoker.plugins.table.reinit", function () {
  expect(21);

  var packet = {
    "type": "PacketPokerTable",
    "id": 100
  };
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.tables[packet.id] = new jpoker.table(server, packet);
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;

  var game_id = 100;

  place.jpoker('table', 'url', game_id);
  content = $("#" + id).text();
  for (var seat = 0; seat < 10; seat++) {
    equals($("#seat" + seat + id).size(), 1, "seat " + seat);
  }
  var names = jpoker.plugins.playerSelf.names;
  for (var name = 0; name < names.length; name++) {
    equals($("#" + names[name] + id).css('display'), 'none', names[name]);
  }
  content = $("#" + id).text();
});

test("jpoker.plugins.table.chat", function () {
  expect(10);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var player_serial = 1;
  server.serial = player_serial; // pretend logged in
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var game_window = $('#game_window' + id);
  var chat = $(".jpoker_chat_input", game_window);
  equals(chat.size(), 1, "chat DOM element");
  equals(chat.is(':hidden'), true, "chat hidden");
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: 0,
    serial: player_serial,
    game_id: game_id,
    name: 'username'
  });
  equals(chat.is(':visible'), true, "chat visible");
  var sent = false;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerChat');
    equals(packet.serial, player_serial);
    equals(packet.game_id, game_id);
    equals("^" + packet.message + "$", '^A\'B"C$');
    sent = true;
  };
  $('input', chat).attr('value', 'A\'B"C');
  chat.triggerKeypress("13");
  equals(sent, true, "packet sent");
  equals($('input', chat).attr('value'), '', 'input is reset');
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerLeave',
    seat: 0,
    serial: player_serial,
    game_id: game_id
  });
  equals(chat.is(':hidden'), true, "chat hidden (2)");
  cleanup(id);
});

if (TEST_AVATAR) {
  test("jpoker.plugins.table: PokerPlayerArrive/Leave (Self)", function () {
    expect(18);

    var server = jpoker.serverCreate({
      url: 'url'
    });
    var player_serial = 1;
    server.serial = player_serial; // pretend logged in
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    $('#jpokerRebuy').remove(); // just in case it pre-existed
    place.jpoker('table', 'url', game_id);
    equals($("#seat0" + id).size(), 1, "seat0 DOM element");
    equals($("#seat0" + id).css('display'), 'none', "seat0 hidden");
    equals($("#sit_seat0" + id).css('display'), 'block', "sit_seat0 hidden");
    equals(table.seats[0], null, "seat0 empty");
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: 0,
      serial: player_serial,
      game_id: game_id,
      name: 'username',
      url: 'http://mycustomavatar.png'
    });
    equals($("#jpokerSound " + jpoker.sound).attr("src").indexOf('arrive') >= 0, true, 'sound arrive');
    equals($("#seat0" + id).css('display'), 'block', "arrive");
    equals($("#sit_seat0" + id).css('display'), 'none', "seat0 hidden");
    equals($("#player_seat0_name" + id).html(), 'click to sit', "username arrive");
    var avatar_image = $("#player_seat0_avatar" + id + " img").attr("src");
    ok(avatar_image.indexOf("mycustomavatar.png") >= 0, "custom avatar" + avatar_image);
    equals($("#player_seat0_avatar" + id + " img").attr('alt'), 'username', 'alt of seat0');
    equals(table.seats[0], player_serial, "player 1");
    equals(table.serial2player[player_serial].serial, player_serial, "player 1 in player2serial");
    var names = ['check', 'call', 'raise', 'fold'];
    var texts = ['check', 'call ', 'Raise', 'fold'];
    for (var i = 0; i < names.length; i++) {
      equals($("#" + names[i] + id).text(), texts[i]);
    }
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerLeave',
      seat: 0,
      serial: player_serial,
      game_id: game_id
    });
    equals($("#seat0" + id).css('display'), 'none', "leave");
    equals(table.seats[0], null, "seat0 again");
    cleanup(id);
  });
} else { // TEST_AVATAR
  test("jpoker.plugins.table: PokerPlayerArrive/Leave (Self)", function () {
    expect(16);

    var server = jpoker.serverCreate({
      url: 'url'
    });
    var player_serial = 1;
    server.serial = player_serial; // pretend logged in
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    $('#jpokerRebuy').remove(); // just in case it pre-existed
    place.jpoker('table', 'url', game_id);
    equals($("#seat0" + id).size(), 1, "seat0 DOM element");
    equals($("#seat0" + id).css('display'), 'none', "seat0 hidden");
    equals($("#sit_seat0" + id).css('display'), 'block', "sit_seat0 hidden");
    equals(table.seats[0], null, "seat0 empty");
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: 0,
      serial: player_serial,
      game_id: game_id,
      name: 'username',
      url: 'http://mycustomavatar.png'
    });
    equals($("#jpokerSound " + jpoker.sound).attr("src").indexOf('arrive') >= 0, true, 'sound arrive');
    equals($("#seat0" + id).css('display'), 'block', "arrive");
    equals($("#sit_seat0" + id).css('display'), 'none', "seat0 hidden");
    equals($("#player_seat0_name" + id).html(), 'click to sit', "username arrive");
    equals(table.seats[0], player_serial, "player 1");
    equals(table.serial2player[player_serial].serial, player_serial, "player 1 in player2serial");
    var names = ['check', 'call', 'raise', 'fold'];
    for (var i = 0; i < names.length; i++) {
      equals($("#" + names[i] + id).text(), names[i]);
    }
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerLeave',
      seat: 0,
      serial: player_serial,
      game_id: game_id
    });
    equals($("#seat0" + id).css('display'), 'none', "leave");
    equals(table.seats[0], null, "seat0 again");
    cleanup(id);
  });
} // TEST_AVATAR
test("jpoker.plugins.table: sit_seat", function () {
  expect(63);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id,
    seats: 5
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  equals(table.max_players, 5, 'max_players');
  for (var i = 2; i <= 10; ++i) {
    table.max_players = i;
    table.resetSeatsLeft();
    equals(table.seats_left.length, i, i + ' seats left');
  }
  table.max_players = 0;
  table.resetSeatsLeft();
  equals(table.seats_left.length, 0, '0 seats left');
  table.max_players = 4;
  table.resetSeatsLeft();

  place.jpoker('table', 'url', game_id);
  equals($("#seat0" + id).css('display'), 'none', "seat0 hidden");
  equals($("#sit_seat0" + id).is(':hidden'), true, "sit_seat0 hidden");
  equals($("#sit_seat1" + id).is(':hidden'), true, "sit_seat1 hidden");
  equals($("#sit_seat2" + id).is(':hidden'), true, "sit_seat2 hidden");
  equals($("#sit_seat3" + id).is(':hidden'), true, "sit_seat3 hidden");
  equals($("#sit_seat4" + id).is(':hidden'), true, "sit_seat4 hidden");
  equals($("#sit_seat5" + id).is(':hidden'), true, "sit_seat5 hidden");
  equals($("#sit_seat6" + id).is(':hidden'), true, "sit_seat6 hidden");
  equals($("#sit_seat7" + id).is(':hidden'), true, "sit_seat7 hidden");
  equals($("#sit_seat8" + id).is(':hidden'), true, "sit_seat8 hidden");
  equals($("#sit_seat9" + id).is(':hidden'), true, "sit_seat9 hidden");
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  equals($("#sit_seat0" + id).is(':hidden'), true, "sit_seat0 hidden");
  equals($("#sit_seat1" + id).is(':visible'), true, "sit_seat1 visible");
  equals($("#sit_seat2" + id).is(':hidden'), true, "sit_seat2 hidden");
  equals($("#sit_seat3" + id).is(':visible'), true, "sit_seat3 visible");
  equals($("#sit_seat4" + id).is(':hidden'), true, "sit_seat4 hidden");
  equals($("#sit_seat5" + id).is(':hidden'), true, "sit_seat5 hidden");
  equals($("#sit_seat6" + id).is(':visible'), true, "sit_seat6 visible");
  equals($("#sit_seat7" + id).is(':hidden'), true, "sit_seat7 hidden");
  equals($("#sit_seat8" + id).is(':visible'), true, "sit_seat8 visible");
  equals($("#sit_seat9" + id).is(':hidden'), true, "sit_seat9 hidden");
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: 1,
    serial: player_serial,
    game_id: game_id,
    name: 'playername'
  });
  equals($("#sit_seat0" + id).is(':hidden'), true, "sit_seat0 hidden");
  equals($("#sit_seat1" + id).is(':hidden'), true, "sit_seat1 hidden");
  equals($("#sit_seat2" + id).is(':hidden'), true, "sit_seat2 hidden");
  equals($("#sit_seat3" + id).is(':hidden'), true, "sit_seat3 hidden");
  equals($("#sit_seat4" + id).is(':hidden'), true, "sit_seat4 hidden");
  equals($("#sit_seat5" + id).is(':hidden'), true, "sit_seat5 hidden");
  equals($("#sit_seat6" + id).is(':hidden'), true, "sit_seat6 hidden");
  equals($("#sit_seat7" + id).is(':hidden'), true, "sit_seat7 hidden");
  equals($("#sit_seat8" + id).is(':hidden'), true, "sit_seat8 hidden");
  equals($("#sit_seat9" + id).is(':hidden'), true, "sit_seat9 hidden");
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: 3,
    serial: player_serial + 1,
    game_id: game_id,
    name: 'playername'
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerLeave',
    seat: 3,
    serial: player_serial + 1,
    game_id: game_id
  });
  equals($("#sit_seat3" + id).is(':hidden'), true, "sit_seat3 hidden");

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerLeave',
    seat: 1,
    serial: player_serial,
    game_id: game_id
  });
  equals($("#sit_seat0" + id).is(':hidden'), true, "sit_seat0 hidden");
  equals($("#sit_seat1" + id).is(':visible'), true, "sit_seat1 visible");
  equals($("#sit_seat2" + id).is(':hidden'), true, "sit_seat2 hidden");
  equals($("#sit_seat3" + id).is(':visible'), true, "sit_seat3 visible");
  equals($("#sit_seat4" + id).is(':hidden'), true, "sit_seat4 hidden");
  equals($("#sit_seat5" + id).is(':hidden'), true, "sit_seat5 hidden");
  equals($("#sit_seat6" + id).is(':visible'), true, "sit_seat6 visible");
  equals($("#sit_seat7" + id).is(':hidden'), true, "sit_seat7 hidden");
  equals($("#sit_seat8" + id).is(':visible'), true, "sit_seat8 visible");
  equals($("#sit_seat9" + id).is(':hidden'), true, "sit_seat9 hidden");
  server.logout();
  equals($("#sit_seat0" + id).is(':hidden'), true, "sit_seat0 hidden");
  equals($("#sit_seat1" + id).is(':hidden'), true, "sit_seat1 hidden");
  equals($("#sit_seat2" + id).is(':hidden'), true, "sit_seat2 hidden");
  equals($("#sit_seat3" + id).is(':hidden'), true, "sit_seat3 hidden");
  equals($("#sit_seat4" + id).is(':hidden'), true, "sit_seat4 hidden");
  equals($("#sit_seat5" + id).is(':hidden'), true, "sit_seat5 hidden");
  equals($("#sit_seat6" + id).is(':hidden'), true, "sit_seat6 hidden");
  equals($("#sit_seat7" + id).is(':hidden'), true, "sit_seat7 hidden");
  equals($("#sit_seat8" + id).is(':hidden'), true, "sit_seat8 hidden");
  equals($("#sit_seat9" + id).is(':hidden'), true, "sit_seat9 hidden");
  cleanup(id);
});

test("jpoker.plugins.table: sit_seat_progress", function () {
  expect(5);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id,
    seats: 5
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  place.jpoker('table', 'url', game_id);
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: 42
  });
  var sit_seat = $("#sit_seat0" + id);
  equals(sit_seat.is(':visible'), true, "sit_seat0 visible");
  equals(sit_seat.hasClass('jpoker_sit_seat'), true, ".jpoker_sit_seat");
  equals($('.jpoker_sit_seat_progress', sit_seat).length, 1, ".jpoker_sit_seat_progress");
  sit_seat.click();
  equals(sit_seat.hasClass('jpoker_self_get_seat'), true, '.jpoker_self_get_seat is set');
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: 0,
    serial: 42,
    game_id: game_id,
    name: 'username',
    url: 'http://mycustomavatar.png'
  });
  equals(sit_seat.hasClass('jpoker_self_get_seat'), false, '.jpoker_self_get_seat is not set');
  cleanup(id);
});

test("jpoker.plugins.table: PacketPokerBoardCards", function () {
  expect(7);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  equals($("#board0" + id).size(), 1, "board0 DOM element");
  equals($("#board0" + id).css('display'), 'none', "board0 hidden");
  equals(table.board[0], null, "board0 empty");
  var card_value = 1;
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    cards: [card_value],
    game_id: game_id
  });
  equals($("#board0" + id).css('display'), 'block', "card 1 set");
  equals($("#board0" + id).hasClass('jpoker_card_3h'), true, 'card_3h class');
  equals($("#board1" + id).css('display'), 'none', "card 2 not set");
  equals(table.board[0], card_value, "card in slot 0");
  start_and_cleanup();
});

test("jpoker.plugins.table: PacketPokerTableQuit", function () {
  expect(7);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;
  server.serial = 42;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  equals($("#quit" + id).size(), 1, "quit DOM element");
  var sent = false;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerTableQuit');
    equals(packet.game_id, game_id);
    equals(server.state, server.TABLE_QUIT);
    sent = true;
    server.setState(server.RUNNING);
  };
  server.setTimeout = function (callback, delay) {
    callback();
  };
  equals($("#game_window" + id).size(), 1, 'game element exists');
  $("#quit" + id).click();
  equals(sent, true, "packet sent");
  equals($("#game_window" + id).size(), 0, 'game element destroyed');
  cleanup(id);
});

test("jpoker.plugins.table: options", function () {
  expect(9);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  var table;
  var player_serial = 42;
  var player_seat = 1;
  server.tables[game_id] = new jpoker.table(server, table_packet);
  server.serial = player_serial;
  table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var options = $("#options" + id);
  equals(options.length, 1, '#options element');
  equals(options.is(':hidden'), true, '#options hidden after table create');
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: 'dummy',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  equals($('.jpoker_options', options).length, 1, '.jpoker_options element');
  equals(options.is(':visible'), true, '#options visible after player arrive');
  options.trigger('mouseenter');
  equals(options.hasClass('hover'), true, 'hasClass hover');
  options.trigger('mouseleave');
  equals(options.hasClass('hover'), false, '!hasClass hover');
  equals($('#jpokerOptionsDialog').length, 1, '#jpokerOptionsDialog element');
  equals($('.ui-dialog.jpoker_options_dialog').length, 1, 'dialog initialized');
  options.click();
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerLeave',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  equals(options.is(':hidden'), true, '#options hidden after player leave');
  cleanup(id);
});

test("jpoker.plugins.table: quit callback PacketPokerTableDestroy", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var callback = jpoker.plugins.table.callback.quit;
  jpoker.plugins.table.callback.quit = function (table, packet) {
    jpoker.plugins.table.callback.quit = callback;
    equals(game_id, table.id, 'callback called');
    equals(packet.type, 'PacketPokerTableDestroy', 'packet arg');
    start_and_cleanup();
  };

  place.jpoker('table', 'url', game_id);
  $("#quit" + id).click();
});

test("jpoker.plugins.table: quit callback PacketPokerTableMove", function () {
  expect(0);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var callback = jpoker.plugins.table.callback.quit;
  jpoker.plugins.table.callback.quit = function (table, packet) {
    ok(false, 'should not be called');
  };

  place.jpoker('table', 'url', game_id);
  table.handler(server, game_id, {
    type: 'PacketPokerTableMove',
    game_id: game_id
  });
  jpoker.plugins.table.callback.quit = callback;
  start_and_cleanup();
});

test("jpoker.plugins.table: quit non running", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  place.jpoker('table', 'url', game_id);
  server.setState('dummy');
  $("#quit" + id).click();

  var callback = jpoker.plugins.table.callback.quit;
  jpoker.plugins.table.callback.quit = function (table) {
    jpoker.plugins.table.callback.quit = callback;
    equals(server.state, 'running', 'server running');
    start_and_cleanup();
  };
  setTimeout(function () {
    server.setState('running');
  }, 10);
});

test("jpoker.plugins.table: PacketPokerShowdown sound", function () {
  // {"length":589,"cookie":"","showdown_stack":[{"player_list":[18,5],"serial2share":{"5":1180000},"pot":1200000,"serial2delta":{"18":-200000,"5":180000},"serial2rake":{"5":20000},"serial2best":{"5":{"hi":[34036736,["TwoPair",46,33,31,18,38]]}},"type":"game_state","side_pots":{"building":0,"contributions":{"0":{"1":{"5":800000},"0":{"18":200000,"5":200000}},"total":{"18":200000,"5":1000000}},"last_round":0,"pots":[[400000,400000],[800000,1200000]]}},{"serials":[5,18],"pot":1200000,"hi":[5],"chips_left":0,"type":"resolve","serial2share":{"5":1200000}}],"game_id":204,"serial":0,"type":"PacketPokerShowdown","time__":1255989192205}
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var user_serial = 20;
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  server.serial = user_serial;
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var packet = {
    'type': 'PacketPokerShowdown',
    'game_id': game_id,
    'showdown_stack': [{
      'serial2delta': {}
    }]
  };
  var sound_table_self_win = jpoker.plugins.table.callback.sound.self_win;
  jpoker.plugins.table.callback.sound.self_win = function (server) {
    sound_table_self_win(server);
    equals($("#jpokerSoundTable " + jpoker.sound).attr("src").indexOf('win') >= 0, true, 'sound win');
  };
  packet.showdown_stack[0].serial2delta[user_serial] = 1;
  table.handler(server, game_id, packet);
  packet.showdown_stack[0].serial2delta[user_serial] = -1;
  table.handler(server, game_id, packet);
  delete packet.showdown_stack[0].serial2delta[user_serial];
  table.handler(server, game_id, packet);
  delete packet.showdown_stack[0].serial2delta;
  table.handler(server, game_id, packet);
  packet.showdown_stack = [];
  table.handler(server, game_id, packet);
  delete packet.showdown_stack;
  table.handler(server, game_id, packet);
  jpoker.plugins.table.callback.sound.self_win = sound_table_self_win;
  cleanup();
});

test("jpoker.plugins.table: PacketPokerDealer", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  equals($("#dealer0" + id).size(), 1, "dealer0 DOM element");
  equals($("#dealer0" + id).css('display'), 'none', "dealer0 hidden");
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: 0,
    game_id: game_id
  });
  equals($("#dealer0" + id).css('display'), 'block', "dealer 0 set");
  equals($("#dealer1" + id).css('display'), 'none', "dealer 1 not set");
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: 1,
    game_id: game_id
  });
  equals($("#dealer0" + id).css('display'), 'none', "dealer 0 not set");
  equals($("#dealer1" + id).css('display'), 'block', "dealer 1 set");
  start_and_cleanup();
});

test("jpoker.plugins.table: PacketPokerChat", function () {
  expect(20);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  var player_seat = 2;
  var player_name = 'username';
  var game_window = $('#game_window' + id);
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id,
    name: player_name
  });
  equals($(".jpoker_chat_history_dealer", game_window).size(), 1, "chat history dealer DOM element");
  equals($(".jpoker_chat_history_player", game_window).size(), 1, "chat history player DOM element");
  var message = 'voila\ntout';
  table.handler(server, game_id, {
    type: 'PacketPokerChat',
    message: message,
    game_id: game_id,
    serial: player_serial
  });
  var chat_history_player = $(".jpoker_chat_history_player", game_window);
  var chat_lines = $(".jpoker_chat_line", chat_history_player);
  equals(chat_lines.length, 2);
  equals($(".jpoker_chat_prefix", chat_lines.eq(0)).html(), "username: ");
  equals($(".jpoker_chat_message", chat_lines.eq(0)).html(), "voila");
  equals($(".jpoker_chat_prefix", chat_lines.eq(1)).html(), "username: ");
  equals($(".jpoker_chat_message", chat_lines.eq(1)).html(), "tout");
  equals($(".jpoker_chat_history_player").attr('scrollTop'), 0);
  equals($(".jpoker_chat_history_dealer").text(), "", "no dealer message");
  $(".jpoker_chat_history_player").text("");

  var dealer_message = 'Dealer: voila\nDealer: tout\n';
  table.handler(server, game_id, {
    type: 'PacketPokerChat',
    message: dealer_message,
    game_id: game_id,
    serial: 0
  });
  var chat_history_dealer = $(".jpoker_chat_history_dealer", game_window);
  var chat_lines_dealer = $(".jpoker_chat_line", chat_history_dealer);
  equals(chat_lines_dealer.length, 2);
  equals($(".jpoker_chat_prefix", chat_lines_dealer.eq(0)).html(), "Dealer: ");
  equals($(".jpoker_chat_message", chat_lines_dealer.eq(0)).html(), "voila");
  equals($(".jpoker_chat_prefix", chat_lines_dealer.eq(1)).html(), "Dealer: ");
  equals($(".jpoker_chat_message", chat_lines_dealer.eq(1)).html(), "tout");
  equals($(".jpoker_chat_history_dealer").attr('scrollTop'), 0);
  equals($(".jpoker_chat_history_player").text(), "", "no player message");

  for (var i = 0; i < 42; ++i) {
    table.handler(server, game_id, {
      type: 'PacketPokerChat',
      message: dealer_message,
      game_id: game_id,
      serial: 0
    });
    table.handler(server, game_id, {
      type: 'PacketPokerChat',
      message: message,
      game_id: game_id,
      serial: player_serial
    });
  }
  //
  // chat modification callback
  //
  var chat_changed = jpoker.plugins.table.callback.chat_changed;
  jpoker.plugins.table.callback.chat_changed = function (element) {
    ok($(element).html().indexOf('chat changed'));
  };
  var chat_filter = jpoker.plugins.table.callback.chat_filter;
  jpoker.plugins.table.callback.chat_filter = function (table, packet) {
    equals(packet.message, 'chat unfiltered');
    packet.message = 'chat changed';
    return packet;
  };
  table.handler(server, game_id, {
    type: 'PacketPokerChat',
    message: 'chat unfiltered',
    game_id: game_id,
    serial: player_serial
  });
  jpoker.plugins.table.callback.chat_changed = function (element) {
    equals('', 'unexpected call to chat_changed');
  };
  jpoker.plugins.table.callback.chat_filter = function (table, packet) {
    // packet filtered out
    return null;
  };
  table.handler(server, game_id, {
    type: 'PacketPokerChat',
    message: 'chat filtered out',
    game_id: game_id,
    serial: player_serial
  });
  jpoker.plugins.table.callback.chat_changed = chat_changed;
  jpoker.plugins.table.callback.chat_filter = chat_filter;
  ok($(".jpoker_chat_history_player").attr('scrollTop') > 0, 'scrollTop');
  ok($(".jpoker_chat_history_dealer").attr('scrollTop') > 0, 'scrollTop');

  cleanup();
});

test("jpoker.plugins.table: PacketPokerChat code injection", function () {
  expect(0);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  var player_seat = 2;
  var player_name = '<script>$.jpoker.injection();</script>';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id,
    name: player_name
  });
  jpoker.injection = function () {
    ok(false, 'code injection');
  };
  var message = '<script>$.jpoker.injection();</script>';
  table.handler(server, game_id, {
    type: 'PacketPokerChat',
    message: message,
    game_id: game_id,
    serial: player_serial
  });
  delete jpoker.injection;
  cleanup();
});

test("jpoker.plugins.table: PacketPokerPosition", function () {
  expect(12);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var player_name = 'username';
  for (var i = 1; i <= 3; i++) {
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: i,
      serial: i * 10,
      game_id: game_id,
      name: player_name + i
    });
    table.serial2player[i * 10].sit_out = false;
  }

  place.jpoker('table', 'url', game_id);

  var seat;
  for (seat = 1; seat <= 3; seat++) {
    var c = "#player_seat" + seat + id;
    equals($(c).size(), 1, "seat length " + seat);
    equals($(c).hasClass('jpoker_position'), false, "seat " + seat);
  }
  table.handler(server, game_id, {
    type: 'PacketPokerPosition',
    serial: 10,
    game_id: game_id
  });
  equals($("#player_seat1" + id).hasClass('jpoker_position'), true, "seat 1 in position");
  equals($("#player_seat1" + id).hasClass('jpoker_sit_out'), false, "seat 1 sit");

  equals($("#player_seat2" + id).hasClass('jpoker_position'), false, "seat 2 not in position");
  equals($("#player_seat2" + id).hasClass('jpoker_sit_out'), false, "seat 2 sit");

  table.handler(server, game_id, {
    type: 'PacketPokerPosition',
    serial: 20,
    game_id: game_id
  });
  equals($("#player_seat1" + id).hasClass('jpoker_position'), false, "seat 1 not in position");
  equals($("#player_seat2" + id).hasClass('jpoker_position'), true, "seat 2 in position");

  start_and_cleanup();
});

test("jpoker.plugins.table.timeout", function () {
  expect(24);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var player_name = 'username';
  for (var i = 1; i <= 3; i++) {
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: i,
      serial: i * 10,
      game_id: game_id,
      name: player_name + i
    });
    table.serial2player[i * 10].sit_out = false;
  }

  place.jpoker('table', 'url', game_id);

  var seat;
  for (seat = 1; seat <= 3; seat++) {
    var c = "#player_seat" + seat + "_timeout" + id;
    equals($(c).size(), 1, "seat timeout length " + seat);
    equals($(c).hasClass("jpoker_timeout"), true, "seat jpoker_timeout class " + seat);
    equals($(c).is(":hidden"), true, "seat timeout hidden");
  }
  equals($(".jpoker_timeout_progress", place).length, 3, "timeout_progress");

  table.handler(server, game_id, {
    type: 'PacketPokerPosition',
    serial: 10,
    game_id: game_id
  });
  equals($("#player_seat1_timeout" + id).is(":visible"), true, "seat 1 timeout visible");
  equals($("#player_seat1_timeout" + id).attr("pcur"), 100, "seat 1 timeout 100");
  equals($("#player_seat2_timeout" + id).is(":hidden"), true, "seat 2 timeout hidden");

  table.handler(server, game_id, {
    type: 'PacketPokerPosition',
    serial: 20,
    game_id: game_id
  });

  equals($("#player_seat1_timeout" + id).is(":hidden"), true, "seat 1 timeout hidden");
  equals($("#player_seat2_timeout" + id).is(":visible"), true, "seat 2 timeout visible");
  equals($("#player_seat2_timeout" + id).attr("pcur"), 100, "seat 2 timeout 100");
  var full_width = parseFloat($("#player_seat2_timeout" + id + " .jpoker_timeout_progress").css("width"));

  var jquery_stop = jQuery.fn.stop;
  jQuery.fn.stop = function () {
    ok(true, '$.stop called');
    return this;
  };
  table.handler(server, game_id, {
    type: 'PacketPokerTimeoutWarning',
    serial: 20,
    game_id: game_id
  });
  jQuery.fn.stop = jquery_stop;

  var half_width = parseFloat($("#player_seat2_timeout" + id + " .jpoker_timeout_progress").css("width"));
  var width_delta = full_width / 2 - half_width;
  equals(Math.abs(width_delta) < 1.0, true, "seat 2 width 50% delta = " + width_delta);
  equals($("#player_seat1_timeout" + id).is(":hidden"), true, "seat 1 timeout hidden");
  equals($("#player_seat2_timeout" + id).is(":visible"), true, "seat 2 timeout visible");
  equals($("#player_seat2_timeout" + id).attr("pcur"), 50, "seat 2 timeout 50");

  table.handler(server, game_id, {
    type: 'PacketPokerTimeoutNotice',
    serial: 20,
    game_id: game_id
  });

  equals($("#player_seat1_timeout" + id).is(":hidden"), true, "seat 1 timeout hidden");
  equals($("#player_seat2_timeout" + id).is(":visible"), true, "seat 2 timeout hidden");
  equals($("#player_seat2_timeout" + id).attr("pcur"), 0, "seat 2 timeout 0");

  start_and_cleanup();
});

test("jpoker.plugins.table: PacketPokerPotChips/Reset", function () {
  expect(70);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  equals(table.pots[0], 0, "pot0 empty");
  var pot = [10, 3, 100, 8];
  var pot_value = jpoker.chips.chips2value(pot);
  equals(pot_value - 8.30 < jpoker.chips.epsilon, true, "pot_value");

  var pots_element = $('#pots' + id);

  equals(pots_element.length, 1, 'pots element');
  ok(pots_element.hasClass('jpoker_pots'), '.jpoker_pots');
  ok(pots_element.hasClass('jpoker_ptable_pots'), '.jpoker_ptable_pots');
  ok(pots_element.hasClass('jpoker_pots0'), '.jpoker_pots0');
  equals($('.jpoker_pot', pots_element).length, 10, '.jpoker_pot childs');
  for (var i = 0; i < 10; i += 1) {
    equals($('.jpoker_pot' + i, pots_element).length, 1, '.jpoker_pot' + i);
    equals($('.jpoker_pot' + i, pots_element).is(':hidden'), true, 'hidden .jpoker_pot' + i);
  }
  equals($('.jpoker_chips_image', pots_element).length, 10, '.jpoker_chips_image');
  equals($('.jpoker_chips_amount', pots_element).length, 10, '.jpoker_chips_amount');


  table.handler(server, game_id, {
    type: 'PacketPokerPotChips',
    bet: pot,
    index: 0,
    game_id: game_id
  });
  equals(table.pots[0], pot_value, "pot0 empty");
  equals($('.jpoker_pot0', pots_element).is(':visible'), true, 'pot 0 visible');
  equals($('.jpoker_pot0', pots_element).attr('title'), pot_value, 'pot 0 title');
  equals($('.jpoker_pot0 .jpoker_chips_amount', pots_element).text(), pot_value, 'pot 0 text');
  ok(pots_element.hasClass('jpoker_pots'), '.jpoker_pots');
  ok(pots_element.hasClass('jpoker_ptable_pots'), '.jpoker_ptable_pots');
  ok(pots_element.hasClass('jpoker_pots1'), '.jpoker_pots1');
  equals(pots_element.hasClass('jpoker_pots0'), false, 'no .jpoker_pots0');

  table.handler(server, game_id, {
    type: 'PacketPokerPotChips',
    bet: pot,
    index: 1,
    game_id: game_id
  });
  equals($('.jpoker_pot1', pots_element).is(':visible'), true, 'pot 1 visible');
  equals($('.jpoker_pot1', pots_element).attr('title'), pot_value, 'pot 1 title');
  equals($('.jpoker_pot1 .jpoker_chips_amount', pots_element).text(), pot_value, 'pot 1 text');
  ok(pots_element.hasClass('jpoker_pots'), '.jpoker_pots');
  ok(pots_element.hasClass('jpoker_ptable_pots'), '.jpoker_ptable_pots');
  ok(pots_element.hasClass('jpoker_pots2'), '.jpoker_pots2');
  equals(pots_element.hasClass('jpoker_pots0'), false, 'no .jpoker_pots0');
  equals(pots_element.hasClass('jpoker_pots1'), false, 'no .jpoker_pots1');

  table.handler(server, game_id, {
    type: 'PacketPokerChipsPotReset',
    game_id: game_id
  });
  equals(table.pots[0], 0, "pot0 empty");
  ok(pots_element.hasClass('jpoker_pots'), '.jpoker_pots');
  ok(pots_element.hasClass('jpoker_ptable_pots'), '.jpoker_ptable_pots');
  ok(pots_element.hasClass('jpoker_pots0'), '.jpoker_pots0');
  equals($('.jpoker_chips_amount', pots_element).length, 10, '.jpoker_chips_amount');
  for (i = 0; i < 10; i += 1) {
    var pot_element = $('.jpoker_pot' + i, pots_element);
    equals(pot_element.is(':hidden'), true, 'hidden .jpoker_pot' + i);
    equals($('.jpoker_chips_amount', pot_element).text(), '', 'empty .jpoker_chips_amount' + i);
  }
  start_and_cleanup();
});

test("jpoker.plugins.table: PacketSerial ", function () {
  expect(7);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  var packet = {
    type: 'PacketPokerBetLimit',
    game_id: game_id,
    min: 500,
    max: 20000,
    step: 100,
    call: 1000,
    allin: 4000,
    pot: 2000
  };
  table.handler(server, game_id, packet);
  var player_seat = 2;
  var player_name = 'username';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  table.handler(server, game_id, {
    type: 'PacketPokerSit',
    serial: player_serial,
    game_id: game_id
  });
  equals($("#player_seat" + player_seat + id).hasClass('jpoker_sit_out'), false, 'no class sitout');
  equals($("#fold" + id).is(':hidden'), true, 'fold interactor not visible');
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($("#fold" + id).is(':visible'), true, 'fold interactor visible');
  equals($("#jpokerSound " + jpoker.sound).attr("src").indexOf('hand') >= 0, true, 'sound in position');

  // table is destroyed and rebuilt from cached state
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  equals(server.tables[game_id].id, table_packet.id);
  equals($("#player_seat" + player_seat + id).hasClass('jpoker_sit_out'), false, 'no class sitout');
  equals($("#fold" + id).is(':visible'), false, 'fold interactor visible');

  jpoker.plugins.playerSelf.hide(id);

  cleanup();
});

test("jpoker.plugins.table: PacketPokerUserInfo", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var rebuy = jpoker.plugins.playerSelf.rebuy;
  jpoker.plugins.playerSelf.rebuy = function () {
    jpoker.plugins.playerSelf.rebuy = rebuy;
    ok(true, 'rebuy called');
  };
  server.handler(server, game_id, {
    'type': 'PacketPokerUserInfo',
    'game_id': game_id
  });
});

test("jpoker.plugins.table: callback.tourney_end", function () {
  expect(6);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  table.is_tourney = true;
  var tourney_serial = 42;
  table.tourney_serial = tourney_serial;

  var money = 1000;
  place.jpoker('table', 'url', game_id);
  equals(table.tourney_rank, undefined, 'tourney_rank undefined');
  table.handler(server, game_id, {
    'type': 'PacketPokerTourneyRank',
    'serial': tourney_serial,
    'game_id': game_id,
    'rank': 1,
    'players': 10,
    'money': money
  });
  equals(table.tourney_rank.rank, 1, 'tourney_rank.rank');
  equals(table.tourney_rank.players, 10, 'tourney_rank.players');
  equals(table.tourney_rank.money, money / 100.0, 'tourney_rank.money');

  var jpoker_table_callback_tourney_end = jpoker.plugins.table.callback.tourney_end;
  jpoker.plugins.table.callback.tourney_end = function (table) {
    jpoker.plugins.table.callback.tourney_end = jpoker_table_callback_tourney_end;
    equals(table.tourney_serial, tourney_serial, 'callback tourney_end called');
    equals($('#game_window' + id).length, 0, 'game window removed');
  };
  table.handler(server, game_id, {
    'type': 'PacketPokerTableDestroy',
    'game_id': game_id
  });
  cleanup();
});

test("jpoker.plugins.table: callback.tourney_end default", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];
  table.is_tourney = true;
  var tourney_serial = 42;
  table.tourney_serial = tourney_serial;

  place.jpoker('table', 'url', game_id);
  table.handler(server, game_id, {
    'type': 'PacketPokerTourneyRank',
    'serial': tourney_serial,
    'game_id': game_id,
    'rank': 1,
    'players': 10,
    'money': 1000
  });
  server.tourneyRowClick = function (server, packet) {
    equals(packet.name, '');
    equals(packet.game_id, tourney_serial);
  };
  table.handler(server, game_id, {
    'type': 'PacketPokerTableDestroy',
    'game_id': game_id
  });
});

test("jpoker.plugins.table: remove callbacks", function () {
  expect(4);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  table.callbacks.update = [];
  place.jpoker('table', 'url', game_id);
  equals(table.callbacks.update.length, 1, 'table updateCallback registered');
  equals(table.callbacks.reinit.length, 1, 'table reinitCallback registered');
  $("#" + id).remove();
  table.notifyUpdate({
    type: 'Packet'
  });
  equals(table.callbacks.update.length, 0, 'table updateCallback removed');
  table.notifyReinit({
    type: 'Packet'
  });
  equals(table.callbacks.reinit.length, 0, 'table reinitCallback removed');
});

if (TEST_POWERED_BY) {
  test("jpoker.plugins.table: powered_by", function () {
    expect(2);
    var packet = {
      "type": "PacketPokerTable",
      "id": 100,
      "name": "One",
      "percent_flop": 98,
      "betting_structure": "15-30-no-limit"
    };
    var server = jpoker.serverCreate({
      url: 'url'
    });
    server.tables[packet.id] = new jpoker.table(server, packet);
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;

    var game_id = 100;

    place.jpoker('table', 'url', game_id);

    var powered_by_element = $('#powered_by' + id);
    equals(powered_by_element.length, 1, 'table info');
    ok(powered_by_element.hasClass('jpoker_powered_by'), 'jpoker_powered_by class');
    cleanup();
  });
} // TEST_POWERED_BY
test("jpoker.plugins.table: display done callback", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var player_serial = 1;
  server.serial = player_serial; // pretend logged in
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  var display_done = jpoker.plugins.table.callback.display_done;
  jpoker.plugins.table.callback.display_done = function (element) {
    jpoker.plugins.table.callback.display_done = display_done;
    equals($(".jpoker_chat_input", element).length, 1);
  };
  place.jpoker('table', 'url', game_id);
  cleanup(id);
});

//
// player
//
test("jpoker.plugins.player: PacketPokerPlayerArrive", function () {
  expect(TEST_AVATAR ? 14 : 13);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  //
  // player arrives and is sitout
  //
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  equals(player.serial, player_serial, "player_serial");

  if (TEST_AVATAR) {
    var avatar = $("#player_seat2_avatar" + id);
    equals(avatar.hasClass('jpoker_avatar_default_3'), true, 'default avatar 3');
  }
  ok($('#player_seat2' + id).hasClass('jpoker_player_seat'), 'jpoker_seat');
  ok($('#player_seat2' + id).hasClass('jpoker_sit_out'), 'player is initialy sitout by default');
  ok($('#player_seat2' + id).hasClass('jpoker_player_seat2'), 'jpoker_seat2');
  ok($('#seat2' + id).hasClass('jpoker_seat'), 'jpoker_seat');
  ok($('#seat2' + id).hasClass('jpoker_seat2'), 'jpoker_seat2');

  ok($("#player_seat2_hole" + id).hasClass('jpoker_player_hole'), 'jpoker_player_hole');

  //
  // player arrives and is sit
  //
  player_serial++;
  player_seat++;
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id,
    sit_out: false,
    auto: false
  });
  player = server.tables[game_id].serial2player[player_serial];
  equals(player.serial, player_serial, "player_serial");

  ok($('#player_seat' + player_seat + id).hasClass('jpoker_player_seat' + player_seat), 'jpoker_seat' + player_seat);
  equals($('#player_seat' + player_seat + id).hasClass('jpoker_sit_out'), false, 'jpoker is sit because sit_out is false in player arrive packet');

  //
  // player arrives and is sit but also in auto mode
  //
  player_serial++;
  player_seat++;
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id,
    sit_out: false,
    auto: true
  });
  player = server.tables[game_id].serial2player[player_serial];
  equals(player.serial, player_serial, "player_serial");

  ok($('#player_seat' + player_seat + id).hasClass('jpoker_player_seat' + player_seat), 'jpoker_seat' + player_seat);
  ok($('#player_seat' + player_seat + id).hasClass('jpoker_sit_out'), 'jpoker is sitout because sit_out is false in player arrive packet but auto is also set meaning the user cannot act');

  start_and_cleanup();
});

test("jpoker.plugins.player: PacketPokerPlayerArrive code injection", function () {
  expect(0);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  jpoker.injection = function () {
    ok(false, 'injection');
  };
  var player_name = '<script>$.jpoker.injection()</script>';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  delete jpoker.injection;
  start_and_cleanup();
});

test("jpoker.plugins.player: sounds", function () {
  expect(10);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';
  var sound_player_arrive = jpoker.plugins.player.callback.sound.arrive;
  jpoker.plugins.player.callback.sound.arrive = function (server) {
    sound_player_arrive(server);
    equals($("#jpokerSound " + jpoker.sound).attr("src").indexOf('arrive') >= 0, true, 'sound arrive');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  var sound_player_self_in_position = jpoker.plugins.playerSelf.callback.sound.in_position;
  jpoker.plugins.playerSelf.callback.sound.in_position = function (server) {
    sound_player_self_in_position(server);
    equals($("#jpokerSound " + jpoker.sound).attr("src").indexOf('hand') >= 0, true, 'sound position');
  };
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 50,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  var sound_player_self_timeout_notice = jpoker.plugins.playerSelf.callback.sound.timeout_notice;
  jpoker.plugins.playerSelf.callback.sound.timeout_notice = function (server) {
    sound_player_self_timeout_notice(server);
    equals($("#jpokerSound " + jpoker.sound).attr("src").indexOf('notice') >= 0, true, 'sound timeout notice');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerTimeoutNotice',
    serial: player_serial,
    game_id: game_id
  });
  var sound_player_self_timeout_warning = jpoker.plugins.playerSelf.callback.sound.timeout_warning;
  jpoker.plugins.playerSelf.callback.sound.timeout_warning = function (server) {
    sound_player_self_timeout_warning(server);
    equals($("#jpokerSound " + jpoker.sound).attr("src").indexOf('warning') >= 0, true, 'sound timeout warning');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerTimeoutWarning',
    serial: player_serial,
    game_id: game_id
  });
  var sound_player_call = jpoker.plugins.player.callback.sound.call;
  jpoker.plugins.player.callback.sound.call = function (server) {
    sound_player_call(server);
    equals($("#jpokerSoundAction " + jpoker.sound).attr("src").indexOf('call') >= 0, true, 'sound call');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerCall',
    serial: player_serial,
    game_id: game_id
  });
  var sound_player_raise = jpoker.plugins.player.callback.sound.raise;
  jpoker.plugins.player.callback.sound.raise = function (server) {
    sound_player_raise(server);
    equals($("#jpokerSoundAction " + jpoker.sound).attr("src").indexOf('bet') >= 0, true, 'sound raise');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerRaise',
    serial: player_serial,
    game_id: game_id
  });
  var sound_player_check = jpoker.plugins.player.callback.sound.check;
  jpoker.plugins.player.callback.sound.check = function (server) {
    sound_player_check(server);
    equals($("#jpokerSoundAction " + jpoker.sound).attr("src").indexOf('check') >= 0, true, 'sound check');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerCheck',
    serial: player_serial,
    game_id: game_id
  });
  var sound_player_fold = jpoker.plugins.player.callback.sound.fold;
  jpoker.plugins.player.callback.sound.fold = function (server) {
    sound_player_fold(server);
    equals($("#jpokerSoundAction " + jpoker.sound).attr("src").indexOf('fold') >= 0, true, 'sound fold');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerFold',
    serial: player_serial,
    game_id: game_id
  });

  var sound_table_deal_card = jpoker.plugins.table.callback.sound.deal_card;
  jpoker.plugins.table.callback.sound.deal_card = function (server) {
    sound_table_deal_card(server);
    equals($("#jpokerSoundTable " + jpoker.sound).attr("src").indexOf('deal_card') >= 0, true, 'sound deal card');
  };
  var sound_player_deal_card = jpoker.plugins.player.callback.sound.deal_card;
  jpoker.plugins.player.callback.sound.deal_card = function (server) {
    sound_player_deal_card(server);
    equals($("#jpokerSoundTable " + jpoker.sound).attr("src").indexOf('deal_card') >= 0, true, 'sound deal card');
  };
  table.handler(server, game_id, {
    "serials": [player_serial],
    "length": 21,
    "game_id": game_id,
    "numberOfCards": 2,
    "serial": 0,
    "type": "PacketPokerDealCards"
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    cards: [],
    game_id: game_id
  }); // no sound
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    cards: [1, 2, 3],
    game_id: game_id
  });

  jpoker.plugins.player.callback.sound.arrive = sound_player_arrive;
  jpoker.plugins.playerSelf.callback.sound.in_position = sound_player_self_in_position;
  jpoker.plugins.playerSelf.callback.sound.timeout_notice = sound_player_self_timeout_notice;
  jpoker.plugins.playerSelf.callback.sound.timeout_warning = sound_player_self_timeout_warning;
  jpoker.plugins.player.callback.sound.call = sound_player_call;
  jpoker.plugins.player.callback.sound.raise = sound_player_raise;
  jpoker.plugins.player.callback.sound.check = sound_player_check;
  jpoker.plugins.player.callback.sound.fold = sound_player_fold;
  jpoker.plugins.table.callback.sound.deal_card = sound_table_deal_card;
  jpoker.plugins.player.callback.sound.deal_card = sound_player_deal_card;

  start_and_cleanup();
});

test("jpoker.plugins.player: sounds preferences", function () {
  expect(12);
  var server = jpoker.serverCreate({
    url: 'url'
  });

  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  function nosound() {
    $.each(["jpokerSoundAction", "jpokerSound", "jpokerSoundTable"], function () {
      equals($("#" + this).length, 1, this);
      equals($("#" + this + " " + jpoker.sound).length, 0, this + ' empty');
    });
  }
  nosound();
  server.preferences.sound = false;
  jpoker.plugins.table.callback.sound.deal_card(server);
  jpoker.plugins.player.callback.sound.arrive(server);
  jpoker.plugins.player.callback.sound.fold(server);
  jpoker.plugins.player.callback.sound.check(server);
  jpoker.plugins.player.callback.sound.call(server);
  jpoker.plugins.player.callback.sound.raise(server);
  jpoker.plugins.playerSelf.callback.sound.in_position(server);
  nosound();
});

test("jpoker.plugins.player: sounds soundCreate", function () {
  expect(6);
  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.preferences.sound = false;
  $('#main').append('<div id=\'sound_control\' />');
  jpoker.plugins.table.soundCreate('sound_control', server);
  $.each(["jpokerSoundAction", "jpokerSound", "jpokerSoundTable"], function () {
    equals($("#" + this).length, 1, this);
  });
  equals($('#sound_control.jpoker_sound_off').length, 1, 'sound off');
  $('#sound_control').click();
  equals(server.preferences.sound, true, 'preference sound on');
  equals($('#sound_control.jpoker_sound_off').length, 0, 'class sound on');
});

test("jpoker.plugins.player: animation", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  var money2bet = jpoker.plugins.player.callback.animation.money2bet;
  jpoker.plugins.player.callback.animation.money2bet = function (player, id) {
    money2bet(player, id);
    ok(true, 'money2bet animation');
  };
  table.handler(server, game_id, {
    "type": "PacketPokerChipsPlayer2Bet",
    "length": 15,
    "cookie": "",
    "game_id": game_id,
    "serial": player_serial,
    "chips": [10000, 2]
  });
  var player_deal_card = jpoker.plugins.player.callback.animation.deal_card;
  jpoker.plugins.player.callback.animation.deal_card = function (player, id, duration, callback) {
    player_deal_card(player, id);
    ok(true, 'player deal card animation');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [1, 2]
  });
  var table_deal_card = jpoker.plugins.table.callback.animation.deal_card;
  jpoker.plugins.table.callback.animation.deal_card = function (table, id, packet) {
    table_deal_card(table, id, packet);
    ok(true, 'board deal card animation');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: []
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4]
  });

  var bet2pot = jpoker.plugins.player.callback.animation.bet2pot;
  jpoker.plugins.player.callback.animation.bet2pot = function (player, id, packet) {
    bet2pot(player, id, packet);
    ok(true, 'player bet2pot animation');
  };

  table.handler(server, game_id, {
    type: 'PacketPokerChipsBet2Pot',
    pot: 0,
    game_id: game_id,
    serial: player_serial
  });

  var table_best_card = jpoker.plugins.table.callback.animation.best_card;
  jpoker.plugins.table.callback.animation.best_card = function (table, id, packet) {
    table_best_card(table, id, packet);
    ok(true, 'table best_card animation');
  };
  table.handler(server, game_id, {
    "besthand": 1,
    "hand": "Flush Queen high",
    "length": 47,
    "cookie": "",
    "board": [21, 30, 33, 36, 32],
    "bestcards": [36, 33, 32, 30, 26],
    "cards": [7, 26],
    "game_id": game_id,
    "serial": player_serial,
    "type": "PacketPokerBestCards",
    "side": ""
  });

  jpoker.plugins.player.callback.animation.money2bet = money2bet;
  jpoker.plugins.player.callback.animation.deal_card = player_deal_card;
  jpoker.plugins.table.callback.animation.deal_card = table_deal_card;
  jpoker.plugins.player.callback.animation.bet2pot = bet2pot;
  jpoker.plugins.table.callback.animation.best_card = table_best_card;

  var table_best_card_reset = jpoker.plugins.table.callback.animation.best_card_reset;
  jpoker.plugins.table.callback.animation.best_card_reset = function (table, id) {
    table_best_card_reset(table, id);
  };
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: []
  });

  jpoker.plugins.table.callback.animation.best_card_reset = table_best_card_reset;
  start_and_cleanup();
});

test("jpoker.plugins.player: animation deal_card", function () {
  expect(8);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });

  var player_deal_card = jpoker.plugins.player.callback.animation.deal_card;
  jpoker.plugins.player.callback.animation.deal_card = function (player, id, duration, callback) {
    var dealer = $('#dealer' + player.seat + id);
    var hole = $('#player_seat' + player.seat + '_hole' + id);
    var holeOffsetBefore = hole.getOffset();
    player_deal_card(player, id, 100, function () {
      equals(hole.getOffset().top, holeOffsetBefore.top, 'move to hole top');
      equals(hole.getOffset().left, holeOffsetBefore.left, 'move to hole left');
      equals(hole.css('opacity'), 1.0, 'opacity 1');
      var card = $("#card_seat" + player_seat + "0" + id);
      equals(card.hasClass('jpoker_card_3h'), false, 'card_3h class');
      callback.call(0);
      equals(card.hasClass('jpoker_card_3h'), true, 'card_3h class');
      jpoker.plugins.player.callback.animation.deal_card = player_deal_card;
      start_and_cleanup();
    });
    equals(Math.round(hole.getOffset().top + hole.height() / 2.0 - dealer.height() / 2.0), dealer.getOffset().top, 'move from dealer top');
    equals(Math.round(hole.getOffset().left + hole.width() / 2.0 - dealer.width() / 2.0), dealer.getOffset().left, 'move from dealer left');
    equals(hole.css('opacity'), 0.0, 'opacity 0');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [1, 2]
  });
});

test("jpoker.plugins.player: animation deal_card no dealer", function () {
  expect(6);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  // Because the following is not run, there is no dealer, which is the intended effect
  //        table.handler(server, game_id, { type: 'PacketPokerDealer', dealer: player_seat, game_id: game_id });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });

  var player_deal_card = jpoker.plugins.player.callback.animation.deal_card;
  jpoker.plugins.player.callback.animation.deal_card = function (player, id, duration, callback) {
    equals(table.dealer, -1, 'no dealer');
    var hole = $('#player_seat' + player.seat + '_hole' + id);
    var holeOffsetBefore = hole.getOffset();
    player_deal_card(player, id, 100, function () {
      equals(hole.getOffset().top, holeOffsetBefore.top, 'move to hole top');
      equals(hole.getOffset().left, holeOffsetBefore.left, 'move to hole left');
      equals(hole.css('opacity'), 1.0, 'opacity 1');
      var card = $("#card_seat" + player_seat + "0" + id);
      equals(card.hasClass('jpoker_card_3h'), false, 'card_3h class');
      callback.call(0);
      equals(card.hasClass('jpoker_card_3h'), true, 'card_3h class');
      jpoker.plugins.player.callback.animation.deal_card = player_deal_card;
    });
  };
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [1, 2]
  });
  cleanup();
});

test("jpoker.plugins.player: animation deal_card x2", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });

  var player_deal_card = jpoker.plugins.player.callback.animation.deal_card;
  var count = 0;
  jpoker.plugins.player.callback.animation.deal_card = function (player, id, element) {
    count += 1;
  };
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [1, 2]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [1, 2]
  });
  equals(count, 1, 'callback animation.deal_card should not be called if cards not changed');
  table.handler(server, game_id, {
    type: 'PacketPokerStart',
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [1, 2]
  });
  equals(count, 2, 'callback animation.deal_card should be called if cards reseted');
  jpoker.plugins.player.callback.animation.deal_card = player_deal_card;
});

test("jpoker.plugins.player: animation deal_card board flop", function () {
  expect(18);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  var table_deal_card = jpoker.plugins.table.callback.animation.deal_card;
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: []
  });
  jpoker.plugins.table.callback.animation.deal_card = function (table, id, packet) {
    var dealer = $('#dealer' + table.dealer + id);
    var board0 = $('#board0' + id);
    var board1 = $('#board1' + id);
    var board2 = $('#board2' + id);
    var board0OffsetBefore = board0.getOffset();
    var board1OffsetBefore = board1.getOffset();
    var board2OffsetBefore = board2.getOffset();
    var count = 0;
    table_deal_card(table, id, packet, 100, function () {
      count += 1;
      if (count == 3) {
        equals(board0.getOffset().top, board0OffsetBefore.top, 'move to board0 top');
        equals(board0.getOffset().left, board0OffsetBefore.left, 'move to board0 left');
        equals(board0.css('opacity'), 1.0, 'opacity 1');
        equals(board1.getOffset().top, board1OffsetBefore.top, 'move to board1 top');
        equals(board1.getOffset().left, board1OffsetBefore.left, 'move to board1 left');
        equals(board1.css('opacity'), 1.0, 'opacity 1');
        equals(board2.getOffset().top, board2OffsetBefore.top, 'move to board2 top');
        equals(board2.getOffset().left, board2OffsetBefore.left, 'move to board2 left');
        equals(board2.css('opacity'), 1.0, 'opacity 1');
        jpoker.plugins.table.callback.animation.deal_card = table_deal_card;
        start_and_cleanup();
      }
    });
    equals(Math.round(board0.getOffset().top + board0.height() / 2.0 - dealer.height() / 2.0), dealer.getOffset().top, 'move from dealer top');
    equals(Math.round(board0.getOffset().left + board0.width() / 2.0 - dealer.width() / 2.0), dealer.getOffset().left, 'move from dealer left');
    equals(board0.css('opacity'), 0.0, 'opacity 0');
    equals(Math.round(board1.getOffset().top + board1.height() / 2.0 - dealer.height() / 2.0), dealer.getOffset().top, 'move from dealer top');
    equals(Math.round(board1.getOffset().left + board1.width() / 2.0 - dealer.width() / 2.0), dealer.getOffset().left, 'move from dealer left');
    equals(board1.css('opacity'), 0.0, 'opacity 0');
    equals(Math.round(board2.getOffset().top + board2.height() / 2.0 - dealer.height() / 2.0), dealer.getOffset().top, 'move from dealer top');
    equals(Math.round(board2.getOffset().left + board2.width() / 2.0 - dealer.width() / 2.0), dealer.getOffset().left, 'move from dealer left');
    equals(board2.css('opacity'), 0.0, 'opacity 0');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3]
  });
});

test("jpoker.plugins.player: animation deal_card board turn", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  var table_deal_card = jpoker.plugins.table.callback.animation.deal_card;
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: []
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3]
  });
  jpoker.plugins.table.callback.animation.deal_card = function (table, id, packet) {
    var dealer = $('#dealer' + table.dealer + id);
    var board3 = $('#board3' + id);
    var board3OffsetBefore = board3.getOffset();
    table_deal_card(table, id, packet, 100, function () {
      equals(board3.getOffset().top, board3OffsetBefore.top, 'move to board3 top');
      equals(board3.getOffset().left, board3OffsetBefore.left, 'move to board3 left');
      equals(board3.css('opacity'), 1.0, 'opacity 1');
      jpoker.plugins.table.callback.animation.deal_card = table_deal_card;
      start_and_cleanup();
    });
    var top = board3.getOffset().top + board3.height() / 2.0 - dealer.height() / 2.0;
    ok(Math.abs(top - dealer.getOffset().top) < 1, 'move from dealer top');
    var left = board3.getOffset().left + board3.width() / 2.0 - dealer.width() / 2.0;
    ok(Math.abs(left - dealer.getOffset().left) < 1, 'move from dealer left');
    equals(board3.css('opacity'), 0.0, 'opacity 0');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4]
  });
});

test("jpoker.plugins.player: animation deal_card board river", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  var table_deal_card = jpoker.plugins.table.callback.animation.deal_card;
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: []
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4]
  });
  jpoker.plugins.table.callback.animation.deal_card = function (table, id, packet) {
    var dealer = $('#dealer' + table.dealer + id);
    var board4 = $('#board4' + id);
    var board4OffsetBefore = board4.getOffset();
    table_deal_card(table, id, packet, 100, function () {
      equals(board4.getOffset().top, board4OffsetBefore.top, 'move to board4 top');
      equals(board4.getOffset().left, board4OffsetBefore.left, 'move to board4 left');
      equals(board4.css('opacity'), 1.0, 'opacity 1');
      jpoker.plugins.table.callback.animation.deal_card = table_deal_card;
      start_and_cleanup();
    });
    var top = board4.getOffset().top + board4.height() / 2.0 - dealer.height() / 2.0;
    ok(Math.abs(top - dealer.getOffset().top) < 1, 'move from dealer top');
    var left = board4.getOffset().left + board4.width() / 2.0 - dealer.width() / 2.0;
    ok(Math.abs(left - dealer.getOffset().left) < 1, 'move from dealer left');
    equals(board4.css('opacity'), 0.0, 'opacity 0');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4, 5]
  });
});

test("jpoker.plugins.player: animation best_card", function () {
  expect(30);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  var table_deal_card = jpoker.plugins.table.callback.animation.deal_card;
  jpoker.plugins.table.callback.animation.deal_card = function (table, id, packet) {};
  var player_deal_card = jpoker.plugins.player.callback.animation.deal_card;
  jpoker.plugins.player.callback.animation.deal_card = function (player, id, element) {};

  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [6, 7]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4, 5]
  });
  var table_best_card = jpoker.plugins.table.callback.animation.best_card;
  var board0 = $('#board0' + id);
  var board1 = $('#board1' + id);
  var board2 = $('#board2' + id);
  var board3 = $('#board3' + id);
  var board4 = $('#board4' + id);
  var board0Position = board0.getPosition();
  var board1Position = board1.getPosition();
  var board2Position = board2.getPosition();
  var board3Position = board3.getPosition();
  var board4Position = board4.getPosition();
  var card_seat = $('#card_seat' + player_seat + id);
  var cards = $('.jpoker_card', card_seat);
  var card0Position = cards.eq(0).getPosition();
  var card1Position = cards.eq(1).getPosition();
  var count = 0;
  jpoker.plugins.table.callback.animation.best_card = function (table, id, packet) {
    table_best_card(table, id, packet, 100, function () {
      count += 1;
      if (count == 7) {
        equals(board0.getPosition().top, board0Position.top, 'board0 position');
        equals(board0.css('opacity'), 0.5, 'board0 opacity');
        equals(board1.getPosition().top, board1Position.top + 8, 'board1 position');
        equals(board1.css('opacity'), 1.0, 'board1 opacity');
        equals(board2.getPosition().top, board2Position.top + 8, 'board2 position');
        equals(board2.css('opacity'), 1.0, 'board2 opacity');
        equals(board3.getPosition().top, board3Position.top + 8, 'board3 position');
        equals(board3.css('opacity'), 1.0, 'board3 opacity');
        equals(board4.getPosition().top, board4Position.top + 8, 'board4 position');
        equals(board4.css('opacity'), 1.0, 'board4 opacity');
        equals(cards.eq(0).getPosition().top, card0Position.top + 8, 'card0 position');
        equals(cards.eq(0).css('opacity'), 1.0, 'card0 opacity');
        equals(cards.eq(1).getPosition().top, card1Position.top, 'card1 position');
        equals(cards.eq(1).css('opacity'), 0.5, 'card1 opacity');
        equals($('.jpoker_best_card').length, 5, '5 best cards');
        table.handler(server, game_id, {
          type: 'PacketPokerBoardCards',
          game_id: game_id,
          cards: []
        });
      }
    });
  };
  table.handler(server, game_id, {
    "besthand": 1,
    "hand": "Flush Queen high",
    "length": 47,
    "cookie": "",
    "board": [1, 2, 3, 4, 5],
    "bestcards": [2, 3, 4, 5, 6],
    "cards": [6, 7],
    "game_id": game_id,
    "serial": player_serial,
    "type": "PacketPokerBestCards",
    "side": ""
  });
  var table_best_card_reset = jpoker.plugins.table.callback.animation.best_card_reset;
  jpoker.plugins.table.callback.animation.best_card_reset = function (table, id) {
    table_best_card_reset(table, id);
    equals($('.jpoker_best_card').length, 0, 'no best cards');
    equals(board0.getPosition().top, board0Position.top, 'board0 position');
    equals(board0.css('opacity'), 1.0, 'board0 opacity');
    equals(board1.getPosition().top, board1Position.top, 'board1 position');
    equals(board1.css('opacity'), 1.0, 'board1 opacity');
    equals(board2.getPosition().top, board2Position.top, 'board2 position');
    equals(board2.css('opacity'), 1.0, 'board2 opacity');
    equals(board3.getPosition().top, board3Position.top, 'board3 position');
    equals(board3.css('opacity'), 1.0, 'board3 opacity');
    equals(board4.getPosition().top, board4Position.top, 'board4 position');
    equals(board4.css('opacity'), 1.0, 'board4 opacity');
    equals(cards.eq(0).getPosition().top, card0Position.top, 'card0 position');
    equals(cards.eq(0).css('opacity'), 1.0, 'card0 opacity');
    equals(cards.eq(1).getPosition().top, card1Position.top, 'card1 position');
    equals(cards.eq(1).css('opacity'), 1.0, 'card1 opacity');
    jpoker.plugins.table.callback.animation.deal_card = table_deal_card;
    jpoker.plugins.player.callback.animation.deal_card = player_deal_card;
    jpoker.plugins.table.callback.animation.best_card = table_best_card;
    jpoker.plugins.table.callback.animation.best_card_reset = table_best_card_reset;
    start_and_cleanup();
  };
});

test("jpoker.plugins.player: animation best_card x2", function () {
  expect(13);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat + 1,
    serial: player_serial + 1,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  var table_deal_card = jpoker.plugins.table.callback.animation.deal_card;
  jpoker.plugins.table.callback.animation.deal_card = function (table, id, packet) {};
  var player_deal_card = jpoker.plugins.player.callback.animation.deal_card;
  jpoker.plugins.player.callback.animation.deal_card = function (player, id, element) {};

  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial,
    game_id: game_id,
    cards: [6, 7]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    serial: player_serial + 1,
    game_id: game_id,
    cards: [6, 7]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBoardCards',
    game_id: game_id,
    cards: [1, 2, 3, 4, 5]
  });
  var board0 = $('#board0' + id);
  var board1 = $('#board1' + id);
  var board2 = $('#board2' + id);
  var board3 = $('#board3' + id);
  var board4 = $('#board4' + id);
  var board0Position = board0.getPosition();
  var board1Position = board1.getPosition();
  var board2Position = board2.getPosition();
  var board3Position = board3.getPosition();
  var board4Position = board4.getPosition();
  var player0_card_seat = $('#card_seat' + player_seat + id);
  var player1_card_seat = $('#card_seat' + (player_seat + 1) + id);
  var player0_cards = $('.jpoker_card', player0_card_seat);
  var player1_cards = $('.jpoker_card', player1_card_seat);
  var player0card0Position = player0_cards.eq(0).getPosition();
  var player0card1Position = player0_cards.eq(1).getPosition();
  var player1card0Position = player1_cards.eq(0).getPosition();
  var player1card1Position = player1_cards.eq(1).getPosition();
  var table_best_card = jpoker.plugins.table.callback.animation.best_card;
  var count = 0;
  jpoker.plugins.table.callback.animation.best_card = function (table, id, packet) {
    table_best_card(table, id, packet, 100, function () {
      count += 1;
      if (count == 7) {
        equals(board0.getPosition().top, board0Position.top, 'board0 position');
        equals(board1.getPosition().top, board1Position.top + 8, 'board1 position');
        equals(board2.getPosition().top, board2Position.top + 8, 'board2 position');
        equals(board3.getPosition().top, board3Position.top + 8, 'board3 position');
        equals(board4.getPosition().top, board4Position.top + 8, 'board4 position');
        equals(player0_cards.eq(0).getPosition().top, player0card0Position.top + 8, 'card0 position');
        equals(player0_cards.eq(1).getPosition().top, player0card1Position.top, 'card1 position');
        table.handler(server, game_id, {
          "besthand": 1,
          "hand": "Flush Queen high",
          "length": 47,
          "cookie": "",
          "board": [1, 2, 3, 4, 5],
          "bestcards": [2, 3, 4, 5, 6],
          "cards": [6, 7],
          "game_id": game_id,
          "serial": player_serial + 1,
          "type": "PacketPokerBestCards",
          "side": ""
        });
      } else if (count == 10) {
        equals(player1_cards.eq(0).getPosition().top, player1card0Position.top + 8, 'card0 position');
        equals(player1_cards.eq(1).getPosition().top, player1card1Position.top, 'card1 position');
        table.handler(server, game_id, {
          type: 'PacketPokerBoardCards',
          game_id: game_id,
          cards: []
        });
      }
    });
  };
  table.handler(server, game_id, {
    "besthand": 1,
    "hand": "Flush Queen high",
    "length": 47,
    "cookie": "",
    "board": [1, 2, 3, 4, 5],
    "bestcards": [2, 3, 4, 5, 6],
    "cards": [6, 7],
    "game_id": game_id,
    "serial": player_serial,
    "type": "PacketPokerBestCards",
    "side": ""
  });
  var table_best_card_reset = jpoker.plugins.table.callback.animation.best_card_reset;
  jpoker.plugins.table.callback.animation.best_card_reset = function (table, id) {
    table_best_card_reset(table, id);
    jpoker.plugins.table.callback.animation.deal_card = table_deal_card;
    jpoker.plugins.player.callback.animation.deal_card = player_deal_card;
    jpoker.plugins.table.callback.animation.best_card = table_best_card;
    jpoker.plugins.table.callback.animation.best_card_reset = table_best_card_reset;
    equals(player0_cards.eq(0).getPosition().top, player0card0Position.top, 'card0 position');
    equals(player0_cards.eq(1).getPosition().top, player0card1Position.top, 'card1 position');
    equals(player1_cards.eq(0).getPosition().top, player1card0Position.top, 'card0 position');
    equals(player1_cards.eq(1).getPosition().top, player1card1Position.top, 'card1 position');
    start_and_cleanup();
  };
});

test("jpoker.plugins.player: animation money2bet", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  var money2bet = jpoker.plugins.player.callback.animation.money2bet;
  jpoker.plugins.player.callback.animation.money2bet = function (player, id, duration, callback) {
    var bet = $('#player_seat' + player.seat + '_bet' + id);
    var bet_offset = bet.getOffset();
    var money = $('#player_seat' + player.seat + '_money' + id);
    var player_seat = $('#player_seat' + player_seat + id);
    equals(duration, undefined, 'duration should not be set');
    equals(callback, undefined, 'callback should not be set');
    money2bet(player, id, 100, function () {
      equals(bet.getOffset().top, bet_offset.top, 'chip should move to bet position top');
      equals(bet.getOffset().left, bet_offset.left, 'chip should move to bet position left');
      jpoker.plugins.player.callback.animation.money2bet = money2bet;
      start_and_cleanup();
    });
    equals(bet.getOffset().top, money.getOffset().top, 'chip should move from money position top');
    equals(bet.getOffset().left, money.getOffset().left, 'chip should move from money position left');
  };
  table.handler(server, game_id, {
    "type": "PacketPokerChipsPlayer2Bet",
    "length": 15,
    "cookie": "",
    "game_id": game_id,
    "serial": player_serial,
    "chips": [10000, 2]
  });
});

test("jpoker.plugins.player: animation bet2pot", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  var bet2pot = jpoker.plugins.player.callback.animation.bet2pot;
  jpoker.plugins.player.callback.animation.bet2pot = function (player, id, packet, duration, callback) {
    var pot_offset = $('.jpoker_pot' + packet.pot).getOffset();
    var bet2pot_animation_element;
    equals(duration, undefined, 'duration should not be set');
    equals(callback, undefined, 'callback should not be set');
    bet2pot(player, id, packet, 100, function (callback) {
      equals(bet2pot_animation_element.getOffset().top, pot_offset.top, 'chip should move to pot position top');
      equals(bet2pot_animation_element.getOffset().left, pot_offset.left, 'chip should move to pot position left');
      jpoker.plugins.player.callback.animation.bet2pot = bet2pot;
      callback();
      equals($('.jpoker_bet2pot_animation').length, 0, 'jpoker_bet2pot_animation removed');
      start_and_cleanup();
    });
    bet2pot_animation_element = $('.jpoker_bet2pot_animation');
    equals(bet2pot_animation_element.length, 1, 'jpoker_bet2pot_animation');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerChipsBet2Pot',
    pot: 0,
    game_id: game_id,
    serial: player_serial
  });
});

test("jpoker.plugins.player: animation pot2money", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPotChips',
    bet: [1, 20000],
    index: 0,
    game_id: game_id
  });
  var pot2money = jpoker.plugins.player.callback.animation.pot2money;
  jpoker.plugins.player.callback.animation.pot2money = function (player, id, packet, duration, callback) {
    var money_offset = $('#player_seat' + player.seat + '_money' + id).getOffset();
    var pot2money_animation_element;
    equals(duration, undefined, 'duration should not be set');
    equals(callback, undefined, 'callback should not be set');
    pot2money(player, id, packet, 100, function (callback) {
      equals(pot2money_animation_element.getOffset().top, money_offset.top, 'chip should move to money position top');
      equals(pot2money_animation_element.getOffset().left, money_offset.left, 'chip should move to money position left');
      jpoker.plugins.player.callback.animation.pot2money = pot2money;
      callback();
      equals($('.jpoker_pot2money_animation').length, 0, 'jpoker_pot2money_animation removed');
      start_and_cleanup();
    });
    pot2money_animation_element = $('.jpoker_pot2money_animation');
    equals(pot2money_animation_element.length, 1, 'jpoker_pot2money_animation');
  };
  table.handler(server, game_id, {
    "type": "PacketPokerChipsPot2Player",
    "pot": 0,
    "length": 21,
    "reason": "win",
    "game_id": game_id,
    "serial": player_serial,
    "chips": [100, 8, 200, 5, 500, 2]
  });

});

test("jpoker.plugins.player: animation pot2money 2x players same pot", function () {
  expect(9);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var player_name = 'dummy';

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    name: player_name,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat + 1,
    serial: player_serial + 1,
    name: player_name,
    game_id: game_id
  });
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerPotChips',
    bet: [1, 20000],
    index: 0,
    game_id: game_id
  });

  var count = 0;
  var pot2money = jpoker.plugins.player.callback.animation.pot2money;

  var player1_seat = player_seat;
  var player2_seat = player_seat + 1;
  var money_offset = {
    2: $('#player_seat' + player1_seat + '_money' + id).getOffset(),
    3: $('#player_seat' + player2_seat + '_money' + id).getOffset()
  };
  var pots = $('#pots' + id);
  var pot_offset = {
    2: $('.jpoker_pot0').getOffset(),
    3: $('.jpoker_pot0').getOffset()
  };
  var pot2money_animation_element = $('.jpoker_pot2money_animation');
  equals(pot2money_animation_element.length, 0, 'no .jpoker_pot2money_animation');

  jpoker.plugins.player.callback.animation.pot2money = function (player, id, packet, duration, callback, hook) {
    pot2money(player, id, packet, 100, function (remove_chip, chip) {
      count += 1;
      equals(chip.getOffset().top, money_offset[player.seat].top, 'chip should move to money position top');
      equals(chip.getOffset().left, money_offset[player.seat].left, 'chip should move to money position left');
      remove_chip();
      if (count == 2) {
        jpoker.plugins.player.callback.animation.pot2money = pot2money;
        start_and_cleanup();
      }
    }, function (chip) {
      equals(chip.getOffset().top, pot_offset[player.seat].top, 'chip should move from pot position top');
      equals(chip.getOffset().left, pot_offset[player.seat].left, 'chip should move from pot position left');
    });
  };

  table.handler(server, game_id, {
    "type": "PacketPokerChipsPot2Player",
    "pot": 0,
    "length": 21,
    "reason": "win",
    "game_id": game_id,
    "serial": player_serial,
    "chips": [100, 8, 200, 5, 500, 2]
  });
  table.handler(server, game_id, {
    "type": "PacketPokerChipsPot2Player",
    "pot": 0,
    "length": 21,
    "reason": "win",
    "game_id": game_id,
    "serial": player_serial + 1,
    "chips": [100, 8, 200, 5, 500, 2]
  });


});

if (TEST_AVATAR) {
  test("jpoker.plugins.player: avatar", function () {
    expect(1);
    stop();

    var server = jpoker.serverCreate({
      url: 'url',
      urls: {
        avatar: 'http://avatar-server/'
      }
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);
    var player_serial = 1;
    server.serial = player_serial;
    var player_seat = 2;
    var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
    jpoker.plugins.muck.sendAutoMuck = function () {};
    server.ajax = function (options) {
      options.success('data', 'status');
    };
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: player_seat,
      serial: player_serial,
      game_id: game_id
    });
    ok($("#player_seat2_avatar" + id + " img").attr("src").indexOf('/1') >= 0, 'avatar');
    jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
    start_and_cleanup();
  });

  test("jpoker.plugins.player: avatar", function () {
    expect(1);
    stop();

    var server = jpoker.serverCreate({
      url: 'url',
      urls: {
        avatar: 'http://avatar-server/'
      }
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);
    var player_serial = 1;
    server.serial = player_serial;
    var player_seat = 2;
    var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
    jpoker.plugins.muck.sendAutoMuck = function () {};
    server.ajax = function (options) {
      ok(false, 'ajax not called');
    };
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: player_seat,
      serial: player_serial,
      game_id: game_id,
      url: 'http://host/customavatar.png'
    });
    ok($("#player_seat2_avatar" + id + " img").attr("src").indexOf('http://host/customavatar.png') >= 0, 'avatar');
    jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
    start_and_cleanup();
  });

  test("jpoker.plugins.player: avatar race condition", function () {
    expect(3);
    stop();

    var server = jpoker.serverCreate({
      url: 'url',
      urls: {
        avatar: 'http://avatar-server/'
      }
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);
    var player_serial = 1;
    server.serial = player_serial;
    var player_seat = 2;
    var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
    jpoker.plugins.muck.sendAutoMuck = function () {};
    var ajax_success = [];
    server.ajax = function (options) {
      ajax_success.push(options.success);
    };
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      name: "player1",
      seat: player_seat,
      serial: player_serial,
      game_id: game_id
    });
    var player2_name = "player2";
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      name: player2_name,
      seat: player_seat + 1,
      serial: player_serial + 1,
      game_id: game_id
    });

    ajax_success[0]('data', 'status');
    ajax_success[1]('data', 'status');
    ok($("#player_seat2_avatar" + id + " img").attr("src").indexOf('/1') >= 0, 'avatar');
    ok($("#player_seat3_avatar" + id + " img").attr('src').indexOf('/2') >= 0, 'avatar 2');
    equals($("#player_seat3_avatar" + id + " img").attr('alt'), player2_name, 'avatar 2 alt');

    jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
    start_and_cleanup();
  });
} // TEST_AVATAR
test("jpoker.plugins.player: seat hover", function () {
  expect(4);
  stop();

  var server = jpoker.serverCreate({
    url: 'url',
    urls: {
      avatar: 'http://avatar-server/'
    }
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
  jpoker.plugins.muck.sendAutoMuck = function () {};
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var seat_hover_enter = jpoker.plugins.player.callback.seat_hover_enter;
  jpoker.plugins.player.callback.seat_hover_enter = function (player, jpoker_id) {
    equals(player.serial, player_serial, 'seat hover enter serial');
    equals(jpoker_id, id, 'seat hover enter id');
  };
  $("#player_seat2" + id).trigger('mouseenter');
  jpoker.plugins.player.callback.seat_hover_enter = seat_hover_enter;
  var seat_hover_leave = jpoker.plugins.player.callback.seat_hover_leave;
  jpoker.plugins.player.callback.seat_hover_leave = function (player, jpoker_id) {
    equals(player.serial, player_serial, 'seat hover leave serial');
    equals(jpoker_id, id, 'seat hover leave id');
  };
  $("#player_seat2" + id).trigger('mouseleave');
  jpoker.plugins.player.callback.seat_hover_leave = seat_hover_leave;
  jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
  start_and_cleanup();
});

test("jpoker.plugins.player: seat click", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url',
    urls: {
      avatar: 'http://avatar-server/'
    }
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
  jpoker.plugins.muck.sendAutoMuck = function () {};
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var seat_click = jpoker.plugins.player.callback.seat_click;
  jpoker.plugins.player.callback.seat_click = function (player, jpoker_id) {
    equals(player.serial, player_serial, 'seat click serial');
    equals(jpoker_id, id, 'seat click id');
  };
  $("#player_seat2" + id).click();
  jpoker.plugins.player.callback.seat_click = seat_click;
  jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
  start_and_cleanup();
});

test("jpoker.plugins.player: seat hover default", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url',
    urls: {
      avatar: 'http://avatar-server/'
    }
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
  jpoker.plugins.muck.sendAutoMuck = function () {};
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];

  var seat_element = $('#player_seat2' + id);
  jpoker.plugins.player.callback.seat_hover_enter(player, id);
  equals(seat_element.hasClass('jpoker_seat_hover'), true, 'jpoker_seat_hover');
  jpoker.plugins.player.callback.seat_hover_leave(player, id);
  equals(seat_element.hasClass('jpoker_seat_hover'), false, 'no jpoker_seat_hover');

  jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
  start_and_cleanup();
});

if (TEST_RANK) {
  test("jpoker.plugins.player: rank and level", function () {
    expect(16);
    stop();

    var server = jpoker.serverCreate({
      url: 'url',
      urls: {
        avatar: 'http://avatar-server/'
      }
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);
    var player_serial = 1;
    server.serial = player_serial;
    var player_seat = 2;
    var send_auto_muck = jpoker.plugins.muck.sendAutoMuck;
    jpoker.plugins.muck.sendAutoMuck = function () {
      jpoker.plugins.muck.sendAutoMuck = send_auto_muck;
    };
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: player_seat,
      serial: player_serial,
      game_id: game_id
    });
    var player = table.serial2player[player_serial];
    var element = $("#player_seat2_stats" + id);
    var seat_element = $("#player_seat2" + id);
    ok(element.hasClass('jpoker_player_stats'), 'player stats seat class');
    ok(element.hasClass('jpoker_ptable_player_seat2_stats'), 'player stats seat class');
    equals(element.html(), '', 'no stats');
    server.handler(server, 0, {
      type: 'PacketPokerPlayerStats',
      serial: player_serial,
      rank: undefined,
      percentile: undefined
    });
    equals($('.jpoker_player_rank', element).length, 0, 'player rank');
    equals($('.jpoker_player_level', element).length, 0, 'player level');
    server.handler(server, 0, {
      type: 'PacketPokerPlayerStats',
      serial: player_serial,
      rank: 1,
      percentile: 0
    });
    equals($('.jpoker_player_rank', element).length, 1, 'player rank');
    equals($('.jpoker_player_level', element).length, 1, 'player level');
    equals($('.jpoker_player_rank', element).html(), 1, 'player rank 100');
    ok($('.jpoker_player_level', element).hasClass('jpoker_player_level_junior'), 'player level junior');
    ok(seat_element.hasClass('jpoker_player_level_junior'), 'player level junior');
    server.handler(server, 0, {
      type: 'PacketPokerPlayerStats',
      serial: player_serial,
      rank: 1,
      percentile: 1
    });
    ok($('.jpoker_player_level', element).hasClass('jpoker_player_level_pro'), 'player level pro');
    ok(seat_element.hasClass('jpoker_player_level_pro'), 'player level pro');
    server.handler(server, 0, {
      type: 'PacketPokerPlayerStats',
      serial: player_serial,
      rank: 1,
      percentile: 2
    });
    ok($('.jpoker_player_level', element).hasClass('jpoker_player_level_expert'), 'player level expert');
    ok(seat_element.hasClass('jpoker_player_level_expert'), 'player level expert');
    server.handler(server, 0, {
      type: 'PacketPokerPlayerStats',
      serial: player_serial,
      rank: 1,
      percentile: 3
    });
    ok($('.jpoker_player_level', element).hasClass('jpoker_player_level_master'), 'player level master');
    ok(seat_element.hasClass('jpoker_player_level_master'), 'player level master');
    start_and_cleanup();
  });
} // TEST_RANK
if (TEST_RANK) {
  test("jpoker.plugins.player: rejoin", function () {
    expect(6);

    var server = jpoker.serverCreate({
      url: 'url'
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);

    var player_name = 'username';
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: 1,
      serial: 11,
      game_id: game_id,
      name: player_name
    });
    equals($(".jpoker_timeout_progress", place).length, 1, 'timeout_progress added');
    equals($(".jpoker_player_stats", place).length, 1, 'player_stats added');
    equals($(".jpoker_player_sidepot", place).length, 1, 'player_sidepot added');
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: 1,
      serial: 12,
      game_id: game_id,
      name: player_name
    });
    equals($(".jpoker_timeout_progress", place).length, 1, 'timeout_progress x1');
    equals($(".jpoker_player_stats", place).length, 1, 'player_stats x1');
    equals($(".jpoker_player_sidepot", place).length, 1, 'player_sidepot x1');
  });
} else { // TEST_RANK
  test("jpoker.plugins.player: rejoin", function () {
    expect(2);

    var server = jpoker.serverCreate({
      url: 'url'
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);

    var player_name = 'username';
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: 1,
      serial: 11,
      game_id: game_id,
      name: player_name
    });
    equals($(".jpoker_timeout_progress", place).length, 1, 'timeout_progress added');
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: 1,
      serial: 12,
      game_id: game_id,
      name: player_name
    });
    equals($(".jpoker_timeout_progress", place).length, 1, 'timeout_progress x1');
  });
} // TEST_RANK
test("jpoker.plugins.player: PacketPokerPlayerCards", function () {
  expect(8);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerDealer',
    dealer: player_seat,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  equals(player.serial, player_serial, "player_serial");

  var card = $("#card_seat" + player_seat + "0" + id);
  var card_value = 1;
  equals(card.size(), 1, "seat 2, card 0 DOM element");
  equals(player.cards[0], null, "player card empty");
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    cards: [card_value],
    serial: player_serial,
    game_id: game_id
  });
  equals(card.hasClass('jpoker_card_3h'), false, 'card_3h class not yet (animate)'); // because it is set after the animation is complete and this test is done in the animation related test. Here we just assert that the change is no happening right away
  equals(player.cards[0], card_value, "card in slot 0");
  var seat_element = $('#seat' + player_seat + id);
  equals(seat_element.hasClass('jpoker_player_dealt'), true, '.jpoker_player_dealt class');

  table.handler(server, game_id, {
    type: 'PacketPokerFold',
    serial: player_serial,
    game_id: game_id
  });
  equals(seat_element.hasClass('jpoker_player_dealt'), false, 'no .jpoker_player_dealt class');

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerCards',
    cards: [card_value],
    serial: player_serial,
    game_id: game_id
  });
  table.handler(server, game_id, {
    type: 'PacketPokerStart',
    game_id: game_id
  });
  equals(seat_element.hasClass('jpoker_player_dealt'), false, 'no .jpoker_player_dealt class');

  start_and_cleanup();
});

if (TEST_ACTION) {
  test("jpoker.plugins.player: PacketPokerPlayerCall/Fold/Raise/Check/Start", function () {
    expect(8);
    stop();

    var server = jpoker.serverCreate({
      url: 'url'
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);
    var player_serial = 1;
    var player_seat = 2;
    server.tables[game_id].handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      seat: player_seat,
      serial: player_serial,
      game_id: game_id
    });
    var player = server.tables[game_id].serial2player[player_serial];
    var player_action_element = $('#player_seat' + player.seat + '_action' + id);
    equals(player_action_element.length, 1, 'player action');
    equals(player_action_element.hasClass('jpoker_action'), true, 'player action class');

    table.handler(server, game_id, {
      type: 'PacketPokerCall',
      serial: player_serial,
      game_id: game_id
    });
    equals(player_action_element.html(), 'call');

    table.handler(server, game_id, {
      type: 'PacketPokerEndRound',
      serial: 0,
      game_id: game_id
    });
    equals(player_action_element.html(), '');

    table.handler(server, game_id, {
      type: 'PacketPokerFold',
      serial: player_serial,
      game_id: game_id
    });
    equals(player_action_element.html(), 'fold');

    table.handler(server, game_id, {
      type: 'PacketPokerRaise',
      serial: player_serial,
      game_id: game_id
    });
    equals(player_action_element.html(), 'raise');

    table.handler(server, game_id, {
      type: 'PacketPokerCheck',
      serial: player_serial,
      game_id: game_id
    });
    equals(player_action_element.html(), 'check');

    table.handler(server, game_id, {
      type: 'PacketPokerStart',
      serial: 0,
      game_id: game_id
    });
    equals(player_action_element.html(), '');

    start_and_cleanup();
  });
}

test("jpoker.plugins.player: allin", function () {
  expect(8);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  var player_seat = 2;
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  var player_element = $('#player_seat' + player.seat + id);
  equals(player.all_in, false, 'player.all_in should be false by default');
  equals(player_element.hasClass('jpoker_player_allin'), false, 'jpoker_player_allin class should not be set by default');

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 100,
    bet: 10,
    serial: player_serial,
    game_id: game_id
  });
  equals(player.all_in, false, 'player.all_in should be false if money > 0');
  equals(player_element.hasClass('jpoker_player_allin'), false, 'jpoker_player_allin class should not be set if money > 0');

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 90,
    serial: player_serial,
    game_id: game_id
  });
  equals(player.all_in, true, 'player.all_in should be true if money = 0 and bet > 0');
  equals(player_element.hasClass('jpoker_player_allin'), true, 'jpoker_player_allin class should not be set if money = 0 and bet > 0');

  table.handler(server, game_id, {
    type: 'PacketPokerStart',
    serial: 0,
    game_id: game_id
  });
  equals(player.all_in, false, 'player.all_in should be false after PacketPokerStart');
  equals(player_element.hasClass('jpoker_player_allin'), false, 'jpoker_player_allin class should not be set after PacketPokerStart');
  start_and_cleanup();
});


test("jpoker.plugins.player: PacketPokerPlayerChips", function () {
  expect(15);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  equals(player.serial, player_serial, "player_serial");

  var slots = ['bet', 'money'];
  for (var i = 0; i < slots.length; i++) {
    var chips = $("#player_seat" + player_seat + "_" + slots[i] + id);
    equals(chips.size(), 1, slots[i] + " DOM element");
    equals(chips.css('display'), 'none', slots[i] + " chips hidden");
    equals(player[slots[i]], 0, slots[i] + " chips");
    equals(player.state, 'buyin');
    var packet = {
      type: 'PacketPokerPlayerChips',
      money: 0,
      bet: 0,
      serial: player_serial,
      game_id: game_id
    };
    var amount = 101;
    packet[slots[i]] = amount;
    table.handler(server, game_id, packet);
    if (slots[i] == 'bet') {
      equals(player.state, 'buyin');
    } else {
      equals(player.state, 'playing');
    }
    equals(chips.css('display'), 'block', slots[i] + " chips visible");
    equals(chips.html().indexOf(amount / 100) >= 0, true, amount / 100 + " in html ");
  }

  start_and_cleanup();
});

test("jpoker.plugins.player: bet chips", function () {
  expect(7);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 1;
  server.serial = player_serial;
  var player_seat = 2;
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  equals(player.serial, player_serial, "player_serial");
  var bet_element = $('#player_seat' + player_seat + '_bet' + id);
  equals(bet_element.hasClass('jpoker_bet'), true, '.jpoker_bet');
  equals($('.jpoker_chips_image', bet_element).length, 1, '.jpoker_chips_image');
  equals($('.jpoker_chips_amount', bet_element).length, 1, '.jpoker_chips_amount');

  equals(bet_element.is(':hidden'), true, 'chips hidden');
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 100,
    serial: player_serial,
    game_id: game_id
  });
  equals(bet_element.is(':visible'), true, 'chips visible');
  equals($('.jpoker_chips_amount', bet_element).text().indexOf(1) >= 0, true, 'chips amount in text');
  start_and_cleanup();
});

test("jpoker.plugins.player: PokerSeat", function () {
  expect(6);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  equals($("#sit_seat0" + id).css('display'), 'block', "sit_seat0 visible");
  var sent = false;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerSeat');
    equals(packet.serial, player_serial);
    equals(packet.game_id, game_id);
    equals(packet.seat, 0);
    sent = true;
  };
  $("#sit_seat0" + id).click();
  equals(sent, true, "packet sent");
  cleanup(id);
});

test("jpoker.plugins.player: PokerSit/SitOut", function () {
  expect(16);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  equals($("#rebuy" + id).css('display'), 'none', "rebuy is not visible");
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  var player_seat = 2;
  var player_name = 'username';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.money = 100;
  //
  // sit
  //
  var sit = $("#player_seat2_name" + id);
  equals($("#rebuy" + id).css('display'), 'block', "rebuy is visible");
  equals(sit.html(), 'click to sit', 'click to sit (A)');
  var sent = false;
  server.sendPacket = function (packet) {
    if (packet.type == 'PacketPokerAutoBlindAnte') {
      return;
    }
    equals(packet.type, 'PacketPokerSit');
    equals(packet.game_id, game_id);
    equals(packet.serial, player_serial);
    sent = true;
  };
  sit.click();
  equals(sent, true, "packet sent");

  table.handler(server, game_id, {
    type: 'PacketPokerSit',
    serial: player_serial,
    game_id: game_id
  });
  equals($("#player_seat2" + id).hasClass('jpoker_sit_out'), false, 'no class sitout');
  equals(sit.html(), player_name);

  //
  // sit out
  //
  sent = false;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerSitOut');
    equals(packet.game_id, game_id);
    equals(packet.serial, player_serial);
    sent = true;
  };
  sit.click();

  table.handler(server, game_id, {
    type: 'PacketPokerSitOut',
    serial: player_serial,
    game_id: game_id
  });
  equals($("#player_seat2" + id).hasClass('jpoker_sit_out'), true, 'class sitout');
  equals(sit.html(), 'click to sit');

  //
  // sit when broke
  //
  player.money = 0;
  var called = false;
  dialog = jpoker.dialog;
  jpoker.dialog = function (message) {
    equals(message.indexOf('not enough') >= 0, true, message);
    called = true;
  };
  server.sendPacket = function () {};
  sit.click();
  jpoker.dialog = dialog;
  equals(called, true, "broke");

  cleanup(id);
});


test("jpoker.plugins.player: PokerSit/SitOut PacketPokerAutoFold", function () {
  expect(2);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  var player_seat = 2;
  var player_name = 'username';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.money = 100;
  //
  // sit
  //
  var sit = $("#player_seat2_name" + id);
  sit.click();
  table.handler(server, game_id, {
    type: 'PacketPokerSit',
    serial: player_serial,
    game_id: game_id
  });

  //
  // sit out
  //
  sit.click();
  table.handler(server, game_id, {
    type: 'PacketPokerAutoFold',
    serial: player_serial,
    game_id: game_id
  });
  equals($("#player_seat2" + id).hasClass('jpoker_sit_out'), true, 'class sitout');
  equals(sit.html(), 'click to sit');

  cleanup(id);
});

if (TEST_SIDE_POT) {
  test("jpoker.plugins.player: side_pot", function () {
    expect(8);

    var server = jpoker.serverCreate({
      url: 'url'
    });
    var place = $("#main");
    var id = 'jpoker' + jpoker.serial;
    var game_id = 100;

    var table_packet = {
      id: game_id
    };
    server.tables[game_id] = new jpoker.table(server, table_packet);
    var table = server.tables[game_id];

    place.jpoker('table', 'url', game_id);
    var player_serial = 43;
    server.handler(server, 0, {
      type: 'PacketSerial',
      serial: player_serial
    });
    var player_seat = 2;
    var player_name = 'username';
    table.handler(server, game_id, {
      type: 'PacketPokerPlayerArrive',
      name: player_name,
      seat: player_seat,
      serial: player_serial,
      game_id: game_id
    });
    var player = server.tables[game_id].serial2player[player_serial];
    player.money = 100;
    player.sit_out = false;
    var side_pot = $('#player_seat2_sidepot' + id);
    equals(side_pot.length, 1, 'side pot element');
    ok(side_pot.hasClass('jpoker_player_sidepot'), 'side pot class');
    ok(side_pot.hasClass('jpoker_ptable_player_seat2_sidepot'), 'side pot seat class');
    ok(side_pot.is(':hidden'), 'side pot hidden');

    player.money = 0;
    table.handler(server, game_id, {
      type: 'PacketPokerPotChips',
      game_id: game_id,
      index: 1,
      bet: [1, 100000]
    });
    equals(side_pot.html(), 'Pot 1: 1.0K');
    ok(side_pot.is(':visible'), 'side pot visible');
    table.handler(server, game_id, {
      type: 'PacketPokerChipsPotReset',
      game_id: game_id
    });
    equals(side_pot.html(), '');
    ok(side_pot.is(':hidden'), 'side pot hidden');
    cleanup(id);
  });
}

test("jpoker.plugins.player: PacketPokerStart", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  var player_seat = 2;
  var player_name = 'username';
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.money = 100;

  player.handler = function (server, game_id, packet) {
    equals(packet.serial, undefined, 'packet serial undefined');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerStart',
    game_id: game_id
  });
  var card = $("#card_seat" + player_seat + "0" + id);
  equals(card.is(':hidden'), true, 'card hidden');
  start_and_cleanup();
});

test("jpoker.plugins.player: player callback", function () {
  expect(6);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var id = 'jpoker' + jpoker.serial;
  var game_id = 100;

  var table_packet = {
    id: game_id
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  place.jpoker('table', 'url', game_id);
  var player_serial = 43;
  server.handler(server, 0, {
    type: 'PacketSerial',
    serial: player_serial
  });
  var player_seat = 2;
  var player_name = 'username';
  var jpoker_player_callback_player_arrive = jpoker.plugins.player.callback.player_arrive;
  jpoker.plugins.player.callback.player_arrive = function (element, serial) {
    equals(serial, player_serial, 'player serial');
    equals(element.length, undefined, 'not a jquery selector');
    equals($('.jpoker_name', element).length, 1, 'player element');
    jpoker.plugins.player.callback.player_arrive = jpoker_player_callback_player_arrive;
  };
  var jpoker_player_callback_display_done = jpoker.plugins.player.callback.display_done;
  jpoker.plugins.player.callback.display_done = function (element, player) {
    equals(player.serial, player_serial, 'player serial');
    equals(element.length, undefined, 'not a jquery selector');
    equals($('.jpoker_name', element).length, 1, 'player element');
    jpoker.plugins.player.callback.display_done = jpoker_player_callback_display_done;
    start_and_cleanup();
  };

  table.handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    name: player_name,
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
});

function _SelfPlayer(game_id, player_serial) {
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");

  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);
  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  equals(player.serial, player_serial, "player_serial");
  // player money
  var money = 500;
  var in_game = 44;
  var points = 45;
  var currency_key = 'X' + currency_serial;
  server.userInfo = {
    money: {}
  };
  server.userInfo.money[currency_key] = [money * 100, in_game * 100, points];
}

function _SelfPlayerSit(game_id, player_serial, money) {
  _SelfPlayer(game_id, player_serial);
  // buy in
  var Z = jpoker.getServerTablePlayer('url', game_id, player_serial);
  var packet = {
    type: 'PacketPokerPlayerChips',
    money: money * 100,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  };
  Z.table.handler(Z.server, game_id, packet);
  equals(Z.player.money, money, 'player money');
  // sit
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSit',
    serial: player_serial,
    game_id: game_id
  });
  equals(Z.player.sit_out, false, 'player is sit');
}

test("jpoker.plugins.player: PacketPokerSelfInPosition/LostPosition", function () {
  expect(214);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);

  var Z = jpoker.getServerTablePlayer('url', game_id, player_serial);

  var visibility = function (selector, ids, comment) {
      for (var i = 0; i < ids.length; i++) {
        equals($('#' + ids[i] + id).is(selector), true, ids[i] + ' ' + selector + ' ' + comment);
      }
    };

  var interactors = function (active, passive, amount, comment) {
      var i;
      var all = active.concat(passive);
      visibility(':hidden', all, '(1) ' + comment);
      Z.table.handler(Z.server, game_id, {
        type: 'PacketPokerSelfInPosition',
        serial: player_serial,
        game_id: game_id
      });
      visibility(':visible', active, '(2) ' + comment);
      visibility(':hidden', passive, '(3) ' + comment);

      var click = function (id, suffix, amount) {
          var sent = false;
          var sendPacket = Z.server.sendPacket;
          Z.server.sendPacket = function (packet) {
            equals(packet.type, 'PacketPoker' + suffix, suffix + ' ' + comment);
            equals(packet.game_id, game_id, 'game_id for ' + suffix + ' ' + comment);
            equals(packet.serial, player_serial, 'serial for ' + suffix + ' ' + comment);
            if (amount) {
              equals(packet.amount, amount, 'amount for ' + suffix + ' ' + comment);
            }
            sent = true;
          };
          $(id).click();
          Z.server.sendPacket = sendPacket;
          equals(sent, true, suffix + ' packet sent ' + comment);
        };
      var keys = {
        'fold': 'Fold',
        'call': 'Call',
        'raise': 'Raise',
        'check': 'Check',
        'allin': 'Raise',
        'pot': 'Raise',
        'halfpot': 'Raise',
        'threequarterpot': 'Raise'
      };
      for (i = 0; i < active.length; i++) {
        click('#' + active[i] + id, keys[active[i]], amount[i]);
      }

      Z.table.handler(Z.server, game_id, {
        type: 'PacketPokerSelfLostPosition',
        serial: 333,
        game_id: game_id
      });
      visibility(':hidden', all, '(4) ' + comment);
    };

  Z.table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  interactors(['fold', 'call', 'raise', 'allin', 'pot', 'halfpot', 'threequarterpot'], ['check'], [undefined, undefined, 500, 4000, 2000, 1000, 1500], 'no check');

  Z.table.betLimit = {
    min: 10,
    max: 10,
    step: 1,
    call: 10,
    allin: 40,
    pot: 20
  };
  interactors(['fold', 'call', 'raise'], ['check', 'allin', 'pot', 'halfpot', 'threequarterpot'], [undefined, undefined, 0, undefined], 'limit');

  Z.table.betLimit = {
    min: 10,
    max: 100,
    step: 1,
    call: 10,
    allin: 40,
    pot: 200
  };
  interactors(['fold', 'call', 'raise', 'allin'], ['check', 'pot', 'halfpot', 'threequarterpot'], [undefined, undefined, 0, undefined], 'large pot');

  Z.table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 0,
    allin: 40,
    pot: 20
  };
  interactors(['fold', 'check', 'raise', 'allin', 'pot', 'halfpot', 'threequarterpot'], ['call'], [undefined, undefined, 500, 4000, 2000, 1000, 1500], 'can check');

  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  ok($("#game_window" + id).hasClass('jpoker_self_in_position'), 'jpoker_self_in_position is set');
  ok($("#game_window" + id).hasClass('jpoker_ptable'), 'jpoker_ptable');
  var raise = $('#raise_range' + id);
  equals($(".jpoker_raise_label", raise).html(), 'Raise', 'raise label');
  equals($(".jpoker_raise_min", raise).html(), Z.table.betLimit.min, 'min');
  equals($(".jpoker_raise_current", raise).html(), Z.table.betLimit.min, 'current');
  equals($(".jpoker_raise_max", raise).html(), Z.table.betLimit.max, 'max');
  equals(raise.is(':visible'), true, 'raise range visible');
  var raise_input = $('#raise_input' + id);
  equals(raise_input.is(':visible'), true, 'raise input visible');
  equals($('.jpoker_raise_input', raise_input).length, 1, 'raise input');
  var slider = $('.ui-slider-1', raise);
  equals($('.jpoker_raise_current', raise).attr("title"), 500, "title = raise amount");
  equals($('.jpoker_raise_input', raise_input).val(), 5, 'raise input value = raise amount');
  slider.slider("moveTo", 600, 0);
  equals(slider.slider("value", 0), 600, "slider value updated");
  equals($('.jpoker_raise_current', raise).attr("title"), 600, "title updated by slider");
  equals($('.jpoker_raise_input', raise_input).val(), 6, 'raise input updated by slider');
  $('.jpoker_raise_input', raise_input).val(7).change();
  equals(slider.slider("value", 0), 700, "slider value updated");
  equals($('.jpoker_raise_current', raise).attr("title"), 700, "title updated by input");
  //        $('.ui-slider-handle', raise).parent().triggerKeydown("38");
  // equals($(".jpokerRaiseCurrent", raise).attr('title'), Z.table.betLimit.min, 'value changed');
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSelfLostPosition',
    serial: 333,
    game_id: game_id
  });
  equals($("#game_window" + id).hasClass('jpoker_self_in_position'), false, 'jpoker_self_in_position not set');
  ok($("#game_window" + id).hasClass('jpoker_ptable'), 'jpoker_ptable');
  equals(raise.is(':hidden'), true, 'raise range hidden');
  equals($('#raise_input' + id).is(':hidden'), true, 'raise input hidden');

  Z.table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 60,
    allin: 40,
    pot: 20
  };
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($("#game_window" + id).hasClass('jpoker_self_in_position'), true, 'jpoker_self_in_position set');

  cleanup(id);
});

test("jpoker.plugins.player: slider decimal", function () {
  expect(7);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);

  var Z = jpoker.getServerTablePlayer('url', game_id, player_serial);
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerBetLimit',
    game_id: game_id,
    min: 100,
    max: 200,
    step: 1,
    call: 1,
    allin: 2,
    pot: 2
  });
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });

  var raise = $('#raise_range' + id);
  var raise_input = $('#raise_input' + id);
  var slider = $('.ui-slider-1', raise);
  slider.slider("moveTo", 20, 0);
  equals(slider.slider("value", 0), 20, "slider value updated");
  equals($('.jpoker_raise_current', raise).attr("title"), 20, "title updated by slider");
  equals($('.jpoker_raise_input', raise_input).val(), 0.2, 'raise input updated by slider');
  Z.server.sendPacket = function (packet) {
    equals(packet.amount, 20, 'raise 20 cents');
  };
  $('#raise' + id).click();
  cleanup(id);
});

test("jpoker.plugins.player: raise bug: default raise_current title should be in cents", function () {
  expect(7);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);

  var Z = jpoker.getServerTablePlayer('url', game_id, player_serial);
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerBetLimit',
    game_id: game_id,
    min: 100,
    max: 200,
    step: 1,
    call: 1,
    allin: 2,
    pot: 2
  });
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });

  var raise = $('#raise_range' + id);
  var raise_input = $('#raise_input' + id);
  equals($('.jpoker_raise_current', raise).attr("title"), 100, "title updated from template");
  Z.server.sendPacket = function (packet) {
    equals(packet.amount, 100, 'raise 100 cents');
  };
  var slider = $('.ui-slider-1', raise);
  $('#raise' + id).click();
  slider.slider("moveTo", 200, 0);
  equals($('.jpoker_raise_current', raise).attr("title"), 200, "title updated by slider");
  Z.server.sendPacket = function (packet) {
    equals(packet.amount, 200, 'raise 200 cents');
  };
  $('#raise' + id).click();
  cleanup(id);
});

test("jpoker.plugins.player: ignore non numeric raise entry", function () {
  expect(8);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);

  var Z = jpoker.getServerTablePlayer('url', game_id, player_serial);
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerBetLimit',
    game_id: game_id,
    min: 100,
    max: 200,
    step: 1,
    call: 1,
    allin: 2,
    pot: 2
  });
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });

  var raise = $('#raise_range' + id);
  var raise_input = $('#raise_input' + id);
  var slider = $('.ui-slider-1', raise);
  $('.jpoker_raise_input', raise_input).val('0.2').change();
  equals(slider.slider('value', 0), 20);
  $('.jpoker_raise_input', raise_input).val('0,3').change();
  equals(slider.slider('value', 0), 30);
  $('.jpoker_raise_input', raise_input).val('abc').change();
  equals(slider.slider('value', 0), 30);
  equals($('.jpoker_raise_input', raise_input).val(), '0.3');
  Z.server.sendPacket = function (packet) {
    equals(packet.amount, 30, 'raise 30 cents');
  };
  $('#raise' + id).click();
  cleanup(id);
});

test("jpoker.plugins.player: raise NaN should trigger an error", function () {
  expect(5);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);

  var Z = jpoker.getServerTablePlayer('url', game_id, player_serial);
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerBetLimit',
    game_id: game_id,
    min: 100,
    max: 200,
    step: 1,
    call: 1,
    allin: 2,
    pot: 2
  });
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });

  var raise = $('#raise_range' + id);
  var raise_input = $('#raise_input' + id);
  var sent = false;
  Z.server.sendPacket = function (packet) {
    sent = true;
  };
  var jpokerError = jpoker.error;
  var reason;
  jpoker.error = function (r) {
    reason = r;
  };

  $('.jpoker_raise_current', raise).attr('title', 'abc');
  $('#raise' + id).click();
  equals(sent, false, 'no packet sent');
  equals(reason, 'raise with NaN amount: abc', 'error');
  cleanup(id);
});

test("jpoker.plugins.player: rebuy if broke", function () {
  expect(8);
  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);
  var Z = jpoker.getServerTablePlayer('url', game_id, player_serial);
  equals(Z.player.broke, false, 'player is not broke');
  equals($("#jpokerRebuy").size(), 0, "rebuy dialog DOM element is not present");
  var packet = {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  };
  Z.table.handler(Z.server, game_id, packet);
  equals(Z.player.broke, true, 'player is broke');
  var rebuy = $("#jpokerRebuy");
  equals(rebuy.size(), 1, "rebuy dialog DOM element");
  equals(rebuy.parents().is(':visible'), true, 'dialog is visible');
});

test("jpoker.plugins.player: hover button", function () {
  expect(33);
  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);
  var element = $('#fold' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#check' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#call' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#raise' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#rebuy' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#sitout' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#sitin' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#muck_accept' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#muck_deny' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
  element = $('#quit' + id);
  equals(element.length, 1, 'element');
  element.trigger('mouseenter');
  equals(element.hasClass('hover'), true, 'hasClass hover');
  element.trigger('mouseleave');
  equals(element.hasClass('hover'), false, '!hasClass hover');
});

test("jpoker.plugins.player: text button", function () {
  expect(5);
  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);
  var element = $('#quit' + id);
  equals($('div a', element).html(), 'Exit', 'exit label');
  element = $('#rebuy' + id);
  equals($('div a', element).html(), 'Rebuy', 'rebuy label');
});

test("jpoker.plugins.player: jpoker_self class", function () {
  expect(6);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var Z;
  _SelfPlayer(game_id, player_serial);
  Z = jpoker.getServerTablePlayer('url', game_id, player_serial);
  ok($("#game_window" + id).hasClass('jpoker_self'), 'jpoker_self is set');
  ok($("#game_window" + id).hasClass('jpoker_ptable'), 'jpoker_ptable');
  ok($("#seat" + Z.player.seat + id).hasClass('jpoker_player_self'), 'jpoker_player_self is set');
  Z.table.handler(Z.server, game_id, {
    type: 'PacketPokerPlayerLeave',
    seat: 2,
    serial: player_serial,
    game_id: game_id
  });
  equals($("#game_window" + id).hasClass('jpoker_self'), false, 'jpoker_self is not set');
  equals($("#player_seat" + Z.player.seat + id).hasClass('jpoker_player_self'), false, 'jpoker_player_self is not set');
});

test("jpoker.plugins.player: rebuy", function () {
  expect(30);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  _SelfPlayer(game_id, player_serial);
  var server = jpoker.getServer('url');
  var player = jpoker.getPlayer('url', game_id, player_serial);
  var table = jpoker.getTable('url', game_id);

  // buy in
  var min = 10;
  var best = 50;
  var max = 100;
  var rebuy_min = 4;
  table.handler(server, game_id, {
    type: 'PacketPokerBuyInLimits',
    game_id: game_id,
    min: min * 100,
    max: max * 100,
    best: best * 100,
    rebuy_min: rebuy_min
  });
  equals(table.buyInLimits()[0], min, 'buy in min 2');

  // rebuy error
  equals(jpoker.plugins.playerSelf.rebuy('url', game_id, 33333), false, 'rebuy for player that is not sit');

  // buyin
  $("#rebuy" + id).click();
  var rebuy = $("#jpokerRebuy");
  equals(rebuy.size(), 1, "rebuy dialog DOM element");
  equals(rebuy.parents().is(':visible'), true, 'dialog visible');
  equals($(".jpoker_rebuy_min", rebuy).html(), min, 'min');
  equals($(".jpoker_rebuy_current", rebuy).html(), best, 'best');
  equals($(".jpoker_rebuy_max", rebuy).html(), max, 'max');
  equals($(".jpoker_auto_sitin label", rebuy).length, 1);
  equals($(".jpoker_auto_sitin input", rebuy).length, 1);
  equals($(".jpoker_auto_sitin input", rebuy).is(":checked"), true);
  var server_preferences_auto_sitin = server.preferences.auto_sitin;
  equals(server_preferences_auto_sitin, true);
  var sitin_clicked = function () {
      ok(true, 'sitin should be called because checked by default');
    };
  $("#sitin" + id).click(function () {
    sitin_clicked();
  });


  var sent;
  sent = false;
  sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    server.sendPacket = sendPacket;
    equals(packet.type, 'PacketPokerBuyIn');
    sent = true;
  };
  $("button", rebuy).click();
  equals(sent, true, 'BuyIn packet sent');
  equals(rebuy.parents().is(':hidden'), true, 'dialog hidden');

  player.buy_in_payed = true;
  sent = false;
  sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    server.sendPacket = sendPacket;
    equals(packet.type, 'PacketPokerRebuy');
    sent = true;
  };
  $("#rebuy" + id).hide().click();
  $("button", rebuy).click();
  equals(sent, true, 'Rebuy packet sent');
  equals(rebuy.parents().is(':hidden'), true, 'dialog hidden');

  $("#rebuy" + id).hide();
  jpoker.plugins.playerSelf.rebuy('url', game_id, player.serial, id);
  equals($("#rebuy" + id).is(":visible"), true, "rebuy should be shown if cancelled");

  // rebuy
  player.state = 'playing';
  $("#rebuy" + id).click();
  equals(rebuy.parents().is(':visible'), true, 'dialog visible');

  // value change
  var slider = $('.ui-slider-1', rebuy);
  $('.ui-slider-handle').css('width', 1); // there is no graphics, size is undefined
  slider.slider("moveTo", "-=1000000000");
  equals($(".jpoker_rebuy_current", rebuy).html(), min, 'min value');
  slider.slider("moveTo", "+=" + min * 100);
  equals($(".jpoker_rebuy_current", rebuy).html(), min * 2, '10 above min');
  $('.ui-slider-handle', slider).parent().triggerKeydown("37");
  equals($(".jpoker_rebuy_current", rebuy).html(), min + 10 - 0.01, 'value changed');
  $('.ui-slider-handle', slider).parent().triggerKeydown("37");
  equals($(".jpoker_rebuy_current", rebuy).html(), min + 10 - 0.02, 'value changed');

  $(".jpoker_auto_sitin input", rebuy)[0].checked = false;
  sitin_clicked = function () {
    ok(false, 'sitin should not be called if unchecked');
  };


  // click
  sent = false;
  sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    server.sendPacket = sendPacket;
    equals(packet.type, 'PacketPokerRebuy');
    sent = true;
  };
  $("button", rebuy).click();
  equals(sent, true, 'Rebuy packet sent');
  equals(rebuy.parents().is(':hidden'), true, 'dialog hidden');

  equals(server.preferences.auto_sitin, false, 'auto_sitin preferences should be updated');
  server.preferences.auto_sitin = server_preferences_auto_sitin;

  cleanup(id);
});

test("jpoker.plugins.player: rebuy bug: low buy in limits should not be truncated", function () {
  expect(6);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  _SelfPlayer(game_id, player_serial);
  var server = jpoker.getServer('url');
  var player = jpoker.getPlayer('url', game_id, player_serial);
  var table = jpoker.getTable('url', game_id);

  // buy in
  var min = 1.1;
  var best = 2.2;
  var max = 3.3;
  var rebuy_min = 100;
  table.handler(server, game_id, {
    type: 'PacketPokerBuyInLimits',
    game_id: game_id,
    min: min * 100,
    max: max * 100,
    best: best * 100,
    rebuy_min: rebuy_min
  });

  // buyin
  $("#rebuy" + id).click();
  var rebuy = $("#jpokerRebuy");
  equals($(".jpoker_rebuy_current", rebuy).html(), '2.2', 'best');
  equals($(".jpoker_rebuy_current", rebuy).attr('title'), '220', 'best');

  var sent;
  sent = false;
  sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    server.sendPacket = sendPacket;
    sent = true;
    equals(packet.amount, 220);
  };

  $("button", rebuy).click();
  equals(sent, true, 'BuyIn packet sent');
  equals(rebuy.parents().is(':hidden'), true, 'dialog hidden');

  cleanup(id);
});

test("jpoker.plugins.player: rebuy bug: high buy in limit should be formatted", function () {
  expect(6);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  _SelfPlayer(game_id, player_serial);
  var server = jpoker.getServer('url');
  var player = jpoker.getPlayer('url', game_id, player_serial);
  var table = jpoker.getTable('url', game_id);

  server.userInfo.money.X42 = [100000000, 100000000, 100000000];

  // buy in
  var min = 10000;
  var best = 20000;
  var max = 30000;
  var rebuy_min = 10000;
  table.handler(server, game_id, {
    type: 'PacketPokerBuyInLimits',
    game_id: game_id,
    min: min * 100,
    max: max * 100,
    best: best * 100,
    rebuy_min: rebuy_min
  });

  // buyin
  $("#rebuy" + id).click();
  var rebuy = $("#jpokerRebuy");
  equals($(".jpoker_rebuy_current", rebuy).html(), '20K', 'best');
  equals($(".jpoker_rebuy_current", rebuy).attr('title'), '2000000', 'best');

  var sent;
  sent = false;
  sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    server.sendPacket = sendPacket;
    sent = true;
    equals(packet.amount, 2000000);
  };

  $("button", rebuy).click();
  equals(sent, true, 'BuyIn packet sent');
  equals(rebuy.parents().is(':hidden'), true, 'dialog hidden');
  cleanup(id);
});

test("jpoker.plugins.player: rebuy NaN should trigger an error", function () {
  expect(3);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  _SelfPlayer(game_id, player_serial);
  var server = jpoker.getServer('url');
  var player = jpoker.getPlayer('url', game_id, player_serial);
  var table = jpoker.getTable('url', game_id);

  // buy in
  var min = 100;
  var best = 200;
  var max = 300;
  var rebuy_min = 100;
  table.handler(server, game_id, {
    type: 'PacketPokerBuyInLimits',
    game_id: game_id,
    min: min * 100,
    max: max * 100,
    best: best * 100,
    rebuy_min: rebuy_min
  });

  $("#rebuy" + id).click();
  var rebuy = $("#jpokerRebuy");
  $(".jpoker_rebuy_current", rebuy).attr('title', 'abc'); // NaN amount
  var sent;
  sent = false;
  server.sendPacket = function (packet) {
    sent = true;
  };

  var reason;
  var jpokerError = jpoker.error;
  jpoker.error = function (r) {
    jpoker.error = jpokerError;
    reason = r;
  };

  $("#jpokerRebuy button").click();

  equals(sent, false, 'BuyIn packet not sent');
  equals(reason, 'rebuy with NaN amount: abc', 'error');
  cleanup(id);
});

test("jpoker.plugins.player: rebuy if not enough money", function () {
  expect(2);

  var id = 'jpoker' + jpoker.serial;
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var game_id = 100;
  var currency_serial = 42;
  var player_serial = 12;
  var player_seat = 2;

  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  server.tables[game_id].buyIn.min = 1000;
  server.tables[game_id].buyIn.bankroll = 1000;

  place.jpoker('table', 'url', game_id);
  // player
  server.serial = player_serial;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var rebuy = $("#rebuy" + id);

  rebuy.click(function () {
    ok(true, 'rebuy clicked');
  });
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  });
  equals(rebuy.is(':visible'), true, 'rebuy shown');
  cleanup();
});

test("jpoker.plugins.player: no rebuy in tourney", function () {
  expect(1);

  var id = 'jpoker' + jpoker.serial;
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var game_id = 100;
  var currency_serial = 42;
  var player_serial = 12;
  var player_seat = 2;

  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  server.tables[game_id].buyIn.min = 1000;
  server.tables[game_id].buyIn.bankroll = 1000;
  server.tables[game_id].is_tourney = true;

  place.jpoker('table', 'url', game_id);
  // player
  server.serial = player_serial;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var rebuy = $("#rebuy" + id);

  rebuy.click(function () {
    ok(false, 'rebuy should not be clicked');
  });
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  });
  equals(rebuy.is(':hidden'), true, 'rebuy hidden');
  cleanup();
});

test("jpoker.plugins.player: no rebuy dialog if tablepicker", function () {
  expect(1);

  var id = 'jpoker' + jpoker.serial;
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var game_id = 100;
  var currency_serial = 42;
  var player_serial = 12;
  var player_seat = 2;

  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  server.tables[game_id].buyIn.min = 1000;
  server.tables[game_id].buyIn.bankroll = 1000;
  server.tables[game_id].reason = 'TablePicker';

  place.jpoker('table', 'url', game_id);
  // player
  server.serial = player_serial;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var rebuy = $("#rebuy" + id);

  rebuy.click(function () {
    ok(false, 'rebuy should not be clicked');
  });
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 0,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  });
  equals(rebuy.is(':visible'), true, 'rebuy visible');
  cleanup();
});

test("jpoker.plugins.player: no rebuy if money", function () {
  expect(3);

  var id = 'jpoker' + jpoker.serial;
  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var game_id = 100;
  var currency_serial = 42;
  var player_serial = 12;
  var player_seat = 2;

  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  server.tables[game_id].buyIn.min = 500;
  server.tables[game_id].buyIn.max = 1000;
  server.tables[game_id].buyIn.bankroll = 1000;
  server.tables[game_id].is_tourney = false;

  place.jpoker('table', 'url', game_id);
  // player
  server.serial = player_serial;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var rebuy = $("#rebuy" + id);

  rebuy.click(function () {
    ok(false, 'rebuy should not be clicked');
  });
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 10000,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  });
  equals(rebuy.is(':visible'), true, 'rebuy visible');
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 100000,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  });
  equals(rebuy.is(':visible'), false, 'rebuy hidden');
  server.tables[game_id].buyIn.bankroll = 100;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerChips',
    money: 10000,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  });
  equals(rebuy.is(':visible'), true, 'rebuy visible');
  cleanup();
});


test("jpoker.plugins.userInfo", function () {
  expect(23);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '8',
    'phone': '000-00000',
    'cookie': '',
    'serial': server.serial,
    'password': '',
    'addr_country': 'Yours',
    'name': 'testuser',
    'gender': 'Male',
    'birthdate': '01/01/1970',
    'addr_street2': 'Main street',
    'addr_zip': '5000',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': 'GhostTown',
    'addr_state': 'Alabama',
    'type': 'PacketPokerPersonalInfo',
    'email': 'john@doe.com'
  };

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(PERSONAL_INFO_PACKET) + " ]",

    handle: function (packet) {}
  };
  ActiveXObject.prototype.server = new PokerServer();

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  equals('update' in server.callbacks, false, 'no update registered');
  var display_done = jpoker.plugins.userInfo.callback.display_done;
  jpoker.plugins.userInfo.callback.display_done = function (element) {
    jpoker.plugins.userInfo.callback.display_done = display_done;
    equals($(".jpoker_user_info", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('userInfo', 'url');
  equals(server.callbacks.update.length, 1, 'userInfo update registered');
  equals($('.jpoker_user_info').length, 1, 'user info div');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPersonalInfo') {
        equals($('.jpoker_user_info_name', element).text(), 'testuser');
        equals($('input[name=password]', element).val(), '');
        equals($('input[name=password]', element).attr('type'), 'password');
        equals($('input[name=password_confirmation]', element).val(), '');
        equals($('input[name=password_confirmation]', element).attr('type'), 'password');
        equals($('input[name=email]', element).val(), 'john@doe.com');
        equals($('input[name=phone]', element).val(), '000-00000');
        equals($('input[name=firstname]', element).val(), 'John');
        equals($('input[name=lastname]', element).val(), 'Doe');
        equals($('input[name=addr_street]', element).val(), '8');
        equals($('input[name=addr_street2]', element).val(), 'Main street');
        equals($('input[name=addr_zip]', element).val(), '5000');
        equals($('input[name=addr_town]', element).val(), 'GhostTown');
        equals($('input[name=addr_state]', element).val(), 'Alabama');
        equals($('input[name=addr_country]', element).val(), 'Yours');
        equals($('input[name=gender]', element).val(), 'Male');
        equals($('input[name=birthdate]', element).val(), '01/01/1970');
        equals($('input[type=submit]').length, 2, 'user info submit');
        equals($('.jpoker_user_info_avatar_upload input[type=submit]').length, 1, 'user info avatar submit');
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.userInfo update", function () {
  expect(16);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': server.serial,
    'password': '',
    'addr_country': '',
    'name': 'testuser',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  server.getPersonalInfo = function () {
    server.registerUpdate(function (server, what, data) {
      var element = $('#' + id);
      if (element.length > 0) {
        equals($(".jpoker_user_info_feedback", element).text(), '');
        $('input[name=password]', element).val('testpassword');
        $('input[name=email]', element).val('alan@smith.com');
        $('input[name=phone]', element).val('000-00000');
        $('input[name=firstname]', element).val('Alan');
        $('input[name=lastname]', element).val('Smith');
        $('input[name=addr_street]', element).val('8');
        $('input[name=addr_street2]', element).val('Main street');
        $('input[name=addr_zip]', element).val('5000');
        $('input[name=addr_town]', element).val('GhostTown');
        $('input[name=addr_state]', element).val('Alabama');
        $('input[name=addr_country]', element).val('Yours');
        $('input[name=gender]', element).val('Male');
        $('input[name=birthdate]', element).val('01/01/1970');
        server.setPersonalInfo = function (info) {
          equals(info.password, 'testpassword');
          equals(info.email, 'alan@smith.com');
          equals(info.phone, '000-00000');
          equals(info.firstname, 'Alan');
          equals(info.lastname, 'Smith');
          equals(info.addr_street, '8');
          equals(info.addr_street2, 'Main street');
          equals(info.addr_zip, '5000');
          equals(info.addr_town, 'GhostTown');
          equals(info.addr_state, 'Alabama');
          equals(info.addr_country, 'Yours');
          equals(info.gender, 'Male');
          equals(info.birthdate, '01/01/1970');

          var packet = $.extend(PERSONAL_INFO_PACKET, info, {
            set_account: true
          });
          setTimeout(function () {
            server.registerUpdate(function (server, what, data) {
              var element = $('#' + id);
              if (element.length > 0) {
                equals($(".jpoker_user_info_feedback", element).text(), "Updated");
                setTimeout(function () {
                  $('#' + id).remove();
                  server.notifyUpdate({});
                  start_and_cleanup();
                }, 0);
                return false;
              }
            });
            server.notifyUpdate(packet);
          }, 0);
        };
        $('.jpoker_user_info_submit', element).click(function () {
          equals($(".jpoker_user_info_feedback", element).text(), "Updating...");
        }).click();
        return false;
      }
      return true;
    });
    server.notifyUpdate(PERSONAL_INFO_PACKET);
  };
  place.jpoker('userInfo', 'url');
});

test("jpoker.plugins.userInfo avatar upload succeed", function () {
  expect(8);
  stop();

  var server = jpoker.serverCreate({
    url: 'url',
    urls: {
      avatar: 'http://avatar-server/'
    }
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': server.serial,
    'password': '',
    'addr_country': '',
    'name': 'testuser',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');
  var ajaxform = $.fn.ajaxForm;
  var ajaxFormCallback;
  $.fn.ajaxForm = function (options) {
    ajaxFormCallback = function () {
      var element = $('#' + id);
      options.beforeSubmit();
      equals($(".jpoker_user_info_avatar_upload_feedback", element).text(), "Uploading...");
      $(".jpoker_user_info_avatar_preview", element).css("background-image", "none");
      options.success('<pre>image uploaded</pre>');
      equals($(".jpoker_user_info_avatar_upload_feedback", element).text(), "Uploaded");
      ok($(".jpoker_user_info_avatar_preview", element).css("background-image").indexOf("/42") >= 0, "avatar preview updated");
      setTimeout(function () {
        $('#' + id).remove();
        server.notifyUpdate({});
        start_and_cleanup();
      }, 0);
    };
  };
  server.getPersonalInfo = function () {
    server.registerUpdate(function (server, what, data) {
      var element = $('#' + id);
      if (element.length > 0) {
        ok($(".jpoker_user_info_avatar_upload", element).attr("action").indexOf('auth=') >= 0, 'session hash');
        ok($(".jpoker_user_info_avatar_upload", element).attr("action").indexOf(server.urls.upload) >= 0, 'upload url');
        equals($(".jpoker_user_info_avatar_upload_feedback", element).text(), '');
        equals($('.jpoker_user_info_avatar_preview').length, 1, 'user info avatar preview');
        ok($('.jpoker_user_info_avatar_preview').css('background-image').indexOf('42') >= 0, 'user info avatar preview');
        ajaxFormCallback();
        return false;
      }
    });
    server.notifyUpdate(PERSONAL_INFO_PACKET);
  };
  place.jpoker('userInfo', 'url');
});

test("jpoker.plugins.userInfo avatar upload failed", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url',
    urls: {
      avatar: 'http://avatar-server/'
    }
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': server.serial,
    'password': '',
    'addr_country': '',
    'name': 'testuser',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');
  var ajaxform = $.fn.ajaxForm;
  var ajaxFormCallback;
  $.fn.ajaxForm = function (options) {
    ajaxFormCallback = function () {
      var element = $('#' + id);
      options.beforeSubmit();
      var error_message = 'error';
      options.success(error_message);
      equals($(".jpoker_user_info_avatar_upload_feedback", element).text(), "Uploading failed: " + error_message);
      setTimeout(function () {
        $('#' + id).remove();
        server.notifyUpdate({});
        start_and_cleanup();
      }, 0);
    };
  };
  server.getPersonalInfo = function () {
    server.registerUpdate(function (server, what, data) {
      var element = $('#' + id);
      if (element.length > 0) {
        ajaxFormCallback();
        return false;
      }
    });
    server.notifyUpdate(PERSONAL_INFO_PACKET);
  };
  place.jpoker('userInfo', 'url');
});

test("jpoker.plugins.player: sitout", function () {
  expect(7);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);
  var server = jpoker.getServer('url');
  var player = jpoker.getPlayer('url', game_id, player_serial);

  // click on sitout, packet sent and sitout button hides
  var sitout = $("#sitout" + id);
  equals(sitout.is(':visible'), true, 'sitout button visible');
  var sent = false;
  sendPacket = server.sendPacket;
  server.sendPacket = function (packet) {
    if (packet.type == 'PacketPokerSitOut') {
      sent = true;
    }
  };
  sitout.click();
  equals(sent, true, 'sitout packet sent');
  equals(sitout.is(':hidden'), true, 'sitout button hidden');

  // when PokerSitOut packet arrives, sitout button is hidden again
  sitout.show();
  var table = server.tables[game_id];
  table.handler(server, game_id, {
    type: 'PacketPokerSitOut',
    game_id: game_id,
    serial: player_serial
  });
  equals(sitout.is(':hidden'), true, 'sitout button hidden');

  cleanup(id);
});

test("jpoker.plugins.player: sitout fold", function () {
  expect(18);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;
  _SelfPlayerSit(game_id, player_serial, money);
  var server = jpoker.getServer('url');
  var player = jpoker.getPlayer('url', game_id, player_serial);

  // click on sitout, packet sent and sitout button hides
  var sitout = $("#sitout_fold" + id);

  sitout.trigger('mouseenter');
  equals(sitout.hasClass('hover'), true, 'hasClass hover');
  sitout.trigger('mouseleave');
  equals(sitout.hasClass('hover'), false, '!hasClass hover');

  equals(sitout.length, 1);
  equals(sitout.is(':visible'), true, 'sitout button visible');
  var sent = false;
  sendPacket = server.sendPacket;
  var packets = [];
  server.sendPacket = function (packet) {
    packets.push(packet);
  };
  sitout.click();
  equals('sit_out_fold_sent' in player, true, 'sit_out_fold_sent has been added');
  equals(player.sit_out_fold_sent, true, 'sit_out_sent is true');
  equals(packets.length, 2);
  equals(packets[0].type, 'PacketPokerSitOut');
  equals(packets[1].type, 'PacketPokerFold');
  equals(sitout.is(':hidden'), true, 'sitout button hidden');

  var table = server.tables[game_id];
  table.betLimit = {
    min: 5000,
    max: 10000,
    step: 1000,
    call: 10000,
    allin: 40000,
    pot: 20000
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    game_id: game_id,
    serial: player_serial
  });
  equals(packets.length, 3);
  equals(packets[2].type, 'PacketPokerFold');

  // when PokerSitOut packet arrives, sitout button is hidden again
  sitout.show();
  table.handler(server, game_id, {
    type: 'PacketPokerSitOut',
    game_id: game_id,
    serial: player_serial
  });
  equals('sit_out_fold_sent' in player, false, 'SitOut => sit_out_fold_sent has been removed');
  equals(sitout.is(':hidden'), true, 'sitout button hidden');
  player.sit_out_fold_sent = true;
  table.handler(server, game_id, {
    type: 'PacketPokerSit',
    game_id: game_id,
    serial: player_serial
  });

  equals('sit_out_fold_sent' in player, false, 'Sit => sit_out_fold_sent has been removed');
  cleanup(id);
});


test("jpoker.plugins.player: sitin", function () {
  expect(8);

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");

  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  var table = server.tables[game_id];

  // table
  place.jpoker('table', 'url', game_id);
  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];

  var sitin = $("#sitin" + id);
  equals(sitin.is(':visible'), true, 'sitin button visible');

  // player money
  var money = 500;
  var in_game = 44;
  var points = 45;
  var currency_key = 'X' + currency_serial;
  server.userInfo = {
    money: {}
  };
  server.userInfo.money[currency_key] = [money * 100, in_game * 100, points];

  // buy in
  var packet = {
    type: 'PacketPokerPlayerChips',
    money: money * 100,
    bet: 0,
    serial: player_serial,
    game_id: game_id
  };
  table.handler(server, game_id, packet);

  // sit
  table.handler(server, game_id, {
    type: 'PacketPokerSit',
    serial: player_serial,
    game_id: game_id
  });
  equals(sitin.is(':hidden'), true, 'sitin button hidden');

  table.handler(server, game_id, {
    type: 'PacketPokerSitOut',
    game_id: game_id,
    serial: player_serial
  });

  equals(sitin.is(':visible'), true, 'sitin button visible');

  // click on sitin, packet sent and sitout button hides
  var packets = [];
  server.sendPacket = function (packet) {
    packets.push(packet);
  };
  sitin.click();
  equals(packets.length, 2, '2 packets sent');
  equals(packets[0].type, 'PacketPokerAutoBlindAnte', 'autoblind sent');
  equals(packets[1].type, 'PacketPokerSit', 'sit sent');
  equals(sitin.is(':hidden'), true, 'sitin button hidden');

  // when PokerSitIn packet arrives, sitout button is hidden again
  sitin.show();
  table.handler(server, game_id, {
    type: 'PacketPokerSit',
    game_id: game_id,
    serial: player_serial
  });
  equals(sitin.is(':hidden'), true, 'sitin button hidden');

  cleanup(id);
});

test("jpoker.plugins.playerSelf: create in position", function () {
  expect(1);

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var place = $("#main");
  var game_id = 100;
  var currency_serial = 42;
  var player_serial = 12;
  var player_seat = 2;

  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);
  server.tables[game_id].serial_in_position = player_serial;

  place.jpoker('table', 'url', game_id);
  // player
  server.serial = player_serial;
  var inPosition = jpoker.plugins.playerSelf.inPosition;
  jpoker.plugins.playerSelf.inPosition = function (player, id) {
    jpoker.plugins.playerSelf.inPosition = inPosition;
    equals(player, server.tables[game_id].serial2player[player_serial], "in position");
  };
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
});

test("jpoker.plugins.muck", function () {
  expect(29);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var sendAutoMuck = jpoker.plugins.muck.sendAutoMuck;
  jpoker.plugins.muck.sendAutoMuck = function () {
    ok(true, 'sendAutoMuck called');
  };

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.preferences.extend({
    auto_muck_win: false,
    auto_muck_lose: false
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);


  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];

  jpoker.plugins.muck.sendAutoMuck = sendAutoMuck;

  var table = server.tables[game_id];

  var muck_accept_element = $("#muck_accept" + id);
  equals(muck_accept_element.length, 1, '#muck_accept');
  ok(muck_accept_element.children(0).hasClass('jpoker_muck_accept'), 'jpoker_muck_accept');
  ok(muck_accept_element.children(0).hasClass('jpoker_muck'), 'jpoker_muck');

  var muck_deny_element = $("#muck_deny" + id);
  equals(muck_deny_element.length, 1, '#muck_deny');
  ok(muck_deny_element.children(0).hasClass('jpoker_muck_deny'), 'jpoker_muck_deny');
  ok(muck_deny_element.children(0).hasClass('jpoker_muck'), 'jpoker_muck');

  var auto_muck_element = $('#jpokerOptionsDialog');
  equals(auto_muck_element.length, 1, '#jpokerOptionsDialog');
  ok(auto_muck_element.children(0).hasClass('jpoker_auto_muck'), 'jpoker_auto_muck');
  equals($('input', auto_muck_element).length, 2, 'input');
  equals($('label', auto_muck_element).length, 2, 'label');

  var auto_muck_win = $('#auto_muck_win' + id);
  var auto_muck_lose = $('#auto_muck_lose' + id);
  equals(auto_muck_win.attr('type'), 'checkbox', '#auto_muck_win checkbox');
  equals(auto_muck_lose.attr('type'), 'checkbox', '#auto_muck_win checkbox');
  equals(auto_muck_win.is(':checked'), false, '#auto_muck_win checked preferences');
  equals(auto_muck_lose.is(':checked'), false, '#auto_muck_lose checked preferences');
  equals($('.jpoker_auto_muck_win label', auto_muck_element).attr('title'), 'Muck winning hands on showdown');
  equals($('.jpoker_auto_muck_lose label', auto_muck_element).attr('title'), 'Muck losing hands on showdown');

  server.sendPacket = function () {};
  auto_muck_win.click();
  auto_muck_lose.click();

  server.sendPacket = function (packet) {
    equals(packet.auto_muck, 0, 'AUTO_MUCK_NEVER');
  };
  auto_muck_win[0].checked = false;
  auto_muck_lose[0].checked = false;
  jpoker.plugins.muck.sendAutoMuck(server, game_id, id);

  server.sendPacket = function (packet) {
    equals(packet.auto_muck, 1, 'AUTO_MUCK_WIN');
  };
  auto_muck_win[0].checked = true;
  auto_muck_lose[0].checked = false;
  jpoker.plugins.muck.sendAutoMuck(server, game_id, id);

  server.sendPacket = function (packet) {
    equals(packet.auto_muck, 2, 'AUTO_MUCK_LOSE');
  };
  auto_muck_win[0].checked = false;
  auto_muck_lose[0].checked = true;
  jpoker.plugins.muck.sendAutoMuck(server, game_id, id);

  server.sendPacket = function (packet) {
    equals(packet.auto_muck, 3, 'AUTO_MUCK_WIN|AUTO_MUCK_LOSE');
  };
  auto_muck_win[0].checked = true;
  auto_muck_lose[0].checked = true;
  jpoker.plugins.muck.sendAutoMuck(server, game_id, id);
  equals(server.preferences.auto_muck_win, true, 'server.preferences.auto_muck_win updated');
  equals(server.preferences.auto_muck_lose, true, 'server.preferences.auto_muck_lose updated');

  table.handler(server, game_id, {
    type: 'PacketPokerMuckRequest',
    serial: player_serial,
    game_id: game_id,
    muckable_serials: [player_serial]
  });
  equals($("#muck_accept" + id).is(':visible'), true, 'muck accept visible');
  equals($("#muck_deny" + id).is(':visible'), true, 'muck deny visible');

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerMuckAccept', 'send PacketPokerMuckAccept');
  };
  $("#muck_accept" + id).click();

  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerMuckDeny', 'send PacketPokerMuckDeny');
  };
  $("#muck_deny" + id).click();

  table.handler(server, game_id, {
    type: 'PacketPokerState',
    game_id: game_id,
    state: 'end'
  });
  equals($("#muck_accept" + id).is(':hidden'), true, 'muck accept hidden');
  equals($("#muck_deny" + id).is(':hidden'), true, 'muck deny hidden');

  cleanup(id);
});

test("jpoker.plugins.playerSelf call with amount", function () {
  expect(3);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];
  table.betLimit = {
    min: 5000,
    max: 10000,
    step: 1000,
    call: 10000,
    allin: 40000,
    pot: 20000
  };

  var auto_action_element = $('#auto_action' + id);

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_call label .jpoker_call_amount', auto_action_element).text(), '10K', 'auto_call label');
  table.betLimit.call = 20000;
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_call label .jpoker_call_amount', auto_action_element).text(), '20K', 'auto_call label');
  table.betLimit.call = 30000;
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('#call' + id + ' .jpoker_call_amount').text(), '30K', 'call label');
  cleanup(id);
});

test("jpoker.plugins.playerSelf hand strength", function () {
  expect(11);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var hand_strength_element = $('#hand_strength' + id);
  equals(hand_strength_element.length, 1, 'hand_strength element');
  equals($('.jpoker_hand_strength_label', hand_strength_element).length, 1, '.jpoker_hand_strength_label');
  equals($('.jpoker_hand_strength_value', hand_strength_element).length, 1, '.jpoker_hand_strength_value');
  ok(hand_strength_element.is(':hidden'), 'hand_strength should be hidden after player creation');
  var player = server.tables[game_id].serial2player[player_serial];
  var table = server.tables[game_id];
  table.handler(server, game_id, {
    type: 'PacketPokerStart',
    game_id: game_id
  });
  equals($('.jpoker_hand_strength_value', hand_strength_element).text(), '', 'hand_strength should be reset after hand start');
  ok(hand_strength_element.is(':hidden'), 'hand_strength should be hidden after hand start');
  var called = false;
  var display_done = jpoker.plugins.playerSelf.callback.hand_strength.display_done;
  jpoker.plugins.playerSelf.callback.hand_strength.display_done = function (element) {
    equals(element.text(), 'Hand strength: foo', 'callback on display');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerPlayerHandStrength',
    game_id: game_id,
    serial: player_serial,
    hand: 'foo'
  });
  equals($('.jpoker_hand_strength_value', hand_strength_element).text(), 'foo', 'hand_strength should be set by PokerPlayerHandStrength');
  ok(hand_strength_element.is(':visible'), 'hand_strength should be hidden after receiving PokerPlayerHandStrength');
  jpoker.plugins.playerSelf.callback.hand_strength.display_done = display_done;
  table.handler(server, game_id, {
    type: 'PacketPokerStart',
    game_id: game_id
  });
  equals($('.jpoker_hand_strength_value', hand_strength_element).text(), '', 'hand_strength should be reset by PokerStart (2)');
  ok(hand_strength_element.is(':hidden'), 'hand_strength should be hidden after hand start (2)');
  cleanup(id);
});

test("jpoker.plugins.playerSelf.auto_action check/fold", function () {
  expect(7);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 0,
    allin: 40,
    pot: 20
  };

  var auto_action_element = $('#auto_action' + id);
  equals(auto_action_element.length, 1, '#auto_action');
  equals($('.jpoker_auto_check_fold', auto_action_element).length, 1, '.jpoker_auto_check_fold');
  equals($('input[name=auto_check_fold]', auto_action_element).length, 1, 'auto_check_fold input');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_check_fold]', auto_action_element)[0].checked = true;
  table.betLimit.call = 0;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerCheck');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('input[name=auto_check_fold]', auto_action_element).is(':checked'), false, 'auto_check_fold should be unchecked after selfInPosition');
  equals($('.jpoker_auto_check_fold', auto_action_element).is(':hidden'), true, 'auto_check_fold should be hidden after selfInPosition');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_check_fold]', auto_action_element)[0].checked = true;
  table.betLimit.call = 10;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerFold');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  cleanup(id);
});

test("jpoker.plugins.playerSelf.auto_action check/call", function () {
  expect(7);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 0,
    allin: 40,
    pot: 20
  };

  var auto_action_element = $('#auto_action' + id);
  equals(auto_action_element.length, 1, '#auto_action');
  equals($('.jpoker_auto_check_call', auto_action_element).length, 1, '.jpoker_auto_check_call');
  equals($('input[name=auto_check_call]', auto_action_element).length, 1, 'auto_check_call input');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_check_call]', auto_action_element)[0].checked = true;
  table.betLimit.call = 0;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerCheck');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('input[name=auto_check_call]', auto_action_element).is(':checked'), false, 'auto_check_call should be unchecked after selfInPosition');
  equals($('.jpoker_auto_check_call', auto_action_element).is(':hidden'), true, 'auto_check_call should be hidden after selfInPosition');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_check_call]', auto_action_element)[0].checked = true;
  table.betLimit.call = 10;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerCall');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  cleanup(id);
});

test("jpoker.plugins.playerSelf.auto_action raise", function () {
  expect(8);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 0,
    allin: 40,
    pot: 20
  };

  var auto_action_element = $('#auto_action' + id);
  equals(auto_action_element.length, 1, '#auto_action');
  equals($('.jpoker_auto_raise', auto_action_element).length, 1, '.jpoker_auto_raise');
  equals($('input[name=auto_raise]', auto_action_element).length, 1, 'auto_raise input');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_raise]', auto_action_element)[0].checked = true;
  table.betLimit.call = 0;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerRaise');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('input[name=auto_raise]', auto_action_element).is(':checked'), false, 'auto_raise should be unchecked after selfInPosition');
  equals($('.jpoker_auto_raise', auto_action_element).is(':hidden'), true, 'auto_raise should be hidden after selfInPosition');

  $('.jpoker_auto_raise', auto_action_element).show();
  $('input[name=auto_raise]')[0].checked = true;
  table.betLimit.call = 10;
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_raise', auto_action_element).is(':visible'), true, 'auto_raise should be hidden after betIncrease');
  equals($('input[name=auto_raise]').is(':checked'), false, 'auto_raise should be unchecked after betIncrease');
  cleanup(id);
});

test("jpoker.plugins.playerSelf.auto_action check", function () {
  expect(11);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 0,
    allin: 40,
    pot: 20
  };

  var auto_action_element = $('#auto_action' + id);
  equals(auto_action_element.length, 1, '#auto_action');
  equals($('.jpoker_auto_check', auto_action_element).length, 1, '.jpoker_auto_check');
  equals($('input[name=auto_check]', auto_action_element).length, 1, 'auto_check input');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_check]', auto_action_element)[0].checked = true;
  table.betLimit.call = 0;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerCheck');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('input[name=auto_check]', auto_action_element).is(':checked'), false, 'auto_check should be unchecked after selfInPosition');
  equals($('.jpoker_auto_check', auto_action_element).is(':hidden'), true, 'auto_check should be hidden after selfInPosition');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_check]', auto_action_element)[0].checked = true;
  table.betLimit.call = 10;
  server.sendPacket = function (packet) {
    ok(false, 'should not be called');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('input[name=auto_check]', auto_action_element).is(':checked'), false, 'auto_check should be unchecked after selfInPosition');

  $('.jpoker_auto_check', auto_action_element).hide();
  table.betLimit.call = 0;
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_check', auto_action_element).is(':visible'), true, 'auto_check should be visible after beginRound if call == 0');

  $('.jpoker_auto_check', auto_action_element).hide();
  table.betLimit.call = 10;
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_check', auto_action_element).is(':hidden'), true, 'auto_check should be hidden after beginRound if call > 0');
  $('.jpoker_auto_check', auto_action_element).show();
  $('input[name=auto_check]')[0].checked = true;
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_check', auto_action_element).is(':hidden'), true, 'auto_check should be hidden after betIncrease');
  equals($('input[name=auto_check]').is(':checked'), false, 'auto_check should be unchecked after betIncrease');

  cleanup(id);
});

test("jpoker.plugins.playerSelf.auto_action call", function () {
  expect(12);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 0,
    allin: 40,
    pot: 20
  };

  var auto_action_element = $('#auto_action' + id);
  equals(auto_action_element.length, 1, '#auto_action');
  equals($('.jpoker_auto_call', auto_action_element).length, 1, '.jpoker_auto_call');
  equals($('input[name=auto_call]', auto_action_element).length, 1, 'auto_call input');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_call]', auto_action_element)[0].checked = true;
  table.betLimit.call = 10;
  server.sendPacket = function (packet) {
    equals(packet.type, 'PacketPokerCall');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('input[name=auto_call]', auto_action_element).is(':checked'), false, 'auto_call should be unchecked after selfInPosition');
  equals($('.jpoker_auto_call', auto_action_element).is(':hidden'), true, 'auto_call should be hidden after selfInPosition');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  $('input[name=auto_call]', auto_action_element)[0].checked = true;
  table.betLimit.call = 0;
  server.sendPacket = function (packet) {
    ok(false, 'should not be called');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerSelfInPosition',
    serial: player_serial,
    game_id: game_id
  });
  equals($('input[name=auto_call]', auto_action_element).is(':checked'), false, 'auto_call should be unchecked after selfInPosition');

  $('.jpoker_auto_call', auto_action_element).hide();
  table.betLimit.call = 0;
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_call', auto_action_element).is(':hidden'), true, 'auto_call should be hidden after beginRound if call == 0');

  $('.jpoker_auto_call', auto_action_element).hide();
  table.betLimit.call = 10;
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_call', auto_action_element).is(':visible'), true, 'auto_call should be visible after beginRound if call > 0');

  $('.jpoker_auto_call', auto_action_element).show();
  $('input[name=auto_call]')[0].checked = true;
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_call', auto_action_element).is(':visible'), true, 'auto_call should be visible after betIncrease');
  equals($('input[name=auto_call]').is(':checked'), false, 'auto_call should be unchecked after betIncrease');

  player.in_game = false;
  $('.jpoker_auto_call', auto_action_element).hide();
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_call', auto_action_element).is(':hidden'), true, 'auto_call should be hidden if not inGame');

  cleanup(id);
});

test("jpoker.plugins.playerSelf.auto_action visibility", function () {
  expect(13);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];
  table.betLimit = {
    min: 5,
    max: 10,
    step: 1,
    call: 0,
    allin: 40,
    pot: 20
  };

  var auto_action_element = $('#auto_action' + id);

  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_action should be hidden by default');

  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':visible'), true, 'auto_action should be visible after beginRound');

  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':visible'), true, 'auto_action should be visible after betIncrease');

  $('.jpoker_auto_action', auto_action_element).show();
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    game_id: game_id,
    players: [player_serial]
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_fold should be hidden after inGame');
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':visible'), true, 'auto_action should be visible after beginRound if inGame');

  $('.jpoker_auto_action', auto_action_element).show();
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    game_id: game_id,
    players: [player_serial]
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_fold should be hidden after inGame');
  table.betLimit.call = 20;
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':visible'), true, 'auto_action should be visible after betIncrease if inGame and not playerSelf bet (call > 0)');

  $('.jpoker_auto_action', auto_action_element).show();
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    game_id: game_id,
    players: [player_serial]
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_fold should be hidden after inGame');
  table.betLimit.call = 0;
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_action should be hidden after betIncrease if inGame and playerSelf bet (call == 0)');

  $('.jpokerf_auto_action', auto_action_element).show();
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    game_id: game_id,
    players: []
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_action should be hidden after beginRound if inGame');

  $('.jpoker_auto_action', auto_action_element).show();
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    game_id: game_id,
    players: []
  });
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_action should be hidden after beginRound if inGame');

  $('.jpoker_auto_action', auto_action_element).show();
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    game_id: game_id,
    players: [player_serial]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerFold',
    game_id: game_id,
    serial: player_serial
  });
  table.handler(server, game_id, {
    type: 'PacketPokerBeginRound',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_action should be hidden after beginRound if player folded');

  $('.jpoker_auto_action', auto_action_element).show();
  table.handler(server, game_id, {
    type: 'PacketPokerInGame',
    game_id: game_id,
    players: [player_serial]
  });
  table.handler(server, game_id, {
    type: 'PacketPokerFold',
    game_id: game_id,
    serial: player_serial
  });
  table.handler(server, game_id, {
    type: 'PacketPokerHighestBetIncrease',
    game_id: game_id
  });
  equals($('.jpoker_auto_action', auto_action_element).is(':hidden'), true, 'auto_action should be hidden after betIncrease if player folded');
  cleanup(id);
});

test("jpoker.plugins.playerSelf.auto_action radio checkbox", function () {
  expect(4);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  player.in_game = true;
  var table = server.tables[game_id];

  var auto_action_element = $('#auto_action' + id);

  $('input[name=auto_check_fold]', auto_action_element).click();
  equals($('input[name=auto_check_fold]', auto_action_element).is(':checked'), true, 'auto_check_fold selection');
  $('input[name=auto_check_call]', auto_action_element).click();
  equals($('input[name=auto_check_call]', auto_action_element).is(':checked'), true, 'auto_check_call selection');
  equals($('input[name=auto_check_fold]', auto_action_element).is(':checked'), false, 'auto_check_fold should be unchecked after auto_check_call selection');
  $('input[name=auto_check_fold]', auto_action_element).click();
  equals($('input[name=auto_check_call]', auto_action_element).is(':checked'), false, 'auto_check_call should be unchecked after auto_check_fold selection');
  cleanup(id);
});

test("jpoker.plugins.playerSelf table move", function () {
  expect(1);

  var place = $("#main");

  var id = 'jpoker' + jpoker.serial;
  var player_serial = 1;
  var game_id = 100;
  var money = 1000;

  var server = jpoker.serverCreate({
    url: 'url'
  });
  var currency_serial = 42;
  var table_packet = {
    id: game_id,
    currency_serial: currency_serial
  };
  server.tables[game_id] = new jpoker.table(server, table_packet);

  // table
  place.jpoker('table', 'url', game_id);

  // player
  server.serial = player_serial;
  var player_seat = 2;
  server.tables[game_id].handler(server, game_id, {
    type: 'PacketPokerPlayerArrive',
    seat: player_seat,
    serial: player_serial,
    game_id: game_id
  });
  var player = server.tables[game_id].serial2player[player_serial];
  var table = server.tables[game_id];
  var table_move = jpoker.plugins.playerSelf.callback.table_move;
  jpoker.plugins.playerSelf.callback.table_move = function (packet) {
    equals(packet.to_game_id, 101);
  };
  table.handler(server, game_id, {
    type: 'PacketPokerTableMove',
    game_id: game_id,
    serial: player_serial,
    to_game_id: game_id + 1
  });
  jpoker.plugins.playerSelf.callback.table_move = function (packet) {
    ok(false, 'should not be called');
  };
  table.handler(server, game_id, {
    type: 'PacketPokerTableMove',
    game_id: game_id,
    serial: player_serial + 1,
    to_game_id: game_id + 1
  });
  jpoker.plugins.playerSelf.callback.table_move = table_move;
  cleanup(id);
});


test("jpoker.plugins.places", function () {
  expect(9);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    serial: 42,
    tables: [11, 12, 13],
    tourneys: [21, 22]
  };

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(PLAYER_PLACES_PACKET) + " ]",

    handle: function (packet) {}
  };
  ActiveXObject.prototype.server = new PokerServer();

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  equals('update' in server.callbacks, false, 'no update registered');
  var display_done = jpoker.plugins.places.callback.display_done;
  jpoker.plugins.places.callback.display_done = function (element) {
    jpoker.plugins.places.callback.display_done = display_done;
    equals($(".jpoker_places", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('places', 'url');
  equals(server.callbacks.update.length, 1, 'places update registered');
  equals($('.jpoker_places', place).length, 1, 'places div');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPlayerPlaces') {
        equals($('tbody .jpoker_places_table', element).length, 3, 'jpoker_places_table');
        equals($('tbody .jpoker_places_tourney', element).length, 2, 'jpoker_places_tourney');
        server.tableJoin = function (id) {
          equals(id, PLAYER_PLACES_PACKET.tables[0], 'tableJoin called');
        };
        $('.jpoker_places_table', element).eq(0).click();
        server.placeTourneyRowClick = function (server, packet) {
          equals(packet.game_id, PLAYER_PLACES_PACKET.tourneys[0], 'placeTourneyRowClick called');
          equals(packet.name, '', 'placeTourneyRowClick called');
        };
        $('.jpoker_places_tourney', element).eq(0).click();
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.places other serial", function () {
  expect(1);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  server.getPlayerPlaces = function (serial) {
    equals(serial, 42, 'serial');
    setTimeout(function () {
      $('#' + id).remove();
      server.notifyUpdate({});
      start_and_cleanup();
    }, 0);
  };
  place.jpoker('places', 'url', {
    serial: '42'
  });
});

test("jpoker.plugins.places link_pattern", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    serial: 42,
    tables: [11, 12, 13],
    tourneys: [21, 22]
  };

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(PLAYER_PLACES_PACKET) + " ]",

    handle: function (packet) {}
  };
  ActiveXObject.prototype.server = new PokerServer();

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  var table_link_pattern = 'http://foo.com/table?game_id={game_id}';
  var tourney_link_pattern = 'http://foo.com/tourney?tourney_serial={tourney_serial}';
  place.jpoker('places', 'url', {
    table_link_pattern: table_link_pattern,
    tourney_link_pattern: tourney_link_pattern
  });
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPlayerPlaces') {
        server.tableJoin = function (id) {
          ok(false, 'tableJoin disabled');
        };
        var table = $('.jpoker_places_table', element).eq(0).click();
        server.placeTourneyRowClick = function (server, id) {
          ok(false, 'tourneyRowClick disabled');
        };
        var tourney = $('.jpoker_places_tourney', element).eq(0).click();

        var table_link = table_link_pattern.supplant({
          game_id: 11
        });
        ok($('td:nth-child(1)', table).html().indexOf(table_link) >= 0, table_link);
        var tourney_link = tourney_link_pattern.supplant({
          tourney_serial: 21
        });
        ok($('td:nth-child(1)', tourney).html().indexOf(tourney_link) >= 0, tourney_link);
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.playerLookup", function () {
  expect(14);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;
  lookup_serial = 84;
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    serial: lookup_serial,
    name: 'user',
    tables: [11, 12, 13],
    tourneys: [21, 22]
  };

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  equals('update' in server.callbacks, false, 'no update registered');
  place.jpoker('playerLookup', 'url');
  equals(server.callbacks.update.length, 1, 'player_lookup update registered');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPlayerPlaces') {
        equals($('.jpoker_player_lookup_table', element).length, 3, 'jpoker_places_table');
        equals($('.jpoker_player_lookup_tourney', element).length, 2, 'jpoker_places_tourney');
        server.tableJoin = function (id) {
          equals(id, PLAYER_PLACES_PACKET.tables[0], 'tableJoin called');
        };
        $('.jpoker_player_lookup_table', element).eq(0).click();
        server.placeTourneyRowClick = function (server, packet) {
          equals(packet.game_id, PLAYER_PLACES_PACKET.tourneys[0], 'placeTourneyRowClick called');
          equals(packet.name, '', 'placeTourneyRowClick called');
        };
        $('.jpoker_player_lookup_tourney', element).eq(0).click();
        server.sendPacket = function (packet) {
          equals(packet.type, 'PacketPokerCreateTourney');
          equals(packet.players[0], server.serial, 'challenging player');
          equals(packet.players[1], lookup_serial, 'challenged player');
        };
        $('.jpoker_player_lookup_challenge a', element).eq(0).click();
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
  var player_lookup_element = $('.jpoker_player_lookup');
  equals(player_lookup_element.length, 1, 'player_lookup div');
  equals($('.jpoker_player_lookup_input', player_lookup_element).length, 1, 'player_lookup_input');
  equals($('.jpoker_player_lookup_submit', player_lookup_element).length, 1, 'player_lookup_submit');
  $('.jpoker_player_lookup_input', player_lookup_element).val('user');
  server.sendPacket = function (packet) {
    equals(packet.name, 'user', 'packet.name');
    server.queueIncoming([PLAYER_PLACES_PACKET]);
  };
  $('.jpoker_player_lookup_submit', player_lookup_element).click();
});

test("jpoker.plugins.playerLookup not logged", function () {
  expect(7);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 0;
  lookup_serial = 84;
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    serial: lookup_serial,
    name: 'user',
    tables: [11, 12, 13],
    tourneys: [21, 22]
  };

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  equals('update' in server.callbacks, false, 'no update registered');
  place.jpoker('playerLookup', 'url');
  equals(server.callbacks.update.length, 1, 'player_lookup update registered');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPlayerPlaces') {
        $('.jpoker_player_lookup_challenge a', element).eq(0).click();
        equals($('#jpokerDialog').text().indexOf('you must login') >= 0, true, 'not logged means no challenge');
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
  var player_lookup_element = $('.jpoker_player_lookup');
  equals(player_lookup_element.length, 1, 'player_lookup div');
  equals($('.jpoker_player_lookup_input', player_lookup_element).length, 1, 'player_lookup_input');
  equals($('.jpoker_player_lookup_submit', player_lookup_element).length, 1, 'player_lookup_submit');
  $('.jpoker_player_lookup_input', player_lookup_element).val('user');
  server.sendPacket = function (packet) {
    equals(packet.name, 'user', 'packet.name');
    server.queueIncoming([PLAYER_PLACES_PACKET]);
  };
  $('.jpoker_player_lookup_submit', player_lookup_element).click();
});

test("jpoker.plugins.playerLookup error", function () {
  expect(4);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    name: 'user',
    tables: [11, 12, 13],
    tourneys: [21, 22]
  };
  var ERROR_PACKET = {
    type: 'PacketError',
    other_type: jpoker.packetName2Type.PACKET_POKER_PLAYER_PLACES
  };
  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  var jpoker_playerLookup_callback_error = jpoker.plugins.playerLookup.callback.error;
  jpoker.plugins.playerLookup.callback.error = function (packet) {
    ok(true, 'callback error called');
  };
  place.jpoker('playerLookup', 'url');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPlayerPlaces') {
        server.sendPacket = function (packet) {
          equals($('.jpoker_player_lookup_result', player_lookup_element).html(), '', 'empty result');
          server.queueIncoming([ERROR_PACKET]);
        };
        $('.jpoker_player_lookup_submit', player_lookup_element).click();
      } else if (data.type == 'PacketError') {
        equals($('.jpoker_player_lookup_tables', element).length, 0, 'jpoker_places_table');
        equals($('.jpoker_player_lookup_tourneys', element).length, 0, 'jpoker_places_tourney');
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
  var player_lookup_element = $('.jpoker_player_lookup', place);
  $('.jpoker_player_lookup_input', player_lookup_element).val('user');
  server.sendPacket = function (packet) {
    server.queueIncoming([PLAYER_PLACES_PACKET]);
  };
  $('.jpoker_player_lookup_submit', player_lookup_element).click();
});

test("jpoker.plugins.playerLookup link_pattern", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    name: 'user',
    tables: [11, 12, 13],
    tourneys: [21, 22]
  };

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  var table_link_pattern = 'http://foo.com/table?game_id={game_id}';
  var tourney_link_pattern = 'http://foo.com/tourney?tourney_serial={tourney_serial}';
  place.jpoker('playerLookup', 'url', {
    table_link_pattern: table_link_pattern,
    tourney_link_pattern: tourney_link_pattern
  });
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPlayerPlaces') {
        server.tableJoin = function (id) {
          ok(false, 'tableJoin disabled');
        };
        var table = $('.jpoker_player_lookup_table', element).eq(0).click();
        server.placeTourneyRowClick = function (server, id) {
          ok(false, 'tourneyRowClick disabled');
        };
        var tourney = $('.jpoker_player_lookup_tourney', element).eq(0).click();

        var table_link = table_link_pattern.supplant({
          game_id: 11
        });
        ok($('td:nth-child(1)', table).html().indexOf(table_link) >= 0, table_link);
        var tourney_link = tourney_link_pattern.supplant({
          tourney_serial: 21
        });
        ok($('td:nth-child(1)', tourney).html().indexOf(tourney_link) >= 0, tourney_link);
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
  var player_lookup_element = $('.jpoker_player_lookup');
  $('.jpoker_player_lookup_input', player_lookup_element).val('user');
  server.sendPacket = function (packet) {
    server.queueIncoming([PLAYER_PLACES_PACKET]);
  };
  $('.jpoker_player_lookup_submit', player_lookup_element).click();
});

test("jpoker.plugins.playerLookup options", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  var PLAYER_PLACES_PACKET = {
    type: 'PacketPokerPlayerPlaces',
    name: 'user',
    tables: [11, 12, 13],
    tourneys: [21, 22]
  };
  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  place.jpoker('playerLookup', 'url', {
    dialog: false,
    tag: 42
  });
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPlayerPlaces') {
        setTimeout(function () {
          $('#' + id).remove();
          server.notifyUpdate({});
          start_and_cleanup();
        }, 0);
      }
      return false;
    }
  });
  var player_lookup_element = $('.jpoker_player_lookup', place);
  $('.jpoker_player_lookup_input', player_lookup_element).val('user');
  server.getPlayerPlacesByName = function (name, options) {
    equals(options.dialog, false, 'options dialog');
    equals(options.tag, 42, 'options tag');
    server.notifyUpdate(PLAYER_PLACES_PACKET);
  };
  $('.jpoker_player_lookup_submit', player_lookup_element).click();
});

test("jpoker.plugins.cashier", function () {
  expect(13);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;
  var USER_INFO_PACKET = {
    "rating": 1000,
    "name": "proppy",
    "money": {
      "X1": [100000, 10000, 0],
      "X2": [200000, 20000, 0]
    },
    "affiliate": 0,
    "cookie": "",
    "serial": 4,
    "password": "",
    "type": "PacketPokerUserInfo",
    "email": "",
    "uid__": "jpoker1220102037582"
  };

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(USER_INFO_PACKET) + " ]",

    handle: function (packet) {}
  };
  ActiveXObject.prototype.server = new PokerServer();

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  equals('update' in server.callbacks, false, 'no update registered');
  var display_done = jpoker.plugins.cashier.callback.display_done;
  jpoker.plugins.cashier.callback.display_done = function (element) {
    jpoker.plugins.cashier.callback.display_done = display_done;
    equals($(".jpoker_cashier", $(element).parent()).length, 1, 'display done called when DOM is done');
  };
  place.jpoker('cashier', 'url');
  equals(server.callbacks.update.length, 1, 'cashier update registered');
  equals($('.jpoker_cashier').length, 1, 'cashier div');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerUserInfo') {
        equals($('.jpoker_cashier_currency', element).length, 2, 'jpoker_places_currency');
        equals($('.jpoker_cashier_currency td:nth-child(1)', element).eq(0).html(), '1', 'jpoker_places_currency amount 1');
        equals($('.jpoker_cashier_currency td:nth-child(2)', element).eq(0).html(), '1000', 'jpoker_places_currency amount 1');
        equals($('.jpoker_cashier_currency td:nth-child(3)', element).eq(0).html(), '100', 'jpoker_places_currency in game 1');
        equals($('.jpoker_cashier_currency td:nth-child(4)', element).eq(0).html(), '0', 'jpoker_places_currency points 1');
        equals($('.jpoker_cashier_currency td:nth-child(1)', element).eq(1).html(), '2', 'jpoker_places_currency amount 2');
        equals($('.jpoker_cashier_currency td:nth-child(2)', element).eq(1).html(), '2000', 'jpoker_places_currency amount 2');
        equals($('.jpoker_cashier_currency td:nth-child(3)', element).eq(1).html(), '200', 'jpoker_places_currency in game 2');
        equals($('.jpoker_cashier_currency td:nth-child(4)', element).eq(1).html(), '0', 'jpoker_places_currency points 2');
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });
});

test("jpoker.plugins.tablepicker", function () {
  expect(25);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;

  var TABLE_PACKET = {
    type: 'PacketPokerTable',
    id: 11,
    reason: 'TablePicker'
  };

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(TABLE_PACKET) + " ]",
    handle: function (packet) {}
  };
  ActiveXObject.prototype.server = new PokerServer();

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  server.preferences.tablepicker = {
    variant: 'omaha'
  };
  place.jpoker('tablepicker', 'url', {
    currency_serial: 1,
    variant: 'holdem'
  });
  equals($('.jpoker_tablepicker').length, 1, 'tablepicker div');
  equals($('.jpoker_tablepicker_submit').length, 1, 'tablepicker submit input');
  equals($('.jpoker_tablepicker_submit').val(), 'Play now', 'tablepicker submit value');
  equals($('.jpoker_tablepicker_submit').attr('title'), 'Click here to automatically pick a table', 'tablepicker submit title');
  ok($('.jpoker_tablepicker_error').is(':hidden'), 'tablepicker error hidden');
  equals($('.jpoker_tablepicker_show_options').length, 1, 'tablepicker show options');
  equals($('.jpoker_tablepicker_options').length, 1, 'tablepicker options');
  equals($('.jpoker_tablepicker_options label').length, 3, 'tablepicker options label');

  equals($('.jpoker_tablepicker input[name=variant]').length, 1, 'tablepicker variant input');
  equals($('.jpoker_tablepicker input[name=variant]').val(), 'omaha', 'tablepicker variant input value');
  equals($('.jpoker_tablepicker input[name=betting_structure]').length, 1, 'tablepicker betting_structure input');
  equals($('.jpoker_tablepicker input[name=betting_structure]').val(), '', 'tablepicker betting_structure input value');
  equals($('.jpoker_tablepicker input[name=currency_serial]').length, 1, 'tablepicker currency_serial input');
  equals($('.jpoker_tablepicker input[name=currency_serial]').val(), 1, 'tablepicker currency_serial input value');
  equals($('.jpoker_tablepicker_option').length, 3);
  equals($('.jpoker_tablepicker_options').is(':hidden'), true);

  $('.jpoker_tablepicker_show_options').click();
  equals($('.jpoker_tablepicker_options').is(':visible'), true);
  $('.jpoker_tablepicker_show_options').click();
  equals($('.jpoker_tablepicker_options').is(':hidden'), true);
  $('.jpoker_tablepicker input[name=betting_structure]').val('1-2-limit').change();
  equals(server.preferences.tablepicker.betting_structure, '1-2-limit');
  equals(server.callbacks.update.length, 1, 'tablepicker update registered');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerTable') {
        ok($('.jpoker_tablepicker_error').is(':hidden'), 'tablepicker error hidden');
        equals($('.jpoker_tablepicker_error').text(), '', 'empty error');
        $('#' + id).remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });

  var tablePick = server.tablePick;
  server.tablePick = function (criterion) {
    equals(criterion.variant, 'omaha', 'variant criterion');
    equals(criterion.betting_structure, '1-2-limit', 'betting_structure criterion');
    equals(criterion.currency_serial, 1, 'currency_serial criterion');
    tablePick.apply(server, arguments);
  };

  $('.jpoker_tablepicker_error').show();
  $('.jpoker_tablepicker_error').text('foo');
  $('.jpoker_tablepicker_submit').click();
});

test("jpoker.plugins.tablepicker failed", function () {
  expect(2);
  stop();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';

  server.serial = 42;

  var ERROR_PACKET = {
    type: 'PacketPokerError',
    other_type: $.jpoker.packetName2Type.POKER_TABLE_PICKER,
    message: "tablepicker error"
  };

  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(ERROR_PACKET) + " ]",
    handle: function (packet) {}
  };
  ActiveXObject.prototype.server = new PokerServer();

  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');

  place.jpoker('tablepicker', 'url');
  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerError') {
        ok($('.jpoker_tablepicker_error', element).is(':visible'), 'table picker error shown');
        equals($('.jpoker_tablepicker_error', element).text(), 'tablepicker error');
        element.remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });

  $('.jpoker_tablepicker input[type=submit]').click();
});

test("jpoker.plugins.signup", function () {
  expect(14);
  stop();


  var PERSONAL_INFO_PACKET = {
    'rating': 1000,
    'firstname': 'John',
    'money': {},
    'addr_street': '',
    'phone': '',
    'cookie': '',
    'serial': 42,
    'password': '',
    'addr_country': '',
    'name': 'testuser',
    'gender': '',
    'birthdate': '',
    'addr_street2': '',
    'addr_zip': '',
    'affiliate': 0,
    'lastname': 'Doe',
    'addr_town': '',
    'addr_state': '',
    'type': 'PacketPokerPersonalInfo',
    'email': ''
  };
  var PokerServer = function () {};
  PokerServer.prototype = {
    outgoing: "[ " + JSON.stringify(PERSONAL_INFO_PACKET) + " ]",
    handle: function (packet) {}
  };
  ActiveXObject.prototype.server = new PokerServer();

  var server = jpoker.serverCreate({
    url: 'url'
  });
  server.connectionState = 'connected';
  var id = 'jpoker' + jpoker.serial;
  var place = $('#main');
  place.jpoker('signup', 'url');
  equals($('.jpoker_signup.ui-dialog-content').length, 1, 'signup div');
  ok($('.jpoker_signup').hasClass('jpoker_jquery_ui'), 'jquery_jquery_ui');
  equals($('.jpoker_signup input').length, 5, 'input');
  equals($('.jpoker_signup label').length, 4, 'label');
  equals($('.jpoker_signup input[name=login]').length, 1, 'login');
  equals($('.jpoker_signup input[name=password]').length, 1, 'password');
  equals($('.jpoker_signup input[name=password_confirmation]').length, 1, 'password confirmation');
  equals($('.jpoker_signup input[name=email]').length, 1, 'email');
  equals($('.jpoker_signup input[type=submit]').length, 1, 'submit');

  $('.jpoker_signup input[name=login]').val('john');
  $('.jpoker_signup input[name=password]').val('doe1');
  $('.jpoker_signup input[name=password_confirmation]').val('doe1');
  $('.jpoker_signup input[name=email]').val('john@doe.com');

  server.registerUpdate(function (server, what, data) {
    var element = $('#' + id);
    if (element.length > 0) {
      if (data.type == 'PacketPokerPersonalInfo') {
        equals($('.jpoker_signup').is(':hidden'), true, 'dialog closed');
        element.remove();
      }
      return true;
    } else {
      start_and_cleanup();
      return false;
    }
  });

  var createAccount = server.createAccount;
  server.createAccount = function (options) {
    equals(options.name, 'john');
    equals(options.password, 'doe1');
    equals(options.password_confirmation, 'doe1');
    equals(options.email, 'john@doe.com');
    createAccount.apply(server, arguments);
  };

  $('.jpoker_signup input[type=submit]').click();
});

test("jpoker.preferences", function () {
  expect(5);

  var hash = jpoker.url2hash('url');
  $.cookie('jpoker_preferences_' + hash, '{"a": 1}');
  var preferences = new jpoker.preferences(hash);
  equals(preferences.a, 1, 'jpoker.preferences.a');
  preferences.extend({
    'b': 2,
    'c': 3
  });
  equals(preferences.b, 2, 'jpoker.preferences.b');
  equals(preferences.c, 3, 'jpoker.preferences.c');
  equals($.cookie('jpoker_preferences_' + hash), JSON.stringify(preferences), 'cookie updated');
  preferences.b = 200;
  preferences.save();
  equals($.cookie('jpoker_preferences_' + hash), JSON.stringify(preferences), 'cookie updated');
  cleanup();
});

test("jpoker.preferences defaults values", function () {
  expect(2);

  equals(jpoker.preferences.prototype.auto_muck_win, true);
  equals(jpoker.preferences.prototype.auto_muck_lose, true);
  cleanup();
});

test("jpoker.preferences in jpoker.server", function () {
  expect(1);
  var hash = jpoker.url2hash('url');
  $.cookie('jpoker_preferences_' + hash, '{"a": 1}');
  var server = jpoker.serverCreate({
    url: 'url'
  });
  equals(server.preferences.a, 1, 'server.preferences.a');
  cleanup();
});

test("jquery.fn.moveFrom", function () {
  expect(6);
  stop();
  $('#main').html('<div id=\'money\' /><div id=\'bet\' />');
  $('#money').css({
    position: 'absolute',
    left: '100px',
    top: '100px'
  }).hide();
  $('#bet').css({
    position: 'absolute',
    left: '200px',
    top: '200px'
  });
  $("#bet").moveFrom('#money', {
    duration: 100,
    complete: function () {
      equals($('#bet').css('left'), '200px');
      equals($('#bet').css('top'), '200px');
      start();
    }
  });
  equals($('#bet').css('left'), '100px');
  equals($('#bet').css('top'), '100px');
  ok($('#money').is(':hidden'), 'hidden');
  ok($('#bet').is(':visible'), 'visible');
});

test("jquery.fn.getOffset", function () {
  expect(2);
  $('#main').html('<div id="parent"><div id="child"></div></div>');
  $('#parent').css({
    position: 'absolute',
    left: '101px',
    top: '102px'
  });
  $('#child').hide();
  equals($('#child').getOffset().top, 102, 'top position');
  equals($('#child').getOffset().left, 101, 'left position');
});

test("jquery.fn.getPosition", function () {
  expect(2);
  $('#main').html('<div id="parent"><div id="child"></div></div>');
  $('#parent').css({
    position: 'absolute',
    left: '101px',
    top: '102px'
  });
  $('#child').hide();
  equals($('#child').getPosition().top, 0, 'top position');
  equals($('#child').getPosition().left, 0, 'left position');
});

test("jquery Date format", function () {
  equals($.strftime("%Y %m %d", new Date(0)), "1970 01 01");
});

test("$.fn.frame", function () {
  expect(4);
  var element = $("<div id='PID'><div id='ID'></div></div>").appendTo(document.body);
  $('#ID', element).frame('FRAME');
  equals($('#PID > .FRAME > .FRAME-s').size(), 1, 'south div');
  equals($('#PID > .FRAME-container > .FRAME-inner > #ID').size(), 1, 'ID');
  $('#PID > .FRAME').trigger('mouseenter');
  equals($('#PID > .FRAME-hover').size(), 1, 'class FRAME-hover added');
  $('#PID > .FRAME').trigger('mouseleave');
  equals($('#PID > .FRAME-hover').size(), 0, 'class FRAME-hover removed');
});

test("IE7Bugs", function () {
  var dialogTest = $("<div id='dialogtest1'>Test Dialog</div>").dialog({
    width: 'none',
    height: 'none'
  });
  equals(dialogTest !== undefined, true, 'UI Dialog Bug on IE (width, height = "none")');
  dialogTest.dialog('close').remove();

  var dialogTestIE7 = $("<div style=\'margin:auto\' id='dialogtest2'>Test Dialog</div>").dialog();
  equals(dialogTestIE7 !== undefined, true, 'UI Dialog Bug on IE (margin = "auto" )');
  dialogTestIE7.dialog('close').remove();

  var limits = [0, 0, 0];
  var sliderTest = $("<div class=\'ui-slider-1\' id=\'slidertest\'></div>").appendTo("#main").slider({
    min: limits[0],
    startValue: limits[1],
    //IE bug
    max: limits[2],
    stepping: 1,
    change: function (event, ui) {}
  });
  equals($('#slidertest').length, 1, 'UI Slider Bug on IE');
});

//
// catch leftovers
//
// test("leftovers", function(){
//         expect(1);
//         stop();
//         var PokerServer = function() {};
//         PokerServer.prototype = {
//             outgoing: '[]',
//             handle: function(packet) {
//                 equals(packet, '');
//                 start();
//             }
//         };
//         ActiveXObject.prototype.server = new PokerServer();

//     });
