#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2008, 2009 Loic Dachary    <loic@dachary.org>
# Copyright (C) 2009 Bradley M. Kuhn <bkuhn@ebb.org>
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

import simplejson

from twisted.trial import unittest, runner, reporter
from twisted.internet import defer, reactor
from twisted.application import internet
from twisted.python import failure
from twisted.python.runtime import seconds
import twisted.internet.base
twisted.internet.base.DelayedCall.debug = True

from twisted.web import client, http

from tests import testmessages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: testmessages.silence_all_messages()

from tests import testclock

from pokernetwork import pokermemcache
from pokernetwork import pokersite
from pokernetwork import pokernetworkconfig
from pokernetwork import pokerservice
from pokernetwork import proxyfilter
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

settings_xml_proxy = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" simultaneous="4" chat="yes" >
  <delays autodeal="20" round="0" position="0" showdown="0" autodeal_max="1" finish="0" messages="60" />

  <listen tcp="19480" />

  <rest_filter>.././../pokernetwork/proxyfilter.py</rest_filter>

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}
class ProxyTestCase(unittest.TestCase):
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
      def initProxy(self):
            settings = pokernetworkconfig.Config([])
            settings.loadFromString(settings_xml_proxy)
            self.proxy_service = pokerservice.PokerService(settings)
            self.proxy_service.disconnectAll = lambda: True
            self.proxy_service.startService()
            self.proxy_site = pokersite.PokerSite(settings, pokerservice.PokerRestTree(self.proxy_service))
            self.proxy_port = reactor.listenTCP(19480, self.proxy_site, interface="127.0.0.1")
      # --------------------------------------------------------------
      def setUp(self):
            testclock._seconds_reset()
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            pokermemcache.memcache_singleton = {}
            self.destroyDb()
            self.initServer()
            self.initProxy()
      # --------------------------------------------------------------
      def tearDownServer(self):
            self.server_site.stopFactory()
            d = self.server_service.stopService()
            d.addCallback(lambda x: self.server_port.stopListening())
            return d
      # --------------------------------------------------------------
      def tearDownProxy(self):
            self.proxy_site.stopFactory()
            d = self.proxy_service.stopService()
            d.addCallback(lambda x: self.proxy_port.stopListening())
            return d
      # --------------------------------------------------------------
      def tearDown(self):
            d = defer.DeferredList((
                  self.tearDownServer(),
                  self.tearDownProxy()
                  ))
            d.addCallback(self.destroyDb)
            d.addCallback(lambda x: reactor.disconnectAll())
            return d
      # --------------------------------------------------------------
      def test01_ping_proxy(self):
            """
            Ping to the proxy.
            """
            d = client.getPage("http://127.0.0.1:19480/POKER_REST",
                               postdata = '{"type": "PacketPing"}')
            def checkPing(result):
                  self.assertEqual('[]', str(result))
            d.addCallback(checkPing)
            return d
      # --------------------------------------------------------------
      def test02_ping_server(self):
            """
            Ping to the server.
            """
            d = client.getPage("http://127.0.0.1:19481/POKER_REST",
                               postdata = '{"type": "PacketPing"}')
            def checkPing(result):
                  self.assertEqual('[]', str(result))
            d.addCallback(checkPing)
            return d
      # --------------------------------------------------------------
      def test03_listTables(self):
            """
            Select all tables. The list obtained from the proxy contains the tables
            created by the server.
            """
            d = client.getPage("http://127.0.0.1:19480/POKER_REST",
                               postdata = '{"type":"PacketPokerTableSelect"}')
            def checkTables(result):
                  packets = simplejson.JSONDecoder().decode(result)
                  self.assertEqual('PacketPokerTableList', packets[0]['type'])
                  tables = packets[0]['packets']
                  self.assertEqual('Table1', tables[0]['name'])
            d.addCallback(checkTables)
            return d
      # --------------------------------------------------------------
      def test04_tableJoin(self):
            """
            Join a table thru a proxy.
            """
            d = client.getPage("http://127.0.0.1:19480/POKER_REST",
                               postdata = '{"type":"PacketPokerTableJoin","game_id":1}')
            def checkTable(result):
                  packets = simplejson.JSONDecoder().decode(result)
                  self.assertEqual('PacketPokerTable', packets[0]['type'])
                  self.assertEqual('Table1', packets[0]['name'])
            d.addCallback(checkTable)
            return d
      # --------------------------------------------------------------
      def test05_connectionrefused(self):
            """
            Create a route that leads to a non-existent server.
            """
            db = self.proxy_service.db
            db.db.query("INSERT INTO route VALUES (6, 0, 0, 60)")
            db.db.query("INSERT INTO resthost VALUES (60, 'fake', '127.0.0.1', 6666, '/fail')")
            d = client.getPage("http://127.0.0.1:19480/POKER_REST",
                               postdata = '{"type":"PacketPokerTableJoin","game_id":6}')
            def checkTable(result):
                  self.assertSubstring('Connection was refused by other side', result.value.response)
            d.addBoth(checkTable)
            return d
      # --------------------------------------------------------------
      def test06_tableSeat_auth(self):
            """
            Join a table thru a proxy, using an authenticated session
            """
            info = self.server_service.auth('user1', 'password1', PacketPokerRoles.PLAY)
            serial = info[0][0]
            self.proxy_site.memcache.set('auth', str(serial))
            #
            # Join table
            #
            d = client.getPage("http://127.0.0.1:19480/POKER_REST?uid=uid&auth=auth",
                               postdata = '{"type":"PacketPokerTableJoin","game_id":1,"serial":' + str(serial) + '}')
            def checkTable(result):
                  packets = simplejson.JSONDecoder().decode(result)
                  self.assertEqual('PacketPokerTable', packets[0]['type'])
                  self.assertEqual('Table1', packets[0]['name'])
                  return result
            d.addCallback(checkTable)
            #
            # Get a seat
            #
            def seat(result):
                  d1 = client.getPage("http://127.0.0.1:19480/POKER_REST?uid=uid&auth=auth",
                                     postdata = '{"type":"PacketPokerSeat","game_id":1,"serial":' + str(serial) + '}')
                  def checkSeat(result):
                        self.assertSubstring('PlayerArrive', result)
                        return True
                  d1.addCallback(checkSeat)
                  return d1
            d.addCallback(seat)
            return d
      # --------------------------------------------------------------
      def test07_tourneyRegister(self):
            """
            Register to a tourney thru a proxy, using an authenticated session
            """
            #
            # Create tourney
            #
            db = self.server_service.db
            cursor = db.cursor()
            cursor.execute("INSERT INTO tourneys_schedule (resthost_serial, active, start_time) VALUES (%s, 'y', %s)", ( self.server_service.resthost_serial, seconds() + 36000))
            schedule_serial = cursor.lastrowid
            self.server_service.updateTourneysSchedule()
            cursor.execute("SELECT serial FROM tourneys WHERE schedule_serial = %s", schedule_serial)
            tourney_serial = cursor.fetchone()[0]
            cursor.close()
            self.assertEqual(True, self.server_service.tourneys.has_key(tourney_serial))
            #
            # Create user
            #

            info = self.server_service.auth('user1', 'password1', PacketPokerRoles.PLAY)
            serial = info[0][0]
            self.proxy_site.memcache.set('auth', str(serial))
            #
            # Register tourney
            #
            d = client.getPage("http://127.0.0.1:19480/POKER_REST?uid=uid&auth=auth",
                               postdata = '{"type":"PacketPokerTourneyRegister","game_id":' + str(tourney_serial) + ',"serial":' + str(serial) + '}')
            def checkTable(result):
                  packets = simplejson.JSONDecoder().decode(result)
                  self.assertEqual('PacketPokerTourneyRegister', packets[0]['type'])
                  self.assertEqual(tourney_serial, packets[0]['game_id'])
                  return result
            d.addCallback(checkTable)
            return d
      # --------------------------------------------------------------
      def test08_tableSeat_relogin(self):
            """
            Join a table thru a proxy, using an anonymous session that becomes an
            authenticated session
            """
            self.proxy_site.memcache.set('auth', '0')
            #
            # Join table
            #
            d = client.getPage("http://127.0.0.1:19480/POKER_REST?uid=uid&auth=auth",
                               postdata = '{"type":"PacketPokerTableJoin","game_id":1}')
            def checkTable(result):
                  packets = simplejson.JSONDecoder().decode(result)
                  self.assertEqual('PacketPokerTable', packets[0]['type'])
                  self.assertEqual('Table1', packets[0]['name'])
                  return result
            d.addCallback(checkTable)
            #
            # Login
            #
            def login(result):
                  d3 = client.getPage("http://127.0.0.1:19480/POKER_REST?uid=uid&auth=auth",
                                     postdata = '{"type":"PacketLogin","user":"user1","password":"password"}')
                  def checkLogin(result):
                        global serial
                        packets = simplejson.JSONDecoder().decode(result)
                        serial = packets[1]['serial']
                        return True
                  d3.addCallback(checkLogin)
                  return d3
            d.addCallback(login)
            #
            # Get a seat
            #
            def seat(result):
                  global serial
                  d1 = client.getPage("http://127.0.0.1:19480/POKER_REST?uid=uid&auth=auth",
                                     postdata = '{"type":"PacketPokerSeat","game_id":1,"serial":' + str(serial) + '}')
                  def checkSeat(result):
                        self.assertSubstring('PlayerArrive', result)
                        return True
                  d1.addCallback(checkSeat)
                  return d1
            d.addCallback(seat)
            return d
      # --------------------------------------------------------------
      def test09_pokerPoll(self):
            """
            """
            d = client.getPage("http://127.0.0.1:19480/POKER_REST",
                               postdata = '{"type":"PacketPokerPoll","game_id":1}')
            def checkTable(result):
                  packets = simplejson.JSONDecoder().decode(result)
                  self.assertEqual(0, len(packets))
            d.addCallback(checkTable)
            return d
      # --------------------------------------------------------------
      def test10_error500(self):
            """
            """
            def error500(game_id):
                  raise UserWarning, "%d fail" % game_id
            self.server_service.getTable = error500
            d = client.getPage("http://127.0.0.1:19480/POKER_REST",
                               postdata = '{"type":"PacketPokerTableJoin","game_id":1}')
            def checkError(result):
                  self.assertSubstring('500', str(result))
                  return True
            d.addErrback(checkError)
            return d
