#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2006 Mekensleep <licensing@mekensleep.com>
#                    24 rue vieille du temple, 75004 Paris
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
import urllib
import libxml2
from types import ListType

from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor, defer

#
# Must be done before importing pokerclient or pokerclient
# will have to be patched too.
#
from tests import testclock
twisted.internet.base.DelayedCall.debug = True

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from pokernetwork import pokerservice, pokernetworkconfig, user
from pokernetwork import currencyclient
from pokernetwork import pokersite
currencyclient.CurrencyClient = currencyclient.FakeCurrencyClient
from pokernetwork.pokerclientpackets import *

from twisted.web import xmlrpc

settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19480" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

from twisted.web import xmlrpc, server, client, http, resource

from tests import testlock

#
# Override QueryProtocol from xmlrpc because it lacks
# the Cookie header.
#
class QueryProtocol(http.HTTPClient):

    def connectionMade(self):
	if hasattr(self.factory, "path"): # twisted-2.4 / 2.5
            self.sendCommand('POST', self.factory.path)
	elif hasattr(self.factory, "url"): # twisted-2.2
            self.sendCommand('POST', self.factory.url)
        self.sendHeader('User-Agent', 'Twisted/XMLRPClib')
        self.sendHeader('Host', self.factory.host)
        if self.factory.cookie:
            self.sendHeader('Cookie', self.factory.cookie)
        self.sendHeader('Content-type', 'text/xml')
        self.sendHeader('Content-length', str(len(self.factory.payload)))
	if hasattr(self.factory, "user") and self.factory.user:
            auth = '%s:%s' % (self.factory.user, self.factory.password)
            auth = auth.encode('base64').strip()
            self.sendHeader('Authorization', 'Basic %s' % (auth,))
        self.endHeaders()
        self.transport.write(self.factory.payload)

    def handleStatus(self, version, status, message):
        if status != '200':
            self.factory.badStatus(status, message)

    def handleResponse(self, contents):
        self.factory.parseResponse(contents)


class PokerServiceTestCase(unittest.TestCase):

    def destroyDb(self, arg = None):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    # -----------------------------------------------------------------------------------------------------
    def setUp(self):
        self.destroyDb()
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.service = pokerservice.PokerService(settings)
        if verbose >=0: self.service.verbose = verbose
        site = server.Site(resource.IResource(self.service))
        self.p = reactor.listenTCP(0, site,
                                   interface="127.0.0.1")
        self.port = self.p.getHost().port
        self.cookie = None

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

    def tearDown(self):
        self.cookie = None
        d = self.service.stopService()
        d.addCallback(lambda x: self.p.stopListening())
        d.addCallback(self.destroyDb)
        d.addCallback(self.cleanSessions)
        return d

    def query(self, *args):
        pass

    def login(self):
        def validate(result):
            self.assertEquals(2, len(result))
            self.assertEquals({'type': 'PacketAuthOk'}, result[0])
            serial_packet = result[1]
            if int(os.environ.get('VERBOSE_T', '-1')) > 0:
                print "serial_packet " + str(serial_packet)
            self.assertEquals(serial_packet['type'], 'PacketSerial')
            self.failUnless(serial_packet.has_key('cookie'))
            self.cookie = serial_packet['cookie']
            self.failUnless(serial_packet.has_key('serial'))
            self.user_serial = serial_packet['serial']
            return serial_packet['cookie']

        d = self.query('use sessions', { 'type': 'PacketLogin',
                                         'name': 'user1',
                                         'password': 'password' })
        d.addCallback(validate)
        return d

    def logout(self, *args):
        def validate(result):
            self.assertEquals([], result)
            return result

        d = self.query('use sessions', { 'type': 'PacketLogout' })
        d.addCallback(validate)
        return d

    def test01_ping(self):
        self.service.startService()
        d = self.query('no sessions', { 'type': 'PacketPing' })
        d.addCallback(self.assertEquals, [])
        return d

    def test02_login(self):
        self.service.startService()
        d = self.login()
        d.addCallback(self.logout)
        return d

    def cashIn(self, arg):
        d = self.query('use sessions', { 'type': 'PacketPokerCashIn',
                                         'serial': self.user_serial,
                                         'url': 'ONE',
                                         'name': "%040d" % 1,
                                         'bserial': 1,
                                         'value': 100 })
        d.addCallback(self.assertEquals, [{'type': 'PacketAck'}])
        return d

    def test03_cashIn(self):
        self.service.startService()
        d = self.login()
        d.addCallback(self.cashIn)
        d.addCallback(self.logout)
        return d

    def getPersonalInfo(self, arg):
        def validate(result):
            self.assertEquals(1, len(result))
            info = result[0]
            self.assertEquals('PacketPokerPersonalInfo', info['type'])
            self.assertEquals(self.user_serial, info['serial'])

        d = self.query('use sessions', { 'type': 'PacketPokerGetPersonalInfo',
                                         'serial': self.user_serial })
        d.addCallback(validate)
        return d

    def test04_getPersonalInfo(self):
        self.service.startService()
        d = self.login()
        d.addCallback(self.getPersonalInfo)
        d.addCallback(self.logout)
        return d

    def cashOut(self, arg):
        d = self.query('use sessions', { 'type': 'PacketPokerCashOut',
                                         'serial': self.user_serial,
                                         'url': 'ONE',
                                         'value': 10 })
        def validate(packet):
            self.assertEquals('PacketPokerCashOut', packet[0]['type'])
            self.assertEquals(3, packet[0]['bserial'])
            return packet

        d.addCallback(validate)
        return d

    def cashOutCommit(self, arg):
        d = self.query('use sessions', { 'type': 'PacketPokerCashOutCommit',
                                         'transaction_id': "%040d" % 1,
                                         'value': 10 })
        d.addCallback(self.assertEquals, [{'type': 'PacketAck'}])
        return d

    def test05_cashOut(self):
        self.service.startService()
        d = self.login()
        d.addCallback(self.cashIn)
        d.addCallback(self.cashOut)
        d.addCallback(self.cashOutCommit)
        d.addCallback(self.logout)
        return d

    def stats(self):
        d = self.query('no sessions', { 'type': 'PacketPokerStatsQuery' })
        def validate(packet):
            self.assertEquals('PacketPokerStats', packet[0]['type'])
            self.assertEquals(1, packet[0]['players'])
            return packet

        d.addCallback(validate)
        return d

    def test06_stats(self):
        self.service.startService()
        return self.stats()
        return d

    def test07_tableSelect(self):
        self.service.startService()
        d = self.query('no sessions', { 'type': 'PacketPokerTableSelect', 'string': ''})
        def validate(packet):
            self.assertEquals('PacketPokerTableList', packet[0]['type'])
            return packet

        d.addCallback(validate)
        return d

    def test08_polling(self):
        self.service.startService()
        d = self.login()
        def avatarPoll(*args):
            #
            # the avatar must be queuing packets broadcasted to it
            #
            avatar = self.service.avatars[0]
            self.assertTrue(avatar._queue_packets)
            avatar.sendPacket(PacketAck())
            #
            # sending a ping packet will return the packets queued
            # by the avatar
            #
            d = self.query('use sessions', { 'type': 'PacketPing' })
            d.addCallback(self.assertEquals, [{'type': 'PacketAck'}])
            return d
        d.addCallback(avatarPoll)
        return d

class XMLRPCPokerServiceTestCase(PokerServiceTestCase):

    def query(self, *args):
        if hasattr(xmlrpc, "_QueryFactory"): # twisted-2.5
            factory = xmlrpc._QueryFactory('/RPC2', '127.0.0.1:' + str(self.port), 'handlePacket', None, None, False, args)
        elif hasattr(factory, "path"): # twisted-2.4
            factory = xmlrpc.QueryFactory('/RPC2', '127.0.0.1:' + str(self.port), 'handlePacket', None, None, *args)
        else: # twisted-2.3
            factory = xmlrpc.QueryFactory('/RPC2', '127.0.0.1:' + str(self.port), 'handlePacket', *args)
        factory.protocol = QueryProtocol
        factory.cookie = self.cookie
        reactor.connectTCP('127.0.0.1', self.port, factory)
        return factory.deferred


class SOAPPokerServiceTestCase(PokerServiceTestCase):

    def query(self, *args):
        pass # not implemented

# -----------------------------------------------------------------------------------------------------
def GetTestedModule():
    return pokerengineconfig

# -----------------------------------------------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "testREST03"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(XMLRPCPokerServiceTestCase))
    return runner.TrialRunner(reporter.TextReporter,
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
# compile-command: "( cd .. ; ./config.status tests/test-webservice.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerservice.py' TESTS='coverage-reset test-webservice.py coverage-report' check )"
# End:
