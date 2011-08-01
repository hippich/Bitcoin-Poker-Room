#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2009 Johan Euphrosine <proppy@aminche.com>
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

from twisted.trial import unittest, runner, reporter
from twisted.internet import defer, reactor
from twisted.internet import defer
from twisted.python.util import InsensitiveDict

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from tests import testclock

from pokernetwork import  pokerrestclient
from pokernetwork import pokerservice
from pokernetwork import pokernetworkconfig
from pokernetwork import pokermemcache
from pokernetwork import pokersite
from pokernetwork.pokerpackets import *

settings_xml_server = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" simultaneous="4" chat="yes" >
  <delays autodeal="20" round="0" position="0" showdown="0" autodeal_max="1" finish="0" messages="60" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19481" />
  <resthost host="127.0.0.1" port="19481" path="/POKER_REST" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

class PokerRestClientTestCase(unittest.TestCase):
      def destroyDb(self, arg = None):
            if len("") > 0:
                  os.system("/usr/bin/mysql -u root --password='' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
            else:
                  os.system("/usr/bin/mysql -u root -e 'DROP DATABASE IF EXISTS pokernetworktest'")
      # --------------------------------------------------------------
      def initServer(self):
            settings = pokernetworkconfig.Config([])
            settings.loadFromString(settings_xml_server)
            self.server_service = pokerservice.PokerService(settings)
            self.server_service.disconnectAll = lambda: True
            self.server_service.startService()
            self.server_site = pokersite.PokerSite(settings, pokerservice.PokerRestTree(self.server_service))
            self.server_port = reactor.listenTCP(19481, self.server_site, interface="127.0.0.1")
      # --------------------------------------------------------------
      def setUp(self):
            testclock._seconds_reset()
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            pokermemcache.memcache_singleton = {}
            self.destroyDb()
            self.initServer()
      # --------------------------------------------------------------
      def tearDownServer(self):
            self.server_site.stopFactory()
            d = self.server_service.stopService()
            d.addCallback(lambda x: self.server_port.stopListening())
            return d
      # --------------------------------------------------------------
      def tearDown(self):
            d = self.tearDownServer()
            d.addCallback(self.destroyDb)
            d.addCallback(lambda x: reactor.disconnectAll())
            return d
      # --------------------------------------------------------------
      def test01_longPoll(self):
            def longPollCallback(packets):
                  self.assertEquals(PACKET_PING, packets[0].type)
            client = pokerrestclient.PokerRestClient('127.0.0.1', 19481, '/POKER_REST?explain=no', longPollCallback, verbose=6)
            def sendPacketData(data):
                  self.assertSubstring('LongPoll', data)
                  return '[ { "type": "PacketPing" } ]'
            client.sendPacketData = sendPacketData
            self.assertNotEquals(None, client.timer)
            client.longPoll()
            self.assertEquals(True, client.pendingLongPoll)
            self.assertEquals(None, client.timer)
            return client.queue
      # --------------------------------------------------------------
      def test02_longPollReturn(self):
            packets = []
            client = pokerrestclient.PokerRestClient('127.0.0.1', 19481, '/POKER_REST?explain=no', lambda packets: None, verbose=6)
            def sendPacketData(data):
                  packets.append(data)
                  return "[]"
            client.sendPacketData = sendPacketData
            client.longPoll()
            d = client.sendPacket(PacketPokerTableSelect(), '{"type": "PacketPokerTableSelect"}')
            d.addCallback(lambda arg: self.assertSubstring('LongPollReturn', packets[1]))
            d.addCallback(lambda arg: self.assertNotEquals(None, client.timer))
            return client.queue
      # --------------------------------------------------------------
      def test03_longPollSchedule(self):
            client = pokerrestclient.PokerRestClient('127.0.0.1', 19481, '/POKER_REST?explain=no', lambda packets: None, verbose=6)
            client.sendPacketData = lambda data: "[]"
            client.longPoll()
            client.longPoll()
            self.assertNotEquals(None, client.timer)
            client.clearTimeout()
            return client.queue
      # --------------------------------------------------------------
      def test04_sendPacketData(self):
            client = pokerrestclient.PokerRestClient('127.0.0.1', 19481, '/POKER_REST?explain=no', None, verbose=6)
            d = client.sendPacketData('{"type": "PacketPokerTableSelect"}')
            d.addCallback(lambda data: self.assertSubstring('PacketPokerTableList', data))
            return d
      # --------------------------------------------------------------
      def test05_sendPacket(self):
            client = pokerrestclient.PokerRestClient('127.0.0.1', 19481, '/POKER_REST?explain=no', None, verbose=6)
            d = client.sendPacket(PacketPokerTableSelect(), '{"type": "PacketPokerTableSelect"}')
            d.addCallback(lambda packets: self.assertEquals(PACKET_POKER_TABLE_LIST, packets[0].type))
            return d
      # --------------------------------------------------------------
      def test06_404(self):
            client = pokerrestclient.PokerRestClient('127.0.0.1', 19481, '/POKER_REST2', None, verbose=6)
            d = client.sendPacket(PacketPokerTableSelect(), '{"type": "PacketPokerTableSelect"}')
            d.addCallback(lambda packets: self.assertEquals(PACKET_ERROR, packets[0].type))
            return d
      # --------------------------------------------------------------
      def test07_connectionFailed(self):
            client = pokerrestclient.PokerRestClient('127.0.0.1', 20000, '/POKER_REST?explain=no', None, verbose=6)
            d = client.sendPacket(PacketPokerTableSelect(), '{"type": "PacketPokerTableSelect"}')
            d.addCallback(lambda packets: self.assertEquals(PACKET_ERROR, packets[0].type))
            return d
      def test08_noCallback(self):
            client = pokerrestclient.PokerRestClient('127.0.0.1', 20000, '/POKER_REST?explain=no', None, verbose=6)
            self.assertEquals(-1, client.longPollFrequency)
            self.assertEquals(None, client.timer)

class MockRequest:
      def finish(self): pass
      def setResponseCode(self, arg1, arg2): pass
      def handlerHeader(self, arg1, arg2): pass
      def setHeader(self, arg1, arg2): pass
      def write(self, arg1): pass

class MockReason():
      def check(self, reason): return False

class PokerProxyClientFactoryTestCase(unittest.TestCase):
      def destroyDb(self, arg = None):
            if len("") > 0:
                  os.system("/usr/bin/mysql -u root --password='' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
            else:
                  os.system("/usr/bin/mysql -u root -e 'DROP DATABASE IF EXISTS pokernetworktest'")
      # --------------------------------------------------------------
      def initServer(self):
            settings = pokernetworkconfig.Config([])
            settings.loadFromString(settings_xml_server)
            self.server_service = pokerservice.PokerService(settings)
            self.server_service.disconnectAll = lambda: True
            self.server_service.startService()
            self.server_site = pokersite.PokerSite(settings, pokerservice.PokerRestTree(self.server_service))
            self.server_port = reactor.listenTCP(19481, self.server_site, interface="127.0.0.1")
      # --------------------------------------------------------------
      def setUp(self):
            testclock._seconds_reset()
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            pokermemcache.memcache_singleton = {}
            self.destroyDb()
            self.initServer()
      # --------------------------------------------------------------
      def tearDownServer(self):
            self.server_site.stopFactory()
            d = self.server_service.stopService()
            d.addCallback(lambda x: self.server_port.stopListening())
            return d
      # --------------------------------------------------------------
      def tearDown(self):
            d = self.tearDownServer()
            d.addCallback(self.destroyDb)
            d.addCallback(lambda x: reactor.disconnectAll())
            return d
      # --------------------------------------------------------------
      def test01_proxy(self):
            data = '{"type": "PacketPing"}'
            headers = InsensitiveDict()
            headers.setdefault('Content-Length', len(data))
            headers.setdefault("connection", "close")
            headers.setdefault("proxy-connection", "foo")
            host = '127.0.0.1'
            port = 19481
            path = '/POKER_REST'
            factory = pokerrestclient.PokerProxyClientFactory('POST', path, '1.1', headers, data, MockRequest(), 6, host + ':' + str(port) + path)
            reactor.connectTCP(host, port, factory)
            factory.deferred.addCallback(self.assertNotEquals, None)
            return factory.deferred
      # --------------------------------------------------------------
      def test02_proxy_failed(self):
            factory = pokerrestclient.PokerProxyClientFactory("command", "rest", "version", "headers", "data", "father",
                                                              "verbose", "destination")
            def errback(reason):
                  self.assertNotEquals(None, reason)
            factory.deferred.addErrback(errback)
            factory.clientConnectionFailed(None, MockReason())
            return factory.deferred
      # --------------------------------------------------------------
      def test03_proxy_lost(self):
            factory = pokerrestclient.PokerProxyClientFactory("command", "rest", "version", "headers", "data", "father",
                                                              "verbose", "destination")
            def errback(reason):
                  self.assertNotEquals(None, reason)
            factory.deferred.addErrback(errback)
            factory.clientConnectionLost(None, MockReason())
            return factory.deferred

def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test05"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerRestClientTestCase))
    suite.addTest(loader.loadClass(PokerProxyClientFactoryTestCase))
    return runner.TrialRunner(
        reporter.VerboseTextReporter,
        tracebackFormat='default',
        ).run(suite)

if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokerrestclient.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerrestclient.py' VERBOSE_T=-1 TESTS='coverage-reset test-pokerrestclient.py coverage-report' check )"
# End:
