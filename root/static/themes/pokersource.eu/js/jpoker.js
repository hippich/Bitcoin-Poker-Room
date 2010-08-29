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
(function($) {
    var jpoker = $.jpoker;

    jpoker.selectors = {
        'table': '#table'
    };

    jpoker.main = function() {
        this.setTemplates();
        this.setSpawnTable();
        this.setLocale();
    };

    jpoker.setSpawnTable = function() {
        jpoker.server.defaults.spawnTable = function(server, packet) {
            server.setLocale(jpoker.global_preferences.lang, packet.game_id);
            $($.jpoker.selectors.table).jpoker('table', server.url, packet.game_id, packet.name);
        };
    };

    jpoker.reload = function() { document.location.href = ''; };

    jpoker.setLocale = function() {
        jpoker.preferences.prototype.lang = $("html").attr("lang");
        this.global_preferences = new jpoker.preferences('global');
    };

    jpoker.changeLocale = function(lang) {
        this.global_preferences.extend({ lang: lang });
        this.reload();
    };

    jpoker.setTemplates = function() {
        jpoker.plugins.login.templates.login = 
        '<ul class=\'jpoker_login_login\'>' +
        ' <li class=\'jpoker_login_label\'>' +
        '  <div class=\'jpoker_login_name_label\'>{login}</div>' +
        '  <div class=\'jpoker_login_password_label\'>{password}</div>' +
        ' </li>' +
        ' <li class=\'jpoker_login_input\'>' +
        '  <div><input type=\'text\' class=\'jpoker_login_name\' /></div>' +
        '  <div><input type=\'password\' class=\'jpoker_login_password\' /></div>' +
        ' </li>' +
        ' <li class=\'jpoker_login_buttons\'>' +
        '  <div class=\'jpoker_login_submit\'><input type=\'text\' class=\'jpoker_login_submit\' value=\'{go}\' /></div>' +
        '  <div class=\'jpoker_login_signup\'><input type=\'text\' class=\'jpoker_login_signup\' value=\'{signup}\' /></div>' +
        ' </li>' + 
        '</ul>';
        jpoker.plugins.serverStatus.templates.players = '<div class=\'jpoker_server_status_players\'> <span class=\'jpoker_server_status_players_count\'>{count}</span> <span class=\'jpoker_server_status_players_label\'>' + _("players online") + '</span> <span class=\'jpoker_server_status_more\'>' + _("more...") + '</span></div>';
        click_to_sit = _("Click to sit");
        jpoker.plugins.table.templates.room = '<div id=\'game_window{id}\' class=\'jpoker_ptable jpoker_table\'>' + 
        '<div id=\'game_fixed{id}\'>' + 
        '<div id=\'game_background{id}\' class=\'jpoker_ptable_game_background\'></div>' + 
        '<div id=\'table{id}\' class=\'jpoker_ptable_table\'></div>' + 
        '<div id=\'board0{id}\' class=\'jpoker_ptable_board0\'></div>' + 
        '<div id=\'board1{id}\' class=\'jpoker_ptable_board1\'></div>' + 
        '<div id=\'board2{id}\' class=\'jpoker_ptable_board2\'></div>' + 
        '<div id=\'board3{id}\' class=\'jpoker_ptable_board3\'></div>' + 
        '<div id=\'board4{id}\' class=\'jpoker_ptable_board4\'></div>' + 
        '<div id=\'winner0{id}\' class=\'jpoker_ptable_winner0\'></div>' + 
        '<div id=\'winner1{id}\' class=\'jpoker_ptable_winner1\'></div>' + 
        '<div id=\'quit{id}\' class=\'jpoker_ptable_quit\'></div>' + 
        '<div id=\'rebuy{id}\' class=\'jpoker_ptable_rebuy\'></div>' + 
        '<div id=\'auto_action{id}\' class=\'jpoker_ptable_auto_action\'></div>' + 
        '<div id=\'check{id}\' class=\'jpoker_ptable_check\'></div>' + 
        '<div id=\'call{id}\' class=\'jpoker_ptable_call\'></div>' + 
        '<div id=\'fold{id}\' class=\'jpoker_ptable_fold\'></div>' + 
        '<div id=\'raise{id}\' class=\'jpoker_ptable_raise\'></div>' + 
        '<div id=\'raise_range{id}\' class=\'jpoker_ptable_raise_range\'></div>' + 
        '<div id=\'sit_seat0{id}\' class=\'jpoker_ptable_sit_seat0\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat1{id}\' class=\'jpoker_ptable_sit_seat1\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat2{id}\' class=\'jpoker_ptable_sit_seat2\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat3{id}\' class=\'jpoker_ptable_sit_seat3\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat4{id}\' class=\'jpoker_ptable_sit_seat4\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat5{id}\' class=\'jpoker_ptable_sit_seat5\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat6{id}\' class=\'jpoker_ptable_sit_seat6\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat7{id}\' class=\'jpoker_ptable_sit_seat7\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat8{id}\' class=\'jpoker_ptable_sit_seat8\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'sit_seat9{id}\' class=\'jpoker_ptable_sit_seat9\'><div class=\'jpoker_click_to_seat\'>' + click_to_sit + '</div></div>' + 
        '<div id=\'seat0{id}\'>' + 
        '<div id=\'player_seat0{id}\'>' + 
        '<div id=\'player_seat0_background{id}\' class=\'jpoker_ptable_player_seat0_background\'></div>' + 
        '<div id=\'player_seat0_name{id}\' class=\'jpoker_ptable_player_seat0_name\'></div>' + 
        '<div id=\'player_seat0_avatar{id}\' class=\'jpoker_ptable_player_seat0_avatar\'></div>' + 
        '<div id=\'player_seat0_timeout{id}\' class=\'jpoker_ptable_player_seat0_timeout\'></div>' + 
        '<div id=\'player_seat0_money{id}\' class=\'jpoker_ptable_player_seat0_money\'></div>' + 
        '<div id=\'player_seat0_action{id}\' class=\'jpoker_ptable_player_seat0_action\'></div>' + 
        '<div id=\'player_seat0_stats{id}\' class=\'jpoker_ptable_player_seat0_stats\'></div></div>' + 
        '<div id=\'player_seat0_sidepot{id}\' class=\'jpoker_ptable_player_seat0_sidepot\'></div>' + 
        '<div id=\'player_seat0_bet{id}\' class=\'jpoker_ptable_player_seat0_bet\'></div>' + 
        '<div id=\'dealer0{id}\' class=\'jpoker_ptable_dealer0\'></div>' + 
        '<div id=\'card_seat0{id}\'>' + 
        '<div id=\'card_seat00{id}\' class=\'jpoker_ptable_card_seat00\'></div>' + 
        '<div id=\'card_seat01{id}\' class=\'jpoker_ptable_card_seat01\'></div></div>' + 
        '<div id=\'player_seat0_hole{id}\' class=\'jpoker_ptable_player_seat0_hole\'></div></div>' + 
        '<div id=\'seat1{id}\'>' + 
        '<div id=\'player_seat1{id}\'>' + 
        '<div id=\'player_seat1_background{id}\' class=\'jpoker_ptable_player_seat1_background\'></div>' + 
        '<div id=\'player_seat1_name{id}\' class=\'jpoker_ptable_player_seat1_name\'></div>' + 
        '<div id=\'player_seat1_avatar{id}\' class=\'jpoker_ptable_player_seat1_avatar\'></div>' + 
        '<div id=\'player_seat1_timeout{id}\' class=\'jpoker_ptable_player_seat1_timeout\'></div>' + 
        '<div id=\'player_seat1_money{id}\' class=\'jpoker_ptable_player_seat1_money\'></div>' + 
        '<div id=\'player_seat1_action{id}\' class=\'jpoker_ptable_player_seat1_action\'></div>' + 
        '<div id=\'player_seat1_stats{id}\' class=\'jpoker_ptable_player_seat1_stats\'></div></div>' + 
        '<div id=\'player_seat1_sidepot{id}\' class=\'jpoker_ptable_player_seat1_sidepot\'></div>' + 
        '<div id=\'player_seat1_bet{id}\' class=\'jpoker_ptable_player_seat1_bet\'></div>' + 
        '<div id=\'dealer1{id}\' class=\'jpoker_ptable_dealer1\'></div>' + 
        '<div id=\'card_seat1{id}\'>' + 
        '<div id=\'card_seat10{id}\' class=\'jpoker_ptable_card_seat10\'></div>' + 
        '<div id=\'card_seat11{id}\' class=\'jpoker_ptable_card_seat11\'></div></div>' + 
        '<div id=\'player_seat1_hole{id}\' class=\'jpoker_ptable_player_seat1_hole\'></div></div>' + 
        '<div id=\'seat2{id}\'>' + 
        '<div id=\'player_seat2{id}\'>' + 
        '<div id=\'player_seat2_background{id}\' class=\'jpoker_ptable_player_seat2_background\'></div>' + 
        '<div id=\'player_seat2_name{id}\' class=\'jpoker_ptable_player_seat2_name\'></div>' + 
        '<div id=\'player_seat2_avatar{id}\' class=\'jpoker_ptable_player_seat2_avatar\'></div>' + 
        '<div id=\'player_seat2_timeout{id}\' class=\'jpoker_ptable_player_seat2_timeout\'></div>' + 
        '<div id=\'player_seat2_money{id}\' class=\'jpoker_ptable_player_seat2_money\'></div>' + 
        '<div id=\'player_seat2_action{id}\' class=\'jpoker_ptable_player_seat2_action\'></div>' + 
        '<div id=\'player_seat2_stats{id}\' class=\'jpoker_ptable_player_seat2_stats\'></div></div>' + 
        '<div id=\'player_seat2_sidepot{id}\' class=\'jpoker_ptable_player_seat2_sidepot\'></div>' + 
        '<div id=\'player_seat2_bet{id}\' class=\'jpoker_ptable_player_seat2_bet\'></div>' + 
        '<div id=\'dealer2{id}\' class=\'jpoker_ptable_dealer2\'></div>' + 
        '<div id=\'card_seat2{id}\'>' + 
        '<div id=\'card_seat20{id}\' class=\'jpoker_ptable_card_seat20\'></div>' + 
        '<div id=\'card_seat21{id}\' class=\'jpoker_ptable_card_seat21\'></div></div>' + 
        '<div id=\'player_seat2_hole{id}\' class=\'jpoker_ptable_player_seat2_hole\'></div></div>' + 
        '<div id=\'seat3{id}\'>' + 
        '<div id=\'player_seat3{id}\'>' + 
        '<div id=\'player_seat3_background{id}\' class=\'jpoker_ptable_player_seat3_background\'></div>' + 
        '<div id=\'player_seat3_name{id}\' class=\'jpoker_ptable_player_seat3_name\'></div>' + 
        '<div id=\'player_seat3_avatar{id}\' class=\'jpoker_ptable_player_seat3_avatar\'></div>' + 
        '<div id=\'player_seat3_timeout{id}\' class=\'jpoker_ptable_player_seat3_timeout\'></div>' + 
        '<div id=\'player_seat3_money{id}\' class=\'jpoker_ptable_player_seat3_money\'></div>' + 
        '<div id=\'player_seat3_action{id}\' class=\'jpoker_ptable_player_seat3_action\'></div>' + 
        '<div id=\'player_seat3_stats{id}\' class=\'jpoker_ptable_player_seat3_stats\'></div></div>' + 
        '<div id=\'player_seat3_sidepot{id}\' class=\'jpoker_ptable_player_seat3_sidepot\'></div>' + 
        '<div id=\'player_seat3_bet{id}\' class=\'jpoker_ptable_player_seat3_bet\'></div>' + 
        '<div id=\'dealer3{id}\' class=\'jpoker_ptable_dealer3\'></div>' + 
        '<div id=\'card_seat3{id}\'>' + 
        '<div id=\'card_seat30{id}\' class=\'jpoker_ptable_card_seat30\'></div>' + 
        '<div id=\'card_seat31{id}\' class=\'jpoker_ptable_card_seat31\'></div></div>' + 
        '<div id=\'player_seat3_hole{id}\' class=\'jpoker_ptable_player_seat3_hole\'></div></div>' + 
        '<div id=\'seat4{id}\'>' + 
        '<div id=\'player_seat4{id}\'>' + 
        '<div id=\'player_seat4_background{id}\' class=\'jpoker_ptable_player_seat4_background\'></div>' + 
        '<div id=\'player_seat4_name{id}\' class=\'jpoker_ptable_player_seat4_name\'></div>' + 
        '<div id=\'player_seat4_avatar{id}\' class=\'jpoker_ptable_player_seat4_avatar\'></div>' + 
        '<div id=\'player_seat4_timeout{id}\' class=\'jpoker_ptable_player_seat4_timeout\'></div>' + 
        '<div id=\'player_seat4_money{id}\' class=\'jpoker_ptable_player_seat4_money\'></div>' + 
        '<div id=\'player_seat4_action{id}\' class=\'jpoker_ptable_player_seat4_action\'></div>' + 
        '<div id=\'player_seat4_stats{id}\' class=\'jpoker_ptable_player_seat4_stats\'></div></div>' + 
        '<div id=\'player_seat4_sidepot{id}\' class=\'jpoker_ptable_player_seat4_sidepot\'></div>' + 
        '<div id=\'player_seat4_bet{id}\' class=\'jpoker_ptable_player_seat4_bet\'></div>' + 
        '<div id=\'dealer4{id}\' class=\'jpoker_ptable_dealer4\'></div>' + 
        '<div id=\'card_seat4{id}\'>' + 
        '<div id=\'card_seat40{id}\' class=\'jpoker_ptable_card_seat40\'></div>' + 
        '<div id=\'card_seat41{id}\' class=\'jpoker_ptable_card_seat41\'></div></div>' + 
        '<div id=\'player_seat4_hole{id}\' class=\'jpoker_ptable_player_seat4_hole\'></div></div>' + 
        '<div id=\'seat5{id}\'>' + 
        '<div id=\'player_seat5{id}\'>' + 
        '<div id=\'player_seat5_background{id}\' class=\'jpoker_ptable_player_seat5_background\'></div>' + 
        '<div id=\'player_seat5_name{id}\' class=\'jpoker_ptable_player_seat5_name\'></div>' + 
        '<div id=\'player_seat5_avatar{id}\' class=\'jpoker_ptable_player_seat5_avatar\'></div>' + 
        '<div id=\'player_seat5_timeout{id}\' class=\'jpoker_ptable_player_seat5_timeout\'></div>' + 
        '<div id=\'player_seat5_money{id}\' class=\'jpoker_ptable_player_seat5_money\'></div>' + 
        '<div id=\'player_seat5_action{id}\' class=\'jpoker_ptable_player_seat5_action\'></div>' + 
        '<div id=\'player_seat5_stats{id}\' class=\'jpoker_ptable_player_seat5_stats\'></div></div>' + 
        '<div id=\'player_seat5_sidepot{id}\' class=\'jpoker_ptable_player_seat5_sidepot\'></div>' + 
        '<div id=\'player_seat5_bet{id}\' class=\'jpoker_ptable_player_seat5_bet\'></div>' + 
        '<div id=\'dealer5{id}\' class=\'jpoker_ptable_dealer5\'></div>' + 
        '<div id=\'card_seat5{id}\'>' + 
        '<div id=\'card_seat50{id}\' class=\'jpoker_ptable_card_seat50\'></div>' + 
        '<div id=\'card_seat51{id}\' class=\'jpoker_ptable_card_seat51\'></div></div>' + 
        '<div id=\'player_seat5_hole{id}\' class=\'jpoker_ptable_player_seat5_hole\'></div></div>' + 
        '<div id=\'seat6{id}\'>' + 
        '<div id=\'player_seat6{id}\'>' + 
        '<div id=\'player_seat6_background{id}\' class=\'jpoker_ptable_player_seat6_background\'></div>' + 
        '<div id=\'player_seat6_name{id}\' class=\'jpoker_ptable_player_seat6_name\'></div>' + 
        '<div id=\'player_seat6_avatar{id}\' class=\'jpoker_ptable_player_seat6_avatar\'></div>' + 
        '<div id=\'player_seat6_timeout{id}\' class=\'jpoker_ptable_player_seat6_timeout\'></div>' + 
        '<div id=\'player_seat6_money{id}\' class=\'jpoker_ptable_player_seat6_money\'></div>' + 
        '<div id=\'player_seat6_action{id}\' class=\'jpoker_ptable_player_seat6_action\'></div>' + 
        '<div id=\'player_seat6_stats{id}\' class=\'jpoker_ptable_player_seat6_stats\'></div></div>' + 
        '<div id=\'player_seat6_sidepot{id}\' class=\'jpoker_ptable_player_seat6_sidepot\'></div>' + 
        '<div id=\'player_seat6_bet{id}\' class=\'jpoker_ptable_player_seat6_bet\'></div>' + 
        '<div id=\'dealer6{id}\' class=\'jpoker_ptable_dealer6\'></div>' + 
        '<div id=\'card_seat6{id}\'>' + 
        '<div id=\'card_seat60{id}\' class=\'jpoker_ptable_card_seat60\'></div>' + 
        '<div id=\'card_seat61{id}\' class=\'jpoker_ptable_card_seat61\'></div></div>' + 
        '<div id=\'player_seat6_hole{id}\' class=\'jpoker_ptable_player_seat6_hole\'></div></div>' + 
        '<div id=\'seat7{id}\'>' + 
        '<div id=\'player_seat7{id}\'>' + 
        '<div id=\'player_seat7_background{id}\' class=\'jpoker_ptable_player_seat7_background\'></div>' + 
        '<div id=\'player_seat7_name{id}\' class=\'jpoker_ptable_player_seat7_name\'></div>' + 
        '<div id=\'player_seat7_avatar{id}\' class=\'jpoker_ptable_player_seat7_avatar\'></div>' + 
        '<div id=\'player_seat7_timeout{id}\' class=\'jpoker_ptable_player_seat7_timeout\'></div>' + 
        '<div id=\'player_seat7_money{id}\' class=\'jpoker_ptable_player_seat7_money\'></div>' + 
        '<div id=\'player_seat7_action{id}\' class=\'jpoker_ptable_player_seat7_action\'></div>' + 
        '<div id=\'player_seat7_stats{id}\' class=\'jpoker_ptable_player_seat7_stats\'></div></div>' + 
        '<div id=\'player_seat7_sidepot{id}\' class=\'jpoker_ptable_player_seat7_sidepot\'></div>' + 
        '<div id=\'player_seat7_bet{id}\' class=\'jpoker_ptable_player_seat7_bet\'></div>' + 
        '<div id=\'dealer7{id}\' class=\'jpoker_ptable_dealer7\'></div>' + 
        '<div id=\'card_seat7{id}\'>' + 
        '<div id=\'card_seat70{id}\' class=\'jpoker_ptable_card_seat70\'></div>' + 
        '<div id=\'card_seat71{id}\' class=\'jpoker_ptable_card_seat71\'></div></div>' + 
        '<div id=\'player_seat7_hole{id}\' class=\'jpoker_ptable_player_seat7_hole\'></div></div>' + 
        '<div id=\'seat8{id}\'>' + 
        '<div id=\'player_seat8{id}\'>' + 
        '<div id=\'player_seat8_background{id}\' class=\'jpoker_ptable_player_seat8_background\'></div>' + 
        '<div id=\'player_seat8_name{id}\' class=\'jpoker_ptable_player_seat8_name\'></div>' + 
        '<div id=\'player_seat8_avatar{id}\' class=\'jpoker_ptable_player_seat8_avatar\'></div>' + 
        '<div id=\'player_seat8_timeout{id}\' class=\'jpoker_ptable_player_seat8_timeout\'></div>' + 
        '<div id=\'player_seat8_money{id}\' class=\'jpoker_ptable_player_seat8_money\'></div>' + 
        '<div id=\'player_seat8_action{id}\' class=\'jpoker_ptable_player_seat8_action\'></div>' + 
        '<div id=\'player_seat8_stats{id}\' class=\'jpoker_ptable_player_seat8_stats\'></div></div>' + 
        '<div id=\'player_seat8_sidepot{id}\' class=\'jpoker_ptable_player_seat8_sidepot\'></div>' + 
        '<div id=\'player_seat8_bet{id}\' class=\'jpoker_ptable_player_seat8_bet\'></div>' + 
        '<div id=\'dealer8{id}\' class=\'jpoker_ptable_dealer8\'></div>' + 
        '<div id=\'card_seat8{id}\'>' + 
        '<div id=\'card_seat80{id}\' class=\'jpoker_ptable_card_seat80\'></div>' + 
        '<div id=\'card_seat81{id}\' class=\'jpoker_ptable_card_seat81\'></div></div>' + 
        '<div id=\'player_seat8_hole{id}\' class=\'jpoker_ptable_player_seat8_hole\'></div></div>' + 
        '<div id=\'seat9{id}\'>' + 
        '<div id=\'player_seat9{id}\'>' + 
        '<div id=\'player_seat9_background{id}\' class=\'jpoker_ptable_player_seat9_background\'></div>' + 
        '<div id=\'player_seat9_name{id}\' class=\'jpoker_ptable_player_seat9_name\'></div>' + 
        '<div id=\'player_seat9_avatar{id}\' class=\'jpoker_ptable_player_seat9_avatar\'></div>' + 
        '<div id=\'player_seat9_timeout{id}\' class=\'jpoker_ptable_player_seat9_timeout\'></div>' + 
        '<div id=\'player_seat9_money{id}\' class=\'jpoker_ptable_player_seat9_money\'></div>' + 
        '<div id=\'player_seat9_action{id}\' class=\'jpoker_ptable_player_seat9_action\'></div>' + 
        '<div id=\'player_seat9_stats{id}\' class=\'jpoker_ptable_player_seat9_stats\'></div></div>' + 
        '<div id=\'player_seat9_sidepot{id}\' class=\'jpoker_ptable_player_seat9_sidepot\'></div>' + 
        '<div id=\'player_seat9_bet{id}\' class=\'jpoker_ptable_player_seat9_bet\'></div>' + 
        '<div id=\'dealer9{id}\' class=\'jpoker_ptable_dealer9\'></div>' + 
        '<div id=\'card_seat9{id}\'>' + 
        '<div id=\'card_seat90{id}\' class=\'jpoker_ptable_card_seat90\'></div>' + 
        '<div id=\'card_seat91{id}\' class=\'jpoker_ptable_card_seat91\'></div></div>' + 
        '<div id=\'player_seat9_hole{id}\' class=\'jpoker_ptable_player_seat9_hole\'></div></div>' + 
        '<div id=\'sitout{id}\' class=\'jpoker_ptable_sitout\'></div>' + 
        '<div id=\'muck_accept{id}\' class=\'jpoker_ptable_muck_accept\'></div>' + 
        '<div id=\'muck_deny{id}\' class=\'jpoker_ptable_muck_deny\'></div>' + 
        '<div id=\'raise_input{id}\' class=\'jpoker_ptable_raise_input\'></div>' + 
        '<div id=\'table_info{id}\' class=\'jpoker_ptable_table_info\'></div>' + 
        '<div id=\'sitin{id}\' class=\'jpoker_ptable_sitin\'></div>' + 
        '<div id=\'powered_by{id}\' class=\'jpoker_ptable_powered_by\'></div>' + 
        '<div id=\'allin{id}\' class=\'jpoker_ptable_allin\'></div>' + 
        '<div id=\'hand_strength{id}\' class=\'jpoker_ptable_hand_strength\'></div>' + 
        '<div id=\'pots{id}\' class=\'jpoker_ptable_pots\'></div>' + 
        '<div id=\'options{id}\' class=\'jpoker_ptable_options\'></div>' + 
        '<div id=\'sound_control{id}\' class=\'jpoker_ptable_sound_control\'></div>' + 
        '<div id=\'threequarterpot{id}\' class=\'jpoker_ptable_threequarterpot\'></div>' + 
        '<div id=\'halfpot{id}\' class=\'jpoker_ptable_halfpot\'></div>' + 
        '<div id=\'pot{id}\' class=\'jpoker_ptable_pot\'></div></div></div>';
    };
})(jQuery);
