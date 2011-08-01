#!/usr/bin/python
# -*- py-indent-offset: 4; coding: iso-8859-1; mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C)       2008 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C) 2006       Mekensleep
#                          24 rue vieille du temple 75004 Paris
#                          <licensing@mekensleep.com>
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
#  Loic Dachary <loic@dachary.org>
#  Bradley M. Kuhn <bkuhn@ebb.org>
#
import sys, os
sys.path.insert(0, "./..")
sys.path.insert(0, "..")

from twisted.trial import unittest, runner, reporter
from twisted.internet import protocol, reactor, defer
from twisted.application import service

#
# Must be done before importing pokerclient or pokerclient
# will have to be patched too.
#
from tests import testclock

from tests.testmessages import restore_all_messages, silence_all_messages, search_output, clear_all_messages, get_messages
#os.environ['VERBOSE_T'] = '0'
verbose = int(os.environ.get('VERBOSE_T', '-1'))
#if verbose < 0: silence_all_messages()

import twisted.internet.base
twisted.internet.base.DelayedCall.debug = True

import pokernetwork.server
import pokernetwork.client
import pokernetwork.protocol
from pokernetwork.packets import *

class FakeService(service.Service):
    def __init__(self):
        self._ping_delay = 0.1

class FakeAvatar:
    def __init__(self):
        pass

    def setProtocol(self, protocol):
        if verbose > 0:
            print "SetProtocol"
        self.protocol = protocol

    def handlePacket(self, packet):
        print "FakeAvatar: handlePacket " + str(packet)
        if packet.type == PACKET_ERROR:
            raise Exception, "EXCEPTION TEST"
        return []

class  FakeUser:
    def __init__(self):
        self.name = "Mr.Fakey"
        self.serial = -1

class FakeFactory(protocol.ServerFactory):

    def __init__(self, testObject = None):
        self.tester = testObject
        self.service = FakeService()
        self.verbose = 7
        self.destroyedAvatars = []

    def createAvatar(self):
        return FakeAvatar()

    def destroyAvatar(self, avatar):
        self.destroyedAvatars.append(avatar)
    
    def buildProtocol(self, addr):
        class Transport:
            def __init__(self):
                self.loseConnectionCount = 0

            def loseConnection(self):
                self.loseConnectionCount += 1

            def setTcpKeepAlive(self, val):
                pass
        self.instance = pokernetwork.server.PokerServerProtocol()

        # Asserts that assure PokerServerProtocol.__init__() acts as
        # expected
        self.tester.assertEquals(self.instance._ping_timer, None)
        self.tester.assertEquals(self.instance._ping_delay, 10)
        self.tester.assertEquals(self.instance.avatar, None)
        self.tester.assertEquals(self.instance.bufferized_packets, [])

        # Set up variables and mock ups for tests 
        self.instance.transport = Transport()
        self.instance.verbose = 7
        self.instance.exception = None
        self.instance.factory = self
        self.instance.user = FakeUser()
        return self.instance

class ClientServerTestBase(unittest.TestCase):
    def setUpServer(self):
        self.server_factory = FakeFactory(self)
        self.p = reactor.listenTCP(0, self.server_factory,
                                   interface="127.0.0.1")
        self.port = self.p.getHost().port
        if verbose > 0:
            print "Listening on 127.0.0.1:" + str(self.port)

    def setUpClient(self, index):
        self.client_factory[index] = pokernetwork.client.UGAMEClientFactory()
        self.client_factory[index].verbose = 7
        def setUpProtocol(client):
            client._poll_frequency = 0.1
            return client
        d = self.client_factory[index].established_deferred
        d.addCallback(setUpProtocol)

    def setUp(self):
        self.setUpServer()
        self.client_factory = [None, None]
        self.setUpClient(0)
        reactor.connectTCP('127.0.0.1', self.port, self.client_factory[0])
        if verbose > 0:
            print "Connecting on 127.0.0.1:" + str(self.port)

    def cleanSessions(self, arg):
        #
        # twisted Session code has leftovers : disable the hanging delayed call warnings
        # of trial by nuking all what's left.
        #
        pending = reactor.getDelayedCalls()
        if pending:
            for p in pending:
                if p.active():
#                    print "still pending:" + str(p)
                    p.cancel()
        return arg
    # -----------------------------------------------------------------------        
    def tearDown(self):
        reactor.iterate()
        reactor.iterate()
        self.p.stopListening()
        return self.cleanSessions(None)

class ClientServer(ClientServerTestBase):
    # -----------------------------------------------------------------------        
    def quit(self, args):
        client = args[0]
        client.sendPacket(PacketQuit())
        client.transport.loseConnection()
        server = self.server_factory.instance
        def serverPingTimeout(val):
            self.assertEqual(search_output("ping: timeout Mr.Fakey/-1"), True)
        client.connection_lost_deferred.addCallback(serverPingTimeout)
        silence_all_messages()
        return client.connection_lost_deferred
    # -----------------------------------------------------------------------        
    def ping(self, client):
        clear_all_messages()
        client.sendPacket(PacketPing())
        self.assertEquals(get_messages(), ["sendPacket(0) type = PING(5) "])
        return (client,)
    # -----------------------------------------------------------------------        
    def pingExpectingPrefix(self, client):
        clear_all_messages()
        client.sendPacket(PacketPing())
        self.assertEquals(get_messages(),
                          ["ATesterPrefix: sendPacket(0) type = PING(5) "])
        return (client,)
    # -----------------------------------------------------------------------        
    def setPrefix(self, client):
        client._prefix = "ATesterPrefix: "
        return client
    # -----------------------------------------------------------------------        
    def test01_ping(self):
        d = self.client_factory[0].established_deferred
        silence_all_messages()
        d.addCallback(self.ping)
        d.addCallback(self.quit)
        return d
    # -----------------------------------------------------------------------        
    def test02_pingExpectingPrefix(self):
        d = self.client_factory[0].established_deferred
        silence_all_messages()
        d.addCallback(self.setPrefix)
        d.addCallback(self.pingExpectingPrefix)
        d.addCallback(self.quit)
        return d

    def exception(self, client):
        client.sendPacket(PacketError())
        d = client.connection_lost_deferred
        def validate(result, count):
            server_protocol = self.server_factory.instance
            if server_protocol.exception:
                self.assertEquals("EXCEPTION TEST", str(server_protocol.exception[1]))
            else:
                if count >= 5: print "Waiting for exception to be raised ",
                if count > 0: print ".",
                if count == 0:
                    self.fail("exception was not received")
                else:
                    reactor.callLater(1, lambda: validate(result, count -1))

        d.addCallback(lambda result: validate(result, 5))
        return d
        
    def test02_exception(self):
        d = self.client_factory[0].established_deferred
        d.addCallback(self.exception)
        return d

    # -----------------------------------------------------------------------
    def killThenPing(self, client):
        self.messageValue = ""
        def getMessage(str):
            self.messageValue += str
        client.message = getMessage
        def sendLostConnectionPacket(val):
            client.sendPacket(PacketPing())
            self.assertEqual(self.messageValue.find("ufferized") >= 0, True)
            self.assertEqual(len(client.bufferized_packets), 1)
            self.assertEqual(client.bufferized_packets[0].type, PACKET_PING)
        d = client.connection_lost_deferred
        d.addCallback(sendLostConnectionPacket)
        return d

    def test03_killThenPing(self):
        "Designed to cover client.py when it tests for established"
        d = self.client_factory[0].established_deferred
        d.addCallback(self.killThenPing)
        return d

    # -----------------------------------------------------------------------
    def deadServerTransport(self, client):
        server = self.server_factory.instance
        saveMyTransport = server.transport
        server.transport = None

        self.messageValue = ""
        def getMessage(str):
            self.messageValue += str
        server.message = getMessage

        server.sendPackets([PacketPing()])
        self.assertEquals(len(server.bufferized_packets), 1)
        self.assertEquals(server.bufferized_packets[0].type, PACKET_PING)
        self.assertEquals(self.messageValue.find("bufferized") > 0, True)
        self.assertEquals(self.messageValue.find("no usuable transport") > 0, True)
        server.transport = saveMyTransport
        return client.connection_lost_deferred

    def test04_deadServerTransport(self):
        """Covers the case where there is no transport available and the
        packets must be buffered by the server."""
        d = self.client_factory[0].established_deferred
        d.addCallback(self.deadServerTransport)
        return d
    # -----------------------------------------------------------------------
    def clientConnectionLost(self, client):
        class ReasonMockUp:
            def __str__(self):
                return "you mock me"
            def check(self, foo):
                return False
        silence_all_messages()
        clear_all_messages()
        client.connectionLost(ReasonMockUp())
        self.assertEquals(get_messages(), ['connectionLost: reason = you mock me',
                                           'UGAMEClient.connectionLost you mock me'])
        self.assertEquals(client._ping_timer, None)
        self.assertEquals(self.client_factory[0].protocol_instance,  None)
        return True

    def test05_clientConnectionLost(self):
        """Covers the case where the client connection is lost"""
        d = self.client_factory[0].established_deferred
        d.addCallback(self.clientConnectionLost)
        return d
    # -----------------------------------------------------------------------
    def dummyClientError(self, client):
        silence_all_messages()
        clear_all_messages()
        client.error("stupid dummy error test since client never calls")
        self.assertEquals(get_messages(),
                          ["ERROR stupid dummy error test since client never calls"])
        return (client,)
    # -----------------------------------------------------------------------
    def test06_dummyClientError(self):
        """At the time of writing, client.error() is not used internally
        to client, so this is a call to test its use"""
        d = self.client_factory[0].established_deferred
        d.addCallback(self.dummyClientError)
        return d
    # -----------------------------------------------------------------------
    def test07_bufferizedClientPackets(self):
        silence_all_messages()
        d = self.client_factory[0].established_deferred
        def bufferPackets(client):
            def checkOutput(client):
                msgs = get_messages()
                self.assertEquals(msgs[0], 'sendPacket(0) type = ACK(4) ')
                return (client,)

            client.bufferized_packets = [ PacketAck() ]
            clear_all_messages()
            ccd = client.connection_lost_deferred
            ccd.addCallback(checkOutput)
            return ccd

        d.addCallback(bufferPackets)
        return d
    # -----------------------------------------------------------------------
    def test08_bufferizedClientPacketsTwo(self):
        silence_all_messages()
        d = self.client_factory[0].established_deferred
        def bufferPackets(client):
            def checkOutput(client):
                msgs = get_messages()
                self.assertEquals(msgs[0], 'sendPacket(0) type = ACK(4) ')
                self.assertEquals(msgs[1], 'sendPacket(0) type = SERIAL(6) serial = 0 ')
                return (client,)

            client.bufferized_packets = [ PacketAck(), PacketSerial() ]
            clear_all_messages()
            ccd = client.connection_lost_deferred
            ccd.addCallback(checkOutput)
            return ccd

        d.addCallback(bufferPackets)
        return d
#    def test09_badClientProtocol(self):
#        pass
#-------------------------------------------------------------------------------
class ClientServerBadClientProtocol(ClientServerTestBase):
    def setUpServer(self):
        class BadVersionFakeFactory(FakeFactory):
            def buildProtocol(self, addr):
                proto = FakeFactory.buildProtocol(self, addr)
                def badSendVersion():
                    proto.transport.write('CGI 0.00\n')
                proto._sendVersion = badSendVersion
                return proto

        self.server_factory = BadVersionFakeFactory(self)
        self.p = reactor.listenTCP(0, self.server_factory,
                                   interface="127.0.0.1")
        self.port = self.p.getHost().port
        if verbose > 0:
            print "Listening on 127.0.0.1:" + str(self.port)
    # -----------------------------------------------------------------------
    def test01_badClientProtocol(self):
        silence_all_messages()
        d = self.client_factory[0].established_deferred
        def findError(myFailure):
            from pokernetwork.protocol import PROTOCOL_MAJOR, PROTOCOL_MINOR
            msg = myFailure.getErrorMessage()
            self.failIf(msg.find("'0.00\\n', '%s.%s')" 
                                 % (PROTOCOL_MAJOR, PROTOCOL_MINOR )) < 0)
            self.failIf(msg.find("(<pokernetwork.client.UGAMEClientProtocol instance at") > 0)
        d.addErrback(findError)
        return d
#-------------------------------------------------------------------------------
class ClientServerQueuedServerPackets(ClientServerTestBase):
    def setUpServer(self):
        class BufferedFakeFactory(FakeFactory):
            def buildProtocol(self, addr):
                proto = FakeFactory.buildProtocol(self, addr)
                silence_all_messages()
                clear_all_messages()
                proto.bufferized_packets.append(PacketAck())
                return proto

        self.server_factory = BufferedFakeFactory(self)
        self.p = reactor.listenTCP(0, self.server_factory,
                                   interface="127.0.0.1")
        self.port = self.p.getHost().port
        if verbose > 0:
            print "Listening on 127.0.0.1:" + str(self.port)
    # -----------------------------------------------------------------------
    def getServerPacket(self, client):
        self.failUnless(search_output('protocol established'))
        clear_all_messages()
        def findBufferedAckPacket(client):
            self.failUnless(search_output("(3 bytes) => type = ACK(4)"))

        d = client.connection_lost_deferred
        d.addCallback(findBufferedAckPacket)
        return d
    # -----------------------------------------------------------------------
    def test01_getServerPacket(self):
        d = self.client_factory[0].established_deferred
        d.addCallback(self.getServerPacket)
        return d
#-------------------------------------------------------------------------------
class ClientServerDeferredServerPackets(ClientServerTestBase):
    def deferPacket(self, client):
        server = self.server_factory.instance
        self.failUnless(search_output('protocol established'))
        clear_all_messages()
        self.deferredPacket = defer.Deferred()
        server.sendPackets([ self.deferredPacket, PacketAck()])
        self.assertEquals(get_messages(), [])
        self.deferredPacket.callback(PacketPing())
        self.assertEquals(get_messages(), [])

        def callbackDeferredPacket(client):
            pingFound = False
            ackFound = False
            msgs = get_messages()
            for msg in get_messages():
                if msg == '(3 bytes) => type = PING(5)':
                    self.failIf(pingFound or ackFound)
                    pingFound = True
                elif msg == '(3 bytes) => type = ACK(4)':
                    self.failUnless(pingFound)
                    ackFound = True
            self.failUnless(ackFound and pingFound)

        d = client.connection_lost_deferred
        d.addCallback(callbackDeferredPacket)
        return d
    # -----------------------------------------------------------------------
    def test01_deferredPacket(self):
        d = self.client_factory[0].established_deferred
        d.addCallback(self.deferPacket)
        return d
    # -----------------------------------------------------------------------
    def deferErrorPacket(self, client):
        server = self.server_factory.instance
        clear_all_messages()
        self.deferredPacket = defer.Deferred()
        server.sendPackets([ self.deferredPacket, PacketAck()])
        self.assertEquals(get_messages(), [])
        self.deferredPacket.errback("forced to fail")
        self.assertEquals(get_messages(), [])

        def callbackDeferredPacket(client):
            errFound = False
            ackFound = False
            msgs = get_messages()
            for msg in get_messages():
                if msg == "(132 bytes) => type = ERROR(3) message = [Failure instance: Traceback (failure with no frames): <class 'twisted.python.failure.DefaultException'>: forced to fail\n], code = 0, other_type = ERROR":
                    self.failIf(errFound or ackFound)
                    errFound = True
                elif msg == '(3 bytes) => type = ACK(4)':
                    self.failUnless(errFound)
                    ackFound = True
            self.failUnless(ackFound and errFound)

        d = client.connection_lost_deferred
        d.addCallback(callbackDeferredPacket)
        return d
    # -----------------------------------------------------------------------
    def test02_deferredErrBackPacket(self):
        d = self.client_factory[0].established_deferred
        d.addCallback(self.deferErrorPacket)
        return d
# -----------------------------------------------------------------------
# Following class is used for the DummyServerTests and DummyClientTests
# for the ping code.
class  MockPingTimer:
    def __init__(self):
        self.isActive = False
        self.resetValues = []
        self.cancelCount = 0
    def active(self):
        return self.isActive
    def reset(self, val):
        self.resetValues.append(val)
    def cancel(self):
        self.cancelCount += 1
#-------------------------------------------------------------------------------
# DummyServerTests are to cover code on the server that doesn't need a
# client running to test it.

class DummyServerTests(unittest.TestCase):
    def test01_invalidProtocol(self):
        self.server_factory = FakeFactory(self)
        silence_all_messages()
        self.server_factory.buildProtocol('addr').dataReceived("invalid protocol\n")
        if verbose < 0: # can only grep output when output is redirected
            self.assertEqual(search_output('client with protocol UNKNOWN rejected'), True)
    # -----------------------------------------------------------------------
    def test02_pingWithoutTimer(self):
        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        del  server.__dict__['_ping_timer']
        self.assertEquals(server.ping(), None)
        self.assertEqual(get_messages(), [])
    # -----------------------------------------------------------------------
    def test03_pingWithNoneTimer(self):
        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        server._ping_timer = None
        self.assertEquals(server.ping(), None)
        self.assertEqual(get_messages(), [])
    # -----------------------------------------------------------------------
    def test04_pingWithActiveTimerNoUser(self):
        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        pt = MockPingTimer()
        pt.isActive = True
        server._ping_timer = pt
        del  server.__dict__['user']
        self.assertEquals(server.ping(), None)
        self.assertEquals(pt, server._ping_timer)
        self.assertEquals(pt.resetValues, [ 10 ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(server.transport.loseConnectionCount, 0)
        self.assertEqual(get_messages(), [])
    # -----------------------------------------------------------------------
    def test05_pingWithActiveTimerWithUser(self):
        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        pt = MockPingTimer()
        pt.isActive = True
        server._ping_timer = pt
        self.assertEquals(server.ping(), None)
        self.assertEquals(pt, server._ping_timer)
        self.assertEquals(pt.resetValues, [ 10 ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(server.transport.loseConnectionCount, 0)
        self.assertEqual(get_messages(), ['ping: renew Mr.Fakey/-1'])
    # -----------------------------------------------------------------------
    def test06_pingWithInactiveTimerNoUser(self):
        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        pt = MockPingTimer()
        server._ping_timer = pt
        del  server.__dict__['user']
        self.assertEquals(server.ping(), None)
        self.assertEquals(server._ping_timer, None)
        self.assertEquals(pt.resetValues, [ ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(server.transport.loseConnectionCount, 1)
        self.assertEqual(get_messages(), [])
    # -----------------------------------------------------------------------
    def test07_pingWithInactiveTimerWithUser(self):
        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        pt = MockPingTimer()
        server._ping_timer = pt
        self.assertEquals(server.ping(), None)
        self.assertEquals(server._ping_timer, None)
        self.assertEquals(pt.resetValues, [ ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(server.transport.loseConnectionCount, 1)
        self.assertEqual(get_messages(), ['ping: timeout Mr.Fakey/-1'])
    # -----------------------------------------------------------------------
    def processQueuesCounter(self):
        global processQueuesCount
        processQueuesCount += 1

    def ignoreIncomingDataCounter(self):
        global ignoreIncomingDataCount
        ignoreIncomingDataCount += 1
    # -----------------------------------------------------------------------
    def test08_connectionLostNonePingTimerNoAvatar(self):
        global processQueuesCount
        processQueuesCount = 0
        global ignoreIncomingDataCount
        ignoreIncomingDataCount = 0

        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')

        server._processQueues = self.processQueuesCounter
        server.ignoreIncomingData = self.ignoreIncomingDataCounter

        server._ping_timer = None
        server._queues = []
        server.avatar = None
 
        self.assertEquals(server.connectionLost("test08"), None)

        self.failIf(server.__dict__.has_key('avatar'))
        self.assertEquals(server._ping_timer, None)
        self.assertEquals(processQueuesCount, 0)
        self.assertEquals(ignoreIncomingDataCount, 1)
        self.assertEquals(self.server_factory.destroyedAvatars, [])

        self.assertEquals(get_messages(), ['connectionLost: reason = test08',
                                           'connectionLost: reason = test08',
                                           'client with protocol different rejected (need 002.000)'])
    # -----------------------------------------------------------------------
    def test09_connectionLostNoPingTimerWithAvatarButNoQueues(self):
        global processQueuesCount
        processQueuesCount = 0

        global ignoreIncomingDataCount
        ignoreIncomingDataCount = 0

        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        server._protocol_ok = True
        
        server._processQueues = self.processQueuesCounter
        server.ignoreIncomingData = self.ignoreIncomingDataCounter

        del server._ping_timer
        server._queues = []
        server.avatar = FakeAvatar()

        self.assertEquals(server.connectionLost("test09"), None)

        self.failIf(server.__dict__.has_key('avatar'))
        self.assertEquals(server._ping_timer, None)
        self.assertEquals(processQueuesCount, 0)
        self.assertEquals(ignoreIncomingDataCount, 1)
        self.assertEquals(len(self.server_factory.destroyedAvatars), 1)
        self.failUnless(isinstance(self.server_factory.destroyedAvatars[0], 
                                   FakeAvatar))
        self.assertEquals(get_messages(), ['connectionLost: reason = test09'])

    # -----------------------------------------------------------------------
    def test10_connectionLostWithInactivePingTimerWithAvatarAndQueues(self):
        global processQueuesCount
        processQueuesCount = 0

        global ignoreIncomingDataCount
        ignoreIncomingDataCount = 0

        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        server._protocol_ok = True
        
        def actualButDummyProcessQueueCounter():
            global processQueuesCount
            processQueuesCount += 1
            if processQueuesCount > 1:
                server._queues = []

        server._processQueues = actualButDummyProcessQueueCounter
        server.ignoreIncomingData = self.ignoreIncomingDataCounter

        pt = MockPingTimer()
        server._ping_timer = pt
        server._queues = ['a', 'b', 'c']
        server.avatar = FakeAvatar()

        self.assertEquals(server.connectionLost("test10"), None)

        self.failIf(server.__dict__.has_key('avatar'))
        self.assertEquals(server._ping_timer, None)
        self.assertEquals(processQueuesCount, 2)
        self.assertEquals(ignoreIncomingDataCount, 1)
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(pt.resetValues, [])
        self.assertEquals(len(self.server_factory.destroyedAvatars), 1)
        self.failUnless(isinstance(self.server_factory.destroyedAvatars[0], 
                                   FakeAvatar))
        self.assertEquals(get_messages(), ['connectionLost: reason = test10'])
    # -----------------------------------------------------------------------
    def test11_connectionLostActivePingTimerNoAvatarOneQueues(self):
        global processQueuesCount
        processQueuesCount = 0

        global ignoreIncomingDataCount
        ignoreIncomingDataCount = 0

        clear_all_messages()
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')
        server._protocol_ok = True
        
        def actualButDummyProcessQueueCounter():
            global processQueuesCount
            processQueuesCount += 1
            server._queues = []

        server._processQueues = actualButDummyProcessQueueCounter
        server.ignoreIncomingData = self.ignoreIncomingDataCounter

        pt = MockPingTimer()
        pt.isActive = True
        server._ping_timer = pt
        server._queues = ['b', 'c']
        server.avatar = None

        self.assertEquals(server.connectionLost("test11"), None)

        self.failIf(server.__dict__.has_key('avatar'))
        self.assertEquals(server._ping_timer, None)
        # Queues don't get processed when lost connection without avatar
        self.assertEquals(processQueuesCount, 0)
        self.assertEquals(ignoreIncomingDataCount, 1)
        self.assertEquals(pt.cancelCount, 1)
        self.assertEquals(pt.resetValues, [])
        self.assertEquals(self.server_factory.destroyedAvatars, [])
        self.assertEquals(get_messages(), ['connectionLost: reason = test11'])
    # -----------------------------------------------------------------------
    def test12_handleConnectionNoException(self):
        """test12_handleConnectionNoException
        This and the following test is a mock-up test of server's
        _handleConnection() method.  I had searched for a way to test this
        particular method in a more interactive way using a real
        client/server connection in one of the classes above.  However, I
        was not able to find a way to force this method to be called using
        the MockUps already developed in the above test classes, and
        decided it was more expedient to test this method using these
        dummy server mechanism here."""

        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')

        pt = MockPingTimer()
        pt.isActive = True
        server._ping_timer = pt

        class MockAvatar:
            def __init__(avatarSelf, expected = None):
                avatarSelf.handlePacketCount = 0
                avatarSelf.expectedPacket = expected
            def handlePacket(avatarSelf, packet):
                global triggerCount
                global sendPacketsCount
                avatarSelf.handlePacketCount += 1
                self.assertEquals(packet, avatarSelf.expectedPacket)
                self.assertEquals(pt, server._ping_timer)
                self.assertEquals(pt.resetValues, [ 10 ])
                self.assertEquals(pt.cancelCount, 0)
                self.assertEquals(server._blocked, True)
                self.assertEquals(sendPacketsCount, 0)
                return "handlePacketsReturn"

        avatar = MockAvatar("test12 dummy packets")

        global sendPacketsCount
        triggerCount = 0
        sendPacketsCount = 0
        def doMyTrigger():
            self.failIf(True) # should never be called!
        def doSendPackets(packets):
            global sendPacketsCount
            sendPacketsCount += 1
            self.assertEquals(packets, "handlePacketsReturn")

        server.avatar = avatar
        server._blocked = False

        server.triggerTimer = doMyTrigger
        server.sendPackets = doSendPackets

        clear_all_messages()

        self.assertEquals(server.exception, None)

        server._handleConnection("test12 dummy packets")

        self.assertEquals(get_messages(), ['ping: renew Mr.Fakey/-1'])
        self.assertEquals(pt, server._ping_timer)
        self.assertEquals(pt.resetValues, [ 10 ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(avatar.handlePacketCount, 1)
        self.assertEquals(server._blocked, True)
        self.assertEquals(sendPacketsCount, 1)
        self.assertEquals(triggerCount, 0)  # should be 0 since unblock() isn't called 
        self.assertEquals(server.exception, None)
        self.assertEquals(server.transport.loseConnectionCount, 0)
    # -----------------------------------------------------------------------
    def test13_handleConnectionWithExceptionRaised(self):
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')

        pt = MockPingTimer()
        pt.isActive = True
        server._ping_timer = pt

        class  MockRaise:
            def __init__(raiseSelf, str):
                raiseSelf.value = str
        class MockAvatar:
            def __init__(avatarSelf, expected = None):
                avatarSelf.handlePacketCount = 0
                avatarSelf.expectedPacket = expected
            def handlePacket(avatarSelf, packet):
                global triggerCount
                global sendPacketsCount
                avatarSelf.handlePacketCount += 1
                self.assertEquals(packet, avatarSelf.expectedPacket)
                self.assertEquals(pt, server._ping_timer)
                self.assertEquals(pt.resetValues, [ 10 ])
                self.assertEquals(pt.cancelCount, 0)
                self.assertEquals(server._blocked, True)
                self.assertEquals(triggerCount, 0)
                raise MockRaise("handlePacketsRaise")
                return "handlePacketsReturn"

        avatar = MockAvatar("test13 dummy packets")

        global triggerCount
        triggerCount = 0
        def doMyTrigger():
            global triggerCount
            triggerCount += 1
        def doSendPackets(packets):
            self.failIf(True)  # This should never be called

        server.avatar = avatar
        server._blocked = False

        server.triggerTimer = doMyTrigger
        server.sendPackets = doSendPackets

        clear_all_messages()

        self.assertEquals(server.exception, None)

        server._handleConnection("test13 dummy packets")

        self.assertEquals(get_messages(), ['ping: renew Mr.Fakey/-1'])
        self.assertEquals(pt, server._ping_timer)
        self.assertEquals(pt.resetValues, [ 10 ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(avatar.handlePacketCount, 1)
        self.assertEquals(server._blocked, False)
        self.assertEquals(triggerCount, 1)
        self.assertEquals(len(server.exception), 3)
        self.assertEquals(server.exception[0], MockRaise)
        self.failUnless(isinstance(server.exception[1], MockRaise))
        self.assertEquals(server.exception[1].value, 'handlePacketsRaise')
        self.assertEquals(server.transport.loseConnectionCount, 1)
    # -----------------------------------------------------------------------
    def test14_handleConnectionWithExceptionRaisedNotSet(self):
        self.server_factory = FakeFactory(self)
        server = self.server_factory.buildProtocol('addr')

        pt = MockPingTimer()
        pt.isActive = True
        server._ping_timer = pt

        class  MockRaise:
            def __init__(raiseSelf, str):
                raiseSelf.value = str
                del server.exception
        class MockAvatar:
            def __init__(avatarSelf, expected = None):
                avatarSelf.handlePacketCount = 0
                avatarSelf.expectedPacket = expected
            def handlePacket(avatarSelf, packet):
                global triggerCount
                global sendPacketsCount
                avatarSelf.handlePacketCount += 1
                self.assertEquals(packet, avatarSelf.expectedPacket)
                self.assertEquals(pt, server._ping_timer)
                self.assertEquals(pt.resetValues, [ 10 ])
                self.assertEquals(pt.cancelCount, 0)
                self.assertEquals(server._blocked, True)
                self.assertEquals(triggerCount, 0)
                raise MockRaise("handlePacketsRaise")
                return "handlePacketsReturn"

        avatar = MockAvatar("test14 dummy packets")

        global triggerCount
        triggerCount = 0
        def doMyTrigger():
            global triggerCount
            triggerCount += 1
        def doSendPackets(packets):
            self.failIf(True)  # This should never be called

        server.avatar = avatar
        server._blocked = False

        server.triggerTimer = doMyTrigger
        server.sendPackets = doSendPackets

        clear_all_messages()

        self.assertEquals(server.exception, None)

        exceptionFound = False
        try:
            server._handleConnection("test14 dummy packets")
            self.failIf(True)  # This line should not be reached.
        except MockRaise, mr:
            exceptionFound = True
            self.failUnless(isinstance(mr, MockRaise))
            self.assertEquals(mr.value, 'handlePacketsRaise')

        self.assertEquals(exceptionFound, True)
            
        self.assertEquals(get_messages(), ['ping: renew Mr.Fakey/-1'])
        self.assertEquals(pt, server._ping_timer)
        self.assertEquals(pt.resetValues, [ 10 ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(avatar.handlePacketCount, 1)
        self.assertEquals(server._blocked, False)
        self.assertEquals(triggerCount, 1)
        self.assertEquals(server.transport.loseConnectionCount, 0)
#-------------------------------------------------------------------------------
# DummyClientTests are to cover code on the server that doesn't need a
# client running to test it.

class DummyClientTests(unittest.TestCase):
    # -----------------------------------------------------------------------
    def test01_pingWithoutTimer(self):
        def myDataWrite(clientSelf): failIf(True)
        clear_all_messages()

        client = pokernetwork.client.UGAMEClientProtocol()
        client.dataWrite = myDataWrite
        del client._ping_timer
        client.factory = None

        self.assertEquals(client.ping(), None)
        self.assertEqual(get_messages(), [])
    # -----------------------------------------------------------------------
    def test02_pingWithNoneTimer(self):
        def myDataWrite(clientSelf): failIf(True)
        clear_all_messages()

        client = pokernetwork.client.UGAMEClientProtocol()
        client.dataWrite = myDataWrite
        client._ping_timer = None
        client.factory = None

        self.assertEquals(client.ping(), None)
        self.assertEqual(get_messages(), [])
    # -----------------------------------------------------------------------
    def test03_pingWithActiveTimer(self):
        def myDataWrite(clientSelf): failIf(True)
        clear_all_messages()

        client = pokernetwork.client.UGAMEClientProtocol()
        pt = MockPingTimer()
        pt.isActive = True
        client._ping_timer = pt
        client.factory = None

        self.assertEquals(client.ping(), None)
        self.assertEquals(pt, client._ping_timer)
        self.assertEquals(pt.resetValues, [ 5 ])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEqual(get_messages(), [])
    # -----------------------------------------------------------------------
    def test04_pingWithInactiveTimer(self):
        global dataWritten
        dataWritten = 0
        def myDataWrite(packet):
            global dataWritten
            self.assertEquals(packet, PacketPing().pack())
            dataWritten += 1

        class DummyFactory:
            def __init__(factSelf):
                factSelf.verbose = 7

        clear_all_messages()

        client = pokernetwork.client.UGAMEClientProtocol()
        pt = MockPingTimer()
        pt.isActive = False
        client._ping_timer = pt
        client.factory = DummyFactory()
        client.dataWrite = myDataWrite
        client._prefix = "BLAH "

        # Reactor failure should occur if this never gets called.  We
        # replace the real object's ping with pingDummy and call using the
        # static method so that new reactor setup works properly.
        pingRecallDeferred = defer.Deferred()
        def pingDummy():
            pingRecallDeferred.callback(True)

        client.ping = pingDummy
        self.assertEquals(pokernetwork.client.UGAMEClientProtocol.ping(client), None)
        self.failUnless(isinstance(client._ping_timer, twisted.internet.base.DelayedCall))
        self.failUnless(client._ping_timer.__str__().find('pingDummy()') > 0)

        self.assertEquals(pt.resetValues, [])
        self.assertEquals(pt.cancelCount, 0)
        self.assertEquals(dataWritten, 1)
        self.assertEqual(get_messages(), ['BLAH send ping'])

        return pingRecallDeferred
    # -----------------------------------------------------------------------
    def test05_getSerial(self):
        class  MockUser:
            def __init__(userSelf):
                userSelf.serial = 5
        client = pokernetwork.client.UGAMEClientProtocol()
        client.user = MockUser()
        self.assertEquals(client.getSerial(), 5)
    # -----------------------------------------------------------------------
    def test06_getName(self):
        class  MockUser:
            def __init__(userSelf):
                userSelf.name = "joe"
        client = pokernetwork.client.UGAMEClientProtocol()
        client.user = MockUser()
        self.assertEquals(client.getName(), "joe")
    # -----------------------------------------------------------------------
    def test07_getURL(self):
        class  MockUser:
            def __init__(userSelf):
                userSelf.url = "http://example.org"
        client = pokernetwork.client.UGAMEClientProtocol()
        client.user = MockUser()
        self.assertEquals(client.getUrl(), "http://example.org")
    # -----------------------------------------------------------------------
    def test08_getOutfit(self):
        class  MockUser:
            def __init__(userSelf):
                userSelf.outfit = "naked"
        client = pokernetwork.client.UGAMEClientProtocol()
        client.user = MockUser()
        self.assertEquals(client.getOutfit(), "naked")
    # -----------------------------------------------------------------------
    def test09_isLogged(self):
        class  MockUser:
            def isLogged(userself): return True
        client = pokernetwork.client.UGAMEClientProtocol()
        client.user = MockUser()
        self.assertEquals(client.isLogged(), True)
    # -----------------------------------------------------------------------
    def test10_factoryError(self):
        clear_all_messages()
        clientFactory = pokernetwork.client.UGAMEClientFactory()
        clientFactory.error("test10")
        self.assertEquals(get_messages(), [ "ERROR test10"])
# -----------------------------------------------------------------------------------------------------
def Run():
    silence_all_messages()
    loader = runner.TestLoader()
#    loader.methodPrefix = "test09"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(ClientServer))
    suite.addTest(loader.loadClass(ClientServerBadClientProtocol))
    suite.addTest(loader.loadClass(ClientServerQueuedServerPackets))
    suite.addTest(loader.loadClass(ClientServerDeferredServerPackets))
    suite.addTest(loader.loadClass(DummyServerTests))
    suite.addTest(loader.loadClass(DummyClientTests))
    return runner.TrialRunner(reporter.VerboseTextReporter,
#                              tracebackFormat='verbose',
                              tracebackFormat='default',
                              ).run(suite)

# -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-clientserver.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/server.py ../pokernetwork/client.py' TESTS='coverage-reset test-clientserver.py coverage-report' check )"
# End:
