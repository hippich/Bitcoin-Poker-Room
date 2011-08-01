#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
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

from twisted.internet import selectreactor, main
class MyReactor(selectreactor.SelectReactor):
      def runUntilCurrent(self):
            self._cancellations = 20000000
            selectreactor.SelectReactor.runUntilCurrent(self)
main.installReactor(MyReactor())
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

class LeakTestCase(unittest.TestCase):

      def destroyDb(self, arg = None):
            if len("") > 0:
                  os.system("/usr/bin/mysql -u root --password='' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
            else:
                  os.system("/usr/bin/mysql -u root -e 'DROP DATABASE IF EXISTS pokernetworktest'")

      def initServer(self):
            settings = pokernetworkconfig.Config([])
            settings.loadFromString(settings_xml_server)
            self.server_service = pokerservice.PokerService(settings)
            self.server_service.disconnectAll = lambda: True
            self.server_service.startService()
            self.server_site = pokersite.PokerSite(settings, pokerservice.PokerRestTree(self.server_service))
            self.server_port = reactor.listenTCP(19481, self.server_site, interface="127.0.0.1")

      def setUp(self):
            testclock._seconds_reset()
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            pokermemcache.memcache_singleton.clear()
            pokermemcache.memcache_expiration_singleton.clear()
            self.destroyDb()
            self.initServer()

      def tearDownServer(self):
            self.server_site.stopFactory()
            d = self.server_service.stopService()
            d.addCallback(lambda x: self.server_port.stopListening())
            return d

      def tearDown(self):
            d = self.tearDownServer()
            d.addCallback(self.destroyDb)
            d.addCallback(lambda x: reactor.disconnectAll())
            return d

      def test00(self):
            pass

      def test01_ping(self):
            """
            """
            def f(ignored):
                  d = client.getPage("http://127.0.0.1:19481/POKER_REST", postdata = '{"type":"PacketPing"}')
                  def cleanMemcache(x):
                        pokermemcache.memcache_singleton.clear()
                        pokermemcache.memcache_expiration_singleton.clear()
                  d.addCallback(cleanMemcache)
                  d.addCallback(f)
            f(None)
            d = defer.Deferred()
            return d
      test01_ping.timeout = pow(2, 30)

      def test02_joinTable(self):
            """
            """
            def f(ignored, i):
                  serial = 0
                  session = 'session' + str(i)
                  self.server_site.memcache.set(session, str(serial))
                  headers = { 'Cookie': 'TWISTED_SESSION='+session }
                  d = client.getPage("http://127.0.0.1:19481/POKER_REST", postdata = '{"type":"PacketPokerTableJoin","game_id":1}', headers = headers)
                  d.addCallback(lambda x: client.getPage("http://127.0.0.1:19481/POKER_REST", postdata = '{"type":"PacketPokerTableQuit","game_id":1}', headers = headers))
                  def cleanMemcache(x):
                        pokermemcache.memcache_singleton.clear()
                        pokermemcache.memcache_expiration_singleton.clear()
                  d.addCallback(cleanMemcache)
                  d.addCallback(f, i+1)
            i = 1
            f(None, i)
            d = defer.Deferred()
            return d
      test02_joinTable.timeout = pow(2, 30)

      def test03_joinTable_guppy(self):
            import guppy, gc
            hpy = guppy.hpy()
            def f(ignored, last, first, i):
                  gc.collect()
                  next = hpy.heap()
                  print 'SINCE LAST TIME'
                  print next - last
                  print 'SINCE FOREVER'
                  print last - first
                  serial = 0
                  session = 'session' + str(i)
                  self.server_site.memcache.set(session, str(serial))
                  headers = { 'Cookie': 'TWISTED_SESSION='+session }
                  d = client.getPage("http://127.0.0.1:19481/POKER_REST", postdata = '{"type":"PacketPokerTableJoin","game_id":1}', headers = headers)
                  d.addCallback(lambda x: client.getPage("http://127.0.0.1:19481/POKER_REST", postdata = '{"type":"PacketPokerTableQuit","game_id":1}', headers = headers))
                  def cleanMemcache(x):
                        pokermemcache.memcache_singleton.clear()
                        pokermemcache.memcache_expiration_singleton.clear()
                  d.addCallback(cleanMemcache)
                  d.addCallback(f, next, first, i+1)
            first = hpy.heap()
            i = 1
            f(None, first, first, i)
            d = defer.Deferred()
            return d
      test03_joinTable_guppy.timeout = pow(2, 30)

def Run():
      loader = runner.TestLoader()
      loader.methodPrefix = "test03"
      suite = loader.suiteFactory()
      suite.addTest(loader.loadClass(LeakTestCase))
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

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-leak.py ) ; ( cd ../tests ; make VERBOSE_T=-2 TESTS='test-leak.py' check )"
# End:
