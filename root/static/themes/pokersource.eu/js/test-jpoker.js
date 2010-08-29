//
//     Copyright (C) 2010 Loic Dachary <loic@dachary.org>
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
module("jpoker");

if(!window.ActiveXObject) {
    window.ActiveXObject = true;
}

var ActiveXObject = function(options) {
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

    open: function(type, url, async) {
//        window.console.log('ActiveXObject ' + url);
    },
    
    setRequestHeader: function(header) {
        this.headers.push(header);
    },
    
    getResponseHeader: function(header) {
        if(header == "content-type") {
            return "text/plain";
        } else {
            return null;
        }
    },

    abort: function() {
    },

    send: function(data) {
        if('server' in this && this.server && !this.timeout && this.status == 200) {
            this.server.handle(data);
            this.responseText = this.server.outgoing;
        }
    }
};

test("jpoker: main", function() {
        expect(0);
    });

test("jpoker: setTemplates", function() {
        expect(1);
        var login = $.jpoker.plugins.login.templates.login;
        $.jpoker.setTemplates();
        ok(login != $.jpoker.plugins.login.templates.login);
    });

test("jpoker: setLocale", function() {
        expect(4);

	$.cookie('jpoker_preferences_global', null);
        ok($.jpoker.global_preferences === undefined, 'global is undefined');
        $.jpoker.setLocale();
        equals($.jpoker.global_preferences.lang, 'en');
        ok($.cookie('jpoker_preferences_global') === null, 'cookie global is null');

	$.cookie('jpoker_preferences_global', '{"lang":"fr"}');
        $.jpoker.setLocale();
        equals($.jpoker.global_preferences.lang, 'fr'); // overrides the default 'en'
	$.cookie('jpoker_preferences_global', null);
    });

function reset_locale() {
    $.cookie('jpoker_preferences_global', null);
    $.jpoker.global_preferences = null;
}

test("jpoker: changeLocale", function() {
        expect(2);
        var reloaded = false;
        reset_locale();
        $.jpoker.setLocale();
        $.jpoker.reload = function() { reloaded = true; };
        $.jpoker.changeLocale('fr');
	equals($.cookie('jpoker_preferences_global'), '{"lang":"fr"}', 'global cookie');
        equals($.jpoker.global_preferences.lang, 'fr');
        reset_locale();
    });

test("jpoker: setSpawnTable", function() {
        expect(1);
        
        $.jpoker.setLocale();
        $.jpoker.setSpawnTable();
        var server = $.jpoker.url2server('url');
        var game_id = 10;
        var name = 'TABLE NAME';
        var packet = { "type": 'PacketPokerTable',
                       "game_id": game_id,
                       "id": game_id,
                       "name": name };
        server.handler(server, game_id, packet);
        var t = $($.jpoker.selectors.table).text();
        ok(t.indexOf(name) >= 0, 'looking for ' + name + ' in ' + t);
    });
