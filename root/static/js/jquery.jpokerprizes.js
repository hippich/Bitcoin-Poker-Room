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

    jpoker.tourneyAdminEditPrizes = function(url, tourney, options) {
        var dialog = jpoker.tourneyAdminEdit(url, tourney, options);
        dialog.append('<div id=\'jpokerAdminEditPrizes\' />');
        jpoker.plugins.tourneyAdminEditPrizes.getPrizes(url, options);
        $('#jpokerAdminEditPrizes').jpoker('tourneyAdminEditPrizes', url, tourney, options);
    };

    //
    // tourneyAdminEditPrizes
    //
    jpoker.plugins.tourneyAdminEditPrizes = function(url, tourney, options) {

        var tourneyAdminEditPrizes = jpoker.plugins.tourneyAdminEditPrizes;
        var opts = $.extend(true, {}, tourneyAdminEditPrizes.defaults, options);
	opts.templates = tourneyAdminEditPrizes.defaults.templates; // FIXME : this function must be called with a proper options arg

        return this.each(function() {
                var $this = $(this);

                var error = function(xhr, status, error) {
                    throw error;
                };
                var success = function(prize_serials, status) {
                    var prize_serial;
                    if(prize_serials.length > 0) {
                        prize_serial = prize_serials[0].serial;
                    } else {
                        prize_serial = undefined;
                    }
                    tourneyAdminEditPrizes.populate(url, $this, tourney, prize_serial, opts);
                };
                var params = {
                    'query': 'SELECT p.serial FROM prizes AS p,tourneys_schedule2prizes AS t WHERE p.serial = t.prize_serial AND t.tourneys_schedule_serial = '+tourney.serial,
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
                return this;
            });
    };

    jpoker.plugins.tourneyAdminEditPrizes.serial2prize = {};

    jpoker.plugins.tourneyAdminEditPrizes.getPrizes = function(url, options) {
        var error = function(xhr, status, error) {
            throw error;
        };
        var success = function(prizes, status) {
            serial2prize = {}
            for(var i = 0; i < prizes.length; i++) {
		var prize = prizes[i];
		for (k in prize) {
		    if (prize[k] == null) {
			prize[k] = '';
		    }
		}
                serial2prize[prize.serial] = prize;
            }
            jpoker.plugins.tourneyAdminEditPrizes.serial2prize = serial2prize
        };
        var params = {
            'query': 'SELECT * FROM prizes',
            'output': 'rows'
        };
        options.ajax({
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

    jpoker.plugins.tourneyAdminEditPrizes.populate = function(url, element, tourney, prize_serial, options) {
        var option_elements = [];
        var serial2prize = jpoker.plugins.tourneyAdminEditPrizes.serial2prize;
	var old_prize_serial = prize_serial;
        for(var serial in serial2prize) {
            if(prize_serial == undefined) {
		prize_serial = serial;
	    }
            option_elements.push(options.templates.option.supplant(serial2prize[serial]));
        }
        var selector = options.templates.selector.supplant({ options: option_elements.join('') }); 
        element.html(options.templates.layout.supplant({ selector: selector }));
	
        $('select[name=prize_serial]', element).val(prize_serial).change(function() {
		var old_prize_serial = prize_serial;
		prize_serial = $(this).val();
                jpoker.plugins.tourneyAdminEditPrizes.update(url, element, tourney, old_prize_serial, prize_serial, options);
            });
	options.callback.display_done(element);
        jpoker.plugins.tourneyAdminEditPrizes.update(url, element, tourney, old_prize_serial, prize_serial, options);
    };

    jpoker.plugins.tourneyAdminEditPrizes.update = function(url, element, tourney, old_prize_serial, new_prize_serial, options) {
        var html = options.templates.prize.supplant(options.templates);
        var serial2prize = jpoker.plugins.tourneyAdminEditPrizes.serial2prize;
        $('.jpoker_prize', element).html(html.supplant(serial2prize[new_prize_serial]));
        
        if(old_prize_serial != new_prize_serial) {
            $('select[name=prize_serial]', element).val(new_prize_serial);
            var params = {
                'query': 'INSERT tourneys_schedule2prizes SET prize_serial = ' + new_prize_serial.toString() + ', tourneys_schedule_serial = ' + tourney.serial.toString() + ' ON DUPLICATE KEY UPDATE prize_serial = ' + new_prize_serial.toString()
            };

            var error = function(xhr, status, error) {
                throw error;
            };

            var success = function(rowcount, status) {
                if(rowcount < 1) {
                    throw 'expected ' + params.query + ' to modify at least one row but it modified ' + rowcount.toString() + ' rows instead';
                }
                options.callback.updated(tourney);
            };

            options.ajax({
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
        }
    };

    jpoker.plugins.tourneyAdminEditPrizes.defaults = $.extend({
            templates: {
                layout: '<form action=\'javascript://\'><fieldset><legend>Prizes</legend>{selector}<div class=\'jpoker_prize\'>prize descriptions</div></fieldset></form>',
                selector: '<select name=\'prize_serial\'>{options}</select>',
                option: '<option value=\'{serial}\'>{name}</option>',
                prize: '{image}{description}{points}',
		description: '<div class=\'jpoker_prize_description\'><label for=\'jpoker_prize_description_input=\'>Description</label><input id=\'jpoker_prize_description_input\' readonly=\'yes\' value=\'{description}\' /></div>',
		points: '<div class=\'jpoker_prize_points\'><label for=\'jpoker_prize_points_input\'>Points</label><input id=\'jpoker_prize_points_input\' readonly=\'yes\' value=\'{points}\' /></div>',
                image: '<div class=\'jpoker_prize_image\'><a href=\'{link_url}\'><img src=\'{image_url}\' alt=\'prize image\' /></a></div>'
            },
            callback: {
                display_done: function(element) {
                },
                updated: function(tourney) {
                }
            },
            ajax: function(o) { return jQuery.ajax(o); }
        }, jpoker.defaults);

    jpoker.plugins.tourneyAdminList.defaults.tourneyEdit = jpoker.tourneyAdminEditPrizes;
    jpoker.plugins.tourneyAdminList.defaults.callback.display_done = function(element, url, id, options) {
	var template = {
	    prize_header: '<th>Prize</th>',
	    prize: '<td class=\'jpoker_tourney_prize\'></td>'
	};
	$('.jpoker_admin_edit_header', element).before(template.prize_header);
	$('.jpoker_admin_edit', element).before(template.prize);

	var error = function(xhr, status, error) {
	    throw error;
	};
	var success = function(tourney2prizes, status) {
	    for (var i in tourney2prizes) {
		var tourney2prize = tourney2prizes[i];
		$('#admin' + tourney2prize.tourneys_schedule_serial + id + ' .jpoker_tourney_prize', element).html(tourney2prize.name);
	    }
	};
	var params = {
	    'query': ' SELECT t.tourneys_schedule_serial, p.name FROM prizes AS p, tourneys_schedule2prizes AS t WHERE p.serial = prize_serial',
	    'output': 'rows'
	};
	options.ajax({
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

})(jQuery);
