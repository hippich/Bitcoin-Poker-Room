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
(function($) {
    var jpoker = $.jpoker;

    jpoker.admin = function(selector) {	
        $(selector).jpoker('tourneyAdminList', '', {});
    };

    jpoker.tourneyAdminEdit = function(url, tourney, options) {
        var dialog = $('#jpokerAdminEdit');
        if(dialog.size() != 1) {
            $('body').append('<div id=\'jpokerAdminEdit\' class=\'jpoker_jquery_ui\' />');
            dialog = $('#jpokerAdminEdit');
            dialog.dialog({ width: '800px', height: '600px', autoOpen: false, dialog: true, title: 'edit tournament'});
        }
        dialog.jpoker('tourneyAdminEdit', url, tourney, options);
        dialog.dialog('open');
	$.validator.methods.greaterOrEqual = function(value, element, param) {
	    return parseInt(value, 10) >= parseInt($(param).val(), 10);
	};
	$("form", dialog).validate({
		ignoreTitle: true,
		    rules: {
		    players_min: {
			min: 2
			    },
			players_quota: {
			min: 2,
			    greaterOrEqual: '.jpoker_admin_players_min input'
			    },
			seats_per_game: {
			range: [2, 10]
			    },
			player_timeout: {
			range: [30, 120]
			    }
		},
		    messages: {
		    players_quota: {
			greaterOrEqual: 'Player quota should be greater or equal to player min.'
			    }
		}
	    });
        return dialog;
    };

    //
    // tourneyAdminEdit
    //
    jpoker.plugins.tourneyAdminEdit = function(url, tourney, options) {

        var tourneyAdminEdit = jpoker.plugins.tourneyAdminEdit;
        var opts = $.extend({}, tourneyAdminEdit.defaults, options);

	for (var k in tourney) {
	    if (tourney[k] === null) {
		tourney[k] = '';
	    }
	}

        return this.each(function() {
                var $this = $(this);

                $this.html(tourneyAdminEdit.getHTML(tourney, opts));
                tourneyAdminEdit.decorate(url, $this, tourney, opts);
                return this;
            });
    };

    jpoker.plugins.tourneyAdminEdit.update = function(url, element, tourney, options) {
        var setters = [];
        var inputs = $('.jpoker_admin_tourney_params input[type=text]', element);
        for(var i = 0; i < inputs.length; i++) {
            var name = $.attr(inputs[i], 'name');
            var value = $.attr(inputs[i], 'value');
            if(name == 'start_time' || name == 'register_time') {
                value = Date.parseDate(value, options.dateFormat).valueOf() / 1000;
            }
            if(tourney[name] != value) {
                setters.push(name + ' = \'' + value.toString() + '\'');
                tourney[name] = value;
            }
        }
	name = 'sit_n_go';
	if ($('.jpoker_admin_sit_n_go input[type=radio]')[0].checked) {
	    value = 'y';
	} else if ($('.jpoker_admin_sit_n_go input[type=radio]')[1].checked) {
	    value = 'n';
	}
	if (tourney[name] != value) {
	    tourney[name] = value;
	    setters.push(name + ' = \'' + value + '\'');
	}

	name = 'respawn';
	if ($('.jpoker_admin_respawn input[type=checkbox]')[0].checked) {
	    value = 'y';
	} else {
	    value = 'n';
	}
	if (tourney[name] != value) {
	    tourney[name] = value;
	    setters.push(name + ' = \'' + value + '\'');
	}

	name = 'active';
	if ($('.jpoker_admin_active input[type=checkbox]')[0].checked) {
	    value = 'y';
	} else {
	    value = 'n';
	}
	if (tourney[name] != value) {
	    tourney[name] = value;
	    setters.push(name + ' = \'' + value + '\'');
	}

	name = 'via_satellite';
	if ($('.jpoker_admin_via_satellite input[type=checkbox]')[0].checked) {
	    value = 1;
	} else {
	    value = 0;
	}
	if (tourney[name] != value) {
	    tourney[name] = value;
	    setters.push(name + ' = \'' + value.toString() + '\'');
	}

        $('.jpoker_admin_tourney_params select', element).each(function() {
                name = $(this).attr('name');
                value = $('option:selected', this).val();
		if (value && value != 'from_date_format') {
		    if (tourney[name] != value) {
			setters.push(name + ' = \'' + value.toString() + '\'');
			tourney[name] = value;
		    }
		}
            });

        if(setters.length === 0) {
            return undefined;
        }
            
        var params = {
            'query': 'UPDATE tourneys_schedule SET ' + setters.join(',') + ' WHERE serial = ' + tourney.serial.toString()
        };

        var error = function(xhr, status, error) {
            throw error;
        };

        var success = function(rowcount, status) {
            if(rowcount != 1) {
                throw 'expected ' + params.query + ' to modify exactly one row but it modified ' + rowcount.toString() + ' rows instead';
            }
            options.callback.updated(tourney);
        };

        options.ajax({
                async: false,
                    timeout: 30000,
                    url: url + '?' + $.param(params),
                    type: 'GET',
                    dataType: 'json',
                    global: false,
                    success: success,
                    error: error
                    });
        return true;
    };

    jpoker.plugins.tourneyAdminEdit.decorate = function(url, element, tourney, options) {

        var tourneyAdminEdit = jpoker.plugins.tourneyAdminEdit;

        element.unbind('keypress').keypress(function(event) {
                if(event.which == 13) {
                    tourneyAdminEdit.update(url, element, tourney, options);
                }
            });
	$('.jpoker_admin_update button').click(function() {
		tourneyAdminEdit.update(url, element, tourney, options);
	    });
        $('.jpoker_admin_tourney_params select', element).each(function() {
                var name = $(this).attr('name');
                $(this).val(tourney[name]);
            }); 
	if (tourney.sit_n_go == 'y') {
	    $('.jpoker_admin_sit_n_go input[type=radio]')[0].checked = true;
	} else {
	    $('.jpoker_admin_sit_n_go input[type=radio]')[1].checked = true;
	}
	if (tourney.respawn == 'y') {
	    $('.jpoker_admin_respawn input[type=checkbox]')[0].checked = true;
	} else {
	    $('.jpoker_admin_respawn input[type=checkbox]')[0].checked = false;
	}
	if (tourney.active == 'y') {
	    $('.jpoker_admin_active input[type=checkbox]')[0].checked = true;
	} else {
	    $('.jpoker_admin_active input[type=checkbox]')[0].checked = false;
	}
	if (tourney.via_satellite == 1) {
	    $('.jpoker_admin_via_satellite input[type=checkbox]')[0].checked = true;
	} else {
	    $('.jpoker_admin_via_satellite input[type=checkbox]')[0].checked = false;
	}
        $('input[name=start_time],input[name=register_time]', element).dynDateTime({
                showsTime: true,
                    ifFormat: options.dateFormat,
                    align: "TL",
                    electric: false,
                    singleClick: false,
                    button: ".next()" //next sibling
                    });
	var sitngo = $('.jpoker_admin_sit_n_go input[type=radio]', element).eq(0);
	var regular = $('.jpoker_admin_sit_n_go input[type=radio]', element).eq(1);
	var times = $('.jpoker_admin_register_time, .jpoker_admin_start_time', element);
	sitngo.click(function() {
		times.hide();
	    });
	regular.click(function() {
		times.show();
	    });
	if (tourney.sit_n_go == 'y') {
	    sitngo.click();
	} else {
	    regular.click();
	}
	if (tourney.currency_serial_from_date_format.length > 0) {
	    $('.jpoker_admin_currency_serial select', element).val('from_date_format');
	    $('.jpoker_admin_currency_serial_from_date_format input', element).attr('readonly', false);
	}
	$('.jpoker_admin_currency_serial select', element).change(function() {
		var enabled = $(this).val() != 'from_date_format';
		$('.jpoker_admin_currency_serial_from_date_format input', element).val('').attr('readonly', enabled);
	    });
    };

    jpoker.plugins.tourneyAdminEdit.getHTML = function(tourney, options) {
        tourney.start_time_string = new Date(tourney.start_time*1000).print(options.dateFormat);
        tourney.register_time_string = new Date(tourney.register_time*1000).print(options.dateFormat);
	var resthost_html = $.map(jpoker.plugins.tourneyAdminList.resthost, function(host, i) {
		return options.templates.resthost_serial_option.supplant(host);
	    }).join('');
	var currencies_html = $.map(jpoker.plugins.tourneyAdminList.currencies, function(currency, i) {
		return options.templates.currency_serial_option.supplant(currency);
	    }).join('');
	var schedule_serial_html = $.map(jpoker.plugins.tourneyAdminList.schedule_serial, function(schedule_serial, i) {
		return options.templates.satellite_of_option.supplant({schedule_serial: schedule_serial});
	    }).join('');
	var resthost_serial_select = options.templates.resthost_serial_select.supplant({options: resthost_html});
	var currency_serial_select = options.templates.currency_serial_select.supplant({options: currencies_html});
	var satellite_of_select = options.templates.satellite_of_select.supplant({options: schedule_serial_html});
        var html = options.templates.layout.supplant({resthost_serial_select: resthost_serial_select,
						      currency_serial_select: currency_serial_select,
						      satellite_of_select:  satellite_of_select}).supplant(options.templates);
        return html.supplant(tourney);
    };

    jpoker.plugins.tourneyAdminEdit.defaults = $.extend({
            dateFormat: '%Y/%m/%d-%H:%M',
            path: '/cgi-bin/poker-network/pokersql',
            templates: {
                layout: '<form action=\'javascript://\'><div class=\'jpoker_admin_tourney_params\'>{sit_n_go}{start_time}{register_time}{resthost_serial_select}{serial}{name}{description_short}{description_long}{variant}{betting_structure}{players_min}{players_quota}{seats_per_game}{player_timeout}{currency_serial_select}{currency_serial_from_date_format}{buy_in}{rake}{prize_min}{bailor_serial}{breaks_first}{breaks_interval}{breaks_duration}{via_satellite}{satellite_of_select}{satellite_player_count}{respawn}{active}</div>{update}</form>',
		serial: '<div class=\'jpoker_admin_serial\'><label for=\'jpoker_admin_serial_input\'>Serial</label><input id=\'jpoker_admin_serial_input\' name=\'serial\' title=\'Serial of the tournament.\' value=\'{serial}\' readonly=\'true\'  maxlength=\'5\' size=\'5\' /></div>',
		resthost_serial_select: '<div class=\'jpoker_admin_resthost_serial\'><label for=\'jpoker_admin_resthost_serial_input\'>Rest host serial</label><select id=\'jpoker_admin_resthost_serial_input\' name=\'resthost_serial\' title=\'Serial of the server.\'>{options}</select></div>',
		resthost_serial_option: '<option value=\'{serial}\'>{host}:{port}{path}</option>',
                variant: '<div class=\'jpoker_admin_variant\'><label for=\'jpoker_admin_variant_input\'>Variant</label><select id=\'jpoker_admin_variant_input\' name=\'variant\'><option value=\'holdem\'>Holdem</option><option value=\'omaha\'>Omaha</option><option value=\'omaha8\'>Omaha High/Low</option></select></div>',
                betting_structure: '<div class=\'jpoker_admin_betting_structure\'><label for=\'jpoker_admin_betting_structure_input\'>Betting structure</label><select id=\'jpoker_admin_betting_structure_input\' name=\'betting_structure\'><option value=\'level-001\'>No limit tournament</option><option value=\'level-10-15-pot-limit\'>Pot limit 10/15</option><option value=\'level-10-20-no-limit\'>No limit 10/20</option><option value=\'level-15-30-no-limit\'>No limit 15/30</option><option value=\'level-2-4-limit\'>Limit 2/4</option></select></div>',
                start_time: '<div class=\'jpoker_admin_start_time\'><label for=\'jpoker_admin_start_time_input\'>Start time</label><input id=\'jpoker_admin_start_time_input\' type=\'text\' size=\'16\' maxlength=\'16\' value=\'{start_time_string}\' name=\'start_time\' title=\'Time and date of the tournament start.\' /><button type=\'button\'>pick</button></label></div>',
                register_time: '<div class=\'jpoker_admin_register_time\'><label for=\'jpoker_admin_register_time_input\'>Register time</label><input id=\'jpoker_admin_register_time_input\' type=\'text\' size=\'16\' maxlength=\'16\' value=\'{register_time_string}\' name=\'register_time\' title=\'Time and date of the registration.\' /><button type=\'button\'>pick</button></div>',
                description_short: '<div class=\'jpoker_admin_description_short\'><label for=\'jpoker_admin_description_short_input\'>Description short</label><input id=\'jpoker_admin_description_short_input\' name=\'description_short\' title=\'Short description of the tournament. It will be displayed on each line of the tournament list.\' value=\'{description_short}\' maxlength=\'64\' size=\'20\' /></div>',
                description_long: '<div class=\'jpoker_admin_description_long\'><label for=\'jpoker_admin_description_long_input\'>Description long</label><textarea id=\'jpoker_admin_description_long_input\' name=\'description_long\' title=\'Description that will be shown on a detailed page about the tournament.\' value=\'{description_long}\' /></div>',
		players_quota: '<div class=\'jpoker_admin_players_quota\'><label for=\'jpoker_admin_players_quota_input\'>Player quota</label><input id=\'jpoker_admin_players_quota_input\' name=\'players_quota\' title=\'The maximum number of players allowed to register in the tournament\' value=\'{players_quota}\' maxlength=\'4\' size=\'4\' /></div>',
		players_min: '<div class=\'jpoker_admin_players_min\'><label for=\'jpoker_admin_players_min_input\'>Player min</label><input id=\'jpoker_admin_players_min_input\' name=\'players_min\' title=\'The minimum number of players to start the tournament. If the number of registered players in the tournament is less than this limit, the tournament is canceled\' value=\'{players_min}\' maxlength=\'4\' size=\'4\' /></div>',
		buy_in: '<div class=\'jpoker_admin_buy_in\'><label for=\'jpoker_admin_buy_in_input\'>Buy in</label><input id=\'jpoker_admin_buy_in_input\' name=\'buy_in\' title=\'Tournament buyin in cent.\' value=\'{buy_in}\' maxlength=\'5\' size=\'5\' /></div>',
		rake: '<div class=\'jpoker_admin_rake\'><label for=\'jpoker_admin_rake_input\'>Rake</label><input id=\'jpoker_admin_rake_input\' name=\'rake\' title=\'Tournament rake in cent.\' value=\'{rake}\' maxlength=\'5\' size=\'5\' /></div>',
		prize_min: '<div class=\'jpoker_admin_prize_min\'><label for=\'jpoker_admin_prize_min_input\'>Prize min</label><input id=\'jpoker_admin_prize_min_input\' name=\'prize_min\' title=\'Minimum prize pool in cents.\' value=\'{prize_min}\' maxlength=\'5\' size=\'5\' /></div>',
		bailor_serial: '<div class=\'jpoker_admin_bailor_serial\'><label for=\'jpoker_admin_bailor_serial_input\'>Bailor serial</label><input id=\'jpoker_admin_bailor_serial_input\' name=\'bailor_serial\' title=\'Serial number of the player (serial field of the users table)  who guarantees the minimum prize set in the prize_min field if the total buyin payed by the players is not enough.\' value=\'{bailor_serial}\' maxlength=\'4\' size=\'4\' /></div>',
		breaks_first: '<div class=\'jpoker_admin_breaks_first\'><label for=\'jpoker_admin_breaks_first_input\'>Breaks first</label><input id=\'jpoker_admin_breaks_first_input\' name=\'breaks_first\' title=\'Number of seconds for the first breaks.\' value=\'{breaks_first}\' maxlength=\'5\' size=\'5\' /></div>',
		breaks_interval: '<div class=\'jpoker_admin_breaks_interval\'><label for=\'jpoker_admin_breaks_interval_input\'>Breaks interval</label><input id=\'jpoker_admin_breaks_interval_input\' name=\'breaks_interval\' title=\'Number of seconds between breaks after the first break.\' value=\'{breaks_interval}\' maxlength=\'5\' size=\'5\' /></div>',
		breaks_duration: '<div class=\'jpoker_admin_breaks_duration\'><label for=\'jpoker_admin_breaks_duration_input\'>Breaks duration</label><input id=\'jpoker_admin_breaks_duration_input\' name=\'breaks_duration\' title=\'Number of seconds of each break.\' value=\'{breaks_duration}\' maxlength=\'5\' size=\'5\' /></div>',
		name: '<div class=\'jpoker_admin_name\'><label for=\'jpoker_admin_name_input\'>Name</label><input id=\'jpoker_admin_name_input\' name=\'name\' title=\'Tourney name\' value=\'{name}\' maxlength=\'200\' size=\'10\' /></div>',
		currency_serial_select: '<div class=\'jpoker_admin_currency_serial\'><label for=\'jpoker_admin_currency_serial_input\'>Currency serial</label><select id=\'jpoker_admin_currency_serial_input\' name=\'currency_serial\' title=\'Serial of the currency required to pay the buyin.\'>{options}<option value=\'from_date_format\'>from date format</option></select></div>',
		currency_serial_option: '<option value=\'{serial}\'>{name}</option>',
		currency_serial_from_date_format: '<div class=\'jpoker_admin_currency_serial_from_date_format\'><label for=\'jpoker_admin_currency_serial_from_date_format_input\'>Date format</label><input id=\'jpoker_admin_currency_serial_from_date_format_input\' name=\'currency_serial_from_date_format\' title=\'Format string to override currency serial from date.\' value=\'{currency_serial_from_date_format}\' maxlength=\'8\' size=\'8\' readonly=\'true\' /></div>',
		player_timeout: '<div class=\'jpoker_admin_player_timeout\'><label for=\'jpoker_admin_player_timeout_input\'>Player timeout</label><input id=\'jpoker_admin_player_timeout_input\' name=\'player_timeout\' title=\'Maximum number of seconds before a player times out when in position.\' value=\'{player_timeout}\' maxlength=\'4\' size=\'4\' /></div>',
		seats_per_game: '<div class=\'jpoker_admin_seats_per_game\'><label for=\'jpoker_admin_seats_per_game_input\'>Seats per game</label><input id=\'jpoker_admin_seats_per_game_input\' name=\'seats_per_game\' title=\'Number of seats, in the range 2 and 10 included.\' value=\'{seats_per_game}\' maxlength=\'2\' size=\'2\' /></div>',
		sit_n_go: '<div class=\'jpoker_admin_sit_n_go\'><input id=\'jpoker_admin_sit_n_go_input\' name=\'sit_n_go\' title=\'Tourney type\' value=\'y\' type=\'radio\' /><label for=\'jpoker_admin_sit_n_go_input\'>Sit and go</label><input id=\'jpoker_admin_regular_input\' name=\'sit_n_go\' title=\'Tourney type\' value=\'n\' type=\'radio\' /><label for=\'jpoker_admin_regular_input\'>Regular</label></div>',
		via_satellite: '<div class=\'jpoker_admin_via_satellite\'><label for=\'jpoker_admin_via_satellite\'>Via satellite</label><input id=\'jpoker_admin_via_satellite_input\' name=\'via_satellite\' type=\'checkbox\' title=\'Control if registration is only allowed by playing a satellite\' /></div>',
		satellite_of_select: '<div class=\'jpoker_admin_satellite_of\'><label for=\'jpoker_admin_satellite_of\'>Satellite of</label><select id=\'jpoker_admin_satellite_of_input\' name=\'satellite_of\' title=\'Control if the tournament is a satellite, the value is a reference to the serial field of the tourneys_schedule table.\' ><option value=\'0\'>none</option>{options}</select></div>',
		satellite_of_option: '<option value=\'{schedule_serial}\'>{schedule_serial}</option>',
		satellite_player_count: '<div class=\'jpoker_admin_satellite_player_count\'><label for=\'jpoker_admin_satellite_player_count\'>Satellite player count</label><input id=\'jpoker_admin_satellite_player_count_input\' name=\'satellite_player_count\' type=\'text\' title=\'The number of tournament winners that will be registered to the satellite_of tournament\' value=\'{satellite_player_count}\' /></div>',
		active: '<div class=\'jpoker_admin_active\'><label for=\'jpoker_admin_active_input\'>Active</label><input id=\'jpoker_admin_active_input\' name=\'active\' type=\'checkbox\' title=\'Control if the tournament is considered by the server.\' /></div>',
		respawn: '<div class=\'jpoker_admin_respawn\'><label for=\'jpoker_admin_respawn_input\'>Respawn</label><input id=\'jpoker_admin_respawn_input\' name=\'respawn\' type=\'checkbox\' title=\'Control if the tournament restarts when complete.\' /></div>',
		update: '<div class=\'jpoker_admin_update\'><button>Update tourney</button></div>'
            },
            callback: {
                display_done: function(element) {
                },
                updated: function(tourney) {
                }
            },
            ajax: function(o) { return jQuery.ajax(o); }
        }, jpoker.defaults);

    //
    // tourneyAdminList
    //
    jpoker.plugins.tourneyAdminList = function(url, options) {

        var tourneyAdminList = jpoker.plugins.tourneyAdminList;
        var opts = $.extend(true, {}, tourneyAdminList.defaults, options);
        url = url + opts.path;

	jpoker.plugins.tourneyAdminList.getResthost(url, opts);
	jpoker.plugins.tourneyAdminList.getCurrencies(url, opts);

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();
		
                $this.append('<div class=\'jpoker_widget\' id=\'' + id + '\'></table>');
		
		tourneyAdminList.refresh(url, id, opts);
		
                return this;
            });
    };

    jpoker.plugins.tourneyAdminList.refresh = function(url, id, opts) {
	var tourneyAdminList = jpoker.plugins.tourneyAdminList;

	var error = function(xhr, status, error) {
	    throw error;
	};
	
	var success = function(tourneys, status) {
	    var element = document.getElementById(id);
	    if(element) {
		$(element).html(tourneyAdminList.getHTML(id, tourneys, opts));
		$('.jpoker_admin_new a').click(function() {			
			tourneyAdminList.tourneyCreate(url, opts, function() {
				jpoker.plugins.tourneyAdminList.refresh(url, id, opts);
			    });
		    });
		tourneyAdminList.schedule_serial = [];
		for(var i = 0; i < tourneys.length; i++) {
		    (function(){
			var tourney = tourneys[i];
			tourneyAdminList.schedule_serial.push(tourney.serial);
			$('#admin' + tourney.id + ' .jpoker_admin_edit a').click(function() {
				var edit_options = $.extend(true, {}, opts.tourneyEditOptions);
				edit_options.callback.updated = function(tourney) {
				    jpoker.plugins.tourneyAdminList.refresh(url, id, opts);
				};
				opts.tourneyEdit(url, tourney, edit_options);
			    });
			$('#admin' + tourney.id + ' .jpoker_admin_delete a').click(function() {
				tourneyAdminList.tourneyDelete(url, tourney.id, opts, function() {
					jpoker.plugins.tourneyAdminList.refresh(url, id, opts);
				    });
			    });
			$('#admin' + tourney.id).hover(function(){
				$(this).addClass('hover');
			    },function(){
				$(this).removeClass('hover');
			    });
		    })();
		}
		if(tourneys.length > 0) {
		    var t = opts.templates;
		    var params = {
			container: $('.pager', element),
			positionFixed: false,
			previous_label: t.previous_label.supplant({previous_label: "Previous page"}),
			next_label: t.next_label.supplant({next_label: "Next page"})};
		    $('table', element).tablesorter({widgets: ['zebra'], sortList: opts.sortList}).tablesorterPager(params);
		}
		opts.callback.display_done(element, url, id, opts);
	    }
	};
	
	var params = {
	    'query': 'SELECT * FROM tourneys_schedule WHERE active = \'n\'',
	    'output': 'rows'
	};
	opts.ajax({
		async: false,
		    mode: 'queue',
		    timeout: 30000,
		    url: url + '?' + $.param(params),
		    type: 'GET',
		    dataType: 'json',
		    global: false,
		    success: success,
		    error: error
                    });
    };

    jpoker.plugins.tourneyAdminList.getHTML = function(id, tourneys, options) {
        var t = options.templates;
        var html = [];
        html.push(t.header.supplant({
		    'serial': 'Serial',
		    'players_quota': "Players Quota",
                        'players_abbrev':"Play.",
                        'breaks_first':"Break First",
                        'name':"Name",
                        'description_short':"Description",
                        'start_time':"Start Time",
                        'breaks_interval':"Breaks Interval",
                        'breaks_interval_abbrev':"Brk.",
                        'variant':"Variant",
                        'betting_structure':"Betting Structure",
                        'currency_serial':"Currency",
                        'buy_in':"Buy In",
                        'breaks_duration':"Breaks Duration",
                        'sit_n_go':"Sit'n'Go",
			'player_timeout':"Player Timeout",
                        'player_timeout_abbrev':"Time"
                        }));
        for(var i = 0; i < tourneys.length; i++) {
            var tourney = tourneys[i];
            if(!('game_id' in tourney)) {
                tourney.game_id = tourney.serial;
                tourney.id = tourney.game_id + id;
                tourney.buy_in /= 100;
	    }
	    tourney.start_time_string = new Date(tourney.start_time*1000).print(options.dateFormat);
	    tourney.register_time_string = new Date(tourney.register_time*1000).print(options.dateFormat);
            html.push(t.rows.supplant(tourney).replace(/{oddEven}/g, i%2 ? 'odd' : 'even'));
        }
        html.push(t.footer);
        html.push(t.pager);
        return html.join('\n');
    };

    jpoker.plugins.tourneyAdminList.tourneyCreate = function(url, options, callback) {
        var params = {
            'query': 'INSERT INTO tourneys_schedule SET active = \'n\''
        };

        var error = function(xhr, status, error) {
            throw error;
        };

        var success = function(rowcount, status) {
            if(rowcount != 1) {
                throw 'expected ' + params.query + ' to modify exactly one row but it modified ' + rowcount.toString() + ' rows instead';
            }
	    callback();
        };

        options.ajax({
                async: false,
                    timeout: 30000,
                    url: url + '?' + $.param(params),
                    type: 'GET',
                    dataType: 'json',
                    global: false,
                    success: success,
                    error: error
                    });
        return true;	
    };

    jpoker.plugins.tourneyAdminList.tourneyDelete = function(url, tourney_serial, options, callback) {
        var params = {
            'query': 'DELETE FROM tourneys_schedule WHERE serial = \''+tourney_serial+'\''
        };

        var error = function(xhr, status, error) {
            throw error;
        };

        var success = function(rowcount, status) {
            if(rowcount != 1) {
                throw 'expected ' + params.query + ' to modify exactly one row but it modified ' + rowcount.toString() + ' rows instead';
            }
	    callback();
        };

        options.ajax({
                async: false,
                    timeout: 30000,
                    url: url + '?' + $.param(params),
                    type: 'GET',
                    dataType: 'json',
                    global: false,
                    success: success,
                    error: error
                    });
        return true;	
    };
    
    jpoker.plugins.tourneyAdminList.defaults = $.extend({
            sortList: [[0, 0]],
            dateFormat: '%Y/%m/%d-%H:%M',
            path: '/cgi-bin/poker-network/pokersql',
            string: '',
            templates: {
                header : '<table><thead><tr><th>{serial}</th><th>{description_short}</th><th>{variant}</th><th>{players_quota}</th><th>{buy_in}</th><th class=\'jpoker_admin_edit_header\'></th><th class=\'jpoker_admin_new\'><a href=\'javascript://\'>New</a></th></tr></thead><tbody>',
                rows : '<tr id=\'admin{id}\' title=\'Click to edit\'><td>{serial}</td><td>{description_short}</td><td>{variant}</td><td>{players_quota}</td><td>{buy_in}</td><td class=\'jpoker_admin_edit\'><a href=\'javascript://\'>Edit</a></td><td class=\'jpoker_admin_delete\'><a href=\'javascript://\'>Delete</a></td></tr>',
                footer : '</tbody></table>',
                link: '<a href=\'{link}\'>{name}</a>',
                pager: '<div class=\'pager\'><input class=\'pagesize\' value=\'10\'></input><ul class=\'pagelinks\'></ul></div>',
                next_label: '{next_label} >>>',
                previous_label: '<<< {previous_label}'
            },
            callback: {
                display_done: function(element) {
                }
            },
            tourneyEditOptions: $.extend({}, jpoker.plugins.tourneyAdminEdit.defaults),
            tourneyEdit: jpoker.tourneyAdminEdit,
            ajax: function(o) { return jQuery.ajax(o); }
        }, jpoker.defaults);

    jpoker.plugins.tourneyAdminList.resthost = [];

    jpoker.plugins.tourneyAdminList.getResthost = function(url, options) {
        var error = function(xhr, status, error) {
            throw error;
        };
        var success = function(resthost, status) {
	    jpoker.plugins.tourneyAdminList.resthost = resthost;
        };
        var params = {
            'query': 'SELECT * FROM resthost',
            'output': 'rows'
        };
        options.ajax({
                async: false,
                    timeout: 30000,
                    url: url + '?' + $.param(params),
                    type: 'GET',
                    dataType: 'json',
                    global: false,
                    success: success,
                    error: error
                    });	
    };

    jpoker.plugins.tourneyAdminList.currencies = [];

    jpoker.plugins.tourneyAdminList.getCurrencies = function(url, options) {
        var error = function(xhr, status, error) {
            throw error;
        };
        var success = function(currencies, status) {
	    jpoker.plugins.tourneyAdminList.currencies = currencies;
        };
        var params = {
            'query': 'SELECT * FROM currencies',
            'output': 'rows'
        };
        options.ajax({
                async: false,
                    timeout: 30000,
                    url: url + '?' + $.param(params),
                    type: 'GET',
                    dataType: 'json',
                    global: false,
                    success: success,
                    error: error
                    });	
    };

    jpoker.plugins.tourneyAdminList.schedule_serial = [];

})(jQuery);
