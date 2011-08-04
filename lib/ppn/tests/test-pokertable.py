#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2006, 2007, 2008       Loic Dachary <loic@dachary.org>
# Copyright (C)             2008, 2009 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C)                   2009 Johan Euphrosine <proppy@aminche.com>
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
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

import libxml2
from pprint import pprint
from string import split
import time

from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor, defer

from random import seed, randint
import copy

twisted.internet.base.DelayedCall.debug = True

#
# Must be done before importing pokerclient or pokerclient
# will have to be patched too.
#
from tests import testclock

from tests.testmessages import restore_all_messages, silence_all_messages, search_output, clear_all_messages, get_messages, redirect_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
silence_all_messages()

from pokerengine import pokertournament
from pokernetwork import pokertable, pokernetworkconfig
from pokernetwork.pokerpackets import *
from pokernetwork.pokeravatar import DEFAULT_PLAYER_USER_DATA, PokerAvatar
from pokerengine.pokercards import PokerCards

global table1ID
global table2ID
table1ID = 100
table2ID = 200
settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="4" autodeal="yes" max_missed_round="5">
  <delays autodeal_tournament_min="2" autodeal="2" autodeal_max="2" autodeal_check="0" round="0" position="0" showdown="0" finish="0" />

  <path>%s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % SCRIPT_DIR
settings_stripped_deck_no_autodeal_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="4" autodeal="no" >
  <delays autodeal_tournament_min="2" autodeal="2" autodeal_max="2" autodeal_check="0" round="0" position="0" showdown="0" finish="0" />

  <decks>
    <deck>9c 9d 9h Ts Tc Td Th Ts Jc Jd Jh Js Qc Qd Qh Qs Kc Kd Kh Ks Ac Ad Ah As</deck>
  </decks>

  <path>%s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % SCRIPT_DIR

board = PokerCards()
hand1 = PokerCards(['Qd', 'Ts'])
hand2 = PokerCards(['Kh', 'Kc'])
hand1_extra_river = PokerCards(['Qd', 'Ts', '9c'])
hand2_extra_river = PokerCards(['Qd', 'Ts', '9h'])
flop  = PokerCards(['Jd', 'Js', "Jc"])
turn  = PokerCards(['Tc', 'Js', 'Jc', 'Tc'])
river  = PokerCards(['Tc', 'Js', 'Jc', 'Tc', 'Ad'])
river_extra_river  = PokerCards(['Tc', 'Js', 'Jc', 'Tc', 'Ad', '9d'])

exampleHand =  [ \
        ('wait_for', 1, 'first_round'), \
        ('player_list', [1, 2]), \
        ('round', 'round1', board, { 1 : hand1, 2 : hand2}), \
        ('round', 'round2', flop, { 1 : hand1, 2 : hand2}), \
        ('round', 'round3', turn, { 1 : hand1, 2 : hand2}), \
        ('round', 'round4', river, { 1 : hand1, 2 : hand2}), \
# Round 5 doesn't changed the board to test certain code in
# compressedHistory: it expects that if you haven't changed the board in a
# new round, the history gives you "None"
        ('round', 'round5', river, { 1 : hand1, 2 : hand2}), \
        ('showdown', river, {1 : hand1, 2 : hand2}), \
        ('showdown', river_extra_river, {1 : hand1_extra_river, 2 : hand2_extra_river}), \
        ('position', 1), \
        ('blind_request', 1, 222, 735, 'big_and_dead'), \
        ('wait_blind', 1), \
        ('blind', 1, 222, 0), \
        ('ante_request', 1, 111), \
        ('ante', 1, 111), \
        ('ante', 5, 555), \
        ('all-in', 1), \
        ('call', 1, 411), \
        ('call', 6, 626), \
        ('check', 1), \
        ('fold', 1), \
        ('raise', 1, 888, 888, 666), \
# Note: 3 appears first here to test something appearing first as a raise.
        ('raise', 10, 976, 976, 754), \
        ('canceled', 4, 10), \
        ('rake', 7, { 1 : 7}), \
        ('end', [8, 1], [{ 'serial2share': { 8: 888, 1: 233 } }]), \
        ('sitOut', 1), \
        ('leave', [(1, 2), (2, 7)]), \
        ('finish', 1), \
        ('muck', (1,2)), \
        ('rebuy', 1, 9999), \
        ('unknown',) ]
def convertHandHistoryToDict (hist):
    dict = {}
    for entry in hist:
        key = entry[0]
        dict[key] = entry[1:-1]
    return dict

class MockService:

    def __init__(self, settings):
        self.settings = settings
        self.verbose = settings.headerGetInt("/server/@verbose")
        self.dirs = split(settings.headerGet("/server/path"))
        self.simultaneous = 1
        self.shutting_down = False
        self.hand_serial = 0
        self.hands = {}
        self.chat = False
        self.players = {}
        self.table1 = None
        self.table2 = None
        self.testObject = None
        self.joined_count = 0
        self.joined_max = 1000
        self.chat_messages = []

    def getMissedRoundMax(self):
        return 5  # if you change this, change it in settings_xml above

    # Just copied these joinedCount functions from the real service.
    def joinedCountReachedMax(self):
        """Returns True iff. the number of joins to tables has exceeded
        the maximum allowed by the server configuration"""
        return self.joined_count >= self.joined_max

    def joinedCountIncrease(self, num = 1):
        """Increases the number of currently joins to tables by num, which
        defaults to 1."""
        self.joined_count += num
        return self.joined_count

    def joinedCountDecrease(self, num = 1):
        """Decreases the number of currently joins to tables by num, which
        defaults to 1."""
        self.joined_count -= num
        return self.joined_count

    def getTable(self, gameId):
        if gameId == self.table1.game.id:
            return self.table1
        elif gameId == self.table2.game.id:
            return self.table2
        else:
            self.error("Unknown game requested: " + gameId)
            return None

    def message(self, message):
        print "MockService " + message

    def getName(self, serial):
        return "MockServiceName%d" % serial

    def getPlayerInfo(self, serial):
        class Dummy:
            def __init__(self):
                self.name = "MockServicePlayerInfo"
                self.url = "MockServicePlayerInfo.url"
                self.outfit = "MockServicePlayerInfo.outfit"
        return Dummy()

    def error(self, message):
        self.message("error " + message)

    def movePlayer(self, serial, fromGameId, toGameId):
        return 0

    def seatPlayer(self, serial, table_id, amount):
        if self.players.has_key(serial):
            self.error("Player is already seated at table, ." % table_id)
            return False
        else:
            self.players[serial] = { 'table_id' : table_id, 'amount' : amount }
            return True

    def buyInPlayer(self, serial, game_id, currency_serial, amount):
        if serial == 9 and amount != 1000 and amount != 100000000:
            return 0
        else:
            return amount

    def getHandSerial(self):
        self.hand_serial += 1
        return self.hand_serial

    def tableMoneyAndBet(self, table_id):
        return (0, 500)

    def leavePlayer(self, serial, table_id, currency_serial):
        if self.players.has_key(serial):
            del self.players[serial]
            return True
        else:
            self.error("Player is already seated at table, %d." % table_id)
            return False

    def deleteTable(self, x):
        pass

    def destroyTable(self, x):
        pass

    def eventTable(self, table):
        pass

    def updateTableStats(self, game, observers, waiting):
        pass

    def loadHand(self, handId, removeList = []):
        # Only ever return the one hand; the only one this mock game ever had...
        #  ... but only if they give a positive integer as a handId.
        if handId <= 0:
            return None
        else:
            l = copy.deepcopy(exampleHand)
            # Remove anything that this specific test wants to get rid of,
            # perhaps because it messes with their results.
            for xx in removeList:
                l.remove(xx)
            l.insert(0, ('game', 1, handId, 3, time.time(), 'variant','betting_structure', [1, 2], 7, { 1 : 7890, 2 : 1234, 'values' : ''}))
            self.hands[handId] = convertHandHistoryToDict(l)
            return l

    def saveHand(self, history, serial):
        if self.testObject:
            historyDict = convertHandHistoryToDict(history)
            handId = historyDict['game'][1]
            origDict = self.hands[handId]
            for (action, fields) in historyDict.iteritems():
                if action == "showdown":
                    self.testObject.failUnless(fields == (None,) or fields == (PokerCards([34, 48, 35, 34, 25, 20]),))
                elif action == "round" and fields[0] == "round5":
                    self.testObject.assertEqual(fields, ('round5', None,))
                else:
                    self.testObject.assertEqual(origDict[action], fields)

    def updatePlayerMoney(self, serial, gameId, amount):
        # Most of this function matches up with the false hand history above
        #  Compare it to that when figuring out where these numbers come from,
        #  except for serial 3, which is based on the ante he makes in test21
        if self.testObject:
            self.testObject.assertEqual(gameId,  self.testObject.table1_value)
            if serial == 1:
                self.testObject.assertEqual(amount,  -1399)
            elif serial == 3:
                self.testObject.assertEqual(amount,  -100)
            elif serial == 10:
                self.testObject.assertEqual(amount,  -976)
            elif serial == 4:
                self.testObject.assertEqual(amount,  10)
            elif serial == 5:
                self.testObject.assertEqual(amount,  -555)
            elif serial == 6:
                self.testObject.assertEqual(amount,  -626)
            elif serial == 8:
                self.testObject.assertEqual(amount,  888)
            else:
                self.testObject.fail("Unkown serial in hand history: %d" % serial)

    def updatePlayerRake(self, currencySerial, serial, rakeAmount):
        if self.testObject:
            self.testObject.assertEqual(rakeAmount,  7)
            self.testObject.assertEqual(serial,  1)

    def tourneyEndTurn(self, tourney, game_id):
        if self.testObject:
            self.testObject.assertEqual(game_id,  self.testObject.table1_value)
            self.testObject.assertEqual(tourney.name,  'My Old Sit and Go')

    def resetBet(self, gameId):
        if self.testObject:
            self.testObject.assertEqual(gameId,  self.testObject.table1_value)

    def databaseEvent(self, event, param1, param2):
        if self.testObject:
            self.testObject.assertEqual(PacketPokerMonitorEvent.HAND, event)

    def chatMessageArchive(self, player_serial, game_id, message):
        self.chat_messages.append((player_serial, game_id, message))

