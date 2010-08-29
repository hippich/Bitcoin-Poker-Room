//
//     Copyright (C) 2009 Loic Dachary <loic@dachary.org>
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

module("jpokerprizes");

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

test("jpoker.tourneyAdminEditPrizes.getPrizes", function(){
        expect(1);
	var prizes = [{"serial": 1, "image_url": "url1"}, {"serial": 2, "image_url": "url2"}];

        var tourneyAdminEditPrizes = $.jpoker.plugins.tourneyAdminEditPrizes;
        var ajax = function(args) {
            args.success(prizes, 'success');
            equals(tourneyAdminEditPrizes.serial2prize[1].serial, 1);
        };
        tourneyAdminEditPrizes.getPrizes('URL', { ajax: ajax });
    });

test("jpoker.tourneyAdminEditPrizes", function(){
        expect(21);
        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135597, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30};
	var prizes = [{"serial": 1, "name": "prize 1", "image_url": "url1", description: null, link_url: null, points: 100}, {"serial": 2, "name": "prize 2", "image_url": "url2", description: null, link_url: null, points: 200}];

	var expected = ['SELECT+*+FROM+prizes', 'SELECT+p.serial+FROM+prizes', 'ON+DUPLICATE+KEY+UPDATE', 'ON+DUPLICATE+KEY+UPDATE'];
	var results = [prizes, [{"serial":1}], 1, 2];

	var options = {
	    ajax: function(params) {
		equals(params.url.indexOf('URL'), 0, params.url);
		ok(params.url.indexOf(expected.shift()) >= 0, params.url);
		params.success(results.shift(), 'success');
	    },
	    callback: {
		display_done: function(e) {
		    equals($('select[name=prize_serial] option', e).length, 2);
		    equals($('select[name=prize_serial] option', e).eq(0).text(), 'prize 1');
		    equals($('select[name=prize_serial] option', e).eq(1).text(), 'prize 2');
		}
	    }
	};

	$.jpoker.tourneyAdminEditPrizes('URL', tourney, options);
	equals($('#jpokerAdminEdit').length, 1, 'admin edit dialog');
	equals($('#jpokerAdminEditPrizes').length, 1, 'admin edit prizes');
	equals($('#jpokerAdminEditPrizes form').length, 1, 'admin edit prizes form');
	equals($('#jpokerAdminEditPrizes form fieldset').length, 1, 'admin edit prizes from fieldset');
	equals($('#jpokerAdminEditPrizes form fieldset input[readonly]').length, 2, 'admin edit prizes from fieldset input');
	equals($('.jpoker_prize_description input').val(), '');
	equals($('.jpoker_prize_image a').attr('href'), '');
	equals($('.jpoker_prize_points input').val(), 100);
	$('#jpokerAdminEditPrizes select[name=prize_serial]').val('2').change();
	equals($('#jpokerAdminEditPrizes .jpoker_prize img').attr('src'),  'url2');
	$('#jpokerAdminEditPrizes select[name=prize_serial]').val('1').change();
	equals($('#jpokerAdminEditPrizes .jpoker_prize img').attr('src'),  'url1');
	
	cleanup();
    });


test("jpoker.tourneyAdminEditPrizes no serial defined", function(){
        expect(15);
        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135597, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30};
	var prizes = [{"serial": 1, "name": "prize 1", "image_url": "url1", description: null, link_url: null}, {"serial": 2, "name": "prize 2", "image_url": "url2", description: null, link_url: null}];

	var expected = ['SELECT+*+FROM+prizes', 'SELECT+p.serial+FROM+prizes', 'ON+DUPLICATE+KEY+UPDATE', 'ON+DUPLICATE+KEY+UPDATE'];
	var results = [prizes, [], 1, 2];

	var options = {
	    ajax: function(params) {
		equals(params.url.indexOf('URL'), 0, params.url);
		ok(params.url.indexOf(expected.shift()) >= 0, params.url);
		params.success(results.shift(), 'success');
	    },
	    callback: {
		display_done: function(e) {
		    equals($('select[name=prize_serial] option', e).length, 2);
		    equals($('select[name=prize_serial] option', e).eq(0).text(), 'prize 1');
		    equals($('select[name=prize_serial] option', e).eq(1).text(), 'prize 2');
		}
	    }
	};

	$.jpoker.tourneyAdminEditPrizes('URL', tourney, options);
	equals($('#jpokerAdminEdit').length, 1, 'admin edit dialog');
	equals($('#jpokerAdminEditPrizes').length, 1, 'admin edit prizes');
	equals($('#jpokerAdminEditPrizes .jpoker_prize img').attr('src'),  'url1');
	$('#jpokerAdminEditPrizes select[name=prize_serial]').val('2').change();
	equals($('#jpokerAdminEditPrizes .jpoker_prize img').attr('src'),  'url2');
	
	cleanup();
    });

test("jpoker.tourneyAdminEditPrizes update", function(){
        expect(4);

	$.jpoker.plugins.tourneyAdminList.resthost = [{"host": "server1.com", "path": "/REST", "serial": 1, "name": "server1", "port": 1111}, {"host": "server2.com", "path": "/REST2", "serial": 2, "name": "server2", "port": 2222}];

        var tourney_serial = 1111;
	var tourney = {"register_time": 1233135597, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 1, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30};

	var prizes = [{"serial": 1, "name": "prize 1", "image_url": "url1"}, {"serial": 2, "name": "prize 2", "image_url": "url2"}];
	var results = [prizes, [], 1, 1];

	var options = {
	    ajax: function(params) {
		var result = results.shift();
		params.success(result, 'status');
	    },
	    callback : {
		updated: function(tourney) {
		    equals(tourney.serial, tourney_serial, 'updated');
		    equals(tourney.prize_serial, undefined, 'prize serial should not be set in tourney object');
		}
	    }	    
	};

        $.jpoker.tourneyAdminEditPrizes('URL', tourney, options);
	$('#jpokerAdminEdit input[name=description_short]').attr('value', 'TEXT2');
	$("#jpokerAdminEdit .jpoker_admin_update button").click();
	cleanup();
    });

test("jpoker.plugins.tourneyAdminList with prizes", function(){
        expect(7);

	var getResthost = $.jpoker.plugins.tourneyAdminList.getResthost;
	$.jpoker.plugins.tourneyAdminList.getResthost = function() {
	    $.jpoker.plugins.tourneyAdminList.getResthost = getResthost;
	}
	var getCurrencies = $.jpoker.plugins.tourneyAdminList.getCurrencies;
	$.jpoker.plugins.tourneyAdminList.getCurrencies = function() {
	    $.jpoker.plugins.tourneyAdminList.getCurrencies = getCurrencies;
	}

        var tourney_serial = 1111;
	var TOURNEY_LIST = [{"register_time": 1233135597, "betting_structure": "level-001", "currency_serial": 1, "description_long": "Holdem No Limit Freeroll", "breaks_interval": 60, "serial": tourney_serial, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "111 asdasdasdasd", "player_timeout": 60, "players_quota": 1000, "rake": 0, "add_on": 1, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 3, "active": "n", "add_on_delay": 60, "name": "regular1", "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 30}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+1, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "zzz abc80 test", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, {"register_time": 0, "betting_structure": "level-001", "currency_serial": null, "description_long": null, "breaks_interval": 3600, "serial": tourney_serial+2, "resthost_serial": 0, "buy_in": 0, "respawn_interval": 0, "description_short": "blablabla 21", "player_timeout": 60, "players_quota": 10, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "active": "n", "add_on_delay": 60, "name": null, "respawn": "n", "prize_min": 0, "currency_serial_from_date_format": null, "breaks_duration": 300, "seats_per_game": 10, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}];

	var state = TOURNEY_LIST[1].state;
	var prizes = [{tourneys_schedule_serial:tourney_serial, name:'prize A'}];       

	var excepted = ['FROM+tourneys_schedule', 'FROM+prizes'];
	var results = [TOURNEY_LIST, prizes];

	var ajax = function(params) {
	    equals(params.url.indexOf(excepted.shift()) >= 0, true, params.url);
            params.success(results.shift(), 'status');
        };
	
        var place = $("#main");
	
        place.jpoker('tourneyAdminList', 'url', {ajax: ajax});

	var tr = $('tbody tr', place);
	equals(tr.length, 3, 'number of rows');
	var th = $('thead tr:nth-child(1) th', place);
	equals(th.length, 8, 'number of column');
	var td = $('tbody tr:nth-child(1) td', place);
	equals(td.length, 8, 'number of column');
	var prize = $('tbody tr:nth-child(1) .jpoker_tourney_prize', place);
	equals(prize.length, 1, 'prize, element');
	equals(prize.text(), 'prize A');
	
        cleanup();
    });