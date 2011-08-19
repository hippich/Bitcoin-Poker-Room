//
//     Copyright (C) 2008 - 2010 Loic Dachary <loic@dachary.org>
//     Copyright (C) 2008 - 2010 Johan Euphrosine <proppy@aminche.com>
//     Copyright (C) 2008, 2009 Saq Imtiaz <lewcid@gmail.com>
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
    var _ = $.gt.gettext;

    if(!String.prototype.supplant) {
        //
        // Douglas Crockford douglas@crockford.com snippet
        //
        String.prototype.supplant = function (o) {
            return this.replace(/{([^{}]*)}/g,
                                function (a, b) {
                                    var r = o[b];
                                    return typeof r === 'string' || typeof r === 'number' ? r : a;
                                }
                                );
        };
    }

    //
    // decoration divs to help CSS skining
    // example $('.jpoker_download', copyright).frame('box1');
    //
    $.fn.extend({
            frame: function(css) {
                var box = '';
                var positions = [ 'n', 'e', 's', 'w', 'se', 'sw', 'nw', 'ne' ];
                for(var i = 0; i < positions.length; i++) {
                    box += '<div style=\'position: absolute\' class=\'' + css + ' ' + css + '-' + positions[i] + '\'></div>';
                }
                var toggle = function() { $(this).toggleClass(css + '-hover'); };

                return this.each(function() {
                        var $this = $(this);
                        $this.wrap('<div style=\'position: relative\' class=\'' + css + ' ' + css + '-container\'></div>');
                        $this.parent().hover(toggle, toggle);
                        $this.after(box);
                        $this.wrap('<div class=\'' + css + ' ' + css + '-inner\'></div>');
                        return this;
                    });
            }
        });

    $.fn.jpoker = function() {
        var args = Array.prototype.slice.call(arguments);
        var name = args.shift();
        $.jpoker.plugins[name].apply(this, args);
    };

    $.jpoker = {

        jpoker_version: '2.0.0',

        jpoker_sources: 'http://jspoker.pokersource.info/packaging-farm/jpoker/gnulinux/debian/squeeze/src/jpoker_{jpoker-version}.orig.tar.gz',

        poker_network_version: '2.0.0',

        poker_network_sources: 'http://farmpoker.pokersource.info/packaging-farm/poker-network/gnulinux/debian/squeeze/src/poker-network_{poker-network-version}.orig.tar.gz',

        sound: 'embed width=\'1\' height=\'1\' pluginspage=\'http://getgnash.org/\' type=\'application/x-shockwave-flash\' ',

        sound_directory: '',

        packetName2Type: { NONE: 0, STRING: 1, INT: 2, ERROR: 3, ACK: 4, PING: 5, SERIAL: 6, QUIT: 7, AUTH_OK: 8, AUTH_REFUSED: 9, LOGIN: 10, AUTH_REQUEST: 11, LIST: 12, LOGOUT: 13, BOOTSTRAP: 14, PROTOCOL_ERROR: 15, MESSAGE: 16, POKER_SEATS: 50, POKER_ID: 51, POKER_MESSAGE: 52, ERROR: 53, POKER_POSITION: 54, POKER_INT: 55, POKER_BET: 56, POKER_FOLD: 57, POKER_STATE: 58, POKER_WIN: 59, POKER_CARDS: 60, POKER_PLAYER_CARDS: 61, POKER_BOARD_CARDS: 62, POKER_CHIPS: 63, POKER_PLAYER_CHIPS: 64, POKER_CHECK: 65, POKER_START: 66, POKER_IN_GAME: 67, POKER_CALL: 68, POKER_RAISE: 69, POKER_DEALER: 70, POKER_TABLE_JOIN: 71, POKER_TABLE_SELECT: 72, POKER_TABLE: 73, POKER_TABLE_LIST: 74, POKER_SIT: 75, POKER_TABLE_DESTROY: 76, POKER_TIMEOUT_WARNING: 77, POKER_TIMEOUT_NOTICE: 78, POKER_SEAT: 79, POKER_TABLE_MOVE: 80, POKER_PLAYER_LEAVE: 81, POKER_SIT_OUT: 82, POKER_TABLE_QUIT: 83, POKER_BUY_IN: 84, POKER_REBUY: 85, POKER_CHAT: 86, POKER_PLAYER_INFO: 87, POKER_PLAYER_ARRIVE: 88, POKER_HAND_SELECT: 89, POKER_HAND_LIST: 90, POKER_HAND_SELECT_ALL: 91, POKER_USER_INFO: 92, POKER_GET_USER_INFO: 93, POKER_ANTE: 94, POKER_BLIND: 95, POKER_WAIT_BIG_BLIND: 96, POKER_AUTO_BLIND_ANTE: 97, POKER_NOAUTO_BLIND_ANTE: 98, POKER_CANCELED: 99, POKER_BLIND_REQUEST: 100, POKER_ANTE_REQUEST: 101, POKER_AUTO_FOLD: 102, POKER_WAIT_FOR: 103, POKER_STREAM_MODE: 104, POKER_BATCH_MODE: 105, POKER_LOOK_CARDS: 106, POKER_TABLE_REQUEST_PLAYERS_LIST: 107, POKER_PLAYERS_LIST: 108, POKER_PERSONAL_INFO: 109, POKER_GET_PERSONAL_INFO: 110, POKER_TOURNEY_SELECT: 111, POKER_TOURNEY: 112, POKER_TOURNEY_INFO: 113, POKER_TOURNEY_LIST: 114, POKER_TOURNEY_REQUEST_PLAYERS_LIST: 115, POKER_TOURNEY_REGISTER: 116, POKER_TOURNEY_UNREGISTER: 117, POKER_TOURNEY_PLAYERS_LIST: 118, POKER_HAND_HISTORY: 119, POKER_SET_ACCOUNT: 120, POKER_CREATE_ACCOUNT: 121, POKER_PLAYER_SELF: 122, POKER_GET_PLAYER_INFO: 123, POKER_ROLES: 124, POKER_SET_ROLE: 125, POKER_READY_TO_PLAY: 126, POKER_PROCESSING_HAND: 127, POKER_MUCK_REQUEST: 128, POKER_AUTO_MUCK: 129, POKER_MUCK_ACCEPT: 130, POKER_MUCK_DENY: 131, POKER_CASH_IN: 132, POKER_CASH_OUT: 133, POKER_CASH_OUT_COMMIT: 134, POKER_CASH_QUERY: 135, POKER_RAKE: 136, POKER_TOURNEY_RANK: 137, POKER_PLAYER_IMAGE: 138, POKER_GET_PLAYER_IMAGE: 139, POKER_HAND_REPLAY: 140, POKER_GAME_MESSAGE: 141, POKER_EXPLAIN: 142, POKER_STATS_QUERY: 143, POKER_STATS: 144, PACKET_POKER_PLAYER_PLACES: 152, PACKET_POKER_SET_LOCALE: 153, POKER_TABLE_PICKER: 165, PACKET_POKER_BEST_CARDS: 170, PACKET_POKER_POT_CHIPS: 171, PACKET_POKER_CLIENT_ACTION: 172, PACKET_POKER_BET_LIMIT: 173, POKER_SIT_REQUEST: 174, POKER_PLAYER_NO_CARDS: 175, PACKET_POKER_CHIPS_PLAYER2BET: 176, PACKET_POKER_CHIPS_BET2POT: 177, PACKET_POKER_CHIPS_POT2PLAYER: 178, PACKET_POKER_CHIPS_POT_MERGE: 179, POKER_CHIPS_POT_RESET: 180, POKER_CHIPS_BET2PLAYER: 181, POKER_END_ROUND: 182, PACKET_POKER_DISPLAY_NODE: 183, PACKET_POKER_DEAL_CARDS: 184, POKER_CHAT_HISTORY: 185, POKER_DISPLAY_CARD: 186, POKER_SELF_IN_POSITION: 187, POKER_SELF_LOST_POSITION: 188, POKER_HIGHEST_BET_INCREASE: 189, POKER_PLAYER_WIN: 190, POKER_ANIMATION_PLAYER_NOISE: 191, POKER_ANIMATION_PLAYER_FOLD: 192, POKER_ANIMATION_PLAYER_BET: 193, POKER_ANIMATION_PLAYER_CHIPS: 194, POKER_ANIMATION_DEALER_CHANGE: 195, POKER_ANIMATION_DEALER_BUTTON: 196, POKER_BEGIN_ROUND: 197, POKER_CURRENT_GAMES: 198, POKER_END_ROUND_LAST: 199, POKER_PYTHON_ANIMATION: 200, POKER_SIT_OUT_NEXT_TURN: 201, POKER_RENDERER_STATE: 202, POKER_CHAT_WORD: 203, POKER_SHOWDOWN: 204, POKER_CLIENT_PLAYER_CHIPS: 205, POKER_INTERFACE_COMMAND: 206, POKER_PLAYER_ME_LOOK_CARDS: 207, POKER_PLAYER_ME_IN_FIRST_PERSON: 208, POKER_ALLIN_SHOWDOWN: 209, POKER_PLAYER_HAND_STRENGTH: 210 },

        verbose: 0,

        doReconnect: true,
        doReconnectAlways: false,
        doRejoin: true,

        msie_compatibility: function() {
            /*
             *  On IE, the widget container width and height needs to be set explicitly
             *  if the widget width/height is being set as 'none'
             */
            this.dialog_options.containerWidth = '400px';
            this.dialog_options.containerHeight = '300px';

            this.error_dialog_options.containerWidth = '400px';
            this.error_dialog_options.containerHeight = '300px';

            this.plugins.playerSelf.rebuy_options.containerWidth = '400px';
            this.plugins.playerSelf.rebuy_options.containerHeight = '300px';

            this.copyright_options.containerWidth = '400px';
            this.copyright_options.containerHeight = '300px';

            this.plugins.table.rank.options.containerWidth = '400px';
            this.plugins.table.rank.options.containerHeight = '300px';
        },

        other_compatibility: function() {
            this.dialog_options.containerWidth = '400px';
            this.dialog_options.containerHeight = '300px';

            this.plugins.playerSelf.rebuy_options.containerWidth = '400px';
            this.plugins.playerSelf.rebuy_options.containerHeight = '300px';

            this.copyright_options.containerWidth = '400px';
            this.copyright_options.containerHeight = '300px';

            this.plugins.table.rank.options.containerWidth = '400px';
            this.plugins.table.rank.options.containerHeight = '300px';
        },

        copyrightTimeout: 5000,

        copyright_options: { width: 'none', height: 'none' },

        copyright_template: '',

        copyright_text: 'replaced by copyright_template with substitutions',

        copyright: function() {
            /*
             * On IE7, css('margin') returns 'auto' instead of the actual margin value unless
             * the  margin is set explicitly. This causes ui.dialog to throw exceptions.
             */
            var copyright = $('<div style=\'margin:0px\'>' + this.copyright_text + '<div class=\'jpoker_dismiss\'><a href=\'javascript://\'>Dismiss</a></div></div>').dialog(this.copyright_options);
            this.copyright_callback.display_done(copyright);
            $('.ui-dialog-titlebar', copyright.parents('.ui-dialog-container')).hide();
            var close = function() { copyright.dialog('destroy'); };
            window.setTimeout(close, this.copyrightTimeout);
            copyright.click(close);
            return copyright;
        },

        copyright_callback: {
            display_done: function(element) {
            }
        },

        serial: (new Date()).getTime(),

        servers: {},

        url2hashCache: {},

        uninit: function() {
            $.each(this.servers,
                   function(key, value) {
                       value.uninit();
                   });
            this.servers = {};
        },

        quit: function(callback) {
            var server;
            for(var url in this.servers) {
                server = this.servers[url];
                break;
            }
            if(server === undefined) {
                if(callback !== undefined) {
                    callback();
                }
                return true;
            } else {
                server.quit(function(server) {
                        delete jpoker.servers[url];
                        jpoker.quit(callback);
                    });
                return false;
            }
        },

        now: function() { return (new Date()).getTime(); },

        uid: function() { return 'jpoker' + $.jpoker.serial++ ; },

        console : window.console,

        message: function(str) {
            if(jpoker.console) { jpoker.console.log(str); }
        },

        dialog_options: { width: '300px', height: 'auto', autoOpen: false, dialog: true, title: 'jpoker message'},

        dialog: function(content) {
            var message = $('#jpokerDialog');
            if(message.size() != 1) {
                $('body').append('<div id=\'jpokerDialog\' class=\'jpoker_jquery_ui\' />');
                message = $('#jpokerDialog');
                if (jpoker.dialog_options.title) {
                    message.attr('title', jpoker.dialog_options.title);
                }
                message.dialog(this.dialog_options);
            }
            message.html(content).dialog('open');
        },

        error: function(reason) {
            var str = '';
            try {
                if (reason.xhr) {
                    // We need to give stringify a whitelist so that it doesn't throw an error if it's called on a
                    // XMLHttpRequest object, and we can't really detect it with instanceof... so let's assume all .xhr
                    // are XMLHttpRequest objects
                    var copy = {};
                    for(var key in reason) {
                        copy[key] = reason[key];
                    }
                    copy.xhr = JSON.stringify(copy.xhr, ['status', 'responseText', 'readyState']);
                    str = JSON.stringify(copy);
                } else {
                    str = JSON.stringify(reason);
                }
                str += '\n\n' + printStackTrace({guess:true}).slice(2).join('\n');
                str += '\n\n' + navigator.userAgent;
            } catch(e) {
                str += 'attempt to stringify failed with exception: ' + e.toString();
            }
            this.uninit();
            this.errorHandler(reason, str);
        },

        error_template: '<span class=\'jquery_error_message\'>{message} <a href="">{retry}</a></span> <div class=\'jquery_error_details\'><pre>{details}</pre></div>',

        error_dialog_options: { width: '300px', height: 'auto', autoOpen: false, dialog: true, title: 'Connection error' },

        errorHandler: function(reason, str) {
            if (jpoker.console) {
                this.message(str);
            }
            var errorDialog = $('#jpokerErrorDialog');
            if(errorDialog.size() === 0) {
                $('body').append('<div id=\'jpokerErrorDialog\' class=\'jpoker_jquery_ui\' />');
                errorDialog = $('#jpokerErrorDialog');
                errorDialog.dialog(jpoker.error_dialog_options);
            }
            var info = { 'details': str,
                         'message': _("Lost connection to the poker server."),
                         'retry': _("Click to retry.")
            };
            errorDialog.html(this.error_template.supplant(info)).dialog('open');
            throw reason;
        },

        serverCreate: function(options) {
            this.servers[options.url] = new jpoker.server(options);
            return this.servers[options.url];
        },

        serverDestroy: function(url) {
            this.servers[url].uninit();
            delete this.servers[url];
        },

        url2server: function(options) {
            if(!(options.url in this.servers)) {
                this.serverCreate(options);
            }
            return this.servers[options.url];
        },

        getServer: function(url) {
            return this.servers[url];
        },

        getTable: function(url, game_id) {
            var server = jpoker.servers[url];
            if(!server) {
                return undefined;
            } else {
                return server.tables[game_id];
            }
        },

        getPlayer: function(url, game_id, serial) {
            var server = jpoker.servers[url];
            if(!server) {
                return undefined;
            }
            var table = server.tables[game_id];
            if(!table) {
                return undefined;
            }
            return table.serial2player[serial];
        },

        getServerTablePlayer: function(url, game_id, serial) {
            var server = jpoker.servers[url];
            if(!server) {
                return undefined;
            }
            var table = server.tables[game_id];
            if(!table) {
                return undefined;
            }
            if(!table.serial2player[serial]) {
                return undefined;
            }
            return { server: server,
                     table: table,
                     player: table.serial2player[serial]
                    };
        },

        url2hash: function(url) {
            if(!(url in this.url2hashCache)) {
                this.url2hashCache[url] = jpoker.Crypto.hexSha1Str(url);
            }
            return this.url2hashCache[url];
        },

        getCallAmount: function(betLimit, player) {
            var call = betLimit.call;
            var money = player.money;
            if (call > money) {
                return money;
            }

            return call;
        },

        gettext: _
    };

    var jpoker = $.jpoker;

    //--
    //-- Crypto functions and associated conversion routines
    //--

    //
    // Copyright (c) UnaMesa Association 2004-2007
    //
    // Licensed under Modified BSD
    //

    // Crypto namespace
    jpoker.Crypto = function() {};

    // Convert a string to an array of big-endian 32-bit words
    jpoker.Crypto.strToBe32s = function(str)
        {
            var be = Array();
            var len = Math.floor(str.length/4);
            var i, j;
            for(i=0, j=0; i<len; i++, j+=4) {
                be[i] = ((str.charCodeAt(j)&0xff) << 24)|((str.charCodeAt(j+1)&0xff) << 16)|((str.charCodeAt(j+2)&0xff) << 8)|(str.charCodeAt(j+3)&0xff);
            }
            while (j<str.length) {
                be[j>>2] |= (str.charCodeAt(j)&0xff)<<(24-(j*8)%32);
                j++;
            }
            return be;
        };

    // Convert an array of big-endian 32-bit words to a string
    jpoker.Crypto.be32sToStr = function(be)
        {
            var str = '';
            for(var i=0;i<be.length*32;i+=8) {
                str += String.fromCharCode((be[i>>5]>>>(24-i%32)) & 0xff);
            }
            return str;
        };

    // Convert an array of big-endian 32-bit words to a hex string
    jpoker.Crypto.be32sToHex = function(be)
        {
            var hex = '0123456789ABCDEF';
            var str = '';
            for(var i=0;i<be.length*4;i++) {
                str += hex.charAt((be[i>>2]>>((3-i%4)*8+4))&0xF) + hex.charAt((be[i>>2]>>((3-i%4)*8))&0xF);
            }
            return str;
        };

    // Return, in hex, the SHA-1 hash of a string
    jpoker.Crypto.hexSha1Str = function(str)
        {
            return jpoker.Crypto.be32sToHex(jpoker.Crypto.sha1Str(str));
        };

    // Return the SHA-1 hash of a string
    jpoker.Crypto.sha1Str = function(str)
        {
            return jpoker.Crypto.sha1(jpoker.Crypto.strToBe32s(str),str.length);
        };

    // Calculate the SHA-1 hash of an array of blen bytes of big-endian 32-bit words
    jpoker.Crypto.sha1 = function(x,blen)
        {
            // Add 32-bit integers, wrapping at 32 bits
            add32 = function(a,b)
            {
                var lsw = (a&0xFFFF)+(b&0xFFFF);
                var msw = (a>>16)+(b>>16)+(lsw>>16);
                return (msw<<16)|(lsw&0xFFFF);
            };
            // Add five 32-bit integers, wrapping at 32 bits
            add32x5 = function(a,b,c,d,e)
            {
                var lsw = (a&0xFFFF)+(b&0xFFFF)+(c&0xFFFF)+(d&0xFFFF)+(e&0xFFFF);
                var msw = (a>>16)+(b>>16)+(c>>16)+(d>>16)+(e>>16)+(lsw>>16);
                return (msw<<16)|(lsw&0xFFFF);
            };
            // Bitwise rotate left a 32-bit integer by 1 bit
            rol32 = function(n)
            {
                return (n>>>31)|(n<<1);
            };

            var len = blen*8;
            // Append padding so length in bits is 448 mod 512
            x[len>>5] |= 0x80 << (24-len%32);
            // Append length
            x[((len+64>>9)<<4)+15] = len;
            var w = Array(80);

            var k1 = 0x5A827999;
            var k2 = 0x6ED9EBA1;
            var k3 = 0x8F1BBCDC;
            var k4 = 0xCA62C1D6;

            var h0 = 0x67452301;
            var h1 = 0xEFCDAB89;
            var h2 = 0x98BADCFE;
            var h3 = 0x10325476;
            var h4 = 0xC3D2E1F0;

            for(var i=0;i<x.length;i+=16) {
                var j,t;
                var a = h0;
                var b = h1;
                var c = h2;
                var d = h3;
                var e = h4;
                for(j = 0;j<16;j++) {
                    w[j] = x[i+j];
                    t = add32x5(e,(a>>>27)|(a<<5),d^(b&(c^d)),w[j],k1);
                    e=d; d=c; c=(b>>>2)|(b<<30); b=a; a = t;
                }
                for(j=16;j<20;j++) {
                    w[j] = rol32(w[j-3]^w[j-8]^w[j-14]^w[j-16]);
                    t = add32x5(e,(a>>>27)|(a<<5),d^(b&(c^d)),w[j],k1);
                    e=d; d=c; c=(b>>>2)|(b<<30); b=a; a = t;
                }
                for(j=20;j<40;j++) {
                    w[j] = rol32(w[j-3]^w[j-8]^w[j-14]^w[j-16]);
                    t = add32x5(e,(a>>>27)|(a<<5),b^c^d,w[j],k2);
                    e=d; d=c; c=(b>>>2)|(b<<30); b=a; a = t;
                }
                for(j=40;j<60;j++) {
                    w[j] = rol32(w[j-3]^w[j-8]^w[j-14]^w[j-16]);
                    t = add32x5(e,(a>>>27)|(a<<5),(b&c)|(d&(b|c)),w[j],k3);
                    e=d; d=c; c=(b>>>2)|(b<<30); b=a; a = t;
                }
                for(j=60;j<80;j++) {
                    w[j] = rol32(w[j-3]^w[j-8]^w[j-14]^w[j-16]);
                    t = add32x5(e,(a>>>27)|(a<<5),b^c^d,w[j],k4);
                    e=d; d=c; c=(b>>>2)|(b<<30); b=a; a = t;
                }

                h0 = add32(h0,a);
                h1 = add32(h1,b);
                h2 = add32(h2,c);
                h3 = add32(h3,d);
                h4 = add32(h4,e);
            }
            return Array(h0,h1,h2,h3,h4);
        };

    //
    // chips helpers
    //
    jpoker.chips = {
        epsilon: 0.001,
        fraction: '.',
        thousand: ',',
        thousand_re: new RegExp(/(\d+)(\d\d\d)/),

        chips2value: function(chips) {
            var value = 0;
            for(var i = 0; i < chips.length; i += 2) {
                value += ( chips[i] / 100 ) * chips[i + 1];
            }
            return value;
        },

        SHORT: function(chips) {
            var unit = [ 'G', 'M', 'K', '' ];
            for(var magnitude = 1000000000; magnitude > 0; magnitude /= 1000) {
                if(chips >= magnitude || magnitude == 1) {
                    if(chips / magnitude < 10) {
                        chips = Math.round(chips / ( magnitude / 100 ));
                        return parseInt(chips / 100, 10) + this.fraction + parseInt( (chips/10) % 10, 10) + parseInt(chips % 10, 10) + unit[0];
                    } else if(chips / magnitude < 100) {
                        chips = Math.round(chips / ( magnitude / 10 ));
                        return parseInt(chips / 10, 10) + this.fraction + parseInt(chips % 10, 10) + unit[0];
                    } else {
                        return parseInt(chips / magnitude, 10) + unit[0];
                    }
                }
                unit.shift();
            }
        },

        LONG: function(chips) {
            var chips_fraction = parseInt(chips * 100, 10) % 100;
            var chips_str = String(parseInt(chips, 10));
            var replacement = '$1' + this.thousand + '$2';
            while(this.thousand_re.test(chips_str)) {
                chips_str = chips_str.replace(this.thousand_re, replacement);
            }
            if(chips_fraction === 0) {
                return chips_str;
            } else if(chips_fraction % 10) {
                if(chips_fraction < 10) {
                    return chips_str + '.0' + chips_fraction;
                } else {
                    return chips_str + '.' + chips_fraction;
                }
            } else {
                return chips_str + '.' + parseInt(chips_fraction / 10, 10);
            }
        }

    };

    //
    // cards helpers
    //
    jpoker.cards = {
        // Ad replaced with Ax to escape adblock
        card2string: [ '2h', '3h', '4h', '5h', '6h', '7h', '8h', '9h', 'Th', 'Jh', 'Qh', 'Kh', 'Ah', '2d', '3d', '4d', '5d', '6d', '7d', '8d', '9d', 'Td', 'Jd', 'Qd', 'Kd', 'Ax', '2c', '3c', '4c', '5c', '6c', '7c', '8c', '9c', 'Tc', 'Jc', 'Qc', 'Kc', 'Ac', '2s', '3s', '4s', '5s', '6s', '7s', '8s', '9s', 'Ts', 'Js', 'Qs', 'Ks', 'As' ]
    };

    //
    // Abstract prototype for all objects that
    // call destroy and update callbacks
    //
    jpoker.watchable = function(options) {
        $.extend(this, jpoker.watchable.defaults, options);
        if(jpoker.verbose > 0) {
            this.uid = jpoker.uid(); // helps track the packets
        }
        this.init();
    };

    jpoker.watchable.defaults = {
    };

    jpoker.watchable.prototype = {

        init: function() {
            this.setCallbacks();
        },

        uninit: function(arg) {
            this.notifyDestroy(arg);
            this.setCallbacks();
        },

        setCallbacks: function() {
            this.callbacks = { };
            this.protect = { };
        },

        notify: function(what, data) {
            if(what in this.callbacks) {
                if(what in this.protect) {
                    throw 'notify recursion for ' + what;
                }
                this.protect[what] = [];
                var result = [];
                var l = this.callbacks[what];
                for(var i = 0; i < l.length; i++) {
                    if(l[i](this, what, data)) {
                        result.push(l[i]);
                    }
                }
                this.callbacks[what] = result;
                var backlog = this.protect[what];
                delete this.protect[what];
                for(var j = 0; j < backlog.length; j++) {
                    backlog[j]();
                }
            }
        },

        notifyUpdate: function(data) { this.notify('update', data); },
        notifyDestroy: function(data) { this.notify('destroy', data); },
        notifyReinit: function(data) { this.notify('reinit', data); },

        register: function(what, callback, callback_data, signature) {
            if(what in this.protect) {
                var self = this;
                this.protect[what].push(function() {
                        self.register(what, callback, callback_data, signature);
                    });
            } else {
                this.unregister(what, signature || callback);
                if(!(what in this.callbacks)) {
                    this.callbacks[what] = [];
                }
                var wrapper = function($this, what, data) {
                    return callback($this, what, data, callback_data);
                };
                wrapper.signature = signature || callback;
                this.callbacks[what].push(wrapper);
            }
        },

        registerUpdate: function(callback, callback_data, signature) { this.register('update', callback, callback_data, signature); },
        registerDestroy: function(callback, callback_data, signature) { this.register('destroy', callback, callback_data, signature); },
        registerReinit: function(callback, callback_data, signature) { this.register('reinit', callback, callback_data, signature); },

        unregister: function(what, signature) {
            if(what in this.callbacks) {
                this.callbacks[what] = $.grep(this.callbacks[what],
                                              function(e, i) { return e.signature != signature; });
                if(this.callbacks[what].length <= 0) {
                    delete this.callbacks[what];
                }
            }
        },

        unregisterUpdate: function(callback) { this.unregister('update', callback); },
        unregisterDestroy: function(callback) { this.unregister('destroy', callback); },
        unregisterReinit: function(callback) { this.unregister('reinit', callback); }

    };

    //
    // Abstract prototype to manage the communication with a single poker server
    //
    jpoker.connection = function(options) {
        $.extend(this, jpoker.connection.defaults, options);
        this.init();
    };

    jpoker.connection.defaults = $.extend({
            url: '',
            async: true,
            lagmax: 6000,
            dequeueFrequency: 50,
            longPollFrequency: 50,
            minLongPollFrequency: 5,
            timeout: 30000,
            retryCount: 10,
            clearTimeout: function(id) { return window.clearTimeout(id); },
            setTimeout: function(cb, delay) { return window.setTimeout(cb, delay); },
            ajax: function(o) { return jQuery.ajax(o); },
            protocol: function() { return document.location.protocol; }
        }, jpoker.watchable.defaults);

    jpoker.connection.prototype = $.extend({}, jpoker.watchable.prototype, {

            LOGIN: 'loging',
            RUNNING: 'running',
            QUITTING: 'quitting',
            USER_INFO: 'retrieving user info',
            RECONNECT: 'trying to reconnect',
            MY: 'searching my tables',
            TABLE_LIST: 'searching tables',
            TOURNEY_LIST: 'searching tourneys',
            TOURNEY_DETAILS: 'retrieving tourney details',
            TABLE_JOIN: 'joining table',
            TABLE_PICK: 'picking table',
            TABLE_QUIT: 'quitting table',
            TOURNEY_REGISTER: 'updating tourney registration',
            PERSONAL_INFO: 'getting personal info',
            CREATE_ACCOUNT: 'creating account',
            PLACES: 'getting player places',
            STATS: 'getting player stats',
            LOCALE: 'setting locales',

            blocked: false,

            lag: 0,

            high: ['PacketPokerChat', 'PacketPokerMessage', 'PacketPokerGameMessage'],

            incomingTimer: -1,

            longPollTimer: -1,

            init: function() {
                jpoker.watchable.prototype.init.call(this);
                this.queues = {};
                this.delays = {};

                if (! this.auth) {
                  this.auth = 'auth=' + this.getAuthHash();
                }
                
                this.session_uid = 'uid=' + jpoker.Crypto.hexSha1Str(this.url + Math.random());

                if (this.urls === undefined) {
                    this.urls = {};
                }
                if (this.urls.avatar === undefined) {
                    this.urls.avatar = this.url.substr(0, this.url.lastIndexOf('/')+1) + 'AVATAR';
                }
                if (this.urls.upload === undefined) {
                    this.urls.upload = this.url.substr(0, this.url.lastIndexOf('/')+1) + 'UPLOAD?' + this.auth;
                }
                this.reset();
            },

            uninit: function() {
                this.blocked = true;
                jpoker.watchable.prototype.uninit.call(this);
                this.reset();
            },

            getAuthHash: function() {
                var auth_cookie = 'JPOKER_AUTH_' + jpoker.url2hash(this.url);
                var auth_hash = $.cookie(auth_cookie);
                if(auth_hash === null) {
                    auth_hash = jpoker.Crypto.hexSha1Str(this.url + Math.random());
                    var expires = new Date();
                    expires.setTime(expires.getTime() + self.authExpires);
                    //$.cookie(auth_cookie, auth_hash, { expires: expires, path: '/' } );
                    $.cookie(auth_cookie, auth_hash, { path: '/' } );
                } else {
                    this.foundAuthCookie = true;
                }
                return auth_hash;
            },

            reset: function() {
                this.clearTimeout(this.longPollTimer);
                this.longPollTimer = -1;
                this.pendingLongPoll = false;
                this.clearTimeout(this.incomingTimer);
                this.incomingTimer = -1;
                // empty the outgoing queue
                jQuery([$.ajax_queue]).queue('ajax', []);
                // empty the incoming queue
                this.queues = {};
                this.packet_id = 0;
                this.delays = {};
                this.sentTime = 0;
                this.connectionState = 'disconnected';
                this.longPoll();
            },

            quit: function() {
                this.longPollFrequency = -1;
            },

            error: function(reason) {
                jpoker.watchable.prototype.setCallbacks.call(this);
                jpoker.connection.prototype.quit.call(this);
                this.reset();
                this.setConnectionState('disconnected');
                jpoker.error(reason);
            },

            setConnectionState: function(state) {
                if(this.connectionState != state) {
                    this.connectionState = state;
                    this.notifyUpdate({type: 'PacketConnectionState', state: state});
                }
            },

            getConnectionState: function() {
                return this.connectionState;
            },

            connected: function() {
                return this.getConnectionState() == 'connected';
            },

            //
            // Call 'handler' for each packet sent to the poker game 'id'
            // If id == 0, 'handler' is called for each packet not associated with
            // a poker game.
            //
            // Prototype: handler(server, id, packet) returns a boolean
            //
            // server: the $.jpoker.server instance connected to the server from
            //        which the packet was received
            // id: is 0 if the packet is not associated to a poker game or the serial
            //     number of the poker game
            // packet: is the packet received from the server
            //
            // If the return value of the handler function is false,
            // the handler is discarded and will not
            // be called again. If the return value is true, the handler is retained
            // and will be called when the next packet matching the 'id' parameter
            // arrives.
            //
            // If the handler throws an exception, the server will be killed and
            // all communications interrupted. The handler must NOT call server.error,
            // it must throw an exception whenever a fatal error occurs.
            //
            registerHandler: function(id, handler, handler_data, signature) {
                this.register(id, handler, handler_data, signature);
            },

            unregisterHandler: function(id, handler) {
                this.unregister(id, handler);
            },

            handle: function(id, packet) {
                if(jpoker.verbose > 1) {
                    jpoker.message('connection handle ' + id + ': ' + JSON.stringify(packet));
                }
                if(id in this.callbacks) {
                    delete packet.time__;
                    if(jpoker.verbose > 1) {
                        //
                        // For debugging purposes associate a unique ID to each packet in
                        // order to track it in the log messages.
                        //
                        packet.uid__ = jpoker.uid();
                    }
                    try {
                        this.notify(id, packet);
                    } catch(e) {
                        var error = 'ID: ' + id + ', Packet: ' + JSON.stringify(packet) + ', ' + e;
                        this.error(error); // delegate exception handling to the error function
                        return false; // error will throw and this statement will never be reached
                    }
                    return true;
                } else {
                    return false;
                }
            },

            delayQueue: function(id, time) {
                this.delays[id] = time;
            },

            noDelayQueue: function(id) {
                if(id in this.delays) {
                    delete this.delays[id];
                }
            },

            // null => no delay
            handleDelay: function(id) {
                if(id in this.delays) {
                    return this.delays[id];
                } else {
                    return null;
                }
            },

            sendPacket: function(packet, callback) {
                var reqtype,
                    packet_to_send = packet,
                    callback_to_send = callback,
                    thisObject = this;

                if(this.pendingLongPoll) {
                    if(jpoker.verbose > 0) {
                        jpoker.message('sendPacket PacketPokerLongPollReturn');
                    }
                    this.sendPacketAjax({ type: 'PacketPokerLongPollReturn' }, 'direct');
                }

                var reqtype = 'next';

                if(packet.type == 'PacketPokerLongPoll') {
                    this.pendingLongPoll = true;
                    reqtype = 'queue';
                }

                thisObject.sendPacketAjax(packet_to_send, reqtype, callback_to_send);
            },

            receivePacket: function(data) {
                if(this.pendingLongPoll) {
                    this.scheduleLongPoll(0);
                }
                this.pendingLongPoll = false;
                this.queueIncoming(data);
            },

            sendPacketAjax: function(packet, mode, callback) {
                var $this = this;
                var json_data = JSON.stringify(packet);
                if(jpoker.verbose > 0) {
                    jpoker.message('sendPacket (' + mode + ')' + json_data);
                }
                var packet_type = packet.type;
                var retry = 0;

                var timeout = 3000;
                if (packet_type == 'PacketPokerLongPoll') {
                  timeout = this.timeout;
                }
            
                var args = {
                    async: this.async,
                    data: json_data,
                    mode: mode,
                    timeout: timeout,
                    url: this.url + '?' + this.auth + '&' + this.session_uid,
                    type: 'POST',
                    dataType: 'text json',
                    global: false, // do not fire global events
                    success: function(data, status) {
                        $('.ajax-retry').remove();
                        if(jpoker.verbose > 0) {
                            jpoker.message('success ' + json_data + ' returned ' + data);
                        }
                        if($this.getConnectionState() != 'connected') {
                            $this.setConnectionState('connected');
                        }
                        if(packet_type != 'PacketPokerLongPollReturn') {
                            $this.receivePacket(data);
                        }
                        if (callback !== undefined) {
                            callback(data, status);
                        }
                    },
                    error: function(xhr, status, error) {
                        if(jpoker.verbose > 0) {
                            jpoker.message('error callback fire for ' + json_data);
                        }
                        if(status == 'timeout') {
                            if ($this.getConnectionState() != 'disconnected') {
                              $this.setConnectionState('disconnected');
                              $.jpoker.errorHandler({}, "Connection timed out.");
                              $this.reset();
                            }
                            //window.location.reload();
                        } else {
                            switch (xhr.status) {
                              case 0: // when the browser aborts xhr ( unload for instance )
                                return; // discard the error
                              case 12152:
                              case 12030:
                              case 12031:
                                 ++retry;
                                if (retry < $this.retryCount) {
                                    return false; // retry
                                }
                                error = 'ajax retry count exceeded: '+ retry;
                                break;
                            }

                            $this.error({ 
                              xhr: xhr,
                              status: status,
                              url: $this.url,
                              error: error
                            });
                        }
                    }
                };
                this.sentTime = jpoker.now();
                this.ajax(args);
            },

            longPoll: function() {
                if(this.longPollFrequency > 0) {
                    var delta = jpoker.now() - this.sentTime;
                    var in_line = jQuery([$.ajax_queue]).queue('ajax').length;
                    if(in_line <= 0 &&
                       delta > this.longPollFrequency) {
                        this.clearTimeout(this.longPollTimer);
                        this.longPollTimer = -1;
                        this.sendPacket({ type: 'PacketPokerLongPoll' });
                    } else {
                        this.scheduleLongPoll(delta > 0 ? delta : 0);
                    }
                }
            },

            scheduleLongPoll: function(delta) {
                this.clearTimeout(this.longPollTimer);
                var $this = this;
                this.longPollTimer = this.setTimeout(
                    function() {
                        $this.longPoll();
                    }, Math.max(this.minLongPollFrequency, this.longPollFrequency - delta));
            },

            queueIncoming: function(packets) {
                if(!this.blocked) {
                    for(var i = 0; i < packets.length; i++) {
                        packet = packets[i];
                        if('session' in packet) {
                            delete packet.session;
                        }
                        packet.time__ = jpoker.now();

                        var id;
                        if('game_id' in packet) {
                            id = packet.game_id;
                        } else {
                            id = 0;
                        }
                        if(!(id in this.queues)) {
                            this.queues[id] = { 'high': {'packets': [],
                                                         'delay': 0 },
                                                'low': {'packets': [],
                                                        'delay': 0 } };
                        }
                        var queue;
                        if(jQuery.inArray(packet.type, this.high) >= 0) {
                          if (packet.type == 'PacketPokerChat' && packet.serial == 0) {
                            queue = this.queues[id].low;
                          }
                          else {
                            queue = this.queues[id].high;
                          }
                        } else {
                          queue = this.queues[id].low;
                        }

/*                        if (
                            queue.packets[0] &&
                            packet.packet_id > 0 && 
                            queue.packets[0].packet_id > 0 && 
                            packet.packet_id < queue.packets[0].packet_id && 
                            queue.packets[0].packet_id - packet.packet_id < 3000000
                        ) {
                          queue.packets.unshift(packet);
                        }
                        else { */
                          queue.packets.push(packet);
                        /* } */

                        if(jpoker.verbose > 1) {
                            jpoker.message('queueIncoming ' + JSON.stringify(packet));
                        }
                    }
                    this.clearTimeout(this.incomingTimer);
                    var $this = this;
                    this.incomingTimer = this.setTimeout(function() {
                            $this.dequeueIncoming(); },
                        this.dequeueFrequency);
                }
            },

            dequeueIncoming: function() {
                if(!this.blocked) {
                    now = jpoker.now();
                    this.lag = 0;

                    for(var id in this.queues) {
                        for(var priority in this.queues[id]) {
                            var queue = this.queues[id][priority];
                            if(queue.packets.length <= 0) {
                                continue;
                            }
                            lag = now - queue.packets[0].time__;
                            this.lag = this.lag > lag ? this.lag : lag;
                            if(queue.delay > now && lag > this.lagmax) {
                                queue.delay = 0;
                            }
                            if(queue.delay <= now) {
                                delay = this.handleDelay(id);
                                if(lag > this.lagmax || delay === null || delay <= now) {
                                    if(this.handle(id, queue.packets[0])) {
                                        queue.packets.shift();
                                    }
                                } else {
                                    queue.delay = delay;
                                }
                            } else if(jpoker.verbose > 0) {
                                jpoker.message(_("wait for {delay}s for queue {id}").supplant({ 'delay': queue.delay / 1000.0, 'id': id}));
                            }
                        }
                        //
                        // get rid of queues with no associated delay AND no pending packets.
                        // this.queues may be undefined if a handler destroyed the object
                        //
                        if(id in this.queues) {
                            queue = this.queues[id];
                            if(queue.high.packets.length <= 0 && queue.low.packets.length <= 0) {
                                if(queue.high.delay <= now && queue.low.delay <= now) {
                                    delete this.queues[id];
                                }
                            }
                        }
                    }
                }
                var empty = true;
                for(var j in this.queues) {
                    empty = false;
                    break;
                }
                this.clearTimeout(this.incomingTimer);
                if(!empty) {
                    var $this = this;
                    this.incomingTimer = this.setTimeout(function() {
                            $this.dequeueIncoming(); },
                        this.dequeueFrequency);
                }
            }

        });

    //
    // server
    //
    jpoker.server = function(options) {
        $.extend(this, jpoker.server.defaults, options);
        this.init();
    };

    jpoker.server.defaults = $.extend({
            playersCount: null,
            tablesCount: null,
            playersTourneysCount: null,
            tourneysCount: null,
            spawnTable: function(server, packet) {},
            placeTourneyRowClick: function(server, packet) {},
            placeChallengeClick: function(server, serial) {
                server.sendPacket({
                        type: 'PacketPokerCreateTourney',
                        serial: server.serial,
                        name: server.serial + 'versus' + serial,
                        players: [ server.serial, serial ]
                    });
            },
            tourneyRowClick: function(server, packet) {},
            rankClick: function(server, tourney_serial) {},
            reconnectFinish: function(server) {},
            setInterval: function(cb, delay) { return window.setInterval(cb, delay); },
            clearInterval: function(id) { return window.clearInterval(id); },
            authExpires: 60 * 60 * 1000 // auth cookie expires after 1 hour by default
        }, jpoker.connection.defaults);

    jpoker.server.prototype = $.extend({}, jpoker.connection.prototype, {
            init: function() {
                jpoker.connection.prototype.init.call(this);
                this.tables = {};
                this.tableLists = {};
                this.timers = {};

                if (! this.serial) {
                  this.serial = 0;
                }
                  
                this.userInfo = {};
                this.preferences = new jpoker.preferences(jpoker.url2hash(this.url));
                this.registerHandler(0, this.handler);
                if(jpoker.doReconnect && (jpoker.doReconnectAlways || this.foundAuthCookie || this.protocol() == 'file:')) {
                    this.reconnect();
                }
            },

            uninit: function() {
                this.clearTimers();
                this.unregisterHandler(0, this.handler);
                $.each(this.tables, function(game_id, table) {
                        table.uninit();
                    });
                this.tables = {};
                jpoker.connection.prototype.uninit.call(this);
            },

            reset: function() {
                this.clearTimers();
                jpoker.connection.prototype.reset.call(this);
                this.stateQueue = [];
                this.setState(this.RUNNING, 'reset');
            },

            quit: function(callback) {
                this.queueRunning(function(server) {
                        jpoker.connection.prototype.quit.call(server);
                        server.setState(server.QUITTING, 'quit');
                        server.sendPacket({ type: 'PacketQuit' }, 
                                          function() {
                                              server.uninit();
                                              if (callback !== undefined) {
                                                  callback(server);
                                              }
                                          });
                    });
            },

            queueRunning: function(callback) {
                this.stateQueue.push(callback);
                this.dequeueRunning();
            },

            dequeueRunning: function() {
                while(this.stateQueue.length > 0 && this.state == this.RUNNING) {
                    var callback = this.stateQueue.shift();
                    callback(this);
                }
            },

            setState: function(state, comment) {
                if(this.state != state) {
                    this.state = state;
                    if(!state) {
                        jpoker.error('undefined state');
                    }
                    if(jpoker.verbose > 0) {
                        jpoker.message('setState ' + state + ' ' + comment);
                    }
                    this.notifyUpdate({type: 'PacketState', state: state});
                    this.dequeueRunning();
                }
            },

            getState: function() {
                return this.state;
            },

            clearTimers: function() {
                var $this = this;
                if (this.timers) {
                    $.each(this.timers, function(key, value) {
                            $this.clearInterval(value.timer);
                        });
                    this.timers = {};
                }
            },

            handler: function(server, game_id, packet) {
                if(jpoker.verbose > 0) {
                    jpoker.message('server.handler ' + JSON.stringify(packet));
                }

                switch(packet.type) {

                case 'PacketPokerTourneyStart':
                  server.tableJoin(packet.table_serial);
                break;

                case 'PacketPokerTable':
                  if (server.onTourneyStart && packet.reason == 'TourneyStart') {
                    try {
                      server.onTourneyStart(packet.id);
                    }
                    catch (e) {
                      alert("Popup blocker prevents table autospawn. Please disable all popup blockers for https://betco.in");
                    }
                  } 
                  else {
                    if(packet.id in server.tables) {
                        server.tables[packet.id].reinit(packet);
                    } else {
                        var table = new jpoker.table(server, packet);
                        server.tables[packet.id] = table;
                        server.notifyUpdate(packet);
                    }
                    packet.game_id = packet.id;
                    server.spawnTable(server, packet);
                  }
                break;

                case 'PacketSerial':
                server.setSerial(packet);
                break;

                case 'PacketPokerPlayerInfo':
                server.userInfo = packet;
                break;

                case 'PacketPokerUserInfo':
                server.userInfo = packet;
                for(id in server.tables) {
                    packet.game_id = id;
                    server.tables[id].handler(server, game_id, packet);
                    server.tables[id].notifyUpdate(packet);
                }
                delete packet.game_id;
                server.notifyUpdate(packet);
                server.setState(server.RUNNING, 'PacketPokerUserInfo');
                break;

                case 'PacketPokerPlayerStats':
                for (id in server.tables) {
                    packet.game_id = id;
                    server.tables[id].handler(server, id, packet);
                }
                delete packet.game_id;
                break;

                }

                return true;
            },

            setSerial: function(packet) {
                this.serial = packet.serial;
                var id;
                for(id in this.tables) {
                    this.tables[id].notifyUpdate(packet);
                }
            },

            reconnect: function() {
                this.setState(this.RECONNECT);
                //
                // the answer to PacketPokerGetPlayerInfo gives back the serial, if and
                // only if the session is still valid. Otherwise it returns an error
                // packet and the session must be re-initialized.
                //
                var handler = function(server, game_id, packet) {
                    if(packet.type == 'PacketPokerPlayerInfo') {
                        server.setSerial({ type: 'PacketSerial', serial: packet.serial });
                        if (jpoker.doRejoin) {
                            server.rejoin();
                        } else {
                            server.setState(server.RUNNING, 'no rejoin');
                        }
                        return false;
                    } else if(packet.type == 'PacketError') {
                        if(packet.other_type != jpoker.packetName2Type.POKER_GET_PLAYER_INFO) {
                            jpoker.error('unexpected error while reconnecting ' + JSON.stringify(packet));
                        }
                        server.setState(server.RUNNING, 'PacketError reconnect');
                        return false;
                    }
                    return true;
                };
                this.registerHandler(0, handler);
                this.sendPacket({ type: 'PacketPokerGetPlayerInfo' });
            },

            refresh: function(tag, request, handler, state, options) {
                var timerRequest = jpoker.refresh(this, request, handler, state, options);
                if(timerRequest.timer) {
                    if(tag in this.timers) {
                        this.clearInterval(this.timers[tag].timer);
                    }
                    this.timers[tag] = timerRequest;
                }
                return timerRequest;
            },

            stopRefresh: function(tag) {
                if (this.timers[tag] !== undefined) {
                    this.clearInterval(this.timers[tag].timer);
                    delete this.timers[tag];
                }
            },

            //
            // tables lists
            //
            refreshTables: function(string, options) {

                if(!(string in this.tables)) {
                    this.tableLists[string] = {};
                }

                var request = function(server) {
                    server.sendPacket({
                            type: 'PacketPokerTableSelect',
                            string: string
                        });
                };

                var handler = function(server, packet) {
                    var info = server.tableLists && server.tableLists[string];
                    if(packet.type == 'PacketPokerTableList') {
                        info.packet = packet;
                        // although the tables/players count is sent with each
                        // table list, it is global to the server
                        server.playersCount = packet.players;
                        server.tablesCount = packet.tables;
                        server.notifyUpdate(packet);
                        return false;
                    }
                    return true;
                };

                return this.refresh('tableList', request, handler, this.TABLE_LIST, options);
            },

            //
            // table information
            //
            tableInformation: function(game_id, callback) {
                this.queueRunning(function(server) {
                                      server.setState(server.TABLE_JOIN, 'tableInformation');
                                      var users = {};
                                      var spawnTable = server.spawnTable;
                                      var handler = function(server, game_id, packet) {
                                          if(packet.type == 'PacketPokerPlayerArrive') {
                                              users[packet.serial] = { name: packet.name, seat: packet.seat, serial: packet.serial };
                                          } else if(packet.type == 'PacketPokerPlayerChips') {
                                              users[packet.serial].chips = packet.money;
                                          } else if(packet.type == 'PacketPokerStreamMode') {
                                              server.spawnTable = spawnTable;
                                              server.tables[game_id].handler(server, game_id,
                                                                             { type: 'PacketPokerTableDestroy',
                                                                               game_id: game_id });
                                              server.setState(server.RUNNING, 'tableInformation');
                                              var table_info = [];
                                              for(serial in users) {
                                                  table_info.push(users[serial]);
                                              }
                                              callback(server, table_info);
                                              return false;
                                          }
                                          return true;
                                      };
                                      server.spawnTable = function() { };
                                      server.registerHandler(game_id, handler);
                                      server.sendPacket({ type: 'PacketPokerTableJoin',
                                                          game_id: game_id });
                                  });
            },

            //
            // tourneys lists
            //
            refreshTourneys: function(string, options) {

                var request = function(server) {
                    server.sendPacket({
                            type: 'PacketPokerTourneySelect',
                            string: string
                        });
                };

                var handler = function(server, packet) {
                    if(packet.type == 'PacketPokerTourneyList') {
                        // although the tourneys/players count is sent with each
                        // tourney list, it is global to the server
                        server.playersTourneysCount = packet.players;
                        server.tourneysCount = packet.tourneys;
                        server.notifyUpdate(packet);
                        return false;
                    }
                    return true;
                };

                return this.refresh('tourneyList', request, handler, this.TOURNEY_LIST, options);
            },

            //
            // tourney details
            //
            refreshTourneyDetails: function(game_id, options) {

                var request = function(server) {
                    server.sendPacket({
                            type: 'PacketPokerGetTourneyManager',
                            tourney_serial: game_id
                        });
                };

                var handler = function(server, packet) {
                    if(packet.type == 'PacketPokerTourneyManager') {
                        // although the tourneys/players count is sent with each
                        // tourney list, it is global to the server
                        server.notifyUpdate(packet);
                        return false;
                    }
                    return true;
                };

                return this.refresh('tourneyDetails', request, handler, this.TOURNEY_DETAILS, options);
            },

            //
            // login / logout
            //
            loggedIn: function() {
                return this.serial !== 0;
            },

            login: function(name, password) {
                if(this.serial !== 0) {
                    throw _("{url} attempt to login {name} although serial is {serial} instead of 0").supplant({ 'url': this.url, 'name': name, 'serial': this.serial});
                }
                this.setState(this.LOGIN);
                this.userInfo.name = name;
                this.sendPacket({
                        type: 'PacketLogin',
                        name: name,
                        password: password
                    });
                this.getUserInfo(); // will fire when login is complete
                var answer = function(server, game_id, packet) {
                    switch(packet.type) {

                    case 'PacketAuthOk':
                    return true;

                    case 'PacketAuthRefused':
                    jpoker.dialog(_(packet.message) + _(" (login name is {name} )").supplant({ 'name': name }));
                    server.notifyUpdate(packet);
                    server.setState(server.RUNNING, 'PacketAuthRefused');
                    return false;

                    case 'PacketError':
                    if(packet.other_type == jpoker.packetName2Type.LOGIN) {
                        jpoker.dialog(_("user {name} is already logged in".supplant({ 'name': name })));
                        server.notifyUpdate(packet);
                    }
                    server.setState(server.RUNNING, 'login PacketError');
                    return false;

                    case 'PacketSerial':
                    server.notifyUpdate(packet);
                    server.setState(server.RUNNING, 'login serial received');
                    return false;
                    }

                    return true;
                };
                this.registerHandler(0, answer);
            },

            logout: function() {
                if(this.serial !== 0) {
                    //
                    // redundant with PacketLogout handler in server to ensure all
                    // notify functions will see serial == 0 regardless of the
                    // order in which they are called.
                    //
                    this.serial = 0;
                    this.userInfo = {};
                    var packet = { type: 'PacketLogout' };
                    this.sendPacket(packet);
                    //
                    // LOGOUT IMPLIES ALL TABLES ARE DESTROYED INSTEAD
                    //
                    for(var game_id in this.tables) {
                        this.tables[game_id].notifyUpdate(packet);
                    }
                    this.notifyUpdate(packet);
                }
            },

            getUserInfo: function() {
                this.queueRunning(function(server) {
                        server.setState(server.USER_INFO);
                        server.sendPacket({
                                type: 'PacketPokerGetUserInfo',
                                    serial: server.serial });
                    });
            },

            rejoin: function() {
                this.setState(this.MY);
                var handler = function(server, game_id, packet) {
                    if(packet.type == 'PacketPokerPlayerPlaces') {
                        for(var i = 0; i < packet.tables.length; i++) {
                            var table_id = packet.tables[i];
                            server.tableJoin(table_id);
                        }
                        server.getUserInfo();
                        server.queueRunning(function(server) { server.reconnectFinish(server); });
                        server.setState(server.RUNNING, 'rejoin');
                        return false;
                    }
                    return true;
                };
                this.registerHandler(0, handler);
                this.sendPacket({ type: 'PacketPokerGetPlayerPlaces', serial: this.serial });
            },

            tableJoin: function(game_id) {
                this.queueRunning(function(server) {
                        server.setState(server.TABLE_JOIN);
                        server.sendPacket({ 'type': 'PacketPokerTableJoin',
                                    'game_id': game_id });
                    });
            },

            tablePick: function(criterion) {
                if (this.loggedIn() === false) {
                    jpoker.dialog(_("User must be logged in"));
                } else {
                    this.queueRunning(function(server) {
                            server.setState(server.TABLE_PICK);
                            var packet = $.extend(criterion, {
                                    type: 'PacketPokerTablePicker',
                                    serial: server.serial,
                                    auto_blind_ante: true
                                });
                            if (packet.variant === '') {
                                delete packet.variant;
                            }
                            if (packet.betting_structure === '') {
                                delete packet.betting_structure;
                            }
                            if (packet.currency_serial !== undefined) {
                                packet.currency_serial = parseInt(packet.currency_serial, 10);
                            } else {
                                delete packet.currency_serial;
                            }
                            server.sendPacket(packet);
                            server.registerHandler(0, function(server, unused_game_id, packet) {
                                    if ((packet.type == 'PacketPokerTable') &&
                                        (packet.reason == 'TablePicker')) {
                                        server.setState(server.RUNNING, 'PacketPokerTable');
                                        return false;
                                    } else if ((packet.type == 'PacketPokerError') &&
                                               (packet.other_type == jpoker.packetName2Type.POKER_TABLE_PICKER)) {
                                        server.notifyUpdate(packet);
                                        server.setState(server.RUNNING, 'PacketPokerError');
                                        return false;
                                    }
                                    return true;
                                });
                        });
                }
            },

            tableQuit: function(game_id) {
                if (this.loggedIn() === false) {
                  jpoker.dialog(_("User must be logged in"));
                } else {
                  this.queueRunning(function(server) {
                    server.setState(server.TABLE_QUIT);
                    server.sendPacket(
                      { type: 'PacketPokerTableQuit', game_id: game_id }, 
                      function() {
                            server.setState(server.RUNNING, 'PacketPokerTableQuit');
                      }
                    );
                  });
                }
            },

            bankroll: function(currency_serial) {
                var key = 'X' + currency_serial;
                if(this.loggedIn() && 'money' in this.userInfo && key in this.userInfo.money) {
                    return this.userInfo.money[key][0] / 100; // PacketPokerUserInfo for documentation
                }
                return 0;
            },

            tourneyRegister: function(game_id) {
                this.queueRunning(function(server) {
                        server.setState(server.TOURNEY_REGISTER);
                        server.sendPacket({'type': 'PacketPokerTourneyRegister', 'serial': server.serial, 'game_id' : game_id});
                        server.registerHandler(game_id, function(server, game_id, packet) {
                                if (packet.type == 'PacketPokerTourneyRegister') {
                                    server.notifyUpdate(packet);
                                    server.queueRunning(function() {
                                            if (server.timers.tourneyDetails !== undefined) {
                                                server.timers.tourneyDetails.request();
                                            }
                                        });
                                    server.setState(server.RUNNING, 'PacketPokerTourneyRegister');
                                    return false;
                                }
                                return true;
                            });
                        server.registerHandler(0, function(server, unused_game_id, packet) {
                                if ((packet.type == 'PacketError') && (packet.subpacket == jpoker.packetName2Type.PACKET_POKER_TOURNEY_REGISTER)) {
                                    var code2message = {
                                        1:_("Tournament {game_id} does not exist"),
                                        2:_("Player {serial} already registered in tournament {game_id}"),
                                        3:_("Registration refused in tournament {game_id}"),
                                        4:_("Not enough money to enter the tournament {game_id}")};
                                    if (code2message[packet.code] !== undefined) {
                                        packet.message = code2message[packet.code].supplant({game_id: game_id, serial: server.serial});
                                    }
                                    jpoker.dialog(packet.message);
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketError');
                                    return false;
                                }
                                return true;
                            });
                    });
            },

            tourneyUnregister: function(game_id) {
                this.queueRunning(function(server) {
                        server.setState(server.TOURNEY_REGISTER);
                        server.sendPacket({'type': 'PacketPokerTourneyUnregister', 'serial': server.serial, 'game_id' : game_id});
                        server.registerHandler(game_id, function(server, game_id, packet) {
                                if (packet.type == 'PacketPokerTourneyUnregister') {
                                    server.notifyUpdate(packet);
                                    server.queueRunning(function() {
                                            if (server.timers.tourneyDetails !== undefined) {
                                                server.timers.tourneyDetails.request();
                                            }
                                        });
                                    server.setState(server.RUNNING, 'PacketPokerTourneyUnregister');
                                    return false;
                                }
                                return true;
                            });
                        server.registerHandler(0, function(server, unused_game_id, packet) {
                                if ((packet.type == 'PacketError') && (packet.subpacket == jpoker.packetName2Type.PACKET_POKER_TOURNEY_UNREGISTER)) {
                                    var code2message = {
                                        1: _("Tournament {game_id} does not exist"),
                                        2: _("Player {serial} is not registered in tournament {game_id}"),
                                        3: _("It is too late to unregister player {serial} from tournament {game_id}")};
                                    if (code2message[packet.code] !== undefined) {
                                        packet.message = code2message[packet.code].supplant({game_id: game_id, serial: server.serial});
                                    }
                                    jpoker.dialog(_(packet.message));
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketError');
                                    return false;
                                }
                                return true;
                            });
                    });
            },

            getPersonalInfo : function() {
                if (this.loggedIn())  {
                    this.queueRunning(function(server) {
                            server.setState(server.PERSONAL_INFO);
                            server.sendPacket({'type': 'PacketPokerGetPersonalInfo', 'serial': server.serial});
                            server.registerHandler(0, function(server, unused_game_id, packet) {
                                    if (packet.type == 'PacketPokerPersonalInfo') {
                                        server.notifyUpdate(packet);
                                        server.setState(server.RUNNING, 'PacketPokerPersonalInfo');
                                        return false;
                                    }
                                    return true;
                                });
                        });
                } else {
                    jpoker.dialog(_("User must be logged in"));
                }
            },

            setPersonalInfo : function(info) {
                this.queueRunning(function(server) {
                        if (info.password != info.password_confirmation) {
                            jpoker.dialog(_("Password confirmation does not match"));
                        } else {
                            server.setState(server.PERSONAL_INFO);
                            var personalInfoDefaults = {
                                'type' : 'PacketPokerSetAccount',
                                'serial': server.serial,
                                'name': server.userInfo.name,
                                'password': ''
                            };
                            server.sendPacket($.extend(personalInfoDefaults, info));
                            server.registerHandler(0, function(server, unused_game_id, packet) {
                                    if (packet.type == 'PacketPokerPersonalInfo') {
                                        packet.set_account = true;
                                        server.notifyUpdate(packet);
                                        server.setState(server.RUNNING, 'PacketPokerPersonalInfo');
                                        return false;
                                    }
                                    else if (packet.type == 'PacketError') {
                                        jpoker.dialog(packet.message);
                                        server.notifyUpdate(packet);
                                        server.setState(server.RUNNING, 'PacketError');
                                    }
                                    return true;
                                });
                        }
                    });
            },

            createAccount : function(options) {
                this.queueRunning(function(server) {
                        if (options.password != options.password_confirmation) {
                            jpoker.dialog(_("Password confirmation does not match"));
                        } else {
                            server.setState(server.CREATE_ACCOUNT);
                            var packet = {
                                'type' : 'PacketPokerCreateAccount'
                            };
                            server.sendPacket($.extend(packet, options));
                            server.registerHandler(0, function(server, unused_game_id, packet) {
                                    if (packet.type == 'PacketPokerPersonalInfo') {
                                        server.notifyUpdate(packet);
                                        server.queueRunning(function(server) {
                                                server.login(options.name, options.password);
                                            });
                                        server.setState(server.RUNNING, 'PacketPokerPersonalInfo');
                                        return false;
                                    }
                                    else if (packet.type == 'PacketError') {
                                        jpoker.dialog(packet.message);
                                        server.notifyUpdate(packet);
                                        server.setState(server.RUNNING, 'PacketError');
                                        return false;
                                    }
                                    return true;
                                });
                        }
                    });
            },

            selectTables : function(string) {
                this.queueRunning(function(server) {
                        server.setState(server.TABLE_LIST);
                        server.sendPacket({'type': 'PacketPokerTableSelect', 'string': string});
                        server.registerHandler(0, function(server, unused_game_id, packet) {
                                if (packet.type == 'PacketPokerTableList') {
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketPokerTableList');
                                    return false;
                                }
                                return true;
                            });
                    });
            },

            getPlayerPlaces : function(serial) {
                if ((this.loggedIn() === false) && (serial === undefined)) {
                    jpoker.dialog(_("User must be logged in"));
                }
                else {
                    var player_serial = serial;
                    if (player_serial === undefined) {
                        player_serial = this.serial;
                    }
                    this.queueRunning(function(server) {
                            server.setState(server.PLACES);
                            server.sendPacket({'type': 'PacketPokerGetPlayerPlaces', 'serial': player_serial});
                            server.registerHandler(0, function(server, unused_game_id, packet) {
                                    if (packet.type == 'PacketPokerPlayerPlaces') {
                                        server.notifyUpdate(packet);
                                        server.setState(server.RUNNING, 'PacketPokerPlayerPlaces');
                                        return false;
                                    }
                                    return true;
                                });
                        });
                }
            },

            getPlayerPlacesByName : function(name, options) {
                this.queueRunning(function(server) {
                        server.setState(server.PLACES);
                        server.sendPacket({'type': 'PacketPokerGetPlayerPlaces', 'name': name});
                        server.registerHandler(0, function(server, unused_game_id, packet) {
                                if (packet.type == 'PacketPokerPlayerPlaces') {
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketPokerPlayerPlaces');
                                    return false;
                                } else if ((packet.type == 'PacketError') && (packet.other_type == jpoker.packetName2Type.PACKET_POKER_PLAYER_PLACES)) {
                                    if (options === undefined || options.dialog) {
                                        jpoker.dialog(_("No such user: "+name));
                                    }
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketError');
                                    return false;
                                }
                                return true;
                            });
                    });
            },

            getPlayerStats : function(serial) {
                this.queueRunning(function(server) {
                        server.setState(server.STATS);
                        server.sendPacket({'type': 'PacketPokerGetPlayerStats', 'serial': serial});
                        server.registerHandler(0, function(server, unused_game_id, packet) {
                                if (packet.type == 'PacketPokerPlayerStats') {
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketPokerPlayerStats');
                                    return false;
                                }
                                return true;
                            });
                    });
            },

            setLocale: function(locale, game_id) {
                this.queueRunning(function(server) {
                        server.setState(server.LOCALE);
                        server.sendPacket({'type': 'PacketPokerSetLocale', 'serial': server.serial, 'locale': locale, 'game_id': game_id});
                        server.registerHandler(0, function(server, unused_game_id, packet) {
                                if (packet.type == 'PacketAck') {
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketAck');
                                    return false;
                                }
                                else if (packet.type == 'PacketPokerError' && packet.other_type == jpoker.packetName2Type.PACKET_POKER_SET_LOCALE) {
                                    jpoker.dialog('setLocale failed: ' + packet.message);
                                    server.notifyUpdate(packet);
                                    server.setState(server.RUNNING, 'PacketError');
                                }
                                return true;
                            });
                    });
            }
        });

    //
    // table
    //
    jpoker.table = function(server, packet) {
        $.extend(this, jpoker.table.defaults, packet);
        if (packet.betting_structure) {
            this.is_tourney = packet.betting_structure.search(/^level-/) === 0;
        } else {
            this.is_tourney = false;
        }
        if (packet.seats) {
            this.max_players = packet.seats;
        } else {
            this.max_players = 10;
        }
        this.url = server.url;
        this.init();
        server.registerHandler(packet.id, this.handler);
    };

    jpoker.table.defaults = {
        betThisRound: false,
    };

    jpoker.table.prototype = $.extend({}, jpoker.watchable.prototype, {
            init: function() {
                jpoker.watchable.prototype.init.call(this);
                this.reset();
            },

            uninit: function(arg) {
                jpoker.watchable.prototype.uninit.call(this, arg);
                for(var serial in this.serial2player) {
                    this.serial2player[serial].uninit();
                }
                this.reset();
            },

            reinit: function(table) {
                if(table) {
                    $.extend(this, jpoker.table.defaults, table);
                }
                for(var serial in this.serial2player) {
                    this.serial2player[serial].uninit();
                }
                this.reset();
                this.notifyReinit(table);
            },

            reset: function() {
                this.serial2player = {};
                this.seats = [ null, null, null, null, null,
                               null, null, null, null, null ];
                this.resetSeatsLeft();
                this.board = [ null, null, null, null, null ];
                this.pots = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
                this.buyIn = { min: 1000000000, max: 1000000000, best: 1000000000, bankroll: 0 };
                this.dealer = -1;
                this.position = -1;
                this.state = 'end';
                this.tourney_rank = undefined;
            },

            resetSeatsLeft: function() {
                switch (this.max_players) {
                case 2:
                this.seats_left = [2, 7];
                break;
                case 3:
                this.seats_left = [2, 7, 5];
                break;
                case 4:
                this.seats_left = [1, 6, 3, 8];
                break;
                case 5:
                this.seats_left = [0, 2, 4, 6, 8];
                break;
                case 6:
                this.seats_left = [0, 2, 4, 5, 7, 9];
                break;
                case 7:
                this.seats_left = [0, 2, 3, 5, 6, 8, 9];
                break;
                case 8:
                this.seats_left = [1, 2, 3, 4, 5, 6, 7, 8];
                break;
                case 9:
                this.seats_left = [0, 1, 2, 3, 4, 5, 6, 7, 8];
                break;
                case 10:
                this.seats_left = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9];
                break;
                default:
                this.seats_left = [];
                break;
                }
            },

            buyInLimits: function() {
                var max = Math.min(this.buyIn.max, this.buyIn.bankroll);
                var min = Math.min(this.buyIn.min, this.buyIn.bankroll);
                var best = Math.min(this.buyIn.best, this.buyIn.bankroll);
                return [ min, best, max ];
            },

            handler: function(server, game_id, packet) {
                if(jpoker.verbose > 0) {
                    jpoker.message('table.handler ' + JSON.stringify(packet));
                }

                var table = server.tables[packet.game_id];
                if(!table) {
                    jpoker.message('unknown table ' + packet.game_id);
                    return true;
                }
                var url = server.url;
                var serial = packet.serial;

                switch(packet.type) {

                // The server sends a PacketPokerMessage when broadcasting
                // informative announcements to players, such as scheduled
                // maintenance.
                case 'PacketPokerMessage':
                case 'PacketPokerGameMessage':
                jQuery.jpoker.dialog(packet.string);
                break;


                case 'PacketPokerBatchMode':
                    break;

                case 'PacketPokerStreamMode':
                    server.setState(server.RUNNING, 'PacketPokerStreamMode');
                    break;

                case 'PacketPokerTableDestroy':
                    table.uninit(packet);
                    delete server.tables[game_id];
                    break;

                case 'PacketPokerPlayerArrive':
                    packet.avatar_url = packet.url;
                    if(server.loggedIn() && packet.serial == server.serial) {
                        table.serial2player[serial] = new jpoker.playerSelf(server, packet);
                    } else {
                        table.serial2player[serial] = new jpoker.player(server, packet);
                    }
                    table.seats[packet.seat] = serial;
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerPlayerLeave':
                    table.seats[packet.seat] = null;
                    table.serial2player[serial].uninit();
                    delete table.serial2player[serial];
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerBoardCards':
                    for(var i = 0; i < packet.cards.length; i++) {
                        table.board[i] = packet.cards[i];
                    }
                    for(var j = packet.cards.length; j < table.board.length; j++) {
                        table.board[j] = null;
                    }
            
                    // we reset bet state to false on every street except preflop
                    if(packet.cards.length == 0) {
                        table.betThisRound = true;
                    } else {
                        table.betThisRound = false;
                    }
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerBestCards':
                case 'PacketPokerDealCards':
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerPotChips':
                    table.pots[packet.index] = jpoker.chips.chips2value(packet.bet);
                    $.each(table.serial2player, function(serial, player) {
                            player.handler(server, game_id, packet);
                        });
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerChipsPotReset':
                    table.pots = [ 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ];
                    $.each(table.serial2player, function(serial, player) {
                            player.handler(server, game_id, packet);
                        });
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerState':
                    table.state = packet.string;
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerDealer':
                    table.dealer = packet.dealer;
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerPosition':
                    table.serial_in_position = packet.serial;
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerBetLimit':
                    table.betLimit = {
                        min: packet.min / 100,
                        max: packet.max / 100,
                        step: packet.step / 100,
                        call: packet.call / 100,
                        allin: packet.allin / 100,
                        pot: packet.pot / 100
                    };
                    break;

                case 'PacketPokerSelfLostPosition':
                    // use serial for dispatching because the serial of the
                    // player in position is not used
                    serial = server.serial;
                    packet.serial = serial;
                    break;

                case 'PacketPokerBuyInLimits':
                    table.buyIn = {
                        min: packet.min / 100,
                        max: packet.max / 100,
                        best: packet.best / 100,
                        rebuy_min: packet.rebuy_min / 100
                    };
                    table.buyIn.bankroll = server.bankroll(table.currency_serial);
                    break;

                case 'PacketPokerUserInfo':
                    table.buyIn.bankroll = server.bankroll(table.currency_serial);
                    break;

                case 'PacketPokerChat':
                case 'PacketPokerTimeoutWarning':
                case 'PacketPokerTimeoutNotice':
                case 'PacketPokerMuckRequest':
                case 'PacketPokerSelfInPosition':
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerStart':
                    table.level = packet.level;
                    $.each(table.serial2player, function(serial, player) {
                            player.handler(server, game_id, packet);
                        });
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerBeginRound':
                case 'PacketPokerEndRound':
                case 'PacketPokerHighestBetIncrease':
                case 'PacketPokerInGame':
                    $.each(table.serial2player, function(serial, player) {
                            player.handler(server, game_id, packet);
                        });
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerTableTourneyBreakBegin':
                case 'PacketPokerTableTourneyBreakDone':
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerTourneyRank':
                    table.tourney_rank = packet;
                    table.notifyUpdate(packet);
                    break;

                case 'PacketPokerShowdown':
                    table.notifyUpdate(packet);
                    break;
                }

                if(serial in table.serial2player) {
                    table.serial2player[serial].handler(server, table, packet);
                }

                return true;
            }
        });

    //
    // player
    //

    jpoker.player = function(server, packet) {
        $.extend(this, jpoker.player.defaults, packet);
        this.url = server.url;
        this.init();
    };

    jpoker.player.defaults = {
        sit_out: true,
        in_game: false,
        all_in: false,
        broke: true
    };

    jpoker.player.prototype = $.extend({}, jpoker.watchable.prototype, {
            init: function() {
                jpoker.watchable.prototype.init.call(this);
                this.reset();
            },

            uninit: function() {
                jpoker.watchable.prototype.uninit.call(this);
                this.reset();
            },

            reinit: function(player) {
                if(player) {
                    $.extend(this, jpoker.player.defaults, player);
                }
                this.reset();
                this.notifyReinit(player);
            },

            reset: function() {
                this.cards = [ null, null, null, null, null, null, null ];
                this.cards.dealt = false;
                this.money = 0;
                this.bet = 0;
                this.side_pot = undefined;
                this.stats = undefined;
            },


            handler: function(server, table, packet) {
                if(jpoker.verbose > 0) {
                    jpoker.message('player.handler ' + JSON.stringify(packet));
                }

                switch(packet.type) {

                case 'PacketPokerPlayerCards':
                this.cards.dealt = false;
                for(var i = 0; i < packet.cards.length; i++) {
                    if (this.cards[i] === null) {
                        this.cards.dealt = true;
                    }
                    this.cards[i] = packet.cards[i];
                }
                for(var j = packet.cards.length; j < this.cards.length; j++) {
                    this.cards[j] = null;
                }
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerBestCards':
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerFold':
                this.action = _("fold");
                this.in_game = false;
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerCheck':
                this.action = _("check");
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerCall':
                this.action = _("call");
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerRaise':
                
                if(table.betThisRound == false)
                {
                    this.action = _("bet");
                    table.betThisRound = true;
                }
                else
                {
                    this.action = _("raise");
                }
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerStart':
                  this.action = '';
                  this.all_in = false;
                  for(var k = 0; k < this.cards.length; k++) {
                      this.cards[k] = null;
                  }
                  $(".jpoker_auto_action input").removeAttr("checked");
                  this.notifyUpdate(packet);
                break;

                case 'PacketPokerBeginRound':
                case 'PacketPokerHighestBetIncrease':
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerInGame':
                this.in_game = ($.inArray(this.serial, packet.players) != -1);
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerEndRound':
                this.action = '';
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerPlayerChips':
                this.money = packet.money / 100;
                this.bet = packet.bet / 100;
                if(packet.money === 0) {
                        if(packet.bet > 0) {
                            this.all_in = true;
                        } else if(!this.all_in) {
                            this.broke = true;
                        }
                } else {
                    this.broke = false;
                }
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerChipsBet2Pot':
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerChipsPlayer2Bet':
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerChipsPot2Player':
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerSit':
                this.sit_out = false;
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerSitOut':
                this.sit_out = true;
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerAutoFold':
                this.sit_out = true;
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerPotChips':
                if (!this.sit_out && (this.side_pot === undefined) && (this.money === 0)) {
                    this.side_pot = {bet: jpoker.chips.SHORT(jpoker.chips.chips2value(packet.bet)),
                                     index: packet.index};
                }
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerChipsPotReset':
                this.side_pot = undefined;
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerPlayerStats':
                this.stats = packet;
                this.notifyUpdate(packet);
                break;
                }
            }

        });

    //
    // player that is logged in
    //

    jpoker.playerSelf = function(server, packet) {
        $.extend(this, jpoker.playerSelf.defaults, packet);
        this.url = server.url;
        this.init();
    };

    jpoker.playerSelf.defaults = $.extend(jpoker.player.defaults, {
    });

    jpoker.playerSelf.prototype = $.extend({}, jpoker.player.prototype, {
            init: function() {
                jpoker.player.prototype.init.call(this);
                this.state = 'buyin';
            },

            uninit: function() {
                jpoker.player.prototype.uninit.call(this);
            },

            handler: function(server, table, packet) {
                jpoker.player.prototype.handler.call(this, server, table, packet);

                if(jpoker.verbose > 0) {
                    jpoker.message('playerSelf.handler ' + JSON.stringify(packet));
                }

                switch(packet.type) {
                case 'PacketPokerPlayerChips':
                if(packet.money > 0 && this.state == 'buyin') {
                    this.state = 'playing';
                }
                break;

                case 'PacketPokerSit':
                case 'PacketPokerSitOut':
                    if('sit_out_fold_sent' in this) {
                        delete this.sit_out_fold_sent;
                    }
                break;

                case 'PacketPokerBeginRound':
                case 'PacketPokerHighestBetIncrease':
                case 'PacketPokerInGame':
                case 'PacketPokerPlayerHandStrength':
                case 'PacketPokerSelfLostPosition':
                case 'PacketPokerSelfInPosition':
                case 'PacketPokerTimeoutWarning':
                case 'PacketPokerTimeoutNotice':
                case 'PacketPokerTableMove':
                this.notifyUpdate(packet);
                break;

                case 'PacketPokerBlindRequest':
                case 'PacketPokerAnteRequest':
                    $('.jpoker_timeout').hide();

                    serial = packet.serial;
                    if (server.serial != serial) break;
                    game_id = parseInt(packet.game_id);

                    if (packet.state != "late" || !$('#jpoker_wait_for_bb input').attr('checked')) {
                        server.sendPacket({ 
                            'type': 'PacketPokerBlind',
                            'serial': serial,
                            'game_id': game_id,
                            'amount': packet.amount,
                            'dead': packet.dead
                        });

                        server.sendPacket({ 
                          'type': 'PacketPokerAutoBlindAnte',
                          'serial': serial,
                          'game_id': game_id
                        });
                    }
                    else {
                        server.sendPacket({ 
                            'type': 'PacketPokerWaitBigBlind',
                            'serial': serial,
                            'game_id': game_id
                        });
                    }

                    break;

                }
            }

        });
    //
    // Refresh data with the 'handler' function after sending
    // a packet to the 'url' poker server with the 'request' function.
    //
    jpoker.refresh = function(server, request, handler, state, options) {

        var opts = $.extend({}, this.refresh.defaults, options);

        var waiting = false; // is there a refresh being served

        var timer = 0;

        var url = server.url;

        var callHandler = function(server, game_id, packet) {
            var status = handler(server, packet);
            if(status === false) {
                waiting = false;
                server.setState(server.RUNNING, 'refresh ' + state);
            }
            return status;
        };

        var sendRequest = function() {
            var server = jpoker.getServer(url);
            if(server && ( opts.requireSession === false || server.connected() )) {
                if(!waiting) {
                    waiting = true;
                    server.queueRunning(function(server) {
                            server.setState(state, 'refresh');
                            request(server);
                            server.registerHandler(opts.game_id, callHandler, opts);
                        });
                } else if(jpoker.verbose > 0) {
                    jpoker.message('refresh waiting');
                }
                return true;
            } else {
                opts.clearInterval(timer);
                timer = 0; // relevant for the first call (see below)
                return false;
            }
        };

        if(sendRequest() && opts.delay > 0) {
            timer = opts.setInterval(sendRequest, opts.delay);
        }

        return { timer: timer, request: sendRequest };
    };

    jpoker.refresh.defaults = {
        delay: 120000,
        game_id: 0,
        requireSession: false,

        setInterval: function(cb, delay) { return window.setInterval(cb, delay); },
        clearInterval: function(id) { return window.clearInterval(id); }
    };

    //
    // jQuery plugin container (must only contain jQuery plugins)
    //
    jpoker.plugins = {};

    //
    // tableList
    //
    jpoker.plugins.tableList = function(url, options) {

        var tableList = jpoker.plugins.tableList;
        var opts = $.extend({}, tableList.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_table_list\' id=\'' + id + '\'></table>');

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerTableList') {
                            $(element).html(tableList.getHTML(id, packet, opts.link_pattern));
                            if (opts.link_pattern === undefined) {
                                for(var i = 0; i < packet.packets.length; i++) {
                                    (function(){
                                        var subpacket = packet.packets[i];
                                        $('#' + subpacket.id).click(function() {
                                                var server = jpoker.getServer(url);
                                                if(server) {
                                                    server.tableJoin(subpacket.game_id);
                                                }
                                            }).hover(function(){
                                                    $(this).addClass('hover');
                                                },function(){
                                                    $(this).removeClass('hover');
                                                });
                                    })();
                                }
                            }
                            if ($('tbody tr', element).length > 0) {
                                var t = jpoker.plugins.tableList.templates;
                                var options = {container: $('.pager', element),
                                               positionFixed: false,
                                               previous_label: t.previous_label.supplant({previous_label: _("Previous page")}),
                                               next_label: t.next_label.supplant({next_label: _("Next page")})};
                                $('table', element).tablesorter({widgets: ['zebra'], sortList: opts.sortList}).tablesorterPager(options);
                            }
                            tableList.callback.display_done(element);
                        }
                        return true;
                    } else {
                        server.stopRefresh('tableList');
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'tableList' + id);

                server.refreshTables(opts.string, options);
                return this;
            });
    };

    jpoker.plugins.tableList.defaults = $.extend({
            sortList: [[0, 0]],
            string: ''
        }, jpoker.refresh.defaults, jpoker.defaults);

    jpoker.plugins.tableList.getHTML = function(id, packet, link_pattern) {
        var t = this.templates;
        var html = [];
        packet.packets = $.grep(packet.packets, function(packet) {return packet.tourney_serial === undefined || packet.tourney_serial === 0;});
        html.push(t.header.supplant({
                    'seats': _("Seats"),
                        'average_pot': _("Average Pot"),
                        'average_pot_abbrev': _("AvPot"),
                        'hands_per_hour': _("Hands/Hour"),
                        'hands_per_hour_abbrev': _("H"),
                        'percent_flop': _("% Flop"),
                        'percent_flop_abbrev': _("%F"),
                        'players': _("Players"),
                        'players_abbrev': _("Play."),
                        'observers': _("Observers"),
                        'waiting': _("Waiting"),
                        'player_timeout': _("Timeout"),
                        'currency_serial': _("Currency"),
                        'name': _("Name"),
                        'variant': _("Variant"),
                        'betting_structure': _("Betting Structure"),
                        'skin': _("Skin")
                        }));
        for(var i = 0; i < packet.packets.length; i++) {
            var subpacket = packet.packets[i];
            if(!('game_id' in subpacket)) {
                subpacket.game_id = subpacket.id;
                subpacket.id = subpacket.game_id + id;
                subpacket.average_pot /= 100;
            }
            if (link_pattern) {
                var link = t.link.supplant({link: link_pattern.supplant({game_id: subpacket.game_id}), name: subpacket.name});
                subpacket.name = link;
            }
            if (subpacket.players == subpacket.seats) {
                subpacket.status_class =  'jpoker_table_list_table_full';
            } else if (subpacket.players === 0) {
                subpacket.status_class = 'jpoker_table_list_table_empty';
            } else {
                subpacket.status_class = '';
            }
            html.push(t.rows.supplant(subpacket));
        }
        html.push(t.footer);
        html.push(t.pager);
        return html.join('\n');
    };

    jpoker.plugins.tableList.templates = {
        header : '<table><thead><tr><th>{name}</th><th>{players}</th><th>{seats}</th><th>{betting_structure}</th><th>{average_pot}</th><th>{hands_per_hour}</th><th>{percent_flop}</th></tr></thead><tbody>',
        rows : '<tr id=\'{id}\' title=\'' + _("Click to join the table") + '\' class=\'{status_class}\'><td>{name}</td><td>{players}</td><td>{seats}</td><td>{betting_structure}</td><td>{average_pot}</td><td>{hands_per_hour}</td><td>{percent_flop}</td></tr>',
        footer : '</tbody></table>',
        link: '<a href=\'{link}\'>{name}</a>',
        pager: '<div class=\'pager\'><input class=\'pagesize\' value=\'10\'></input><ul class=\'pagelinks\'></ul></div>',
        next_label: '{next_label} >>>',
        previous_label: '<<< {previous_label}'
    };

    jpoker.plugins.tableList.callback = {
        display_done: function(element) {
        }
    };
    //
    // regularTourneyList
    //
    jpoker.plugins.regularTourneyList = function(url, options) {

        var regularTourneyList = jpoker.plugins.regularTourneyList;
        regularTourneyList.defaults.templates = regularTourneyList.templates;
        regularTourneyList.defaults.callback = regularTourneyList.callback;
        var opts = $.extend({}, regularTourneyList.defaults, options);
        return jpoker.plugins.tourneyList.call(this, url, opts);
    };

    jpoker.plugins.regularTourneyList.templates = {
        header : '<table><thead><tr><th>{description_short}</th><th>{registered}</th><th>{players_quota}</th><th>{buy_in}</th><th>{start_time}</th><th>{state}</th></tr></thead><tbody>',
        rows : '<tr id=\'{id}\' title=\'' + _("Click to show tourney details") + '\' class=\'jpoker_tourney_state_{state}\'><td>{description_short}</td><td>{registered}</td><td>{players_quota}</td><td>{buy_in}</td><td>{start_time}</td><td>{state}</td></tr>',
        footer : '</tbody></table>',
        link: '<a href=\'{link}\'>{name}</a>',
        pager: '<div class=\'pager\'><input class=\'pagesize\' value=\'10\'></input><ul class=\'pagelinks\'></ul></div>',
        next_label: '{next_label} >>>',
        previous_label: '<<< {previous_label}',
        date: ''
    };

    jpoker.plugins.regularTourneyList.callback = {
        display_done: function(element) {
        }
    };

    jpoker.plugins.regularTourneyList.defaults = $.extend({
            sortList: [[4, 0]],
            string: '\tregular', // PacketTourneySelect : any currency\nregular
            css_tag: 'regular_'
        }, jpoker.refresh.defaults, jpoker.defaults);

    //
    // sitngoTourneyList
    //
    jpoker.plugins.sitngoTourneyList = function(url, options) {

        var sitngoTourneyList = jpoker.plugins.sitngoTourneyList;
        sitngoTourneyList.defaults.templates = sitngoTourneyList.templates;
        sitngoTourneyList.defaults.callback = sitngoTourneyList.callback;
        var opts = $.extend({}, sitngoTourneyList.defaults, options);
        return jpoker.plugins.tourneyList.call(this, url, opts);
    };

    jpoker.plugins.sitngoTourneyList.templates = {
        header : '<table><thead><tr><th>{description_short}</th><th>{registered}</th><th>{players_quota}</th><th>{buy_in}</th><th>{state}</th></tr></thead><tbody>',
        rows : '<tr id=\'{id}\' title=\'' + _("Click to show tourney details") + '\' class=\'jpoker_tourney_state_{state}\'><td>{description_short}</td><td>{registered}</td><td>{players_quota}</td><td>{buy_in}</td><td>{state}</td></tr>',
        footer : '</tbody></table>',
        link: '<a href=\'{link}\'>{name}</a>',
        pager: '<div class=\'pager\'><input class=\'pagesize\' value=\'10\'></input><ul class=\'pagelinks\'></ul></div>',
        next_label: '{next_label} >>>',
        previous_label: '<<< {previous_label}'
    };

    jpoker.plugins.sitngoTourneyList.callback = {
        display_done: function(element) {
        }
    };

    jpoker.plugins.sitngoTourneyList.defaults = $.extend({
            sortList: [[3, 0]],
            string: '\tsit_n_go', // PacketTourneySelect : any currency\nsit&go,
            css_tag: 'sitngo_'
        }, jpoker.refresh.defaults, jpoker.defaults);

    //
    // tourneyList
    //
    jpoker.plugins.tourneyList = function(url, options) {

        var tourneyList = jpoker.plugins.tourneyList;
        var opts = $.extend({}, tourneyList.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_' + opts.css_tag + 'tourney_list\' id=\'' + id + '\'></table>');

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerTourneyList') {
                            $(element).html(tourneyList.getHTML(id, packet, opts));
                            if (opts.link_pattern === undefined) {
                                for(var i = 0; i < packet.packets.length; i++) {
                                    (function(){
                                        var subpacket = packet.packets[i];
                                        if (subpacket.state != 'announced' && subpacket.state != 'canceled') {
                                            $('#' + subpacket.id).click(function() {
                                                    var server = jpoker.getServer(url);
                                                    if(server) {
                                                        server.tourneyRowClick(server, subpacket);
                                                    }});
                                        }
                                        $('#' + subpacket.id).hover(function(){
                                                $(this).addClass('hover');
                                            },function(){
                                                $(this).removeClass('hover');
                                            });
                                    })();
                                }
                            }
                             if ($('tbody tr', element).length > 0) {
                                var t = opts.templates;
                                var options = {container: $('.pager', element),
                                               positionFixed: false,
                                               previous_label: t.previous_label.supplant({previous_label: _("Previous page")}),
                                               next_label: t.next_label.supplant({next_label: _("Next page")})};
                                $('table', element).tablesorter({widgets: ['zebra'], sortList: opts.sortList}).tablesorterPager(options);
                            }
                            opts.callback.display_done(element);
                        }
                        return true;
                    } else {
                        server.stopRefresh('tourneyList');
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'tourneyList' + id);

                server.refreshTourneys(opts.string, opts);
                return this;
            });
    };

    jpoker.plugins.tourneyList.getHTML = function(id, packet, options) {
        var link_pattern = options.link_pattern;
        var t = options.templates;
        var html = [];
        html.push(t.header.supplant({
                    'players_quota': _("Players Quota"),
                        'players_abbrev': _("Play."),
                        'breaks_first': _("Break First"),
                        'name': _("Name"),
                        'description_short': _("Description"),
                        'start_time': _("Start Time"),
                        'breaks_interval': _("Breaks Interval"),
                        'breaks_interval_abbrev': _("Brk."),
                        'variant': _("Variant"),
                        'currency_serial': _("Currency"),
                        'state': _("State"),
                        'buy_in': _("Buy In"),
                        'breaks_duration': _("Breaks Duration"),
                        'sit_n_go': _("Sit'n'Go"),
                        'registered': _("Registered"),
                        'player_timeout': _("Player Timeout"),
                        'player_timeout_abbrev': _("Time")
                        }));
        var packets = packet.packets;
        for(var i = 0; i < packets.length; i++) {
            var subpacket = packets[i];
            if(!('game_id' in subpacket)) {
                subpacket.game_id = subpacket.serial;
                subpacket.id = subpacket.game_id + id;
                subpacket.buy_in /= 100;
            }
            if (t.date && (t.date !== '')) {
                subpacket.start_time = $.strftime(t.date, new Date(subpacket.start_time*1000));
            } else {
                subpacket.start_time = new Date(subpacket.start_time*1000).toLocaleString();
            }
            if (link_pattern && subpacket.state != 'announced' && subpacket.state != 'canceled') {
                subpacket.tourney_serial = subpacket.serial; // for backward compatibility only
                var link = t.link.supplant({link: link_pattern.supplant(subpacket), name: subpacket.description_short});
                subpacket.description_short = link;
            }
            html.push(t.rows.supplant(subpacket));
        }
        html.push(t.footer);
        html.push(t.pager);
        return html.join('\n');
    };

    jpoker.plugins.tourneyList.defaults = $.extend({
            sortList: [[0, 0]],
            string: '',
            css_tag: '',
            templates: {
                header : '<table><thead><tr><th>{description_short}</th><th>{registered}</th><th>{players_quota}</th><th>{buy_in}</th><th>{start_time}</th><th>{state}</th></tr></thead><tbody>',
                rows : '<tr id=\'{id}\' title=\'' + _("Click to show tourney details") + '\' class=\'jpoker_tourney_state_{state}\'><td>{description_short}</td><td>{registered}</td><td>{players_quota}</td><td>{buy_in}</td><td>{start_time}</td><td>{state}</td></tr>',
                footer : '</tbody></table>',
                link: '<a href=\'{link}\'>{name}</a>',
                pager: '<div class=\'pager\'><input class=\'pagesize\' value=\'10\'></input><ul class=\'pagelinks\'></ul></div>',
                next_label: '{next_label} >>>',
                previous_label: '<<< {previous_label}',
                date: ''
            },
            callback: {
                display_done: function(element) {
                }
            }
        }, jpoker.refresh.defaults, jpoker.defaults);

    //
    // tourneyDetails
    //
    jpoker.plugins.tourneyDetails = function(url, game_id, name, options, server_options) {

        game_id = parseInt(game_id, 10);

        var tourneyDetails = jpoker.plugins.tourneyDetails;
        var opts = $.extend({}, tourneyDetails.defaults, options);

        server_options.url = url;
        var server = jpoker.url2server(server_options);

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_tourney_details\' id=\'' + id + '\'></div>');

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerTourneyManager') {
                            var logged = server.loggedIn();
                            var registered = packet.user2properties['X'+server.serial.toString()] !== undefined;
                            $.each(packet.user2properties, function(serial, player) {
                                    if (player.money != -1) {
                                        player.money /= 100;
                                    }
                                });
                            if (packet.tourney.rank2prize) {
                                $.each(packet.tourney.rank2prize, function(i, prize) {
                                        packet.tourney.rank2prize[i] /= 100;
                                    });
                            }
                            $(element).html(tourneyDetails.getHTML(id, packet, logged, registered, opts.link_pattern));

                            if ($('.jpoker_tourney_details_players table tbody tr').length > 0) {
                                $('.jpoker_tourney_details_players table').tablesorter({widgets: ['zebra'], sortList: tourneyDetails.templates.players[packet.tourney.state].sortList});
                            }

                            /**
                             * Bugs: on new packet the whole table with players resets. When clicking on open table link - list of players expands.
                             */
                            /*$('.jpoker_tourney_details_table', element).click(function() {
                                var table_details = $('.jpoker_tourney_details_table_details', element);
                                table_details.html(tourneyDetails.getHTMLTableDetails(id, packet, $(this).attr('id')));
                                tourneyDetails.callback.table_players_display_done(table_details);
                            }).hover(function(){
                                $(this).addClass('hover');
                            },function(){
                                $(this).removeClass('hover');
                            });*/

                            if (opts.link_pattern === undefined) {
                                $('.jpoker_tourney_details_tables_goto_table', element).click(function() {
                                        server.tableJoin(parseInt($(this).parent().parent().attr('id').substr(1), 10));
                             
                                });
                            }


                            if(logged) {
                                var input = $('.jpoker_tourney_details_register input', element);
                                if (registered) {
                                    input.click(function() {
                                            server.tourneyUnregister(game_id);
                                        });
                                } else {
                                    input.click(function() {
                                            server.tourneyRegister(game_id);
                                        });
                                }
                            }
                            tourneyDetails.callback.display_done(element);
                        }
                        return true;
                    } else {
                        server.stopRefresh('tourneyDetails');
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'tourneyDetails' + id);
                server.refreshTourneyDetails(game_id, opts);
                return this;
            });
    };

    jpoker.plugins.tourneyDetails.defaults = $.extend(jpoker.defaults,
                                                      jpoker.refresh.defaults,
                                                      {delay: 5000});

    jpoker.plugins.tourneyDetails.getHTML = function(id, packet, logged, registered, link_pattern) {
        var t = this.templates;
        var html_map = {};
        var html = [];
        var i = 0;

        html_map.tname = t.tname.supplant(packet.tourney);

        var player_state_template = t.players[packet.tourney.state];
        if (player_state_template) {
            html = [];
            html.push(t.players.header);
            html.push(player_state_template.header.supplant({
                        'caption': _("Players"),
                        'name': _("Name"),
                        'money': _("Money"),
                        'rank' : _("Rank")
                        }));
            i = 0;
            for(var serial in packet.user2properties) {
                var player = packet.user2properties[serial];
                if (player.rank == -1) {
                    player.rank = '';
                }
                if (player.money == -1) {
                    player.money = '';
                }
                html.push(player_state_template.rows.supplant(player).replace(/{oddEven}/g, i%2 ? 'odd' : 'even'));
                i++;
            }
            html.push(player_state_template.footer);
            html.push(t.players.footer);
            html_map.players = html.join('\n');
        } else {
            html_map.players = '';
        }

        if (t.date && (t.date !== '')) {
            packet.tourney.start_time = $.strftime(t.date, new Date(packet.tourney.start_time*1000));
        } else {
            packet.tourney.start_time = new Date(packet.tourney.start_time*1000).toLocaleString();
        }
        packet.tourney.buy_in = packet.tourney.buy_in/100;
        var tourney_type = 'regular';
        if (packet.tourney.sit_n_go == 'y') {
            tourney_type = 'sitngo';
        }
        html_map.info = t.info[tourney_type].supplant({
                'registered_label' : _("players registered."),
                    'players_quota_label' : _("players max."),
                    'start_time_label' : _("Start time:"),
                    'buy_in_label' : _("Buy in:")
                       });

        html_map.register = '';
        if (packet.tourney.state == 'registering') {
            if (logged) {
                if (registered) {
                    html_map.register = t.register.supplant({'register': _("Unregister")});
                } else {
                    html_map.register = t.register.supplant({'register': _("Register")});
                }
            }
        }

        if (packet.tourney.state != 'canceled' && packet.tourney.state != 'announced' ) {
            html = [];
            html.push(t.prizes.header.supplant({
                        'caption': _("Prizes"),
                        'rank': _("Rank"),
                        'prize': _("Prize")
                    }));
            if (packet.tourney.rank2prize) {
                $.each(packet.tourney.rank2prize, function(rank, prize) {
                        html.push(t.prizes.rows.supplant({
                                    'rank': rank+1,
                                        'prize': prize,
                                        'oddEven': rank%2 ? 'odd' : 'even'
                                        }));
                    });
            }
            html.push(t.prizes.footer);
            html_map.prizes = html.join('\n');
        } else {
            html_map.prizes = '';
        }
        if (packet.tourney.state == "running" || packet.tourney.state == 'break' || packet.tourney.state == 'breakwait') {
            html = [];
            html.push(t.tables.header.supplant({
                        'caption': _("Tables"),
                        'table': _("Table"),
                        'players': _("Players"),
                        'max_money': _("Max money"),
                        'min_money': _("Min money"),
                        'goto_table': _("Go to table")
                    }));
            var table_index = 0;
            $.each(packet.table2serials, function(table, players) {
                    if (table != '-1') {
                        var row = {
                            id: table,
                            table: table.substr(1),
                            players: players.length,
                            min_money: '',
                            max_money: ''};
                        var moneys = $.map(players, function(player) {
                                return packet.user2properties['X'+player.toString()].money;
                            }).sort();
                        if (moneys.length >= 2) {
                            row.min_money = moneys[0];
                            row.max_money = moneys[moneys.length - 1];
                        }
                        if (link_pattern === undefined) {
                            row.goto_table = t.tables.goto_table_button.supplant({'goto_table_label': _("Go to table")});
                        } else {
                            row.goto_table = t.tables.goto_table_link.supplant({
                              'goto_table_label': _("Go to table"), 
                              'link': link_pattern.supplant({game_id: table.substr(1)}), 
                              'game_id': table.substr(1)
                            });
                        }
                        row.oddEven = table_index&1 ? 'odd' : 'even';
                        html.push(t.tables.rows.supplant(row));
                        table_index += 1;
                    }
                });
            html.push(t.tables.footer);
            html_map.tables = html.join('\n');
        } else {
            html_map.tables = '';
        }

        html_map.table_details = t.table_details;
        return t.layout.supplant(html_map).supplant(packet.tourney);
    };

    jpoker.plugins.tourneyDetails.getHTMLTableDetails = function(id, packet, table) {
        var t = this.templates;
        var html = [];
        html.push(t.table_players.header.supplant({
                        caption: _("Table"),
                        player: _("Player"),
                        money: _("Money")
                        }));
        var players = packet.table2serials[table];
        $.each(players, function(i, serial) {
                var player = packet.user2properties['X'+serial];
                html.push(t.table_players.rows.supplant(player).replace(/{oddEven}/g, i%2 ? 'odd' : 'even'));
            });
        html.push(t.table_players.footer);
        return html.join('\n');
    };

    jpoker.plugins.tourneyDetails.templates = {
        layout: '{tname}{players}{prizes}{info}{register}{tables}{table_details}', // layout of the templates defined below
        tname: '<div class=\'jpoker_tourney_name\'>{description_short}</div>',
        info: {
            regular: '<div class=\'jpoker_tourney_details_info jpoker_tourney_details_{state}\'>'
                    +'<div class=\'jpoker_tourney_details_info_description\'>{description_long}</div>'
                    +'<div class=\'jpoker_tourney_details_info_registered\'>{registered} {registered_label}</div>'
                    +'<div class=\'jpoker_tourney_details_info_players_quota\'>{players_quota} {players_quota_label}</div>'
                    +'<div class=\'jpoker_tourney_details_info_start_time\'>{start_time_label} {start_time}</div>'
                    +'<div class=\'jpoker_tourney_details_info_buy_in\'>{buy_in_label} {buy_in}</div></div>',

            sitngo:  '<div class=\'jpoker_tourney_details_info jpoker_tourney_details_{state}\'>'
                    +'<div class=\'jpoker_tourney_details_info_description\'>{description_long}</div>'
                    +'<div class=\'jpoker_tourney_details_info_registered\'>{registered} {registered_label}</div>'
                    +'<div class=\'jpoker_tourney_details_info_players_quota\'>{players_quota} {players_quota_label}</div>'
                    +'<div class=\'jpoker_tourney_details_info_buy_in\'>{buy_in_label} {buy_in}</div></div>'
        },
        players : {
            registering : {
                header : '<table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th>{caption}</th></tr></thead><tbody>',
                rows : '<tr class=\'{oddEven}\'><td>{name}</td></tr>',
                footer : '</tbody></table>',
                sortList : [[0,0]]
            },
            running : {
                header : '<table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th colspan=\'3\'>{caption}</th></tr><tr><th>{name}</th><th>{money}</th><th>{rank}</th></tr></thead><tbody>',
                rows : '<tr class=\'{oddEven}\'><td>{name}</td><td>{money}</td><td>{rank}</td></tr>',
                footer : '</tbody></table>',
                sortList : [[1,1]]
            },
            'break' : {
                header : '<table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th colspan=\'3\'>{caption}</th></tr><tr><th>{name}</th><th>{money}</th><th>{rank}</th></tr></thead><tbody>',
                rows : '<tr class=\'{oddEven}\'><td>{name}</td><td>{money}</td><td>{rank}</td></tr>',
                footer : '</tbody></table>',
                sortList : [[1,1]]
            },
            breakwait : {
                header : '<table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th colspan=\'3\'>{caption}</th></tr><tr><th>{name}</th><th>{money}</th><th>{rank}</th></tr></thead><tbody>',
                rows : '<tr class=\'{oddEven}\'><td>{name}</td><td>{money}</td><td>{rank}</td></tr>',
                footer : '</tbody></table>',
                sortList : [[1,1]]
            },
            complete : {
                header : '<table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th colspan=\'2\'>{caption}</th></tr><tr><th>{name}</th><th>{rank}</th></tr></thead><tbody>',
                rows : '<tr class=\'{oddEven}\'><td>{name}</td><td>{rank}</td></tr>',
                footer : '</tbody></table>',
                sortList : [[1,0]]
            },
            header: '<div class=\'jpoker_tourney_details_players\'>',
            footer: '</div>'
        },
        tables : {
            header : '<div class=\'jpoker_tourney_details_tables\'><table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th colspan=\'5\'>{caption}</th></tr><tr><th>{table}</th><th>{players}</th><th>{max_money}</th><th>{min_money}</th><th>{goto_table}</th></tr></thead><tbody>',
            rows : '<tr id=\'{id}\' class=\'jpoker_tourney_details_table {oddEven}\' title=\'' + _("Click to show table details") + '\'><td>{table}</td><td>{players}</td><td>{max_money}</td><td>{min_money}</td><td>{goto_table}</td></tr>',
            footer : '</tbody></table></div>',
            goto_table_button: '<input class=\'jpoker_tourney_details_tables_goto_table\' type=\'submit\' value=\'{goto_table_label}\'></input>',
            goto_table_link: '<a class=\'jpoker_tourney_details_tables_goto_table\' onclick="javascript:popitup(\'{link}\', {game_id});return false;" target=\'tourney_{game_id}\' href=\'{link}\'>{goto_table_label}</a>'
        },
        table_players : {
            header : '<div class=\'jpoker_tourney_details_table_players\'><table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th colspan=\'2\'>{caption}</th></tr><tr><th>{player}</th><th>{money}</th></tr></thead><tbody>',
            rows : '<tr class=\'{oddEven}\'><td>{name}</td><td>{money}</td></tr>',
            footer : '</tbody></table></div>'
        },
        prizes : {
            header : '<div class=\'jpoker_tourney_details_prizes\'><table cellspacing=\'0\'><thead><tr class=\'jpoker_thead_caption\'><th colspan=\'2\'>{caption}</th></tr><tr><th>{rank}</th><th>{prize}</th></tr></thead><tbody>',
            rows : '<tr class=\'{oddEven}\'><td>{rank}</td><td>{prize}</td></tr>',
            footer : '</tbody></table></div>'
        },
        register : '<div class=\'jpoker_tourney_details_register\'><input type=\'submit\' value=\'{register}\'></div>',
        table_details : '<div class=\'jpoker_tourney_details_table_details\'>',
        date : ''
    };

    jpoker.plugins.tourneyDetails.callback = {
        display_done: function(element) {
        },
        table_players_display_done: function(element) {
        }
    };

    //
    // tourneyPlaceholder
    //
    jpoker.plugins.tourneyPlaceholder = function(url, game_id, options) {

        game_id = parseInt(game_id, 10);

        var tourneyPlaceholder = jpoker.plugins.tourneyPlaceholder;
        var opts = $.extend({}, tourneyPlaceholder.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_tourney_placeholder\' id=\'' + id + '\'></div>');

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerTourneyManager') {
                            $(element).html(tourneyPlaceholder.getHTML(id, packet));
                            tourneyPlaceholder.callback.display_done(element);
                        }
                        return true;
                    } else {
                        server.stopRefresh('tourneyDetails');
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'tourneyPlaceholder' + id);
                server.refreshTourneyDetails(game_id, opts);
                return this;
            });
    };

    jpoker.plugins.tourneyPlaceholder.defaults = $.extend({
        }, jpoker.refresh.defaults, jpoker.defaults);

    jpoker.plugins.tourneyPlaceholder.getHTML = function(id, packet) {
        var t = this.templates;
        var html = [];
        html.push(t.table);
        var date = new Date(packet.tourney.start_time*1000);
        var date_string;
        if (t.date && (t.date !== '')) {
            date_string = $.strftime(t.date, date);
        } else {
            date_string = date.toLocaleString();
        }
        html.push(t.starttime.supplant({tourney_starttime:
                                        _("Tournament is starting at: ")+date_string}));
        return html.join('\n');
    };

    jpoker.plugins.tourneyPlaceholder.templates = {
        table: '<div class=\'jpoker_tourney_placeholder_table\'></div>',
        starttime: '<div class=\'jpoker_tourney_placeholder_starttime\'>{tourney_starttime}</div>',
        date: ''
    };

    jpoker.plugins.tourneyPlaceholder.callback = {
        display_done: function(element) {
        }
    };

    //
    // serverStatus
    //
    jpoker.plugins.serverStatus = function(url, options) {

        var serverStatus = jpoker.plugins.serverStatus;
        var opts = $.extend({}, serverStatus.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_server_status\' id=\'' + id + '\'></div>');

                var updated = function(server) {
                    var element = document.getElementById(id);
                    if(element) {
                        $(element).html(serverStatus.getHTML(server));
                        serverStatus.callback.display_done(element);
                        return true;
                    } else {
                        return false;
                    }
                };

                if(updated(server)) {
                    server.registerUpdate(updated, null, 'serverStatus ' + id);
                }

                return this;
            });
    };

    jpoker.plugins.serverStatus.defaults = $.extend({
        }, jpoker.defaults);

    jpoker.plugins.serverStatus.getHTML = function(server) {
        var t = this.templates;
        var html = [];

        if(server.connected()) {
            html.push(t.connected);
        } else {
            html.push(t.disconnected.supplant({ 'label': _("disconnected") }));
        }
        if(server.playersCount) {
            html.push(t.players.supplant({ 'count': server.playersCount, 'players': _("players") }));
        }
        if(server.tablesCount) {
            html.push(t.tables.supplant({ 'count': server.tablesCount, 'tables': _("tables") }));
        }
        if(server.playersTourneysCount) {
            html.push(t.players_tourneys.supplant({ 'count': server.playersTourneysCount, 'players_tourneys': _("tournaments players") }));
        }
        if(server.tourneysCount) {
            html.push(t.tourneys.supplant({ 'count': server.tourneysCount, 'tourneys': _("tourneys") }));
        }
        return html.join(' ');
    };

    jpoker.plugins.serverStatus.templates = {
        disconnected: '<div class=\'jpoker_server_status_disconnected\'> {label} </div>',
        connected: '<div class=\'jpoker_server_status_connected\'></div>',
        players: '<div class=\'jpoker_server_status_players\'> <span class=\'jpoker_server_status_players_count\'>{count}</span> <span class=\'jpoker_server_status_players_label\'>{players}</span> </div>',
        tables: '<div class=\'jpoker_server_status_tables\'> <span class=\'jpoker_server_status_tables_count\'>{count}</span> <span class=\'jpoker_server_status_tables_label\'>{tables}</span> </div>',

        players_tourneys: '<div class=\'jpoker_server_status_players_tourneys\'> <span class=\'jpoker_server_status_players_tourneys_count\'>{count}</span> <span class=\'jpoker_server_status_players_tourneys_label\'>{players_tourneys}</span> </div>',

        tourneys: '<div class=\'jpoker_server_status_tourneys\'> <span class=\'jpoker_server_status_tourneys_count\'>{count}</span> <span class=\'jpoker_server_status_tourneys_label\'>{tourneys}</span> </div>'
    };

    jpoker.plugins.serverStatus.callback = {
        display_done: function(element) {
        }
    };

    //
    // login
    //
    jpoker.plugins.login = function(url, options) {

        var login = jpoker.plugins.login;
        var opts = $.extend(true, {}, jpoker.plugins.login.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_login\' id=\'' + id + '\'></div>');

                var updated = function(server) {
                    var element = document.getElementById(id);
                    if(element) {
                        var e = $(element);
                        var loginDisplayed = $('.jpoker_login_name', element).length == 1;
        
                        if (server.loggedIn() === false && loginDisplayed) {
                            return true;
                        }

                        e.html(login.getHTML(server, opts));
                        if(server.loggedIn()) {
                            e.click(function() {
                                    var server = jpoker.getServer(url);
                                    if(server && server.loggedIn()) {
                                        server.logout();
                                    }
                                });
                        } else {
                            var action = function() {
                                var name = $('.jpoker_login_name', e).attr('value');
                                var password = $('.jpoker_login_password', e).attr('value');
                                if(!name) {
                                    jpoker.dialog(_("the user name must not be empty"));
                                } else if(!password) {
                                    jpoker.dialog(_("the password must not be empty"));
                                } else {
                                    var server = jpoker.getServer(url);
                                    if(server) {
                                        server.login(name, password);
                                        $('#' + id).html('<div class=\'jpoker_login_progress\'>' + _("login in progress") + '</a>');
                                    }
                                }
                            };
                            $('.jpoker_login_submit', e).click(action);
                            $('.jpoker_login_signup', e).click(function() {
                                    $this.jpoker('signup', url);
                                });

                            e.unbind('keypress'); // prevent accumulation of handlers
                            e.keypress(function(event) {
                                    if(event.which == 13) {
                                        action.call(this);
                                    }
                                });
                        }
                        login.callback.display_done(element);
                        return true;
                    } else {
                        return false;
                    }
                };

                if(updated(server)) {
                    server.registerUpdate(updated, null, 'login ' + id);
                }

                return this;
            });
    };

    jpoker.plugins.login.templates = {
        login: '<table>\n<tbody><tr>\n<td class=\'jpoker_login_name_label\'><b>{login}</b></td>\n<td><input type=\'text\' class=\'jpoker_login_name\' size=\'10\'/></td>\n<td><input type=\'submit\' class=\'jpoker_login_submit\' value=\'{go}\' /></td>\n</tr>\n<tr>\n<td class=\'jpoker_login_name_label\'><b>{password}</b></td>\n<td><input type=\'password\' class=\'jpoker_login_password\' size=\'10\'/></td>\n<td><input type=\'submit\' class=\'jpoker_login_signup\' value=\'{signup}\' /></td>\n</tr>\n</tbody></table>',
        logout: '<div class=\'jpoker_logout\'>{logout}<div>'
    };

    jpoker.plugins.login.callback = {
        display_done: function(element) {
        }
    };

    jpoker.plugins.login.defaults = $.extend(
        {
            templates: jpoker.plugins.login.templates,
            callback: jpoker.plugins.login.callback
        }, jpoker.defaults);

    jpoker.plugins.login.getHTML = function(server, options) {
        var t = options.templates;
        var html = [];
        if(server.loggedIn()) {
            html.push(t.logout.supplant({'logout': '{logname} <a href=\'javascript:;\'>' + _("logout") + '</a>'}).supplant({ 'logname': server.userInfo.name }));
        } else {
            html.push(t.login.supplant({ 'login': _("user: "),
                                         'password': _("password: "),
                                         'signup': _("Sign Up"),
                                         'go': _("Login")
                    }));
        }
        return html.join('\n');
    };

    //
    // featured table
    //
    jpoker.plugins.featuredTable = function(url, options) {

        var opts = $.extend({}, jpoker.plugins.featuredTable.defaults, options);
        var server = jpoker.url2server({ url: url });

        server.registerUpdate(function(server, what, packet) {
                if (packet && packet.type == 'PacketPokerTableList') {
                    if (packet.packets.length === 0) {
                        var updated = function(server, what, packet) {
                            if(packet && packet.type == 'PacketPokerTableList') {
                                var found = null;
                                for(var i = packet.packets.length - 1; i >= 0 ; i--) {
                                    var subpacket = packet.packets[i];
                                    if(opts.compare(found, subpacket) >= 0) {
                                        found = subpacket;
                                    }
                                }
                                if(found) {
                                    found.game_id = found.id;
                                    server.setTimeout(function() { server.tableJoin(found.game_id); }, 1);
                                }
                                return false;
                            } else {
                                return true;
                            }
                        };
                        server.registerUpdate(updated, null, 'featuredTable ' + url);
                        server.selectTables(opts.string);
                    }
                    return false;
                } else {
                    return true;
                }
            }, null, 'featuredTable ' + url);
        server.selectTables('my');
        return this;
    };

    jpoker.plugins.featuredTable.defaults = {
        string: '',
        compare: function(a, b) { return a && b && b.players - a.players; }
    };

    //
    // table
    //
    jpoker.plugins.table = function(url, game_id, name, options) {

        var opts = $.extend({}, jpoker.plugins.table.defaults, options);
        var server = jpoker.url2server({ url: url });

        game_id = parseInt(game_id, 10);

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                var placeholder = jpoker.plugins.table.templates.placeholder.supplant({ 'name': name });
                $this.append('<span class=\'jpoker_widget jpoker_table\' id=\'' + id + '\'><div class=\'jpoker_connecting\'><div class=\'jpoker_connecting_message\'>' + placeholder + '</div><div class=\'jpoker_connecting_image\'></div></div></span>');

                if(game_id in server.tables) {
                    var element = document.getElementById(id);
                    jpoker.plugins.table.create($(element), id, server, game_id);
                    jpoker.plugins.table.callback.display_done(element);
                }

                return this;
            });
    };

    jpoker.plugins.table.defaults = $.extend({
        }, jpoker.defaults);

    jpoker.plugins.table.create = function(element, id, server, game_id) {
        var game_fixed, game_window;
        if(jpoker.verbose > 0) {
            jpoker.message('plugins.table.create ' + id + ' game: ' + game_id);
        }
        if(game_id in server.tables) {
            var url = server.url;
            var table = server.tables[game_id];
            element.html(this.templates.room.supplant({ id: id }));
            game_fixed = $('#game_fixed' + id);
            game_window = $('#game_window' + id);
            jpoker.plugins.table.seats(id, server, table);
            jpoker.plugins.table.dealer(id, table, table.dealer);
            jpoker.plugins.cards.update(table.board, 'board', id);
            $('#pots' + id).addClass('jpoker_pots jpoker_pots0').html(jpoker.plugins.table.templates.pots.supplant({
                        chips: jpoker.plugins.chips.template
                            }));
            for(var pot = 0; pot < table.pots.length; pot++) {
                jpoker.plugins.chips.update(table.pots[pot], '#pots' + id + ' .jpoker_pot' + pot );
            }

            for(var winner = 0; winner < 2; winner++) {
                $('#winner' + winner + id).hide();
            }
            $('#rebuy' + id).hide();
            $('#sitout' + id).hide();
            $('#sitin' + id).hide();
            $('#options' + id).hide();
            $('#muck_accept' + id).hide();
            $('#muck_deny' + id).hide();

            if (server.serial > 0) {
              $('#quit' + id).click(function() {
                  if (! confirm('Are you sure you want to leave this table?')) {
                    return;
                  }

                  var server = jpoker.getServer(url);
                  var table = jpoker.getTable(url, game_id);
                  if(server) {
                      server.tableQuit(game_id);

                      server.queueRunning(function(server) {
                        table.handler(
                          server, game_id, 
                          { 
                            type: 'PacketPokerTableDestroy',
                            game_id: game_id 
                          }
                        );
                      });
                  }
              }).hover(function(){
                  $(this).addClass('hover');
              },function(){
                  $(this).removeClass('hover');
              }).html('<div class=\'jpoker_quit\'><a href=\'javascript://\'>' + _("Exit") + '</a></div>');
            }

            game_fixed.append(this.templates.chat.supplant({
                        chat_history_player_label: _("chat"),
                        chat_history_dealer_label: _("dealer")
            }));

            game_fixed.append(this.templates.wait_for_bb.supplant({
                        wait_for_bb: _("Wait for BB")
            }));

            $('#jpoker_wait_for_bb').hide();

            $('.jpoker_chat_input', game_window).hide();
            jpoker.plugins.playerSelf.hide(id);
            for(var serial in table.serial2player) {
                jpoker.plugins.player.create(table, table.serial2player[serial], id);
            }
            jpoker.plugins.table.position(id, table, table.serial_in_position);
            jpoker.plugins.table.timeout(id, table, table.serial_in_position, 0.0);
            //
            // sound
            //
            jpoker.plugins.table.soundCreate('sound_control' + id, server);

            $('#table_info' + id).html(this.templates.table_info.supplant($.extend(table, {
                            name_label: _("Name: "),
                            variant_label: _("Variant: "),
                            betting_structure_label: _("Structure: "),
                            seats_label: _("Seats: "),
                            percent_flop_label: _("% Flop"),
                            player_timeout_label: _("Player timeout: "),
                            muck_timeout_label: _("Muck timeout: ")
                        })));

            $('.jpoker_table', element).append(jpoker.copyright_text);
            $('#powered_by' + id).addClass('jpoker_powered_by').html(this.templates.powered_by);


            for (var i = 0; i < 10; i+=1) {
                var sit_seat = $('#sit_seat' + i + id).addClass('jpoker_sit_seat');
                $('<div class=\'jpoker_sit_seat_progress\'>').appendTo(sit_seat);
            }

            // it does not matter to register twice as long as the same key is used
            // because the second registration will override the first
            table.registerUpdate(this.update, id, 'table update' + id);
            table.registerDestroy(this.destroy, id, 'table destroy' + id);
            table.registerReinit(this.reinit, id, 'table reinit' + id);
        }
    };

     jpoker.plugins.table.soundCreate = function(id, server) {
         if($('#jpokerSound').size() === 0) {
             $('body').append('<div id=\'jpokerSound\' />');
         }
         if($('#jpokerSoundAction').size() === 0) {
             $('body').append('<div id=\'jpokerSoundAction\' />');
         }
         if($('#jpokerSoundTable').size() === 0) {
             $('body').append('<div id=\'jpokerSoundTable\' />');
         }
         var element = $('#' + id);
         element.addClass('jpoker_sound_control');
         var url = server.url;
         function update_css(element, server) {
             if(server.preferences.sound) {
                 element.html(jpoker.plugins.table.templates.sound.supplant({ sound: _("<span>Sound On</span>") }));
                 element.removeClass('jpoker_sound_off');
             } else {
                 element.html(jpoker.plugins.table.templates.sound.supplant({ sound: _("<span>Sound Off</span>") }));
                 element.addClass('jpoker_sound_off');
             }
         }
         update_css(element, server);
         element.click(
             function() {
                 var server = jpoker.getServer(url);
                 server.preferences.sound = !server.preferences.sound;
                 server.preferences.save();
                 update_css($(this), server);
             });
     };

    jpoker.plugins.table.seats = function(id, server, table) {
        for(var seat = 0; seat < table.seats.length; seat++) {
            jpoker.plugins.player.seat(seat, id, server, table);
        }
    };

    jpoker.plugins.table.dealer = function(id, table, dealer) {
        for(var seat = 0; seat < table.seats.length; seat++) {
            if(seat == dealer) {
                $('#dealer' + seat + id).show();
            } else {
                $('#dealer' + seat + id).hide();
            }
        }
    };

    jpoker.plugins.table.position = function(id, table, serial_in_position) {
        var in_position = table.serial2player[serial_in_position];
        for(var seat = 0; seat < table.seats.length; seat++) {
            var seat_element = $('#player_seat' + seat + id);
            if(in_position && in_position.sit_out === false && in_position.seat == seat) {
                if(!seat_element.hasClass('jpoker_position')) {
                    seat_element.addClass('jpoker_position');
                }
            } else {
                if(seat_element.hasClass('jpoker_position')) {
                    seat_element.removeClass('jpoker_position');
                }
            }
        }
    };

    jpoker.plugins.table.timeout = function(id, table, serial_in_position, ratio) {
        var in_position = table.serial2player[serial_in_position];
        for(var seat = 0; seat < table.seats.length; seat++) {
            var timeout_element = $('#player_seat' + seat + '_timeout' + id);
            var width = parseFloat(timeout_element.css('width'));
            if(in_position && in_position.sit_out === false && in_position.seat == seat) {
                $('.jpoker_timeout_progress', timeout_element).stop().css({width: ratio*width+'px'}).show().animate({width: '0'}, {duration: ratio*table.player_timeout*1000, queue: false});
                timeout_element.attr('pcur', ratio*100).show();
            } else {
                timeout_element.hide();
            }
            timeout_element.find('.text').hide();
        }
    };

    jpoker.plugins.table.serial = function(id, server, table, serial) {
        if(serial in table.serial2player) {
            //
            // if the player who logs in is already sit at the table, recreate all
            //
            this.destroy(table, null, id);
            var element = document.getElementById(id);
            if(element) {
                this.create($(element), id, server, table.id);
            }
        } else {
            this.seats(id, server, table);
        }
    };

    jpoker.plugins.table.update = function(table, what, packet, id) {
        var element = document.getElementById(id);
        var server = jpoker.getServer(table.url);
        var url = table.url;
        var game_id = packet.game_id;
        var serial = packet.serial;
        var game_window = $('#game_window' + id);
        if(element && server) {
            switch(packet.type) {

            case 'PacketSerial':
                jpoker.plugins.table.serial(id, server, table, packet.serial);
                break;

            case 'PacketLogout':
                jpoker.plugins.table.seats(id, server, table);
                break;

            case 'PacketPokerPlayerArrive':
                jpoker.plugins.player.create(table, packet, id);
                if(server.loggedIn() && packet.serial == server.serial) {
                    $('.jpoker_sit_seat', game_window).hide();
                }
                break;

            case 'PacketPokerPlayerLeave':
                jpoker.plugins.player.leave(table, packet, id);
                if(server.loggedIn() && packet.serial == server.serial) {
                    jpoker.plugins.table.seats(id, server, table);
                }
                break;

            case 'PacketPokerUserInfo':
                jpoker.plugins.playerSelf.rebuy(url, game_id, serial, id);
                break;

            case 'PacketPokerState':
                jpoker.plugins.muck.muckRequestTimeout(id);
                break;

            case 'PacketPokerBoardCards':
                if (packet.cards.length > 0) {
                    jpoker.plugins.cards.update(table.board, 'board', id);
                    jpoker.plugins.table.callback.animation.deal_card(table, id, packet);
                    jpoker.plugins.table.callback.sound.deal_card(server);
                } else {
                    jpoker.plugins.cards.update(table.board, 'board', id);
                    jpoker.plugins.table.callback.animation.best_card_reset(table, id);
                }
                break;

            case 'PacketPokerBestCards':
                jpoker.plugins.table.callback.animation.best_card(table, id, packet);
                break;

            case 'PacketPokerDealCards':
                jpoker.plugins.table.callback.sound.deal_card(server);
                break;

            case 'PacketPokerPotChips':
                var count = 0;
                for(var pot = 0; pot < table.pots.length; pot+=1) {
                    if (table.pots[pot] !== 0) {
                        count += 1;
                    }
                }
                $('#pots' + id).removeClass().addClass('jpoker_ptable_pots jpoker_pots jpoker_pots'+count);
                jpoker.plugins.chips.update(table.pots[packet.index], '#pots' + id + ' .jpoker_pot' + packet.index);
                break;

            case 'PacketPokerChipsPotReset':
                $('#pots' + id).removeClass().addClass('jpoker_ptable_pots jpoker_pots jpoker_pots0');
                for(pot = 0; pot < table.pots.length; pot+=1) {
                    $('#pots' + id + ' .jpoker_pot' + pot).hide().children('.jpoker_chips_amount').text('');
                }
                break;

            case 'PacketPokerDealer':
                jpoker.plugins.table.dealer(id, table, packet.dealer);
                break;

            case 'PacketPokerSelfInPosition':
            case 'PacketPokerPosition':
                jpoker.plugins.table.position(id, table, packet.serial);
                jpoker.plugins.table.timeout(id, table, packet.serial, 1.0);
                break;

            case 'PacketPokerTimeoutWarning':
                jpoker.plugins.table.timeout(id, table, packet.serial, 0.5);
                break;

            case 'PacketPokerTimeoutNotice':
                jpoker.plugins.table.timeout(id, table, packet.serial, 0.0);
                break;

            case 'PacketPokerChat':
                var filtered_packet = jpoker.plugins.table.callback.chat_filter(table, packet);
                if(filtered_packet !== null) {
                    var lines = filtered_packet.message.replace(/\n$/, '').split('\n');
                    var chat;
                    var prefix = '';
                    if (filtered_packet.serial === 0) {
                        chat = $('.jpoker_chat_history_dealer', game_window);
                        prefix = _("Dealer") + ': ';
                    }
                    else {
                        chat = $('.jpoker_chat_history_player', game_window);
                        if(filtered_packet.serial in table.serial2player) {
                            prefix = table.serial2player[filtered_packet.serial].name + ': ';
                        }
                    }
                    for(var line = 0; line < lines.length; line++) {
                        var message = lines[line];
                        if (filtered_packet.serial === 0) {
                            message = message.replace(/^Dealer: /, '');
                        }
                        var chat_line = $('<div class=\'jpoker_chat_line\'>').appendTo(chat);
                        var chat_prefix = $('<span class=\'jpoker_chat_prefix\'></span>').appendTo(chat_line).text(prefix);
                        var chat_message = $('<span class=\'jpoker_chat_message\'></span>').appendTo(chat_line).text(message);
                    }
                    chat.attr('scrollTop', chat.attr('scrollHeight') || 0);
                jpoker.plugins.table.callback.chat_changed(chat);
                }
                break;

            case 'PacketPokerMuckRequest':
                jpoker.plugins.muck.muckRequest(server, packet, id);
                break;

            case 'PacketPokerStart':
                var table_info = $('#table_info' + id);
                if (table.is_tourney) {
                    $('.jpoker_table_info_level', table_info).html(table.level);
                }
                jpoker.plugins.table.callback.hand_start(packet);
                break;

            case 'PacketPokerTableTourneyBreakBegin':
                jpoker.plugins.table.callback.tourney_break(packet);
                break;

            case 'PacketPokerTableTourneyBreakDone':
                jpoker.plugins.table.callback.tourney_resume(packet);
                break;

            case 'PacketPokerTourneyRank':
                jpoker.plugins.table.rank(table, packet, id);
                break;

            case 'PacketPokerShowdown':
                $('.jpoker_timeout').hide();

                if(packet.showdown_stack && packet.showdown_stack.length > 0) {
                    var serial2delta = packet.showdown_stack[0].serial2delta;
                    if(serial2delta && server.serial in serial2delta && serial2delta[server.serial] > 0) {
                        jpoker.plugins.table.callback.sound.self_win(server);
                    }
                }
                break;
            }

            return true;
        } else {
            return false;
        }
    };

    jpoker.plugins.table.destroy = function(table, what, packet, id) {
        // it is enough to destroy the DOM elements, even for players
        if(jpoker.verbose) {
            jpoker.message('plugins.table.destroy ' + id);
        }
        jpoker.plugins.table.callback.quit(table, packet);
        $('#game_window' + id).remove();
        if (table.tourney_rank !== undefined) {
            jpoker.plugins.table.callback.tourney_end(table);
        }
        return false;
    };

    jpoker.plugins.table.reinit = function(table, what, packet, id) {
        jpoker.plugins.table.destroy(table, 'destroy', null, id);
        var element = document.getElementById(id);
        var server = jpoker.getServer(table.url);
        if(element && server) {
            jpoker.plugins.table.create($(element), id, server, table.id);
            return true;
        } else {
            return false;
        }
    };

    jpoker.plugins.table.rank = function(table, packet, id) {
        var rank = _(jpoker.plugins.table.templates.rank); // necessary because i18n is inactive when the template is first read
        packet.money = jpoker.chips.LONG(packet.money/100.0);
        var message = rank.supplant(packet);

        $.jpoker.dialog(message);
    };

    jpoker.plugins.table.rank.options = { width: 'none', height: 'none', autoOpen: false, resizable: false, dialogClass: 'jpoker_dialog_rank'};

    jpoker.plugins.table.templates = {
        room: 'expected to be overriden by mockup.js but was not',
        tourney_break: '<div>{label}</div><div>{date}</div>',
        powered_by: '',
        chat: '<div class=\'jpoker_chat_input\'><input value=\'chat here\' type=\'text\' width=\'100%\' maxlength=\'128\' /></div><div class=\'jpoker_chat_history_player_box\'><div class=\'jpoker_chat_history_player_heading\'>{chat_history_player_label}</div><div class=\'jpoker_chat_history_player\'></div></div><div class=\'jpoker_chat_history_dealer_box\'><div class=\'jpoker_chat_history_dealer_heading\'>{chat_history_dealer_label}</div><div class=\'jpoker_chat_history_dealer\'></div></div>',
        wait_for_bb: '<div id="jpoker_wait_for_bb"><input type="checkbox" checked /> <span>{wait_for_bb}</span>',
        placeholder: _("connecting to table {name}"),
        table_info: '<div class=\'jpoker_table_info_name\'><span class=\'jpoker_table_info_name_label\'>{name_label}</span>{name}</div><div class=\'jpoker_table_info_variant\'><span class=\'jpoker_table_info_variant_label\'>{variant_label}</span>{variant}</div><div class=\'jpoker_table_info_blind\'><span class=\'jpoker_table_info_blind_label\'>{betting_structure_label}</span>{betting_structure}</div><div class="jpoker_table_info_hand"></div><div class=\'jpoker_table_info_seats\'><span class=\'jpoker_table_info_seats_label\'>{seats_label}</span>{max_players}</div><div class=\'jpoker_table_info_flop\'>{percent_flop}<span class=\'jpoker_table_info_flop_label\'>{percent_flop_label}</span></div><div class=\'jpoker_table_info_player_timeout\'><span class=\'jpoker_table_info_player_timeout_label\'>{player_timeout_label}</span>{player_timeout}</div><div class=\'jpoker_table_info_muck_timeout\'><span class=\'jpoker_table_info_muck_timeout_label\'>{muck_timeout_label}</span>{muck_timeout}</div><div class=\'jpoker_table_info_level\'></div>',
        date: '',
        pots: '<div class=\'jpoker_pots_align\'><span class=\'jpoker_pot jpoker_pot9\'>{chips}</span><span class=\'jpoker_pot jpoker_pot7\'>{chips}</span><span class=\'jpoker_pot jpoker_pot5\'>{chips}</span><span class=\'jpoker_pot jpoker_pot3\'>{chips}</span><span class=\'jpoker_pot jpoker_pot1\'>{chips}</span><span class=\'jpoker_pot jpoker_pot0\'>{chips}</span><span class=\'jpoker_pot jpoker_pot2\'>{chips}</span><span class=\'jpoker_pot jpoker_pot4\'>{chips}</span><span class=\'jpoker_pot jpoker_pot6\'>{chips}</span><span class=\'jpoker_pot jpoker_pot8\'>{chips}</span></div>',
        rank: _("Won {money} chips, {rank} out of {players}."),
        sound: "{sound}"
    };

    jpoker.plugins.table.callback = {
        hand_start: function(packet) {
          $(".jpoker_table_info_hand").text("#"+packet.hand_serial);
        },
        tourney_break: function(packet) {
            var t = jpoker.plugins.table.templates;
            var date = new Date(packet.resume_time*1000);
            var date_string;
            if (t.date && (t.date !== '')) {
                date_string = $.strftime(t.date, date);
            } else {
                date_string = date.toLocaleString();
            }
            jpoker.dialog(t.tourney_break.supplant({label: _("This tournament is on break, and will resume at:"),
                            date: date_string}));
        },
        tourney_resume: function(packet) {
            $('#jpokerDialog').dialog('close');
        },
        tourney_end: function(table) {
            var server = jpoker.getServer(table.url);
            server.tourneyRowClick(server, {name: '', game_id: table.tourney_serial});
        },
        quit: function(table, packet) {
        },
        display_done: function(element) {
        },
        chat_changed: function(element) {
        },
        chat_filter: function(table, packet) {
            return packet;
        },
        sound: {
            deal_card: function(server) {
                if(server.preferences.sound) {
                    $('#jpokerSoundTable').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'deal_card.swf\' />');
                }
            },
            self_win: function(server) {
                if(server.preferences.sound) {
                    $('#jpokerSoundTable').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_win.swf\' />');
                }
            }
        },
        animation: {
            deal_card: function(table, id, packet, duration_arg, callback) {
                var duration = duration_arg ? duration_arg : 500;
                var game_window = $('#game_window' + id);
                var dealer_seat = table.dealer;
                var board_cards = {3: $('.jpoker_ptable_board0, .jpoker_ptable_board1, .jpoker_ptable_board2', game_window),
                                   4: $('.jpoker_ptable_board3', game_window),
                                   5: $('.jpoker_ptable_board4', game_window)}[packet.cards.length];
                if ((dealer_seat != -1) && board_cards) {
                    board_cards.each(function() {
                            var dealer = $('#dealer' + dealer_seat + id);
                            var dealerSeatOffset = $('#seat'+ dealer_seat + id).getOffset();
                            var dealerPosition = $('#dealer' + dealer_seat + id).getPosition();
                            var card = $(this);
                            var cardPosition = card.getPosition();
                            var gameFixedOffset = $('#game_fixed' + id).getOffset();
                            dealerPosition.top += dealerSeatOffset.top;
                            dealerPosition.left += dealerSeatOffset.left;
                            dealerPosition.top -= gameFixedOffset.top;
                            dealerPosition.left -= gameFixedOffset.left;
                            dealerPosition.top -= card.height()/2.0;
                            dealerPosition.left -= card.width()/2.0;
                            dealerPosition.top += dealer.height()/2.0;
                            dealerPosition.left += dealer.width()/2.0;
                            card.css({top: dealerPosition.top, left: dealerPosition.left, opacity: 0.0}).animate({top: cardPosition.top, left: cardPosition.left, opacity: 1.0}, duration, callback);
                        });
                }
            },
            best_card: function(table, id, packet, duration_arg, callback) {
                var duration = duration_arg ? duration_arg : 500;
                var game_window = $('#game_window' + id);
                var player = table.serial2player[packet.serial];
                var cards_element = $('.jpoker_ptable_board0, .jpoker_ptable_board1, .jpoker_ptable_board2, .jpoker_ptable_board3, .jpoker_ptable_board4, #card_seat'+player.seat+id+' .jpoker_card', game_window);
                var cards = packet.board.concat(packet.cards);
                if (jpoker.plugins.table.callback.animation.best_card.positions === undefined) {
                    jpoker.plugins.table.callback.animation.best_card.positions = {
                    };
                }
                cards_element.each(function() {
                        if (jpoker.plugins.table.callback.animation.best_card.positions[$(this).attr('id')] === undefined) {
                            jpoker.plugins.table.callback.animation.best_card.positions[$(this).attr('id')] = $(this).getPosition();
                        }
                    });

                cards_element.each(function(i) {
                        if ($(this).hasClass('jpoker_best_card') === false) {
                            if (jQuery.inArray(cards[i], packet.bestcards) != -1) {
                                $(this).addClass('jpoker_best_card').animate({top: '+=8px'}, duration, callback);
                            } else {
                                $(this).animate({opacity: 0.5}, duration, callback);
                            }
                        }
                    });
            },
            best_card_reset: function(table, id) {
                var game_window = $('#game_window' + id);
                if (jpoker.plugins.table.callback.animation.best_card.positions !== undefined) {
                    $.each(jpoker.plugins.table.callback.animation.best_card.positions, function(id, position) {
                            $('#'+id).removeClass('jpoker_best_card').css(position).css({opacity: 1.0});
                        });
                }
            }
        }
    };

    //
    // player (table plugin helper)
    //
    jpoker.plugins.player = {
        create: function(table, packet, id) {
            var url = table.url;
            var game_id = table.id;
            var serial = packet.serial;
            var player = table.serial2player[serial];
            var seat = player.seat;
            var server = jpoker.getServer(url);
            jpoker.plugins.player.seat(seat, id, server, table);
            jpoker.plugins.cards.update_value(player.cards, 'card_seat' + player.seat, id);
            $('#player_seat' + seat + '_bet' + id).addClass('jpoker_bet').html(jpoker.plugins.chips.template);
            $('#player_seat' + seat  + '_money' + id).addClass('jpoker_money').html(jpoker.plugins.chips.template);
            $('#player_seat' + seat  + '_action' + id).addClass('jpoker_action');
            var avatar_element = $('#player_seat' + seat  + '_avatar' + id);
            if ((packet.avatar_url !== undefined) && (packet.avatar_url != 'random')) {
                avatar_element.removeClass().addClass('jpoker_avatar jpoker_ptable_player_seat' + seat + '_avatar ');
                this.avatar.update(player.name, packet.avatar_url, avatar_element);
            } else {
                var avatar = (seat + 1) + (10 * game_id % 2);
                avatar_element.removeClass().addClass('jpoker_avatar jpoker_ptable_player_seat' + seat + '_avatar jpoker_avatar_default_' + avatar);
                avatar_element.empty();
                var avatar_url = server.urls.avatar+'/'+serial;
                jpoker.plugins.player.avatar.update(player.name, avatar_url, avatar_element);
            }
            avatar_element.show();
            var seat_element = $('#player_seat' + seat + id);
            seat_element.hover(function() {
                    jpoker.plugins.player.callback.seat_hover_enter(player, id);
                }, function() {
                    jpoker.plugins.player.callback.seat_hover_leave(player, id);
                }).click(function() {
                        jpoker.plugins.player.callback.seat_click(player, id);
                    });
            var timeout_element = $('#player_seat' + seat  + '_timeout' + id).removeClass().addClass('jpoker_timeout jpoker_ptable_player_seat' + seat + '_timeout').html('<div class=\'jpoker_timeout_progress\'></div>');

            jpoker.plugins.player.chips(player, id);
            var name = $('#player_seat' + seat + '_name' + id);
            name.addClass('jpoker_name');
            name.text(player.name);
            if(server.serial == serial) {
                jpoker.plugins.playerSelf.create(table, packet, id);
            }
            if(!player.sit_out && !player.auto) {
                jpoker.plugins.player.sit(player, id);
            } else {
                jpoker.plugins.player.sitOut(player, id);
            }
            this.callback.sound.arrive(server);
            player.registerUpdate(this.update, id, 'update' + id);
            player.registerDestroy(this.destroy, id, 'destroy' + id);
            var stats_element = $('#player_seat' + seat  + '_stats' + id).removeClass().addClass('jpoker_player_stats jpoker_ptable_player_seat' + seat + '_stats');
            var sidepot_element = $('#player_seat' + seat  + '_sidepot' + id).removeClass().addClass('jpoker_player_sidepot jpoker_ptable_player_seat' + seat + '_sidepot').hide();

            $('#player_seat' + seat  + '_hole' + id).addClass('jpoker_player_hole');

            // at the end of player.create: call player_arrive callback
            $('#seat' + seat + id).addClass('jpoker_seat jpoker_seat'+seat);
            seat_element.addClass('jpoker_player_seat jpoker_player_seat'+seat);
            this.callback.player_arrive(seat_element.get(0), serial);
            this.callback.display_done(seat_element.get(0), player);
        },

        leave: function(player, packet, id) {
            var server = jpoker.getServer(player.url);
            if(server.serial == packet.serial) {
                jpoker.plugins.playerSelf.leave(player, packet, id);
            }
        },

        update: function(player, what, packet, id) {
            var server = jpoker.getServer(player.url);

            switch(packet.type) {

            case 'PacketPokerSit':
            jpoker.plugins.player.sit(player, id);
            break;

            case 'PacketPokerSitOut':
            jpoker.plugins.player.sitOut(player, id);
            break;

            case 'PacketPokerAutoFold':
            jpoker.plugins.player.sitOut(player, id);
            break;

            case 'PacketPokerPlayerCards':
            var update = function() {
                jpoker.plugins.cards.update_value(player.cards, 'card_seat' + player.seat, id);
            };
            $('#seat' + player.seat + id).addClass('jpoker_player_dealt');
            if(player.cards.dealt === true) {
                jpoker.plugins.player.callback.animation.deal_card(player, id, undefined, update);
            } else {
                update();
            }
            break;

            case 'PacketPokerBestCards':
            break;

            case 'PacketPokerFold':
            $('#seat' + player.seat + id).removeClass('jpoker_player_dealt');
            jpoker.plugins.player.action(player, id);
            jpoker.plugins.player.callback.sound.fold(server);
            break;

            case 'PacketPokerCheck':
            jpoker.plugins.player.action(player, id);
            jpoker.plugins.player.callback.sound.check(server);
            break;

            case 'PacketPokerCall':
            jpoker.plugins.player.action(player, id);
            jpoker.plugins.player.callback.sound.call(server);
            break;

            case 'PacketPokerRaise':
            jpoker.plugins.player.action(player, id);
            jpoker.plugins.player.callback.sound.raise(server);
            break;

            case 'PacketPokerStart':
            $('.jpoker_card').each(function() {
              var c = $(this).attr('class');
              $(this).attr('class', c.replace(/\sjpoker_card_[^\s]+/, ' jpoker_card_back'));
            });
            
            $('#seat' + player.seat + id).removeClass('jpoker_player_dealt');
            jpoker.plugins.player.action(player, id);
            jpoker.plugins.player.handStart(player, id);
            $('#player_seat' + player.seat + id).removeClass('jpoker_player_allin');
            break;

            case 'PacketPokerBeginRound':
            jpoker.plugins.player.beginRound(player, id);
            break;

            case 'PacketPokerHighestBetIncrease':
            jpoker.plugins.player.highestBetIncrease(player, id);
            break;

            case 'PacketPokerInGame':
            jpoker.plugins.player.inGame(player, id);
            break;

            case 'PacketPokerPlayerHandStrength':
            jpoker.plugins.player.handStrength(player, packet.hand, id);
            break;

            case 'PacketPokerTableMove':
            jpoker.plugins.player.tableMove(player, packet, id);
            break;

            case 'PacketPokerEndRound':
            jpoker.plugins.player.action(player, id);
            break;

            case 'PacketPokerPlayerChips':
            jpoker.plugins.player.chips(player, id);
            if (player.all_in === true) {
                $('#player_seat' + player.seat + id).addClass('jpoker_player_allin');
            }
            break;

            case 'PacketPokerChipsBet2Pot':
            jpoker.plugins.player.callback.animation.bet2pot(player, id, packet);
            break;

            case 'PacketPokerChipsPlayer2Bet':
            jpoker.plugins.player.callback.animation.money2bet(player, id);
            break;

            case 'PacketPokerChipsPot2Player':
            jpoker.plugins.player.callback.animation.pot2money(player, id, packet);
            break;

            case 'PacketPokerTimeoutWarning':
            case 'PacketPokerTimeoutNotice':
            if(server.serial == packet.serial) {
                jpoker.plugins.playerSelf.timeout(player, id, packet);
            }
            break;

            case 'PacketPokerSelfInPosition':
            jpoker.plugins.playerSelf.inPosition(player, id);
            break;

            case 'PacketPokerSelfLostPosition':
            jpoker.plugins.playerSelf.lostPosition(player, packet, id);
            break;

            case 'PacketPokerPotChips':
            jpoker.plugins.player.side_pot.update(player, id);
            break;

            case 'PacketPokerChipsPotReset':
            jpoker.plugins.player.side_pot.update(player, id);
            break;

            case 'PacketPokerPlayerStats':
            jpoker.plugins.player.stats.update(player, packet, id);
            break;
            }
            return true;
        },

        handStart: function(player, id) {
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.handStart(player, id);
            }
        },

        beginRound: function(player, id) {
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.beginRound(player, id);
            }
        },

        highestBetIncrease: function(player, id) {
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.highestBetIncrease(player, id);
            }
        },

        inGame: function(player, id) {
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.inGame(player, id);
            }
        },

        handStrength: function(player, hand, id) {
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.handStrength(player, hand, id);
            }
        },

        tableMove: function(player, packet, id) {
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.tableMove(player, packet, id);
            }
        },

        sit: function(player, id) {
            var name = $('#player_seat' + player.seat + id);
            if(name.hasClass('jpoker_sit_out')) {
                name.removeClass('jpoker_sit_out');
            }
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.sit(player, id);
            }
        },

        sitOut: function(player, id) {
            var name = $('#player_seat' + player.seat + id);
            if(!name.hasClass('jpoker_sit_out')) {
                name.addClass('jpoker_sit_out');
            }
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.sitOut(player, id);
            }
        },

        chips: function(player, id) {
            jpoker.plugins.chips.update(player.money, '#player_seat' + player.seat + '_money' + id);
            jpoker.plugins.chips.update(player.bet, '#player_seat' + player.seat + '_bet' + id);
            if(jpoker.getServer(player.url).serial == player.serial) {
                jpoker.plugins.playerSelf.chips(player, id);
            }
        },

        action: function(player, id) {
            $('#player_seat' + player.seat + '_action' + id).html(player.action);
        },

        seat: function(seat, id, server, table) {
            var selfPlayerLoggedButNotSit = server.loggedIn() && (table.serial2player[server.serial] === undefined) && !table.is_tourney;
            if(table.seats[seat] !== null) {
                $('#seat' + seat + id).show();
                $('#sit_seat' + seat + id).hide();
            } else {
                $('#seat' + seat + id).hide();
                if(selfPlayerLoggedButNotSit && ($.inArray(seat, table.seats_left) != -1)) {
                    var sit = $('#sit_seat' + seat + id);
                    sit.show();
                    sit.click(function() {
                            var server = jpoker.getServer(table.url);
                            if(server && server.loggedIn()) {
                                server.sendPacket({ 'type': 'PacketPokerSeat',
                                            'serial': server.serial,
                                            'game_id': table.id,
                                            'seat': seat
                                            });
                            }
                            $('#sit_seat' + seat + id).addClass('jpoker_self_get_seat');
                        });
                } else {
                    $('#sit_seat' + seat + id).hide();
                }
            }
        },

        side_pot: {
            template : '{label} {index}: {bet}',
            update: function(player, id) {
                if (player.side_pot !== undefined) {
                    var html = this.template.supplant($.extend(player.side_pot, {label: _("Pot")}));
                    $('#player_seat' + player.seat + '_sidepot' + id).html(html).show();
                } else {
                    $('#player_seat' + player.seat + '_sidepot' + id).html('').hide();
                }
            }
        },

        avatar: {
            template : '<img src=\'{url}\' alt=\'{name}\' />',
            update: function(name, url, element) {
                return element.html(this.template.supplant({ name: name, url: url }));
            }
        },

        stats: {
            templates: {
                rank: '<div class=\'jpoker_player_rank\'>{rank}</div>',
                level: '<div class=\'jpoker_player_level jpoker_player_level_{level}\'></div>'
            },
            getLevel: function(percentile) {
                var level;
                if (percentile >= 3) {
                    level = 'master';
                } else if (percentile >= 2) {
                    level = 'expert';
                } else if (percentile >= 1) {
                    level = 'pro';
                } else if (percentile >= 0) {
                    level = 'junior';
                }
                return level;
            },
            getHTML: function(packet) {
                var html = [];
                var t = this.templates;
                if ((packet.rank !== undefined) && (packet.rank !== null)) {
                    html.push(t.rank.supplant({rank: packet.rank}));
                }
                if ((packet.level !== undefined) && (packet.level !== null)) {
                    html.push(t.level.supplant({level: packet.level}));
                }
                return html.join('\n');
            },
            update: function(player, packet, id) {
                packet.level = this.getLevel(packet.percentile);
                $('#player_seat' + player.seat + '_stats' + id).html(this.getHTML(packet));
                $('#player_seat' + player.seat + id).addClass('jpoker_player_level_'+packet.level);
            }
        },

        destroy: function(player, what, dummy, id) {
            var server = jpoker.servers[player.url];
            var table = server.tables[player.game_id];
            jpoker.plugins.player.seat(player.seat, id, server, table);
            if(player.serial == server.serial) {
                jpoker.plugins.playerSelf.destroy(player, dummy, id);
            }
        },

        callback: {
            seat_hover_enter: function(player, id) {
                $('#player_seat' + player.seat  + id).addClass('jpoker_seat_hover');
            },
            seat_hover_leave: function(player, id) {
                $('#player_seat' + player.seat  + id).removeClass('jpoker_seat_hover');
            },
            seat_click: function(player, id) {
            },
            player_arrive: function(element, serial) {
            },
            display_done: function(element, player) {
            },
            sound: {
                arrive: function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSound').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_arrive.swf\' />');
                    }
                },
                call: function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSoundAction').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_call.swf\' />');
                    }
                },
                raise: function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSoundAction').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_bet.swf\' />');
                    }
                },
                fold: function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSoundAction').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_fold.swf\' />');
                    }
                },
                check: function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSoundAction').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_check.swf\' />');
                    }
                }

            },
            animation: {
                money2bet: function(player, id, duration_arg, callback) {
                    var duration = duration_arg ? duration_arg : 500;
                    var bet = $('#player_seat' + player.seat + '_bet' + id);
                    var bet_position = bet.getPosition();
                    var money = $('#player_seat' + player.seat + '_money' + id);
                    var money_position = money.getPosition();
                    var seat_offset = $('#seat'+ player.seat + id).getOffset();
                    var player_seat_offset = $('#player_seat'+ player.seat + id).getOffset();
                    money_position.top += player_seat_offset.top;
                    money_position.left += player_seat_offset.left;
                    money_position.top -= seat_offset.top;
                    money_position.left -= seat_offset.left;
                    bet.css({top: money_position.top, left: money_position.left, opacity: 0}).animate({top: bet_position.top, left: bet_position.left, opacity: 1.0}, duration, callback);
                },
                deal_card: function(player, id, duration_arg, callback) {
                    var duration = duration_arg ? duration_arg : 500;
                    var table = jpoker.getTable(player.url, player.game_id);
                    var playerSeatOffset = $('#seat'+ player.seat + id).getOffset();
                    var hole = $('#player_seat'+ player.seat + '_hole' + id);
                    var holePosition = hole.getPosition();
                    var dealer_seat = table.dealer;
                    var dealer, dealerSeatOffset, dealerPosition;
                    if (dealer_seat != -1) {
                        dealer = $('#dealer' + dealer_seat + id);
                        dealerSeatOffset = $('#seat'+ dealer_seat + id).getOffset();
                        dealerPosition = $('#dealer' + dealer_seat + id).getPosition();
                        dealerPosition.top += dealerSeatOffset.top;
                        dealerPosition.top -= playerSeatOffset.top;
                        dealerPosition.left += dealerSeatOffset.left;
                        dealerPosition.left -= playerSeatOffset.left;
                        dealerPosition.top -= hole.height()/2.0;
                        dealerPosition.left -= hole.width()/2.0;
                        dealerPosition.top += dealer.height()/2.0;
                        dealerPosition.left += dealer.width()/2.0;
                        hole.css({top: dealerPosition.top, left: dealerPosition.left, opacity: 0}).animate({top: holePosition.top, left: holePosition.left, opacity: 1.0}, duration, callback);
                    } else {
                        callback.call();
                    }
                },
                bet2pot: function(player, id, packet, duration_arg, callback) {
                    var duration = duration_arg ? duration_arg : 500;
                    var bet = $('#player_seat' + player.seat + '_bet' + id);
                    var chip = bet.clone().insertAfter(bet).addClass('jpoker_bet2pot_animation');
                    var pots_element = $('#pots' + id);
                    var pots_offset = pots_element.getOffset();
                    var player_seat_offset = $('#seat'+ player.seat + id).getOffset();
                    var pot_position = $('.jpoker_pot' + packet.pot).getPosition();
                    var remove_chip = function() {
                        chip.remove();
                    };
                    pot_position.left += pots_offset.left;
                    pot_position.left -= player_seat_offset.left;
                    pot_position.top += pots_offset.top;
                    pot_position.top -= player_seat_offset.top;
                    chip.css({opacity: 1}).animate({top: pot_position.top, left: pot_position.left, opacity: 0.0}, duration, callback ? function() {callback(remove_chip);} : remove_chip);
                },
                pot2money: function(player, id, packet, duration_arg, callback, hook) {
                    var duration = duration_arg ? duration_arg : 500;
                    var pots = $('#pots' + id);
                    var pots_offset = pots.getOffset();
                    var pot = $('.jpoker_pot' + packet.pot, pots).not('.jpoker_pot2money_animation');
                    var chip = pot.show().clone().insertAfter(pot).addClass('jpoker_pot2money_animation');
                    var money_element = $('#player_seat' + player.seat + '_money' + id);
                    var player_seat_offset = $('#player_seat'+ player.seat + id).getOffset();
                    var money_position = money_element.getPosition();
                    var pot_position = pot.getPosition();
                    var remove_chip = function() {
                        chip.remove();
                    };
                    pot.hide();
                    money_position.top += player_seat_offset.top;
                    money_position.left += player_seat_offset.left;
                    money_position.top -= pots_offset.top;
                    money_position.left -= pots_offset.left;
                    chip.css({opacity: 1, position: 'absolute', top: pot_position.top, left: pot_position.left});
                    if (hook !== undefined) {
                        hook(chip);
                    }
                    chip.animate({top: money_position.top, left: money_position.left, opacity: 0.0}, duration, callback ? function() {callback(remove_chip, chip);} : remove_chip);
                }
            }
        }
    };

    //
    // player self (table plugin helper)
    //
    jpoker.plugins.playerSelf = {
        create: function(table, packet, id) {
            var game_window = $('#game_window' + id);
            table.registerUpdate(this.updateTable, id, 'self update' + id);

            var url = table.url;
            var game_id = packet.game_id;
            var serial = packet.serial;
            var player = table.serial2player[serial];
            var names = [ 'check', 'call', 'raise', 'fold', 'allin', 'pot', 'halfpot', 'threequarterpot' ];
            var labels = [ _("check"), _("call") + ' <span class=\'jpoker_call_amount\'></span>', _("Raise"), _("fold"), _("all in"), _("pot"), _("1/2"), _("3/4") ];
            for(var i = 0; i < names.length; i++) {
                $('#' + names[i] + id).html(jpoker.plugins.playerSelf.templates.action.supplant({ action: labels[i] })).hover(function(){
                  $(this).addClass('hover');
                },function(){
                  $(this).removeClass('hover');
                });
            }

            if (! table.is_tourney) {
              $('#jpoker_wait_for_bb').show();
            }

            //
            // rebuy
            //
            var rebuy = $('#rebuy' + id);
            rebuy.click(function() {
                    var server = jpoker.getServer(url);
                    if(server && server.loggedIn()) {
                        var element = jpoker.plugins.playerSelf.rebuy(url, game_id, serial, id);
                        if(element) {
                            element.dialog('open');
                            server.getUserInfo();
                        }
                    }
                });
            rebuy.hover(function(){
                        $(this).addClass('hover');
                    },function(){
                        $(this).removeClass('hover');
                    });
            rebuy.html(jpoker.plugins.playerSelf.templates.rebuy_button.supplant({ rebuy: _("Rebuy") }));
            rebuy.show();

            //
            // sitout
            //
            $('#sitout' + id).html(jpoker.plugins.playerSelf.templates.sitout.supplant({ sitout: _("sit out") }));

            $('#sitout' + id).click(function() {
                var info = jpoker.getServerTablePlayer(url, table.id, serial);
                if(info.server && info.server.loggedIn()) {
                    server.sendPacket({ 'type': 'PacketPokerSitOut',
                                'game_id': table.id,
                                'serial': serial });
                    $(this).hide();
                }
                return false;
            }).hover(function(){
                $(this).addClass('hover');
            },function(){
                $(this).removeClass('hover');
            });


            $('<div id=\'sitout_fold' + id  + '\'>')
              .insertAfter('#sitout' + id)
              .addClass('jpoker_ptable_sitout_fold')
              .html(jpoker.plugins.playerSelf.templates.sitout.supplant({ sitout: _("fold/sit out") }))
              .click(function() {
                  var info = jpoker.getServerTablePlayer(url, table.id, serial);
                      if(info.server && info.server.loggedIn()) {
                          info.player.sit_out_fold_sent = true;
                          server.sendPacket({ 'type': 'PacketPokerSitOut',
                                      'game_id': table.id,
                                      'serial': serial });
                          server.sendPacket({ 'type': 'PacketPokerFold',
                                      'game_id': table.id,
                                      'serial': serial });
                          $(this).hide();
                      }
                      return false;
              }).hover(function(){
                  $(this).addClass('hover');
              },function(){
                  $(this).removeClass('hover');
              });

            //
            // sitin
            //
            $('#sitin' + id).html(jpoker.plugins.playerSelf.templates.sitin.supplant({ sitin: _("sit in") }));
            $('#sitin' + id).click(function() {
                    var server = jpoker.getServer(url);
                    if(server && server.loggedIn()) {
                        server.sendPacket({ 'type': 'PacketPokerSit',
                                    'game_id': table.id,
                                    'serial': serial });
                        $(this).hide();
                    }
                    return false;
                }).hover(function(){
                        $(this).addClass('hover');
                    },function(){
                        $(this).removeClass('hover');
                    }).show();

            //
            // chat
            //

            var chat = function() {
                var server = jpoker.getServer(url);
                if(server) {
                    var input = $('.jpoker_chat_input input', game_window);
                    var message = input.attr('value');

                    if (message && message != '') {
                      server.sendPacket({ 'type': 'PacketPokerChat',
                                  'serial': server.serial,
                                  'game_id': table.id,
                                  'message': message
                                  });
                    }
                    input.attr('value', '');
                }
            };
            $('.jpoker_chat_input', game_window).unbind('keypress').keypress(function(e) {
                    if(e.which == 13) {
                        chat();
                    }
                }).show();

            //
            // muck
            //
            $('#muck_accept' + id).html(jpoker.plugins.muck.templates.muck_accept.supplant({muck_accept_label: _("Muck")})).click(function() {
                    var server = jpoker.getServer(url);
                    server.sendPacket({type: 'PacketPokerMuckAccept', serial: server.serial, game_id: table.id});
                }).hover(function(){
                        $(this).addClass('hover');
                    },function(){
                        $(this).removeClass('hover');
                    });
            $('#muck_deny' + id).html(jpoker.plugins.muck.templates.muck_deny.supplant({muck_deny_label: _("Show")})).click(function() {
                    var server = jpoker.getServer(url);
                    server.sendPacket({type: 'PacketPokerMuckDeny', serial: server.serial, game_id: table.id});
                }).hover(function(){
                        $(this).addClass('hover');
                    },function(){
                        $(this).removeClass('hover');
                    });

            //
            // options
            //
            var options = $('#options' + id).html(jpoker.plugins.options.templates.button.supplant({options_label: _("Options")})).hover(function(){
                    $(this).addClass('hover');
                },function(){
                    $(this).removeClass('hover');
                }).show();
            options.after(jpoker.plugins.options.templates.dialog.supplant({
                        auto_muck: jpoker.plugins.muck.templates.auto_muck.supplant({
                                id: id,
                                    auto_muck_win_label: _("Muck winning"),
                                    auto_muck_win_title: _("Muck winning hands on showdown"),
                                    auto_muck_lose_label: _("Muck losing"),
                                    auto_muck_lose_title: _("Muck losing hands on showdown")})}));
            $('#jpokerOptionsDialog').dialog($.extend({}, jpoker.dialog_options, {title: _("Options")}));
            options.click(function() {
                    $('#jpokerOptionsDialog').dialog('open');
                });

            $('#auto_muck_win' + id).click(function() {
                    var server = jpoker.getServer(url);
                    jpoker.plugins.muck.sendAutoMuck(server, game_id, id);
                });
            $('#auto_muck_lose' + id).click(function() {
                    var server = jpoker.getServer(url);
                    jpoker.plugins.muck.sendAutoMuck(server, game_id, id);
                });

            var server = jpoker.getServer(url);
            $('#auto_muck_win' + id).each(function() { this.checked = server.preferences.auto_muck_win; });
            $('#auto_muck_lose' + id).each(function() { this.checked = server.preferences.auto_muck_lose; });
            jpoker.plugins.muck.sendAutoMuck(server, game_id, id);

            //
            // autoaction
            //
            var auto_action_element = $('#auto_action' + id).html(jpoker.plugins.playerSelf.templates.auto_action.supplant({
                id: id,
                auto_check_fold_label: _("Check/Fold"),
                auto_check_call_label: _("Check/Call any"),
                auto_raise_label: _("Raise"),
                auto_check_label: _("check"),
                auto_call_label: _("Call")
            }));

            $('.jpoker_auto_action', auto_action_element).hide();

            $('input[type=checkbox]', auto_action_element).click(function() {
                var clicked = this;
                $('input[type=checkbox]', auto_action_element).each(function() {
                    if (this != clicked) {
                        this.checked = false;
                    }
                });
            });

            //
            // hand strength
            //
            var hand_strength_element = $('#hand_strength' + id).html(jpoker.plugins.playerSelf.templates.hand_strength.supplant({
                        label: _("Hand strength:")
                    })).hide();

            if(serial == table.serial_in_position) {
                jpoker.plugins.playerSelf.inPosition(player, id);
            }
            $('#game_window' + id).addClass('jpoker_self');
            $('#sit_seat' + player.seat + id).removeClass('jpoker_self_get_seat');
            $('#seat' + player.seat + id).addClass('jpoker_player_self');
        },

        leave: function(player, packet, id) {
            var game_window = $('#game_window' + id);
            $('#sitout' + id).hide();
            $('#sitout_fold' + id).hide();
            $('#rebuy' + id).hide();
            $('#options' + id).hide();
            $('#jpoker_wait_for_bb').hide();
            $('.jpoker_chat_input', game_window).hide();
            game_window.removeClass('jpoker_self');
            $('#player_seat' + packet.seat + id).removeClass('jpoker_player_self');
        },

        updateTable: function(table, what, packet, id) {
            switch(packet.type) {

            }
            return true;
        },

        rebuy_options: { width: '300', height: '200', minHeight: '300px', autoOpen: false, resizable: false },

        rebuy: function(url, game_id, serial, id) {
            $('#rebuy' + id).show();
            var server = jpoker.getServer(url);
            var player = jpoker.getPlayer(url, game_id, serial);
            if(!player) {
                return false;
            }
            var table = jpoker.getTable(url, game_id);
            var limits = table.buyInLimits();
            var rebuy = $('#jpokerRebuy');
            if(rebuy.size() === 0) {
                $('body').append('<div style="min-width: 300px; min-height: 300px;" id=\'jpokerRebuy\' class=\'jpoker_jquery_ui\' title=\'' + _("Add chips") + '\' />');
                rebuy = $('#jpokerRebuy');
                rebuy.dialog(this.rebuy_options);
            }
            var packet_type;
            var label;
            if ((player.state == 'buyin') && !player.buy_in_payed) {
                packet_type = 'PacketPokerBuyIn';
                label = _("Buy In");
            } else {
                packet_type = 'PacketPokerRebuy';
                label = _("Rebuy");
            }
            rebuy.html(this.templates.rebuy.supplant({
                        'min': jpoker.chips.SHORT(limits[0]),
                        'current': jpoker.chips.SHORT(limits[1]),
                        'title' : Math.floor(limits[1]*100),
                        'max': jpoker.chips.SHORT(limits[2]),
                        'label': label,
                        'auto_sitin_label': _("Sit in")
                    }));
            $('.jpoker_auto_sitin input', rebuy).each(function() { this.checked = server.preferences.auto_sitin; });

            $('.jpoker_rebuy_action', rebuy).click(function() {
                    var server = jpoker.getServer(url);
                    if(server) {
                        var amount = parseInt($('.jpoker_rebuy_current', rebuy).attr('title'), 10);
                        if (!isNaN(amount)) {
                            server.sendPacket({ 'type': packet_type,
                                        'serial': server.serial,
                                        'game_id': table.id,
                                        'amount': parseInt($('.jpoker_rebuy_current', rebuy).attr('title'), 10)
                            }, function() {
                              if ($('.jpoker_auto_sitin input', rebuy).is(':checked')) {
                                  $('#sitin' + id).click();
                              }
                              server.preferences.auto_sitin = $('.jpoker_auto_sitin input', rebuy).is(':checked');
                            });
                        } else {
                            jpoker.error('rebuy with NaN amount: ' + $('.jpoker_rebuy_current', rebuy).attr('title'));
                        }
                    }
                    rebuy.dialog('close');
            });

            $('.ui-slider-1', rebuy).slider({
                        min: limits[0]*100,
                        startValue: limits[1]*100,
                        max: limits[2]*100,
                        step: 1,
                        change: function(event, ui) {
                          var current = $('.jpoker_rebuy_current').html(ui.value/100.0);
                          current.attr('title', ui.value);
                        },
                        slide: function(event, ui) {
                          var current = $('.jpoker_rebuy_current').html(ui.value/100.0);
                          current.attr('title', ui.value);
                        }
            });
            
            return rebuy;
        },

        updateAutoAction: function(player, id) {
        },

        beginRound: function(player, id) {
            var server = jpoker.servers[player.url];
            var table = server.tables[player.game_id];
            var auto_action_element = $('#auto_action' + id);
            if (player.in_game) {
                $('.jpoker_auto_action', auto_action_element).show();
                if (table.betLimit.call > 0) {
                    $('.jpoker_auto_check', auto_action_element).hide();

                    var call = jpoker.getCallAmount(table.betLimit, player);
                    $('.jpoker_call_amount', auto_action_element).text(jpoker.chips.SHORT(call));
                } else {
                    $('.jpoker_auto_call', auto_action_element).hide();
                }
            }
        },

        highestBetIncrease: function(player, id) {
            var server = jpoker.servers[player.url];
            var table = server.tables[player.game_id];
            var auto_action_element = $('#auto_action' + id);
            if (player.in_game) {
                if (table.betLimit.call > 0) {
                    var call = jpoker.getCallAmount(table.betLimit, player);
                    $('.jpoker_auto_action', auto_action_element).show();
                    $('input[name=auto_check]')[0].checked = false;
                    $('input[name=auto_call]')[0].checked = false;
                    $('input[name=auto_raise]')[0].checked = false;
                    $('.jpoker_auto_check', auto_action_element).hide();
                    $('.jpoker_auto_call', auto_action_element).show();
                    $('.jpoker_call_amount', auto_action_element).text(jpoker.chips.SHORT(call));
                }
            }
        },


        handStart: function(player, id) {
            var hand_strength_element = $('#hand_strength' + id).hide();
            $('.jpoker_hand_strength_value', hand_strength_element).text('');
        },

        inGame: function(player, id) {
            var auto_action_element = $('#auto_action' + id);
            $('.jpoker_auto_action', auto_action_element).hide();
        },

        handStrength: function(player, hand, id) {
            var hand_strength_element = $('#hand_strength' + id).show();
            $('.jpoker_hand_strength_value', hand_strength_element).text(hand);
            jpoker.plugins.playerSelf.callback.hand_strength.display_done(hand_strength_element);
        },

        tableMove: function(player, packet, id) {
            jpoker.plugins.playerSelf.callback.table_move(player, packet, id);
        },

        sit: function(player, id) {
            var name = $('#player_seat' + player.seat + '_name' + id);
            var url = player.url;
            var server = jpoker.servers[url];
            var serial = player.serial;
            var game_id = player.game_id;
            name.unbind('click');
            name.html(player.name);
            name.click(function() {
                    var server = jpoker.servers[url];
                    if(server) {
                        server.sendPacket({ 'type': 'PacketPokerSitOut',
                                    'serial': serial,
                                    'game_id': game_id
                                    });
                    }
                });
            $('#sitout' + id).show();
            $('#sitout_fold' + id).show();
            $('#sitin' + id).hide();
        },

        sitOut: function(player, id) {
            var name = $('#player_seat' + player.seat + '_name' + id);
            var url = player.url;
            var server = jpoker.servers[url];
            var serial = player.serial;
            var game_id = player.game_id;
            name.unbind('click');
            name.html(_("click to sit"));
            name.click(function() {
                    var server = jpoker.servers[url];
                    if(server) {
                        var player = server.tables[game_id].serial2player[serial];
                        if(player.money > jpoker.chips.epsilon) {
                            server.sendPacket({ 'type': 'PacketPokerSit',
                                        'serial': serial,
                                        'game_id': game_id
                                        });
                        } else {
                            jpoker.dialog(_("not enough money"));
                        }
                    }
                });
            $('#sitout' + id).hide();
            $('#sitout_fold' + id).hide();
            $('#sitin' + id).show();
        },

        chips: function(player, id) {
            var table = jpoker.getTable(player.url, player.game_id);
            if(table.state == 'end') {
                var limits = table.buyIn;
                if(player.money < limits.max) {
                    $('#rebuy' + id).show();
                } else {
                    $('#rebuy' + id).hide();
                }
            }

            if (table.is_tourney) {
                $('#rebuy' + id).hide();
            } else if ((player.state == 'buyin') &&
                       (player.money === 0) &&
                       (table.reason != 'TablePicker')) {
                $('#rebuy' + id).click();
            } else if (player.state != 'buyin' && player.broke) {
                $('#rebuy' + id).click();
            }
        },

        inPosition: function(player, id) {
            var game_id = player.game_id;
            var serial = player.serial;
            var url = player.url;
            var server = jpoker.getServer(url);
            var table = jpoker.getTable(url, game_id);
            var betLimit = table.betLimit;
            // TODO: it'd be better to check for blindAnte round here
            if (betLimit == null) return;
            var send = function(what) {
                var server = jpoker.getServer(url);
                if(server) {
                    server.sendPacket({ 'type': 'PacketPoker' + what,
                                'serial': serial,
                                'game_id': game_id
                                });
                }
                return false; // prevent default action on <a href>
            };

            var auto_action_element = $('#auto_action' + id);
            var auto_check_fold_input = $('input[name=auto_check_fold]', auto_action_element);
            var auto_check_call_input = $('input[name=auto_check_call]', auto_action_element);
            var auto_raise_input = $('input[name=auto_raise]', auto_action_element);
            var auto_check_input = $('input[name=auto_check]', auto_action_element);
            var auto_call_input = $('input[name=auto_call]', auto_action_element);

            if (player.sit_out_fold_sent) {
                send('Fold');
            }

            if (auto_check_fold_input.is(':checked')) {
                if (betLimit.call > 0) {
                    send('Fold');
                } else {
                    send('Check');
                }
            }
            if (auto_check_call_input.is(':checked')) {
                if (betLimit.call > 0) {
                    send('Call');
                } else {
                    send('Check');
                }
            }
            if (auto_raise_input.is(':checked')) {
                send('Raise');
            }
            if (auto_check_input.is(':checked')) {
                if (betLimit.call === 0) {
                    send('Check');
                }
            }
            if (auto_call_input.is(':checked')) {
                if (betLimit.call > 0) {
                    send('Call');
                }
            }
            $('input[type=checkbox]', auto_action_element).each(function() {
                    this.checked = false;
                });
            $('.jpoker_auto_action', auto_action_element).hide();

            $('#fold' + id).unbind('click').click(
              function() { 
                if ($('#check' + id + ':visible').length > 0) {
                  if (!confirm('You can check instead. Are you sure you want to fold?')) {
                    return;
                  }
                }
                $(this).unbind('click'); return send('Fold'); 
              }
            ).show();
            
            if(betLimit.call > 0) {
                var call = jpoker.getCallAmount(betLimit, player);
                var call_element = $('#call' + id);
                $('.jpoker_call_amount', call_element).text(jpoker.chips.SHORT(call));
                call_element.unbind('click').click(function() { $(this).unbind('click'); return send('Call'); }).show();
            } else {
                $('#check' + id).unbind('click').click(function() { $(this).unbind('click'); return send('Check'); }).show();
            }
            
            if(betLimit.allin > betLimit.call) {
                var click;
                var sliding = false;
                
                if(betLimit.max > betLimit.min) {
                    var raise = $('#raise_range' + id);
                    raise.html(jpoker.plugins.raise.getHTML(betLimit, player));
                    raise.show(); // must be visible otherwise outerWeight/outerWidth returns 0

                    var raise_input = $('#raise_input' + id);
                    raise_input.empty();
                    $('<input class=\'jpoker_raise_input\' type=\'text\'>').appendTo(raise_input).val(betLimit.min);
                    raise_input.show();

                    $('.ui-slider-1', raise).slider({
                                min: betLimit.min*100,
                                startValue: betLimit.min*100,
                                max: betLimit.max*100,
                                axis: 'horizontal',
                                step: betLimit.step*100,
                                change: function(event, ui) {
                                  var current = $('.jpoker_raise_current', ui.element);
                                  current.html(jpoker.chips.SHORT(ui.value/100.0));
                                  current.attr('title', ui.value);
                                  if (! sliding) {
                                    $('.jpoker_raise_input', raise_input).val(ui.value/100.0);
                                  }
                                },
                                slide: function(event, ui) {
                                  var current = $('.jpoker_raise_current', ui.element);
                                  current.html(jpoker.chips.SHORT(ui.value/100.0));
                                  current.attr('title', ui.value);
                                  if (! sliding) {
                                    $('.jpoker_raise_input', raise_input).val(ui.value/100.0);
                                  }
                                }
                    });

                    var slider_raise_update = function() {
                      sliding = true;
                      var value = parseFloat($('.jpoker_raise_input', raise_input).val().replace(',', '.'));
                      if (isNaN(value)) {
                          value = $('.ui-slider-1', raise).slider('value', 0);
                          $('.jpoker_raise_input', raise_input).val(value/100.0);
                      } else {
                          $('.ui-slider-1', raise).slider('value', value*100);
                      }
                      sliding = false;
                    }
                
                    $('.jpoker_raise_input', raise_input).keyup(slider_raise_update);

                    $('.jpoker_raise_input', raise_input).focus(function() {
                      this.select();
                    });


                    click = function() {
                        var server = jpoker.getServer(url);
                        if(server) {
                            var amount = parseFloat($('.jpoker_raise_input', raise_input).attr('value'), 10);
                            if (!isNaN(amount)) {
                                amount = Math.min(amount, betLimit.max);
                                amount = Math.min(amount, betLimit.allin);
                                server.sendPacket({ 'type': 'PacketPokerRaise',
                                            'serial': serial,
                                            'game_id': game_id,
                                            'amount': Math.round(amount*100)
                                            });
                            } else {
                                jpoker.error('raise with NaN amount: ' + $('.jpoker_raise_input', raise_input).attr('value'));
                            }
                        }
                    };
                    $('#allin' + id).unbind('click').click(function() {
                            var server = jpoker.getServer(url);
                            if(server) {
                                server.sendPacket({ 'type': 'PacketPokerRaise',
                                            'serial': serial,
                                            'game_id': game_id,
                                            'amount': Math.round(betLimit.allin*100)
                                            });
                            }
                        }).show();
                    if(betLimit.allin > betLimit.pot) {
                       $('#pot' + id).unbind('click').click(function() {
                            $(".jpoker_raise_input", raise_input).val(Math.floor(betLimit.pot*100)/100);
                            slider_raise_update();
                        }).show();
                       $('#halfpot' + id).unbind('click').click(function() {
                            $(".jpoker_raise_input", raise_input).val(Math.floor(betLimit.pot*100*0.5)/100);
                            slider_raise_update();
                        }).show();
                       $('#threequarterpot' + id).unbind('click').click(function() {
                            $(".jpoker_raise_input", raise_input).val(Math.floor(betLimit.pot*100*0.75)/100);
                            slider_raise_update();
                        }).show();
                    }
                } else {
                    click = function() {
                        $(this).unbind('click');
                        var server = jpoker.getServer(url);
                        var amount = Math.min(betLimit.min, betLimit.allin)*100;
                        if(server) {
                            server.sendPacket({ 'type': 'PacketPokerRaise',
                                        'serial': serial,
                                        'game_id': game_id,
                                        'amount': Math.round(amount)
                                        });
                        }
                    };
                }

                var raiseLabel = _("Bet")
                if (betLimit.call > 0 || player.bet > 0) {
                    raiseLabel = _("Raise")
                }
                $('#raise' + id).html(jpoker.plugins.playerSelf.templates.action.supplant({ action: raiseLabel })).unbind('click').click(click).show();
            }
            jpoker.plugins.playerSelf.callback.sound.in_position(server);
            $(window).focus();
            $('#game_window' + id).addClass('jpoker_self_in_position');
        },

        lostPosition: function(player, packet, id) {
            jpoker.plugins.playerSelf.hide(id);
           $('#game_window' + id).removeClass('jpoker_self_in_position');
        },

        timeout: function(player, id, packet) {
            var server = jpoker.getServer(player.url);
            switch(packet.type) {
            case 'PacketPokerTimeoutWarning':
                jpoker.plugins.playerSelf.callback.sound.timeout_warning(server);
                break;
            case 'PacketPokerTimeoutNotice':
                jpoker.plugins.playerSelf.callback.sound.timeout_notice(server);
                break;
            }
        },

        names: [ 'fold', 'call', 'check', 'raise', 'raise_range', 'raise_input', 'rebuy', 'allin', 'pot', 'halfpot', 'threequarterpot' ],

        hide: function(id) {
            for(var i = 0; i < this.names.length; i++) {
                $('#' + this.names[i] + id).hide();
            }
        },

        destroy: function(player, dummy, id) {
            jpoker.plugins.playerSelf.hide(id);
        },

        templates: {
            rebuy: '<div class=\'jpoker_rebuy_bound jpoker_rebuy_min\'>{min}</div><div class=\'ui-slider-1\'><div class=\'ui-slider-handle\'></div></div><div class=\'jpoker_rebuy_current\' title=\'{title}\'>{current}</div><div class=\'jpoker_rebuy_bound jpoker_rebuy_max\'>{max}</div><div class=\'ui-dialog-buttonpane\'><button class=\'jpoker_rebuy_action\'>{label}</button></div><div class=\'jpoker_auto_sitin\'><input name=\'jpoker_auto_sitin\' type=\'checkbox\'></input><label for=\'jpoker_auto_sitin\'>{auto_sitin_label}</label></div>',
            auto_action: '<div class=\'jpoker_auto_check_fold jpoker_auto_action\'><label for=\'auto_check_fold{id}\'>{auto_check_fold_label}</label><input type=\'checkbox\' name=\'auto_check_fold\' id=\'auto_check_fold{id}\' /></div><div class=\'jpoker_auto_check jpoker_auto_action\'><label for=\'auto_check{id}\'>{auto_check_label}</label><input type=\'checkbox\' name=\'auto_check\' id=\'auto_check{id}\' /></div><div class=\'jpoker_auto_call jpoker_auto_action\'><label for=\'auto_call{id}\'>{auto_call_label} <span class=\'jpoker_call_amount\'></span></label><input type=\'checkbox\' name=\'auto_call\' id=\'auto_call{id}\' /></div><div class=\'jpoker_auto_check_call jpoker_auto_action\'><label for=\'auto_check_call{id}\'>{auto_check_call_label}</label><input type=\'checkbox\' name=\'auto_check_call\' id=\'auto_check_call{id}\' /></div><div class=\'jpoker_auto_raise jpoker_auto_action\'><label for=\'auto_raise{id}\'>{auto_raise_label}</label><input type=\'checkbox\' name=\'auto_raise\' id=\'auto_raise{id}\' /></div>',
            hand_strength: '<span class=\'jpoker_hand_strength_label\'>{label}</span> <span class=\'jpoker_hand_strength_value\'></span>',
            action: '<div class=\'jpoker_button\'><a href=\'javascript://\'>{action}</a></div>',
            rebuy_button: '<div class=\'jpoker_rebuy\'><a href=\'javascript://\'>{rebuy}</a></div>',
            sitout: '<div class=\'jpoker_sitout\'><a href=\'javascript://\'>{sitout}</a></div>',
            sitin: '<div class=\'jpoker_sitin\'><a href=\'javascript://\'>{sitin}</a></div>'
        },

        callback: {
            sound: {
                in_position : function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSound').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_hand.swf\' />');
                    }
                },
                timeout_warning : function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSound').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_timeout_warning.swf\' />');
                    }
                },
                timeout_notice : function(server) {
                    if(server.preferences.sound) {
                        $('#jpokerSound').html('<' + jpoker.sound + ' src=\'' + jpoker.sound_directory + 'player_timeout_notice.swf\' />');
                    }
                }
            },

            hand_strength: { display_done : function() { } },
        
            table_move: function(player, packet, id) {
              if (packet.serial == player.serial) {
                var server = jQuery.jpoker.servers[player.url];
                game_id = packet.to_game_id;
                server.tableJoin(packet.to_game_id);
                jQuery.jpoker.dialog(_('Moved to table #') + packet.to_game_id);
              }
            }
        }
    };

    //
    // options (table plugin helper)
    //

    jpoker.plugins.options = {
        templates: {
            button: '<div class=\'jpoker_options\'><a href=\'javascript://\'>{options_label}</a></div>',
            dialog: '<div id=\'jpokerOptionsDialog\' class=\'jpoker_options_dialog jpoker_jquery_ui\'>{auto_muck}</div>'
        }
    };

    //
    // muck (table plugin helper)
    //

    jpoker.plugins.muck = {
        AUTO_MUCK_WIN: 1,
        AUTO_MUCK_LOSE: 2,
        templates : {
            muck_accept: '<div class=\'jpoker_muck jpoker_muck_accept\'><a href=\'javascript://\'>{muck_accept_label}</a></div>',
            muck_deny: '<div class=\'jpoker_muck jpoker_muck_deny\'><a href=\'javascript://\'>{muck_deny_label}</a></div>',
            auto_muck: '<div class=\'jpoker_auto_muck\'><div class=\'jpoker_auto_muck_win\'><input type=\'checkbox\' name=\'auto_muck_win\' id=\'auto_muck_win{id}\'></input><label for=\'auto_muck_win{id}\' title=\'{auto_muck_win_title}\'>{auto_muck_win_label}</label></div><div class=\'jpoker_auto_muck_lose\'><input type=\'checkbox\' name=\'auto_muck_lose\' id=\'auto_muck_lose{id}\'></input><label for=\'auto_muck_lose{id}\' title=\'{auto_muck_lose_title}\'>{auto_muck_lose_label}</label></div></div>'
        },
        muckRequest: function(server, packet, id) {
            if ($.inArray(server.serial, packet.muckable_serials) != -1) {
                $('#muck_accept' + id).show();
                $('#muck_deny' + id).show();
            }
        },

        muckRequestTimeout: function(id) {
            $('#muck_accept' + id).hide();
            $('#muck_deny' + id).hide();
        },
        sendAutoMuck: function(server, game_id, id) {
            var auto_muck = 0;
            if ($('#auto_muck_win' + id).is(':checked')) {
                auto_muck |= jpoker.plugins.muck.AUTO_MUCK_WIN;
            }
            if ($('#auto_muck_lose' + id).is(':checked')) {
                auto_muck |= jpoker.plugins.muck.AUTO_MUCK_LOSE;
            }
            server.sendPacket({type: 'PacketPokerAutoMuck', serial: server.serial, game_id: game_id, auto_muck: auto_muck});
            server.preferences.extend({auto_muck_win: $('#auto_muck_win' + id).is(':checked'), auto_muck_lose: $('#auto_muck_lose' + id).is(':checked')});
        }
    };

    //
    // cards (table plugin helper)
    //
    jpoker.plugins.cards = {
        update: function(cards, prefix, id) {
            jpoker.plugins.cards.update_value(cards, prefix, id);
            jpoker.plugins.cards.update_visibility(cards, prefix, id);
        },
        update_value: function(cards, prefix, id) {
            for(var i = 0; i < cards.length; i++) {
                var card = cards[i];
                var element = $('#' + prefix + i + id);
                element.removeClass().addClass('jpoker_ptable_' + prefix + i);
                if(card !== null) {
                    var card_image = 'back';
                    if(card != 255) {
                        card_image = jpoker.cards.card2string[card & 0x3F];
                    }
                    element.addClass('jpoker_card jpoker_card_' + card_image);
                }
            }
        },
        update_visibility: function(cards, prefix, id) {
            for(var i = 0; i < cards.length; i++) {
                var card = cards[i];
                var element = $('#' + prefix + i + id);
                if(card !== null) {
                    element.show();
                } else {
                    element.hide();
                }
            }
        }
    };
    //
    // chips (table plugin helper)
    //
    jpoker.plugins.chips = {
        template: '<div class=\'jpoker_chips_image\'></div><div class=\'jpoker_chips_amount\'></div>',
        update: function(chips, id) {
            var element = $(id);
            if(chips > 0) {
                element.show();
                $('.jpoker_chips_amount', element).text(jpoker.chips.SHORT(chips));
                element.attr('title', jpoker.chips.LONG(chips));
            } else {
                element.hide();
            }
        }
    };

    $.fn.getPosition = function() {
        var visible = $(this).is(':visible');
        $(this).show();
        var position = $(this).position();
        if (visible === false) {
            $(this).hide();
        }
        return position;
    };

    $.fn.getOffset = function() {
        var visible = $(this).is(':visible');
        $(this).show();
        var position = $(this).offset();
        if (visible === false) {
            $(this).hide();
        }
        return position;
    };

    $.fn.moveFrom = function(from, options) {
        var positionFrom = $(from).getPosition();
        var positionTo = $(this).getPosition();
        $(this).css(positionFrom).animate(positionTo, options);
        return this;
    };

    //
    // raise (SelfPlayer plugin helper)
    //
    jpoker.plugins.raise = {
        template: '<div class=\'jpoker_raise_label\'>{raise_label}</div><div class=\'jpoker_raise_bound jpoker_raise_min\'>{raise_min}</div><div class=\'jpoker_raise_current\' title=\'{raise_current_title}\'>{raise_current}</div><div class=\'jpoker_raise_bound jpoker_raise_max\'>{raise_max}</div><div class=\'ui-slider-1\'><div class=\'ui-slider-handle\'></div></div>',
        getHTML: function(betLimit, player) {
            var t = this.template;
            var label = _("Bet")
            if (betLimit.call > 0 || player.bet > 0) {
                label = _("Raise")
            }
            return t.supplant({raise_label: label,
                                                raise_min: jpoker.chips.SHORT(betLimit.min),
                                                raise_current_title: Math.floor(betLimit.min*100),
                                                raise_current: jpoker.chips.SHORT(betLimit.min),
                                                raise_max: jpoker.chips.SHORT(betLimit.max)});
        }
    };

    //
    // userInfo
    //
    jpoker.plugins.userInfo = function(url, options) {

        var userInfo = jpoker.plugins.userInfo;
        var opts = $.extend({}, userInfo.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_user_info\' id=\'' + id + '\'></div>');

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerPersonalInfo') {
                            $(element).html(userInfo.getHTML(packet, url));
                            $('.jpoker_user_info_submit', element).click(function() {
                                    $('.jpoker_user_info_feedback', element).text(_("Updating..."));
                                    var info = {};
                                    $('input[type=text]', element).each(function() {
                                            info[$(this).attr('name')] = $(this).attr('value');
                                        });
                                    $('input[type=password]', element).each(function() {
                                            info[$(this).attr('name')] = $(this).attr('value');
                                        });
                                    server.setPersonalInfo(info);
                                });
                            if (packet.set_account) {
                                $('.jpoker_user_info_feedback', element).text(_("Updated"));
                            }
                            var avatar_url = server.urls.avatar+'/'+server.serial;
                            var avatar_preview = $('.jpoker_user_info_avatar_preview', element);
                            avatar_preview.css({
                                    'background-image': 'url("' + avatar_url + '")',
                                    'display': 'block'
                                    });
                            $('.jpoker_user_info_avatar_upload', element).ajaxForm({
                                    beforeSubmit: function() {
                                        $('.jpoker_user_info_avatar_upload_feedback', element).text(_("Uploading..."));
                                    },
                                    success: function(data) {
                                        if (data.search('image uploaded') != -1) {
                                            $('.jpoker_user_info_avatar_upload_feedback', element).text(_("Uploaded"));
                                            $('.jpoker_user_info_avatar_preview', element).replaceWith(avatar_preview.clone().css({'background-image': 'url("' + avatar_url + '")',
                                  'display': 'block'}));
                                        } else {
                                            $('.jpoker_user_info_avatar_upload_feedback', element).text(_("Uploading failed") + ': ' + data);
                                        }
                                    }
                                });
                            userInfo.callback.display_done(element);
                        }
                        return true;
                    } else {
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'userInfo ' + id);
                server.getPersonalInfo();

                return this;
            });
    };

    jpoker.plugins.userInfo.defaults = $.extend({
        }, jpoker.defaults);

    jpoker.plugins.userInfo.getHTML = function(packet, url) {
        var t = this.templates;
        var html = [];
        html.push(t.info.supplant($.extend({
                    'name_title': _("Login name"),
                    'password_title': _("Password"),
                    'password_confirmation_title': _("Password confirmation"),
                    'email_title': _("Email"),
                    'phone_title' : _("Phone Number"),
                    'firstname_title': _("First name"),
                    'lastname_title': _("Last name"),
                    'addr_street_title' : _("Street"),
                    'addr_street2_title' : _("Street (continue)"),
                    'addr_zip_title' : _("Zip code"),
                    'addr_town_title' : _("Town"),
                    'addr_state_title' : _("State"),
                    'addr_country_title' : _("Country"),
                    'gender_title' : _("Gender"),
                    'birthdate_title' : _("Birthdate"),
                    'submit_title': _("Update personal info")
                }, packet)));
        var server = jpoker.getServer(url);
        html.push(t.avatar.supplant({'upload_url' : server.urls.upload,
                                     'upload': _("Upload avatar")}));
        return html.join('\n');
    };

    jpoker.plugins.userInfo.templates = {
        info: '<table><tr><td>{name_title}</td><td><div class=\'jpoker_user_info_name\'>{name}</div></input></td></tr><tr><td>{password_title}</td><td><input type=\'password\' name=\'password\' value=\'{password}\'></input></td></tr><tr><td>{password_confirmation_title}</td><td><input type=\'password\' name=\'password_confirmation\'></input></td></tr><tr><td>{email_title}</td><td><input type=\'text\' name=\'email\' value=\'{email}\'></input></td></tr><tr><td>{phone_title}</td><td><input type=\'text\' name=\'phone\' value=\'{phone}\'></input></td></tr><tr><td>{firstname_title}</td><td><input type=\'text\' name=\'firstname\' value=\'{firstname}\'></input></td></tr><tr><td>{lastname_title}</td><td><input type=\'text\' name=\'lastname\' value=\'{lastname}\'></input></td></tr><tr><td>{addr_street_title}</td><td><input type=\'text\' name=\'addr_street\' value=\'{addr_street}\'></input></td></tr><tr><td>{addr_street2_title}</td><td><input type=\'text\' name=\'addr_street2\' value=\'{addr_street2}\'></input></td></tr><tr><td>{addr_zip_title}</td><td><input type=\'text\' name=\'addr_zip\' value=\'{addr_zip}\'></input></td></tr><tr><td>{addr_town_title}</td><td><input type=\'text\' name=\'addr_town\' value=\'{addr_town}\'></input></td></tr><tr><td>{addr_state_title}</td><td><input type=\'text\' name=\'addr_state\' value=\'{addr_state}\'></input></td></tr><tr><td>{addr_country_title}</td><td><input type=\'text\' name=\'addr_country\' value=\'{addr_country}\'></input></td></tr><tr><td>{gender_title}</td><td><input type=\'text\' name=\'gender\' value=\'{gender}\'></input></td></tr><tr><td>{birthdate_title}</td><td><input type=\'text\' name=\'birthdate\' value=\'{birthdate}\'></input></td></tr><tr><td><input class=\'jpoker_user_info_submit\' type=\'submit\' value=\'{submit_title}\'></input></td><td><div class=\'jpoker_user_info_feedback\'></div></td></tr></table>',
        avatar: '<div class=\'jpoker_user_info_avatar_preview\'></div><form class=\'jpoker_user_info_avatar_upload\' action=\'{upload_url}\' method=\'post\' enctype=\'multipart/form-data\'><input type=\'file\' name=\'filename\'></input><input type=\'submit\' value=\'{upload}\'></input></form><div class=\'jpoker_user_info_avatar_upload_feedback\'></div>'
    };

    jpoker.plugins.userInfo.callback = {
        display_done: function(element) {
        }
    };

    //
    // places
    //
    jpoker.plugins.places = function(url, options) {

        var places = jpoker.plugins.places;
        var opts = $.extend({}, places.defaults, options);
        var server = jpoker.url2server({ url: url });

        var player_serial = server.serial;
        if (opts.serial !== undefined) {
            player_serial = parseInt(opts.serial, 10);
        }

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_places\' id=\'' + id + '\'></div>');

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerPlayerPlaces') {
                            $(element).html(places.getHTML(packet, opts.table_link_pattern, opts.tourney_link_pattern));
                            if(opts.table_link_pattern === undefined) {
                                $.each(packet.tables, function(i, table) {
                                        $('#' + table, element).click(function() {
                                                var server = jpoker.getServer(url);
                                                if(server) {
                                                    server.tableJoin(table);
                                                }
                                            });
                                    });
                            }
                            if(opts.tourney_link_pattern === undefined) {
                                $.each(packet.tourneys, function(i, tourney) {
                                        $('#' + tourney, element).click(function() {
                                                var server = jpoker.getServer(url);
                                                if(server) {
                                                    var packet = {game_id: tourney, name: ''};
                                                    server.placeTourneyRowClick(server, packet);
                                                }
                                            });
                                    });
                            }
                            places.callback.display_done(element);
                        }
                        return true;
                    } else {
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'places ' + id);
                server.getPlayerPlaces(player_serial);

                return this;
            });
    };

    jpoker.plugins.places.defaults = $.extend({
        }, jpoker.defaults);

    jpoker.plugins.places.getHTML = function(packet, table_link_pattern, tourney_link_pattern) {
        var t = this.templates;
        var html = [];
        html.push(t.tables.header.supplant({table_title: _("Tables")}));
        $.each(packet.tables, function(i, table) {
                var game_id = table;
                if (table_link_pattern) {
                    table = t.tables.link.supplant({link: table_link_pattern.supplant({game_id: game_id}), name: game_id});
                }
                html.push(t.tables.rows.supplant({id: game_id,
                                table: table}));
            });
        html.push(t.tables.footer);

        html.push(t.tourneys.header.supplant({tourney_title: _("Tourneys")}));
        $.each(packet.tourneys, function(i, tourney) {
                var tourney_serial = tourney;
                if (tourney_link_pattern) {
                    tourney = t.tourneys.link.supplant({link: tourney_link_pattern.supplant({tourney_serial: tourney_serial}), name: tourney_serial});
                }
                html.push(t.tourneys.rows.supplant({id: tourney_serial,
                                tourney: tourney}));
            });
        html.push(t.tourneys.footer);
        return html.join('\n');
    };

    jpoker.plugins.places.templates = {
        tables : {
            header : '<div class=\'jpoker_places_tables\'><table><thead><tr><th>{table_title}</th></tr></thead><tbody>',
            rows : '<tr class=\'jpoker_places_table\' id={id}><td>{table}</td></tr>',
            footer : '</tbody></table></div>',
            link: '<a href=\'{link}\'>{name}</a>'
        },
        tourneys : {
            header : '<div class=\'jpoker_places_tourneys\'><table><thead><tr><th>{tourney_title}</th></tr></thead><tbody>',
            rows : '<tr class=\'jpoker_places_tourney\' id={id}><td>{tourney}</td></tr>',
            footer : '</tbody></table></div>',
            link: '<a href=\'{link}\'>{name}</a>'
        }
    };

    jpoker.plugins.places.callback = {
        display_done: function(element) {
        }
    };

    //
    // playerLookup
    //
    jpoker.plugins.playerLookup = function(url, options) {

        var playerLookup = jpoker.plugins.playerLookup;
        var opts = $.extend({}, playerLookup.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();
                var player_lookup_element = $('<div class=\'jpoker_widget jpoker_player_lookup\' id=\'' + id + '\'></div>').appendTo($this);

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet) {
                            if (packet.type == 'PacketPokerPlayerPlaces') {
                                $('.jpoker_player_lookup_result', element).html(playerLookup.getHTML(packet, opts.table_link_pattern, opts.tourney_link_pattern));
                                if (opts.table_link_pattern === undefined) {
                                    $.each(packet.tables, function(i, table) {
                                            $('#' + table, element).click(function() {
                                                    var server = jpoker.getServer(url);
                                                    if(server) {
                                                        server.tableJoin(table);
                                                    }
                                                });
                                        });
                                }
                                if (opts.tourney_link_pattern === undefined) {
                                    $.each(packet.tourneys, function(i, tourney) {
                                            $('#' + tourney, element).click(function() {
                                                    var server = jpoker.getServer(url);
                                                    if(server) {
                                                        var packet = {game_id: tourney, name: ''};
                                                        server.placeTourneyRowClick(server, packet);
                                                    }
                                                });
                                        });
                                }
                                $('.jpoker_player_lookup_challenge a', element).click(function() {
                                        var server = jpoker.getServer(url);
                                        if(server) {
                                            if(server.loggedIn()) {
                                                server.placeChallengeClick(server, packet.serial);
                                            } else {
                                                jpoker.dialog(_("you must login before you can challenge the player"));
                                            }
                                        }
                                    });
                                playerLookup.callback.display_done(element);
                            } else if ((packet.type == 'PacketError') && (packet.other_type == jpoker.packetName2Type.PACKET_POKER_PLAYER_PLACES)) {
                                playerLookup.callback.error(packet);
                            }
                        }
                        return true;
                    } else {
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'playerLookup ' + id);

                $(player_lookup_element).html(playerLookup.getHTMLForm());
                $('.jpoker_player_lookup_submit', player_lookup_element).click(function() {
                        $('.jpoker_player_lookup_result', player_lookup_element).empty();
                        server.getPlayerPlacesByName($('.jpoker_player_lookup_input', player_lookup_element).val(), options);
                    });
                return this;
            });
    };

    jpoker.plugins.playerLookup.defaults = $.extend({
        }, jpoker.defaults);

    jpoker.plugins.playerLookup.getHTML = function(packet, table_link_pattern, tourney_link_pattern) {
        var t = this.templates;
        var html = [];
        html.push(t.tables.header.supplant({table_title: _("Tables")}));
        $.each(packet.tables, function(i, table) {
                var game_id = table;
                if (table_link_pattern) {
                    table = t.tables.link.supplant({link: table_link_pattern.supplant({game_id: game_id}), name: game_id});
                }
                html.push(t.tables.rows.supplant({id: game_id,
                                table: table}));
            });
        html.push(t.tables.footer);

        html.push(t.tourneys.header.supplant({tourney_title: _("Tourneys")}));
        $.each(packet.tourneys, function(i, tourney) {
                var tourney_serial = tourney;
                if (tourney_link_pattern) {
                    tourney = t.tourneys.link.supplant({link: tourney_link_pattern.supplant({tourney_serial: tourney_serial}), name: tourney_serial});
                }
                html.push(t.tourneys.rows.supplant({id: tourney_serial,
                                tourney: tourney}));
            });
        html.push(t.tourneys.footer);
        if(packet.tourneys.length > 0 || packet.tables.length > 0) {
            html.push(t.challenge.supplant({ 'label': _("Challenge player to a heads up tournament") }));
        }
        return html.join('\n');
    };

    jpoker.plugins.playerLookup.getHTMLForm = function() {
        var t = this.templates;
        var html = [];
        html.push(t.form.supplant({player_lookup: _("Look for player")}));
        return html.join('\n');
    };

    jpoker.plugins.playerLookup.templates = {
        form : '<input class=\'jpoker_player_lookup_input\' type=\'text\'></input><input class=\'jpoker_player_lookup_submit\' type=\'submit\' value=\'{player_lookup}\'></input><div class=\'jpoker_player_lookup_result\'></div>',
        tables : {
            header : '<div class=\'jpoker_player_lookup_tables\'><table><thead><tr><th>{table_title}</th></tr></thead><tbody>',
            rows : '<tr class=\'jpoker_player_lookup_table\' id={id}><td>{table}</td></tr>',
            footer : '</tbody></table></div>',
            link: '<a href=\'{link}\'>{name}</a>'
        },
        tourneys : {
            header : '<div class=\'jpoker_player_lookup_tourneys\'><table><thead><tr><th>{tourney_title}</th></tr></thead><tbody>',
            rows : '<tr class=\'jpoker_player_lookup_tourney\' id={id}><td>{tourney}</td></tr>',
            footer : '</tbody></table></div>',
            link: '<a href=\'{link}\'>{name}</a>'
        },
        challenge: '<div class=\'jpoker_player_lookup_challenge\'><a href=\'javascript://\'>{label}</a></div>'
    };

    jpoker.plugins.playerLookup.callback = {
        error: function(packet) {
        },

        display_done: function(element) {
        }
    };

    //
    // cashier
    //
    jpoker.plugins.cashier = function(url, options) {

        var cashier = jpoker.plugins.cashier;
        var opts = $.extend({}, cashier.defaults, options);
        var server = jpoker.url2server({ url: url });

        return this.each(function() {
                var $this = $(this);

                var id = jpoker.uid();

                $this.append('<div class=\'jpoker_widget jpoker_cashier\' id=\'' + id + '\'></div>');

                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerUserInfo') {
                            $(element).html(cashier.getHTML(packet));
                            cashier.callback.display_done(element);
                        }
                        return true;
                    } else {
                        return false;
                    }
                };

                server.registerUpdate(updated, null, 'cashier ' + id);
                server.getUserInfo();

                return this;
            });
    };

    jpoker.plugins.cashier.defaults = $.extend({
        }, jpoker.defaults);

    jpoker.plugins.cashier.getHTML = function(packet) {
        var t = this.templates;
        var html = [];
        html.push(t.currencies.header.supplant({currency_serial_title: _("Currency"),
                        currency_amount_title: _("Amount"),
                        currency_ingame_title: _("In Game"),
                        currency_points_title: _("Points")
                        }));
        $.each(packet.money, function(currency_serial, money) {
                html.push(t.currencies.rows.supplant({currency_serial: currency_serial.substr(1),
                                currency_amount: money[0]/=100,
                                currency_ingame: money[1]/=100,
                                currency_points: money[2]}));
            });
        html.push(t.currencies.footer);
        return html.join('\n');
    };

    jpoker.plugins.cashier.templates = {
        currencies : {
            header : '<div class=\'jpoker_cashier_currencies\'><table><thead><tr><th>{currency_serial_title}</th><th>{currency_amount_title}</th><th>{currency_ingame_title}</th><th>{currency_points_title}</th></tr></thead><tbody>',
            rows : '<tr class=\'jpoker_cashier_currency\'><td>{currency_serial}</td><td>{currency_amount}</td><td>{currency_ingame}</td><td>{currency_points}</td></tr>',
            footer : '</tbody></table></div>'
        }
    };

    jpoker.plugins.cashier.callback = {
        display_done: function(element) {
        }
    };

    //
    // tablepicker
    //
    jpoker.plugins.tablepicker = function(url, options) {

        var server = jpoker.url2server({ url: url });
        var tablepicker = jpoker.plugins.tablepicker;
        var opts = $.extend({}, tablepicker.defaults, options, server.preferences.tablepicker);

        return this.each(function() {
                var $this = $(this);
                var id = jpoker.uid();
                var element = $('<div class=\'jpoker_widget jpoker_tablepicker\' id=\'' + id + '\'></div>').appendTo($this);
                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet) {
                            if ((packet.type == 'PacketPokerTable') &&
                                (packet.reason == 'TablePicker')) {
                                $('.jpoker_tablepicker_error', element).text('');
                                $('.jpoker_tablepicker_error', element).hide();
                            } else if((packet.type == 'PacketPokerError') &&
                                      (packet.other_type == jpoker.packetName2Type.POKER_TABLE_PICKER)) {
                                $('.jpoker_tablepicker_error', element).text(packet.message);
                                $('.jpoker_tablepicker_error', element).show();
                            }
                        }
                        return true;
                    } else {
                        return false;
                    }
                };
                var getOptions = function() {
                    return {variant: $('input[name=variant].jpoker_tablepicker_option', element).val(),
                            betting_structure: $('input[name=betting_structure].jpoker_tablepicker_option ', element).val(),
                            currency_serial: $('input[name=currency_serial].jpoker_tablepicker_option', element).val()
                    };
                };
                opts.id = id;
                $(element).html(jpoker.plugins.tablepicker.template.supplant(opts));
                $('.jpoker_tablepicker_options', element).hide();
                $('.jpoker_tablepicker_error', element).hide();
                $('.jpoker_tablepicker_show_options', element).click(function() {
                        $('.jpoker_tablepicker_options', element).toggle();
                    });
                $('.jpoker_tablepicker_option', element).change(function() {
                        server.preferences.extend({tablepicker: getOptions()});
                    });

                $('.jpoker_tablepicker_submit', element).click(function() {
                        server.tablePick(getOptions());
                    });
                server.registerUpdate(updated, null, 'tablepicker ' + id);
                return this;
            });
    };

    jpoker.plugins.tablepicker.defaults = $.extend({
            variant: '',
            betting_structure: '',
            currency_serial: 0,
            submit_label: _("Play now"),
            show_options_label: _("Toggle options"),
            submit_title: _("Click here to automatically pick a table"),
            variant_label: _("Variant"),
            betting_structure_label: _("Betting structure"),
            currency_serial_label: _("Currency serial")
        }, jpoker.defaults);

    jpoker.plugins.tablepicker.template = '<input class=\'jpoker_tablepicker_submit\' type=\'submit\' value=\'{submit_label}\' title=\'{submit_title}\' /><a class=\'jpoker_tablepicker_show_options\' href=\'javascript://\'>{show_options_label}</a><div class=\'jpoker_tablepicker_options\'><label for=\'jpoker_tablepicker_option_variant{id}\'>{variant_label}</label><input class=\'jpoker_tablepicker_option\' type=\'text\' name=\'variant\' value=\'{variant}\' id=\'jpoker_tablepicker_option_variant{id}\'/><label for=\'jpoker_tablepicker_option_betting_structure{id}\'>{betting_structure_label}</label><input class=\'jpoker_tablepicker_option\' type=\'text\' name=\'betting_structure\' value=\'{betting_structure}\' id=\'jpoker_tablepicker_option_betting_structure{id}\'/><label for=\'jpoker_tablepicker_option_current_serial{id}\'>{currency_serial_label}</label><input class=\'jpoker_tablepicker_option\'type=\'text\' name=\'currency_serial\' value=\'{currency_serial}\' id=\'jpoker_tablepicker_option_current_serial{id}\'/></div><div class=\'jpoker_tablepicker_error\'></div>';

    //
    // signup
    //
    jpoker.plugins.signup = function(url, options) {

        var server = jpoker.url2server({ url: url });
        var signup = jpoker.plugins.signup;
        var opts = $.extend({}, signup.defaults, options, server.preferences.signup);

        return this.each(function() {
                var $this = $(this);
                var id = jpoker.uid();
                var element = $('<div class=\'jpoker_widget jpoker_signup jpoker_jquery_ui\' id=\'' + id + '\'></div>').appendTo($this);
                var updated = function(server, what, packet) {
                    var element = document.getElementById(id);
                    if(element) {
                        if(packet && packet.type == 'PacketPokerPersonalInfo') {
                            $(element).dialog('close');
                            return false;
                        }
                        return true;
                    } else {
                        return false;
                    }
                };
                opts.id = id;
                $(element).html(jpoker.plugins.signup.template.supplant({
                            login_label: _("Login name"),
                                password_label: _("Password"),
                                password_confirmation_label: _("Password confirmation"),
                                email_label: _("Email address"),
                                submit_label: _("Register")
                                }));

                $('input[type=submit]', element).click(function() {
                        var options = {
                            name: $('input[name=login]', element).val(),
                            password: $('input[name=password]', element).val(),
                            password_confirmation: $('input[name=password_confirmation]', element).val(),
                            email: $('input[name=email]', element).val()
                        };
                        // server.createAccount(options);
                    });
                server.registerUpdate(updated, null, 'signup ' + id);
                $(element).dialog(opts.dialog);
                return this;
            });
    };

    jpoker.plugins.signup.defaults = $.extend({
            dialog: {
                resizable: false,
                draggable: false,
                modal: true,
                width: '400px',
                height: '300px'
            }
        }, jpoker.defaults);

    jpoker.plugins.signup.template = '<div class=\'jpoker_signup_content\'><dl><dt><label for=\'jpoker_signup_login{id}\'>{login_label}</label></dt><dd><input name=\'login\' type=\'text\' id=\'jpoker_signup_login{id}\'/></dd><dt><label for=\'jpoker_signup_password{id}\'>{password_label}</label></dt><dd><input name=\'password\' type=\'password\' id=\'jpoker_signup_password{id}\'/></dd><dt><label for=\'jpoker_signup_password_confirmation{id}\'>{password_confirmation_label}</label></dt></dt><dd><input name=\'password_confirmation\' type=\'password\' id=\'jpoker_signup_password_confirmation{id}\'/></dd><dt><label for=\'jpoker_signup_email{id}\'>{email_label}</label></dt><dd><input name=\'email\' type=\'text\' id=\'jpoker_signup_email{id}\'/></dd></dl><input type=\'submit\' value=\'{submit_label}\'/></div>';

    //
    // user preferences
    //
    jpoker.preferences = function(hash) {
            var cookie = 'jpoker_preferences_'+hash;
            if ($.cookie(cookie)) {
                $.extend(this, JSON.parse($.cookie(cookie)));
            }
            this.extend = function(preferences) {
                $.extend(this, preferences);
                this.save();
            };
            this.save = function() {
                $.cookie(cookie, JSON.stringify(this));
            };
    };
    jpoker.preferences.prototype = {
        auto_muck_win: true,
        auto_muck_lose: true,
        auto_sitin: true,
        sound: true
    };

    jpoker.compatibility = function(msie) {
        if(msie) {
            jpoker.msie_compatibility();
        } else {
            jpoker.other_compatibility();
        }
    };

    jpoker.compatibility($.browser.msie); // no coverage

    jpoker.copyright_text = jpoker.copyright_template.supplant({ 'jpoker-sources': jpoker.jpoker_sources, 'poker-network-sources': jpoker.poker_network_sources }).supplant({ 'jpoker-version': jpoker.jpoker_version, 'poker-network-version': jpoker.poker_network_version });

})(jQuery);