if verbose < 0: redirect_messages(MockService)

class MockClient:
    class User:
        def isLogged(self):
            return True

    def __init__(self, serial, testObject, expectedReason = ""):
        self.serial = serial
        self.deferred = None
        self.raise_if_packet = None
        self.type = None
        self.tables = {}
        self.packets = []
        self.user = MockClient.User()
        self.testObject = testObject
        self.reasonExpected = expectedReason
        self.bugous_processing_hand = False

    def __str__(self):
        return "MockClient of Player%d" % self.serial

    def waitFor(self, type):
        self.deferred = defer.Deferred()
        self.type = type
        return self.deferred

    def raiseIfPacket(self, type):
        self.raise_if_packet = type

    def lookForPacket(self, type):
        for packet in self.packets:
            if packet.type == type:
                return packet
        return False

    def message(self, message):
        print "MockClient " + message

    def error(self, message):
        self.message("error " + message)

    def join(self, table, reason = ""):
        self.testObject.assertEquals(reason, self.reasonExpected)

    # Loic indicates that it's the job of the Client to pass along a few
    # things, including "player removes", and various clients settings, to
    # the game class.  These next few functions do that to be consistent
    # with what the pokertable API expects.

    def removePlayer(self, table, serial):
        if not self.tables.has_key(table.game.id):
            self.error("Table with game number %d does not occur exactly once for this player." % table.game.id)
        if serial == 9:
            table.game.removePlayer(serial)
            return False
        return table.game.removePlayer(serial)

    def autoBlindAnte(self, table, serial, auto):
        table.game.getPlayer(serial).auto_blind_ante = auto

    def sitPlayer(self, table, serial):
        table.game.sit(serial)

    def addPlayer(self, table, seat):
        self.tables[table.game.id] = table
        if table.game.addPlayer(self.serial, seat):
            player = table.game.getPlayer(self.serial)
            player.setUserData(DEFAULT_PLAYER_USER_DATA.copy())
        return True

    def sitOutPlayer(self, table, serial):
        table.game.sitOutNextTurn(serial)

    def sendPacket(self, packet):
        self.message("sendPacket: " + str(packet))
        self.packets.append(packet)
        if self.deferred:
            if self.raise_if_packet and packet.type == self.raise_if_packet:
                reactor.callLater(0, lambda: self.deferred.errback(packet))
            elif self.type == packet.type:
                reactor.callLater(0, lambda: self.deferred.callback(packet))

    def sendPacketVerbose(self, packet):
        self.sendPacket(packet)

    def getSerial(self):
        return self.serial

    def setMoney(self, table, amount):
        return table.game.payBuyIn(self.serial, amount)

    def getName(self):
        return "Player%d" % self.serial

    def getPlayerInfo(self):
        class MockPlayerInfo:
            def __init__(self, player):
                self.player = player
                self.name = self.player.getName()
                self.url = "http://fake"
                self.outfit = None
        return MockPlayerInfo(self)

if verbose < 0: redirect_messages(MockClient)

# --------------------------------------------------------------------------------
class MockClientBot(MockClient):
    def getName(self):
        return "BOT%d" % self.serial
# --------------------------------------------------------------------------------
class MockClientWithTableDict(MockClient):
    def __init__(self, serial, testObject):
        self.tables = {}
        MockClient.__init__(self, serial, testObject)

    def addPlayer(self, table, seat):
        MockClient.addPlayer(self, table, seat)
        self.tables[table.game.id] = seat
# --------------------------------------------------------------------------------
class MockClientWithRemoveTable(MockClient):
    def removeTable(self, gameId):
        return True
# --------------------------------------------------------------------------------
class MockClientWithRealJoin(MockClient, PokerAvatar):
    def join(self, table, reason=""):
        PokerAvatar.join(self, table, reason)

class PokerAvatarCollectionTestCase(unittest.TestCase):

    def test01(self):
        avatar_collection = pokertable.PokerAvatarCollection(prefix = '', verbose = 6)
        serial1 = 200
        serial2 = 400
        self.assertEquals([], avatar_collection.get(serial1))
        avatar1 = "a1"
        avatar2 = "a2"
        avatars = [ avatar1, avatar2 ]
        avatar_collection.set(serial1, avatars)
        self.assertRaises(AssertionError, avatar_collection.set, serial1, avatars)
        self.assertEquals(avatars, avatar_collection.get(serial1))
        avatar_collection.remove(serial1, avatar1)
        self.assertRaises(AssertionError, avatar_collection.remove, serial1, avatar1)
        self.assertEquals([avatar2], avatar_collection.get(serial1))
        avatar_collection.add(serial1, avatar2) # add twice is noop
        self.assertEquals([[avatar2]], avatar_collection.values())
        avatar_collection.add(serial1, avatar1)
        self.assertEquals([avatar2, avatar1], avatar_collection.get(serial1))
        avatar_collection.add(serial2, avatar1)
        self.assertEquals([avatar1], avatar_collection.get(serial2))
        avatar_collection.remove(serial2, avatar1)
        self.assertEquals([], avatar_collection.get(serial2))

# --------------------------------------------------------------------------------
class PokerTableTestCaseBase(unittest.TestCase):
    # -------------------------------------------------------------------
    def setUp(self, settingsXmlStr=settings_xml, ServiceClass = MockService):
        testclock._seconds_reset()
        global table1ID
        global table2ID
        table1ID = table1ID + 1
        table2ID += 1
        self.table1_value = table1ID
        self.table2_value = table2ID

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settingsXmlStr, len(settingsXmlStr))
        settings.header = settings.doc.xpathNewContext()
        self.service = ServiceClass(settings)
        self.table = pokertable.PokerTable(self.service, table1ID,
                                           { 'name': "table1",
                                             'variant': "holdem",
                                             'betting_structure': "2-4-limit",
                                             'seats': 4,
                                             'player_timeout' : 6,
                                             'muck_timeout' : 1,
                                             'currency_serial': 0,
                                             'max_missed_round' : 3
                                             })
        self.table2 = pokertable.PokerTable(self.service, table2ID,
                                           { 'name': "table2",
                                             'variant': "holdem",
                                             'betting_structure': "2-4-limit",
                                             'seats': 4,
                                             'player_timeout' : 6,
                                             'muck_timeout' : 1,
                                             'currency_serial': 0
                                             })
        self.service.table1 = self.table
        self.service.table2 = self.table2

        # Test to make sure that the max_missed_round count can be
        # overwritten by description in init settings.  note That table1
        # has setting of '1' for that value, but table2 accepts the
        # default above.
        self.assertEquals(self.table.max_missed_round, 3)
        self.assertEquals(self.table2.max_missed_round, 5)

        self.clients = {}
    # -------------------------------------------------------------------
    def tearDown(self):
        self.table.cancelDealTimeout()
        self.table.cancelPlayerTimers()
        del self.table
        del self.service
    # -------------------------------------------------------------------
    def createPlayer(self, serial, getReadyToPlay=True, clientClass=MockClient, table=None):
        if table == None:
            table = self.table
        client = clientClass(serial, self)
        client.service = self.service
        self.clients[serial] = client
        if getReadyToPlay:
            client.reasonExpected = "MockCreatePlayerJoin"
            self.assertEqual(True, table.joinPlayer(client, serial,
                                       reason  = "MockCreatePlayerJoin"))
            client.reasonExpected = ""
            self.assertEqual(True, table.seatPlayer(client, serial, -1))
            self.assertEqual(True, table.buyInPlayer(client, self.table.game.maxBuyIn()))
            self.table.sitPlayer(client, serial)
        return client
    # -------------------------------------------------------------------
    def createBot(self, serial, getReadyToPlay=True, clientClass=MockClientBot, table=None):
        return self.createPlayer(serial, getReadyToPlay, clientClass, table)
