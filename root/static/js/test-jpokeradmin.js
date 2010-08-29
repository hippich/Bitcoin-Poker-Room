//
//     Copyright (C) 2009 Loic Dachary <loic@dachary.org>
//     Copyright (C) 2009 Johan Euphrosine <proppy@aminche.com>
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

module("jpokeradmin");

if(!window.ActiveXObject) {
    window.ActiveXObject = true;
}

var ActiveXObject = function(options) {
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
        this.server.open(type, url, async);
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

var cleanup = function() {
    $("#main").empty();
    $('#jpokerAdminEdit').dialog('close').remove();
};

var start_and_cleanup = function(id) {
    setTimeout(function() {
            cleanup(id);
            start();
        }, 1);
};

$.fn.triggerKeypress = function(keyCode) {
    return this.trigger("keypress", [$.event.fix({event:"keypress", keyCode: keyCode, target: this[0]})]);
};

$.jpoker.plugins.tourneyAdminList.resthost = [{"host": "server1.com", "path": "/REST", "serial": 1, "name": "server1", "port": 1111}, {"host": "server2.com", "path": "/REST2", "serial": 2, "name": "server2", "port": 2222}];
$.jpoker.plugins.tourneyAdminList.currencies = [{"url": "http://currency-server/", "cash_out": 0, "serial": 1, "symbol": "P", "name": "playmoney"}, {"url": "http://currency-server-euros/", "cash_out": 0, "serial": 2, "symbol": "E", "name": "euros"}];

//
// tourneyAdminList
//
test("jpoker.plugins.tourneyAdminList", function(){
        expect(8);

	var getResthost = $.jpoker.plugins.tourneyAdminList.getResthost;
	$.jpoker.plugins.tourneyAdminList.getResthost = function() {
	    $.jpoker.plugins.tourneyAdminList.getResthost = getResthost;
	};
	var getCurrencies = $.jpoker.plugins.tourneyAdminList.getCurrencies;
	$.jpoker.plugins.tourneyAdminList.getCurrencies = function() {
	    $.jpoker.plugins.tourneyAdminList.getCurrencies = getCurrencies;
	};

        var tourney_serial = 1111;
	var TOURNEY_LIST = [{"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+1, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "zzz abc80 test", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+2, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "blablabla 21", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}];
	var state = TOURNEY_LIST[1].state;

	var ajax = function(params) {
	    equals(params.url.indexOf('FROM+tourneys_schedule') >= 0, true, params.url);
            params.success(TOURNEY_LIST, 'status');
        };
	
        var place = $("#main");

        var edit = function(url, tourney, options) {
	    edit.callback(url, tourney, options);
        };
	edit.callback = function(url, tourney, options) {
	    equals(url.indexOf('pokersql') >= 0, true, url);
            equals(tourney.serial, tourney_serial);
            tourney.TEST = true;
            options.callback.updated(tourney);
	};

        place.jpoker('tourneyAdminList', 'url', {tourneyEdit: edit, ajax: ajax, callback: {display_done: function(element) {
			var tr = $('tbody tr', element);
			equals(tr.length, 3, 'number of rows');
		    }}});

        $('tbody tr:eq(0) .jpoker_admin_edit a', place).click();

	edit.callback = function(url, tourney, options) {
	    equals(tourney.serial, tourney_serial, 'tourney edit called bis');
	};
        $('tbody tr:eq(0) .jpoker_admin_edit a', place).click();
	equals($.jpoker.plugins.tourneyAdminList.schedule_serial.length, 3);

        cleanup();
    });

test("jpoker.plugins.tourneyAdminList create", function(){
        expect(5);

	var getResthost = $.jpoker.plugins.tourneyAdminList.getResthost;
	$.jpoker.plugins.tourneyAdminList.getResthost = function() {
	    $.jpoker.plugins.tourneyAdminList.getResthost = getResthost;
	};
	var getCurrencies = $.jpoker.plugins.tourneyAdminList.getCurrencies;
	$.jpoker.plugins.tourneyAdminList.getCurrencies = function() {
	    $.jpoker.plugins.tourneyAdminList.getCurrencies = getCurrencies;
	};

        var tourney_serial = 1111;
	var TOURNEY_LIST = [{"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+1, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "zzz abc80 test", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+2, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "blablabla 21", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}];
	var state = TOURNEY_LIST[1].state;

	var ajax = function(params) {
	    equals(params.url.indexOf('FROM+tourneys_schedule') >= 0, true, params.url);
            params.success(TOURNEY_LIST, 'status');
        };

        var place = $("#main");

	var expected = [3, 4];
        place.jpoker('tourneyAdminList', 'url', {ajax: ajax, callback: {display_done: function(element) {
			var tr = $('tbody tr', element);
			equals(tr.length, expected.shift(), 'number of rows');
		    }}});

	var tourneyCreate = $.jpoker.plugins.tourneyAdminList.tourneyCreate;
        $.jpoker.plugins.tourneyAdminList.tourneyCreate = function(url, options, callback) {
            equals(url.indexOf('pokersql') >= 0, true, url);
	    TOURNEY_LIST.push({"players_quota": 2, "players_min": 2, "breaks_first": 7200, "name" : "sitngo2", "description_short" : "Sit and Go 2 players, Holdem", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": tourney_serial+1, "sit_n_go": "y", "registered": 0});
	    callback();
        };

        $('thead .jpoker_admin_new a', place).click();

	$.jpoker.plugins.tourneyAdminList.tourneyCreate = tourneyCreate;
        cleanup();
    });

test("jpoker.plugins.tourneyAdminList delete", function(){
        expect(5);

	var getResthost = $.jpoker.plugins.tourneyAdminList.getResthost;
	$.jpoker.plugins.tourneyAdminList.getResthost = function() {
	    $.jpoker.plugins.tourneyAdminList.getResthost = getResthost;
	};
	var getCurrencies = $.jpoker.plugins.tourneyAdminList.getCurrencies;
	$.jpoker.plugins.tourneyAdminList.getCurrencies = function() {
	    $.jpoker.plugins.tourneyAdminList.getCurrencies = getCurrencies;
	};

        var tourney_serial = 1111;
	var TOURNEY_LIST = [{"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+1, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "zzz abc80 test", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+2, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "blablabla 21", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}];
	var state = TOURNEY_LIST[1].state;

	var ajax = function(params) {
	    equals(params.url.indexOf('FROM+tourneys_schedule') >= 0, true, params.url);
            params.success(TOURNEY_LIST, 'status');
        };

        var place = $("#main");

	var expected = [3, 2];
        place.jpoker('tourneyAdminList', 'url', {ajax: ajax, callback: {display_done: function(element) {
			var tr = $('tbody tr', element);
			equals(tr.length, expected.shift(), 'number of rows');
		    }}});

	var tourneyDelete = $.jpoker.plugins.tourneyAdminList.tourneyDelete;
        $.jpoker.plugins.tourneyAdminList.tourneyDelete = function(url, tourney_serial, options, callback) {
            equals(url.indexOf('pokersql') >= 0, true, url);
	    TOURNEY_LIST.shift();
	    callback();
        };

        $('tbody tr:eq(0) .jpoker_admin_delete a', place).click();

	$.jpoker.plugins.tourneyAdminList.tourneyDelete = tourneyDelete;
        cleanup();
    });

test("jpoker.plugins.tourneyAdminList.tourneyCreate", function() {
	expect(3);
	var ajax = function(params) {
	    equals(params.url.indexOf('INSERT+INTO+tourneys_schedule') >= 0, true, params.url);
	    equals(params.url.indexOf('SET+active+%3D+\'n\'') >= 0, true, params.url);
	    params.success(1, 'status');
	};	
	$.jpoker.plugins.tourneyAdminList.tourneyCreate('url', {ajax: ajax}, function() {
		ok(true, 'callback called');
	    });
    });

test("jpoker.plugins.tourneyAdminList.tourneyDelete", function() {
	expect(3);
	var ajax = function(params) {
	    equals(params.url.indexOf('DELETE+FROM+tourneys_schedule') >= 0, true, params.url);
	    equals(params.url.indexOf('WHERE+serial+%3D+\'111111\'') >= 0, true, params.url);
	    params.success(1, 'status');
	};	
	$.jpoker.plugins.tourneyAdminList.tourneyDelete('url', 111111, {ajax: ajax}, function() {
		ok(true, 'callback called');
	    });
    });

test("jpoker.plugins.tourneyAdminList multiple edit", function(){
        expect(3);

	var getResthost = $.jpoker.plugins.tourneyAdminList.getResthost;
	$.jpoker.plugins.tourneyAdminList.getResthost = function() {
	    $.jpoker.plugins.tourneyAdminList.getResthost = getResthost;
	};
	var getCurrencies = $.jpoker.plugins.tourneyAdminList.getCurrencies;
	$.jpoker.plugins.tourneyAdminList.getCurrencies = function() {
	    $.jpoker.plugins.tourneyAdminList.getCurrencies = getCurrencies;
	};

        var tourney_serial = 1111;
	var TOURNEY_LIST = [{"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+1, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "zzz abc80 test", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+2, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "blablabla 21", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}];

	var state = TOURNEY_LIST[1].state;
	
	var expected = ['SELECT', 'UPDATE', 'SELECT'];
	var results = [TOURNEY_LIST, 1, TOURNEY_LIST];

	var ajax = function(params) {
	    equals(params.url.indexOf(expected.shift()) >= 0, true, params.url);
            params.success(results.shift(), 'status');
        };
	
        var place = $("#main");

        place.jpoker('tourneyAdminList', 'url', {ajax: ajax, tourneyEditOptions: {ajax: ajax}});

        $('tbody tr:eq(0) .jpoker_admin_edit a', place).click();
	$('#jpokerAdminEdit input[name=description_short]').attr('value', 'TEXT1');
        $('tbody tr:eq(1) .jpoker_admin_edit a', place).click();
	$('#jpokerAdminEdit input[name=description_short]').attr('value', 'TEXT1');
        $('tbody tr:eq(2) .jpoker_admin_edit a', place).click();
	$('#jpokerAdminEdit input[name=description_short]').attr('value', 'TEXT1');
	$('#jpokerAdminEdit').triggerKeypress(13);
		
        cleanup();
    });

test("jpoker.tourneyAdminEdit", function(){
        expect(17);
        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30};
	
        $.jpoker.tourneyAdminEdit('URL', tourney);
        equals($('#jpokerAdminEdit .jpoker_admin_serial input').val(), tourney_serial);
        equals($('#jpokerAdminEdit .jpoker_admin_resthost_serial option').length, 2);
        equals($('#jpokerAdminEdit .jpoker_admin_currency_serial option').length, 3);
        var register_time = $('#jpokerAdminEdit .jpoker_admin_register_time input').val();
        var expected = '2009/01/28';
        equals(register_time.indexOf(expected) >= 0, true, register_time + ' does not contain ' + expected);
        equals($('#jpokerAdminEdit .jpoker_admin_currency_serial_from_date_format input').val(), '');
        equals($('#jpokerAdminEdit .jpoker_admin_description_short input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_players_quota input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_players_min input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_buy_in input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_breaks_first input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_breaks_interval input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_breaks_duration input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_name input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_player_timeout input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_seats_per_game input').length, 1);
        equals($('#jpokerAdminEdit .jpoker_admin_sit_n_go input').length, 2);
        equals($('#jpokerAdminEdit .jpoker_admin_betting_structure option').length, 5);
    });

test("jpoker.tourneyAdminEdit validation", function(){
        expect(17);

        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 1, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30};

        $.jpoker.tourneyAdminEdit('URL', tourney);

	$('#jpokerAdminEdit .jpoker_admin_players_min input').focus().val('0').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_players_min label.error').is(':visible'), 'error label shown');
	equals($('#jpokerAdminEdit .jpoker_admin_players_min label.error').text(), 'Please enter a value greater than or equal to 2.');
	$('#jpokerAdminEdit .jpoker_admin_players_min input').focus().val('3').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_players_min label.error').is(':hidden'), 'error label hidden');

	$('#jpokerAdminEdit .jpoker_admin_players_min input').focus().val('0').blur();

	$('#jpokerAdminEdit .jpoker_admin_players_quota input').focus().val('0').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_players_quota label.error').is(':visible'), 'error label shown');
	equals($('#jpokerAdminEdit .jpoker_admin_players_quota label.error').text(), 'Please enter a value greater than or equal to 2.');
	$('#jpokerAdminEdit .jpoker_admin_players_quota input').focus().val('3').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_players_quota label.error').is(':hidden'), 'error label hidden');

	$('#jpokerAdminEdit .jpoker_admin_players_min input').focus().val('10').blur();

	ok($('#jpokerAdminEdit .jpoker_admin_players_quota label.error').is(':hidden'), 'error label hidden');
	$('#jpokerAdminEdit .jpoker_admin_players_quota input').focus().val('5').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_players_quota label.error').is(':visible'), 'error label shown');
	equals($('#jpokerAdminEdit .jpoker_admin_players_quota label.error').text(), 'Player quota should be greater or equal to player min.');
	$('#jpokerAdminEdit .jpoker_admin_players_quota input').focus().val('20').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_players_quota label.error').is(':hidden'), 'error label hidden');

	$('#jpokerAdminEdit .jpoker_admin_seats_per_game input').focus().val('0').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_seats_per_game label.error').is(':visible'), 'error label shown');
	equals($('#jpokerAdminEdit .jpoker_admin_seats_per_game label.error').text(), 'Please enter a value between 2 and 10.');
	$('#jpokerAdminEdit .jpoker_admin_seats_per_game input').focus().val('3').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_seats_per_game label.error').is(':hidden'), 'error label hidden');

	$('#jpokerAdminEdit .jpoker_admin_player_timeout input').focus().val('0').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_player_timeout label.error').is(':visible'), 'error label shown');
	equals($('#jpokerAdminEdit .jpoker_admin_player_timeout label.error').text(), 'Please enter a value between 30 and 120.');
	$('#jpokerAdminEdit .jpoker_admin_player_timeout input').focus().val('200').blur();
	equals($('#jpokerAdminEdit .jpoker_admin_player_timeout label.error').text(), 'Please enter a value between 30 and 120.');
	$('#jpokerAdminEdit .jpoker_admin_player_timeout input').focus().val('100').blur();
	ok($('#jpokerAdminEdit .jpoker_admin_player_timeout label.error').is(':hidden'), 'error label hidden');
    });

test("jpoker.tourneyAdminEdit currency serial", function(){
        expect(11);

        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 1, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30};

	
	var expected = [function(params) {
		ok(params.url.indexOf('currency_serial+') == -1, 'currency_serial not updated:'+params.url);
		ok(params.url.indexOf('currency_serial_from_date_format') >= 0, 'currency_serial_from_date_format updated:'+params.url);
	    },
	    function (params) {
		ok(params.url.indexOf('currency_serial+') >= 0, 'currency_serial updated:'+params.url);
		ok(params.url.indexOf('currency_serial_from_date_format') >= 0, 'currency_serial_from_date_format updated:'+params.url);		
	    }];

	var options = {
	    ajax: function(params) {
		params.success(1, 'status');
		expected.shift()(params);
	    },
	    callback : {
		updated: function(tourney) {
		}
	    }	    
	};

        $.jpoker.tourneyAdminEdit('URL', tourney, options);
	equals($('#jpokerAdminEdit .jpoker_admin_currency_serial_from_date_format input').attr('readonly'), true, 'readonly');

	$('#jpokerAdminEdit .jpoker_admin_currency_serial select').val('from_date_format').change();
	equals($('#jpokerAdminEdit .jpoker_admin_currency_serial_from_date_format input').attr('readonly'), false, 'readonly');	
	$('#jpokerAdminEdit .jpoker_admin_currency_serial_from_date_format input').val('%Y%m');
	$('#jpokerAdminEdit .jpoker_admin_update button').click();

	equals(tourney.currency_serial_from_date_format, '%Y%m');
        $.jpoker.tourneyAdminEdit('URL', tourney, options);
	equals($('#jpokerAdminEdit .jpoker_admin_currency_serial_from_date_format input').attr('readonly'), false, 'readonly');
	equals($('#jpokerAdminEdit .jpoker_admin_currency_serial select').val(), 'from_date_format', 'from_date_format');	

	$('#jpokerAdminEdit .jpoker_admin_currency_serial select').val('euros').change();
	equals($('#jpokerAdminEdit .jpoker_admin_currency_serial_from_date_format input').attr('readonly'), true, 'readonly');
	$('#jpokerAdminEdit .jpoker_admin_update button').click();
	equals(tourney.currency_serial_from_date_format, '');
    });

test("jpoker.tourneyAdminEdit update", function(){
        expect(22);
        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "y", "add_on_delay": 60, "name": "regular1", "respawn": "y", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30, "via_satellite": 1, "satellite_player_count": 2, "satellite_of": 1};

	var options = {
	    ajax: function(params) {
		params.success(1, 'status');
		ok(params.url.indexOf('sit_n_go') >= 0, 'sit_n_go updated:'+params.url);
		ok(params.url.indexOf('respawn') >= 0, 'respawn updated:'+params.url);
		ok(params.url.indexOf('active') >= 0, 'active updated:'+params.url);
		ok(params.url.indexOf('via_satellite') >= 0, 'via_satellite updated:'+params.url);
		ok(params.url.indexOf('satellite_player_count') >= 0, 'satellite_player_count updated:'+params.url);
		ok(params.url.indexOf('satellite_of') >= 0, 'satellite_of updated:'+params.url);
	    },
	    callback : {
		updated: function(tourney) {
		    equals(tourney.serial, tourney_serial, 'updated');
		    equals(tourney.description_short, 'TEXT2', 'description_short updated');
		    equals(tourney.sit_n_go, 'y', 'sit_n_go updated');
		    equals(tourney.respawn, 'n', 'respawn updated');
		    equals(tourney.active, 'n', 'active updated');
		    equals(tourney.via_satellite, 0, 'via_satellite updated');
		    equals(tourney.satellite_player_count, 1, 'satellite_player_count updated');
		    equals(tourney.satellite_of, 2, 'satellite_of updated');
		}
	    }	    
	};

	var schedule_serial = $.jpoker.plugins.tourneyAdminList.schedule_serial;
	$.jpoker.plugins.tourneyAdminList.schedule_serial = [1, 2, 3];
        $.jpoker.tourneyAdminEdit('URL', tourney, options);
	equals($('#jpokerAdminEdit .jpoker_admin_update button').length, 1);
	equals($('.jpoker_admin_sit_n_go input[type=radio]').eq(1).is(":checked"), true);
	equals($('.jpoker_admin_respawn input[type=checkbox]').eq(0).is(":checked"), true);
	equals($('.jpoker_admin_active input[type=checkbox]').eq(0).is(":checked"), true);
	equals($('.jpoker_admin_via_satellite input[type=checkbox]').eq(0).is(":checked"), true);
	equals($('.jpoker_admin_satellite_player_count input[type=text]').eq(0).attr("value"), 2);
	equals($('.jpoker_admin_satellite_of select option').length, 4);
	equals($('.jpoker_admin_satellite_of select').val(), 1);

	$('#jpokerAdminEdit input[name=description_short]').attr('value', 'TEXT2');
	$('.jpoker_admin_sit_n_go input[type=radio]').eq(0).click();
	$('.jpoker_admin_respawn input[type=checkbox]').eq(0).click();
	$('.jpoker_admin_active input[type=checkbox]').eq(0).click();
	$('.jpoker_admin_via_satellite input[type=checkbox]').eq(0).click();
	$('.jpoker_admin_satellite_player_count input[type=text]').attr('value', 1);
	$('.jpoker_admin_satellite_of select').val(2);
	$('#jpokerAdminEdit .jpoker_admin_update button').click();
	$.jpoker.plugins.tourneyAdminList.schedule_serial = schedule_serial;
    });

test("jpoker.tourneyAdminEdit sitngo hide/show", function(){
        expect(4);
        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 30};

        $.jpoker.tourneyAdminEdit('URL', tourney);
	ok($('.jpoker_admin_register_time').is(':hidden'), 'register_time hidden');
	ok($('.jpoker_admin_start_time').is(':hidden'), 'start_time hidden');
	$('.jpoker_admin_sit_n_go input[type=radio]').eq(1).click(); // regular
	ok($('.jpoker_admin_register_time').is(':visible'), 'register_time visible');
	ok($('.jpoker_admin_start_time').is(':visible'), 'start_time visible');
    });

test("jpoker.plugins.tourneyAdminEdit", function(){
        expect(1);
        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30};

        $('#main').jpoker('tourneyAdminEdit', 'URL', tourney, {});
        equals($('#main .jpoker_admin_serial input').val(), tourney_serial);
    });

test("jpoker.plugins.tourneyAdminEdit update", function(){
        expect(6);

        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135540, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 1, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": '', "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30, "via_satellite": 0, "satellite_player_count": 0, "satellite_of": 0};

        var tourneyAdminEdit = $.jpoker.plugins.tourneyAdminEdit;
        var place = $("#main");
        var id = 'id1';
        place.html(tourneyAdminEdit.getHTML(tourney, tourneyAdminEdit.defaults));
        tourneyAdminEdit.decorate('url', place, tourney, tourneyAdminEdit.defaults);
        var options = $.extend({}, tourneyAdminEdit.defaults);

        //
        // nothing changed, nothing done
        //
        equals(tourneyAdminEdit.update('url', place, tourney, options), undefined, 'no change');
        
        var ajax;
        //
        // the pokersql webservice returns an unepxected number of modified rows, throw
        //
        try {
            $('input[name=description_short]', place).attr('value', 'TEXT0');
            ajax = function(params) {
                equals(params.url.indexOf('description_short') >= 0, true, 'name description_short');
                equals(params.url.indexOf('TEXT') >= 0, true, 'value description_short');
                params.success(5, undefined);
            };
            options.ajax = ajax;
            tourneyAdminEdit.update('url', place, tourney, options);
        } catch(e) {
            equals(e.toString().indexOf('modified 5 rows') >=0, true, e.toString());
        }

        //
        // the XHR request fails, throws
        //
        try {
            $('input[name=description_short]', place).attr('value', 'TEXT1');
            ajax = function(params) {
                params.error('xhr', 'status', 'ERROR');
            };
            options.ajax = ajax;
            tourneyAdminEdit.update('url', place, tourney, options);
        } catch(e) {
            equals(e.toString().indexOf('ERROR') >=0, true, e.toString());
        }

        //
        // the update succeeds
        //
        $('input[name=description_short]', place).attr('value', 'TEXT2');
        ajax = function(params) {
            params.success(1, 'status');
        };
        options.ajax = ajax;
        equals(tourneyAdminEdit.update('url', place, tourney, options), true, 'update succeeds');

        cleanup();
    });

test("jpoker.plugins.tourneyAdminList.getResthost", function() {
	expect(3);
	$.jpoker.plugins.tourneyAdminList.getResthost('url', {ajax: function(params) {
		    ok(params.url.indexOf('SELECT') >= 0, params.url);
		    ok(params.url.indexOf('resthost') >= 0, params.url);
		    params.success([{"host": "server1.com", "path": "/REST", "serial": 1, "name": "server1", "port": 1111}, {"host": "server2.com", "path": "/REST2", "serial": 2, "name": "server2", "port": 2222}], 'status');
		}});
	equals($.jpoker.plugins.tourneyAdminList.resthost.length, 2);
    });

test("jpoker.plugins.tourneyAdminList.getCurrencies", function() {
	expect(3);
	$.jpoker.plugins.tourneyAdminList.getCurrencies('url', {ajax: function(params) {
		    ok(params.url.indexOf('SELECT') >= 0, params.url);
		    ok(params.url.indexOf('currencies') >= 0, params.url);
		    params.success([{"url": "http://currency-server/", "cash_out": 0, "serial": 1, "symbol": "P", "name": "playmoney"}, {"url": "http://currency-server-euros/", "cash_out": 0, "serial": 2, "symbol": "E", "name": "euros"}], 'status');
		}});
	equals($.jpoker.plugins.tourneyAdminList.currencies.length, 2);
    });
