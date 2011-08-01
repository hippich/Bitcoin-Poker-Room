#!/usr/bin/python2.4
# -*- mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C)       2008 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C) 2006       Mekensleep <licensing@mekensleep.com>
#                          24 rue vieille du temple 75004 Paris
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
# Authors:
#  J.Jeannin <griim.work@gmail.com>
#  Bradley M. Kuhn <bkuhn@ebb.org>

import sys, os
sys.path.insert(0, "./..")
sys.path.insert(0, "..")

from tests.testmessages import silence_all_messages, search_output, clear_all_messages, get_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
verbose = 5
if verbose < 0: silence_all_messages()

from pokernetwork import protocol
from pokernetwork import protocol_number
from pokernetwork.version import Version

from twisted.trial import unittest, runner, reporter
from twisted.internet import reactor, defer

from time import time

protocol_version = Version(protocol_number)

#-----------------

class FakeFactory:
    """Factory for testing purpose"""
    def __init__(self, verbose):
        self.verbose = verbose

class FakeTransport:
    """Transport for testing purpose"""
    def __init__(self):
        self._loseConnection = False

    def write(self, data = ''):
        return True

    def loseConnection(self):
        self._loseConnection = True
        
class FakeTimer:
    """Timer for testing purpose"""
    def __init__(self):
        self._active = True

    def active(self):
        return self._active

    def cancel(self):
        self._active = False

class FakePacket:
    """Packet for testing purpose"""
    def __init__(self, time, id = None):
        self.time__ = time
        self.nodelay__ = None
        self.arg = time
        self.id = id

#-----------------

class QueueTestCase(unittest.TestCase):
    """Test case for class Queue"""

    def testQueueInit(self):
        """Testing class Queue init"""
        
        queue = protocol.Queue()
        assert queue.delay == 0 , "invalid delay (0 expected)"
        assert len(queue.packets) == 0 , "list packets not empty"

class UGAMEProtocolTestCase(unittest.TestCase):
    """Test case for class UGAMEProtocol"""

    def setUp(self):
        self.u = protocol.UGAMEProtocol()
        self.u.transport = FakeTransport()
        self.u.factory = FakeFactory(int(os.environ.get('VERBOSE_T', 6)))
        silence_all_messages()

    def fakeProcessQueuesDeferred(self, count = 1):
        global calledProcessQueuesCount
        calledProcessQueuesCount = 0
        self.soughtCount= count
        def mockProcessQueues():
            global calledProcessQueuesCount
            calledProcessQueuesCount += 1

        self.u._processQueues = mockProcessQueues

        def doneOk(mySelf):
            global calledProcessQueuesCount
            self.assertEquals(calledProcessQueuesCount, mySelf.soughtCount)
        d = defer.Deferred()
        d.addCallback(doneOk)
        # Note, if test fails, you'll get a reactor error.
        reactor.callLater(1, lambda: d.callback(self))

        return d


    def testUGAMEProtocolInit(self):
        """Testing class UGAMEProtocol init"""
        
        assert len(self.u._packet) == 0       , "list _packet not empty"
        assert self.u._packet_len  == 0       , "invalid _packet_len  (0 expected)"
        assert self.u._timer == None          , "invalid _timer (None expected)"
        assert self.u._packet2id(1) == 0      , "function _packet2id invalid"
        assert self.u._packet2front(2) == False , "function _packet2front invalid"
        assert len(self.u._queues) == 0       , "dictionnary _queues not empty"
        assert self.u._lagmax == 0            , "invalid _lagmax (0 expected)"
        assert self.u._lag == 0               , "invalid _lag (0 expected)"
        assert self.u._prefix == ""           , "invalid _prefix"
        assert self.u._blocked == False       , "invalid _blocked (False expected)"
        assert self.u.established == 0        , "invalid ugp.established (0 expected)"
        assert self.u._protocol_ok == False   , "invalid _protocol_ok (False expected)"
        assert self.u._poll == True                      , "invalid _poll (True expected)"
        assert self.u._poll_frequency == 0.01    , "invalid _poll_frequency (0.01 expected)"
        assert self.u._ping_delay == 5        , "invalid _ping_delay"

    def testSetPingDelay(self):
        """Testing setPingDelay"""        

        self.u.setPingDelay(10)
        assert self.u._ping_delay == 10       , "_ping_delay is not set correctly"

    def testGetPingDelay(self):
        """Testing getPingDelay"""        

        self.u.setPingDelay(8)
        assert self.u.getPingDelay() == 8     , "return value is not the one expected"

    def testGetLag(self):
        """Testing getLag"""

        assert self.u.getLag() == 0             , "return value is not the one expected"

    def testGetOrCreateQueue(self):
        """Testing getOrCreateQueue"""
        
        assert self.u._queues.has_key(0) == False , "queues already containing Key '0'"
        q1 = self.u.getOrCreateQueue(0)
        assert self.u._queues.has_key(0) == True  , "getOrCreateQueue does not have created queues"
        q2 = self.u.getOrCreateQueue(0)

        assert q1 == q2                           , "getOrCreateQueue overwrite queues"

    def testConnectionMade(self):
        """Testing connectionMade"""
        global writeCallCount
        writeCallCount = 0

        def mockTestSendVersion(data):
            global writeCallCount
            self.assertEquals(data, 'CGI %s.%s\n' % (protocol.PROTOCOL_MAJOR, 
                                                     protocol.PROTOCOL_MINOR))
            writeCallCount += 1
        self.u.transport.write = mockTestSendVersion

        self.u.connectionMade()
        self.assertEquals(writeCallCount, 1)
 
    def testConnectionLost(self):
        """Testing ConnectionLost"""
        silence_all_messages()
        clear_all_messages()
        self.u.established = 1
        self.u.connectionLost("testing")
        self.assertEquals(search_output("connectionLost: reason = testing"), True)
            
        assert self.u.established == 0

    def testConnectionLostWithProtocolOk(self):
        """Testing ConnectionLostWithProtocolOk"""
        silence_all_messages()
        clear_all_messages()
        self.u.established = 1
        self.u._protocol_ok = True
        self.u.connectionLost("another")
        self.assertEquals(search_output("connectionLost: reason = another"), True)
            
        assert self.u.established == 0
    
    def testHandleConnection(self):
        """Testing _handleConnection"""        
        clear_all_messages()
        # there is just a pass here in the implementation, there is really
        # nothing to be done to truly test it.
        self.assertEquals(self.u._handleConnection("..."), None)
        self.assertEquals(get_messages(), [])

    def testIgnoreIncomingData(self):
        """Testing ignoreIncomingData"""
        
        self.u.ignoreIncomingData()           
        self.u._timer = FakeTimer()
        self.u.ignoreIncomingData()
        assert self.u._timer._active == False

    def testHandleVersion(self):
        """Testing handleVersion"""

        assert self.u._protocol_ok == False        , "_protocol_ok : False expected"
        # Messages should be empty, protocol is not established
        clear_all_messages()
        self.u._handleVersion()
        self.assertEquals(get_messages(), [])
        
        assert self.u._protocol_ok == False        ,"_protocol_ok change unexpected"
        
        self.u._packet = list('\n')
        # Messages should be empty, protocol is not established
        clear_all_messages()
        self.u._handleVersion()
        self.assertEquals(get_messages(), [])
        assert self.u.transport._loseConnection == True , "loseConnection not called"

        self.u.transport = FakeTransport()      # transport re-init
        self.u._packet = list('CGI a.b\n')
        # Messages should be empty, protocol is not established
        clear_all_messages()
        self.u._handleVersion()
        self.assertEquals(get_messages(), [])
        assert self.u.transport._loseConnection == True , "loseConnection not called"

        self.u.transport = FakeTransport()      # transport re-init
        vers = Version(protocol_number)
        PROTOCOL_MAJOR = "%03d" % vers.major()
        PROTOCOL_MINOR = "%d%02d" % ( vers.medium(), vers.minor() )
        self.u._packet = list( 'CGI %s.%s \n' % (PROTOCOL_MAJOR, PROTOCOL_MINOR ))
        clear_all_messages()
        self.u._handleVersion()
        self.assertEquals(get_messages(), ["protocol established"])

        assert self.u._protocol_ok == True ,  "_protocol_ok value unexpected"

    def testProtocolEstablished(self):
        pass

    def testProtocolInvalid(self):
        pass
    
    def testHold(self):
        """Testing hold"""

        self.u.hold(-2,0)
        assert self.u._queues.has_key(0) == True  , "queue has not been created"
        assert self.u._queues[0].delay == -2  , "delay wrongly set"

        self.u.hold(-4)
        assert self.u._queues[0]. delay == -4 , "delay wrongly  set"

        self.u.hold(1)
        assert self.u._queues[0].delay > 0 , "delay wrongly set"

    def testBlock(self):
        """Testing block"""

        self.u._blocked = False
        self.u.block()
        assert self.u._blocked == True   ,   "block don't block..."

    def testUnblock(self):
        """Testing unblock"""

        self.u._blocked = True
        self.u.unblock()
        assert self.u._blocked == False  ,   "unblock don't unblock..."
 
    def testDiscardPackets(self):
        """Testing discardPackets"""
        
        self.u._queues[0] = protocol.Queue()
        self.u.discardPackets(0)
        assert not hasattr(self.u , '_queues[0]')  ,  "queue not deleted"
 
    def testCanHandlePacket(self):
        """Testing canHandlePackets"""

        assert self.u.canHandlePacket('') == (True,0)
    
    def testProcessQueues(self):
        """Testing _proccessQueues"""
        global triggerTimerCallCount
        triggerTimerCallCount = 0
        def mockTriggerTimer():
            global triggerTimerCallCount
            triggerTimerCallCount += 1
            
        self.u.triggerTimer = mockTriggerTimer
        self.u.canHandlePacket = lambda x : (False, time()+10)
        self.failIf(self.u._queues.has_key(0))
        self.u.getOrCreateQueue(0)
        self.failUnless(self.u._queues.has_key(0))

        self.u._lagmax = 10

        self.failIf(self.u._queues.has_key(1))
        self.u.getOrCreateQueue(1)
        self.failUnless(self.u._queues.has_key(1))
        self.u._queues[1].delay = time()+10
        oneArg = 0
        self.u._queues[1].packets.insert( 0, FakePacket(oneArg, "one") )
        self.u._queues[1].packets[0].nodelay__ = True

        self.failIf(self.u._queues.has_key(2))
        self.u.getOrCreateQueue(2)
        self.failUnless(self.u._queues.has_key(2))
        self.u._queues[2].delay = time()
        twoArg = time()
        self.u._queues[2].packets.insert( 0, FakePacket(twoArg, "two") )

        self.failIf(self.u._queues.has_key(3))
        self.u.getOrCreateQueue(3)
        self.failUnless(self.u._queues.has_key(3))
        self.u._queues[3].delay = time()+1
        threeArg = time() +10
        self.u._queues[3].packets.insert( 0, FakePacket(threeArg, "three") )

        # Ok, Test blocked first -- nothing happens
        clear_all_messages()
        self.u._blocked = True
        self.u._processQueues()
        k = self.u._queues.keys()
        self.assertEquals(triggerTimerCallCount,  1)

        k.sort()
        self.assertEquals(k, [ 0, 1, 2, 3 ])
        self.assertEquals(get_messages(), [])
        self.assertEquals(self.u._lag, 0)

        # Unblocked test, function fully runs
        triggerTimerCallCount = 0
        self.u._blocked = False

        global callCount
        callCount = 0
        def mockHandler(packet):
            global callCount
            callCount += 1
            self.assertEquals(packet.arg, oneArg)
            self.assertEquals(packet.id, 'one')
                
        self.u._handler = mockHandler

        startTime = time()
        self.u._processQueues()
        endTime = time()

        self.assertEquals(callCount, 1)
        self.failUnless(self.u._lag > startTime)
        self.failUnless(self.u._lag <= endTime)

        k = self.u._queues.keys()
        k.sort()
        self.assertEquals(k, [ 1, 2, 3 ])

        self.assertEquals(len(self.u._queues[1].packets), 0)
        self.assertEquals(len(self.u._queues[2].packets), 1)
        self.assertEquals(len(self.u._queues[3].packets), 1)
        self.assertEquals(triggerTimerCallCount,  1)

        self.assertEquals(len(get_messages()), 2)
        self.assertEquals(get_messages()[0], ' => queue 1 delay canceled because lag too high')
        self.assertEquals(get_messages()[1].find('seconds before handling the next packet in queue 3') > 0, True)

    def triggerTimer_expectNoCallLater(self, doneOk):
        def mockProcessQueue(): self.fail()
        self.u._processQueues = mockProcessQueue
        self._poll_frequency = 0.1
        self.u.triggerTimer()

        d = defer.Deferred()
        d.addCallback(doneOk)
        reactor.callLater(1, lambda: d.callback(self))
        return d

    def testTriggerTimer_alreadyHaveActiveTimer(self):
        """Testing triggerTimer when it already has an active timer
        """
        self.assertEquals(self.u._timer, None)
        class  MockTimer:
            def __init__(self): self.myID = "MOCK"
            def active(self): return True

        self.u._timer = MockTimer()

        def doneOk(mySelf):
            mySelf.assertEquals(mySelf.u._timer.myID, "MOCK")

        # Note that _poll is removed because it should never actually be
        # read and if it is, we know something has gone wrong with test.
        del self.u.__dict__['_poll']

        return self.triggerTimer_expectNoCallLater(doneOk)

    def testTriggerTimer_inactiveTimerNoPoll(self):
        """Testing triggerTimer when timer exists, is inactive, but not polling
        """
        self.assertEquals(self.u._timer, None)
        class  MockTimer:
            def __init__(self): self.myID = "MOCK2"
            def active(self): return False

        self.u._timer = MockTimer()

        def doneOk(mySelf):
            mySelf.assertEquals(mySelf.u._timer.myID, "MOCK2")

        self.u._poll = False

        return self.triggerTimer_expectNoCallLater(doneOk)

    def testTriggerTimer_noTimerPollingEmptyQueues(self):
        """Testing triggerTimer without timer, polling on, empty queue
        """
        self.assertEquals(self.u._timer, None)

        def doneOk(mySelf):
            mySelf.assertEquals(mySelf.u._timer, None)

        self.u._poll = True

        return self.triggerTimer_expectNoCallLater(doneOk)

    def testTriggerTimer_reactorIsCalled(self):
        """Testing triggerTimer when reactor is called
        """
        self.assertEquals(self.u._timer, None)
        self.u._poll = True
        self.u.getOrCreateQueue(0)

        global processQueueCalled
        processQueueCalled = 0
        def mockProcessQueue():
            global processQueueCalled
            processQueueCalled += 1
            
        self.u._processQueues = mockProcessQueue

        def doneOk(mySelf):
            global processQueueCalled
            self.assertEquals(processQueueCalled, 1)

        d = defer.Deferred()
        d.addCallback(doneOk)
        # Note, if test fails, you'll get a reactor error.
        reactor.callLater(1, lambda: d.callback(self))

        self.u.triggerTimer()

        return d

    def testPushPacket(self):
        """Testing pushPacket"""
        global triggerTimerCallCount
        triggerTimerCallCount = 0
        def mockTriggerTimer():
            global triggerTimerCallCount
            triggerTimerCallCount += 1
            
        self.u.triggerTimer = mockTriggerTimer
       
        self.u._packet2front = lambda x:  x <= 0

        self.u.pushPacket( FakePacket(1) );        
        self.u.pushPacket( FakePacket(0) );        
        
        assert len(self.u._queues[0].packets) == 2  , "packets not in list"
        assert self.u._queues[0].packets[0].arg <  self.u._queues[0].packets[1].arg  , "packet not set in front of the queue"
        self.assertEquals(triggerTimerCallCount, 2)

    def testHandleData(self):
        """Testing handleData"""
        fakeProcessQueuesDeferred = self.fakeProcessQueuesDeferred()

        self.u._expected_len = 3
        self.u._packet.append("\x00\x00\x03")
        self.u._packet_len = len("\x00\x00\x03")
        clear_all_messages()
        self.u.handleData() 
        self.assertEquals(get_messages(), ['(3 bytes) => type = NONE(0)'])

        self.u._poll = False
        self.u._packet.append("\x00\x00\x03")
        self.u._packet_len = len("\x00\x00\x03")
        clear_all_messages()
        self.u.handleData()
        self.assertEquals(get_messages(), ['(3 bytes) => type = NONE(0)'])

        self.u._packet.append("\xff\x00\x03")
        self.u._packet_len = len("\xff\x00\x03")
        clear_all_messages()
        self.u.handleData()
        self.assertEquals(get_messages(), [': unknown message received (id 255, length 3)\n', "known types are {0: 'NONE', 1: 'STRING', 2: 'INT', 3: 'ERROR', 4: 'ACK', 5: 'PING', 6: 'SERIAL', 7: 'QUIT', 8: 'AUTH_OK', 9: 'AUTH_REFUSED', 10: 'LOGIN', 11: 'AUTH_REQUEST', 12: 'LIST', 13: 'LOGOUT', 14: 'BOOTSTRAP', 15: 'PROTOCOL_ERROR', 16: 'MESSAGE', 50: 'POKER_SEATS', 51: 'POKER_ID', 52: 'POKER_MESSAGE', 53: 'ERROR', 54: 'POKER_POSITION', 55: 'POKER_INT', 56: 'POKER_BET', 57: 'POKER_FOLD', 58: 'POKER_STATE', 59: 'POKER_WIN', 60: 'POKER_CARDS', 61: 'POKER_PLAYER_CARDS', 62: 'POKER_BOARD_CARDS', 63: 'POKER_CHIPS', 64: 'POKER_PLAYER_CHIPS', 65: 'POKER_CHECK', 66: 'POKER_START', 67: 'POKER_IN_GAME', 68: 'POKER_CALL', 69: 'POKER_RAISE', 70: 'POKER_DEALER', 71: 'POKER_TABLE_JOIN', 72: 'POKER_TABLE_SELECT', 73: 'POKER_TABLE', 74: 'POKER_TABLE_LIST', 75: 'POKER_SIT', 76: 'POKER_TABLE_DESTROY', 77: 'POKER_TIMEOUT_WARNING', 78: 'POKER_TIMEOUT_NOTICE', 79: 'POKER_SEAT', 80: 'POKER_TABLE_MOVE', 81: 'POKER_PLAYER_LEAVE', 82: 'POKER_SIT_OUT', 83: 'POKER_TABLE_QUIT', 84: 'POKER_BUY_IN', 85: 'POKER_REBUY', 86: 'POKER_CHAT', 87: 'POKER_PLAYER_INFO', 88: 'POKER_PLAYER_ARRIVE', 89: 'POKER_HAND_SELECT', 90: 'POKER_HAND_LIST', 91: 'POKER_HAND_SELECT_ALL', 92: 'POKER_USER_INFO', 93: 'POKER_GET_USER_INFO', 94: 'POKER_ANTE', 95: 'POKER_BLIND', 96: 'POKER_WAIT_BIG_BLIND', 97: 'POKER_AUTO_BLIND_ANTE', 98: 'POKER_NOAUTO_BLIND_ANTE', 99: 'POKER_CANCELED', 100: 'POKER_BLIND_REQUEST', 101: 'POKER_ANTE_REQUEST', 102: 'POKER_AUTO_FOLD', 103: 'POKER_WAIT_FOR', 104: 'POKER_STREAM_MODE', 105: 'POKER_BATCH_MODE', 106: 'POKER_LOOK_CARDS', 107: 'POKER_TABLE_REQUEST_PLAYERS_LIST', 108: 'POKER_PLAYERS_LIST', 109: 'POKER_PERSONAL_INFO', 110: 'POKER_GET_PERSONAL_INFO', 111: 'POKER_TOURNEY_SELECT', 112: 'POKER_TOURNEY', 113: 'POKER_TOURNEY_INFO', 114: 'POKER_TOURNEY_LIST', 115: 'POKER_TOURNEY_REQUEST_PLAYERS_LIST', 116: 'POKER_TOURNEY_REGISTER', 117: 'POKER_TOURNEY_UNREGISTER', 118: 'POKER_TOURNEY_PLAYERS_LIST', 119: 'POKER_HAND_HISTORY', 120: 'POKER_SET_ACCOUNT', 121: 'POKER_CREATE_ACCOUNT', 122: 'POKER_PLAYER_SELF', 123: 'POKER_GET_PLAYER_INFO', 124: 'POKER_ROLES', 125: 'POKER_SET_ROLE', 126: 'POKER_READY_TO_PLAY', 127: 'POKER_PROCESSING_HAND', 128: 'POKER_MUCK_REQUEST', 129: 'POKER_AUTO_MUCK', 130: 'POKER_MUCK_ACCEPT', 131: 'POKER_MUCK_DENY', 132: 'POKER_CASH_IN', 133: 'POKER_CASH_OUT', 134: 'POKER_CASH_OUT_COMMIT', 135: 'POKER_CASH_QUERY', 136: 'POKER_RAKE', 137: 'POKER_TOURNEY_RANK', 138: 'POKER_PLAYER_IMAGE', 139: 'POKER_GET_PLAYER_IMAGE', 140: 'POKER_HAND_REPLAY', 141: 'POKER_GAME_MESSAGE', 142: 'POKER_EXPLAIN', 143: 'POKER_STATS_QUERY', 144: 'POKER_STATS', 145: 'POKER_BUY_IN_LIMITS', 146: 'POKER_MONITOR', 147: 'POKER_MONITOR_EVENT', 148: 'POKER_GET_TOURNEY_MANAGER', 149: 'POKER_TOURNEY_MANAGER', 151: 'POKER_GET_PLAYER_PLACES', 152: 'POKER_PLAYER_PLACES', 153: 'POKER_SET_LOCALE', 154: 'POKER_TABLE_TOURNEY_BREAK_BEGIN', 155: 'POKER_TABLE_TOURNEY_BREAK_DONE', 156: 'POKER_TOURNEY_START', 161: 'POKER_PLAYER_STATS', 164: 'POKER_TOURNEY_INFO', 165: 'POKER_TABLE_PICKER', 166: 'POKER_CREATE_TOURNEY', 167: 'POKER_LONG_POLL', 168: 'POKER_LONG_POLL_RETURN', 170: 'POKER_BEST_CARDS', 171: 'POKER_POT_CHIPS', 172: 'POKER_CLIENT_ACTION', 173: 'POKER_BET_LIMIT', 174: 'POKER_SIT_REQUEST', 175: 'POKER_PLAYER_NO_CARDS', 176: 'POKER_CHIPS_PLAYER2BET', 177: 'POKER_CHIPS_BET2POT', 178: 'POKER_CHIPS_POT2PLAYER', 179: 'POKER_CHIPS_POT_MERGE', 180: 'POKER_CHIPS_POT_RESET', 181: 'POKER_CHIPS_BET2PLAYER', 182: 'POKER_END_ROUND', 183: 'POKER_DISPLAY_NODE', 184: 'POKER_DEAL_CARDS', 185: 'POKER_CHAT_HISTORY', 186: 'POKER_DISPLAY_CARD', 187: 'POKER_SELF_IN_POSITION', 188: 'POKER_SELF_LOST_POSITION', 189: 'POKER_HIGHEST_BET_INCREASE', 190: 'POKER_PLAYER_WIN', 191: 'POKER_ANIMATION_PLAYER_NOISE', 192: 'POKER_ANIMATION_PLAYER_FOLD', 193: 'POKER_ANIMATION_PLAYER_BET', 194: 'POKER_ANIMATION_PLAYER_CHIPS', 195: 'POKER_ANIMATION_DEALER_CHANGE', 196: 'POKER_ANIMATION_DEALER_BUTTON', 197: 'POKER_BEGIN_ROUND', 198: 'POKER_CURRENT_GAMES', 199: 'POKER_END_ROUND_LAST', 200: 'POKER_PYTHON_ANIMATION', 201: 'POKER_SIT_OUT_NEXT_TURN', 202: 'POKER_RENDERER_STATE', 203: 'POKER_CHAT_WORD', 204: 'POKER_SHOWDOWN', 205: 'POKER_CLIENT_PLAYER_CHIPS', 206: 'POKER_INTERFACE_COMMAND', 207: 'POKER_PLAYER_ME_LOOK_CARDS', 208: 'POKER_PLAYER_ME_IN_FIRST_PERSON', 209: 'POKER_ALLIN_SHOWDOWN', 210: 'POKER_PLAYER_HAND_STRENGTH'} "])
        # trying with wrong packet
        self.u._packet.append("\xff\x00\x00")
        self.u._packet_len = len("\xff\x00\x00")
        clear_all_messages()
        self.u.handleData()
        # FIXME (maybe): I am not completely sure it's correct that we
        # should get absolutely no output when we send the "wrong packet".
        # I've asked Loic to take a look.
        self.assertEquals(get_messages(), [])
        return fakeProcessQueuesDeferred
        
    def testDataReceived(self):
        """Testing dataReceived"""
        global handledVersion
        global handledData
        handledData = handledVersion = 0

        def mockHandleVersion():
            global handledVersion
            handledVersion += 1

        def mockHandleData():
            global handledData
            handledData += 1

        self.u._handleVersion = mockHandleVersion
        self.u.handleData = mockHandleData

        self.assertEquals(self.u._packet, [])
        self.assertEquals(self.u._packet_len, 0)

        self.u.dataReceived("packet_1")

        self.assertEquals(self.u._packet, ['packet_1'])
        self.assertEquals(self.u._packet_len, 8)
        self.failIf(handledData > 0)
        self.failUnless(handledVersion == 1)
        self.assertEquals(self.u.established, 0)

        handledVersion = 0
        self.u.established = 1
        self.u.dataReceived("packet_2  ")

        self.assertEquals(self.u._packet, ['packet_1', 'packet_2  '])
        self.assertEquals(self.u._packet_len, 18)
        self.failIf(handledVersion > 0)
        self.failUnless(handledData == 1)
        
    def testForceError(self):
        """Testing error call"""
        clear_all_messages()
        self.u.error("testing this error")
        self.assertEquals(get_messages(), ["ERROR testing this error"])

    def testCoverDataWrite(self):
        """Testing data write"""
        clear_all_messages()
        tot = protocol.UGAMEProtocol._stats_write

        global calledWrite
        calledWrite = 0
        myData = "testing data"
        def mockTransportWrite(data):
            global calledWrite
            self.assertEquals(data, myData)
            calledWrite += 1
        self.u.transport.write = mockTransportWrite

        self.u.dataWrite(myData)

        self.assertEquals(tot + len(myData), protocol.UGAMEProtocol._stats_write)

        self.assertEquals(calledWrite, 1)
        self.assertEquals(get_messages(), [])

#------------------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
    # Comment in line below this when you wish to run just one test by
    # itself (changing prefix as needed).
#    loader.methodPrefix = "testProcess"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(QueueTestCase))
    suite.addTest(loader.loadClass(UGAMEProtocolTestCase))
    return runner.TrialRunner(
        reporter.VerboseTextReporter,
#	tracebackFormat='verbose',
        tracebackFormat='default',
        ).run(suite)
# ----------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-protocol.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/protocol.py' TESTS='coverage-reset test-protocol.py coverage-report' check )"
# End:
