#!/usr/bin/python
# -*- py-indent-offset: 4; coding: iso-8859-1; mode: python -*-
#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C)             2008 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C) 2006             Mekensleep <licensing@mekensleep.com>
#                                24 rue vieille du temple 75004 Paris
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

import sys, os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

import libxml2
from MySQLdb.cursors import DictCursor
from pprint import pprint

from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor, defer

twisted.internet.base.DelayedCall.debug = True

from tests.testmessages import silence_all_messages, get_messages, clear_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from pokernetwork import pokercashier, pokernetworkconfig, user
from pokernetwork import currencyclient
currencyclient.CurrencyClient = currencyclient.FakeCurrencyClient
from pokernetwork.pokerpackets import *
from pokernetwork.pokerdatabase import PokerDatabase

settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="3">
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
</server>
""" % {'script_dir': SCRIPT_DIR}

class PokerCashierTestCase(unittest.TestCase):
    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    # --------------------------------------------------------
    def setUp(self):
        self.destroyDb()
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        self.settings.header = self.settings.doc.xpathNewContext()
        self.db = PokerDatabase(self.settings)
        self.cashier = pokercashier.PokerCashier(self.settings)
        self.cashier.setDb(self.db)
        self.user_serial = 5050
        self.user1_serial = 6060
        self.user2_serial = 7070
        self.user3_serial = 8080
        self.users_serial = range(9000, 9010)

    # --------------------------------------------------------
    def tearDown(self):
        self.cashier.close()
#        self.destroyDb()

    # --------------------------------------------------------
    def test01_cashIn(self):
        #
        # Cash in <value> more from the fake currency
        #
        self.value = 100
        self.url = 'http://fake'
        packet = PacketPokerCashIn(serial = self.user_serial,
                                   url = self.url,
                                   bserial = 1,
                                   name = "%040d" % 1,
                                   value = self.value)
        d = self.cashier.cashIn(packet)
        d.addCallback(lambda result: self.check01_cashIn(packet))
        return d
    # --------------------------------------------------------
    def check01_cashIn(self, packet):
        cursor = self.db.cursor(DictCursor)

        #
        # A currency was created
        #
        cursor.execute("SELECT url, serial FROM currencies")
        self.assertEquals(1, cursor.rowcount)
        currency_row = cursor.fetchone()
        self.assertEquals(self.url, currency_row['url'])
        self.assertEquals(1, currency_row['serial'])
        #
        # With a single currency note
        #
        cursor.execute("SELECT currency_serial, serial, name, value FROM safe")
        self.assertEquals(1, cursor.rowcount)
        safe_row = cursor.fetchone()
        self.assertEquals(currency_row['serial'], safe_row['currency_serial'])
        self.assertEquals(2, safe_row['serial'])
        self.assertEquals(self.value, safe_row['value'])
        #
        # Credited to the user
        #
        cursor.execute("SELECT currency_serial, user_serial, amount FROM user2money")
        self.assertEquals(1, cursor.rowcount)
        self.user2money_row = cursor.fetchone()
        self.assertEquals(currency_row['serial'], self.user2money_row['currency_serial'])
        self.assertEquals(self.user_serial, self.user2money_row['user_serial'])
        self.assertEquals(self.value, self.user2money_row['amount'])

        cursor.close()

        return packet

    # --------------------------------------------------------
    def test02_cashIn(self):
        self.value = 100
        self.url = 'http://fake'

        note1 = self.cashier.currency_client._buildNote(self.url, self.value)
        packet1 = PacketPokerCashIn(serial = self.user1_serial,
                                    url = note1[0],
                                    bserial = note1[1],
                                    name = note1[2],
                                    value = note1[3])
        d1 = self.cashier.cashIn(packet1)

        note2 = self.cashier.currency_client._buildNote(self.url, self.value)
        packet2 = PacketPokerCashIn(serial = self.user2_serial,
                                    url = note2[0],
                                    bserial = note2[1],
                                    name = note2[2],
                                    value = note2[3])
        d2 = self.cashier.cashIn(packet2)

        note3 = self.cashier.currency_client._buildNote(self.url, self.value)
        packet3 = PacketPokerCashIn(serial = self.user3_serial,
                                    url = note3[0],
                                    bserial = note3[1],
                                    name = note3[2],
                                    value = note3[3])
        d3 = self.cashier.cashIn(packet3)

        d = defer.DeferredList((d1, d2, d3), fireOnOneErrback = True)
        d.addCallback(lambda result: self.check02_cashIn())
        return d
    # --------------------------------------------------------
    def check02_cashIn(self):
        cursor = self.db.cursor(DictCursor)

        #
        # Only one currency for all buyIn
        #
        cursor.execute("SELECT url, serial FROM currencies")
        self.assertEquals(1, cursor.rowcount)
        currency_row = cursor.fetchone()
        #
        # With a single currency note with an amount == <value> * 2
        #
        cursor.execute("SELECT currency_serial, name, serial, value FROM safe")
        self.assertEquals(1, cursor.rowcount)
        safe_row = cursor.fetchone()
        self.assertEquals(currency_row['serial'], safe_row['currency_serial'])
        self.assertEquals(7, safe_row['serial'])
        self.assertEquals(self.value * 3, safe_row['value'])
        #
        # Credited to the user1
        #
        cursor.execute("SELECT currency_serial, user_serial, amount FROM user2money WHERE user_serial = " + str(self.user1_serial))
        self.assertEquals(1, cursor.rowcount)
        user2money_row = cursor.fetchone()
        self.assertEquals(currency_row['serial'], user2money_row['currency_serial'])
        self.assertEquals(self.user1_serial, user2money_row['user_serial'])
        self.assertEquals(self.value, user2money_row['amount'])
        #
        # Credited to the user2
        #
        cursor.execute("SELECT currency_serial, user_serial, amount FROM user2money WHERE user_serial = " + str(self.user2_serial))
        self.assertEquals(1, cursor.rowcount)
        user2money_row = cursor.fetchone()
        self.assertEquals(currency_row['serial'], user2money_row['currency_serial'])
        self.assertEquals(self.user2_serial, user2money_row['user_serial'])
        self.assertEquals(self.value, user2money_row['amount'])
        #
        # Credited to the user3
        #
        cursor.execute("SELECT currency_serial, user_serial, amount FROM user2money WHERE user_serial = " + str(self.user3_serial))
        self.assertEquals(1, cursor.rowcount)
        user2money_row = cursor.fetchone()
        self.assertEquals(currency_row['serial'], user2money_row['currency_serial'])
        self.assertEquals(self.user3_serial, user2money_row['user_serial'])
        self.assertEquals(self.value, user2money_row['amount'])

        cursor.close()

    def cashOut(self, packet):
        cashOut_packet = PacketPokerCashOut(serial = packet.serial,
                                            url = packet.url,
                                            value = 15,
                                            application_data = 'appdata')
        return self.cashier.cashOut(cashOut_packet)
    # --------------------------------------------------------
    def check03_cashOut(self, packet):
        #print "check03_cashOut " + str(note)
        cursor = self.db.cursor(DictCursor)

        #
        # With two currency notes on the counter
        #
        cursor.execute("SELECT transaction_id, user_serial, currency_serial, name, serial, value, status, application_data FROM counter WHERE status = 'c'")
        self.assertEquals(1, cursor.rowcount)
        counter_row = cursor.fetchone()
        #print "counter_row " + str(counter_row)
        self.assertEquals(15, counter_row['value'])
        self.assertEquals(packet.name, counter_row['name'])
        self.assertEquals(packet.application_data, counter_row['application_data'])

        cursor.close()

        return packet
    # --------------------------------------------------------
    def cashOutCommit(self, packet):
        return self.cashier.cashOutCommit(PacketPokerCashOutCommit(transaction_id = packet.name))

    def check03_cashOutCommit(self, count):
        #print "check03_cashOutCommit " + str(count)
        cursor = self.db.cursor(DictCursor)

        cursor.execute("SELECT * FROM counter ORDER BY value")
        self.assertEquals(0, cursor.rowcount)

        cursor.close()

        return count
    # --------------------------------------------------------
    def test03_cashOut(self):
        d = self.test01_cashIn()

        d.addCallback(self.cashOut)
        d.addCallback(self.check03_cashOut)
        d.addCallback(self.cashOutCommit)
        d.addCallback(self.check03_cashOutCommit)
        return d
    # --------------------------------------------------------
    def test03_cashOut_failure(self):
        d = self.test01_cashIn()

        def cashOutFailure(packet):
            currencyclient.FakeCurrencyFailure = True
            return packet
        d.addCallback(cashOutFailure)
        d.addCallback(self.cashOut)

        self.failed = False

        def check_cashOutFailure(reason):
            currencyclient.FakeCurrencyFailure = False
            from twisted.python import failure
            from twisted.web import error
            self.failUnless(isinstance(reason, failure.Failure))
            self.failUnless(isinstance(reason.value, error.Error))
            self.assertEqual("(page content)", reason.value.response)
            self.failed = True
            return True
        d.addErrback(check_cashOutFailure)

        def check_failed(*args):
            currencyclient.FakeCurrencyFailure = False
            self.failUnless(self.failed, "cash out did not fail but was expected to fail")
            del self.failed

        d.addCallback(check_failed)

        return d
    # --------------------------------------------------------
    def cashQuery(self, packet):
        result = self.cashier.cashQuery(PacketPokerCashQuery(application_data = 'appdata'))
        self.assertEqual(PacketAck(), result)
        result = self.cashier.cashQuery(PacketPokerCashQuery(application_data = 'fakeinvalid'))
        self.assertEqual(PACKET_ERROR, result.type)
        self.assertEqual(PacketPokerCashQuery.DOES_NOT_EXIST, result.code)
        return packet
    # --------------------------------------------------------
    def test04_cashQuery(self):
        d = self.test01_cashIn()

        d.addCallback(self.cashOut)
        d.addCallback(self.cashQuery)
        return d
    # --------------------------------------------------------
    def test06_cashInMany(self):
        self.value = 100
        self.url = 'http://fake'

        dlist = []
        for serial in self.users_serial:
            note = self.cashier.currency_client._buildNote(self.url, self.value)
            packet = PacketPokerCashIn(serial = serial,
                                       url = note[0],
                                       bserial = note[1],
                                       name = note[2],
                                       value = note[3])
            dlist.append(self.cashier.cashIn(packet))

        d = defer.DeferredList(dlist, fireOnOneErrback = True)
        d.addCallback(lambda result: self.check04_cashInMany())
        return d

    def check04_cashInMany(self):
        cursor = self.db.cursor(DictCursor)

        #
        # Only one currency for all buyIn
        #
        cursor.execute("SELECT url, serial FROM currencies")
        self.assertEquals(1, cursor.rowcount)
        currency_row = cursor.fetchone()
        #
        # With a single currency note with an amount == <value> * 2
        #
        cursor.execute("SELECT currency_serial, name, serial, value FROM safe")
        self.assertEquals(1, cursor.rowcount)
        safe_row = cursor.fetchone()
        self.assertEquals(currency_row['serial'], safe_row['currency_serial'])
        count = len(self.users_serial)
        self.assertEquals(count * 2 + 1, safe_row['serial'])
        self.assertEquals(self.value * count, safe_row['value'])
        #
        # Credited to the user N
        #
        for serial in self.users_serial:
            cursor.execute("SELECT currency_serial, user_serial, amount FROM user2money WHERE user_serial = " + str(serial))
            self.assertEquals(1, cursor.rowcount)
            user2money_row = cursor.fetchone()
            self.assertEquals(currency_row['serial'], user2money_row['currency_serial'])
            self.assertEquals(serial, user2money_row['user_serial'])
            self.assertEquals(self.value, user2money_row['amount'])

        cursor.close()

    # --------------------------------------------------------
    def test07_getCurrencySerial(self):
        clear_all_messages()
        self.cashier.parameters['user_create'] = 'no';

        pe = self.failUnlessRaises(PacketError, self.cashier.getCurrencySerial, 'http://fake')
        self.assertEquals(pe.type, PACKET_ERROR)
        self.assertEquals(pe.other_type, PACKET_POKER_CASH_IN)
        self.assertEquals(pe.message,
                        'Invalid currency http://fake and user_create = no in settings.')
        self.assertEquals(pe.code, PacketPokerCashIn.REFUSED)
        self.assertEquals(get_messages(),
                          ["SELECT serial FROM currencies WHERE url = 'http://fake'"])
    # --------------------------------------------------------
    def test08_forcecashInUpdateSafeFail(self):
        self.value = 100
        self.url = 'http://fake'
        p = PacketPokerCashIn(serial = self.user_serial,
                              url = self.url, currency_serial = 1L,
                              bserial = 1, name = "%040d" % 1,
                              value = self.value)
        p.currency_serial = 1L

        gotError = False
        try:
            self.cashier.cashInUpdateSafe("OK",
                                      "0000000000000000000000000000000000000002",
                                      p)
        except PacketError, pe:
            gotError = True
            self.assertEquals(pe.code, PacketPokerCashIn.SAFE)
            self.assertEquals(pe.other_type, PACKET_POKER_CASH_IN)
            self.assertEqual(pe.message.find("INSERT INTO safe SELECT currency_serial, serial, name, value FROM counter") >= 0, True)
        self.assertEquals(gotError, True)

    # --------------------------------------------------------
    def test09_forceCashInUpdateCounter(self):
        self.value = 100
        self.url = 'http://fake'
        p = PacketPokerCashIn(serial = self.user_serial,
                              url = self.url, currency_serial = 1L,
                              bserial = 1, name = "%040d" % 1,
                              value = self.value)
        p.currency_serial = 1L

        cursor = self.db.cursor()
        cursor.execute("DROP table counter")
        cursor.close()

        gotError = False
        try:
            self.cashier.cashInUpdateCounter(
                [['http://fake', 2, '0000000000000000000000000000000000000002', 100]],
                p,
                [('http://fake', 1, '0000000000000000000000000000000000000001', 100)])

        except Exception, e:
            self.assertEquals(e[0], 1146)
            self.assertEquals(e[1], "Table 'pokernetworktest.counter' doesn't exist")
            gotError = True
        self.assertEquals(gotError, True)
    # --------------------------------------------------------
    def test10_foundCounterRowBreakingNote(self):
        self.value = 100
        self.url = 'http://fake'
        p = PacketPokerCashIn(serial = self.user_serial,
                              url = self.url, currency_serial = 1L,
                              bserial = 1, name = "%040d" % 1,
                              value = self.value)
        p.currency_serial = 1L
        cursor = self.db.cursor()
        cursor.execute("insert into counter(transaction_id, user_serial, currency_serial, serial, name, value) values('foo', %d, %d, %d, '%040d', %d)" % (self.user_serial, 1L, 1, 1, self.value))
        cursor.close()
        d = self.cashier.cashInValidateNote(1L, p)
        def check_validateNoteFailure(reason):
            from twisted.python import failure
            from twisted.web import error
            self.failUnless(isinstance(reason, failure.Failure))
            self.failUnless(isinstance(reason.value, PacketError))
            self.assertEqual(reason.value.type, PACKET_ERROR)
            self.assertEqual(reason.value.other_type, PACKET_POKER_CASH_IN)
            self.assertEqual(reason.value.message.find("INSERT INTO safe SELECT currency_serial, serial, name, value FROM counter") >= 0, True)
            return True
        d.addErrback(check_validateNoteFailure)
        return d
    # --------------------------------------------------------
    def test11_duplicateSafeEntriesForCashInValidateNote(self):
        self.value = 100
        self.url = 'http://fake'
        p = PacketPokerCashIn(serial = self.user_serial,
                              url = self.url, currency_serial = 1L,
                              bserial = 1, name = "%040d" % 1,
                              value = self.value)
        p.currency_serial = 1L
        cursor = self.db.cursor()
        cursor.execute("insert into safe(currency_serial, serial, name, value) values(%d, %d, '%040d', %d)" % (1L, 1, 1, self.value))
        cursor.execute("insert into safe(currency_serial, serial, name, value) values(%d, %d, '%040d', %d)" % (1L, 2, 1, self.value))
        cursor.close()
        gotError = False
        try:
            self.cashier.cashInValidateNote(1L, p)
            self.assertEquals("This line should not be reached", False)
        except PacketError, pe:
            gotError = True
            self.assertEquals(pe.other_type, PACKET_POKER_CASH_IN)
            self.assertEquals(pe.code, PacketPokerCashIn.SAFE)
            self.assertEqual(pe.message.find("found 2 records instead of 0 or 1") >= 0, True)
        self.assertEquals(gotError, True)
        return True
    # --------------------------------------------------------
    def test12_cashOutCollectWithoutTransaction(self):
        gotError = False
        self.assertEquals(self.cashier.cashOutCollect(1L, None), None)
        return True
    # --------------------------------------------------------
    def test13_cashOutUpdateSafeTest(self):
        gotError = False
        try:
            self.cashier.cashOutUpdateSafe(None, 1, 1)
            self.assertEquals("This line should not be reached", False)
        except PacketError, pe:
            gotError = True
            self.assertEquals(pe.other_type, PACKET_POKER_CASH_OUT)
            self.assertEquals(pe.code, PacketPokerCashOut.SAFE)
            self.assertEqual(pe.message.find("affected 0 records") >= 0, True)
        self.assertEquals(gotError, True)
        return True
    # --------------------------------------------------------
    def test14_cashOutUpdateSafeSecondPartFails(self):
        self.value = 100
        self.url = 'http://fake'
        cursor = self.db.cursor()
        cursor.execute("insert into safe(currency_serial, serial, name, value) values(%d, %d, '%040d', %d)" % (1L, 1, 1, self.value))

        cursor.execute("insert into counter(transaction_id, user_serial, currency_serial, serial, name, value, status) values(%d, %d, %d, %d, '%040d', %d, '%s')" % (2, 2, 1, 2L, 2, self.value, 'n'))
        cursor.execute("insert into counter(transaction_id, user_serial, currency_serial, serial, name, value, status) values(%d, %d, %d, %d, '%040d', %d, '%s')" % (1, 1, 1, 1L, 1, self.value, 'c'))
        cursor.execute("insert into currencies(url, serial) values('%s', %d)" % ('http://fake', 1))
        cursor.close()
        self.closuredCount = 0
        def dummyCashOutCollect(currency_serial, trans_id):
            self.closuredCount += 1
            if self.closuredCount == 1:
                return None
            else:
                return PacketPokerCashOut(serial = 5, url = 'http://fake',
                                          bserial = 5, name = "5", value = 5,
                                          application_data = "dummy")
        origCashOutCollect = self.cashier.cashOutCollect
        self.cashier.cashOutCollect = dummyCashOutCollect

        gotError = False
        try:
            self.cashier.cashOutUpdateSafe(None, 1L, 1)
            self.assertEquals("This line should not be reached", False)
        except PacketError, pe:
            gotError = True
            self.assertEquals(pe.other_type, PACKET_POKER_CASH_OUT)
            self.assertEquals(pe.code, PacketPokerCashOut.SAFE)
            self.assertEqual(pe.message.find("UPDATE user2money SET amount") >= 0,
                             True)
            self.assertEqual(pe.message.find("affected 0 records instead of 1") >= 0,
                             True)
        self.assertEquals(gotError, True)
        self.cashier.cashOutCollect = origCashOutCollect
        return True
# --------------------------------------------------------
# Following tests use a MockDB rather than the real MySQL database
class PokerCashierFakeDBTestCase(unittest.TestCase):
    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    # --------------------------------------------------------
    def setUp(self):
        self.destroyDb()
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        self.settings.header = self.settings.doc.xpathNewContext()
        self.cashier = pokercashier.PokerCashier(self.settings)
        self.user_serial = 5050
        self.user1_serial = 6060
        self.user2_serial = 7070
        self.user3_serial = 8080
        self.users_serial = range(9000, 9010)

    # --------------------------------------------------------
    def tearDown(self):
        self.cashier.close()
#        self.destroyDb()
    # --------------------------------------------------------
    def test01_getCurrencySerial_forceExceptionOnRowCount(self):
        clear_all_messages()
        self.cashier.parameters['user_create'] = 'yes'
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
            def close(cursorSelf): pass
            def execute(*args):
                self = args[0]
                sql = args[1]
                if sql.find('SELECT') >= 0:
                    self.rowcount = 0
                elif sql.find('INSERT') >= 0:
                    self.rowcount = 0
                else:
                    self.failIf(True)  # Should not be reached.
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
            def cursor(dbSelf):
                return MockCursor()

        self.cashier.setDb(MockDatabase())

        caughtExeption = False
        try:
            self.cashier.getCurrencySerial("http://example.org")
            self.failIf(True)
        except Exception, e:
            caughtExeption = True
            self.assertEquals(e.__str__(), "SQL command 'INSERT INTO currencies (url) VALUES (%s)' failed without raising exception.  Underlying DB may be severely hosed")
        self.failUnless(caughtExeption)

        self.assertEquals(get_messages(), ['SELECT serial FROM currencies WHERE url = http://example.org', 'INSERT INTO currencies (url) VALUES (http://example.org)'])
    # --------------------------------------------------------
    def test02_getCurrencySerial_forceExceptionOnExecute(self):
        clear_all_messages()
        from MySQLdb.constants import ER
        self.cashier.parameters['user_create'] = 'yes'
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
            def close(cursorSelf): pass
            def execute(*args):
                self = args[0]
                sql = args[1]
                if sql.find('SELECT') >= 0:
                    self.rowcount = 0
                elif sql.find('INSERT INTO') >= 0:
                    raise Exception(ER.DUP_ENTRY)
                else:
                    self.failIf(True)  # Should not be reached.
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
            def cursor(dbSelf):
                return MockCursor()

        self.cashier.setDb(MockDatabase())

        caughtExeption = False
        try:
            self.cashier.getCurrencySerial("http://example.org", reentrant = False)
            self.failIf(True)
        except Exception, e:
            caughtExeption = True
            self.assertEquals(len(e.args), 1)
            self.assertEquals(e[0], ER.DUP_ENTRY)
        self.failUnless(caughtExeption)

        self.assertEquals(get_messages(), ['SELECT serial FROM currencies WHERE url = http://example.org', 'INSERT INTO currencies (url) VALUES (http://example.org)'])
    # --------------------------------------------------------
    def test03_getCurrencySerial_forceRecursionWithNoResolution(self):
        clear_all_messages()
        from MySQLdb.constants import ER
        self.cashier.parameters['user_create'] = 'yes'
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.selectCount = 0
                cursorSelf.insertCount = 0
            def close(cursorSelf): pass
            def execute(*args):
                cursorSelf = args[0]
                sql = args[1]
                if sql.find('SELECT') >= 0:
                    self.rowcount = 0
                    cursorSelf.selectCount += 1
                elif sql.find('INSERT INTO') >= 0:
                    cursorSelf.insertCount += 1
                    raise Exception(ER.DUP_ENTRY)
                else:
                    self.failIf(True)  # Should not be reached.
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf):
                return dbSelf.cursorValue

        db = MockDatabase()
        self.cashier.setDb(db)

        caughtExeption = False
        try:
            self.cashier.getCurrencySerial("http://example.org")
            self.failIf(True)
        except Exception, e:
            caughtExeption = True
            self.assertEquals(len(e.args), 1)
            self.assertEquals(e[0], ER.DUP_ENTRY)
        self.failUnless(caughtExeption)
        self.assertEquals(db.cursor().selectCount, 2)
        self.assertEquals(db.cursor().insertCount, 2)

        self.assertEquals(get_messages(), ['SELECT serial FROM currencies WHERE url = http://example.org', 'INSERT INTO currencies (url) VALUES (http://example.org)', 'SELECT serial FROM currencies WHERE url = http://example.org', 'INSERT INTO currencies (url) VALUES (http://example.org)'])
    # --------------------------------------------------------
    def test04_cashOutUpdateSafe_twoNullPackets(self):
        """test04_cashOutUpdateSafe_forceFallThrough
        This test is handling the case where cashOutCollect() twice
        returns an empty packet in a row.  The code in cashOutUpdateSafe()
        does not actually check what is returned on the second call, but
        is wrapped in a try/except, so we catch that and make sure the
        operations."""

        clear_all_messages()
        from MySQLdb.constants import ER
        self.cashier.parameters['user_create'] = 'yes'
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'SELECT', 'INSERT INTO', 'UPDATE',
                                                  'DELETE', 'START TRANSACTION',
                                                  'COMMIT', 'ROLLBACK' ]
                for cntType in cursorSelf.acceptedStatements:
                    cursorSelf.counts[cntType] = 0
            def close(cursorSelf): pass
            def execute(*args):
                cursorSelf = args[0]
                sql = args[1]
                found = False
                for str in cursorSelf.acceptedStatements:
                    if sql[:len(str)] == str:
                        cursorSelf.counts[str] += 1
                        cursorSelf.rowcount = 0
                        if str == "DELETE" or str == 'UPDATE':
                            cursorSelf.rowcount = 1
                        found = True
                        break
                self.failUnless(found)
                return cursorSelf.rowcount
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf):
                return dbSelf.cursorValue

        db = MockDatabase()
        self.cashier.setDb(db)

        caughtExeption = False
        try:
            packet = self.cashier.cashOutUpdateSafe("IGNORED", 5, 8)
            self.failIf(True)
        except Exception, e:
            caughtExeption = True
            self.assertEquals(len(e.args), 1)
            self.assertEquals(e[0], "'NoneType' object has no attribute 'value'")

        self.assertEquals(caughtExeption, True)
        self.assertEquals(db.cursor().counts['SELECT'], 2)
        self.assertEquals(db.cursor().counts['DELETE'], 2)
        self.assertEquals(db.cursor().counts['INSERT INTO'], 1)
        self.assertEquals(db.cursor().counts['ROLLBACK'], 1)
        self.assertEquals(db.cursor().counts['COMMIT'], 0)
    # --------------------------------------------------------
    def test05_cashOutUpdateSafe_secondPacketGood(self):
        """test05_cashOutUpdateSafe_secondPacketGood
        On the second call to cashOutCollect(), we return a valid row.
        This causes us to get back a valid packet.  But still an (ignored)
        error on the lock() not existing."""
        clear_all_messages()
        from MySQLdb.constants import ER
        self.cashier.parameters['user_create'] = 'yes'
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'SELECT', 'INSERT INTO', 'UPDATE',
                                                  'DELETE', 'START TRANSACTION',
                                                  'COMMIT', 'ROLLBACK' ]
                cursorSelf.row = ()
                for cntType in cursorSelf.acceptedStatements:
                    cursorSelf.counts[cntType] = 0
            def close(cursorSelf): pass
            def execute(*args):
                cursorSelf = args[0]
                sql = args[1]
                found = False
                for str in cursorSelf.acceptedStatements:
                    if sql[:len(str)] == str:
                        cursorSelf.counts[str] += 1
                        cursorSelf.rowcount = 0
                        if str == "DELETE" or str == 'UPDATE':
                            cursorSelf.rowcount = 1
                        found = True
                        break
                self.failUnless(found)
                # The second time cashOutCollect() is called, we want to
                # return a valid set of values.
                if str == "SELECT" and cursorSelf.counts[str] == 2:
                    cursorSelf.rowcount = 1
                    cursorSelf.row = (5, "http://example.org", 5, "example", 10, "")
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf):
                return dbSelf.cursorValue

        db = MockDatabase()
        self.cashier.setDb(db)

        packet = self.cashier.cashOutUpdateSafe("IGNORED", 5, 8)
        self.assertEquals(packet.type, PACKET_POKER_CASH_OUT)
        self.assertEquals(packet.serial, 5)
        self.assertEquals(packet.url, "http://example.org")
        self.assertEquals(packet.name, "example")
        self.assertEquals(packet.bserial, 5)
        self.assertEquals(packet.value, 10)
        self.assertEquals(db.cursor().counts['SELECT'], 2)
        self.assertEquals(db.cursor().counts['DELETE'], 2)
        self.assertEquals(db.cursor().counts['INSERT INTO'], 1)
        self.assertEquals(db.cursor().counts['ROLLBACK'], 0)
        self.assertEquals(db.cursor().counts['COMMIT'], 1)
        msgs = get_messages()
        self.assertEquals(msgs[len(msgs)-1], '*ERROR* cashInUnlock: unexpected missing cash_5 in locks (ignored)')
    # --------------------------------------------------------
    def test06_cashOutUpdateSafe_forceFakeFalsePacket(self):
        """test06_cashOutUpdateSafe_forceFakeFalsePacket
        We override the second call to cashOutCollect(), so we return a
        valid row.  We force the packet returned to always be false, to
        force the final error code to operate.  """
        clear_all_messages()
        from MySQLdb.constants import ER
        self.cashier.parameters['user_create'] = 'yes'
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'SELECT', 'INSERT INTO', 'UPDATE',
                                                  'DELETE', 'START TRANSACTION',
                                                  'COMMIT', 'ROLLBACK' ]
                cursorSelf.row = ()
                for cntType in cursorSelf.acceptedStatements:
                    cursorSelf.counts[cntType] = 0
            def close(cursorSelf): pass
            def execute(*args):
                cursorSelf = args[0]
                sql = args[1]
                found = False
                for str in cursorSelf.acceptedStatements:
                    if sql[:len(str)] == str:
                        cursorSelf.counts[str] += 1
                        cursorSelf.rowcount = 0
                        if str == "DELETE" or str == 'UPDATE':
                            cursorSelf.rowcount = 1
                        found = True
                        break
                self.failUnless(found)
                return cursorSelf.rowcount
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf):
                return dbSelf.cursorValue

        db = MockDatabase()
        self.cashier.setDb(db)

        global calledCount
        calledCount = 0

        class  MockPacket:
            def __init__(mockPacketSelf):
                mockPacketSelf.serial  = 5
                mockPacketSelf.value  = 10
            def __nonzero__(mockPacketSelf): return False

        def mockedcashOutCollect(currencySerial, transactionId):
            return MockPacket()

        self.cashier.cashOutCollect = mockedcashOutCollect

        packet = self.cashier.cashOutUpdateSafe("IGNORED", 5, 8)

        self.assertEquals(packet.type, PACKET_ERROR)
        self.assertEquals(packet.message, 'no currency note to be collected for currency 5')
        self.assertEquals(packet.other_type, PACKET_POKER_CASH_OUT)
        self.assertEquals(packet.code, PacketPokerCashOut.EMPTY)

        self.assertEquals(db.cursor().counts['SELECT'], 0)
        self.assertEquals(db.cursor().counts['DELETE'], 2)
        self.assertEquals(db.cursor().counts['INSERT INTO'], 1)
        self.assertEquals(db.cursor().counts['ROLLBACK'], 0)
        self.assertEquals(db.cursor().counts['COMMIT'], 1)
        msgs = get_messages()
        self.assertEquals(msgs[len(msgs)-1], '*ERROR* cashInUnlock: unexpected missing cash_5 in locks (ignored)')
    # --------------------------------------------------------
    def cashOutUpdateCounter_weirdLen(self, new_notes, message):
        clear_all_messages()
        class  MockDatabase:
            def cursor(dbSelf): return MockCursor()
        class  MockCursor: pass
        db = MockDatabase()
        self.cashier.setDb(db)

        caughtIt = False
        try:
            self.cashier.cashOutUpdateCounter(new_notes, "dummy packet")
            self.failIf(True)
        except PacketError, pe:
            caughtIt = True
            self.assertEquals(pe.type, PACKET_ERROR)
            self.assertEquals(pe.other_type, PACKET_POKER_CASH_OUT)
            self.assertEquals(pe.code, PacketPokerCashOut.BREAK_NOTE)
            self.assertEquals(pe.message, "breaking dummy packet resulted in %d notes (%s) instead of 2"
                              % (len(new_notes), message))
            self.assertEquals(get_messages(),
                              ["cashOutUpdateCounter: new_notes = %s packet = dummy packet" % message])
        self.failUnless(caughtIt)
    # --------------------------------------------------------
    def test07_cashOutUpdateCounter_weirdLen_1(self):
        self.cashOutUpdateCounter_weirdLen(['a'], "['a']")
    # --------------------------------------------------------
    def test07_cashOutUpdateCounter_weirdLen_3(self):
        self.cashOutUpdateCounter_weirdLen(['a', 'b', 'c'], "['a', 'b', 'c']")
    # --------------------------------------------------------
    def test08_cashOutUpdateCounter_various(self):
        """test08_cashOutUpdateCounter_various
        This is a somewhat goofy test in that it is covering a bunch of
        oddball situations in cashOutUpdateCounter().  First, it's
        checking for the case where the new_notes args are in order [
        user, server].  Second, it checks that when server_note's value is
        zero, only one INSERT is done.  Third, it's handling the case when
        an Exception is thrown by the execute causing a rollback. """
        self.cashier.parameters['user_create'] = 'yes'
        class MockException(Exception):
            pass
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'INSERT INTO', 'START TRANSACTION',
                                                  'COMMIT', 'ROLLBACK' ]
                cursorSelf.row = ()
                for cntType in cursorSelf.acceptedStatements:
                    cursorSelf.counts[cntType] = 0
            def close(cursorSelf): pass
            def execute(*args):
                cursorSelf = args[0]
                sql = args[1]
                found = False
                for str in cursorSelf.acceptedStatements:
                    if sql[:len(str)] == str:
                        cursorSelf.counts[str] += 1
                        cursorSelf.rowcount = 0
                        found = True
                        break
                self.failUnless(found)
                if sql[:len(str)] == "INSERT INTO": raise MockException()
                return cursorSelf.rowcount
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf):
                return dbSelf.cursorValue
        class  MockPacket:
            def __init__(mockPacketSelf):
                mockPacketSelf.value  = 55
                mockPacketSelf.currency_serial = 5
                mockPacketSelf.serial = 1
                mockPacketSelf.application_data = "application"
            def __str__(mockPacketSelf): return "MOCK PACKET"

        db = MockDatabase()
        self.cashier.setDb(db)

        caughtIt = False
        clear_all_messages()
        try:
            self.cashier.cashOutUpdateCounter([ (0, 5, "joe", 55), (0, 0, "server", 0)],
                                              MockPacket())
            self.failIf(True)
        except MockException, me:
            caughtIt = True
            self.failUnless(isinstance(me, MockException))

        self.failUnless(caughtIt)
        self.assertEquals(db.cursor().counts['INSERT INTO'], 1)
        self.assertEquals(db.cursor().counts['ROLLBACK'], 1)
        self.assertEquals(db.cursor().counts['COMMIT'], 0)
        self.assertEquals(db.cursor().counts['START TRANSACTION'], 1)
        self.assertEquals(get_messages(),
                          ["cashOutUpdateCounter: new_notes = [(0, 5, 'joe', 55), (0, 0, 'server', 0)] packet = MOCK PACKET"])
    # --------------------------------------------------------
    def test09_cashOutUpdateCounter_forceRaiseOnNotesOrder(self):
        """test09_cashOutUpdateCounter_forceRaiseOnNotesOrder
        This test handles the case where new_notes do not match what is in
        the packet sent to cashOutUpdateCounter() """
        caughtIt = False
        clear_all_messages()
        class  MockPacket:
            def __init__(mockPacketSelf): mockPacketSelf.value  = 43
            def __str__(mockPacketSelf):  return "MOCK PACKET"
        class  MockDatabase:
            def cursor(mockDBSelf): return "MOCK CURSOR"
        db = MockDatabase()
        self.cashier.setDb(db)
        try:
            self.cashier.cashOutUpdateCounter([ (0, 5, "joe", 57), (0, 0, "server", 59)],
                                              MockPacket())
            self.failIf(True)
        except PacketError, pe:
            caughtIt = True
            self.failUnless(isinstance(pe, PacketError))
            self.assertEquals(pe.other_type, PACKET_POKER_CASH_OUT)
            self.assertEquals(pe.code, PacketPokerCashOut.BREAK_NOTE)
            self.assertEquals(pe.message,
                              "breaking MOCK PACKET did not provide a note with the proper value (notes are [(0, 5, 'joe', 57), (0, 0, 'server', 59)])")
        self.failUnless(caughtIt)
    # --------------------------------------------------------
    def test10_cashOutBreakNote_DeferredFromCommit(self):
        """test10_cashOutBreakNote_DeferredFromCommit
        Handle situation where the currency_serial already has an entry in
        counter table, and causes a deferred to be returned from
        cashOutCurrencyCommit()."""
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'SELECT transaction_id',
                                                  "SELECT serial FROM currencies",
                                                  "SELECT counter.user_serial"]
                cursorSelf.row = ()
                for cntType in cursorSelf.acceptedStatements:
                    cursorSelf.counts[cntType] = 0
            def close(cursorSelf): pass
            def execute(*args):
                cursorSelf = args[0]
                sql = args[1]
                found = False
                for str in cursorSelf.acceptedStatements:
                    if sql[:len(str)] == str:
                        cursorSelf.counts[str] += 1
                        cursorSelf.rowcount = 0
                        cursorSelf.row = ()
                        found = True
                        break
                self.failUnless(found)
                if sql[:len(str)] == 'SELECT transaction_id':
                    cursorSelf.rowcount = 1
                    cursorSelf.row = (777,)
                elif sql[:len(str)] == "SELECT serial FROM currencies":
                    cursorSelf.rowcount = 1
                    cursorSelf.row = (6,)
                elif sql[:len(str)] == "SELECT counter.user_serial":
                    cursorSelf.rowcount = 1
                    cursorSelf.row = ( 6, "http://example.org", 9, "joe", 100, "application" )
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue
        class  MockPacket:
            def __init__(mockPacketSelf):
                mockPacketSelf.url  = "http://cashier.example.org"
                mockPacketSelf.currency_serial = 12
            def __str__(mockPacketSelf): return "MOCK PACKET"
        class  MockCurrencyClient:
            def commit(ccSelf, url, transactionId):
                self.assertEquals(url, "http://cashier.example.org")
                self.assertEquals(transactionId, 777)
                return defer.Deferred()

        db = MockDatabase()
        self.cashier.setDb(db)
        self.cashier.currency_client = MockCurrencyClient()

        clear_all_messages()
        d = self.cashier.cashOutBreakNote("MEANINGLESS ARG", MockPacket())

        for key in db.cursor().counts.keys():
            if key in [ 'SELECT transaction_id', "SELECT serial FROM currencies" ]:
                self.assertEquals(db.cursor().counts[key], 1)
            else:
                self.assertEquals(db.cursor().counts[key], 0)
        self.assertEquals(get_messages(), ['SELECT transaction_id FROM counter WHERE  currency_serial = 12', 'cashOutCurrencyCommit', 'SELECT serial FROM currencies WHERE url = http://cashier.example.org'])
        clear_all_messages()

        self.assertEquals(d.callback(True), None)
        pack = d.result
        self.assertEquals(pack.type, PACKET_POKER_CASH_OUT)
        self.assertEquals(pack.serial,  6)
        self.assertEquals(pack.url, 'http://example.org')
        self.assertEquals(pack.name, 'joe')
        self.assertEquals(pack.bserial, 9)
        self.assertEquals(pack.value, 100)
        self.assertEquals(pack.application_data, 'application')
        [self.assertEquals(db.cursor().counts[key], 1) for key in db.cursor().counts.keys()]
        msgs = get_messages()
        self.assertEquals(len(msgs), 4)
        self.assertEquals(msgs[0], 'cashOutUpdateSafe: 6 777')
        self.assertEquals(msgs[3], '*ERROR* cashInUnlock: unexpected missing cash_6 in locks (ignored)')
    # --------------------------------------------------------
    def test11_cashOutBreakNote_multirowForSerial(self):
        """test11_cashOutBreakNote_multirowForSerial

        """
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'SELECT transaction_id',
                                                  'SELECT name']
                cursorSelf.row = ()
                for cntType in cursorSelf.acceptedStatements:
                    cursorSelf.counts[cntType] = 0
            def close(cursorSelf): pass
            def execute(*args):
                cursorSelf = args[0]
                sql = args[1]
                found = False
                for str in cursorSelf.acceptedStatements:
                    if sql[:len(str)] == str:
                        cursorSelf.counts[str] += 1
                        cursorSelf.rowcount = 0
                        cursorSelf.row = ()
                        found = True
                        break
                self.failUnless(found)
                return cursorSelf.rowcount
        class MockDatabase:
            def __init__(dbSelf):
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue
        class  MockPacket:
            def __init__(mockPacketSelf):
                mockPacketSelf.url  = "http://cashier.example.org"
                mockPacketSelf.currency_serial = 12
            def __str__(mockPacketSelf): return "MOCK PACKET"
        db = MockDatabase()
        self.cashier.setDb(db)

        clear_all_messages()
        caughtIt = False
        failMsg = 'SELECT name, serial, value FROM safe WHERE currency_serial = 12 found 0 records instead of exactly 1'
        try:
            self.cashier.cashOutBreakNote("MEANINGLESS ARG", MockPacket())
            self.failIf(True)  # Should not be reached
        except PacketError, pe:
            caughtIt = True
            self.assertEquals(pe.other_type, PACKET_POKER_CASH_OUT)
            self.assertEquals(pe.type, PACKET_ERROR)
            self.assertEquals(pe.code, PacketPokerCashOut.SAFE)
            self.assertEquals(pe.message, failMsg)
        self.failUnless(caughtIt)
        msgs = get_messages()
        self.assertEquals(len(msgs), 3)
        self.assertEquals(msgs[2], "*ERROR* " + failMsg)
# --------------------------------------------------------
# Following tests are for the lock/unlock mechanism and do not need any
# database at all.
class PokerCashierLockUnlockTestCase(unittest.TestCase):
    # --------------------------------------------------------
    def setUp(self):
        from pokernetwork import pokerlock
        class  MockLock:
            def __init__(lockSelf, params):
                lockSelf.alive = False
                lockSelf.started = False
                lockSelf.acquireCounts = {}
            def isAlive(lockSelf): return lockSelf.alive
            def close(lockSelf):
                lockSelf.alive = False
                lockSelf.started = False
            def release(lockSelf, name):
                lockSelf.alive = False
                lockSelf.acquireCounts[name] -= 1
            def start(lockSelf):
                lockSelf.alive = True
                lockSelf.started = True
            def acquire(lockSelf, name, value):
                self.assertEquals(value, 5)
                if lockSelf.acquireCounts.has_key(name):
                    lockSelf.acquireCounts[name] += 1
                else:
                    lockSelf.acquireCounts[name] = 1
                return "ACQUIRED %s: %d" % (name, lockSelf.acquireCounts[name])

        pokercashier.PokerLock = MockLock
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        self.settings.header = self.settings.doc.xpathNewContext()
        self.cashier = pokercashier.PokerCashier(self.settings)
    # --------------------------------------------------------
    def tearDown(self):
        pass
    # --------------------------------------------------------
    def test01_unlockNonExistent(self):
        """test01_unlockNonExistent
        Tests when unlock is called on a serial that does not exist."""
        self.assertEquals(self.cashier.locks, {})
        clear_all_messages()
        self.assertEquals(self.cashier.unlock(5), None)
        self.assertEquals(self.cashier.locks, {})
        self.assertEquals(get_messages(), ['*ERROR* cashInUnlock: unexpected missing cash_5 in locks (ignored)'])
    # --------------------------------------------------------
    def test02_lockCreateTwice(self):
        """test02_lockCreateTwice
        Testing creation of the lock twice."""
        self.assertEquals(self.cashier.locks, {})
        clear_all_messages()
        self.assertEquals(self.cashier.lock(2), "ACQUIRED cash_2: 1")
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2Lock = self.cashier.locks['cash_2']
        self.failUnless(cash2Lock.alive)
        self.failUnless(cash2Lock.started)
        self.assertEquals(cash2Lock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2Lock.acquireCounts['cash_2'], 1)
    # --------------------------------------------------------
    def test03_lockCreateTwiceWhenUnalive(self):
        """test03_lockCreateTwiceWhenUnalive
        Testing creation of the lock again after the activity is turned
        off."""
        self.assertEquals(self.cashier.locks, {})
        clear_all_messages()
        self.assertEquals(self.cashier.lock(2), "ACQUIRED cash_2: 1")
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2Lock = self.cashier.locks['cash_2']
        self.failUnless(cash2Lock.alive)
        self.failUnless(cash2Lock.started)
        self.assertEquals(cash2Lock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2Lock.acquireCounts['cash_2'], 1)
        self.assertEquals(get_messages(), ['get lock cash_2'])

        clear_all_messages()
        cash2Lock.alive = False

        self.assertEquals(self.cashier.lock(2), "ACQUIRED cash_2: 1")
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2newLock = self.cashier.locks['cash_2']
        self.failUnless(cash2newLock.alive)
        self.failUnless(cash2newLock.started)
        self.assertEquals(cash2newLock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2newLock.acquireCounts['cash_2'], 1)
        self.assertEquals(get_messages(), ['get lock cash_2'])
    # --------------------------------------------------------
    def test04_unlockTwice(self):
        """test03_unlockTwice
        try to unlock a lock twice"""
        self.assertEquals(self.cashier.locks, {})
        clear_all_messages()
        self.assertEquals(self.cashier.lock(2), "ACQUIRED cash_2: 1")
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2Lock = self.cashier.locks['cash_2']
        self.failUnless(cash2Lock.alive)
        self.failUnless(cash2Lock.started)
        self.assertEquals(cash2Lock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2Lock.acquireCounts['cash_2'], 1)
        self.assertEquals(get_messages(), ['get lock cash_2'])

        clear_all_messages()

        self.assertEquals(self.cashier.unlock(2), None)
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2newLock = self.cashier.locks['cash_2']
        self.failIf(cash2newLock.alive)
        self.failUnless(cash2newLock.started)
        self.assertEquals(cash2newLock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2newLock.acquireCounts['cash_2'], 0)
        self.assertEquals(get_messages(), [])

        self.assertEquals(self.cashier.unlock(2), None)
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2newLock = self.cashier.locks['cash_2']
        self.failIf(cash2newLock.alive)
        self.failUnless(cash2newLock.started)
        self.assertEquals(cash2newLock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2newLock.acquireCounts['cash_2'], 0)
        self.assertEquals(get_messages(),
                          ['*ERROR* cashInUnlock: unexpected dead cash_2 pokerlock (ignored)'])
    # --------------------------------------------------------
    def test05_lockCreateTwiceWhenAliven(self):
        """test05_lockCreateTwiceWhenAlive
        relock after lock leaving it alive"""
        self.assertEquals(self.cashier.locks, {})
        clear_all_messages()
        self.assertEquals(self.cashier.lock(2), "ACQUIRED cash_2: 1")
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2Lock = self.cashier.locks['cash_2']
        self.failUnless(cash2Lock.alive)
        self.failUnless(cash2Lock.started)
        self.assertEquals(cash2Lock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2Lock.acquireCounts['cash_2'], 1)
        self.assertEquals(get_messages(), ['get lock cash_2'])

        clear_all_messages()

        self.assertEquals(self.cashier.lock(2), "ACQUIRED cash_2: 2")
        self.assertEquals(self.cashier.locks.keys(), ['cash_2'])
        cash2newLock = self.cashier.locks['cash_2']
        self.failUnless(cash2newLock.alive)
        self.failUnless(cash2newLock.started)
        self.assertEquals(cash2newLock.acquireCounts.keys(), [ 'cash_2' ])
        self.assertEquals(cash2newLock.acquireCounts['cash_2'], 2)
        self.assertEquals(get_messages(), ['get lock cash_2'])
# --------------------------------------------------------
def GetTestSuite():
    suite = runner.TestSuite(PokerCashierTestCase)
    suite.addTest(unittest.makeSuite(PokerCashierTestCase))
    suite.addTest(unittest.makeSuite(PokerCashierFakeDBTestCase))
    suite.addTest(unittest.makeSuite(PokerCashierLockUnlockTestCase))
    return suite
# --------------------------------------------------------
def GetTestedModule():
    return pokerengineconfig

# --------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test11"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerCashierTestCase))
    suite.addTest(loader.loadClass(PokerCashierFakeDBTestCase))
    suite.addTest(loader.loadClass(PokerCashierLockUnlockTestCase))
    return runner.TrialRunner(reporter.VerboseTextReporter,
#                              tracebackFormat='verbose',
                              tracebackFormat='default',
                              ).run(suite)

# --------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokercashier.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokercashier.py' TESTS='coverage-reset test-pokercashier.py coverage-report' check )"
# End:
