#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
#
# This software's license gives you freedom; you can copy, convey,
# propagate, redistribute and/or modify this program under the terms of
# the GNU Affero General Public License (AGPL) as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version of the AGPL published by the FSF.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero
# General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program in a file in the toplevel directory called
# "AGPLv3".  If not, see <http://www.gnu.org/licenses/>.
#
import sys
import os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

from twisted.trial import unittest, runner, reporter

from tests import testclock

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from pokerengine import pokergame
from pokernetwork.pokerexplain import PokerGames
from pokernetwork import pokerexplain

class MockupPokerGameClient:

    def __init__(self, template, dirs):
        self.id = 0
        self.name = "noname"

class PokerGamesTestCase(unittest.TestCase):

    def setUp(self):
        self.games = PokerGames()
        self.games.game_client = MockupPokerGameClient

    def test_all(self):
        self.failIf(self.games.getGame(1))
        game = self.games.getOrCreateGame(1)
        self.assertEquals([1], self.games.getGameIds())
        self.assertEquals([game], self.games.getAll())
        self.assertEquals("noname", game.name)
        self.assertEquals(game, self.games.getGame(1))
        self.assertEquals(game, self.games.getGameByNameNoCase('NoName'))
        self.failIf(self.games.getGameByNameNoCase('unknown'))
        class Packet:
            pass
        p = Packet()
        self.assertEquals(False, self.games.packet2game(p))
        p.game_id = 1
        self.assertEquals(game, self.games.packet2game(p))
        self.failUnless(self.games.gameExists(1))
        self.games.deleteGame(1)
        self.failIf(self.games.getGame(1))

from pokernetwork.pokerexplain import PokerExplain
from pokernetwork.pokerclientpackets import *

class PokerExplainTestCase(unittest.TestCase):

    def setUp(self):
        self.explain = PokerExplain()
        self.explain.games.dirs = ['%s/poker-engine' % SCRIPT_DIR]
        self.explain.setVerbose(10)

    def test01_utilities(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        self.explain.message("")
        self.explain.setVerbose(10)
        self.explain.error("test")
        self.explain.setPrefix("foo")
        self.assertEqual("foo", self.explain._prefix)

    def test02_normalizeChips(self):
        class PokerGame:
            unit = 10
        game = PokerGame()
        self.assertEqual([1, 5, 10, 3], self.explain.normalizeChips(game, 35))
        game.unit = 237
        self.assertEqual([1,5], self.explain.normalizeChips(game, 5))

    def test03_updatePlayerChips(self):
        class PokerGame:
            id = 3
        game = PokerGame()

        class Player:
            bet = 13
            money = 17
            serial = 1
        player = Player()
        packet = self.explain.updatePlayerChips(game, player)
        self.assertEqual(player.money, packet.money)
        self.assertEqual(player.bet, packet.bet)

    def test04_updatePotsChips(self):
        class PokerGame:
            id = 1
            unit = 1
        game = PokerGame()
        packets = self.explain.updatePotsChips(game, [])
        self.assertEqual(PACKET_POKER_CHIPS_POT_RESET, packets[0].type)
        packets = self.explain.updatePotsChips(game, {'pots': [[10, 20], [20, 40]]})
        self.assertEqual(2, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_POT_CHIPS, packet.type)
        self.assertEqual([1, 6, 2, 2], packet.bet)

    def test05_chipsPlayer2Bet(self):
        class PokerGame:
            id = 1
            unit = 1
        class PokerPlayer:
            serial = 10
            bet = 30
            money = 50
        packets = self.explain.chipsPlayer2Bet(PokerGame(), PokerPlayer(), 10)
        self.assertEqual(3, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_CHIPS_PLAYER2BET, packet.type)
        self.assertEqual([1, 6, 2, 2], packet.chips)

    def test06_chipsBet2Pot(self):
        class PokerGame:
            id = 1
            unit = 1

            def isSecondRound(self):
                return True

        class PokerPlayer:
            serial = 10
            bet = 30
            money = 50
            dead = 3

        pot_index = 0
        packets = self.explain.chipsBet2Pot(PokerGame(), PokerPlayer(), 13, pot_index)
        self.assertEqual(3, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_CHIPS_BET2POT, packet.type)
        self.assertEqual([1, 6, 2, 2], packet.chips)
        self.assertEqual(pot_index, packet.pot)
        packet = packets[1]
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, packet.type)
        packet = packets[2]
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, packet.type)

        # test without explain chipstack
        self.explain.what = PacketPokerExplain.REST
        packets = self.explain.chipsBet2Pot(PokerGame(), PokerPlayer(), 13, pot_index)
        self.assertEqual(2, len(packets))

    def test07_chipsPot2Player(self):
        class PokerGame:
            id = 1
            unit = 1

        class PokerPlayer:
            serial = 1

        reason = "reason"
        pot_index = 1
        packet = self.explain.chipsPot2Player(PokerGame(), PokerPlayer(), 10, pot_index, reason)
        self.assertEqual(PACKET_POKER_CHIPS_POT2PLAYER, packet.type)
        self.assertEqual([1, 6, 2, 2], packet.chips)
        self.assertEqual(reason, packet.reason)
        self.assertEqual(pot_index, packet.pot)

    def test08_gameEvent_position(self):
        self.explain.forward_packets = [ 'fake' ]
        class PokerGame:
            id = 3
            def inGameCount(self):
                return 1
        class PokerGames:
            def getGame(self, id):
                return PokerGame()
        self.explain.games = PokerGames()
        self.assertEquals(True, self.explain.gameEvent(1, "position"))
        self.assertEquals(PACKET_POKER_ALLIN_SHOWDOWN, self.explain.forward_packets[1].type)

    def test08_gameEvent_failure(self):
        self.failIf(self.explain.gameEvent(1, "end_round"))
        self.explain.forward_packets = [ 'fake' ]
        self.failIf(self.explain.gameEvent(1, "end_round"))

    def test08_gameEvent_end_round(self):
        self.explain.forward_packets = [ 'fake' ]
        class PokerGame:
            id = 3
        class PokerGames:
            def getGame(self, id):
                return PokerGame()
        self.explain.games = PokerGames()
        self.assertEqual(True, self.explain.gameEvent(1, "end_round"))
        self.assertEqual(2, len(self.explain.forward_packets))
        packet = self.explain.forward_packets[1]
        self.assertEqual(PACKET_POKER_END_ROUND, packet.type)

        self.explain.forward_packets = [ 'fake' ]
        self.assertEqual(True, self.explain.gameEvent(1, "end_round_last"))
        self.assertEqual(2, len(self.explain.forward_packets))
        packet = self.explain.forward_packets[1]
        self.assertEqual(PACKET_POKER_END_ROUND_LAST, packet.type)

    def test08_gameEvent_money2bet(self):
        self.explain.forward_packets = [ 'fake' ]
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))

        event = ( "raise", player_serial, 20 )
        game.historyAdd(*event)
        self.assertEqual(True, self.explain.gameEvent(game_id, "money2bet", player_serial, 20))
        self.assertEqual(5, len(self.explain.forward_packets))
        packet = self.explain.forward_packets[1]
        self.assertEqual(PACKET_POKER_HIGHEST_BET_INCREASE, packet.type)
        packet = self.explain.forward_packets[2]
        self.assertEqual(PACKET_POKER_CHIPS_PLAYER2BET, packet.type)
        packet = self.explain.forward_packets[3]
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, packet.type)
        packet = self.explain.forward_packets[4]
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, packet.type)

        # test without explain chipstack
        self.explain.what = PacketPokerExplain.REST
        self.explain.forward_packets = [ 'fake' ]
        self.assertEqual(True, self.explain.gameEvent(game_id, "money2bet", player_serial, 20))
        self.assertEqual(4, len(self.explain.forward_packets))


    def test08_gameEvent_bet2pot(self):
        self.explain.forward_packets = [ 'fake' ]
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))

        game.current_round = -1
        self.assertEqual(True, self.explain.gameEvent(game_id, "bet2pot", player_serial, 20))
        self.assertEqual(4, len(self.explain.forward_packets))
        packet = self.explain.forward_packets[1]
        self.assertEqual(PACKET_POKER_CHIPS_BET2POT, packet.type)
        packet = self.explain.forward_packets[2]
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, packet.type)
        packet = self.explain.forward_packets[3]
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, packet.type)

        # test without explain chipstack
        self.explain.what = PacketPokerExplain.REST
        self.explain.forward_packets = [ 'fake' ]
        self.assertEqual(True, self.explain.gameEvent(game_id, "bet2pot", player_serial, 20))
        self.assertEqual(3, len(self.explain.forward_packets))


    def test08_gameEvent_round_cap_decrease(self):
        self.explain.forward_packets = [ 'fake' ]
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        def updateBetLimit(game):
            return ('updateBetLimit called',)
        self.explain.updateBetLimit = updateBetLimit
        self.assertEqual(True, self.explain.gameEvent(1, "round_cap_decrease"))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual('updateBetLimit called', self.explain.forward_packets[1])


    def test09_handleSerial(self):
        serial = 1
        self.explain.handleSerial(PacketSerial(serial = serial))
        self.assertEqual(serial, self.explain.serial)
        self.assertEqual('[%i]' % serial, self.explain._prefix)
        self.assertEqual('[%i]' % serial, self.explain.games.prefix)

    def test09_1_handleSerialPrefix(self):
        serial = 1
        self.explain.setPrefix('myprefix')
        self.explain.handleSerial(PacketSerial(serial = serial))
        self.assertEqual(serial, self.explain.serial)
        self.assertEqual('myprefix', self.explain._prefix)
        self.assertEqual('myprefix', self.explain.games.prefix)

    def test10_setPlayerTimeout(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        player.setUserData({ 'timeout': None })

        packet = PacketPokerTimeoutWarning(serial = player_serial,
                                           timeout = 0)
        self.assertEqual(False, self.explain.setPlayerTimeout(game, packet))
        packet.timeout = 2
        self.assertEqual(True, self.explain.setPlayerTimeout(game, packet))
        self.assertEqual((int(testclock._seconds_value), 2), player.user_data['timeout'])
        return (game, player)

    def test11_resendPlayerTimeoutWarning(self):
        (game, player) = self.test10_setPlayerTimeout()
        self.assertEqual((), self.explain.resendPlayerTimeoutWarning(game))
        self.explain.handleSerial(PacketSerial(serial = player.serial))
        game.state = pokergame.GAME_STATE_PRE_FLOP
        game.player_list = [ player.serial ]
        game.position = 0
        (packet,) = self.explain.resendPlayerTimeoutWarning(game)
        self.assertEqual(PACKET_POKER_TIMEOUT_WARNING, packet.type)
        self.assertEqual(player.serial, packet.serial)

    def test12_unsetPlayerTimeout(self):
        (game, player) = self.test10_setPlayerTimeout()
        self.explain.unsetPlayerTimeout(game, player.serial)
        self.assertEqual(None, player.user_data['timeout'])

    def test13_serial2name(self):
        class PokerGame:
            id = 1
            def getPlayer(self, serial):
                return False
        self.assertEqual("<unknown>", self.explain.serial2name(PokerGame(), 1))

        class PokerPlayer:
            name = "myname"

        class PokerGame:
            id = 1
            def getPlayer(self, serial):
                return PokerPlayer()
        self.assertEqual("myname", self.explain.serial2name(PokerGame(), 1))

    def test14_moveBet2Pot(self):

        player_serial = 1

        class PokerPlayer:
            serial = player_serial
            bet = 30
            money = 50
            dead = 3

        game_id = 1
        amount = 23
        class PokerGame:
            id = game_id
            unit = 1
            pots = {'pots': [[10, 20], [20, 40]]}

            def getPots(self):
                return self.pots

            def getPlayer(self, serial):
                return PokerPlayer()

            def getLatestPotContributions(self):
                return {0: {player_serial: amount}}

            def isSecondRound(self):
                return False

        packets = self.explain.moveBet2Pot(PokerGame())
        self.assertEqual(5, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_CHIPS_BET2POT, packet.type)
        self.assertEqual([1, 6, 2, 6, 5, 1], packet.chips)
        packet = packets[1]
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, packet.type)
        packet = packets[2]
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, packet.type)

        # test without explain chipstack
        self.explain.what = PacketPokerExplain.REST
        packets = self.explain.moveBet2Pot(PokerGame())
        self.assertEqual(4, len(packets))


    def test15_updateBetLimit(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        self.explain.handleSerial(PacketSerial(serial = player.serial))

        game.player_list = [ player.serial ]
        game.state = pokergame.GAME_STATE_PRE_FLOP
        game.current_round = 0
        game.bet_info = { 0: {'fixed': 1} }

        packets = self.explain.updateBetLimit(game)
        self.assertEqual(1, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_BET_LIMIT, packet.type)

        self.explain.chips_values = []
        self.assertEqual([], self.explain.updateBetLimit(game))

    def test16_currentGames(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        packet = self.explain.currentGames(game_id)
        self.assertEqual(PACKET_POKER_CURRENT_GAMES, packet.type)

    def test17_packetPot2Player(self):
        class PokerPlayer:
            serial = 1
            bet = 10
            money = 20

        chips_left = 2

        class PokerGame:
            id = 1
            unit = 1
            serial2player = {1: PokerPlayer()}

            def getPlayer(self, serial):
                return self.serial2player[1]

        #
        # chips_left
        #
        class PokerGameChipsLeft(PokerGame):
            showdown_stack = [
                {'type': None,
                 'side_pots': {'pots': []}},
                {'type': 'left_over',
                 'chips_left': chips_left,
                 'serial': 1 },
                ]


        packets = self.explain.packetsPot2Player(PokerGameChipsLeft())
        self.assertEqual(4, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_CHIPS_POT2PLAYER, packet.type)
        self.assertEqual('left_over', packet.reason)
        self.assertEqual([1, chips_left], packet.chips)

        #
        # uncalled
        #
        uncalled = 2
        class PokerGameUncalled(PokerGame):
            showdown_stack = [
                {'type': None,
                 'side_pots': {'pots': []}},
                {'type': 'uncalled',
                 'uncalled': uncalled,
                 'serial': 1 },
                ]

        packets = self.explain.packetsPot2Player(PokerGameUncalled())
        self.assertEqual(4, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_CHIPS_POT2PLAYER, packet.type)
        self.assertEqual('uncalled', packet.reason)
        self.assertEqual([1, chips_left], packet.chips)

        #
        # resolve single winner, single frame
        #
        class PokerGameResolve(PokerGame):
            showdown_stack = [
                {'type': None,
                 'side_pots': {'pots': [[10, 10], [10, 20]]},
                 'pot': 20,
                 },
                {'type': 'resolve',
                 'pot': 20,
                 'serial': 1,
                 'serial2share': {1: 20},
                 },
                ]

        packets = self.explain.packetsPot2Player(PokerGameResolve())
        self.assertEqual(5, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_CHIPS_POT_MERGE, packet.type)
        self.assertEqual([0], packet.sources)
        self.assertEqual(1, packet.destination)
        packet = packets[1]
        self.assertEqual(PACKET_POKER_CHIPS_POT2PLAYER, packet.type)
        self.assertEqual("win", packet.reason)

        #
        # resolve
        #
        class PokerGameResolve(PokerGame):
            showdown_stack = [
                {'type': None,
                 'side_pots': {'pots': [[10, 10], [10, 20]]},
                 'pot': 20,
                 },
                {'type': 'resolve',
                 'pot': 10,
                 'serial': 1,
                 'serial2share': {1: 10},
                 },
                {'type': 'resolve',
                 'pot': 10,
                 'serial': 1,
                 'serial2share': {1: 10},
                 },
                ]

        packets = self.explain.packetsPot2Player(PokerGameResolve())
        self.assertEqual(5, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_CHIPS_POT2PLAYER, packet.type)
        self.assertEqual("win", packet.reason)
        self.assertEqual([1, 6, 2, 2], packet.chips)

    def test18_packetsShowdown(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        self.failIf(self.explain.packetsShowdown(game))
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        game.showdown_stack = [{'serial2delta': {player_serial: 1}}]
        game.state = pokergame.GAME_STATE_END
        game.winners = [player_serial]

        card = 1
        player.hand.add(card, True) # add a visible card

        game.variant = "7stud"
        hand_value_string = "HandValue"
        hand_value = 1010
        hand = [1, 2, 3, 4, 5]
        game.serial2best = {player_serial:
                            {'hi': (hand_value, [hand_value_string] + hand),
                             'low': (hand_value, [hand_value_string] + hand)},
                            }
        game.side2winners = {
            'hi': [player_serial],
            'low': [player_serial],
            }
        game.win_orders = [ "hi", "low" ]
        packets = self.explain.packetsShowdown(game)
        self.assertEqual(4, len(packets))
        packet = packets[0]
        self.assertEqual(PACKET_POKER_PLAYER_NO_CARDS, packet.type)
        packet = packets[1]
        self.assertEqual(PACKET_POKER_PLAYER_CARDS, packet.type)
        self.assertEqual([card], packet.cards)
        packet = packets[2]
        self.assertEqual(PACKET_POKER_BEST_CARDS, packet.type)
        self.assertEqual(hand, packet.bestcards)
        self.assertEqual("hi", packet.side)
        packet = packets[3]
        self.assertEqual(PACKET_POKER_BEST_CARDS, packet.type)
        self.assertEqual(hand, packet.bestcards)
        self.assertEqual("low", packet.side)

    def test19_packetsTableQuit(self):
        class PokerPlayer:
            serial = 1
            seat = 1
        class PokerGame:
            id = 1
            def playersAll(self):
                return [PokerPlayer()]
        game = PokerGame()
        self.explain.games.games = {1: game}
        packets = self.explain.packetsTableQuit(game)
        self.assertEqual(5, len(packets))
        self.assertEqual(PACKET_POKER_BATCH_MODE, packets[0].type)
        self.assertEqual(PACKET_POKER_PLAYER_LEAVE, packets[1].type)
        self.assertEqual(PACKET_POKER_STREAM_MODE, packets[2].type)
        self.assertEqual(PACKET_POKER_TABLE_QUIT, packets[3].type)
        self.assertEqual(PACKET_POKER_CURRENT_GAMES, packets[4].type)

    def test20_explain_poker_table(self):
        self.assertTrue(self.explain.explain(PacketPokerTable(id = 0)))
        self.assertEqual(1, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_TABLE, self.explain.forward_packets[0].type)

        self.assertTrue(self.explain.explain(PacketPokerTable(id = 1,
                                                              betting_structure = '1-2-no-limit',
                                                              variant = 'holdem')))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_TABLE, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_CURRENT_GAMES, self.explain.forward_packets[1].type)

    def test20_explain_poker_table_deleteGame(self):
        self.assertTrue(self.explain.explain(PacketPokerTable(id = 1,
                                                              betting_structure = '1-2-no-limit',
                                                              variant = 'holdem')))
        game = self.explain.games.getGame(1)
        self.assertTrue(self.explain.explain(PacketPokerTable(id = 1,
                                                              betting_structure = '1-2-no-limit',
                                                              variant = 'holdem')))
        self.assertNotEqual(game, self.explain.games.getGame(1))

    def test21_explain_serial(self):
        self.explain.explain(PacketSerial(serial = 42))
        self.assertEqual(42, self.explain.serial)

    def test22_explain_error(self):
        self.failIf(self.explain.explain(PacketError()))

    def test23_explain_table_destroy(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        self.explain.explain(PacketPokerTableDestroy(game_id = game_id))

    def test24_explain_start(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))

        poker_start = PacketPokerStart(game_id = game_id, hand_serial = 0)

        self.explain.explain(poker_start)
        self.assertEqual([], self.explain.forward_packets)

        poker_start.hand_serial = 1
        game.state = "plop"
        self.failUnlessRaises(UserWarning, self.explain.explain, poker_start)

        game.state = pokergame.GAME_STATE_NULL

        call = []
        game.beginTurn = lambda serial: call.append('beginTurn')
        game.player_list = [ player_serial ]
        packets = self.explain.explain(poker_start)
        self.assertEqual(['beginTurn'], call)

    def test25_explain_canceled(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        player.bet = 10

        amount = 1
        self.assertTrue(self.explain.explain(PacketPokerCanceled(game_id = game_id,
                                                                 serial = player_serial,
                                                                 amount = amount)))
        self.assertEqual(6, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_CANCELED, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_CHIPS_BET2POT, self.explain.forward_packets[1].type)
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, self.explain.forward_packets[2].type)
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, self.explain.forward_packets[3].type)

        # test without explain chipstack
        self.explain.forward_packets = []
        self.explain.what = PacketPokerExplain.REST
        self.assertTrue(self.explain.explain(PacketPokerCanceled(game_id = game_id,
                                                                 serial = player_serial,
                                                                 amount = amount)))
        self.assertEqual(5, len(self.explain.forward_packets))

    def test26_explain_player_arrive(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.assertTrue(self.explain.explain(PacketPokerPlayerArrive(game_id = game_id,
                                                                     serial = player_serial,
                                                                     seat = 2,
                                                                     name = 'name',
                                                                     url = 'url',
                                                                     outfit = 'outfit',
                                                                     auto_blind_ante = 1,
                                                                     wait_for = 0)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_PLAYER_ARRIVE, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_SEATS, self.explain.forward_packets[1].type)

    def test26_1_explain_player_arrive_no_seats_left(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        game.seats_left = []
        player_serial = 3
        self.assertTrue(self.explain.explain(PacketPokerPlayerArrive(game_id = game_id,
                                                                     serial = player_serial,
                                                                     seat = 2,
                                                                     name = 'name',
                                                                     url = 'url',
                                                                     outfit = 'outfit',
                                                                     auto_blind_ante = 1,
                                                                     wait_for = 0)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_PLAYER_ARRIVE, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_SEATS, self.explain.forward_packets[1].type)

    def test27_explain_player_leave(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        self.assertTrue(self.explain.explain(PacketPokerPlayerLeave(game_id = game_id,
                                                                    serial = player_serial)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_PLAYER_LEAVE, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_SEATS, self.explain.forward_packets[1].type)

    def test27_explain_table_move(self):
        game_id = 1
        to_game_id = 10
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        self.assertTrue(self.explain.explain(PacketPokerTableMove(game_id = game_id,
                                                                  to_game_id = to_game_id,
                                                                  serial = player_serial)))
        self.assertEqual(3, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_TABLE_MOVE, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_PLAYER_LEAVE, self.explain.forward_packets[1].type)
        self.assertEqual(PACKET_POKER_SEATS, self.explain.forward_packets[2].type)

    def test27_explain_player_self_leave(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        self.explain.explain(PacketSerial(serial = player_serial))
        self.assertTrue(self.explain.explain(PacketPokerPlayerLeave(game_id = game_id,
                                                                    serial = player_serial)))
        self.assertEqual(False, self.explain.games.getGame(game_id))

    def test28_explain_player_self(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        self.explain.updateBetLimit = lambda game: [Packet()]
        player_serial = 3
        game.position_info = [ player_serial, False ]
        self.explain.serial = player_serial
        self.assertTrue(self.explain.explain(PacketPokerPlayerSelf(game_id = game_id,
                                                                   serial = player_serial)))
        self.assertEqual(PACKET_POKER_PLAYER_SELF, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_NONE, self.explain.forward_packets[1].type)

    def test29_explain_position(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        game.current_round = -1
        game.state = pokergame.GAME_STATE_PRE_FLOP
        player_serial = 3
        game.player_list = [ player_serial ]
        self.assertTrue(self.explain.explain(PacketPokerPosition(game_id = game_id,
                                                                 position = 0)))
        self.assertEqual(PACKET_POKER_POSITION, self.explain.forward_packets[0].type)
        self.assertEqual(player_serial, self.explain.forward_packets[0].serial)

    def test30_explain_setters(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        #
        # PacketPokerSeats
        #
        self.assertTrue(self.explain.explain(PacketPokerSeats(game_id = game_id)))
        self.assertEqual([], self.explain.forward_packets)
        #
        # PacketPokerPlayerCards
        #
        self.assertTrue(self.explain.explain(
            PacketPokerPlayerCards(game_id = game_id,
                                   serial = player_serial,
                                   cards = [ 1 ])
            ))
        self.assertEqual(PACKET_POKER_PLAYER_CARDS, self.explain.forward_packets[0].type)
        #
        # PacketPokerBoardCards
        #
        self.assertTrue(self.explain.explain(
            PacketPokerBoardCards(game_id = game_id,
                                  cards = [ 1 ])
            ))
        self.assertEqual(PACKET_POKER_BOARD_CARDS, self.explain.forward_packets[0].type)
        #
        # PacketPokerDealer
        #
        self.assertTrue(self.explain.explain(
            PacketPokerDealer(game_id = game_id,
                              dealer = 1)
            ))
        self.assertEqual(PACKET_POKER_DEALER, self.explain.forward_packets[0].type)
        #
        # PacketPokerSitOut
        #
        player.sit_out = False
        self.failUnless(player.isSit())
        self.assertTrue(self.explain.explain(
            PacketPokerSitOut(game_id = game_id,
                              serial = player_serial)
            ))
        self.assertEqual(PACKET_POKER_SIT_OUT, self.explain.forward_packets[0].type)
        self.failUnless(player.isSitOut())
        #
        # PacketPokerSit
        #
        player.buy_in_payed = True
        player.money = 10000
        player.sit_out = True
        self.failIf(player.isSit())
        self.assertTrue(self.explain.explain(
            PacketPokerSit(game_id = game_id,
                           serial = player_serial)
            ))
        self.assertEqual(PACKET_POKER_SIT, self.explain.forward_packets[0].type)
        self.failUnless(player.isSit())
        #
        # PacketPokerAutoFold
        #
        self.failIf(player.isAuto())
        self.assertTrue(self.explain.explain(
            PacketPokerAutoFold(game_id = game_id,
                               serial = player_serial)
            ))
        self.assertEqual(PACKET_POKER_AUTO_FOLD, self.explain.forward_packets[0].type)
        self.failUnless(player.isAuto())
        #
        # PacketPokerAutoBlindAnte
        #
        self.failIf(player.isAutoBlindAnte())
        self.assertTrue(self.explain.explain(
            PacketPokerAutoBlindAnte(game_id = game_id,
                                     serial = player_serial)
            ))
        self.assertEqual(PACKET_POKER_AUTO_BLIND_ANTE, self.explain.forward_packets[0].type)
        self.failUnless(player.isAutoBlindAnte())
        #
        # PacketPokerNoautoBlindAnte
        #
        player.auto_blind_ante = True
        self.failUnless(player.isAutoBlindAnte())
        self.assertTrue(self.explain.explain(
            PacketPokerNoautoBlindAnte(game_id = game_id,
                                       serial = player_serial)
            ))
        self.assertEqual(PACKET_POKER_NOAUTO_BLIND_ANTE, self.explain.forward_packets[0].type)
        self.failIf(player.isAutoBlindAnte())
        #
        # PacketPokerMuckRequest
        #
        self.assertTrue(self.explain.explain(
            PacketPokerMuckRequest(game_id = game_id,
                                   muckable_serials = [player_serial])
            ))
        self.assertEqual(PACKET_POKER_MUCK_REQUEST, self.explain.forward_packets[0].type)
        self.assertEqual([player_serial], game.muckable_serials)
        #
        # PacketPokerRake
        #
        game.getRakeContributions = lambda: 0
        rake_amount = 101
        self.assertTrue(self.explain.explain(
            PacketPokerRake(game_id = game_id,
                            value = rake_amount)
            ))
        self.assertEqual(PACKET_POKER_RAKE, self.explain.forward_packets[0].type)
        self.assertEqual(rake_amount, game.raked_amount)

    def test31_explain_game_action(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        #
        # fold
        #
        fold = []
        game.fold = lambda serial: fold.append('fold')
        game.isSitOut = lambda serial: fold.append('isSitOut') or True
        self.assertTrue(self.explain.explain(PacketPokerFold(game_id = game_id)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(['fold', 'isSitOut'], fold)
        #
        # call
        #
        call = []
        game.call = lambda serial: call.append('call')
        self.assertTrue(self.explain.explain(PacketPokerCall(game_id = game_id)))
        self.assertEqual(['call'], call)
        #
        # check
        #
        check = []
        game.check = lambda serial: check.append('check')
        self.assertTrue(self.explain.explain(PacketPokerCheck(game_id = game_id)))
        self.assertEqual(['check'], check)
        #
        # raise
        #
        _raise = []
        game.callNraise = lambda serial, amount: _raise.append(amount)
        raise_amount = 303
        self.assertTrue(self.explain.explain(PacketPokerRaise(game_id = game_id,
                                                              amount = raise_amount)))
        self.assertEqual([raise_amount], _raise)
        #
        # blind
        #
        blind = []
        game.blind = lambda serial, amount, dead: blind.append(amount)
        blind_amount = 404
        self.assertTrue(self.explain.explain(PacketPokerBlind(game_id = game_id,
                                                              amount = blind_amount)))
        self.assertEqual([blind_amount], blind)
        #
        # ante
        #
        ante = []
        game.ante = lambda serial, amount: ante.append(amount)
        ante_amount = 505
        self.assertTrue(self.explain.explain(PacketPokerAnte(game_id = game_id,
                                                             amount = ante_amount)))
        self.assertEqual([ante_amount], ante)
        #
        # blind_request
        #
        blind_request = []
        game.setPlayerBlind = lambda serial, state: blind_request.append(state)
        blind_state = "small"
        self.assertTrue(self.explain.explain(PacketPokerBlindRequest(game_id = game_id,
                                                                     state = blind_state)))
        self.assertEqual([blind_state], blind_request)

    def test32_explain_state_flop(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        game.player_list = [player_serial]
        self.explain.moveBet2Pot = lambda game: ['moveBet2Player']
        game_actions = []
        game.initRound = lambda: game_actions.append('initRound')
        game.isRunning = lambda: game_actions.append('isRunning') or True
        game.cardsDealt = lambda: game_actions.append('cardsDealt') or True
        game.serialsNotFold = lambda: game_actions.append('serialsNotFold') or [player_serial]
        down_cards_count = 1
        game.downCardsDealtThisRoundCount = lambda: game_actions.append('downCardsDealtThisRoundCount') or down_cards_count
        cards_count = 2
        game.cardsDealtThisRoundCount = lambda: game_actions.append('cardsDealtThisRoundCount') or cards_count
        self.assertTrue(self.explain.explain(PacketPokerState(game_id = game_id,
                                                              string = pokergame.GAME_STATE_FLOP)))
        self.assertEqual(6, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_STATE, self.explain.forward_packets[0].type)
        self.assertEqual('moveBet2Player', self.explain.forward_packets[1])
        self.assertEqual(PACKET_POKER_DEAL_CARDS, self.explain.forward_packets[2].type)
        self.assertEqual(down_cards_count, self.explain.forward_packets[2].numberOfCards)
        self.assertEqual(PACKET_POKER_PLAYER_CARDS, self.explain.forward_packets[3].type)
        self.assertEqual([], self.explain.forward_packets[3].cards)
        self.assertEqual(PACKET_POKER_BEGIN_ROUND, self.explain.forward_packets[4].type)
        self.assertEqual(PACKET_POKER_POSITION, self.explain.forward_packets[5].type)
        self.assertEqual(player_serial, self.explain.forward_packets[5].serial)

    def test33_explain_state_end(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        game.player_list = [player_serial]
        self.explain.moveBet2Player = lambda game: ['moveBet2Player']
        game_actions = []
        game.isSingleUncalledBet = lambda side_pots: game_actions.append('isSingleUncalledBet') or True

        self.assertTrue(self.explain.explain(PacketPokerState(game_id = game_id,
                                                              string = pokergame.GAME_STATE_END)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual('moveBet2Player', self.explain.forward_packets[1])

        game_actions = []
        game.isFirstRound = lambda: True
        game.isBlindAnteRound = lambda: True
        game.blindAnteRoundEnd = lambda: game_actions.append('blindAnteRoundEnd')
        game.isRunning = lambda: False
        game.initRound = lambda: game_actions.append('initRound')
        game.state = pokergame.GAME_STATE_FLOP
        game.endState = lambda: game_actions.append('endState')
        self.assertTrue(self.explain.explain(PacketPokerState(game_id = game_id,
                                                              string = pokergame.GAME_STATE_END)))
        self.assertEqual(1, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_STATE, self.explain.forward_packets[0].type)
        self.assertEqual(['blindAnteRoundEnd', 'endState', 'initRound'], game_actions)

    def test34_explain_in_game(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        player.buy_in_payed = True
        player.money = 10000
        #
        # player in game and wait for
        #
        player.wait_for = True
        self.assertTrue(self.explain.explain(PacketPokerInGame(game_id = game_id,
                                                               players = [player_serial])))
        self.assertEqual(3, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_IN_GAME, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_SIT, self.explain.forward_packets[1].type)
        self.assertEqual(PACKET_POKER_WAIT_FOR, self.explain.forward_packets[2].type)
        self.assertEqual([player_serial], game.getStaticPlayerList())

        #
        # player not in game and wait for
        #
        self.assertTrue(self.explain.explain(PacketPokerInGame(game_id = game_id,
                                                               players = [])))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_IN_GAME, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_WAIT_FOR, self.explain.forward_packets[1].type)
        #
        # player not in game and not wait for
        #
        player.wait_for = False
        self.assertTrue(self.explain.explain(PacketPokerInGame(game_id = game_id,
                                                               players = [])))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_IN_GAME, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_SIT_OUT, self.explain.forward_packets[1].type)
        #
        # player in game and auto
        #
        player.auto = True
        player.sit_out = True
        self.assertTrue(self.explain.explain(PacketPokerInGame(game_id = game_id,
                                                               players = [player_serial])))
        self.assertEqual(3, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_IN_GAME, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_SIT, self.explain.forward_packets[1].type)
        self.assertEqual(PACKET_POKER_AUTO_FOLD, self.explain.forward_packets[2].type)

    def test35_explain_wait_for(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        wait_for = "big"
        self.assertTrue(self.explain.explain(PacketPokerWaitFor(game_id = game_id,
                                                                serial = player_serial,
                                                                reason = wait_for)))
        self.assertEqual(0, len(self.explain.forward_packets))
        self.assertEqual(player.wait_for, wait_for)

    def test36_explain_timeout(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        player.setUserData({ 'timeout': None })
        #
        # timeout = 33
        #
        timeout = 33
        self.assertTrue(self.explain.explain(PacketPokerTimeoutWarning(game_id = game_id,
                                                                       serial = player_serial,
                                                                       timeout = timeout)))
        self.assertEqual(1, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_TIMEOUT_WARNING, self.explain.forward_packets[0].type)
        self.assertEqual(timeout, player.getUserData()['timeout'][1])
        #
        # timeout = 0
        #
        self.assertTrue(self.explain.explain(PacketPokerTimeoutWarning(game_id = game_id,
                                                                       serial = player_serial,
                                                                       timeout = 0)))
        self.assertEqual(0, len(self.explain.forward_packets))
        #
        # unset the player timeout when the deconnection notice comes
        #
        self.assertTrue(self.explain.explain(PacketPokerTimeoutNotice(game_id = game_id,
                                                                      serial = player_serial)))
        self.assertEqual(1, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_TIMEOUT_NOTICE, self.explain.forward_packets[0].type)
        self.assertEqual(None, player.getUserData()['timeout'])

    def test37_explain_rebuy(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        rebuy = []
        game.rebuy = lambda serial, amount: rebuy.append(amount) or True
        amount = 11
        self.assertTrue(self.explain.explain(PacketPokerRebuy(game_id = game_id,
                                                              serial = player_serial,
                                                              amount = amount)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, self.explain.forward_packets[1].type)

        # test without explain chipstack
        self.explain.forward_packets = []
        self.explain.what = PacketPokerExplain.REST
        self.assertTrue(self.explain.explain(PacketPokerRebuy(game_id = game_id,
                                                              serial = player_serial,
                                                              amount = amount)))
        self.assertEqual(1, len(self.explain.forward_packets))

    def test38_explain_player_chips(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 3
        self.failUnless(game.addPlayer(player_serial, 1))
        player = game.getPlayer(player_serial)
        bet = 12
        money = 23
        #
        # set the money/bet
        #
        self.assertTrue(self.explain.explain(PacketPokerPlayerChips(game_id = game_id,
                                                                    serial = player_serial,
                                                                    money = money - 1,
                                                                    bet = bet - 1)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, self.explain.forward_packets[0].type)
        self.assertEqual(money - 1, player.money)
        self.assertEqual(bet - 1, player.bet)
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, self.explain.forward_packets[1].type)
        self.assertEqual([1, 7, 2, 2], self.explain.forward_packets[1].bet)
        self.assertEqual([1, 7, 2, 5, 5, 1], self.explain.forward_packets[1].money)

        self.failUnless(player.isBuyInPayed())
        #
        # override the money/bet
        #
        self.assertTrue(self.explain.explain(PacketPokerPlayerChips(game_id = game_id,
                                                                    serial = player_serial,
                                                                    money = money,
                                                                    bet = bet)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_PLAYER_CHIPS, self.explain.forward_packets[0].type)
        self.assertEqual(money, player.money)
        self.assertEqual(bet, player.bet)
        self.assertEqual(PACKET_POKER_CLIENT_PLAYER_CHIPS, self.explain.forward_packets[1].type)
        self.assertEqual([1, 6, 2, 3], self.explain.forward_packets[1].bet)
        self.assertEqual([1, 6, 2, 6, 5, 1], self.explain.forward_packets[1].money)

        # test without explain chipstack
        self.explain.forward_packets = []
        self.explain.what = PacketPokerExplain.REST
        self.assertTrue(self.explain.explain(PacketPokerPlayerChips(game_id = game_id,
                                                                    serial = player_serial,
                                                                    money = money,
                                                                    bet = bet)))
        self.assertEqual(1, len(self.explain.forward_packets))

    def test39_explain_win(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        game.isGameEndInformationValid = lambda: True
        self.explain.packetsPot2Player = lambda game: ['packetsPot2Player' ]
        #
        # winners are known
        #
        game.winners = [1]
        self.assertTrue(self.explain.explain(PacketPokerWin(game_id = game_id,
                                                            serials = [1])))
        self.assertEqual(5, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_WIN, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_PLAYER_WIN, self.explain.forward_packets[1].type)
        self.assertEqual(PACKET_POKER_SHOWDOWN, self.explain.forward_packets[2].type)
        self.assertEqual('packetsPot2Player', self.explain.forward_packets[3])
        self.assertEqual(PACKET_POKER_POSITION, self.explain.forward_packets[4].type)
        #
        # winners in packet and computed from the game are inconsistant
        #
        game.winners = []
        game.distributeMoney = lambda: game.winners.append(1)
        self.failUnlessRaises(UserWarning, self.explain.explain, PacketPokerWin(game_id = game_id, serials = [3]))

        #
        # winners are not known
        #
        game.winners = []
        game.endTurn = lambda: True
        self.explain.packetsShowdown = lambda game: ['packetsShowdown']
        self.assertTrue(self.explain.explain(PacketPokerWin(game_id = game_id, serials = [1])))
        self.assertEqual(6, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_WIN, self.explain.forward_packets[0].type)
        self.assertEqual(PACKET_POKER_PLAYER_WIN, self.explain.forward_packets[1].type)
        self.assertEqual('packetsShowdown', self.explain.forward_packets[2])
        self.assertEqual(PACKET_POKER_SHOWDOWN, self.explain.forward_packets[3].type)
        self.assertEqual('packetsPot2Player', self.explain.forward_packets[4])
        self.assertEqual(PACKET_POKER_POSITION, self.explain.forward_packets[5].type)

    def test40_explain_position(self):
        game_id = 1
        game = self.explain.games.getOrCreateGame(game_id)
        player_serial = 1
        self.explain.serial = player_serial
        self.explain.unsetPlayerTimeout = lambda game, serial: True
        game.isRunning = lambda: True
        #
        # game running, position is obsolete and self is in position
        #
        game.position_info = [player_serial, True]
        game.getSerialInPosition = lambda: player_serial
        self.assertTrue(self.explain.explain(PacketPokerId(game_id = game_id)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_SELF_IN_POSITION, self.explain.forward_packets[1].type)
        self.assertEqual(player_serial, self.explain.forward_packets[1].serial)
        #
        # game running, position is not osbolete and self lost its position to another player
        #
        game.position_info = [player_serial, False]
        other_player_serial = 75
        game.getSerialInPosition = lambda: other_player_serial
        other_player_position = 3
        game.position = other_player_position
        self.assertTrue(self.explain.explain(PacketPokerId(game_id = game_id)))
        self.assertEqual(3, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_POSITION, self.explain.forward_packets[1].type)
        self.assertEqual(other_player_serial, self.explain.forward_packets[1].serial)
        self.assertEqual(other_player_position, self.explain.forward_packets[1].position)
        self.assertEqual(PACKET_POKER_SELF_LOST_POSITION, self.explain.forward_packets[2].type)
        self.assertEqual(other_player_serial, self.explain.forward_packets[2].serial)
        #
        # game running, position is not obsolete and self lost its position
        #
        game.position_info = [player_serial, False]
        game.getSerialInPosition = lambda: 0
        self.assertTrue(self.explain.explain(PacketPokerId(game_id = game_id)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_SELF_LOST_POSITION, self.explain.forward_packets[1].type)
        #
        # game not running, self in position
        #
        game.position_info = [player_serial, False]
        game.isRunning = lambda: False
        self.assertTrue(self.explain.explain(PacketPokerId(game_id = game_id)))
        self.assertEqual(2, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_SELF_LOST_POSITION, self.explain.forward_packets[1].type)

    def test41_explain_state_flop_hand_strength(self):
        game_id = 1
        self.explain.explain(PacketPokerTable(id = game_id,
                                              betting_structure = '1-2-no-limit',
                                              variant = 'holdem'))
        def addPlayer(player_serial, seat):
            self.explain.explain(PacketPokerPlayerArrive(game_id = game_id,
                                                         serial = player_serial,
                                                         seat = seat,
                                                         name = 'name',
                                                         url = 'url',
                                                         outfit = 'outfit',
                                                         auto_blind_ante = 1,
                                                         wait_for = 0))
            self.explain.explain(PacketPokerPlayerChips(game_id = game_id,
                                                        serial = player_serial,
                                                        money = 20000))
            self.explain.explain(PacketPokerSit(game_id = game_id,
                                                serial = player_serial))
        addPlayer(42, 1)
        addPlayer(43, 2)
        self.explain.explain(PacketSerial(serial = 42))
        self.explain.explain(PacketPokerInGame(game_id = game_id,
                                               players = [42, 43]))
        self.explain.explain(PacketPokerStart(game_id = game_id, hand_serial = 11))
        self.explain.explain(PacketPokerPlayerCards(game_id = game_id,
                                                    serial = 42,
                                                    cards = [ 1, 2 ]))
        self.explain.explain(PacketPokerPlayerCards(game_id = game_id,
                                                    serial = 43,
                                                    cards = [ 3, 4 ]))
        self.explain.explain(PacketPokerState(game_id = game_id,
                                              string = pokergame.GAME_STATE_PRE_FLOP))
        self.explain.explain(PacketPokerCheck(game_id = game_id, serial = 43))
        self.explain.explain(PacketPokerCheck(game_id = game_id, serial = 42))
        self.explain.explain(PacketPokerBoardCards(game_id = game_id,
                                                   cards = [ 5, 6, 7 ]))
        self.explain.explain(PacketPokerState(game_id = game_id,
                                              string = pokergame.GAME_STATE_FLOP))
        self.assertEqual(7, len(self.explain.forward_packets))
        self.assertEqual(PACKET_POKER_PLAYER_HAND_STRENGTH, self.explain.forward_packets[2].type)
        self.assertEqual('Flush Nine high: 9h, 8h, 7h, 4h, 3h', self.explain.forward_packets[2].hand)

    def test42_explain_state_flop_hand_strength_not_in_game(self):
        game_id = 1
        self.explain.explain(PacketPokerTable(id = game_id,
                                              betting_structure = '1-2-no-limit',
                                              variant = 'holdem'))
        def addPlayer(player_serial, seat):
            self.explain.explain(PacketPokerPlayerArrive(game_id = game_id,
                                                         serial = player_serial,
                                                         seat = seat,
                                                         name = 'name',
                                                         url = 'url',
                                                         outfit = 'outfit',
                                                         auto_blind_ante = 1,
                                                         wait_for = 0))
            self.explain.explain(PacketPokerPlayerChips(game_id = game_id,
                                                        serial = player_serial,
                                                        money = 20000))
            self.explain.explain(PacketPokerSit(game_id = game_id,
                                                serial = player_serial))
        addPlayer(42, 1)
        addPlayer(43, 2)
        self.explain.explain(PacketSerial(serial = 44))
        self.explain.explain(PacketPokerInGame(game_id = game_id,
                                               players = [42, 43]))
        self.explain.explain(PacketPokerStart(game_id = game_id, hand_serial = 11))
        self.explain.explain(PacketPokerPlayerCards(game_id = game_id,
                                                    serial = 42,
                                                    cards = [ 1, 2 ]))
        self.explain.explain(PacketPokerPlayerCards(game_id = game_id,
                                                    serial = 43,
                                                    cards = [ 3, 4 ]))
        self.explain.explain(PacketPokerState(game_id = game_id,
                                              string = pokergame.GAME_STATE_PRE_FLOP))
        self.explain.explain(PacketPokerCheck(game_id = game_id, serial = 43))
        self.explain.explain(PacketPokerCheck(game_id = game_id, serial = 42))
        self.explain.explain(PacketPokerBoardCards(game_id = game_id,
                                                   cards = [ 5, 6, 7 ]))
        self.explain.explain(PacketPokerState(game_id = game_id,
                                              string = pokergame.GAME_STATE_FLOP))
        self.assertEqual(5, len(self.explain.forward_packets))
        for packet in self.explain.forward_packets:
            self.assertNotEqual(PACKET_POKER_PLAYER_HAND_STRENGTH, packet.type)

# ----------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test42"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerGamesTestCase))
    suite.addTest(loader.loadClass(PokerExplainTestCase))
    return runner.TrialRunner(
        reporter.VerboseTextReporter,
        tracebackFormat='default',
        ).run(suite)

# ----------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokerexplain.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerexplain.py' VERBOSE_T=6 TESTS='coverage-reset test-pokerexplain.py coverage-report' check )"
# End:

