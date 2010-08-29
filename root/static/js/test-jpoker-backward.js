//
//     Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
//     Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
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

//
// The tests here have been obsoleted and their sole purpose is to help 
// with backward compatibility. If they fail, there is a good chance existing 
// applications on top of jpoker will fail in the same way.
// 
// MUST BE INCLUDED AFTER test-jpoker.js BECAUSE IT RELIES ON ITS FUNCTIONS
//

//
// regularTourneyList
//
module("backward jpoker");

test("jpoker.plugins.regularTourneyList", function(){
        expect(18);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [{"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "registering", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "announced", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"};
	var start_time = new Date(TOURNEY_LIST_PACKET.packets[1].start_time*1000).toLocaleString();
	var state = TOURNEY_LIST_PACKET.packets[1].state;

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) {
                if(packet.indexOf('PacketPokerTourneySelect') >= 0) {
                    equals(packet.indexOf('regular') >0, true, JSON.stringify(packet));
                }
            }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var row_id = TOURNEY_LIST_PACKET.packets[1].serial + id;
        var place = $("#main");
        equals('update' in server.callbacks, false, 'no update registered');
	var display_done = jpoker.plugins.regularTourneyList.callback.display_done;
	jpoker.plugins.regularTourneyList.callback.display_done = function(element) {
	    jpoker.plugins.regularTourneyList.callback.display_done = display_done;
	    equals($(".jpoker_regular_tourney_list", $(element).parent()).length, 1, 'display done called when DOM is done');
	};
        place.jpoker('regularTourneyList', 'url', { delay: 30 });
        equals(server.callbacks.update.length, 1, 'regularTourneyList update registered');
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
                    var tr = $("#" + id + " tr", place);
                    var row = $("#" + row_id, place);
                    equals(tr.length, 4+1);
                    equals($('td:nth-child(5)', row).text(), start_time, 'start_time');
		    equals($('td:nth-child(6)', row).text(), state, 'state');
		    equals($('.headerSortDown', tr[0]).text(), 'Start Time', "headerSortDown");
		    server.tourneyRowClick = function(server, subpacket) {
			equals(subpacket.serial, TOURNEY_LIST_PACKET.packets[0].serial, 'tourneyRowClick called');
		    };
		    ok(tr.eq(1).hasClass('jpoker_tourney_state_registering'), 'registering css class');
		    tr.eq(1).click();
		    server.tourneyRowClick = function(server, subpacket) {
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
                    equals(server.callbacks.update.length, 2, 'regularTourneyList and test update registered');
                    equals('tourneyList' in server.timers, false, 'timer active');
                    server.setTimeout = function(fun, delay) { };
                    window.setTimeout(function() {
                            start_and_cleanup();
                        }, 30);
                    return false;
                }
            });
        server.registerDestroy(function(server) {
                equals('tourneyList' in server.timers, false, 'timer killed');
                equals(server.callbacks.update.length, 0, 'update & destroy unregistered');
            });
    });

test("jpoker.plugins.regularTourneyList date template", function(){
        expect(1);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [{"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "registering", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "announced", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"};
	var date_format = "%Y/%m/%d %H:%M:%S";
	var start_time = $.strftime(date_format, new Date(TOURNEY_LIST_PACKET.packets[1].start_time*1000));
	var state = TOURNEY_LIST_PACKET.packets[1].state;
	jpoker.plugins.regularTourneyList.templates.date = date_format

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) {
            }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var row_id = TOURNEY_LIST_PACKET.packets[1].serial + id;
        var place = $("#main");
        place.jpoker('regularTourneyList', 'url', { delay: 30 });
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
                    var tr = $("#" + id + " tr", place);
                    var row = $("#" + row_id, place);
                    equals($('td:nth-child(5)', row).text(), start_time, 'start_time');
                    $("#" + id).remove();
                    return true;
                } else {
                    server.setTimeout = function(fun, delay) { };
                    window.setTimeout(function() {
			    jpoker.plugins.regularTourneyList.templates.date = '';
                            start_and_cleanup();
                        }, 30);
                    return false;
                }
            });
    });

test("jpoker.plugins.regularTourneyList link_pattern", function(){
        expect(4);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [{"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "registering", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "announced", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"};
	var state = TOURNEY_LIST_PACKET.packets[1].state;

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) { }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var row_id = TOURNEY_LIST_PACKET.packets[1].serial + id;
        var place = $("#main");
	var link_pattern = 'http://foo.com/tourney?tourney_serial={tourney_serial}';
        place.jpoker('regularTourneyList', 'url', { delay: 30, link_pattern: link_pattern });
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
                    var tr = $("#" + id + " tr", place);
		    server.tourneyRowClick = function(server, subpacket) {
			ok(false, 'tourneyRowClick disabled');
		    };
		    tr.eq(1).click();
		    var link = link_pattern.supplant({tourney_serial: TOURNEY_LIST_PACKET.packets[0].serial});
		    ok($('td:nth-child(1)', tr.eq(1)).html().indexOf(link)>=0, link);
		    equals($('td:nth-child(1) a', tr.eq(1)).length, 1, 'link');
		    equals($('td:nth-child(1) a', tr.eq(2)).length, 0, 'no link for announced');
		    equals($('td:nth-child(1) a', tr.eq(3)).length, 0, 'no link for canceled');
                    $("#" + id).remove();
                    return true;
                } else {
		    start_and_cleanup();
                    return false;
                }
            });
    });

test("jpoker.plugins.regularTourneyList pager", function(){
        expect(6);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"};
	for (var i = 0; i < 30; ++i) {
	    var name = "Tourney" + i;
	    var serial = 100+i;
	    var players = i%11;
	    var packet = {"players_quota": players, "breaks_first": 7200, "name": name, "description_short" : name, "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": serial, "sit_n_go": "n", "registered": 0};
	    TOURNEY_LIST_PACKET.packets.push(packet);
	}

	var state = TOURNEY_LIST_PACKET.packets[1].state;

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) { }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var row_id = TOURNEY_LIST_PACKET.packets[1].serial + id;
        var place = $("#main");
        place.jpoker('regularTourneyList', 'url', { delay: 30 });
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
		    equals($('.pager', element).length, 1, 'has pager');
		    equals($('.pager .current', element).length, 1, 'has current page');
		    ok($('.pager li:last', element).text().indexOf(">>>") >= 0, 'has next page');
		    $('.pager li:last a', element).click();
		    ok($('.pager li:first', element).text().indexOf("<<<") >= 0, 'has previous page');
		    var row = $('table tr', place).eq(1);
		    equals(row.length, 1, 'row element');
		    server.tourneyRowClick = function(server, subpacket) {
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

//
// sitngoTourneyList
//
test("jpoker.plugins.sitngoTourneyList", function(){
        expect(16);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [{"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0}], "tourneys": 1, "type": "PacketPokerTourneyList"};
	var buy_in = TOURNEY_LIST_PACKET.packets[0].buy_in/100;
	var state = TOURNEY_LIST_PACKET.packets[0].state;

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) {
                if(packet.indexOf('PacketPokerTourneySelect') >= 0) {
                    equals(packet.indexOf('sit_n_go') >0, true, JSON.stringify(packet));
                }
            }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var row_id = TOURNEY_LIST_PACKET.packets[0].serial + id;
        var place = $("#main");
        equals('update' in server.callbacks, false, 'no update registered');
	var display_done = jpoker.plugins.sitngoTourneyList.callback.display_done;
	jpoker.plugins.sitngoTourneyList.callback.display_done = function(element) {
	    jpoker.plugins.sitngoTourneyList.callback.display_done = display_done;
	    equals($(".jpoker_sitngo_tourney_list", $(element).parent()).length, 1, 'display done called when DOM is done');
	};
        place.jpoker('sitngoTourneyList', 'url', { delay: 30 });
        equals(server.callbacks.update.length, 1, 'sitngoTourneyList update registered');
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
                    var tr = $("#" + id + " tr", place);
                    var row = $("#" + row_id, place);
                    equals(tr.length, 1+1);
                    equals($('td:nth-child(4)', row).text(), buy_in, 'buy in');
		    equals($('td:nth-child(5)', row).text(), state, 'state');
		    equals($('.headerSortDown', tr[0]).text(), 'Buy In', "headerSortDown");
		    server.tourneyRowClick = function(server, subpacket) {
			equals(subpacket.serial, TOURNEY_LIST_PACKET.packets[0].serial, 'tourneyRowClick called');
		    };
		    ok(row.hasClass('jpoker_tourney_state_registering'), 'registering css class');
		    row.click();
		    row.trigger('mouseenter');
		    equals(row.hasClass('hover'), true, 'hasClass hover');
		    row.trigger('mouseleave');
		    equals(row.hasClass('hover'), false, '!hasClass hover');
                    $("#" + id).remove();
                    return true;
                } else {
                    equals(server.callbacks.update.length, 2, 'sitngoTourneyList and test update registered');
                    equals('tourneyList' in server.timers, false, 'timer active');
                    server.setTimeout = function(fun, delay) { };
                    window.setTimeout(function() {
                            start_and_cleanup();
                        }, 30);
                    return false;
                }
            });
        server.registerDestroy(function(server) {
                equals('tourneyList' in server.timers, false, 'timer killed');
                equals(server.callbacks.update.length, 0, 'update & destroy unregistered');
            });
    });

test("jpoker.plugins.sitngoTourneyList link pattern", function(){
        expect(1);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [{"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll", "start_time": 1216201024, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"};
	var buy_in = TOURNEY_LIST_PACKET.packets[0].buy_in/100;
	var state = TOURNEY_LIST_PACKET.packets[0].state;

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) { }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var row_id = TOURNEY_LIST_PACKET.packets[0].serial + id;
        var place = $("#main");
	var link_pattern = 'http://foo.com/tourney?tourney_serial={tourney_serial}';
        place.jpoker('sitngoTourneyList', 'url', { delay: 30, link_pattern: link_pattern });
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
                    var row = $("#" + row_id, place);
		    server.tourneyRowClick = function(server, subpacket) {
			ok(false, 'tourneyRowClick disabled');
		    };
		    row.click();
		    var link = link_pattern.supplant({tourney_serial: TOURNEY_LIST_PACKET.packets[0].serial});
		    ok($('td:nth-child(1)', row).html().indexOf(link)>=0, link);
                    $("#" + id).remove();
                    return true;
                } else {
		    start_and_cleanup();
                    return false;
                }
            });
    });

test("jpoker.plugins.sitngoTourneyList pager", function(){
        expect(6);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"};
	for (var i = 0; i < 30; ++i) {
	    var name = "Tourney" + i;
	    var players = i%11;
	    var serial = i + 100;
	    var packet = {"players_quota": players, "breaks_first": 7200, "name": name, "description_short" : name, "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": serial, "sit_n_go": "y", "registered": 0};
	    TOURNEY_LIST_PACKET.packets.push(packet);
	}

	var state = TOURNEY_LIST_PACKET.packets[1].state;

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) { }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var row_id = TOURNEY_LIST_PACKET.packets[1].serial + id;
        var place = $("#main");
        place.jpoker('sitngoTourneyList', 'url', { delay: 30 });
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
		    equals($('.pager', element).length, 1, 'has pager');
		    equals($('.pager .current', element).length, 1, 'has current page');
		    ok($('.pager li:last', element).text().indexOf(">>>") >= 0, 'has next page');
		    $('.pager li:last a', element).click();
		    ok($('.pager li:first', element).text().indexOf("<<<") >= 0, 'has previous page');
		    var row = $('table tr', place).eq(1);
		    equals(row.length, 1, 'row element');
		    server.tourneyRowClick = function(server, subpacket) {
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

test("jpoker.plugins.regularTourneyList empty", function(){
        expect(2);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"};

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) { }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var place = $("#main");
	var template = jpoker.plugins.regularTourneyList.templates.header;
	jpoker.plugins.regularTourneyList.templates.header = '<table><thead><tr><th>{description_short}</th></tr><tr><th>{registered}</th></tr></thead><tbody>';
        place.jpoker('regularTourneyList', 'url', { delay: 30 });
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
                    var tr = $("#" + id + " tr", place);
                    equals(tr.length, 2);
		    equals($(".header", element).length, 0, 'no tablesorter');
                    $("#" + id).remove();
                    return true;
                } else {
                    window.setTimeout(function() {
			    jpoker.plugins.regularTourneyList.templates.header = template;
                            start_and_cleanup();
                        }, 30);
                    return false;
                }
            });
    });

test("jpoker.plugins.sitngoTourneyList empty", function(){
        expect(2);
        stop();

        //
        // Mockup server that will always return TOURNEY_LIST_PACKET,
        // whatever is sent to it.
        //
        var PokerServer = function() {};

	var TOURNEY_LIST_PACKET = {"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"};

        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_LIST_PACKET) + " ]",

            handle: function(packet) { }
        };

        ActiveXObject.prototype.server = new PokerServer();

        var server = jpoker.serverCreate({ url: 'url' });
        server.connectionState = 'connected';

        var id = 'jpoker' + jpoker.serial;
        var place = $("#main");
	var template = jpoker.plugins.sitngoTourneyList.templates.header;
	jpoker.plugins.sitngoTourneyList.templates.header = '<table><thead><tr><th>{description_short}</th></tr><tr><th>{registered}</th></tr></thead><tbody>';
        place.jpoker('sitngoTourneyList', 'url', { delay: 30 });
        server.registerUpdate(function(server, what, data) {
                var element = $("#" + id);
                if(element.length > 0) {
                    var tr = $("#" + id + " tr", place);
                    equals(tr.length, 2);
		    equals($(".header", element).length, 0, 'no tablesorter');
                    $("#" + id).remove();
                    return true;
                } else {
                    jpoker.plugins.sitngoTourneyList.templates.header = template;
                    window.setTimeout(function() {
                            start_and_cleanup();
                        }, 30);
                    return false;
                }
            });
    });