# --------------------------------------------------------------------------------
class PokerTableTestCase(PokerTableTestCaseBase):
    # -------------------------------------------------------------------
    def test01_autodeal(self):
        self.createPlayer(1)
        self.createPlayer(2)
        self.table.scheduleAutoDeal()
        return defer.DeferredList((self.clients[1].waitFor(PACKET_POKER_START),
                                   self.clients[2].waitFor(PACKET_POKER_START)))
    # -------------------------------------------------------------------
    def test01_5_autodealWithBots(self):
        """Test that autodeal won't happen when it's all bots sitting down.  I
        wish there was a packet we could catch here to confirm, but I
        can't even do a raise_if_packet because none are coming."""
        self.createBot(1)
        self.createBot(2)
        self.createBot(3)
        self.assertEquals(None, self.table.scheduleAutoDeal())
    # -------------------------------------------------------------------
    def test01_7_autodealShutDown(self):
        self.createPlayer(1)
        self.createPlayer(2)
        self.service.shutting_down = True
        self.assertEquals(None, self.table.scheduleAutoDeal())

    # -------------------------------------------------------------------
    def test01_8_testClientsBogusPokerProcessingHand(self):
        """Test specific situation in autodeal when poker clients send a Processing Hand before a Ready To Play"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
        self.table.processingHand(1)
        self.table.scheduleAutoDeal()
        threeGetsStart = self.clients[3].waitFor(PACKET_POKER_START)
        verboseVal = self.table.factory.verbose
        if self.table.factory.verbose < 2:
            self.table.factory.verbose = 2
        def checkValues(value):
            search_output('Player 1 marked as having a bugous PokerProcessingHand protocol')
            self.failUnless(player[1].bugous_processing_hand, "1 should have bugous_processing_hand")
            for ii in [ 2, 3, 4]:
                self.failIf(player[ii].bugous_processing_hand,
                            "%d should not have bugous_processing_hand" % ii)

        threeGetsStart.addCallback(checkValues)

        clear_all_messages()
        return defer.DeferredList((self.clients[2].waitFor(PACKET_POKER_START),
                                   threeGetsStart))
    # -------------------------------------------------------------------
    def test02_autodeal_check(self):
        self.createPlayer(1)
        self.table.processingHand(1)
        self.table.game_delay["delay"] = 2
        self.table.game_delay["start"] = testclock._seconds_value
        self.createPlayer(2)
        self.table.scheduleAutoDeal()
        return self.clients[2].waitFor(PACKET_POKER_MESSAGE)
    # -------------------------------------------------------------------
    def test_02_1_autodeal_destroy(self):
        self.createPlayer(1)
        self.createPlayer(2)
        self.table.processingHand(1)
        self.table.autoDealCheck(20, 10)
        dealTimeout = self.table.timer_info["dealTimeout"]
        self.table.destroy()
        #self.assertEquals(1, dealTimeout.cancelled)
        self.assertEquals(False, self.table.timer_info.has_key("dealTimeout"))
    # -------------------------------------------------------------------
    def test06_duplicate_buyin(self):
        """ Buy in requested twice for a given player """
        self.createPlayer(1)
        client = self.clients[1]
        self.assertEqual(False, self.table.buyInPlayer(client, self.table.game.maxBuyIn()))
    # -------------------------------------------------------------------
    def test08_player_has_trouble_joining(self):
        """Test for when the table is full and a player is trying hard to join"""
        # Do not use serials of 0's here -- pokerengine will hate that. :)
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
        player[5] = self.createPlayer(5, False)

        # people at table aren't obsrevers
        self.assertEqual(False, self.table.isSerialObserver(1))

        # player5 can't sit because the table is full of 1-4...
        self.assertEqual(False, self.table.seatPlayer(player[5], 5, -1))
        # player5 still not an observer
        self.assertEqual(False, self.table.isSerialObserver(5))

        self.assertEqual(True, self.table.joinPlayer(player[5], 5))
        # player5 now an observer
        self.assertEqual(True, self.table.isSerialObserver(5))
        #  ... but player5 decides to set all sorts of things that she can't
        #      because she's still just an observer.
        self.assertEqual(False, self.table.muckAccept(player[5], 5))
        self.assertEqual(False, self.table.muckDeny(player[5], 5))
        self.assertEqual(False, self.table.autoBlindAnte(player[5], 5, True))
        self.assertEqual(False, self.table.buyInPlayer(player[5], 0))
        self.assertEqual(False, self.table.rebuyPlayerRequest(player[5], 30))

        # player5 cannot sit out either because she isn't joined yet.
        self.assertEqual(False, self.table.sitOutPlayer(player[5], 5))

        # player1 leaves on his own...
        self.assertEqual(True, self.table.leavePlayer(player[1], 1))

        # ... which allows player5 to finally join legitimately and change
        # her settings.  However, she tries to sit in everyone else's
        # seat, she tries to sit out before getting the seat, rebuy before
        # even buying, and then buys in for nothing, and thus must rebuy

        for p in self.table.game.playersAll():
            self.assertEqual(False, self.table.seatPlayer(player[5], 5, p.seat))

        self.assertEqual(False, self.table.sitPlayer(player[5], 5))

        self.assertEqual(True, self.table.seatPlayer(player[5], 5, -1))
        self.assertEqual(False, self.table.rebuyPlayerRequest(player[5], 2))

        self.assertEqual(True, self.table.buyInPlayer(player[5], 0))

        # ... but cannot sit down again
        self.assertEqual(False, self.table.seatPlayer(player[5], 5, -1))

        # I wonder if these should really return True rather than None?  -- bkuhn
        self.assertEqual(None, self.table.muckAccept(player[5], 5))
        self.assertEqual(None, self.table.muckDeny(player[5], 5))
        self.assertEqual(None, self.table.autoBlindAnte(player[5], 5, True))

        self.assertEqual(True, self.table.rebuyPlayerRequest(player[5], \
                                              self.table.game.maxBuyIn()))
        # finally, player5 tries to join table 2, which isn't permitted since
        # we've set MockService.simultaneous to 1
        self.assertEqual(False, self.table2.joinPlayer(player[5], 5))
    # -------------------------------------------------------------------
    def test08_2_brokenSeatFactory(self):
        player = self.createPlayer(1, False)
        self.assertEqual(True, self.table.joinPlayer(player, 1))
        self.table.factory.seatPlayer = lambda a, b, c: False
        self.assertEqual(False, self.table.seatPlayer(player, 1, -1))
    # -------------------------------------------------------------------
    def test08_5_kick(self):
        """Test that kick works correctly"""
        player = self.createPlayer(2)

        self.assertEqual(None, self.table.kickPlayer(2))
        # Test to make sure it's ok if we kick him twice.
        try:
            self.assertEqual(None, self.table.kickPlayer(2))
        except KeyError, ke:
            self.assertEqual(2, ke[0])

        # Special test: player 9's removePlayer always fails, so it covers
        # error conditions.  Note that this has to be reset via this method in
        # tests that wish to use it:

        def fakeGameRemovePlayer(serial):
            from pokerengine.pokergame import PokerGameServer
            ret = PokerGameServer.removePlayer(self.table.game, serial)
            if serial == 9:
                return False
            else:
                return ret
        self.table.game.removePlayer = fakeGameRemovePlayer
        p = self.createPlayer(9)
        self.assertEquals(None, self.table.kickPlayer(9))
    # -------------------------------------------------------------------
    def test08_7_sitout(self):
        """Test that sitOut works correctly"""
        player = self.createPlayer(4)

        # player4 sits out but tries it twice.  (Guess he clicked too much
        # on the button)
        self.assertEqual(True, self.table.sitOutPlayer(player, 4))
        self.assertEqual(True, self.table.sitOutPlayer(player, 4))
    # -------------------------------------------------------------------
    def test08_8_buyinOverMax(self):
        """Test that buyins over the maximum are refused"""
        player = self.createPlayer(1)

        self.assertEqual(False, self.table.rebuyPlayerRequest(player, 1))
        self.assertEqual(False, self.table.rebuyPlayerRequest(player, 2))
    # -------------------------------------------------------------------
    def test09_list_players(self):
        """Test to make sure the list of players given by pokertable is right"""
        d = {}
        for ii in [1, 2, 3, 4]:
            d['Player%d' % ii] = self.createPlayer(ii)
        for x in self.table.listPlayers():
            del d[x[0]]
        self.assertEqual({}, d)
    # -------------------------------------------------------------------
    def test10_info_and_chat(self):
        """Test player discussions and info"""
        p = {}
        for ii in [1, 2, 3, 4]:
            p[ii] = self.createPlayer(ii)
        d = self.table.getPlayerInfo(2)
        self.failUnlessSubstring("Player2", d.name)
        self.table.chatPlayer(self.clients[1], 1, "Hi, I am the One.")
        self.assertEquals(1, self.service.chat_messages[0][0])
        self.assertEquals(table1ID, self.service.chat_messages[0][1])
        self.assertEquals("Hi, I am the One.", self.service.chat_messages[0][2])
        x = p[ii].waitFor(PACKET_POKER_CHAT)
        def chatCatch(packet):
            self.assertEqual(serial, 1)
            self.assertEqual(serial, "Hi, I am the One.")
        x.callback(chatCatch)
        return x
    # -------------------------------------------------------------------
    def test11_packet(self):
        """Test toPacket"""
        packetStr = "%s" % self.table.toPacket()
        idstr = 'id = %d' % self.table.game.id
        for str in [ idstr, 'name = table1', 'variant = holdem', \
                     'betting_structure = 2-4-limit', 'seats = 4', \
                     'average_pot = 0', 'hands_per_hour = 0', \
                     'percent_flop = 0', 'players = 0', 'observers = 0', \
                     'waiting = 0', 'player_timeout = 6', 'muck_timeout = 1', \
                     'currency_serial = 0', 'skin = default' ]:
            self.failUnlessSubstring(str, packetStr)
    # -------------------------------------------------------------------
    def test12_everyone_timeout(self):
        """Test if all players fall through timeout"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
        self.table.update()

        return defer.DeferredList((player[1].waitFor(PACKET_POKER_TIMEOUT_NOTICE),
                                   player[2].waitFor(PACKET_POKER_TIMEOUT_NOTICE),
                                   player[3].waitFor(PACKET_POKER_TIMEOUT_NOTICE),
                                   player[4].waitFor(PACKET_POKER_TIMEOUT_NOTICE)))
    # -------------------------------------------------------------------
    def test13_disconnect(self):
        """Test a disconnected player"""
        p1 = self.createPlayer(1, clientClass=MockClientWithTableDict)
        p9 = self.createPlayer(9, clientClass=MockClientWithTableDict)
        self.table.disconnectPlayer(p1, 1)
        self.table.disconnectPlayer(p9, 9)
    # -------------------------------------------------------------------
    def test14_closed_games(self):
        """Do typical operations act as expected when the game is closed?"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
        self.table.game.close()
        self.table.quitPlayer(player[1], 1)

        # Leaving a closed table generates an error.  player[2] is going
        # to leave, we wait for the error packet to come back, and make
        # sure that they other_type indicates it's a response to our leave
        # request.
        deferredLeaveErrorWait = player[2].waitFor(PACKET_POKER_ERROR)
        def checkReturnPacket(packet):
            self.assertEqual(PACKET_POKER_PLAYER_LEAVE, packet.other_type)
            self.failUnlessSubstring("annot leave", packet.message)
        deferredLeaveErrorWait.addCallback(checkReturnPacket)

        self.table.leavePlayer(player[2], 2)
        return deferredLeaveErrorWait
    # -------------------------------------------------------------------
    def test16_autoMuckTimeoutPolicy(self):
        """Make sure other timeout policies function properly"""
        player = self.createPlayer(1)
        player2 = self.createPlayer(2)
        # Sit out policy is the default
        self.assertEqual(self.table.timeout_policy,  "sitOut")
        self.table.timeout_policy =  "fold"

        expectPlayerAutoFold = player2.waitFor(PACKET_POKER_AUTO_FOLD)
        def checkReturnPacket(packet):
            # Don't assert which serial we get here, as it could be from
            # either player
            self.assertEqual(packet.game_id, self.table1_value)
        expectPlayerAutoFold.addCallback(checkReturnPacket)

        clear_all_messages()
        self.table.update()
        self.assertEquals(get_messages(), ['*ERROR* table %d bet mismatch 0 in memory versus 500 in database' % self.table.game.id, 'AutodealCheck scheduled in 0.000000 seconds'])

        return expectPlayerAutoFold
    # -------------------------------------------------------------------
    def test17_bogusTimeoutPolicy(self):
        self.table.timeout_policy =  "muck"
        player = self.createPlayer(1)
        player2 = self.createPlayer(2)
        self.table.update()
        return player.waitFor(PACKET_POKER_TIMEOUT_NOTICE)
    # -------------------------------------------------------------------
    def test17a_resetTimeoutPolicy(self):
        """Set timeout policy back to the default"""
        self.table.timeout_policy = "sitOut"
    # -------------------------------------------------------------------
    def test18_handReplay(self):
        """Test replay of hand from pokertable"""
        player1 = self.createPlayer(1)

        # First try a hand that doesn't exist
        self.assertEqual(None, self.table.handReplay(player1, 0))

        myHandId = randint(777, 79825)
        def checkHandSerial(packet):
            self.assertEqual(packet.hand_serial, myHandId)
        def checkAmount(amount, value):
            self.assertEqual(amount, value)
        def checkAnteAmount(packet):
            checkAmount(packet.amount, 111)
        def checkBlindAmount(packet):
            checkAmount(packet.amount, 222)
        def checkCallAmount(packet):
            checkAmount(packet.amount, 411)
        def checkRaiseAmount(packet):
            checkAmount(packet.amount, 888)
        def checkRebuyAmount(packet):
            checkAmount(packet.amount, 9999)
        def checkCanceledAmount(packet):
            checkAmount(packet.amount, 10)
        def checkRakeAmount(packet):
            self.assertEqual(packet.value, 7)
        def checkPosition(packet):
            self.assertEqual(packet.position, 1)
        def checkBlindRequest(packet):
            self.assertEqual(packet.state, "big_and_dead")
            checkBlindAmount(packet)
        def checkPlayerMoney(packet):
            self.assertEqual(True, packet.serial == 1 or packet.serial == 2)
            if packet.serial == 1:
                self.assertEqual(packet.amount, 7890)
            else:
                self.assertEqual(packet.amount, 1234)
        def checkPlayerCards(packet):
            self.assertEqual(True, packet.serial == 1 or packet.serial == 2)
            if packet.serial == 1:
                self.assertEqual(packet.cards, [23, 47])
            else:
                self.assertEqual(packet.cards, [11, 37])
        def checkMuckSerials(packet):
            self.assertEqual(packet.muckable_serials, (1, 2))

        # To get coverage of a player who isn't joined to the table requesting.
        player2 = self.createPlayer(2, False)

        player1.reasonExpected = "HandReplay"
        player2.reasonExpected = "HandReplay"
        for player in (player1, player2):
            self.table.handReplay(player, myHandId)
            checkHandSerial(player.lookForPacket(PACKET_POKER_START))
            checkPlayerCards(player.lookForPacket(PACKET_POKER_PLAYER_CARDS))
            checkPlayerCards(player.lookForPacket(PACKET_POKER_PLAYER_CARDS))
            checkPosition(player.lookForPacket(PACKET_POKER_POSITION))
            checkBlindRequest(player.lookForPacket(PACKET_POKER_BLIND_REQUEST))
            checkBlindAmount(player.lookForPacket(PACKET_POKER_BLIND))
            checkAnteAmount(player.lookForPacket(PACKET_POKER_ANTE_REQUEST))
            checkAnteAmount(player.lookForPacket(PACKET_POKER_ANTE))
            checkRebuyAmount(player.lookForPacket(PACKET_POKER_REBUY))
            player.lookForPacket(PACKET_POKER_CALL)
            player.lookForPacket(PACKET_POKER_CHECK)
            player.lookForPacket(PACKET_POKER_FOLD)
            checkRaiseAmount(player.lookForPacket(PACKET_POKER_RAISE))
            checkCanceledAmount(player.lookForPacket(PACKET_POKER_CANCELED))
            checkRakeAmount(player.lookForPacket(PACKET_POKER_RAKE))
            player.lookForPacket(PACKET_POKER_SIT_OUT)
            checkMuckSerials(player.lookForPacket(PACKET_POKER_MUCK_REQUEST))
            checkRebuyAmount(player.lookForPacket(PACKET_POKER_REBUY))
    # -------------------------------------------------------------------
    def test19_avatar_collection_empty(self):
        """Test replay of hand from pokertable"""
        self.assertEqual("MockServiceName1", self.table.getName(1))
        d = self.table.getPlayerInfo(1)
        self.failUnlessSubstring("MockServicePlayerInfo", d.name)
    # -------------------------------------------------------------------
    def test20_quitting(self):
        p = self.createPlayer(1)
        self.assertEquals(True, self.table.quitPlayer(p, 1))
        p = self.createPlayer(2, False, clientClass=MockClientWithTableDict)
        self.assertEqual(True, self.table.joinPlayer(p, 2))
        p.tables[self.table.game.id] = self.table
        self.assertEquals(True, self.table.quitPlayer(p, 2))
        # Special test: player 9's removePlayer always fails
        p = self.createPlayer(9)
        self.assertEquals(True, self.table.quitPlayer(p, 9))
    # -------------------------------------------------------------------
    def test20altForNewClientAPI_quitting(self):
        # This is disabled until the API changes
        return True

        p = self.createPlayer(1)
        self.assertEquals(True, self.table.quitPlayer(p, 1))
        p = self.createPlayer(2, False, clientClass=MockClientWithRemoveTable)
        self.assertEqual(True, self.table.joinPlayer(p, 2))
        self.assertEquals(True, self.table.quitPlayer(p, 2))
    # -------------------------------------------------------------------
    def test20_1_brokenLeaving(self):
        p = self.createPlayer(1)
        self.assertEquals(True, self.table.leavePlayer(p, 1))
        # Special test: player 9's removePlayer always fails
        p = self.createPlayer(9)
        self.assertEquals(True, self.table.leavePlayer(p, 9))
    # -------------------------------------------------------------------
    def test21_syncDatabase(self):
        """Test syncing the Database back to the MockService"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
            self.table.readyToPlay(ii)
        self.service.testObject = self
        self.table.game.turn_history = self.service.loadHand(randint(777, 8975))
        clear_all_messages()
        self.table.update()

        return player[3].waitFor(PACKET_POKER_TIMEOUT_NOTICE)
    # -------------------------------------------------------------------
    def test22_possibleObserverLoggedIn(self):
        """Test possibleObserverLoggedIn"""
        p = self.createPlayer(1)
        self.table.disconnectPlayer(p, 1)
        p2 = self.createPlayer(2)
        # Player 1 is already at the table, so this should be meaningless:
        self.table.possibleObserverLoggedIn(p, 1)
        # Player 2's object has been "lost", s owe created
        p2_reconnected = self.createPlayer(3, getReadyToPlay=False)
        self.table.joinPlayer(p2_reconnected, 3)
        self.table.possibleObserverLoggedIn(p2_reconnected, 2)
    # -------------------------------------------------------------------
    def test23_broadcastingPlayerCards(self):
        """Test to make sure PokerPlayerCards are broadcasted correctly.  This
        test is not particularly good, in my view, because it was written
        to target certain lines in private2public directly and may not
        actually be an adequate test of actual functionality."""
        p = self.createPlayer(1)
        p2 = self.createPlayer(2)
        c1 = PokerCards([ 'As', 'Ah' ])
        c1.allHidden()
        self.table.game.getPlayer(2).hand.set(c1)
        self.table.broadcast([ PacketPokerPlayerCards(game_id = self.table.game.id, serial = 2,
                                                      cards = self.table.game.getPlayer(2).hand.toRawList())])
        def checkReturnPacketBySerial(packet, serial):
            self.assertEqual(packet.serial, 2)
            if serial == 2:
                hand_expected = [243, 204]
            else:
                hand_expected = [255, 255]
            self.assertEqual(packet.cards, hand_expected)
            self.assertEqual(packet.game_id, self.table1_value)

        checkReturnPacketBySerial(p.lookForPacket(PACKET_POKER_PLAYER_CARDS), 1)
        checkReturnPacketBySerial(p2.lookForPacket(PACKET_POKER_PLAYER_CARDS), 2)
    # -------------------------------------------------------------------
    def test24_treeFallingInWoodsWithNoPlayerToHearIt(self):
        """Test a broadcast message that no one is here to hear"""
        self.assertEqual(False, self.table.broadcastMessage(PacketPokerGameMessage, "Tommy, can you hear me?"))
    # -------------------------------------------------------------------
    def test25_buyingInWhilePlaying(self):
        """Test if all players fall through timeout"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)

        def postBlindCallback(packet):
            player[3].sendPacket(PacketPokerBlind())
            self.table.buyInPlayer(player[3], 10)
        defPlayer3Blind = player[3].waitFor(PACKET_POKER_BLIND_REQUEST)

        defPlayer3Blind.addCallback(postBlindCallback)

        self.table.update()
        return defPlayer3Blind
    # -------------------------------------------------------------------
    def test26_wrongPlayerUpdateTimes(self):
        """Test if playerUpdateTimers get called with the wrong serial"""
        p = self.createPlayer(1)
        p = self.createPlayer(2)
        self.assertEqual(None, self.table.playerWarningTimer(2))
        self.assertEqual(None, self.table.playerTimeoutTimer(2))
    # -------------------------------------------------------------------
    def test27_buyinFailures(self):
        p9 = self.createPlayer(9, False)
        self.assertEqual(True, self.table.joinPlayer(p9, 9))
        self.assertEqual(True, self.table.seatPlayer(p9, 9, -1))
        self.assertEqual(True, self.table.buyInPlayer(p9, 1000))

        self.table.game.getPlayer(9).money = 0
        self.assertEqual(False, self.table.rebuyPlayerRequest(p9, 50))

        p1 = self.createPlayer(1)
        self.table.game.getPlayer(1).money = 50
        self.table.game.rebuy = lambda a, b: False
        self.assertEqual(False, self.table.rebuyPlayerRequest(p1, 0))
    # -------------------------------------------------------------------
    def checkFailedJoinDueToMax(self, player):
        self.assertEqual(False, self.table.isJoined(player))
        self.assertEquals(get_messages(), ['*ERROR* joinPlayer: %d cannot join game %d because the server is full' % (player.serial, self.table.game.id), 'sendPacket: type = ERROR(53) serial = %d game_id = %d message = This server has too many seated players and observers., code = 1, other_type = POKER_TABLE_JOIN' % (player.serial, self.table.game.id)])
        self.assertEquals(len(player.packets), 1)
        p = player.packets[0]
        self.assertEquals(p.type, PACKET_POKER_ERROR)
        self.assertEquals(p.serial, player.serial)
        self.assertEquals(p.game_id, self.table.game.id)
        self.assertEquals(p.message, "This server has too many seated players and observers.")
        self.assertEquals(p.code, PacketPokerTableJoin.FULL)
        self.assertEquals(p.other_type, PACKET_POKER_TABLE_JOIN)
        player.packets = []
    # -------------------------------------------------------------------
    def doJoinAndFailDueToMax(self, player):
        """Helper method used to check to for a join failed due to the
        maximum value."""
        clear_all_messages()
        self.table.joinPlayer(player, player.serial)
        self.checkFailedJoinDueToMax(player)
    # -------------------------------------------------------------------
    def test28_tooManyPlayers(self):
        """Generate so many players, trying to join tables, such that we
        get too many.  To force this to happen, we decrease the number of
        permitted players to be very low."""
        clear_all_messages()
        self.table.factory.joined_max = 3
        self.assertEquals(self.table.factory.joined_count, 0)
        players = {}
        for ii in [ 1, 2, 3, 4 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = False)
            self.assertEquals(self.table.factory.joined_count, 0)

        for ii in [ 1, 2, 3 ]:
            self.table.joinPlayer(players[ii], players[ii].serial)
            self.assertEqual(True, self.table.isJoined(players[ii]))
            self.assertEqual(players[ii].packets, [])
            self.assertEquals(self.table.factory.joined_count, ii)
        self.assertEquals(get_messages(), [])
        self.doJoinAndFailDueToMax(players[4])
        self.assertEquals(self.table.factory.joined_count, 3)
    # -------------------------------------------------------------------
    def test29_leavingDoesNotDecreaseCount(self):
        """Players who leave do not actually cease being observers, and
        therefore do not decrease max join count"""
        clear_all_messages()
        self.table.factory.joined_max = 3
        self.assertEquals(self.table.factory.joined_count, 0)
        players = {}
        for ii in [ 1, 2, 3, 4 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = False)
            self.assertEquals(self.table.factory.joined_count, 0)

        for ii in [ 1, 2, 3 ]:
            self.table.joinPlayer(players[ii], players[ii].serial)
            self.assertEqual(True, self.table.isJoined(players[ii]))
            self.assertEqual(players[ii].packets, [])
            self.assertEquals(self.table.factory.joined_count, ii)
        self.assertEquals(get_messages(), [])
        self.assertEquals(True, self.table.leavePlayer(players[1], players[1].serial))

        self.doJoinAndFailDueToMax(players[4])
        self.assertEquals(self.table.factory.joined_count, 3)
    # -------------------------------------------------------------------
    def test30_justEnoughPlayers(self):
        """Tests situation where players truely are gone from the table
        and are no longer observers either, thus allowing more players to
        be conntected."""
        clear_all_messages()
        self.table.factory.joined_max = 3
        self.assertEquals(self.table.factory.joined_count, 0)
        players = {}
        for ii in [ 1, 2, 3 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = True)
            self.assertEqual(True, self.table.isJoined(players[ii]))
            self.assertEqual(players[ii].packets, [])
            self.assertEquals(self.table.factory.joined_count, ii)
        messages = get_messages()
        self.failUnlessSubstring('player 1 get seat 1', messages[1])
        self.failUnlessSubstring('player 2 get seat 6', messages[3])
        self.failUnlessSubstring('player 3 get seat 3', messages[5])
        clear_all_messages()

        for ii in [ 4, 5, 6 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = False)
            self.assertEquals(self.table.factory.joined_count, 3)
        self.assertEquals(get_messages(), [])

        # leavePlayer turns an actual player into an observer, so they are still
        #  connected.  player 4 should still be unable to join.
        self.assertEquals(True, self.table.leavePlayer(players[1], players[1].serial))
        self.assertEquals(self.table.factory.joined_count, 3)
        self.doJoinAndFailDueToMax(players[4])
        self.assertEquals(self.table.factory.joined_count, 3)
        clear_all_messages()

        self.assertEquals(True, self.table.quitPlayer(players[2], 2))
        search_output('[Server][PokerGame %d] removing player %d from game'
                      % (self.table.game.id, players[2].serial))
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 2)

        self.table.joinPlayer(players[4], players[4].serial)
        self.assertEqual(True, self.table.isJoined(players[4]))
        self.assertEquals(get_messages(), [])
        self.assertEquals(self.table.factory.joined_count, 3)

        self.assertEquals(None, self.table.kickPlayer(players[3].serial))
        search_output('[Server][PokerGame %d] removing player %d from game'
                      % (self.table.game.id, players[3].serial))
        self.assertEquals(self.table.factory.joined_count, 3)

        self.doJoinAndFailDueToMax(players[5])
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 3)

        self.assertEquals(True, self.table.disconnectPlayer(players[3], 3))
        search_output('[Server][PokerGame %d] removing player %d from game'
                      % (self.table.game.id, players[3].serial))
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 2)

        self.table.joinPlayer(players[5], players[5].serial)
        self.assertEqual(True, self.table.isJoined(players[5]))
        self.assertEquals(get_messages(), [])
        self.assertEquals(self.table.factory.joined_count, 3)

        self.doJoinAndFailDueToMax(players[6])
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 3)
    # -------------------------------------------------------------------
    def test31_kickPlayerForMissingTooManyBlinds(self):
        """test31_kickPlayerForMissingTooManyBlinds
        Players who pass or equal the max_missed_round count are
        automatically kicked from the table and turned into observers.
        This happens via the update function's call of
        cashGame_kickPlayerSittingOutTooLong().  That function searches in
        the history for a 'finish' event (meaning the hand is done) and
        then kicks the player afer that.  This test sets up that situatoin
        and makes sure the player gets kicked."""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
            self.assertEquals(self.service.players.has_key(ii), True)

        self.table.game.serial2player[4].missed_big_blind_count = 1000
        self.table.game.turn_history = self.service.loadHand(6352,
                                         [('leave', [(1, 2), (2, 7)])])

        # Table starts with no observers before our update

        self.assertEquals(len(self.table.observers), 0)
        if self.table.factory.verbose < 2: self.table.factory.verbose = 2
        clear_all_messages()
        self.table.update()
        for msg in ['[Server][PokerGame %d] removing player 4 from game', 'broadcast[1, 2, 3] type = POKER_PLAYER_LEAVE(81) serial = 4 game_id = %d seat = 8', 'sendPacket: type = POKER_PLAYER_LEAVE(81) serial = 4 game_id = %d seat = 8', 'sendPacket: type = POKER_PLAYER_LEAVE(81) serial = 4 game_id = %d seat = 8', 'sendPacket: type = POKER_PLAYER_LEAVE(81) serial = 4 game_id = %d seat = 8', 'sendPacket: type = POKER_PLAYER_LEAVE(81) serial = 4 game_id = %d seat = 8']:
            self.assertEquals(search_output(msg % self.table1_value), True)

        for ii in [1, 2, 3, 4]:
            # Our service's leavePlayer() should have been called for 4,
            # the rest should still be there
            self.assertEquals(self.service.players.has_key(ii), ii != 4)
            foundCount = 0
            for pp in player[ii].packets:
                if pp.type == PACKET_POKER_PLAYER_LEAVE:
                    foundCount += 1
                    self.assertEquals(pp.serial, 4)
                    self.assertEquals(pp.game_id, self.table1_value)
                    self.assertEquals(pp.seat, 8)
            self.assertEquals(foundCount, 1)
        # Table should now have one observer, 4
        self.assertEquals(len(self.table.observers), 1)
        self.assertEquals(self.table.observers[0].serial, 4)
        return player[1].waitFor(PACKET_POKER_TIMEOUT_NOTICE)
    # -------------------------------------------------------------------
    def test32_seatPlayerUpdateTableStats(self):
        player = self.createPlayer(1, False)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.assertEquals(True, self.table.joinPlayer(player, 1))
        self.assertEquals(True, self.table.seatPlayer(player, 1, 1))
        self.assertEquals(True, updateTableStats.called)
    # -------------------------------------------------------------------
    def test33_leavePlayerUpdateTableStats(self):
        player = self.createPlayer(1)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.table.game.is_open = True
        self.table.leavePlayer(player, 1)
        self.assertEquals(True, updateTableStats.called)
    # -------------------------------------------------------------------
    def test34_leavePlayerDelayedNoUpdateTableStats(self):
        player = self.createPlayer(1)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.table.game.is_open = False
        self.table.leavePlayer(player, 1)
        self.assertEquals(False, updateTableStats.called)
    # -------------------------------------------------------------------
    def test35_quitPlayerUpdateTableStats(self):
        player = self.createPlayer(1)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.table.game.is_open = True
        self.table.quitPlayer(player, 1)
        self.assertEquals(True, updateTableStats.called)
    # -------------------------------------------------------------------
    def test36_quitPlayerDelayedNoUpdateTableStats(self):
        player = self.createPlayer(1)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.table.game.is_open = False
        self.table.quitPlayer(player, 1)
        self.assertEquals(False, updateTableStats.called)
    # -------------------------------------------------------------------
    def test37_disconnectPlayerUpdateTableStats(self):
        player = self.createPlayer(1)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.table.game.is_open = True
        self.table.disconnectPlayer(player, 1)
        self.assertEquals(True, updateTableStats.called)
    # -------------------------------------------------------------------
    def test38_disconnectPlayerDelayedNoUpdateTableStats(self):
        player = self.createPlayer(1)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.table.game.is_open = False
        self.table.disconnectPlayer(player, 1)
        self.assertEquals(False, updateTableStats.called)
    # -------------------------------------------------------------------
    def test39_kickPlayerUpdateTableStats(self):
        player = self.createPlayer(1)
        def updateTableStats(game, observers, waiting):
            updateTableStats.called = True
        updateTableStats.called = False
        self.table.factory.updateTableStats = updateTableStats
        self.table.game.is_open = True
        self.table.kickPlayer(1)
        self.assertEquals(True, updateTableStats.called)
    # -------------------------------------------------------------------
    def test40_destroy_table(self):
        """Test table destruction"""
        p1 = self.createPlayer(1, clientClass=MockClientWithTableDict)
        d = p1.waitFor(PACKET_POKER_TABLE_DESTROY)
        self.table.destroy()
         # Make sure we can't update once table is destroyed.
        self.assertEquals("not valid", self.table.update())
        return d
    # -------------------------------------------------------------------
    def test40_destroy_table_with_observers(self):
        """Test table destruction with observers at the table"""
        p1 = self.createPlayer(1, clientClass=MockClientWithTableDict)
        self.table.seated2observer(p1)
        d = p1.waitFor(PACKET_POKER_TABLE_DESTROY)
        self.table.destroy()
         # Make sure we can't update once table is destroyed.
        self.assertEquals("not valid", self.table.update())
        return d
    # -------------------------------------------------------------------
    def test41_update_exception(self):
        """Test if exception caught in update and hitory reduced"""
        self.table.history_index = -1
        def failure(history_tail):
            raise Exception("FAIL")
        self.table.updateTimers = failure
        exception_occurred = False
        try:
            self.table.update()
        except Exception, e:
            exception_occurred = True
            self.assertEquals("FAIL", e.message)
        self.assertEquals(0, self.table.history_index)
        self.assertEquals(True, exception_occurred)
    # -------------------------------------------------------------------
    def test42_update_recursion(self):
        """Test if update is protected against recursion"""
        self.table.prot = False
        def recurse(dummy):
            self.table.prot = True
            self.assertEquals("recurse", self.table.update())
        self.table.updateTimers = recurse
        self.assertEquals("ok", self.table.update())
        self.assertEquals(True, search_output('unexpected recursion'))
        self.assertEquals(True, self.table.prot)
    # -------------------------------------------------------------------
    def test43_gameStateIsMuckonAutoDealSched(self):
        """If game state is muck when autodeal tries to schedule, it should fail"""
        from pokerengine.pokergame import GAME_STATE_MUCK
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)

        verboseVal = self.table.factory.verbose
        if self.table.factory.verbose < 3: self.table.factory.verbose = 4
        clear_all_messages()
        self.table.game.state = GAME_STATE_MUCK
        self.table.scheduleAutoDeal()
        self.table.factory.verbose = verboseVal

        # No packets should be received if we tried to autodeal in
        # GAME_STATE_MUCK
        for ii in [1, 2, 3, 4]:
            self.assertEquals(player[ii].packets, [])

        search_output("Not autodealing %d because game is in muck state" % self.table.game.id)
    # -------------------------------------------------------------------
    def test44_muckTimeoutTimer_hollowedOutGameWithMuckableSerials(self):
        from pokerengine.pokergame import GAME_STATE_MUCK
        class MockGame():
            def __init__(mgSelf):
                mgSelf.muckable_serials = [ 1, 2 ]
                mgSelf.mucked = {}
                mgSelf.id = 77701
                mgSelf.state = GAME_STATE_MUCK
            def muck(mgSelf, serial, want_to_muck = False):
                mgSelf.mucked[serial] = want_to_muck

            # Rest MockGame methods below are dummy methods needed when
            # self.table.update() gets called.
            def historyGet(mgSelf): return []
            def isRunning(mgSelf): return False
            def potAndBetsAmount(mgSelf): return 0

        self.table.timer_info["muckTimeout"] = None
        origGame = self.table.game
        self.table.game = MockGame()
        verboseVal = self.table.factory.verbose
        if self.table.factory.verbose <= 0: self.table.factory.verbose = 1
        clear_all_messages()

        self.table.muckTimeoutTimer()

        self.assertEquals(len(self.table.game.mucked.keys()), 2)
        for ii in [ 1, 2 ]:
            self.failUnless(self.table.game.mucked[ii], "Serial %d should be mucked" % ii)
        self.assertEquals(get_messages()[0], 'muck timed out')
        self.table.factory.verbose = verboseVal
        self.table.game = origGame
    # -------------------------------------------------------------------
    def test45_cancelMuckTimer_hollowedOutTimer(self):
        class AMockTime(): # Spot the ST:TOS reference. :-) -- bkuhn
            def __init__(amtSelf):
                amtSelf.cancelCalledCount = 0
                amtSelf.activeCalledCount = 0
            def active(amtSelf):
                amtSelf.activeCalledCount += 1
                return True
            def cancel(amtSelf):
                amtSelf.cancelCalledCount += 1
        saveTimerInfo = self.table.timer_info

        aMockTimer = AMockTime()
        self.table.timer_info = { 'muckTimeout' : aMockTimer }

        clear_all_messages()
        self.table.cancelMuckTimer()

        self.assertEquals(self.table.timer_info['muckTimeout'], None)
        self.assertEquals(aMockTimer.cancelCalledCount, 1)
        self.assertEquals(aMockTimer.activeCalledCount, 1)
        self.assertEquals(get_messages(), [])

        self.table.timer_info = saveTimerInfo
    # -------------------------------------------------------------------
    def test46_updatePlayerTimers_hollowedOutGameAndMockedTableVals(self):
        from pokerengine.pokergame import GAME_STATE_MUCK
        class MockGame():
            def __init__(mgSelf):
                mgSelf.muckable_serials = [ 1, 2 ]
                mgSelf.mucked = {}
                mgSelf.id = 77701
                mgSelf.state = GAME_STATE_MUCK
            def isRunning(mgSelf): return True
            def getSerialInPosition(mgSelf): return 664
            def historyGet(mgSelf): return [ "" ]

        self.table.game = MockGame()
        self.table.playerTimeout = 100
        self.table.history_index = -1
        deferredMustBeCalledBackForSuccess = defer.Deferred()
        def myPlayerTimeout(serial):
            self.assertEquals(self.tableSave.timer_info["playerTimeoutSerial"], serial)
            self.assertEquals(serial, 664)
            deferredMustBeCalledBackForSuccess.callback(True)
            self.assertEquals(get_messages(), [])

        self.table.playerWarningTimer = myPlayerTimeout
        def failedToCancelTimeout():
            self.fail("existing playerTimeout was not replaced as expected")

        self.table.timer_info = { 'playerTimeout' :
                                  reactor.callLater(20, failedToCancelTimeout),
                                  'playerTimeoutSerial' : 229 }
                                  # Note: serial is diff from one in position
        clear_all_messages()
        self.table.updatePlayerTimers()

        self.tableSave = self.table

        return deferredMustBeCalledBackForSuccess
    # -------------------------------------------------------------------
    def test48_muckTimeoutTimerShouldEmptyMuckableSerials(self):
        """
        See https://gna.org/bugs/?13898
        """
        from pokerengine.pokergame import GAME_STATE_MUCK

        self.table.timer_info["muckTimeout"] = None
        if self.table.factory.verbose <= 0: self.table.factory.verbose = 1
        clear_all_messages()

        self.createPlayer(1)
        self.createPlayer(2)
        self.table.beginTurn()

        self.table.game.state = GAME_STATE_MUCK
        self.table.game.muckable_serials = [1,2]
        self.table.syncDatabase = lambda: None
        self.table.muckTimeoutTimer()
        self.assertEquals([], self.table.game.muckable_serials)

# -------------------------------------------------------------------

# I seriously considered not having *all* the same tests run with
# predifined decks because it was not needed to get coverage.  A simple
# setup test would have worked.  However, I think it's good leaving it
# this way because if predifined decks are later used extensively, we
# would want all the tests to run and when additional use of predefined
# decks is added.  -- bkuhn, 2008-01-21

# I later decided to mix together the tests for predefined decks with
# tests for autodeal turned off; that's why so many tests are replaced.

class PokerTableTestCaseWithPredefinedDecksAndNoAutoDeal(PokerTableTestCase):
    def setUp(self, settingsXmlStr=settings_stripped_deck_no_autodeal_xml, ServiceClass = MockService):
        PokerTableTestCase.setUp(self, settingsXmlStr, ServiceClass)

    # -------------------------------------------------------------------
    def test01_autodeal(self):
        self.createPlayer(1)
        self.createPlayer(2)
        # Nothing should happen, we don't have autodeal
        self.assertEqual(None, self.table.scheduleAutoDeal())
    # -------------------------------------------------------------------
    def test01_8_testClientsBogusPokerProcessingHand(self):
        """Test specific situation in autodeal when poker clients send a
        Processing Hand before a Ready To Play: not needed when autodeal is off"""
        pass
    # -------------------------------------------------------------------
    def test02_autodeal_check(self):
        self.createPlayer(1)
        self.table.processingHand(1)
        self.table.game_delay["delay"] = 2
        self.table.game_delay["start"] = testclock._seconds_value
        self.createPlayer(2)
        self.assertEqual(None, self.table.scheduleAutoDeal())
    # -------------------------------------------------------------------
    def test12_everyone_timeout(self):
        """Test if all players fall through timeout"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
        self.table.cancelDealTimeout()
        self.table.beginTurn()
        self.table.update()

        return defer.DeferredList((player[1].waitFor(PACKET_POKER_TIMEOUT_NOTICE),
                                   player[2].waitFor(PACKET_POKER_TIMEOUT_NOTICE),
                                   player[3].waitFor(PACKET_POKER_TIMEOUT_NOTICE),
                                   player[4].waitFor(PACKET_POKER_TIMEOUT_NOTICE)))
    # -------------------------------------------------------------------
    def test16_autoMuckTimeoutPolicy(self):
        """Make sure other timeout policies function properly"""
        player = self.createPlayer(1)
        player2 = self.createPlayer(2)
        # Sit out policy is the default
        self.assertEqual(self.table.timeout_policy,  "sitOut")
        self.table.timeout_policy =  "fold"

        expectPlayerAutoFold = player2.waitFor(PACKET_POKER_AUTO_FOLD)
        def checkReturnPacket(packet):
            # Don't assert which serial we get here, as it could be from
            # either player
            self.assertEqual(packet.game_id, self.table1_value)
        expectPlayerAutoFold.addCallback(checkReturnPacket)

        self.table.cancelDealTimeout()
        self.table.beginTurn()
        self.table.update()

        return expectPlayerAutoFold
    # -------------------------------------------------------------------
    def test17_bogusTimeoutPolicy(self):
        self.table.timeout_policy =  "muck"
        player = self.createPlayer(1)
        player2 = self.createPlayer(2)

        self.table.cancelDealTimeout()
        self.table.beginTurn()
        self.table.update()
        return player.waitFor(PACKET_POKER_TIMEOUT_NOTICE)
    # -------------------------------------------------------------------
    def test21_syncDatabase(self):
        """Test syncing the Database back to the MockService"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
            self.table.readyToPlay(ii)
        self.service.testObject = self
        self.table.game.turn_history = self.service.loadHand(randint(777, 8975))
        self.table.beginTurn()
        self.table.update()
        return player[4].waitFor(PACKET_POKER_TIMEOUT_NOTICE)
    # -------------------------------------------------------------------
    def test25_buyingInWhilePlaying(self):
        """Test if all players fall through timeout"""
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
        self.table.beginTurn()

        def postBlindCallback(packet):
            player[3].sendPacket(PacketPokerBlind(serial = 3, game_id = packet.game_id, amount = packet.amount, dead = packet.dead))
            self.assertEqual(False, self.table.buyInPlayer(player[3], 10))

        defPlayer3Blind = player[3].waitFor(PACKET_POKER_BLIND_REQUEST)

        defPlayer3Blind.addCallback(postBlindCallback)

        self.table.update()

        return defPlayer3Blind
    def test27_buyinFailures(self):
        """This test doesn't matter in this subclass"""
        return True
    # -------------------------------------------------------------------
    def test28_joinTwice(self):
        """Player join a second time : packets sent twice"""
        player = self.createPlayer(1)
        self.assertEqual(True, self.table.isJoined(player))
        def join(table, reason = ""):
            player.joined = True
        player.join = join
        self.assertEqual(True, self.table.joinPlayer(player, player.serial))
        self.failUnless(player.joined)
    # -------------------------------------------------------------------
    def test31_kickPlayerForMissingTooManyBlinds(self):
        """SKIP THIS TEST IN THIS SUBCLASS
        """
        return True
# -------------------------------------------------------------------
# This class tests the same operations as PokerTableTestCase but for tables that
#  are transient.  Note the outcome of various operations are quite different
#  when the table is transient.
class PokerTableTestCaseTransient(PokerTableTestCase):
    def setUp(self, settingsXmlStr=settings_xml, ServiceClass = MockService):
        testclock._seconds_reset()
        global table1ID
        global table2ID
        table1ID = table1ID + 1
        table2ID += 1
        self.table1_value = table1ID
        self.table2_value = table2ID

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settingsXmlStr, len(settingsXmlStr))
        settings.header = settings.doc.xpathNewContext()
        self.service = ServiceClass(settings)
        class Tournament:
            name = 'My Old Sit and Go'
            serial = 2
        self.table = pokertable.PokerTable(self.service, table1ID,
                                           { 'name': "table1",
                                             'variant': "holdem",
                                             'betting_structure': "2-4-limit",
                                             'seats': 4,
                                             'player_timeout' : 6,
                                             'muck_timeout' : 1,
                                             'transient' : True,
                                             'tourney' : Tournament(),
                                             'currency_serial': 0
                                             })
        self.table2 = pokertable.PokerTable(self.service, table2ID,
                                           { 'name': "table2",
                                             'variant': "holdem",
                                             'betting_structure': "2-4-limit",
                                             'seats': 4,
                                             'player_timeout' : 6,
                                             'muck_timeout' : 1,
                                             'transient' : True,
                                             'tourney' : Tournament(),
                                             'currency_serial': 0
                                             })
        self.service.table1 = self.table
        self.service.table2 = self.table2
        self.clients = {}

    def createPlayer(self, serial, getReadyToPlay=True, clientClass=MockClient, table=None):
        if table == None:
            table = self.table
        client = clientClass(serial, self)
        self.clients[serial] = client
        client.reasonExpected = "MockTransientCreatePlayer"
        table.joinPlayer(client, serial, reason = "MockTransientCreatePlayer")
        client.reasonExpected = ""
        if getReadyToPlay:
            self.assertEqual(True, table.seatPlayer(client, serial, -1))
            table.sitPlayer(client, serial)
        return client

    # -------------------------------------------------------------------
    def test01_autodeal(self):
        """ Transient tables hand deal has a minimum duration if all players are in auto mode """
        self.createPlayer(1)
        self.createPlayer(2)
        self.table.game_delay["start"] = testclock._seconds_value
        self.table.scheduleAutoDeal()
        return self.clients[2].waitFor(PACKET_POKER_MESSAGE)
    # -------------------------------------------------------------------
    def test02_autodeal_check(self):
        self.createPlayer(1)
        self.table.processingHand(1)
        self.table.game_delay["delay"] = 2
        self.table.game_delay["start"] = testclock._seconds_value
        self.createPlayer(2)
        self.table.scheduleAutoDeal()
        return self.clients[2].waitFor(PACKET_POKER_MESSAGE)
    # -------------------------------------------------------------------
    def test04_autodeal_transient_now(self):
        """ Transient tables hand deal has no minium duration if all players are in auto mode but the hand lasted more than the required minium """
        self.createPlayer(1)
        self.createPlayer(2)
        self.table.game_delay["start"] = testclock._seconds_value - 300
        self.table.scheduleAutoDeal()
        self.clients[2].raiseIfPacket(PACKET_POKER_MESSAGE)
        return self.clients[2].waitFor(PACKET_POKER_START)
    # -------------------------------------------------------------------
    def test05_autodeal_transient_normal(self):
        """ Transient tables hand deal normaly if at least one player is not in auto mode """
        self.createPlayer(1)
        self.createPlayer(2)
        self.table.scheduleAutoDeal()
        self.clients[2].raiseIfPacket(PACKET_POKER_MESSAGE)
        return self.clients[2].waitFor(PACKET_POKER_START)

    def test08_player_has_trouble_joining(self):
        """Test for when the table is full and a player is trying hard to join"""
        # Do not use serials of 0's here -- pokerengine will hate that. :)
        player = {}
        for ii in [1, 2, 3, 4]:
            player[ii] = self.createPlayer(ii)
        player[5] = self.createPlayer(5, False)

        # player5 can't sit because the table is full of 1-4...
        self.assertEqual(False, self.table.seatPlayer(player[5], 5, -1))

        #  ... but player5 decides to set all sorts of things that she can't
        #      because she's still just an observer.
        self.assertEqual(False, self.table.muckAccept(player[5], 5))
        self.assertEqual(False, self.table.muckDeny(player[5], 5))
        self.assertEqual(False, self.table.autoBlindAnte(player[5], 5, True))
        self.assertEqual(False, self.table.rebuyPlayerRequest(player[5], 30))

        # player5 cannot sit out either because she isn't joined yet.
        self.assertEqual(False, self.table.sitOutPlayer(player[5], 5))

        # player1 leaves on his own...
        self.assertEqual(True, self.table.leavePlayer(player[1], 1))

        # ... which allows player5 to finally join legitimately and change
        # her settings.  However, she tries to sit out before getting the
        # seat, rebuy before even buying, and then buys in for nothing,
        # and thus must rebuy

        self.assertEqual(True, self.table.seatPlayer(player[5], 5, -1))
        self.assertEqual(False, self.table.rebuyPlayerRequest(player[5], 2))

        # this table is transient, so no one can buy in.
        self.assertEqual(False, self.table.buyInPlayer(player[5], 0))

        # I wonder if these should really return True rather than None?  -- bkuhn
        self.assertEqual(None, self.table.muckAccept(player[5], 5))
        self.assertEqual(None, self.table.muckDeny(player[5], 5))
        self.assertEqual(None, self.table.autoBlindAnte(player[5], 5, True))

        self.assertEqual(False, self.table.rebuyPlayerRequest(player[5], \
                                              self.table.game.maxBuyIn()))

        # player2 tries to rebuy but is already at the max, and besides,
        # in transient mode, this doesn't work anyway

        self.assertEqual(False, self.table.rebuyPlayerRequest(player[2], 1))
    # -------------------------------------------------------------------
    def test07_break_message(self):
        """ Tournament break issue a message to all players """
        class Tournament:
            def __init__(self):
                self.state = pokertournament.TOURNAMENT_STATE_BREAK_WAIT

        self.createPlayer(1)
        self.createPlayer(2)
        self.table.tourney = Tournament()
        self.table.game.isTournament = lambda: True
        self.table.scheduleAutoDeal()
        self.failUnless(self.clients[1].lookForPacket(PACKET_POKER_GAME_MESSAGE))
        self.failUnless(self.clients[2].lookForPacket(PACKET_POKER_GAME_MESSAGE))
    # -------------------------------------------------------------------
    def test11bis_packet_with_tourney_serial(self):
        """Test toPacket"""
        packetStr = "%s" % self.table.toPacket()
        idstr = 'id = %d' % self.table.game.id
        for str in [ idstr, 'name = table1', 'variant = holdem', \
                     'betting_structure = 2-4-limit', 'seats = 4', \
                     'average_pot = 0', 'hands_per_hour = 0', \
                     'percent_flop = 0', 'players = 0', 'observers = 0', \
                     'waiting = 0', 'player_timeout = 6', 'muck_timeout = 1', \
                     'currency_serial = 0', 'skin = default', \
                     'tourney_serial = 2' ]:
            self.failUnlessSubstring(str, packetStr)
    # -------------------------------------------------------------------
    def test27_buyinFailures(self):
        """This test doesn't matter in this subclass"""
        return True
    # -------------------------------------------------------------------
    def test28_tooManyPlayers(self):
        """Generate so many players, trying to join tables, such that we
        get too many.  To force this to happen, we decrease the number of
        permitted players to be very low.  Note that for transient tables,
        immediate joins are forced, and therefore we get the error
        immediately upon getting ready to play"""
        clear_all_messages()
        self.table.factory.joined_max = 3
        self.assertEquals(self.table.factory.joined_count, 0)
        players = {}
        for ii in [ 1, 2, 3 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = False)
            self.assertEqual(True, self.table.isJoined(players[ii]))
            self.assertEquals(self.table.factory.joined_count, ii)
        self.assertEquals(self.table.factory.joined_count, 3)
        clear_all_messages()
        players[4] = self.createPlayer(4, getReadyToPlay = False)
        self.checkFailedJoinDueToMax(players[4])
        self.assertEquals(self.table.factory.joined_count, 3)
    # -------------------------------------------------------------------
    def test29_leavingDoesNotDecreaseCount(self):
        """Players who leave do not actually cease being observers, and
        therefore do not decrease max join count.  Note this works
        differently with transient tables because the seating is
        automatic."""
        clear_all_messages()
        self.table.factory.joined_max = 3
        self.assertEquals(self.table.factory.joined_count, 0)
        players = {}
        for ii in [ 1, 2, 3 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = False)
            self.assertEqual(True, self.table.isJoined(players[ii]))
            self.assertEquals(self.table.factory.joined_count, ii)

        self.assertEquals(self.table.factory.joined_count, 3)

        self.assertEquals(get_messages(), [])
        self.assertEquals(True, self.table.leavePlayer(players[1], players[1].serial))

        clear_all_messages()  # Ignore any messages from leave
        players[4] = self.createPlayer(4, getReadyToPlay = False)
        self.checkFailedJoinDueToMax(players[4])

        self.assertEquals(self.table.factory.joined_count, 3)
    # -------------------------------------------------------------------
    def test30_justEnoughPlayers(self):
        """Tests situation where players truely are gone from the table
        and are no longer observers either, thus allowing more players to
        be conntected.  With transient tables, this automatically tries to
        seat them."""
        clear_all_messages()
        self.table.factory.joined_max = 3
        players = {}
        for ii in [ 1, 2, 3 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = True)
            self.assertEqual(True, self.table.isJoined(players[ii]))
            self.assertEqual(players[ii].packets, [])
            self.assertEquals(self.table.factory.joined_count, ii)
        messages = get_messages()
        self.failUnlessSubstring('player 1 get seat 1', messages[1])
        self.failUnlessSubstring('player 2 get seat 6', messages[3])
        self.failUnlessSubstring('player 3 get seat 3', messages[5])
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 3)

        for ii in [ 4, 5, 6 ]:
            players[ii] = self.createPlayer(ii, getReadyToPlay = False)
            self.checkFailedJoinDueToMax(players[ii])
            clear_all_messages()
            self.assertEquals(self.table.factory.joined_count, 3)

        # leavePlayer turns an actual player into an observer, so they are still
        #  connected.  player 4 should still be unable to join.
        self.assertEquals(True, self.table.leavePlayer(players[1], players[1].serial))
        self.doJoinAndFailDueToMax(players[4])
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 3)

        self.assertEquals(True, self.table.quitPlayer(players[2], 2))
        search_output('[Server][PokerGame %d] removing player %d from game'
                      % (self.table.game.id, players[2].serial))
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 2)
        self.table.joinPlayer(players[4], players[4].serial)
        self.assertEqual(True, self.table.isJoined(players[4]))
        self.assertEquals(get_messages(), [])
        self.assertEquals(self.table.factory.joined_count, 3)

        self.assertEquals(None, self.table.kickPlayer(players[3].serial))
        search_output('[Server][PokerGame %d] removing player %d from game'
                      % (self.table.game.id, players[3].serial))
        self.assertEquals(self.table.factory.joined_count, 3)

        self.doJoinAndFailDueToMax(players[5])
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 3)

        self.assertEquals(True, self.table.disconnectPlayer(players[3], 3))
        search_output('[Server][PokerGame %d] removing player %d from game'
                      % (self.table.game.id, players[3].serial))
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 2)

        self.table.joinPlayer(players[5], players[5].serial)
        self.assertEqual(True, self.table.isJoined(players[5]))
        self.assertEquals(get_messages(), [])
        self.assertEquals(self.table.factory.joined_count, 3)

        self.doJoinAndFailDueToMax(players[6])
        clear_all_messages()
        self.assertEquals(self.table.factory.joined_count, 3)
    # -------------------------------------------------------------------
    def test31_kickPlayerForMissingTooManyBlinds(self):
        """SKIP THIS TEST IN THIS SUBCLASS
        """
        return True
# --------------------------------------------------------------------------------
class MockServiceWithLadder(MockService):
    def __init__(self, settings):
        MockService.__init__(self, settings)
        self.has_ladder = True
        self.calledLadderMockup = None

    def getLadder(self, game_id, currency_serial, user_serial):
        self.calledLadderMockup = user_serial
        return PacketPokerPlayerStats()

# --------------------------------------------------------------------------------
class PokerTableMoveTestCase(PokerTableTestCaseBase):
    def setUp(self, ServiceClass = MockServiceWithLadder):
        PokerTableTestCaseBase.setUp(self, ServiceClass = MockServiceWithLadder)

    # -------------------------------------------------------------------
    def test15_moveTo(self):
        """Make sure a player can move from one place to another"""
        player = self.createPlayer(1)
        player.reasonExpected = "MockMoveTest"

        otherTablePlayer = self.createPlayer(2, table=self.table2)

        expectPlayerDeferred = otherTablePlayer.waitFor(PACKET_POKER_PLAYER_ARRIVE)
        def checkReturnPacket(packet):
            self.assertEqual(packet.game_id, self.table2_value)
            self.assertEquals(self.service.calledLadderMockup, packet.serial)
            self.assertEquals(self.table2.timer_info.has_key('dealTimeout'), False)
        expectPlayerDeferred.addCallback(checkReturnPacket)

        self.table2.cancelDealTimeout()
        
        self.table_joined = None
        def checkJoin(table, reason):
            print table
            self.table_joined = table
        player.join = checkJoin
        
        self.service.movePlayer = lambda a,b,c: self.table.game.maxBuyIn()
        
        self.table.movePlayer([player], 1, self.table2.game.id, reason = "MockMoveTest")
        self.assertEquals(self.table_joined, self.table2)
        
        return expectPlayerDeferred


class PokerTableRejoinTestCase(PokerTableTestCaseBase):
    def setUp(self, ServiceClass = MockServiceWithLadder):
        PokerTableTestCaseBase.setUp(self, ServiceClass = MockServiceWithLadder)

    def test49_playerRejoinCheckAutoFlag(self):
        """
        See https://gna.org/bugs/?14797
        """
        player1 = self.createPlayer(1)
        player2 = self.createPlayer(2, clientClass=MockClientWithRealJoin)
        
        self.table.scheduleAutoDeal()
        d = player2.waitFor(PACKET_POKER_START)
        def quitPlayer(x):
            thisPlayer = self.table.game.serial2player[2]
            self.table.quitPlayer(player2, 2)
            self.assertTrue(thisPlayer.isAuto())
        def joinPlayer(x):
            self.assertTrue(self.table.joinPlayer(player2, 2))
            d = player2.waitFor(PACKET_POKER_PLAYER_ARRIVE)
            return d
        def checkAutoFlag(x):
            playerArrive = [p for p in player2.packets if p.type == PACKET_POKER_PLAYER_ARRIVE and p.serial == 2]
            self.assertEqual(len(playerArrive), 1)
            self.assertFalse(self.table.game.serial2player[2].isAuto())
            self.assertFalse(playerArrive[0].auto)
        d.addCallback(quitPlayer)
        d.addCallback(joinPlayer)
        d.addCallback(checkAutoFlag)
        return d

# --------------------------------------------------------------------------------
def Run():
    seed(time.time())
    loader = runner.TestLoader()
#    loader.methodPrefix = "test40"
#    os.environ['VERBOSE_T'] = '4'
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerAvatarCollectionTestCase))
    suite.addTest(loader.loadClass(PokerTableTestCase))
    suite.addTest(loader.loadClass(PokerTableTestCaseWithPredefinedDecksAndNoAutoDeal))
    suite.addTest(loader.loadClass(PokerTableTestCaseTransient))
    suite.addTest(loader.loadClass(PokerTableMoveTestCase))
    suite.addTest(loader.loadClass(PokerTableRejoinTestCase))
    return runner.TrialRunner(reporter.VerboseTextReporter,
#                              tracebackFormat='verbose',
                              tracebackFormat='default',
                              ).run(suite)
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokertable.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokertable.py' TESTS='coverage-reset test-pokertable.py coverage-report' check )"
# End:
