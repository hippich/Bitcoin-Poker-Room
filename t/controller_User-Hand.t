use strict;
use warnings;
use Test::More;

BEGIN { use_ok 'Catalyst::Test', 'Room' }
BEGIN { use_ok 'Room::Controller::User::Hand' }

my $controller = Room::Controller::User::Hand->new;
my $history = "[('game', 0, 22, 0, 0.0, 'holdem', '.02-.04-no-limit', [6, 7], 7, {6: 200, 7: 94L}), ('position', 0), ('blind', 6, 2, 0), ('position', 1), ('blind', 7, 4, 0), ('position', -1), ('round', 'pre-flop', PokerCards([]), {6: PokerCards([197, 193]), 7: PokerCards([215, 221])}), ('position', 0), ('call', 6, 2), ('position', 1), ('check', 7), ('position', -1), ('round', 'flop', PokerCards([47, 40, 50]), None), ('position', 0), ('raise', 6, 4), ('position', 1), ('call', 7, 4), ('position', -1), ('round', 'turn', PokerCards([47, 40, 50, 30]), None), ('position', 0), ('check', 6), ('position', 1), ('check', 7), ('position', -1), ('round', 'river', PokerCards([47, 40, 50, 30, 25]), None), ('position', 0), ('check', 6), ('position', 1), ('check', 7), ('position', -1), ('showdown', None, {6: PokerCards([5, 1]), 7: PokerCards([215, 221])}), ('end', [6], [{'serial2delta': {6: 8, 7: -8}, 'player_list': [6, 7], 'serial2rake': {6: 0}, 'serial2share': {6: 16}, 'pot': 16, 'serial2best': {6: {'hi': [16894848, ['OnePair', 40, 1, 25, 50, 47]]}, 7: {'hi': [834180, ['NoPair', 25, 50, 23, 47, 30]]}}, 'type': 'game_state', 'side_pots': {'building': 0, 'pots': [[16, 16]], 'last_round': 3, 'contributions': {0: {0: {6: 4, 7: 4}}, 1: {0: {6: 4, 7: 4}}, 2: {}, 'total': {6: 8, 7: 8}, 3: {}}}}, {'serials': [6, 7], 'pot': 16, 'hi': [6], 'chips_left': 0, 'type': 'resolve', 'serial2share': {6: 16}}])]";

my $tree = $controller->__parse_hands($history);

ok( $tree->[0]->[0] eq 'game', 'History should parse correctly' ); 

done_testing();