################################################################################
class ProxyFilterTestCase(unittest.TestCase):
      # --------------------------------------------------------------
      def test01_rest_filter_finished_request(self):
            """
            proxyfilter.rest_filter should ignore finished request
            """
            class Transport:
                  def write(self, data):
                        pass
            class Channel:
                  transport = Transport()
                  def requestDone(self, request):
                        pass
            class Service:
                  verbose = 6
                  def packet2resthost(self, packet):
                        return (None, None, None)
            class Resource:
                  service = Service()
            class Site:
                  resource = Resource()
            class Packet:
                  pass
            r = pokersite.Request(Channel(), True)
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.setResponseCode(http.OK)
            r.write("FINISHED")
            r.finish()
            r.noLongerQueued()
            proxyfilter.rest_filter(Site(), r, Packet())
      # --------------------------------------------------------------
      def test02_forceInitCoverHeaderReplace(self):
            from pokernetwork.proxyfilter import ProxyClient

            pc = ProxyClient("COMMAND", "REST", "VERSION",
                             { 'proxy-connection' : 'ThisWillBeGone',
                               'cookie' : 'ThisWillStay'}, "DATA", "FATHER")
            self.assertEquals(pc.father, "FATHER")
            self.assertEquals(pc.command, "COMMAND")
            self.assertEquals(pc.rest, "REST")
            self.assertEquals(pc.headers, {'cookie' : 'ThisWillStay',
                                           'connection' : 'close'})
            self.assertEquals(pc.data, "DATA")
      # --------------------------------------------------------------
      def test03_checkbadReason(self):
            class MockReason():
                  def check(mrS, reason): return False
            class MockDeferred():
                  def __init__(mdS):
                        mdS.errbackCount = 0
                        mdS.called = False
                  def errback(mdS, reason):
                        mdS.errbackCount += 1
                        self.failUnless(isinstance(reason, MockReason))

            from pokernetwork.proxyfilter import ProxyClientFactory

            pcf = ProxyClientFactory("command", "rest", "version", "headers", "data", "father",
                                     "verbose", "destination")

            pcf.deferred = MockDeferred()
            pcf.clientConnectionLost(None, MockReason())

            self.assertEquals(pcf.deferred.errbackCount, 1)
################################################################################
def Run():
      loader = runner.TestLoader()
#      loader.methodPrefix = "test06"
      suite = loader.suiteFactory()
      suite.addTest(loader.loadClass(ProxyTestCase))
      suite.addTest(loader.loadClass(ProxyFilterTestCase))
      return runner.TrialRunner(
            reporter.VerboseTextReporter,
            tracebackFormat='default',
#            logfile = '-',
            ).run(suite)

if __name__ == '__main__':
      if Run().wasSuccessful():
            sys.exit(0)
      else:
            sys.exit(1)
################################################################################
# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-proxyfilter.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/proxyfilter.py' VERBOSE_T=-1 TESTS='coverage-reset test-proxyfilter.py coverage-report' check )"
# End:
