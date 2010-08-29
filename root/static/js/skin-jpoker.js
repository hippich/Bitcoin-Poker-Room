//
//     Copyright (C) 2008 Loic Dachary <loic@dachary.org>
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
$.fn.triggerKeypress = function(keyCode) {
    return this.trigger("keypress", [$.event.fix({event:"keypress", keyCode: keyCode, target: this[0]})]);
};

var ActiveXObject;
var jpoker_skin_override_xhr = function() {
if(!window.ActiveXObject) {
    window.ActiveXObject = true;
}

ActiveXObject = function(options) {
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
	if (url.indexOf('AVATAR') >= 0) {
	    this.status = 404;
	}
        //window.console.log(url);
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
            this.server.outgoing = '[]';
        }
    },

    server: {
        outgoing: '[]',
        handle: function(packet) { }
    }
};
};

explain = true;

$.jpoker.doReconnect = false;

function setUp() {
    jpoker_skin_override_xhr();
    $.jpoker.verbose = 1;

    $('.skinclean').empty();
    $('#table').empty();
    $('#text').hide();

    $('#jpoker_copyright').dialog('destroy');
    $('#jpoker_dialog').dialog('destroy').remove();
    $('.jpoker_login').remove();
    $('.jpoker_table_list').remove();
    $('.jpoker_server_status').remove();

    $.jpoker.uninit();
    //
    // disable long poll logic
    ///
    $.jpoker.serverCreate({ url: 'url', longPollFrequency: -1 });
    window.scrollTo(0,0);
}

function jpoker_01_copyright(place) {
    setUp();
    $.jpoker.copyright();
}

function jpokerLogin(place) {
        $(place).jpoker('login', config.jpoker.restURL);
}

function jpokerServerStatus(place) {
        $(place).jpoker('serverStatus', config.jpoker.restURL);
}

function jpokerTableList(place) {
        $(place).jpoker('tableList', config.jpoker.restURL);
}

function jpoker_02_join(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_02_join</b> ');
            $('#explain').append('A player just arrived at the table, he is sit out and has no money in front of him.');
            $('#explain').append('The player name can be 50 characters at most.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{"observers": 1, "name": "One", "percent_flop" : 98, "average_pot": 100, "seats": 10, "variant": "holdem", "hands_per_hour": 220, "betting_structure": "2-4-limit", "currency_serial": 1, "muck_timeout": 5, "players": 4, "waiting": 0, "skin": "default", "id": game_id, "type": "PacketPokerTable", "player_timeout": 60},
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'verylongusername' },
{ type: 'PacketPokerPlayerStats', serial: player_serial, game_id: game_id, rank: 1, percentile: 0 }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_03_joinBuyIn(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_03_joinBuyIn</b> ');
            $('#explain').append('A player arrived at the table, he is sit out he brings money at the table.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i + 1, percentile: i%4 });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money, bet: 0 });
            money *= 10;
        }

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_03_playerBet(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_03_playerBet</b> ');
            $('#explain').append('A player is sit, with money at the table, cards, and a bet.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        var bet = 80000;
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i + 1, percentile: i%4 });
            packets.push({ type: 'PacketPokerSit', serial: player_serial + i, game_id: game_id });
	    packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial + i, game_id: game_id, cards: [255,255]});
            packets.push({ type: 'PacketPokerRaise', serial: player_serial + i, game_id: game_id });
	    packets.push({"type":"PacketPokerChipsPlayer2Bet","length":15,"cookie":"","game_id":game_id,"serial":player_serial+i,"chips":[10000,2]});
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money, bet: bet });
            money *= 10;
            bet *= 10;
        }
	packets.push({ type: 'PacketPokerDealer', dealer: 0, game_id: game_id });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_03_1_playerDealt(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_03_playerDealt</b> ');
            $('#explain').append('All player are sit, dealt cards, and 5 players folded');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i + 1, percentile: i%4 });
            packets.push({ type: 'PacketPokerSit', serial: player_serial + i, game_id: game_id });
	    packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial + i, game_id: game_id, cards: [255,255]});
        }
	packets.push({ type: 'PacketPokerDealer', dealer: 0, game_id: game_id });
        for (var j = 5; j < 10; j+=1) {
	    packets.push({ type: 'PacketPokerFold', serial: player_serial + j, game_id: game_id});
	}

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_04_playerInPosition(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_04_playerInPosition</b> ');
            $('#explain').append('The player username0 is to act / is in position.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
	    packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i + 1, percentile: i%4 });
            packets.push({ type: 'PacketPokerSit', serial: player_serial + i, game_id: game_id });
	    packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial + i, game_id: game_id, cards: [255,255]});
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money, bet: 0 });
            money *= 10;
        }
        packets.push({ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_05_selfPlayer(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_05_selfPlayer</b> ');
            $('#explain').append('The logged in player is sit at the table, buy in dialog shows.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id},
{ type: 'PacketPokerBuyInLimits',
game_id: game_id,
min:   500,
max: 20000,
best:  1000,
rebuy_min: 1000
},
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerStats', serial:player_serial, game_id: game_id, rank: 1, percentile: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
	server.bankroll = function() { return 1000; };
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_05_1_selfPlayerInGame_autoActionCheck(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_05_1_selfPlayerInGame</b> ');
            $('#explain').append('The logged in player is sit at the table and in game.');
            $('#explain').append('Auto actions (with check) are displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id},
{ type: 'PacketPokerBuyInLimits',
game_id: game_id,
min:   500,
max: 20000,
best:  1000,
rebuy_min: 1000
},
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerStats', serial:player_serial, game_id: game_id, rank: 1, percentile: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 10000, bet: 0 },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerInGame', game_id: game_id, players: [player_serial] },
{ type: 'PacketPokerBetLimit',
                       game_id: game_id,
                       min:   500,
                       max: 20000,
                       step:  100,
                       call: 0,
                       allin:4000,
                       pot:  2000
        },
{ type: 'PacketPokerBeginRound', game_id: game_id }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
	server.bankroll = function() { return 1000; };
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_05_1_selfPlayerInGame_autoActionCall(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_05_1_selfPlayerInGame</b> ');
            $('#explain').append('The logged in player is sit at the table and in game.');
            $('#explain').append('Auto actions (with call) are displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id},
{ type: 'PacketPokerBuyInLimits',
game_id: game_id,
min:   500,
max: 20000,
best:  1000,
rebuy_min: 1000
},
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerStats', serial:player_serial, game_id: game_id, rank: 1, percentile: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 10000, bet: 0 },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerInGame', game_id: game_id, players: [player_serial] },
{ type: 'PacketPokerBetLimit',
                       game_id: game_id,
                       min:   500,
                       max: 20000,
                       step:  100,
                       call: 1000,
                       allin:4000,
                       pot:  2000
        },
{ type: 'PacketPokerBeginRound', game_id: game_id }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
	server.bankroll = function() { return 1000; };
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_06_selfInPosition(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_06_selfInPosition</b> ');
            $('#explain').append('The logged in player is in position.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerStats', serial:player_serial, game_id: game_id, rank: 1, percentile: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 1000000, bet: 0 },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerPlayerCards', serial: player_serial, game_id: game_id, cards: [32, 33]},
{ type: 'PacketPokerBetLimit',
                       game_id: game_id,
                       min:   50000,
                       max: 2000000,
                       step:  10000,
                       call: 100000,
                       allin:400000,
                       pot:  200000
},
{ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSelfInPosition', serial: player_serial, game_id: game_id },
{ type: 'one' },
{ type: 'two' },
{ type: 'three' }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
        server.registerHandler(0, function(server, dummy, packet) {
                if(packet.type == 'two') {
                } else if(packet.type == 'three') {
                    server.notifyUpdate();
                    return false;
                }
                return true;
            });
        
}

function jpoker_06_1_selfInPositionCheck(place) {
        setUp();
        if(explain) {
            $(place).append('<b>jpoker_06_1_selfInPositionCheck</b> ');
            $(place).append('The logged in player is in position, and is offered to check.');
            $(place).append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerStats', serial:player_serial, game_id: game_id, rank: 1, percentile: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 1000000, bet: 0 },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerPlayerCards', serial: player_serial, game_id: game_id, cards: [32, 33]},
{ type: 'PacketPokerBetLimit',
                       game_id: game_id,
                       min:   500,
                       max: 20000,
                       step:  100,
                       call: 0,
                       allin:4000,
                       pot:  2000
},
{ type: 'PacketPokerSelfInPosition', serial: player_serial, game_id: game_id },
{ type: 'one' },
{ type: 'two' },
{ type: 'three' }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
        server.registerHandler(0, function(server, dummy, packet) {
                if(packet.type == 'two') {
                } else if(packet.type == 'three') {
                    server.notifyUpdate();
                    return false;
                }
                return true;
            });
        
}

function jpoker_07_joining(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_07_joining</b> ');
            $('#explain').append('A request to join the table was sent to the poker server and the HTML element where the table is going to be displayed has been created, with a message showing the table description is expected to arrive from the server.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        $(place).jpoker('table', 'url', game_id, 'ONE');
}

function jpoker_08_all(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_08_all</b> ');
            $('#explain').append('All community cards and all pots are displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        var bet = 8;
	packets.push({ type: 'PacketSerial', serial: player_serial });
        for(var i = 0; i < 10; i++) {
	    packets.push({ type: 'PacketPokerDealer', dealer: i, game_id: game_id });
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
	    packets.push({"type":"PacketPokerChipsPlayer2Bet","length":15,"cookie":"","game_id":game_id,"serial":player_serial+i,"chips":[10000,2]});
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial + i, game_id: game_id, cards: [ 6, 7 ] });
	    packets.push({ type: 'PacketPokerCheck', serial: player_serial + i, game_id: game_id });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i, percentile: i%4 });
            bet *= 10;
            money *= 10;
        }
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3] });
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3, 4] });
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3, 4, 5] });
        for(var j = 0; j < 9; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100000], game_id: game_id });
	    packets.push({ type: 'PacketPokerChipsBet2Pot', pot: j, game_id: game_id, serial: player_serial + j });
        }
	for(var k = 0; k < 10; k++) {	    
	    packets.push({"besthand":1,"hand":"Flush Queen high","length":47,"cookie":"","board":[1,2,3,4,5],"bestcards":[2,3,4,5,7],"cards":[6,7],"game_id":game_id,"serial":player_serial+k,"type":"PacketPokerBestCards","side":""});
	}
	for(var l = 0; l < 10; l++) {	    
	    packets.push({"type":"PacketPokerChipsPot2Player","pot":l,"length":21,"reason":"win","game_id":game_id,"serial":player_serial+l,"chips":[100,8,200,5,500,2]});
	}
	packets.push({ type: 'PacketPokerPlayerHandStrength', game_id: game_id, serial: player_serial, hand: 'Hand strength: High card Ten: Ts, 9d, 4h, 3d, 2s' });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_08_1_all_cardback(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_08_all</b> ');
            $('#explain').append('All players cards but faceback.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        var bet = 8;
	packets.push({ type: 'PacketPokerDealer', dealer: 0, game_id: game_id });
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
	    packets.push({"type":"PacketPokerChipsPlayer2Bet","length":15,"cookie":"","game_id":game_id,"serial":player_serial+i,"chips":[10000,2]});
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial + i, game_id: game_id, cards: [ 255, 255 ] });
	    packets.push({ type: 'PacketPokerCheck', serial: player_serial + i, game_id: game_id });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i, percentile: i%4 });
            bet *= 10;
            money *= 10;
        }

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_08_2_allin(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_08_all</b> ');
            $('#explain').append('All players are allin.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 0;
        var bet = 8;
	packets.push({ type: 'PacketPokerDealer', dealer: 0, game_id: game_id });
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerSit', serial: player_serial + i, game_id: game_id });
            packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial + i, game_id: game_id, cards: [ 255, 255 ] });
	    packets.push({ type: 'PacketPokerRaise', serial: player_serial + i, game_id: game_id });
	    packets.push({"type":"PacketPokerChipsPlayer2Bet","length":15,"cookie":"","game_id":game_id,"serial":player_serial+i,"chips":[10000,2]});
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
        }

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_09_dialog(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_09_dialog</b> ');
            $('#explain').append('Dialog box used for various game messages and notifications.');
            $('#explain').append('<hr>');
        }

        $.jpoker.dialog('Dialog box used for various game messages and notifications.');
}

function jpoker_10_selfMuck(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_10_selfMuck</b> ');
            $('#explain').append('The logged in player is sit at the table, if muck checkbox are unchecked, muck button will be shown.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id},
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 10000, bet: 0 },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerBetLimit',
                       game_id: game_id,
                       min:   500,
                       max: 20000,
                       step:  100,
                       call: 1000,
                       allin:4000,
                       pot:  2000
},
{ type: 'PacketPokerMuckRequest', serial: player_serial, game_id: game_id, muckable_serials: [player_serial] }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
        server.preferences.auto_muck_win = false;
        server.preferences.auto_muck_lose = false;
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_11_avatarHover(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_11_avatarHover</b> ');
            $('#explain').append('Hovering the avatar show a border around the image by default.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerSit', serial: player_serial + i, game_id: game_id });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money, bet: 0 });
            money *= 10;
        }
        packets.push({ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
	server.getPlayerPlaces = function(serial) {
	    server.notifyUpdate({type: 'PacketPokerPlayerPlaces', serial: serial, tables: [11, 12, 13], tourneys: [21, 22]});
	};
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_12_selfRebuy(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_12_selfRebuy</b> ');
            $('#explain').append('player has less than betlimit money he is able to rebuy.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
		       { type: 'PacketSerial', serial: player_serial },
		       { type: 'PacketPokerTable', id: game_id },
		       { type: 'PacketPokerBuyInLimits',
			 game_id: game_id,
			 min:   500,
			 max: 20000,
			 best:  1000,
			 rebuy_min: 1000
		       },
		       { type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
		       { type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 100, bet: 0 },
		       { type: 'PacketPokerSit', serial: player_serial, game_id: game_id }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
	
	var server = $.jpoker.getServer('url');
	server.bankroll = function() { return 1000; };
	server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}


function jpoker_20_login(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_20_login</b> ');
            $('#explain').append('Player is logged out.');
            $('#explain').append('<hr>');
        }

        $(place).jpoker('login', 'url');
        $("#name", place).attr('value', 'username');
        $("#password", place).attr('value', 'randompassword');
}

function jpoker_21_loginProgress(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_21_loginProgress</b> ');
            $('#explain').append('Login request was sent, waiting for answer.');
            $('#explain').append('<hr>');
        }

        var server = $.jpoker.getServer('url');

        $(place).jpoker('login', 'url');
        $(".jpoker_login_name", place).attr('value', 'username');
        $(".jpoker_login_password", place).attr('value', 'randompassword');
        server.login = function() {};
        $(".jpoker_login", place).triggerKeypress("13");

        
}

function jpoker_22_logout(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_22_logout</b> ');
            $('#explain').append('User is logged in, one choice only : logout.');
            $('#explain').append('<hr>');
        }

        var server = $.jpoker.getServer('url');
        server.serial = 1;

        $(place).jpoker('login', 'url');
}

function jpoker_30_statusDisconnected(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_30_statusDisconnected</b> ');
            $('#explain').append('disconnected from server.');
            $('#explain').append('<hr>');
        }

        $(place).jpoker('serverStatus', 'url');
}

function jpoker_31_connectedTables(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_31_connectedTables</b> ');
            $('#explain').append('connected to server, with tables and no players.');
            $('#explain').append('<hr>');
        }

        var server = $.jpoker.getServer('url');

        server.connectionState = 'connected';
        server.tablesCount = 10;
        $(place).jpoker('serverStatus', 'url');
}

function jpoker_32_connectedTablesPlayers(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_32_connectedTablesPlayers</b> ');
            $('#explain').append('connected to server, with tables and players.');
            $('#explain').append('<hr>');
        }

        var server = $.jpoker.getServer('url');

        server.connectionState = 'connected';
        server.tablesCount = 10;
        server.playersCount = 23;
        $(place).jpoker('serverStatus', 'url');
}

function jpoker_33_connectedAll(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_32_connectedAll</b> ');
            $('#explain').append('connected to server, with cash game tables with players and tournaments with players.');
            $('#explain').append('<hr>');
        }

        var server = $.jpoker.getServer('url');

        server.connectionState = 'connected';
        server.tablesCount = 10;
        server.tourneysCount = 20;
        server.playersCount = 33;
        server.playersTourneysCount = 43;
        $(place).jpoker('serverStatus', 'url');
}

function jpoker_40_tableList(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_40_tableList</b> ');
            $('#explain').append('List of poker tables available on the server.');
            $('#explain').append('<hr>');
        }

        var packets = [ {"players": 4, "type": "PacketPokerTableList", "packets": [{"observers": 1, "name": "One", "percent_flop" : 98, "average_pot": 100, "seats": 10, "variant": "holdem", "hands_per_hour": 220, "betting_structure": "2-4-limit", "currency_serial": 1, "muck_timeout": 5, "players": 4, "waiting": 0, "skin": "default", "id": 100, "type": "PacketPokerTable", "player_timeout": 60}, {"observers": 0, "name": "Two", "percent_flop": 0, "average_pot": 0, "seats": 10, "variant": "holdem", "hands_per_hour": 0, "betting_structure": "10-20-limit", "currency_serial": 1, "muck_timeout": 5, "players": 0, "waiting": 0, "skin": "default", "id": 101,"type": "PacketPokerTable", "player_timeout": 60}, {"observers": 0, "name": "Three", "percent_flop": 0, "average_pot": 0, "seats": 10, "variant": "holdem", "hands_per_hour": 0, "betting_structure": "10-20-pot-limit", "currency_serial": 1, "muck_timeout": 5, "players": 0, "waiting": 0, "skin": "default", "id": 102,"type": "PacketPokerTable", "player_timeout": 60}]} ];

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('tableList', 'url');
}

function jpoker_41_regularTourneyList(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_41_regularTourneyList</b> ');
            $('#explain').append('List of poker regular tourney available on the server.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [{"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 1", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "registering", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 789}, {"players_quota": 2000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 2", "start_time": 1216201025, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "announced", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 3000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 3", "start_time": 1216201026, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 4000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 4", "start_time": 1216201027, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"}];

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('regularTourneyList', 'url');
}

function jpoker_42_sitngoTourneyList(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_42_sitngoTourneyList</b> ');
            $('#explain').append('List of poker regular tourney available on the server.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [{"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem 1", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 100000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 1}, {"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem 2", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 1", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "registering", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 789}, {"players_quota": 2000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 2", "start_time": 1216201025, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 3000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 3", "start_time": 1216201026, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 4000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 4", "start_time": 1216201027, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"}];

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('sitngoTourneyList', 'url');
}

function jpoker_43_tableListWithLink(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_43_tableListWithLink</b> ');
            $('#explain').append('List of poker tables available on the server, with html link on name');
            $('#explain').append('<hr>');
        }

        var packets = [ {"players": 4, "type": "PacketPokerTableList", "packets": [{"observers": 1, "name": "One", "percent_flop" : 98, "average_pot": 100, "seats": 10, "variant": "holdem", "hands_per_hour": 220, "betting_structure": "2-4-limit", "currency_serial": 1, "muck_timeout": 5, "players": 4, "waiting": 0, "skin": "default", "id": 100, "type": "PacketPokerTable", "player_timeout": 60}, {"observers": 0, "name": "Two", "percent_flop": 0, "average_pot": 0, "seats": 10, "variant": "holdem", "hands_per_hour": 0, "betting_structure": "10-20-limit", "currency_serial": 1, "muck_timeout": 5, "players": 0, "waiting": 0, "skin": "default", "id": 101,"type": "PacketPokerTable", "player_timeout": 60}, {"observers": 0, "name": "Three", "percent_flop": 0, "average_pot": 0, "seats": 10, "variant": "holdem", "hands_per_hour": 0, "betting_structure": "10-20-pot-limit", "currency_serial": 1, "muck_timeout": 5, "players": 0, "waiting": 0, "skin": "default", "id": 102,"type": "PacketPokerTable", "player_timeout": 60}]} ];

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('tableList', 'url', {link_pattern: 'http://foo/table/game_id={game_id}'});
}

function jpoker_44_regularTourneyListWithLink(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_44_regularTourneyListWithLink</b> ');
            $('#explain').append('List of poker regular tourney available on the server, with html link on description.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [{"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 1", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "registering", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 789}, {"players_quota": 2000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 2", "start_time": 1216201025, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 3000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 3", "start_time": 1216201026, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 4000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 4", "start_time": 1216201027, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"}];

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('regularTourneyList', 'url', {link_pattern: 'http://foo/tourney/tourney_serial={tourney_serial}'});
}

function jpoker_45_sitngoTourneyListWithLink(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_45_sitngoTourneyListWithLink</b> ');
            $('#explain').append('List of poker regular tourney available on the server, with html link on description.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [{"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem 1", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 100000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 1}, {"players_quota": 2, "breaks_first": 7200, "name": "sitngo2", "description_short" : "Sit and Go 2 players, Holdem 2", "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0}, {"players_quota": 1000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 1", "start_time": 1216201024, "breaks_interval" : 60, "variant": "holdem", "currency_serial": 1, "state": "registering", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 39, "sit_n_go": "n", "registered": 789}, {"players_quota": 2000, "breaks_first" : 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 2", "start_time": 1216201025, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 40, "sit_n_go": "n", "registered": 0}, {"players_quota": 3000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 3", "start_time": 1216201026, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial" : 41, "sit_n_go": "n", "registered": 0}, {"players_quota": 4000, "breaks_first": 7200, "name": "regular1", "description_short": "Holdem No Limit Freeroll 4", "start_time": 1216201027, "breaks_interval": 60, "variant": "holdem", "currency_serial": 1, "state": "canceled", "buy_in": 0, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 42, "sit_n_go": "n", "registered": 0}], "tourneys": 5, "type": "PacketPokerTourneyList"}];

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('sitngoTourneyList', 'url', {link_pattern: 'http://foo/tourney/tourney_serial={tourney_serial}'});
}

function jpoker_46_tableListWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_46_tableListWithPager</b> ');
            $('#explain').append('List of poker tables available on the server.');
            $('#explain').append('<hr>');
        }

        var packets = [ {"players": 4, "type": "PacketPokerTableList", "packets": []} ];
	for (var i = 0; i < 200; ++i) {
	    var name = "Table" + i;
	    var id = 100+i;
	    var players = i%11;
	    var packet = {"observers": 0, "name": name, "percent_flop": 0, "average_pot": 0, "seats": 10, "variant": "holdem", "hands_per_hour": 0, "betting_structure": "10-20-limit", "currency_serial": 1, "muck_timeout": 5, "players": players, "waiting": 0, "skin": "default", "id": id,"type": "PacketPokerTable", "player_timeout": 60};
	    packets[0].packets.push(packet);
	}

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('tableList', 'url');
}

function jpoker_47_regularTourneyListWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_47_regularTourneyListWithPager</b> ');
            $('#explain').append('List of poker tables available on the server.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"}];
	for (var i = 0; i < 200; ++i) {
	    var name = "Tourney" + i;
	    var players = i%11;
	    var packet = {"players_quota": players, "breaks_first": 7200, "name": name, "description_short" : name, "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "n", "registered": 0};
	    packets[0].packets.push(packet);
	}

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('regularTourneyList', 'url');
}

function jpoker_48_sitngoTourneyListWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_48_sitngoTourneyListWithPager</b> ');
            $('#explain').append('List of poker tables available on the server.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"}];
	for (var i = 0; i < 200; ++i) {
	    var name = "Tourney" + i;
	    var players = i%11;
	    var packet = {"players_quota": players, "breaks_first": 7200, "name": name, "description_short" : name, "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0};
	    packets[0].packets.push(packet);
	}

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('sitngoTourneyList', 'url');
}

function jpoker_49_tableListWithPagerWithLinks(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_49_tableListWithPagerWithLinks</b> ');
            $('#explain').append('List of poker tables available on the server.');
            $('#explain').append('<hr>');
        }

        var packets = [ {"players": 4, "type": "PacketPokerTableList", "packets": []} ];
	for (var i = 0; i < 200; ++i) {
	    var name = "Table" + i;
	    var id = 100+i;
	    var players = i%11;
	    var packet = {"observers": 0, "name": name, "percent_flop": 0, "average_pot": 0, "seats": 10, "variant": "holdem", "hands_per_hour": 0, "betting_structure": "10-20-limit", "currency_serial": 1, "muck_timeout": 5, "players": players, "waiting": 0, "skin": "default", "id": id,"type": "PacketPokerTable", "player_timeout": 60};
	    packets[0].packets.push(packet);
	}

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('tableList', 'url', {link_pattern: 'http://foo/table/game_id={game_id}'});
}

function jpoker_49_1_regularTourneyListWithPagerWithLinks(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_49_1_regularTourneyListWithPagerWithLinks</b> ');
            $('#explain').append('List of poker regular tourneys available on the server.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"}];
	for (var i = 0; i < 200; ++i) {
	    var name = "Tourney" + i;
	    var players = i%11;
	    var packet = {"players_quota": players, "breaks_first": 7200, "name": name, "description_short" : name, "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "n", "registered": 0};
	    packets[0].packets.push(packet);
	}

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('regularTourneyList', 'url', {link_pattern: 'http://foo/tourney/tourney_serial={tourney_serial}'});
}

function jpoker_49_2_sitngoTourneyListWithPagerWithLinks(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_49_2_sitngoTourneyListWithPagerWithLinks</b> ');
            $('#explain').append('List of poker sitngo tourneys available on the server.');
            $('#explain').append('<hr>');
        }

	var packets = [{"players": 0, "packets": [], "tourneys": 5, "type": "PacketPokerTourneyList"}];
	for (var i = 0; i < 200; ++i) {
	    var name = "Tourney" + i;
	    var players = i%11;
	    var packet = {"players_quota": players, "breaks_first": 7200, "name": name, "description_short" : name, "start_time": 0, "breaks_interval": 3600, "variant": "holdem", "currency_serial" : 1, "state": "registering", "buy_in": 300000, "type": "PacketPokerTourney", "breaks_duration": 300, "serial": 1, "sit_n_go": "y", "registered": 0};
	    packets[0].packets.push(packet);
	}

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');

        $(place).jpoker('sitngoTourneyList', 'url', {link_pattern: 'http://foo/tourney/tourney_serial={tourney_serial}'});
}

function jpoker_50_sitOut(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_50_sitOut</b> ');
            $('#explain').append('A player is sit out, meaning he occupies a site but does not participate in the game.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER' },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 200, bet: 0 }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_51_sit(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_51_sit</b> ');
            $('#explain').append('A player is sit, meaning he participates in the game.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 200, bet: 0 }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_52_inPosition(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_52_inPosition</b> ');
            $('#explain').append('A player is in position, meaning he participates in the game and must act. This is associated with a sound notification.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 200, bet: 0 },
{ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}


function jpoker_53_timeout(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_53_timeout</b> ');
            $('#explain').append('A descending progress bar shows how much time is left for the player to act.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 200, bet: 0 },
{ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 10; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_1_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 1; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_2_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 2; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_3_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 3; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_4_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 4; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_5_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 5; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_6_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 6; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_7_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 7; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_8_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 8; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_54_9_sidepot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_54_sidepot</b> ');
            $('#explain').append('A label show side pot attribution to allin player.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id, player_timeout: 10 },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'USER 1' },
{ type: 'PacketPokerPlayerArrive', seat: 1, serial: player_serial+1, game_id: game_id, name: 'USER 2' },
{ type: 'PacketPokerPlayerArrive', seat: 2, serial: player_serial+2, game_id: game_id, name: 'USER 3' },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id },
{ type: 'PacketPokerSit', serial: player_serial+2, game_id: game_id },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 0, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+1, game_id: game_id, money: 100, bet: 0 },
{ type: 'PacketPokerPlayerChips', serial: player_serial+2, game_id: game_id, money: 100, bet: 0 }
                       ];
        for(var j = 0; j < 9; j++) {
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_55_allWithSidePot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_55_allWithSidePot</b> ');
            $('#explain').append('All player pots are displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 0;
        var bet = 8;
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
	    packets.push({ type: 'PacketPokerSit', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: 0 });
            packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial + i, game_id: game_id, cards: [ 13, 14 ] });
	    packets.push({ type: 'PacketPokerCheck', serial: player_serial + i, game_id: game_id });
            packets.push({ type: 'PacketPokerPotChips', game_id: game_id, index: i, bet: [ 1, bet ] });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i, percentile: i%4 });
            bet *= 10;
            money *= 10;
        }
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3, 4, 5] });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_56_tourneyBreak(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_56_tourneyBreak</b> ');
            $('#explain').append('Tournaments is on break, resume time is displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        var bet = 8;
        for(var i = 0; i < 2; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
	    packets.push({ type: 'PacketPokerCheck', serial: player_serial + i, game_id: game_id });
            bet *= 10;
            money *= 10;
        }
	packets.push({ type: 'PacketPokerTableTourneyBreakBegin', game_id: game_id, resume_time: 1220979087});

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_57_stats(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_57_stats</b> ');
            $('#explain').append('All player pots are displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 0;
        var bet = 8;
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
	    packets.push({ type: 'PacketPokerSit', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i+1, percentile: i%4 });
            bet *= 10;
            money *= 10;
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_58_tourneyRank(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_56_tourneyBreak</b> ');
            $('#explain').append('Tournaments is on break, resume time is displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        var bet = 8;
        for(var i = 0; i < 2; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
	    packets.push({ type: 'PacketPokerCheck', serial: player_serial + i, game_id: game_id });
            bet *= 10;
            money *= 10;
        }
	packets.push({ type: 'PacketPokerTourneyRank', game_id: game_id, serial: player_serial, rank: 1, players: 1000, money: 1000});

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_60_text(place) {
        setUp();
        $('#text').show();
}

function jpoker_70_userInfo(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_70_userInfo</b> ');
            $('#explain').append('Personal informations of the current logged user.');
            $('#explain').append('<hr>');
        } 

        var server = $.jpoker.getServer('url');
	server.serial = 42;
	var PERSONAL_INFO_PACKET = {'rating': 1000, 'firstname': 'John', 'money': {}, 'addr_street': '8', 'phone': '000-00000', 'cookie': '', 'serial': server.serial, 'password': '', 'addr_country': 'Yours', 'name': 'testuser', 'gender': 'Male', 'birthdate': '01/01/1970', 'addr_street2': 'Main street', 'addr_zip': '5000', 'affiliate': 0, 'lastname': 'Doe', 'addr_town': 'GhostTown', 'addr_state': 'Alabama', 'type': 'PacketPokerPersonalInfo', 'email': 'john@doe.com'};

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(PERSONAL_INFO_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('userInfo', 'url');
}

function jpoker_80_tourneyDetailsRegistering(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_80_tourneyDetailsRegistering</b> ');
            $('#explain').append('Details of a sitngo registering tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 140, "table_serial": 606, "name": "user1", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
        server.serial = 10;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_80_1_tourneyDetailsRegularRegistering(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_80_1_tourneyDetailsRegularRegistering</b> ');
            $('#explain').append('Details of a regular registering tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 140, "table_serial": 606, "name": "user1", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 2000, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
        server.serial = 10;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_81_tourneyDetailsRunning(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_81_tourneyDetailsRunning</b> ');
            $('#explain').append('Details of a sitngo running tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5], "X707": [4,5], "X808": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "running", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_81_1_tourneyDetailsRegularRunning(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_81_1_tourneyDetailsRegularRunning</b> ');
            $('#explain').append('Details of a regular running tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "running", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_81_2_tourneyDetailsRunningWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_81_tourneyDetailsRunning</b> ');
            $('#explain').append('Details of a sitngo running tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5], "X707": [4,5], "X808": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "running", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "BOTRiryeevR" + i;
	    var player_serial = 'X' + i;
	    if (i & 2) {
		TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": -1};
	    } else {
		TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": i+i};
	    }
	}

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_81_3_tourneyDetailsRegularRunningWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_81_1_tourneyDetailsRegularRunning</b> ');
            $('#explain').append('Details of a regular running tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "running", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "BOTRiryeevR" + i;
	    var player_serial = 'X' + i;
	    if (i & 2) {
		TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606+i, "name": player_name, "rank": -1};
	    } else {
		TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606+i, "name": player_name, "rank": i+i};
	    }
	    if (TOURNEY_MANAGER_PACKET.table2serials['X' + 606 + i] == undefined) {
		TOURNEY_MANAGER_PACKET.table2serials['X' + 606 + i] = [];
	    }
	    TOURNEY_MANAGER_PACKET.table2serials['X' + 606 + i].push(i);
	}

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_82_tourneyDetailsCompleted(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_82_tourneyDetailsCompleted</b> ');
            $('#explain').append('Details of a sitngo completed tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": -1, "table_serial": 606, "name": "user1", "rank": 1}, "X5": {"money": -1, "table_serial": 606, "name": "user2", "rank": 2}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "complete", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_82_1_tourneyDetailsRegularCompleted(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_82_1_tourneyDetailsRegularCompleted</b> ');
            $('#explain').append('Details of a regular completed tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": -1, "table_serial": 606, "name": "user1", "rank": 1}, "X5": {"money": -1, "table_serial": 606, "name": "user2", "rank": 2}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "complete", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_82_2_tourneyDetailsRegularCompletedWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_82_1_tourneyDetailsRegularCompleted</b> ');
            $('#explain').append('Details of a regular completed tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": -1, "table_serial": 606, "name": "user1", "rank": 1}, "X5": {"money": -1, "table_serial": 606, "name": "user2", "rank": 2}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "complete", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "user" + i;
	    var player_serial = 'X' + i;
	    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": -1, "name": player_name, "rank": 200-i};
	}

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_83_tourneyDetailsRegisteringWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_83_tourneyDetailsRegisteringWithPager</b> ');
            $('#explain').append('Details of a sitngo registering tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};
	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "user" + i;
	    var player_serial = 'X' + i;
	    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": -1};
	}	

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_83_1_tourneyDetailsRegularRegisteringWithPager(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_83_1_tourneyDetailsRegularRegisteringWithPager</b> ');
            $('#explain').append('Details of a regular registering tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};
	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "user" + i;
	    var player_serial = 'X' + i;
	    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": -1};
	}	

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_84_tourneyDetailsRunningWithLink(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_84_tourneyDetailsRunningWithLink</b> ');
            $('#explain').append('Details of a sitngo running tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "running", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString(), 'tourney1', {link_pattern: 'http://foo.com/tourneytable?game_id={game_id}'});
}

function jpoker_84_1_tourneyDetailsRegularRunningWithLink(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_84_1_tourneyDetailsRegularRunningWithLink</b>');
            $('#explain').append('Details of a regular running tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "running", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString(), 'tourney1', {link_pattern: 'http://foo.com/tourneytable?game_id={game_id}'});
}

function jpoker_85_tourneyDetailsRegisteringWithPagerRegister(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_85_tourneyDetailsRegisteringWithPagerRegister</b> ');
            $('#explain').append('Details of a sitngo registering tournament with 200 players, when player is logged and not registered');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};
	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "user" + i;
	    var player_serial = 'X' + i;
	    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": -1};
	}

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
	server.serial = 666;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString(), 'tourney1');
}

function jpoker_85_1_tourneyDetailsRegularRegisteringWithPagerRegister(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_85_tourneyDetailsRegularRegisteringWithPagerRegister</b> ');
            $('#explain').append('Details of a regular registering tournament with 200 players, when player is logged and not registered');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};
	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "user" + i;
	    var player_serial = 'X' + i;
	    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": -1};
	}

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
	server.serial = 666;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString(), 'tourney1');
}

function jpoker_86_tourneyDetailsRegisteringWithPagerUnregister(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_86_tourneyDetailsRegisteringWithPagerUnregister</b> ');
            $('#explain').append('Details of a sitngo registering tournament with 200 players, when player is logged and registered');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};
	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "user" + i;
	    var player_serial = 'X' + i;
	    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": -1};
	}

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
	server.serial = 1;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString(), 'tourney1');
}

function jpoker_86_1_tourneyDetailsRegularRegisteringWithPagerUnregister(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_86_1_tourneyDetailsRegularRegisteringWithPagerUnregister</b> ');
            $('#explain').append('Details of a regular registering tournament with 200 players, when player is logged and registered');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};
	for (var i = 0; i < 200; ++i) {
	    var player_money = 140+i;
	    var player_name = "user" + i;
	    var player_serial = 'X' + i;
	    TOURNEY_MANAGER_PACKET.user2properties[player_serial] = {"money": player_money, "table_serial": 606, "name": player_name, "rank": -1};
	}

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
	server.serial = 1;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString(), 'tourney1');
}

function jpoker_87_tourneyDetailsBreak(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_87_tourneyDetailsBreak</b> ');
            $('#explain').append('Details of a sitngo break tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "break", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_87_1_tourneyDetailsRegularBreak(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_87_1_tourneyDetailsRegularBreak</b> ');
            $('#explain').append('Details of a regular break tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "break", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_88_tourneyDetailsBreakWait(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_88_tourneyDetailsBreakWait</b> ');
            $('#explain').append('Details of a sitngo breakwait tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "breakwait", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_88_1_tourneyDetailsRegularBreakWait(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_88_1_tourneyDetailsRegularBreakWait</b> ');
            $('#explain').append('Details of a regular breakwait tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 100000, "table_serial": 606, "name": "user1", "rank": -1}, "X5": {"money": 100000, "table_serial": 606, "name": "user2", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4,5]}, "type": 149, "tourney": {"registered": 2, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "breakwait", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 0, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0, "rank2prize": [1000000, 100000]}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_89_tourneyDetailsAnnounced(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_80_tourneyDetailsAnnounced</b> ');
            $('#explain').append('Details of a sitngo announced tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {}, "tourney": {"registered": 0, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "announced", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 2000, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
        server.serial = 10;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_89_1_tourneyDetailsRegularAnnounced(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_80_1_tourneyDetailsRegularAnnounced</b> ');
            $('#explain').append('Details of a regular announced tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {}, "tourney": {"registered": 0, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "announced", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 2000, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
        server.serial = 10;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_89_2_tourneyDetailsCanceled(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_80_tourneyDetailsCanceled</b> ');
            $('#explain').append('Details of a sitngo canceled tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {}, "tourney": {"registered": 0, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "canceled", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 2000, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
        server.serial = 10;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_89_3_tourneyDetailsRegularCanceled(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_80_1_tourneyDetailsRegularCanceled</b> ');
            $('#explain').append('Details of a regular canceled tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {}, "length": 3, "tourney_serial": 1, "table2serials": {}, "tourney": {"registered": 0, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Regular tournament long description", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "canceled", "buy_in": 300000, "add_on_count": 0, "description_short": "Regular tournament", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 2000, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "n", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();

        var server = $.jpoker.getServer('url');
        server.serial = 10;
        $(place).jpoker('tourneyDetails', 'url', tourney_serial.toString());
}

function jpoker_90_tourneyPlaceholder(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_90_tourneyPlaceholder</b> ');
            $('#explain').append('Placeholder table for a registering tournament.');
            $('#explain').append('<hr>');
        }

	var TOURNEY_MANAGER_PACKET = {"user2properties": {"X4": {"money": 140, "table_serial": 606, "name": "user1", "rank": -1}}, "length": 3, "tourney_serial": 1, "table2serials": {"X606": [4]}, "type": 149, "tourney": {"registered": 1, "betting_structure": "level-15-30-no-limit", "currency_serial": 1, "description_long": "Sit and Go 2 players", "breaks_interval": 3600, "serial": 1, "rebuy_count": 0, "state": "registering", "buy_in": 300000, "add_on_count": 0, "description_short": "Sit and Go 2 players, Holdem", "player_timeout": 60, "players_quota": 2, "rake": 0, "add_on": 0, "start_time": 1220102053, "breaks_first": 7200, "variant": "holdem", "players_min": 2, "schedule_serial": 1, "add_on_delay": 60, "name": "sitngo2", "finish_time": 0, "prize_min": 0, "breaks_duration": 300, "seats_per_game": 2, "bailor_serial": 0, "sit_n_go": "y", "rebuy_delay": 0}, "type": "PacketPokerTourneyManager"};

	var tourney_serial = TOURNEY_MANAGER_PACKET.tourney_serial;
	var players_count = 1;

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TOURNEY_MANAGER_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();
	
        $(place).jpoker('tourneyPlaceholder', 'url', tourney_serial.toString());
}

function jpoker_100_places(place) {
        setUp();
        if(explain) {
            $('#explain').append('Tables showing the table and tournaments the player is currently connected to.');
            $('#explain').append('<hr>');
        }

	var PLAYER_PLACES_PACKET = {type: 'PacketPokerPlayerPlaces', serial: 42, tables: [11, 12, 13], tourneys: [21, 22]};

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(PLAYER_PLACES_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();
	
        var server = $.jpoker.getServer('url');
	server.serial = 42;
        $(place).jpoker('places', 'url');
}

function jpoker_101_playerLookup(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_101_playerLookup</b> ');
            $('#explain').append('Form for searching where is a player.');
            $('#explain').append('<hr>');
        }	
	
        var server = $.jpoker.getServer('url');
        $(place).jpoker('playerLookup', 'url');
	$('.jpoker_player_lookup_input', place).val('user');
	var i = 0;
	$('.jpoker_player_lookup_submit', place).click(function() {
		var PLAYER_PLACES_PACKET = {type: 'PacketPokerPlayerPlaces', name: 'user', tables: [11+i, 12+i, 13+i], tourneys: [21+i, 22+i]};
		++i;
		server.queueIncoming([PLAYER_PLACES_PACKET]);
	    }).click();
}

function jpoker_102_placesWithLink(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_102_placesWithLink</b> ');
            $('#explain').append('Tables showing the table and tournaments the player is currently connected to, with html link on name and description');
            $('#explain').append('<hr>');
        }

	var PLAYER_PLACES_PACKET = {type: 'PacketPokerPlayerPlaces', serial: 42, tables: [11, 12, 13], tourneys: [21, 22]};

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(PLAYER_PLACES_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();
	
        var server = $.jpoker.getServer('url');
	server.serial = 42;
	var table_link_pattern = 'http://foo.com/table?game_id={game_id}';
	var tourney_link_pattern = 'http://foo.com/tourney?tourney_serial={tourney_serial}';
        $(place).jpoker('places', 'url', {table_link_pattern: table_link_pattern, tourney_link_pattern: tourney_link_pattern});
}

function jpoker_103_playerLookupWithLink(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_103_playerLookupWithLink</b> ');
            $('#explain').append('Form for searching where is a player, with html link on name and description.');
            $('#explain').append('<hr>');
        }	
	
        var server = $.jpoker.getServer('url');
	var table_link_pattern = 'http://foo.com/table?game_id={game_id}';
	var tourney_link_pattern = 'http://foo.com/tourney?tourney_serial={tourney_serial}';
        $(place).jpoker('playerLookup', 'url', {table_link_pattern: table_link_pattern, tourney_link_pattern: tourney_link_pattern});
	$('.jpoker_player_lookup_input', place).val('user');
	var i = 0;
	$('.jpoker_player_lookup_submit', place).click(function() {
		var PLAYER_PLACES_PACKET = {type: 'PacketPokerPlayerPlaces', name: 'user', tables: [11+i, 12+i, 13+i], tourneys: [21+i, 22+i]};
		++i;
		server.queueIncoming([PLAYER_PLACES_PACKET]);
	    }).click();
}

function jpoker_110_cashier(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_110_cashier</b> ');
            $('#explain').append('Cashier showing player bankroll for each currency.');
            $('#explain').append('<hr>');
        }

	var USER_INFO_PACKET = {"rating":1000,"name":"proppy","money":{"X1":[100000,10000,0], "X2":[200000,20000,0]},"affiliate":0,"cookie":"","serial":4,"password":"","type":"PacketPokerUserInfo","email":"","uid__":"jpoker1220102037582"};

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(USER_INFO_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();
	
        var server = $.jpoker.getServer('url');
	server.serial = 42;
	$(place).jpoker('cashier', 'url');
}


function jpoker_111_tablepicker(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_111_tablepicker</b> ');
            $('#explain').append('Tablepicker allow to quickly join, click on options to show table criterion, click on button to show error message');
            $('#explain').append('<hr>');
        }

	var TABLE_PACKET = {type: "PacketPokerTable", id: 0};

        var PokerServer = function() {};
        PokerServer.prototype = {
            outgoing: "[ " + JSON.stringify(TABLE_PACKET) + " ]",

            handle: function(packet) { }
        };
        ActiveXObject.prototype.server = new PokerServer();
	
        var server = $.jpoker.getServer('url');
	server.serial = 42;
	$(place).jpoker('tablepicker', 'url');
}

function jpoker_120_level_junior(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_120_level_junior</b> ');
            $('#explain').append('3 players with level junior.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 10000;
        var bet = 8;
        for(var i = 0; i < 3; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i+1, percentile: 0 });
        }	
	packets.push({ type: 'PacketPokerSit', serial: player_serial, game_id: game_id, seat: 0});
	packets.push({ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id, seat: 1});
	packets.push({ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_121_level_pro(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_121_level_pro</b> ');
            $('#explain').append('3 players with level pro.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 10000;
        var bet = 8;
        for(var i = 0; i < 3; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i+1, percentile: 1 });
        }	
	packets.push({ type: 'PacketPokerSit', serial: player_serial, game_id: game_id, seat: 0});
	packets.push({ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id, seat: 1});
	packets.push({ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_122_level_expert(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_122_level_expert</b> ');
            $('#explain').append('3 players with level expert.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 10000;
        var bet = 8;
        for(var i = 0; i < 3; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i+1, percentile: 2 });
        }	
	packets.push({ type: 'PacketPokerSit', serial: player_serial, game_id: game_id, seat: 0});
	packets.push({ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id, seat: 1});
	packets.push({ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_123_level_master(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_123_level_master</b> ');
            $('#explain').append('3 players with level master.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 10000;
        var bet = 8;
        for(var i = 0; i < 3; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            packets.push({ type: 'PacketPokerPlayerStats', serial:player_serial + i, game_id: game_id, rank: i+1, percentile: 3 });
        }	
	packets.push({ type: 'PacketPokerSit', serial: player_serial, game_id: game_id, seat: 0});
	packets.push({ type: 'PacketPokerSit', serial: player_serial+1, game_id: game_id, seat: 1});
	packets.push({ type: 'PacketPokerPosition', serial: player_serial, game_id: game_id });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_130_chat_scroll(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_130_chat_scroll</b> ');
            $('#explain').append('The logged in player is in position and the chat shows.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 1000000, bet: 0 },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerChat', serial: 0, game_id: game_id, message: 'Dealer: dealing\nDealer: dealing one\nDealer: dealing two\nDealer: dealing three\nDealer: dealing four\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing\nDealer: dealing' },
{ type: 'PacketPokerChat', serial: player_serial, game_id: game_id, message: 'Message one\nMessage two\nMessage three\nMessage four\nMessage five\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage\nMessage' }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_131_chat_no_scroll(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_131_chat_no_scroll</b> ');
            $('#explain').append('The logged in player is in position and the chat shows.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketSerial', serial: player_serial },
{ type: 'PacketPokerTable', id: game_id },
{ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'myself' },
{ type: 'PacketPokerPlayerChips', serial: player_serial, game_id: game_id, money: 1000000, bet: 0 },
{ type: 'PacketPokerSit', serial: player_serial, game_id: game_id },
{ type: 'PacketPokerChat', serial: 0, game_id: game_id, message: 'Dealer: dealing' },
{ type: 'PacketPokerChat', serial: player_serial, game_id: game_id, message: 'Message one' }
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_141_click_here_to_get_a_seat(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_141_click_here_to_get_a_seat</b> ');
            $('#explain').append('The logged in player is asked which seat he wants to take.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{"observers": 1, "name": "One", "percent_flop" : 98, "average_pot": 100, "seats": 10, "variant": "holdem", "hands_per_hour": 220, "betting_structure": "2-4-limit", "currency_serial": 1, "muck_timeout": 5, "players": 4, "waiting": 0, "skin": "default", "id": game_id, "type": "PacketPokerTable", "player_timeout": 60}
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
	server.serial = 42;
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');	
}

function jpoker_142_click_here_to_get_a_seat_in_progress(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_141_click_here_to_get_a_seat</b> ');
            $('#explain').append('The logged in player has choosed which seat he wants to take.');
            $('#explain').append('A progress indicator is displayed.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{"observers": 1, "name": "One", "percent_flop" : 98, "average_pot": 100, "seats": 10, "variant": "holdem", "hands_per_hour": 220, "betting_structure": "2-4-limit", "currency_serial": 1, "muck_timeout": 5, "players": 4, "waiting": 0, "skin": "default", "id": game_id, "type": "PacketPokerTable", "player_timeout": 60}
                       ];
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };

        var server = $.jpoker.getServer('url');
	server.serial = 42;
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');	    
	    $('.jpoker_sit_seat').click();
	};
        server.sendPacket('ping');	
}

function jpoker_143_board(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_143_board</b> ');
            $('#explain').append('Animation on each street, highlight of best cards.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
	var player_serial = 42;
        var packets = [{ type: 'PacketPokerTable', id: game_id,	delay: { showdown: 500 }}];
	packets.push({ type: 'PacketPokerPlayerArrive', seat: 0, serial: player_serial, game_id: game_id, name: 'foo' });
	packets.push({ type: 'PacketPokerDealer', dealer: 0, game_id: game_id });
	packets.push({ type: 'PacketPokerPlayerCards', serial: player_serial, game_id: game_id, cards: [ 8, 4 ] });	
	packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [] });
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3] });
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3, 6] });
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3, 6, 7] });
	packets.push({ type: 'PacketPokerShowdown', game_id: game_id});
	packets.push({"besthand":1,"hand":"Flush Queen high","length":47,"cookie":"","board":[1,2,3,6,7],"bestcards":[1,2,3,4,5],"cards":[8,4],"game_id":game_id,"serial":player_serial,"type":"PacketPokerBestCards","side":""});
	packets.push({ type: 'PacketPokerShowdown', game_id: game_id});
	packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [] });
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3] });
        packets.push({ type: 'PacketPokerBoardCards', game_id: game_id, cards: [1, 2, 3, 6] });

        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

function jpoker_144_pot(place) {
        setUp();
        if(explain) {
            $('#explain').append('<b>jpoker_143_pot</b> ');
            $('#explain').append('Animation from player bet to pot.');
            $('#explain').append('<hr>');
        }

        var game_id = 100;
        var player_serial = 200;
        var packets = [
{ type: 'PacketPokerTable', id: game_id }
                       ];
        var money = 2;
        var bet = 8;
	packets.push({ type: 'PacketPokerDealer', dealer: 0, game_id: game_id });
	packets.push({ type: 'PacketSerial', serial: player_serial });
        for(var i = 0; i < 10; i++) {
            packets.push({ type: 'PacketPokerPlayerArrive', serial: player_serial + i, game_id: game_id, seat: i, name: 'username' + i });
	    packets.push({"type":"PacketPokerChipsPlayer2Bet","length":15,"cookie":"","game_id":game_id,"serial":player_serial+i,"chips":[10000,2]});
            packets.push({ type: 'PacketPokerPlayerChips', serial: player_serial + i, game_id: game_id, money: money , bet: bet });
            bet *= 10;
            money *= 10;
        }
        for(var j = 0; j < 9; j++) {
	    packets.push({ type: 'PacketPokerChipsBet2Pot', pot: j, game_id: game_id, serial: player_serial + j });
            packets.push({ type: 'PacketPokerPotChips', index: j, bet: [j + 1, 100000], game_id: game_id });
        }
        ActiveXObject.prototype.server = {
            outgoing: JSON.stringify(packets),
            handle: function(packet) { }
        };
        var server = $.jpoker.getServer('url');
        server.spawnTable = function(server, packet) {
	    $(place).jpoker('table', 'url', game_id, 'ONE');
	};
        server.sendPacket('ping');
}

var jpoker_skin_permalink = function() {
    $("#links li a").each(function() {
	    $(this).attr('href', '#'+$(this).text());
	}).click(function() {
		eval($(this).text()+'("#place")');
	    });
    if (window.location.hash) {
	eval(window.location.hash.substr(1)+'("#place")');
    } else {
	$("#links li a").eq(0).click();
    }
};