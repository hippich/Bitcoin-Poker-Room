#!/usr/bin/python
# -*- mode: python; coding: iso-8859-1 -*-
# more information about the above line at http://www.python.org/dev/peps/pep-0263/
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C)       2008, 2009 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C)             2009 Johan Euphrosine <proppy@aminche.com>
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
#  Loic Dachary <loic@gnu.org>
#  Bradley M. Kuhn <bkuhn@ebb.org>
#  Cedric Pinson <cpinson@freesheep.org>
#
import sys, os, tempfile, shutil
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

import time

from string import split
import libxml2
import random
import locale
import sets
from _mysql_exceptions import IntegrityError
import exceptions
from pprint import pprint
from datetime import date

from tests import testclock

from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor, defer

twisted.internet.base.DelayedCall.debug = True

from tests.testmessages import silence_all_messages, search_output, clear_all_messages, get_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
silence_all_messages()

from pokerengine import pokertournament, pokergame
from pokernetwork import pokerservice, pokernetworkconfig, user
from pokernetwork import currencyclient
from pokernetwork import pokerdatabase
currencyclient.CurrencyClient = currencyclient.FakeCurrencyClient
from pokernetwork.pokerpackets import *
from pokernetwork.packets import PacketError
from pokernetwork.pokertable  import PokerAvatarCollection
from MySQLdb.cursors import DictCursor


class ConstantDeckShuffler:
    def shuffle(self, what):
        what[:] = [40, 13, 32, 9, 19, 31, 15, 14, 50, 34, 20, 6, 43, 44, 28, 29, 48, 3, 21, 45, 23, 37, 35, 11, 5, 22, 24, 30, 27, 39, 46, 33, 0, 8, 1, 42, 36, 16, 49, 2, 10, 26, 4, 18, 7, 41, 47, 17]

from pokerengine import pokergame
pokergame.shuffler = ConstantDeckShuffler()

class ConstantPlayerShuffler:
    def shuffle(self, what):
        what.sort()

from pokerengine import pokertournament
pokertournament.shuffler = ConstantPlayerShuffler()

TABLE1 = 1
TABLE2 = 2
TABLE3 = 3

# Note that we use the locale fr_FR.ISO-8859-1 here for testing.  This must be
# a valid locale on the system!  Important tests are skipped otherwise!!!

localLocale = locale.getlocale(locale.LC_ALL)
FRENCH_LOCALE_MISSING = False
MESSAGE_WHEN_FRENCH_LOCALE_MISSING = "WARNING: Locale fr_FR.ISO-8859-1 missing, so certain tests will be SKIPPED and coverage will be INCOMPLETE! FAIL!  fail!"
try:
    locale.setlocale(locale.LC_ALL, "fr_FR.ISO-8859-1")
except locale.Error, le:
    print MESSAGE_WHEN_FRENCH_LOCALE_MISSING
    FRENCH_LOCALE_MISSING = True

locale.setlocale(locale.LC_ALL, localLocale)


settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" remove_completed="1" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19480" />

  <language value="en_US.ISO-8859-1"/>
  <language value="fr_FR.ISO-8859-1"/>
  <language value="fr_FX.ISO-8859-1"/>
  <language value="de_DE.ISO-8859-1"/>
  <language value="en_GB.ISO-8859-1"/>
  <language value="es_ES.ISO-8859-1"/>
  <language value="nl_NL.ISO-8859-1"/>
  <language value="fr_BE.ISO-8859-1"/>
  <language value="en_CA.ISO-8859-1"/>
  <language value="fr_CA.ISO-8859-1"/>
  <language value="it_IT.ISO-8859-1"/>
  <language value="pt_PT.ISO-8859-1"/>
  <language value="da_DK.ISO-8859-1"/>
  <language value="fi_FI.ISO-8859-1"/>
  <language value="nb_NO.ISO-8859-1"/>
  <language value="sv_SE.ISO-8859-1"/>
  <language value="this_locale_does_not_exist"/>

  <stats type="RankPercentile"/>

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

def fun_name():
    try:
        raise ZeroDivisionError
    except ZeroDivisionError:
        return sys.exc_info()[2].tb_frame.f_back.f_code.co_name

class MockCursorBase:
    def __init__(cursorSelf, testObject, acceptList):
        cursorSelf.testObject = testObject
        cursorSelf.rowcount = 0
        cursorSelf.closedCount = 0
        cursorSelf.counts = {}
        cursorSelf.acceptedStatements = acceptList
        cursorSelf.row = ()
        for cntType in cursorSelf.acceptedStatements:
            cursorSelf.counts[cntType] = 0
    def close(cursorSelf):
        cursorSelf.closedCount += 1
    def statementActions(cursorSelf, sql, statment):
        raise NotImplementedError("MockCursor subclass must implement this")
    def execute(*args):
        cursorSelf = args[0]
        sql = args[1]
        found = False
        for statement in cursorSelf.acceptedStatements:
            if sql[:len(statement)] == statement:
                cursorSelf.counts[statement] += 1
                cursorSelf.rowcount = 0
                found = True
                break
        cursorSelf.row = (None,)
        cursorSelf.testObject.failUnless(found, "Unknown sql statement: " + sql)
        cursorSelf.statementActions(sql, statement)
        return cursorSelf.rowcount
    def fetchone(cursorSelf): return cursorSelf.row

class MockDatabase:
    def __init__(dbSelf, cursorClass):
        class MockInternalDatabase:
            def literal(intDBSelf, *args): return args[0]
        dbSelf.db = MockInternalDatabase()
        dbSelf.cursorValue = cursorClass()
    def cursor(dbSelf): return dbSelf.cursorValue
    def literal(dbSelf, val): return dbSelf.db.literal(val)

class PokerServiceTestCaseBase(unittest.TestCase):

    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    # ----------------------------------------------------------------
    def setUp(self, settingsFile = settings_xml):
        testclock._seconds_reset()
        self.destroyDb()
        self.settings = settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settingsFile, len(settingsFile))
        settings.header = settings.doc.xpathNewContext()
        self.db = pokerdatabase.PokerDatabase(settings)
        self.service = pokerservice.PokerService(settings)
        self.default_money = 10000000
#        self.service.verbose = 0
#        self.service.verbose = 4

    # ----------------------------------------------------------------
    def tearDown(self):
        self.db.close()
        d = self.service.stopService()
        d.addCallback(lambda x: self.destroyDb())
        return d

    # ----------------------------------------------------------------
    def createUsers(self):
        cursor = self.db.cursor()
        for user_number in (1, 2, 3):
            cursor.execute("INSERT INTO users (name, password, created) VALUES ('user%d', 'password%d', 0)" % ( user_number, user_number ))
            self.assertEqual(1, cursor.rowcount)

        ( (self.user1_serial, name, privilege), message ) = self.service.auth("user1", "password1", "role1")
        ( (self.user2_serial, name, privilege), message ) = self.service.auth("user2", "password2", "role1")
        ( (self.user3_serial, name, privilege), message ) = self.service.auth("user3", "password3", "role1")

        for user_number in (self.user1_serial, self.user2_serial, self.user3_serial):
            if self.default_money > 0 and user_number == self.user3_serial:
                cursor.execute("INSERT INTO user2money (user_serial, currency_serial, amount) VALUES (%d, 2, %d)" % ( user_number, self.default_money ) )
                self.assertEqual(1, cursor.rowcount)

        cursor.close()

monitor_settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <listen tcp="19480" />

  <monitor>.././monitorplugin.py</monitor>
  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

class MonitorTestCase(unittest.TestCase):

    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    # ----------------------------------------------------------------
    def setUp(self):
        testclock._seconds_reset()
        self.destroyDb()
        settings = pokernetworkconfig.Config([])
        settings.loadFromString(monitor_settings_xml)
        self.db = pokerdatabase.PokerDatabase(settings)
        self.service = pokerservice.PokerService(settings)

    # ----------------------------------------------------------------
    def tearDown(self):
        self.db.close()
        d = self.service.stopService()
        d.addCallback(lambda x: self.destroyDb())
        return d

    # ----------------------------------------------------------------
    def test01_monitor(self):
        self.service.startService()
        test = self
        class Avatar:
            protocol = True
            def sendPacketVerbose(self, packet):
                test.assertEquals(PACKET_POKER_MONITOR_EVENT, packet.type)
                test.assertEquals(1, packet.event)
                test.assertEquals(2, packet.param1)
                test.assertEquals(3, packet.param2)
                self.sent = True
        avatar = Avatar()
        self.assertEquals(PACKET_ACK, self.service.monitor(avatar).type)
        self.service.databaseEvent(event = 1, param1 = 2, param2 = 3)
        self.failUnless(avatar.sent)
        self.failUnless(hasattr(self.service, 'HERE'))
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM monitor WHERE event = 1")
        self.assertEquals(1, cursor.rowcount)

class CleanUpTestCase(PokerServiceTestCaseBase):

    # ----------------------------------------------------------------
    def test01_cleanUp(self):
        self.service.startService()
        db = self.service.db
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (serial, name, password, created) VALUES (43, 'BOTAA', 'passwordAA', 0)")
        cursor.execute("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (43, 1, 200)")
        cursor.execute("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (44, 1, 200)")
        self.service.cleanUp('BOT')
        cursor.execute("SELECT COUNT(*) FROM users WHERE name like 'BOT%'")
        self.assertEqual(0, cursor.fetchone()[0])
        #
        # Bot removed from tourney
        #
        cursor.execute("SELECT COUNT(*) FROM user2tourney WHERE user_serial = 43")
        self.assertEqual(0, cursor.fetchone()[0])
        #
        # Non bot not removed from tourney
        #
        cursor.execute("SELECT COUNT(*) FROM user2tourney WHERE user_serial = 44")
        self.assertEqual(1, cursor.fetchone()[0])
        cursor.close()

list_table_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" remove_completed="1" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="NL HE 10-max 100/200" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="NL HE 6-max 100/200" variant="holdem" betting_structure="100-200-no-limit" seats="6" player_timeout="60" currency_serial="2" />
  <table name="Limit HE 10-max 2/4" variant="holdem" betting_structure="2-4-limit" seats="10" player_timeout="60" currency_serial="2" />
  <table name="Limit HE 6-max 2/4" variant="holdem" betting_structure="2-4-limit" seats="6" player_timeout="60" currency_serial="1" />
  <table name="Stud 8-max 2/4" variant="7stud" betting_structure="2-4-limit" seats="8" player_timeout="60" currency_serial="2" />

  <listen tcp="19480" />

  <language value="en_US.ISO-8859-1"/>

  <stats type="RankPercentile"/>

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

class ListTablesSearchTablesTestCases(PokerServiceTestCaseBase):
    def setUp(self):
        PokerServiceTestCaseBase.setUp(self, settingsFile = list_table_xml)
    # ----------------------------------------------------------------
    def test01_my(self):
        self.service.startService()
        db = self.service.db
        serial = 44
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE1))
        tables = self.service.listTables('my', serial)
        self.assertEqual(1, len(tables))
        self.assertEqual(tables[0]['serial'], TABLE1)
    # ----------------------------------------------------------------
    def test02_currency(self):
        self.service.startService()
        tables = self.service.listTables('50', 0)
        self.assertEqual(0, len(tables))
        tables = self.service.listTables('1', 0)
        self.assertEqual(2, len(tables))
        tables = self.service.listTables('2', 0)
        self.assertEqual(3, len(tables))
    # ----------------------------------------------------------------
    def test03_currency_and_variant(self):
        self.service.startService()
        tables = self.service.listTables('1\tfakevariant', 0)
        self.assertEqual(0, len(tables))
        tables = self.service.listTables('2\tfakevariant', 0)
        self.assertEqual(0, len(tables))
        tables = self.service.listTables('1\tholdem', 0)
        self.assertEqual(2, len(tables))
        tables = self.service.listTables('2\tholdem', 0)
        self.assertEqual(2, len(tables))
        tables = self.service.listTables('1\t7stud', 0)
        self.assertEqual(0, len(tables))
        tables = self.service.listTables('2\t7stud', 0)
        self.assertEqual(1, len(tables))
    # ----------------------------------------------------------------
    def test04_variant(self):
        self.service.startService()
        tables = self.service.listTables('\tfakevariant', 0)
        self.assertEqual(0, len(tables))
        tables = self.service.listTables('\tholdem', 0)
        self.assertEqual(4, len(tables))
        tables = self.service.listTables('\t7stud', 0)
        self.assertEqual(1, len(tables))
    # ----------------------------------------------------------------
    def test05_all(self):
        self.service.startService()
        tables = self.service.listTables('', 0)
        self.assertEqual(5, len(tables))
        tables = self.service.listTables('all', 0)
        self.assertEqual(5, len(tables))
    # ----------------------------------------------------------------
    def test06_name(self):
        self.service.startService()
        tables = self.service.listTables('fakename', 0)
        self.assertEqual(0, len(tables))
        for name in [ "NL HE 10-max 100/200", "NL HE 6-max 100/200",
                      "Limit HE 10-max 2/4", "Limit HE 6-max 2/4", "Stud 8-max 2/4" ]:
            tables = self.service.listTables(name, 0)
            self.assertEqual(1, len(tables))
    # ----------------------------------------------------------------
    def test07_currency_and_variant_and_bettingStructure(self):
        self.service.startService()
        tables = self.service.searchTables(1, 'fakevariant', 'fakebetting')
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(2, 'fakevariant', '2-4-limit')
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, 'fakevariant', '2-4-limit')
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, None, '2-4-limit')
        self.assertEqual(3, len(tables))
        tables = self.service.searchTables(None, None, '100-200-no-limit')
        self.assertEqual(2, len(tables))
        tables = self.service.searchTables(None, 'holdem', '100-200-no-limit')
        self.assertEqual(2, len(tables))
        tables = self.service.searchTables(None, 'holdem', '2-4-limit')
        self.assertEqual(2, len(tables))
        tables = self.service.searchTables(None, '7stud', '2-4-limit')
        self.assertEqual(1, len(tables))
        tables = self.service.searchTables(None, '7stud', '100-200-no-limit')
        self.assertEqual(0, len(tables))
    # ----------------------------------------------------------------
    def test08_currency_and_variant_and_bettingStructure_and_count_noOne(self):
        self.service.startService()
        tables = self.service.searchTables(1,'fakevariant', 'fakebetting', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(2, 'fakevariant', '2-4-limit', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, 'fakevariant', '2-4-limit', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, None, '2-4-limit', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, None, '100-200-no-limit', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, 'holdem', '100-200-no-limit', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, 'holdem', '2-4-limit', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, '7stud', '2-4-limit', 2)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(None, '7stud', '100-200-no-limit', 2)
        self.assertEqual(0, len(tables))
    # ----------------------------------------------------------------
    def test09_currency_and_variant_and_bettingStructure_and_count_withSome(self):
        self.service.startService()
        clear_all_messages()
        nlHe100Currency1 = 1
        nlHe100Currency2 = 2
        limitHE24Currency2 = 3
        limitHE24Currency1 = 4
        stud24Currency2 = 5

        insertSql = "UPDATE pokertables SET players = %d WHERE serial = %d"
        db = self.service.db

        db.db.query(insertSql % (2, limitHE24Currency1))
        db.db.query(insertSql % (2, limitHE24Currency2))
        db.db.query(insertSql % (1, stud24Currency2))

        tables = self.service.searchTables(None, None, None, 0)
        self.assertEqual(5, len(tables))
        tables = self.service.searchTables(None, None, '2-4-limit', 0)
        self.assertEqual(3, len(tables))

        tables = self.service.searchTables(None, None, '2-4-limit', 1)
        self.assertEqual(3, len(tables), "searchTables() should return 3 for 2-4-limit w/ <= 1 player")
        tables = self.service.searchTables(None, None, None, 1)
        self.assertEqual(3, len(tables), "searchTables() query should return 3 for <= 1 player")

        tables = self.service.searchTables(None, None, '2-4-limit', 2)
        self.assertEqual(2, len(tables))
        tables = self.service.searchTables(None, None, None, 2)
        self.assertEqual(2, len(tables))

        for ii in [ 3, 4, 5, 6 ]:
            tables = self.service.searchTables(None, None, '2-4-limit', ii)
            self.assertEqual(0, len(tables))
            tables = self.service.searchTables(None, None, None, ii)
            self.assertEqual(0, len(tables))

        tables = self.service.searchTables(None, 'holdem', None, 0)
        self.assertEqual(4, len(tables))
        tables = self.service.searchTables(None, 'holdem', '2-4-limit', 0)
        self.assertEqual(2, len(tables))

        for ii in [ 1, 2 ]:
            tables = self.service.searchTables(None, 'holdem', '2-4-limit', ii)
            self.assertEqual(2, len(tables), "holdem 2-4-limit <= %d players should be 2" % ii)
            tables = self.service.searchTables(None, 'holdem', None, ii)
            self.assertEqual(2, len(tables), "holdem <= %d players should be 2" % ii)

        for ii in [ 3, 4, 5, 6 ]:
            tables = self.service.searchTables(None, 'holdem', '2-4-limit', ii)
            self.assertEqual(0, len(tables))
            tables = self.service.searchTables(None, 'holdem', None, ii)
            self.assertEqual(0, len(tables))

        # The 100-200 NL tables have no one initially, check that, then
        # add two players to each, checking that now a search for at least
        # two works.

        for query in [ '\t\t100-200-no-limit\t0',  '\tholdem\t100-200-no-limit\t0']:
            tables = self.service.searchTables(None, None, '100-200-no-limit', 0)
            self.assertEqual(2, len(tables), "100-200-no-limit should be 2")
            tables = self.service.searchTables(None, 'holdem', '100-200-no-limit', 0)
            self.assertEqual(2, len(tables), "100-200-no-limit w/ holdem should be 2")

        for ii in [ 1, 2, 3, 4, 5, 6]:
            for query in [ '\t\t100-200-no-limit\t%d',  '\tholdem\t100-200-no-limit\t%d']:
                tables = self.service.searchTables(None, None, '100-200-no-limit', ii)
                self.assertEqual(0, len(tables))
                tables = self.service.searchTables(None, 'holdem', '100-200-no-limit', ii)
                self.assertEqual(0, len(tables))

        db.db.query(insertSql % (3, nlHe100Currency1))
        db.db.query(insertSql % (2, nlHe100Currency2))

        for ii in [ 0, 1, 2 ]:
            for query in  [ '\t\t100-200-no-limit\t%d', '\tholdem\t100-200-no-limit\t%d']:
                for variant in [ None, 'holdem' ]:
                    tables = self.service.searchTables(None, variant, '100-200-no-limit', ii)
                    self.assertEqual(2, len(tables))

        for variant in [ None, 'holdem' ]:
            tables = self.service.searchTables(None, variant, '100-200-no-limit', 3)
            self.assertEqual(1, len(tables))

        for ii in [ 4, 5, 6 ]:
            for variant in [ None, 'holdem' ]:
                tables = self.service.searchTables(None, variant, '100-200-no-limit', ii)
                self.assertEqual(0, len(tables))

        # Now we have a variety of holdem tables, so we can search for
        # holdem user counts without a betting_structure.  There should be
        # four holdem tables with at least 2 people, and one holdem table
        # with at least 3 people.

        for ii in [ 0, 1, 2 ]:
            tables = self.service.searchTables(None, 'holdem', None, ii)
            self.assertEqual(4, len(tables),
              "searchTables() query: holdem w/ players <= %d yields %d not 4" % (ii, len(tables)))

        tables = self.service.searchTables(None, 'holdem', None, 3)
        self.assertEqual(1, len(tables))

        for ii in [ 4, 5, 6 ]:
            tables = self.service.searchTables(None, 'holdem', None, ii)
            self.assertEqual(0, len(tables))

        # Stud only has one player, check that, then add one and see result change.
        tables = self.service.searchTables(None, '7stud', '2-4-limit', 2)
        self.assertEqual(0, len(tables))
        db.db.query(insertSql % (2, stud24Currency2))
        tables = self.service.searchTables(None, '7stud', '2-4-limit', 2)
        self.assertEqual(1, len(tables))

        # Tests with currency serial tests in place

        tables = self.service.searchTables(1, None, None, 0)
        self.assertEqual(2, len(tables), "search for currency_serial 1 yields %d not 4"
                         % len(tables))
        for ii in [ 0, 1, 2 ]:
            tables = self.service.searchTables(1, None, None, ii)
            self.assertEqual(2, len(tables))
            tables = self.service.searchTables(1, 'holdem', None, ii)
            self.assertEqual(2, len(tables))
            tables = self.service.searchTables(1, 'holdem', '100-200-no-limit', ii)
            self.assertEqual(1, len(tables))
            tables = self.service.searchTables(1, 'holdem', '2-4-limit', ii)
            self.assertEqual(1, len(tables))
            tables = self.service.searchTables(1, None, '2-4-limit', ii)
            self.assertEqual(1, len(tables))
            tables = self.service.searchTables(1, '7stud', None, ii)
            self.assertEqual(0, len(tables))
            tables = self.service.searchTables(1, '7stud', '2-4-limit', ii)
            self.assertEqual(0, len(tables))

        tables = self.service.searchTables(2, None, None, 0)
        self.assertEqual(3, len(tables))
        for ii in [ 0, 1, 2 ]:
            tables = self.service.searchTables(2, None, None, ii)
            self.assertEqual(3, len(tables))
            tables = self.service.searchTables(2, 'holdem', None, ii)
            self.assertEqual(2, len(tables))
            tables = self.service.searchTables(2, 'holdem', '100-200-no-limit', ii)
            self.assertEqual(1, len(tables))
            tables = self.service.searchTables(2, 'holdem', '2-4-limit', ii)
            self.assertEqual(1, len(tables))
            tables = self.service.searchTables(2, None, '2-4-limit', ii)
            self.assertEqual(2, len(tables))
            tables = self.service.searchTables(2, '7stud', None, ii)
            self.assertEqual(1, len(tables))
            tables = self.service.searchTables(2, '7stud', '2-4-limit', ii)
            self.assertEqual(1, len(tables))

        # The threes are different: all currency two queries with holdem
        # don't have three.  Also, all stud queries on currency 1 have no one, because
        # there are no currency 1 stud tables.
        tables = self.service.searchTables(2, None, None, 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(2, 'holdem', None, 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(2, 'holdem', '100-200-no-limit', 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(2, 'holdem', '2-4-limit', 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(2, None, '2-4-limit', 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(1, '7stud', None, 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(1, '7stud', '2-4-limit', 3)
        self.assertEqual(0, len(tables))

        tables = self.service.searchTables(1, None, None, 3)
        self.assertEqual(1, len(tables), "searchTables() query: yields %d not 1" % len(tables))
        tables = self.service.searchTables(1, 'holdem', None, 3)
        self.assertEqual(1, len(tables), "searchTables() query: yields %d not 1" % len(tables))
        tables = self.service.searchTables(1, 'holdem', '100-200-no-limit', 3)
        self.assertEqual(1, len(tables), "searchTables() query: yields %d not 1" % len(tables))

        # The rest have zero
        tables = self.service.searchTables(1, 'holdem', '2-4-limit', 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(1, None, '2-4-limit', 3)
        self.assertEqual(0, len(tables))
        tables = self.service.searchTables(1, '7stud', None, 3)
        self.assertEqual(0, len(tables))

        # Finally, no query beyond 3 users should be anything but zero.
        for ii in [ 4, 5, 6 ]:
            for currencySerial in [ 1, 2, None ]:
                for variant in [ None, 'holdem', '7stud', '' ]:
                    for betting in [ None, '', '2-4-limit', '100-200-no-limit' ]:
                        tables = self.service.searchTables(currencySerial, variant, betting, ii)
                        self.assertEqual(0, len(tables))
        self.assertEquals(get_messages(), [])
    # ----------------------------------------------------------------
    def test10_tooMany(self):
        self.service.startService()

        clear_all_messages()
        tables = self.service.listTables('\tholdem\t', 0)
        self.assertEqual(4, len(tables))
        self.assertEquals(get_messages(), ["*ERROR* Following listTables() criteria string has more parameters than expected, ignoring third one and beyond in: \tholdem\t"])
    # ----------------------------------------------------------------
    def test11_currencySerialIsNotAnInteger(self):
        self.service.startService()

        clear_all_messages()
        tables = self.service.listTables("hithere\t", 0)
        self.assertEqual(0, len(tables))
        self.assertEquals(get_messages(), ["*ERROR* listTables(): currency_serial parameter must be an integer, instead was: hithere"])
    # ----------------------------------------------------------------
    def test13_emptyArgsShouldGenerateSameAsSelectAll(self):
        self.service.startService()

        clear_all_messages()
        tables = self.service.listTables("all", 0)
        allSelectCount = len(tables)
        self.assertEquals(allSelectCount, 5)
        self.assertEquals(get_messages(), [])

        clear_all_messages()
        tables = self.service.listTables("\t", 0)
        self.assertEqual(allSelectCount, len(tables))
        self.assertEquals(get_messages(), [])
    # ----------------------------------------------------------------
    def test14_sqlInjectionInParametersShouldNotWork(self):
        self.service.startService()

        clear_all_messages()
        tables = self.service.listTables("\tholdem'; DELETE from pokertables WHERE variant = 'holdem", 0)
        self.assertEqual(0, len(tables))
        self.assertEquals(get_messages(), [])

        clear_all_messages()
        tables = self.service.listTables("\tholdem", 0)
        self.assertEqual(4, len(tables))
        self.assertEquals(get_messages(), [])
###############################################################################
# Much of GetTableByCriteriaTestCase() is testing the algorithm defined in
# getTableBestByCriteria()

class MockPlayerForCriteria:
    def __init__(self, sittingIn = True):
        self.sittingIn = sittingIn
    def isSit(self): return self.sittingIn

class GetTableBestByCriteriaTestCase(PokerServiceTestCaseBase):
    def setUp(self):
        PokerServiceTestCaseBase.setUp(self, settingsFile = list_table_xml)
        self.service.startService()
    # ----------------------------------------------------------------
    def giveUserMoney(self, userSerial, currencySerial, amount):
        """Note: only call this after service is started in the test."""
        db = self.service.db

        insertSql = "INSERT INTO user2money(amount, user_serial, currency_serial) VALUES(%s, %d, %d)"
        db.db.query(insertSql % (str(amount), userSerial, currencySerial))
    # ----------------------------------------------------------------
    def test00_nothingReturnedDueToNoTableMatchingString(self):
        self.giveUserMoney(22, 2, 100000)
        self.giveUserMoney(22, 3, 100000)
        self.giveUserMoney(22, 1, 100000)

        # There are no tables that take currency 3.
        self.assertEquals(self.service.getTableBestByCriteria(22, 3), None)
    # ----------------------------------------------------------------
    def test01_nothingReturnedDueToNotEnoughMoney(self):
        self.giveUserMoney(22, 1, 999)
        self.giveUserMoney(22, 2, 999)

        self.assertEquals(self.service.getTableBestByCriteria(22, 1), None)
        self.assertEquals(self.service.getTableBestByCriteria(22, 2), None)
    # ----------------------------------------------------------------
    def test02_onlySubSetPossibleDueToLimitedFunds(self):
        from pokernetwork.pokertable import PokerTable

        self.giveUserMoney(22, 1, 5000)
        self.giveUserMoney(22, 2, 5000)

        tableCurrency1 = self.service.getTableBestByCriteria(22, 1)
        tableCurrency2 = self.service.getTableBestByCriteria(22, 2)

        self.failUnless(isinstance(tableCurrency1, PokerTable))
        self.failUnless(isinstance(tableCurrency2, PokerTable))

        self.assertEquals(tableCurrency1.game.id, 4)
        self.failUnless(tableCurrency2.game.id in [ 3, 5 ])
    # ----------------------------------------------------------------
    def test03_manyChoicesDueToWealth(self):
        from pokernetwork.pokertable import PokerTable

        self.giveUserMoney(22, 1, 200000)
        self.giveUserMoney(22, 2, 200000)

        tableCurrency1 = self.service.getTableBestByCriteria(22, 1)
        tableCurrency2 = self.service.getTableBestByCriteria(22, 2)

        self.failUnless(isinstance(tableCurrency1, PokerTable))
        self.failUnless(isinstance(tableCurrency2, PokerTable))

        self.failUnless(tableCurrency1.game.id in [ 1, 4 ])
        self.failUnless(tableCurrency2.game.id in [ 2, 3, 5 ])
    # ----------------------------------------------------------------
    def test04_nothingFoundDueToFullness(self):
        self.giveUserMoney(22, 1, 1000)

        # Mock up full table.
        table = self.service.getTable(4)
        for ii in range(table.game.max_players):
            table.game.serial2player[ii] = MockPlayerForCriteria()

        self.assertEquals(self.service.getTableBestByCriteria(22, 1), None)
    # ----------------------------------------------------------------
    def test05_noneDueToAskingForPlayers(self):
        self.giveUserMoney(22, 1, 200000)

        self.assertEquals(self.service.getTableBestByCriteria(22, 1, min_players = 3), None)
    # ----------------------------------------------------------------
    def test06_oneSpecificDueToPlayerSittingOut(self):
        self.giveUserMoney(99, 1, 200000)

        nlHe100Currency1 = 1
        limitHE24Currency1 = 4

        # Note to properly mock up players at the table, you have to both
        # fill the DB properly and set the game object correctly

        insertSql = "UPDATE pokertables SET players = %d WHERE serial = %d"
        db = self.service.db
        db.db.query(insertSql % (3, limitHE24Currency1))
        db.db.query(insertSql % (3, nlHe100Currency1))

        for ii in range(3):
            table = self.service.getTable(limitHE24Currency1)
            table.game.serial2player[ii] = MockPlayerForCriteria()
            table = self.service.getTable(nlHe100Currency1)
            table.game.serial2player[ii] = MockPlayerForCriteria(ii != 0)

        from pokernetwork.pokertable import PokerTable

        foundTable = self.service.getTableBestByCriteria(99, 1, min_players = 3)

        self.failUnless(isinstance(foundTable, PokerTable))

        self.assertEquals(foundTable.game.id, limitHE24Currency1)
    # ----------------------------------------------------------------
    def test07_noneDueToSittingOut(self):
        self.giveUserMoney(99, 1, 200000)

        nlHe100Currency1 = 1
        limitHE24Currency1 = 4

        # Note to properly mock up players at the table, you have to both
        # fill the DB properly and set the game object correctly

        insertSql = "UPDATE pokertables SET players = %d WHERE serial = %d"
        db = self.service.db
        db.db.query(insertSql % (3, limitHE24Currency1))
        db.db.query(insertSql % (3, nlHe100Currency1))

        for ii in range(3):
            table = self.service.getTable(limitHE24Currency1)
            table.game.serial2player[ii] = MockPlayerForCriteria(ii != 1)
            table = self.service.getTable(nlHe100Currency1)
            table.game.serial2player[ii] = MockPlayerForCriteria(ii != 0)

        from pokernetwork.pokertable import PokerTable

        foundTable = self.service.getTableBestByCriteria(99, 1, min_players = 3)

        self.assertEquals(foundTable, None)
#####################################################################
class TourneySelectTestCase(PokerServiceTestCaseBase):

    def test00_all(self):
        self.service.startService()
        tourneys = self.service.tourneySelect('')
        self.assertEqual(2, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual('regular1', tourneys[1]['name'])

    def test01_sit_n_go(self):
        self.service.startService()
        tourneys = self.service.tourneySelect('\tsit_n_go')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])

    def test02_regular(self):
        self.service.startService()
        tourneys = self.service.tourneySelect('\tregular')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('regular1', tourneys[0]['name'])

    def test02_currency_serial(self):
        self.service.startService()
        tourneys = self.service.tourneySelect('1\tregular')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('regular1', tourneys[0]['name'])
        tourneys = self.service.tourneySelect('44\tregular')
        self.assertEqual(0, len(tourneys))

    def test03_name(self):
        self.service.startService()
        tourneys = self.service.tourneySelect('regular1')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('regular1', tourneys[0]['name'])

    def test04_registered(self):
        self.service.startService()
        self.createUsers()
        (heads_up,) = filter(lambda tourney: tourney.name == 'sitngo2', self.service.tourneys.values())
        tourneys = self.service.tourneySelect('')
        self.assertEqual(2, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(0, tourneys[0]['registered'])
        tourneys = self.service.tourneySelect('sitngo2')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(0, tourneys[0]['registered'])
        tourneys = self.service.tourneySelect('\tsit_n_go')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(0, tourneys[0]['registered'])
        tourneys = self.service.tourneySelect('1\tsit_n_go')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(0, tourneys[0]['registered'])
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user2_serial,
                                                                game_id = heads_up.serial))
        tourneys = self.service.tourneySelect('')
        self.assertEqual(2, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(1, tourneys[0]['registered'])
        tourneys = self.service.tourneySelect('sitngo2')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(1, tourneys[0]['registered'])
        tourneys = self.service.tourneySelect('\tsit_n_go')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(1, tourneys[0]['registered'])
        tourneys = self.service.tourneySelect('1\tsit_n_go')
        self.assertEqual(1, len(tourneys))
        self.assertEqual('sitngo2', tourneys[0]['name'])
        self.assertEqual(heads_up.serial, tourneys[0]['serial'])
        self.assertEqual(1, tourneys[0]['registered'])

    def test04_with_old_completed(self):
        self.service.startService()
        self.createUsers()
        tourneys = self.service.tourneySelect('')
        self.assertEquals(len(tourneys),2)
        db = self.service.db
        db.db.query("UPDATE tourneys SET finish_time = UNIX_TIMESTAMP(NOW() - INTERVAL 2 HOUR), state = 'complete' WHERE name = 'regular1'")
        self.assertEquals(self.service.remove_completed, 1)
        tourneys = self.service.tourneySelect('')
        self.assertEquals(len(tourneys),1)
        self.assertEquals(tourneys[0]["name"], "sitngo2")

class PlayerPlacesTestCase(PokerServiceTestCaseBase):

    def test00_not_anywhere(self):
        self.service.startService()
        serial = 888
        places = self.service.getPlayerPlaces(serial)
        self.assertEqual(0, len(places.tables))
        self.assertEqual(0, len(places.tourneys))
        self.assertEqual(serial, places.serial)

    def test01_tables_and_tourneys(self):
        self.service.startService()
        db = self.service.db
        serial = 888
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE1))
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE2))
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE3))
        tourney_serial = 999
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial, 'registering'))
        places = self.service.getPlayerPlaces(serial)
        self.assertEqual([TABLE1, TABLE2, TABLE3], places.tables)
        self.assertEqual([tourney_serial], places.tourneys)
        self.assertEqual(serial, places.serial)

    def test02_tables_and_tourneys_by_name(self):
        self.service.startService()
        db = self.service.db
        serial = 888
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE1))
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE2))
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE3))
        tourney_serial = 999
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial, 'registering'))
        name = 'testuser'
        db.db.query("INSERT INTO users (serial, name) VALUES (%d, '%s')" % (serial, name))
        places = self.service.getPlayerPlacesByName(name)
        self.assertEqual([TABLE1, TABLE2, TABLE3], places.tables)
        self.assertEqual([tourney_serial], places.tourneys)
        self.assertEqual(serial, places.serial)

    def test02_tables_and_tourneys_by_name_error(self):
        self.service.startService()
        db = self.service.db
        serial = 888
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE1))
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE2))
        db.db.query("INSERT INTO user2table (user_serial, table_serial) VALUES (%d, %d)" % (serial, TABLE3))
        tourney_serial = 999
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial))
        name = 'testuser1'
        db.db.query("INSERT INTO users (serial, name) VALUES (%d, '%s')" % (serial, name))
        result = self.service.getPlayerPlacesByName('testuser2')
        self.assertEqual(PACKET_POKER_PLAYER_PLACES, result.other_type)

    def test03_list_tourneys_in_registering_running_break_break_wait_state(self):
        self.service.startService()
        db = self.service.db
        serial = 888
        tourney_serial = 999
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial+1))
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial+2))
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial+3))
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial+4))
        db.db.query("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, %d)" % (serial, tourney_serial+5))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial, 'announced'))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial+1, 'registering'))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial+2, 'running'))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial+3, 'breakwait'))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial+4, 'break'))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial+5, 'complete'))
        db.db.query("INSERT INTO tourneys (serial, state) VALUES (%d, '%s')" % (tourney_serial+6, 'canceled'))
        places = self.service.getPlayerPlaces(serial)
        self.assertEqual([], places.tables)
        self.assertEqual([tourney_serial+1, tourney_serial+2, tourney_serial+3, tourney_serial+4], places.tourneys)
        self.assertEqual(serial, places.serial)

class ResthostTestCase(unittest.TestCase):

    xml_with_resthost = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19480" />

  <resthost host="HOST" port="7777" path="/PATH" />
  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

    xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19480" />

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

    xml_with_resthost_name = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19480" />

  <resthost host="HOST" port="7777" path="/PATH" name="explain1" />
  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    def setUp(self):
        self.destroyDb()

    def setUpService(self, xml):
        settings = pokernetworkconfig.Config([])
        settings.loadFromString(xml)
        self.service = pokerservice.PokerService(settings)

    def tearDown(self):
        d = self.service.stopService()
        d.addCallback(lambda x: self.destroyDb())
        return d

    def test00_init(self):
        """ setupResthost twice with the same information gives the same serial """
        self.setUpService(self.xml_with_resthost)
        self.service.startService()
        self.assertEqual(1, self.service.resthost_serial)
        self.service.resthost_serial = 0
        self.service.setupResthost()
        self.assertEqual(1, self.service.resthost_serial)
        db = self.service.db
        cursor = db.cursor()
        cursor.execute("SELECT * FROM resthost WHERE serial = 1")
        self.assertEqual(1, cursor.rowcount)
        (serial,name,host,port,path) = cursor.fetchone()
        self.assertEqual(1, serial)
        self.assertEqual('HOST', host)
        self.assertEqual(7777, port)
        self.assertEqual('/PATH', path)
        self.assertEqual(None, name)

    def test001_init_with_name(self):
        """ setupResthost with name """
        self.setUpService(self.xml_with_resthost_name)
        self.service.startService()
        db = self.service.db
        cursor = db.cursor()
        cursor.execute("SELECT * FROM resthost WHERE serial = 1")
        self.assertEqual(1, cursor.rowcount)
        (serial,name,host,port,path) = cursor.fetchone()
        self.assertEqual(1, serial)
        self.assertEqual('HOST', host)
        self.assertEqual(7777, port)
        self.assertEqual('/PATH', path)
        self.assertEqual('explain1', name)

    def test01_packet2resthost(self):
        self.setUpService(self.xml_with_resthost)
        self.service.startService()

        db = self.service.db
        db.db.query("INSERT INTO resthost VALUES (2, 'two', 'host2', 2222, 'path2')")
        db.db.query("INSERT INTO route VALUES (102, 0, 0, 2)")

        #
        # ping is never routed
        #
        resthost, game_id = self.service.packet2resthost(PacketPing())
        self.assertEqual(None, resthost)
        self.assertEqual(None, game_id)
        #
        # packet with a valid game_id is routed if resthost is != from server
        #
        resthost, game_id = self.service.packet2resthost(PacketPokerCheck(game_id = 102))
        self.assertEqual('host2', resthost[0])
        self.assertEqual(102, game_id)
        #
        # packet is not routed if resthost point to the same server
        #
        resthost, game_id = self.service.packet2resthost(PacketPokerCheck(game_id = 1))
        self.assertEqual(None, resthost)
        self.assertEqual(1, game_id)
        #
        # packet with an unknown game_id is not routed
        #
        resthost, game_id = self.service.packet2resthost(PacketPokerCheck(game_id = 888))
        self.assertEqual(None, resthost)
        self.assertEqual(888, game_id)
        #
        # packet to a tourney is routed if resthost is != from server
        #
        db = self.service.db
        db.db.query("INSERT INTO route VALUES (0, 484, 1, 2)")
        resthost, game_id = self.service.packet2resthost(PacketPokerGetTourneyManager(tourney_serial = 484))
        self.assertEqual('host2', resthost[0])
        #
        # packet to a tourney is routed if resthost is != from server
        #
        resthost, game_id = self.service.packet2resthost(PacketPokerTourneyRegister(game_id = 484))
        self.assertEqual('host2', resthost[0])
        #
        # packet to a tourney table is routed if resthost is != from server
        #
        db.db.query("INSERT INTO route VALUES (232, 484, 1, 2)")
        resthost, game_id = self.service.packet2resthost(PacketPokerCheck(game_id = 232))
        self.assertEqual('host2', resthost[0])
        self.assertEqual(232, game_id)
        #
        # packet to an unknown tourney_serial is not routed
        #
        resthost, game_id = self.service.packet2resthost(PacketPokerGetTourneyManager(tourney_serial = 999))
        self.assertEqual(None, resthost)
        #
        # packet to an unknown tourney_serial is not routed
        #
        resthost, game_id = self.service.packet2resthost(PacketPokerTourneyRegister(game_id = 999))
        self.assertEqual(None, resthost)

    def test02_packet2resthost_createTourney(self):
        self.setUpService(self.xml)
        self.service.startService()
        resthost, game_id = self.service.packet2resthost(PacketPokerCreateTourney())
        self.failIf(resthost)
        self.failIf(game_id)
        db = self.service.db
        db.db.query("INSERT INTO resthost VALUES (10, 'one', 'host1', 1, 'path1')")
        db.db.query("INSERT INTO route VALUES (0, 100, 0, 10)")
        db.db.query("INSERT INTO route VALUES (0, 200, 0, 10)")
        db.db.query("INSERT INTO resthost VALUES (20, 'two', 'host2', 2, 'path2')")
        db.db.query("INSERT INTO route VALUES (0, 300, 0, 20)")
        resthost, game_id = self.service.packet2resthost(PacketPokerCreateTourney())
        self.assertEqual('host2', resthost[0])
        self.assertEqual(None, game_id)

class PokerServiceTestCase(PokerServiceTestCaseBase):

    # ----------------------------------------------------------------
    def configValues(self, settings_data, joined_max, missed_round_max=10, delaysValue=-1, queuedPacketMax = 500):
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_data, len(settings_data))
        settings.header = settings.doc.xpathNewContext()
        self.service = pokerservice.PokerService(settings)

        for (key, value) in ( ('position', '60'), ('autodeal', '18'),
                              ('showdown', '30'), ('round', '12'), ('finish', '18')):
            self.assertEquals(self.service.delays[key], value)
        for (key, value) in ( ('serial', '1'), ('amount', '10000000')):
            self.assertEquals(self.service.refill[key], value)

        self.assertEquals(self.service.verbose, 6)

        self.assertEquals(joined_max, self.service.joined_max)
        self.assertEquals(missed_round_max, self.service.missed_round_max)
        self.assertEquals(missed_round_max, self.service.getMissedRoundMax())
        self.assertEquals(queuedPacketMax, self.service.client_queued_packet_max)
        self.assertEquals(queuedPacketMax, self.service.getClientQueuedPacketMax())

        startedOnlyVars = [ ('joined_count', 0),
                            ('tables', 2), ('tourney_table_serial', 1),
                            ('shutting_down', False), ('avatars', []),
                            ('avatar_collection', PokerAvatarCollection()), ('simultaneous', 4),
                            ('monitors', []), ('gettextFuncs', 17) ]
        for (instanceVar, val) in startedOnlyVars:
            self.assertEquals(self.service.__dict__.has_key(instanceVar), False)

        clear_all_messages()
        self.service.startService()
        self.failUnless(search_output('*ERROR* Unable to find codeset string in language value: this_locale_does_not_exist'))
        self.failUnless(search_output("*ERROR* No translation for language this_locale_does_not_exist for this_locale_does_not_exist in poker-engine; locale ignored: [Errno 2] No translation file found for domain: 'poker-engine'"))
        self.failUnless(search_output('*ERROR* Translation setup for this_locale_does_not_exist failed.  Strings for clients requesting this_locale_does_not_exist will likely always be in English'))
        for (instanceVar, val) in startedOnlyVars:
            self.assertEquals(self.service.__dict__.has_key(instanceVar), True)
            if instanceVar == "tables":
                self.assertEquals(len(self.service.__dict__[instanceVar]), val)

        for ii in ('this_locale_does_not_exist', 'en_US.ISO-8859-1', 'fr_FR.ISO-8859-1'):
            self.assertEquals(self.service.gettextFuncs.has_key(ii), True)
            self.assertEquals(callable(self.service.locale2translationFunc(ii)), True)
        for ii in ('this_locale_does_not_exist', 'en_US.ISO-8859-1'):
            self.assertEquals(self.service.gettextFuncs[ii]("Aces"), "Aces")
        self.assertEquals(self.service.gettextFuncs['fr_FR.ISO-8859-1']("Aces"), "d'As")

        for ii in ('nothing', 'unknown'):
            self.assertEquals(self.service.locale2translationFunc(ii), None)

        # If delaysValue is negative, that means in the context of this
        # test that we want to assume they weren't given in the settings
        # file and therefore service.delays() should not have them as keys.

        for str in ('extra_wait_tourney_break', 'extra_wait_tourney_start', 'extra_wait_tourney_finish'):
            if delaysValue < 0:
                self.assertEquals(self.service.delays.has_key(str), False)
            else:
                self.assertEquals(int(self.service.delays[str]), delaysValue)

    def test00_01_configValues(self):
        self.configValues(settings_xml, 1000)

    def test00_02_configValues(self):
        self.configValues(settings_xml.replace('max_joined="1000"', ""), 4000)

    def test00_03_configValues(self):
        self.configValues(settings_xml.replace('max_joined="1000"',
                                               'max_missed_round="5" max_queued_client_packets="100"'),
                          4000, 5, queuedPacketMax=100)

    def test00_4_badLocaleObject(self):
        """test00_4_badLocaleObject
        Check the case where the imported locale object's setlocal
        function does not work and causes errors in configuration."""

        def badSetLocale(a, b):
            raise locale.Error("testing bad setlocale")

        myLocale = locale.getlocale(locale.LC_ALL)
        saveLocale = locale.setlocale
        locale.setlocale = badSetLocale

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.service = pokerservice.PokerService(settings)
        clear_all_messages()
        self.service.startService()
        self.assertEquals(len(self.service.gettextFuncs), 17)
        self.failUnless(search_output('*ERROR* Unable to find codeset string in language value: this_locale_does_not_exist'))
        self.failUnless(search_output("*ERROR* No translation for language this_locale_does_not_exist for this_locale_does_not_exist in poker-engine; locale ignored: [Errno 2] No translation file found for domain: 'poker-engine'"))
        for ii in ('en_US.ISO-8859-1', 'fr_FR.ISO-8859-1'):
            self.assertEquals(self.service.gettextFuncs.has_key(ii), True)
        self.assertEquals(self.service.gettextFuncs['en_US.ISO-8859-1']("Aces"), "Aces")
        self.assertEquals(self.service.gettextFuncs['fr_FR.ISO-8859-1']("Aces"), "d'As")
        self.assertEquals(search_output("*ERROR* Unable to restore original locale: testing bad setlocale"), True)
        locale.setlocale = saveLocale

    def test00_05_configValues(self):
        self.configValues(settings_xml.replace('delays',
                                               'delays extra_wait_tourney_break="60" extra_wait_tourney_start="60" extra_wait_tourney_finish="60"'), 1000, delaysValue=60)

    def test00_12_badEncoding(self):
        """test00_12_badEncoding
        Check the case where an error occurs due to an encoding requested
        for a config language value has an unknown encoding."""

        new_settings_xml = settings_xml.replace('<language value="fr_FR.ISO-8859-1"/>',
                                                '<language value="fr_FR.MAGIC-PIXIE-DUST"/>')

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(new_settings_xml, len(new_settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.service = pokerservice.PokerService(settings)
        clear_all_messages()
        self.service.startService()
        self.assertEquals(len(self.service.gettextFuncs), 17)
        self.failUnless(search_output('*ERROR* Unsupported codeset MAGIC-PIXIE-DUST for fr_FR.MAGIC-PIXIE-DUST in poker-engine; locale ignored: unknown encoding: MAGIC-PIXIE-DUST'))
        self.failUnless(search_output('*ERROR* Unable to find codeset string in language value: this_locale_does_not_exist'))
        self.failUnless(search_output("*ERROR* No translation for language this_locale_does_not_exist for this_locale_does_not_exist in poker-engine; locale ignored: [Errno 2] No translation file found for domain: 'poker-engine'"))
        for ii in ('en_US.ISO-8859-1', 'fr_FR.MAGIC-PIXIE-DUST'):
            self.assertEquals(self.service.gettextFuncs.has_key(ii), True)
            self.assertEquals(self.service.gettextFuncs[ii]("Aces"), "Aces")

    def test00_13_anotherBadEncoding(self):
        """test00_13_anotherBadEncoding
        Check the case where an error occurs due to an encoding requested
        for a config language value has an unknown encoding."""

        new_settings_xml = settings_xml.replace('<language value="fr_FR.ISO-8859-1"/>',
                                                '<language value=".MAGIC-PIXIE-DUST"/>')

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(new_settings_xml, len(new_settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.service = pokerservice.PokerService(settings)
        clear_all_messages()
        self.service.startService()
        self.assertEquals(len(self.service.gettextFuncs), 17)
        self.failUnless(search_output('*ERROR* Unable to find codeset string in language value: .MAGIC-PIXIE-DUST'))
        self.failUnless(search_output("*ERROR* No translation for language .MAGIC-PIXIE-DUST for .MAGIC-PIXIE-DUST in poker-engine; locale ignored: [Errno 2] No translation file found for domain: 'poker-engine'"))
        for ii in ('en_US.ISO-8859-1', '.MAGIC-PIXIE-DUST'):
            self.assertEquals(self.service.gettextFuncs.has_key(ii), True)
            self.assertEquals(self.service.gettextFuncs[ii]("Aces"), "Aces")

    def test00_14_languageEmptyStringForSeperate(self):
        """test00_14_languageEmptyString
        Check the case where an error occurs due to a language being the empty string."""

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.service = pokerservice.PokerService(settings)
        clear_all_messages()
        self.service.startService()
        self.service._separateCodesetFromLocale('')
        msgs = get_messages()[-2:]
        self.assertEquals(msgs, ['*ERROR* Unable to find codeset string in language value: ', '*ERROR* Unable to find locale string in language value: '])
    # ----------------------------------------------------------------
    def test01_auth(self):
        self.service.startService()
        ( (serial, name, privilege), message ) = self.service.auth("user1", "password1", "role1")
        self.assertEquals(None, message)
        self.assertEquals(4, serial)
        self.assertEquals("user1", name)
        self.assertEquals(user.User.REGULAR, privilege)

    # ----------------------------------------------------------------
    def test01_auth_invalid_login(self):
        self.service.startService()
        self.service.poker_auth.auto_create_account = False
        ( status, message ) = self.service.auth("user1", "password1", sets.Set("role1"))
        self.assertEquals("Invalid login or password", message)
        self.assertEquals(False, status)

    # ----------------------------------------------------------------
    def test01_auth_already_logged(self):
        class Client:
            def __init__(self):
                self.roles = sets.Set('role1')
            def getName(self):
                return "user1"

        self.service.startService()
        ( (serial, name, privilege), message ) = self.service.auth("user1", "password1", sets.Set('role1'))
        self.service.avatar_collection.add(serial, Client())
        ( (serial, name, privilege), message ) = self.service.auth("user1", "password1", sets.Set('role1'))
        self.assertEquals(None, message)
        self.assertEquals("user1", name)

    # ----------------------------------------------------------------
    def cashIn(self):

        cursor = self.db.cursor()
        cursor.execute("INSERT INTO user2money (user_serial, currency_serial, amount, points, rake) VALUES (%d, 1, 100, 0, 0)" % ( self.user1_serial, ))
        cursor.execute("INSERT INTO user2money (user_serial, currency_serial, amount, points, rake) VALUES (%d, 1, 100, 0, 0)" % ( self.user2_serial, ))
        cursor.execute("INSERT INTO user2money (user_serial, currency_serial, amount, points, rake) VALUES (%d, 2, 200, 0, 0)" % ( self.user2_serial, ))
        cursor.close()
        return

    # ----------------------------------------------------------------
    def test04_getUserInfo(self):
        self.service.startService()
        self.service.refill = None

        self.default_money = 0
        self.createUsers()
        #
        # No cash in means no money
        #
        info = self.service.getUserInfo(self.user1_serial)
        self.assertEqual(0, len(info.money))
        self.cashIn()
        info = self.service.getUserInfo(self.user2_serial)
        self.assertEquals({1: (100, 0, 0), 2: (200, 0, 0)}, info.money)

        #
        # Some money is on a table
        #
        table_serial = self.service.tables.values()[0].game.id
        buy_in = 50
        currency_serial = 1
        self.assertEquals(1, table_serial)
        self.assertEquals(currency_serial, self.service.tables.values()[0].currency_serial)
        self.service.seatPlayer(self.user2_serial, table_serial, 0)
        self.service.buyInPlayer(self.user2_serial, table_serial, currency_serial, buy_in)
        info = self.service.getUserInfo(self.user2_serial)
        self.assertEquals({1: (50, 50, 0), 2: (200, 0, 0)}, info.money)
        #
        # The other player only has one currency
        #
        self.service.seatPlayer(self.user1_serial, table_serial, 0)
        self.service.buyInPlayer(self.user1_serial, table_serial, currency_serial, buy_in)
        info = self.service.getUserInfo(self.user1_serial)
        self.assertEquals({1: (50, 50, 0)}, info.money)

    # ----------------------------------------------------------------
    def test05_getPersonalInfo(self):
        self.service.startService()

        self.createUsers()
        info = self.service.getPersonalInfo(self.user1_serial)
        self.assertEquals(self.user1_serial, info.serial)

    # ----------------------------------------------------------------
    def test07_cashInOut(self):
        self.service.startService()
        class Cashier:
            def cashIn(self, packet):
                self.cashIn_called = True
            def cashOut(self, packet):
                self.cashOut_called = True
            def cashOutCommit(self, packet):
                return packet.count
            def close(self):
                pass
        self.service.cashier = Cashier()

        self.service.cashIn(Packet())
        self.assertTrue(self.service.cashier.cashIn_called)
        self.service.cashOut(Packet())
        self.assertTrue(self.service.cashier.cashOut_called)
        packet = PacketPokerCashOutCommit()
        packet.count = 0
        self.assertEqual(PACKET_ACK, self.service.cashOutCommit(packet).type)
        packet.count = 2
        self.assertEqual(PACKET_ERROR, self.service.cashOutCommit(packet).type)

    # ----------------------------------------------------------------

    class ClientMockup:
        def __init__(self, serial, testObject):
            self.via_satellite = 0
            self.serial = serial
            self.packet_end_tournament = None
            self.packets = []
            self.tables = {}
            self.joinedTables = []
            self.testObject = testObject
            self.expectedReason = ""

        def sendPacketVerbose(self, packet):
            # packet_end_tournament was an expected field by some tests
            # when I got here so I left it as is but added my own packet
            # list for my own tests.
            self.packet_end_tournament = packet
            self.packets.append(packet)

        def join(self, table, reason = ""):
            self.joinedTables.append(table)
            self.tables[table.game.id] = table
            self.testObject.assertEquals(self.expectedReason, reason)

        def getSerial(self):
            return self.serial

        def sendPacket(self, packet):
            self.packets.append(packet)


    class TableMockup:
        def __init__(self):
            self.serial = None
        def kickPlayer(self, serial):
            self.kick_player = serial

    class TourneyMockup:
        def __init__(self):
            self.satellite_of = 0
            self.call_rank = None
            self.serial = 10
            self.schedule_serial = 1
            self.players = [0, 2, 4]
            self.prize = [10,20,30]
            self.rank = 10
        def getRank(self, serial):
            return self.rank

        def prizes(self):
            return self.prize


    def test09_endOfTournamentsNotInPlayers(self):
        self.service.startService()
        self.createUsers()

        table = self.TableMockup()
        kickplayer = None
        def getTableMockup( game_id):
            return table

        tourney = self.TourneyMockup()
        self.service.client = self.ClientMockup(self.user1_serial, self)
        self.service.getTable = getTableMockup
        self.service.tourneyRemovePlayer(tourney, 0, self.user1_serial)
        self.assertEquals(self.service.client.packet_end_tournament == None, True)

    def test10_endOfTournamentsNoPrize(self):
        self.service.startService()
        self.createUsers()

        table = self.TableMockup()
        kickplayer = None
        def getTableMockup( game_id):
            return table

        tourney = self.TourneyMockup()
        tourney.players = [2, self.user1_serial, 10]
        client = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client)
        self.service.getTable = getTableMockup
        self.service.tourneyRemovePlayer(tourney, 0, self.user1_serial)
        self.assertEquals(client.packet_end_tournament != None, True)
        self.assertEquals(client.packet_end_tournament.serial == tourney.serial, True)
        self.assertEquals(client.packet_end_tournament.money == 0, True)
        self.assertEquals(client.packet_end_tournament.rank == 10, True)
        self.assertEquals(client.packet_end_tournament.players == 3, True)

    def test11_endOfTournamentsPrize(self):
        self.service.startService()
        self.createUsers()

        table = self.TableMockup()
        kickplayer = None
        def getTableMockup( game_id):
            return table

        tourney = self.TourneyMockup()
        tourney.rank = 2
        client = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client)
        self.service.getTable = getTableMockup
        self.service.tourneyRemovePlayer(tourney, 0, self.user1_serial)
        self.assertEquals(client.packet_end_tournament != None, True)
        self.assertEquals(client.packet_end_tournament.serial == tourney.serial, True)
        self.assertEquals(client.packet_end_tournament.money == 20, True)
        self.assertEquals(client.packet_end_tournament.rank == 2, True)
        self.assertEquals(client.packet_end_tournament.players == 3, True)


    # ----------------------------------------------------------------
    def test12_playerImage(self):
        self.service.startService()

        self.createUsers()
        player_image1 = PacketPokerPlayerImage(serial = self.user1_serial,
                                               image = "12345")
        self.assertEquals(True, self.service.setPlayerImage(player_image1))
        player_image2 = self.service.getPlayerImage(self.user1_serial)
        self.assertEquals(player_image1.image, player_image2.image)
        player_image2 = self.service.getPlayerImage(self.user2_serial)
        self.assertEquals("", player_image2.image)

    # ----------------------------------------------------------------
    def test13_checkTourneysSchedule_spawn_regular(self):
        pokerservice.UPDATE_TOURNEYS_SCHEDULE_DELAY = 1
        pokerservice.CHECK_TOURNEYS_SCHEDULE_DELAY = 0.5

        #
        # A regular tournament starts registration now
        #
        #  Note that we have to set a respawn here by default so that it
        #  gets created; the default schema doesn't respawn this tourney
        #  by default.
        cursor = self.db.cursor()
        cursor.execute("UPDATE tourneys_schedule SET respawn = 'y', register_time = UNIX_TIMESTAMP(NOW() + INTERVAL 1 SECOND) WHERE name = 'regular1'")
        self.assertEqual(1, cursor.rowcount)
        cursor.close()

        self.service.startService()
        d = defer.Deferred()
        def checkTourneys(status):
            t = self.service.tourneys.values()[0]
            self.failUnless(filter(lambda tourney: tourney.sit_n_go == 'n', self.service.tourneys.values()))
            self.failUnless(filter(lambda tourney: tourney.name == 'regular1', self.service.tourneys.values()))
        d.addCallback(checkTourneys)
        reactor.callLater(3, lambda: d.callback(True))

        return d

    # ----------------------------------------------------------------
    def test14_checkTourneysSchedule_cancel_regular(self):
        pokerservice.DELETE_OLD_TOURNEYS_DELAY = 0
        pokerservice.UPDATE_TOURNEYS_SCHEDULE_DELAY = 1
        pokerservice.CHECK_TOURNEYS_SCHEDULE_DELAY = 0.1

        #
        # A regular tournament starts registration now
        #
        cursor = self.db.cursor()
        cursor.execute("UPDATE tourneys_schedule " +
                       " SET register_time = " + str(testclock._seconds_value) + ", " +
                       "     start_time = " + str(testclock._seconds_value + 10) + ", " +
                       "     respawn = 'n' " +
                       " WHERE name = 'regular1'")
        self.assertEqual(1, cursor.rowcount)
        cursor.close()

        self.service.startService()
        self.createUsers()

        #
        # Register a user who will be re-imbursed when the tournament is canceled
        #
        d1 = defer.Deferred()
        def registerPlayer(status):
            (regular,) = filter(lambda tourney: tourney.name == 'regular1', self.service.tourneys.values())
            self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                    game_id = regular.serial))
            self.assertEquals(self.default_money - regular.buy_in - regular.rake, self.service.getMoney(self.user1_serial, 1))
            self.assertEquals([ self.user1_serial ], regular.players)

        d1.addCallback(registerPlayer)
        reactor.callLater(5, lambda: d1.callback(True))

        d2 = defer.Deferred()
        def checkTourneys(status):
            self.assertEquals([], filter(lambda tourney: tourney['name'] == 'regular1', self.service.tourneys_schedule.values()))
            self.assertEquals([], filter(lambda tourney: tourney.name == 'regular1', self.service.tourneys.values()))
            self.assertEquals(self.default_money, self.service.getMoney(self.user1_serial, 1))
        d2.addCallback(checkTourneys)
        reactor.callLater(15, lambda: d2.callback(True))

        return defer.DeferredList((d1, d2), fireOnOneErrback = True)

    def test14_sng_timeout(self):
        settings = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <server sng_timeout="111">
        <delays />
        </server>
        """
        service = pokerservice.PokerService(settings)
        self.assertEqual(111, service.sng_timeout)

    # ----------------------------------------------------------------
    def test14_checkTourneysSchedule_cancel_sitngo(self):
        self.service.startService()
        self.service.sng_timeout = 0
        (heads_up_before,) = filter(lambda tourney: tourney.name == 'sitngo2', self.service.tourneys.values())
        register_time = int(pokerservice.seconds()) - 1
        self.service.checkTourneysSchedule()
        self.assertEquals(pokertournament.TOURNAMENT_STATE_CANCELED, heads_up_before.state)
        (heads_up_after1, heads_up_after2) = filter(lambda tourney: tourney.name == 'sitngo2', self.service.tourneys.values())
        self.failUnless(abs(register_time - heads_up_after2.register_time) <= 1)
        self.assertEquals(heads_up_before.serial, heads_up_after1.serial)
        self.assertNotEqual(heads_up_before.serial, heads_up_after2.serial)
        self.assertEqual(heads_up_before.schedule_serial, heads_up_after2.schedule_serial)

    # ----------------------------------------------------------------
    def test14_1_checkTourneysSchedule_cancel_sitngo_already_canceled(self):
        self.service.startService()
        self.service.sng_timeout = 0
        (heads_up_before,) = filter(lambda tourney: tourney.name == 'sitngo2', self.service.tourneys.values())
        heads_up_before.state = pokertournament.TOURNAMENT_STATE_CANCELED
        heads_up_before.changeState = lambda x: self.assertFalse(True)
        self.service.checkTourneysSchedule()

    # ----------------------------------------------------------------
    def test15_runTourney(self):
        pokerservice.UPDATE_TOURNEYS_SCHEDULE_DELAY = 1
        pokerservice.CHECK_TOURNEYS_SCHEDULE_DELAY = 0.1

        self.service.startService()
        self.createUsers()

        client1 = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client1)
        client1.expectedReason = PacketPokerTable.REASON_TOURNEY_START
        (heads_up,) = filter(lambda tourney: tourney.name == 'sitngo2', self.service.tourneys.values())
        clear_all_messages()
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                game_id = heads_up.serial))
        self.failUnless(search_output('tourneyRegister: UPDATE user2money SET amount = amount - 300000 WHERE user_serial = %d AND        currency_serial = 1 AND        amount >= 300000' % self.user1_serial), "UPDATE user2money notice not  found in verbose output")
        self.failUnless(search_output('tourneyRegister: INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (%d, 1, 1)' % self.user1_serial), "INSERT INTO user2tourney notice not found in verbose output")
        clear_all_messages()
        self.assertEquals(len(client1.packets), 1)
        self.assertEquals(client1.packets[0].type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(client1.packets[0].serial, self.user1_serial)
        self.assertEquals(client1.packets[0].game_id, heads_up.serial)
        client1.packets = []
        self.assertEquals(self.service.joined_count, 0)

        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user2_serial,
                                                                game_id = heads_up.serial))

        d = defer.Deferred()
        def checkTourneys(status):
            # joined_count should now be one, as the tourneyGameFilled() should
            # have been called, and we only had one client connected.
            self.assertEquals(self.service.joined_count, 1)
            self.assertEquals(len(client1.packets), 14)
            for p in client1.packets:
                self.assertEquals(p.game_id, self.service.tables.values()[2].game.id)
            self.assertEquals(len(client1.tables), 1)
            self.assertEquals(client1.tables.has_key(self.service.tables.values()[2].game.id), True)
            self.assertEquals(client1.tables[self.service.tables.values()[2].game.id], self.service.tables.values()[2])

            self.assertEquals(pokertournament.TOURNAMENT_STATE_RUNNING, heads_up.state)
            game = heads_up.games[0]
            in_position = game.getSerialInPosition()
            game.callNraise(in_position, game.maxBuyIn())
            in_position = game.getSerialInPosition()
            game.call(in_position)
            self.service.tables.values()[2].update() # two tables already in settings

        d.addCallback(checkTourneys)
        reactor.callLater(3, lambda: d.callback(True))

        return d

    # ----------------------------------------------------------------
    def test16_runTourney_freeroll(self):
        return self.runTourney_freeroll(True)

    # ----------------------------------------------------------------
    def test17_runTourney_freeroll(self):
        return self.runTourney_freeroll(False)

    # ----------------------------------------------------------------
    def runTourney_freeroll(self, has_bailor):
        pokerservice.UPDATE_TOURNEYS_SCHEDULE_DELAY = 1
        pokerservice.CHECK_TOURNEYS_SCHEDULE_DELAY = 0.1

        #
        # A regular tournament starts registration now
        #
        cursor = self.db.cursor()
        prize = 100
        cursor.execute("UPDATE tourneys_schedule SET currency_serial = 2, buy_in = 0, prize_min = %d WHERE name = 'sitngo2'" % prize )
        self.assertEqual(1, cursor.rowcount)
        cursor.close()

        self.service.startService()
        self.createUsers()

        (heads_up,) = filter(lambda tourney: tourney.name == 'sitngo2', self.service.tourneys.values())
        if has_bailor:
            heads_up.bailor_serial = self.user3_serial
        else:
            heads_up.bailor_serial = 42

        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                game_id = heads_up.serial))
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user2_serial,
                                                                game_id = heads_up.serial))

        d = defer.Deferred()
        def checkTourneys(status):
            self.assertEquals(pokertournament.TOURNAMENT_STATE_RUNNING, heads_up.state)
            game = heads_up.games[0]
            in_position = game.getSerialInPosition()
            game.callNraise(in_position, game.maxBuyIn())
            in_position = game.getSerialInPosition()
            game.call(in_position)
            self.service.tables.values()[2].update() # two tables already in settings
            if has_bailor:
                self.assertEquals(0, self.service.getMoney(self.user1_serial, 2), "bailor user1")
                self.assertEquals(prize, self.service.getMoney(self.user2_serial, 2), "bailor user2")
                self.assertEquals(self.default_money - prize, self.service.getMoney(self.user3_serial, 2), "bailor user3")
            else:
                self.assertEquals(0, self.service.getMoney(self.user1_serial, 2))
                self.assertEquals(0, self.service.getMoney(self.user2_serial, 2))
                self.assertEquals(self.default_money, self.service.getMoney(self.user3_serial, 2))

        d.addCallback(checkTourneys)
        reactor.callLater(15, lambda: d.callback(True))

        return d

    # ----------------------------------------------------------------
    def test18_cleanupTourneys_registering(self):
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO tourneys (serial, sit_n_go, name, start_time) VALUES (4000, 'n', 'regular3', " + str(testclock._seconds_value + 120) + ")")
        cursor.execute("INSERT INTO user2tourney VALUES (1, 1, 4000, 0, -1)")
        cursor.execute("INSERT INTO user2tourney VALUES (2, 1, 4000, 0, -1)")
        cursor.execute("INSERT INTO user2tourney VALUES (3, 1, 4000, 0, -1)")
        self.service.db = pokerdatabase.PokerDatabase(self.settings)
        self.service.dirs = ['%s/../conf' % SCRIPT_DIR]
        self.service.cleanupTourneys()
        tourney = self.service.tourneys[4000]
        self.assertEqual([1, 2, 3], tourney.players)
        cursor.execute("SELECT tourney_serial FROM route WHERE tourney_serial = 4000")
        self.assertEqual(1, cursor.rowcount)
        (tournament_serial,) = cursor.fetchone()
        self.assertEqual(4000, tournament_serial)
        cursor.close()
    # ----------------------------------------------------------------
    def test19_testJoinCounter(self):
        expectedMax = 1000
        val = 0
        self.service.startService()
        while val < expectedMax + 100:
            self.assertEquals(self.service.joinedCountIncrease(5), val+5)
            self.assertEquals(self.service.joinedCountDecrease(4), val+1)
            val += 1
            self.assertEquals(self.service.joinedCountReachedMax(),
                              val >= expectedMax)
        self.service.stopService()
    # ----------------------------------------------------------------
    def test20_spawnTourneyCurrencySerialFromDateFormat(self):
        cursor = self.db.cursor()
        currency_serial_from_date_format = '%Y%m'
        cursor.execute("UPDATE tourneys_schedule SET currency_serial_from_date_format = '%s' WHERE name = 'sitngo2'" % currency_serial_from_date_format)
        self.assertEqual(1, cursor.rowcount)
        cursor.close()
        self.service.today = lambda: date(1970, 01, 01)
        currency_serial_from_date = 197001L
        self.service.startService()
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        self.assertEqual(currency_serial_from_date_format, schedule["currency_serial_from_date_format"])
        cursor = self.db.cursor()
        cursor.execute("SELECT currency_serial from tourneys WHERE name = '%s'" % 'sitngo2')
        self.assertEqual(1, cursor.rowcount)
        currency_serial = cursor.fetchone()[0]
        cursor.close()
        self.assertEqual(currency_serial_from_date, currency_serial)
        tourney = self.service.tourneys[tourney_serial]
        self.assertEqual(currency_serial_from_date, tourney.currency_serial)
    # ----------------------------------------------------------------
    def test20_spawnTourneyPrizeCurrencyFromDateFormat(self):
        cursor = self.db.cursor()
        prize_currency_from_date_format = '%W'
        cursor.execute("UPDATE tourneys_schedule SET prize_currency_from_date_format = '%s' WHERE name = 'sitngo2'" % prize_currency_from_date_format)
        self.assertEqual(1, cursor.rowcount)
        cursor.close()
        self.service.today = lambda: date(1970, 1, 8)
        prize_currency_from_date = 1L
        self.service.startService()
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        self.assertEqual(prize_currency_from_date_format, schedule["prize_currency_from_date_format"])
        cursor = self.db.cursor()
        cursor.execute("SELECT prize_currency from tourneys WHERE name = '%s'" % 'sitngo2')
        self.assertEqual(1, cursor.rowcount)
        prize_currency = cursor.fetchone()[0]
        cursor.close()
        self.assertEqual(prize_currency_from_date, prize_currency)
        tourney = self.service.tourneys[tourney_serial]
        self.assertEqual(prize_currency_from_date, tourney.prize_currency)
    # ----------------------------------------------------------------
    def test21_today(self):
        self.assertEqual(self.service.today(), date.today())
    # ----------------------------------------------------------------
    def test22_spawnTourneyBadCurrencySerialFromDateFormat(self):
        cursor = self.db.cursor()
        cursor.execute("UPDATE tourneys_schedule SET currency_serial_from_date_format = 'NaN666' WHERE name = 'sitngo2'")
        cursor.close()
        self.assertRaises(UserWarning, self.service.startService)
    # ----------------------------------------------------------------
    def test22_spawnTourneyBadPrizeCurrencyFromDateFormat(self):
        cursor = self.db.cursor()
        cursor.execute("UPDATE tourneys_schedule SET prize_currency_from_date_format = 'NaN666' WHERE name = 'sitngo2'")
        cursor.close()
        self.assertRaises(UserWarning, self.service.startService)
    # ----------------------------------------------------------------
    def test23_isShuttingDown(self):
        from exceptions import AttributeError
        caughtIt = False
        try:
            self.service.isShuttingDown()
            self.failIf(True)  # Should not be reached
        except AttributeError, ae:
            caughtIt = True
            self.assertEquals(ae.__str__(),
                              "PokerService instance has no attribute 'shutting_down'")
        self.failUnless(caughtIt)

        self.service.startService()
        self.assertEquals(self.service.isShuttingDown(), False)
        self.assertEquals(self.service.isShuttingDown(), self.service.shutting_down)

        self.service.stopService()
        self.assertEquals(self.service.isShuttingDown(), True)
        self.assertEquals(self.service.isShuttingDown(), self.service.shutting_down)
    # ----------------------------------------------------------------
    def test24_stopFactory(self):
        # Nothing is actually done by stopFactory(), so this test can't
        # really check anything of use.
        self.assertEquals(self.service.stopFactory(), None)
##############################################################################
    def test23_localeChecks(self):
        self.service.startService()
        for enlo in ('this_locale_does_not_exist', 'en_GB.ISO-8859-1',
                     'en_US.ISO-8859-1', 'en_CA.ISO-8859-1'):
            self.assertEquals(self.service.locale2translationFunc(enlo)("Aces"), "Aces")
        clear_all_messages()
        self.assertEquals(self.service.locale2translationFunc('fr_FR', 'UTF-8'),
                         None)
        self.assertEquals(get_messages(), ['Locale, "fr_FR.UTF-8" not available.  fr_FR.UTF-8 must not have been provide via <language/> tag in settings, or errors occured during loading.'])
        enc = 'ISO-8859-1'
        self.assertEquals(self.service.locale2translationFunc('da_DK', enc)("%(name)s mucks loosing hand"), "%(name)s mucker tabende h\xe5nd")
        self.assertEquals(self.service.locale2translationFunc('de_DE', enc)("%(name)s raises %(amount)s"), '%(name)s erh\xf6ht %(amount)s' )
        self.assertEquals(self.service.locale2translationFunc('fi_FI', enc)("Board: %(board)s"), 'P\xf6yt\xe4kortit: %(board)s')
        for fr in ('fr_FR', 'fr_FX', 'fr_BE', 'fr_CA'):
            self.assertEquals(self.service.locale2translationFunc(fr, enc)("%(name)s receives %(amount)s"), '%(name)s re\xe7oit %(amount)s')
        self.assertEquals(self.service.locale2translationFunc('it_IT', enc)("High card %(card)s"),'Carta pi\xf9 alta: %(card)s')
        self.assertEquals(self.service.locale2translationFunc('nb_NO', enc)("%(name)s mucks loosing hand"), '%(name)s skjuler tapende h\xe5nd')
        self.assertEquals(self.service.locale2translationFunc('nl_NL', enc)("Four of a kind %(card)s"), 'Carr\xe9 %(card)s')
        self.assertEquals(self.service.locale2translationFunc('pt_PT', enc)("Rake %(amount)s"), 'Comiss\xe3o %(amount)s')
        self.assertEquals(self.service.locale2translationFunc('sv_SE', enc)("winners share a pot of %(pot)s"), 'vinnarna delar p\xe5 potten %(pot)s')
    # ----------------------------------------------------------------
    def test24_buyInPlayerNoneAmount(self):
        self.service.startService()
        self.service.refill = None
        self.createUsers()
        table_serial = self.service.tables.values()[0].game.id
        currency_serial = 1
        self.service.seatPlayer(self.user1_serial, table_serial, 0)
        clear_all_messages()
        self.service.buyInPlayer(self.user1_serial, table_serial, currency_serial, None)
        self.assertTrue("*ERROR*" in get_messages()[0])
    # ----------------------------------------------------------------
    def test25_chatMessageArchive(self):
        self.service.startService()
        player_serial = 10
        game_id = 42
        message = 'yeah'
        self.service.chatMessageArchive(player_serial, game_id, message)
        cursor = self.service.db.cursor(DictCursor)
        cursor.execute("SELECT * FROM chat_messages")
        result = cursor.fetchone()
        self.assertEquals(player_serial, result['player_serial'])
        self.assertEquals(game_id, result['game_id'])
        self.assertEquals(message, result['message'])
        self.assertNotEquals(0, result['timestamp'])


##############################################################################
class RefillTestCase(unittest.TestCase):

    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    def setUp(self):
        settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <server verbose="3">
        <listen tcp="19480" />
        <refill serial="1" amount="10000" />
        <delays />
        <path>%(script_dir)s/../conf</path>
        <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
        <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
        </server>
        """ % {'script_dir': SCRIPT_DIR}
        testclock._seconds_reset()
        self.destroyDb()
        self.service = pokerservice.PokerService(settings_xml)

    def tearDown(self):
        d = self.service.stopService()
        d.addCallback(lambda x: self.destroyDb())
        return d

    def test_refill(self):
        self.service.startService()
        refill = 10000
        ( (serial, name, privilege), message ) = self.service.auth("user1", "password1", "role1")
        self.assertEquals(0, self.service.autorefill(serial))
        table_money = 1000
        table_serial = 200
        self.service.db.db.query("INSERT INTO user2table VALUES (" + str(serial) + ", " + str(table_serial) + ", " + str(table_money) + ", 0)")
        self.service.db.db.query("INSERT INTO pokertables (serial, name, currency_serial, tourney_serial) VALUES (" + str(table_serial) + ", 'foo', 1, 0)")
        money_left = 100
        self.service.db.db.query("UPDATE user2money SET amount = " + str(money_left) + " WHERE user_serial = " + str(serial))
        self.assertEquals(refill - table_money, self.service.autorefill(serial))

class TimerTestCase(unittest.TestCase):

    def test_cancelTimers(self):
        settings = """<?xml version="1.0" encoding="ISO-8859-1"?>
        <server verbose="3">
        <delays />
        </server>
        """
        service = pokerservice.PokerService(settings)
        class Timer:
            def active(self):
                return False
        service.timer['foo_1'] = Timer()
        service.timer['foo_2'] = Timer()
        service.cancelTimers('foo')
        self.assertEqual([], service.timer.keys())

class TourneyUnregisterTestCase(PokerServiceTestCaseBase):

    def test_ok(self):
        tourney_serial = 100
        self.service.startService()
        self.createUsers()
        user_serial = self.user1_serial
        tourney = pokertournament.PokerTournament(serial = tourney_serial,
                                                  dirs = ['%s/../conf'
                                                          % SCRIPT_DIR])
        tourney.currency_serial = 1
        tourney.via_satellite = 0
        self.service.tourneys[tourney_serial] = tourney
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                game_id = tourney_serial))
        packet = PacketPokerId(serial = user_serial,
                               game_id = tourney_serial)
        return_packet = self.service.tourneyUnregister(packet)
        self.assertEqual(packet, return_packet)
    # ----------------------------------------------------------------
    def test_does_not_exist(self):
        tourney_serial = 100
        user_serial = 1
        self.service.startService()
        p = self.service.tourneyUnregister(PacketPokerId(serial = user_serial,
                                                         game_id = tourney_serial))
        self.assertEqual(PacketPokerTourneyUnregister.DOES_NOT_EXIST, p.code)
    # ----------------------------------------------------------------
    def test_not_registered(self):
        tourney_serial = 100
        user_serial = 1
        self.service.startService()
        tourney = pokertournament.PokerTournament(serial = tourney_serial,
                                                  dirs = ['%s/../conf'
                                                          % SCRIPT_DIR])
        self.service.tourneys[tourney_serial] = tourney
        p = self.service.tourneyUnregister(PacketPokerId(serial = user_serial,
                                                         game_id = tourney_serial))
        self.assertEqual(PacketPokerTourneyUnregister.NOT_REGISTERED, p.code)
    # ----------------------------------------------------------------
    def test_too_late(self):
        tourney_serial = 100
        user_serial = 1
        self.service.startService()
        tourney = pokertournament.PokerTournament(serial = tourney_serial,
                                                  dirs = ['%s/../conf'
                                                          % SCRIPT_DIR])
        tourney.register(user_serial)
        tourney.currency_serial = 1
        tourney.state = pokertournament.TOURNAMENT_STATE_RUNNING
        self.service.tourneys[tourney_serial] = tourney
        p = self.service.tourneyUnregister(PacketPokerId(serial = user_serial,
                                                         game_id = tourney_serial))
        self.assertEqual(PacketPokerTourneyUnregister.TOO_LATE, p.code)
    # ----------------------------------------------------------------
    def test_no_user2money(self):
        tourney_serial = 100
        user_serial = 1
        self.service.startService()
        tourney = pokertournament.PokerTournament(serial = tourney_serial,
                                                  dirs = ['%s/../conf'
                                                          % SCRIPT_DIR])
        tourney.register(user_serial)
        tourney.currency_serial = 1
        tourney.buy_in = 1000
        self.service.tourneys[tourney_serial] = tourney
        p = self.service.tourneyUnregister(PacketPokerId(serial = user_serial,
                                                         game_id = tourney_serial))
        self.assertEqual(PacketPokerTourneyUnregister.SERVER_ERROR, p.code)
        self.assertTrue("not in user2money" in p.message)
    # ----------------------------------------------------------------
    def test_no_user2tourney(self):
        tourney_serial = 100
        self.service.startService()
        self.createUsers()
        user_serial = self.user1_serial
        tourney = pokertournament.PokerTournament(serial = tourney_serial,
                                                  dirs = ['%s/../conf'
                                                          % SCRIPT_DIR])
        tourney.register(user_serial)
        tourney.currency_serial = 1
        self.service.tourneys[tourney_serial] = tourney
        p = self.service.tourneyUnregister(PacketPokerId(serial = user_serial,
                                                         game_id = tourney_serial))
        self.assertEqual(PacketPokerTourneyUnregister.SERVER_ERROR, p.code)
        self.assertTrue("not in user2tourney" in p.message)
    # ----------------------------------------------------------------
    def test_coverDatabaseEvent(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def __init__(mcSelf): mcSelf.errorPackets = []
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPackets.append(pack)
        class MockPacket:
            def __init__(mpSelf):
                mpSelf.serial = 423
                mpSelf.game_id = 865
        class MockTourney:
            def __init__(mtSelf):
                mtSelf.currency_serial = mtSelf.buy_in = mtSelf.rake = 10
            def isRegistered(mtSelf, serial):
                self.assertEquals(serial, 423)
                return True
            def canUnregister(mtSelf, serial):
                self.assertEquals(serial, 423)
                return True
            def unregister(mtSelf, serial):
                self.assertEquals(serial, 423)
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if sql[:len(statement)] == "UPDATE user2money SET amount = amount + ":
                    cursorSelf.rowcount = 1
                elif sql[:len(statement)] == "DELETE FROM user2tourney WHERE user_serial":
                    cursorSelf.rowcount = 1
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                        [ "UPDATE user2money SET amount = amount + ",
                                          "DELETE FROM user2tourney WHERE user_serial"])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        client = MockClient()
        tourney = MockTourney()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(423, client)
        self.service.tourneys = { 865 : tourney }

        # Not worth making this test cover dbevent, other tests do.  Here,
        # we make sure it is called as expected
        oldDbEvent = self.service.databaseEvent
        global calledDBCount
        calledDBCount = 0
        def dbEventMock(event = None, param1 = None, param2 = None, param3 = None):
            global calledDBCount
            calledDBCount += 1
            self.assertEquals(event, PacketPokerMonitorEvent.UNREGISTER)
            self.assertEquals(param1, 423)
            self.assertEquals(param2, 10)
            self.assertEquals(param3, 20)

        self.service.databaseEvent = dbEventMock

        clear_all_messages()

        pack = MockPacket()
        retPack =  self.service.tourneyUnregister(pack)
        self.assertEquals(pack, retPack)
        self.assertEquals(calledDBCount, 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find('tourneyUnregister: UPDATE user2money SET amount = amount + 20') >= 0)
        self.failUnless(msgs[1].find('tourneyUnregister: DELETE FROM user2tourney WHERE user_serial = 423') >= 0)
        self.service.db = oldDb
        self.service.databaseEvent = oldDbEvent
# ----------------------------------------------------------------
class TourneyCancelTestCase(PokerServiceTestCaseBase):
    def test_ok(self):
        class Tournament:
            def __init__(self):
                self.players = [1]
                self.serial = 1

        self.service.tourneys = {}
        self.service.tourneyCancel(Tournament())
        if verbose < 0:
            self.assertTrue(search_output('tourneyCancel:'))
# ----------------------------------------------------------------
class TourneyManagerTestCase(PokerServiceTestCaseBase):
    class ClientMockup:
        def __init__(self, serial, testObject):
            self.serial = serial
            self.tableJoined = None
            self.packets = []
            self.testObject = testObject
            self.expectedReason = ""

        def join(self, table, reason = ""):
            self.tableJoined = table
            self.testObject.assertEquals(self.expectedReason, reason)

        def sendPacketVerbose(self, packet):
            self.packets.append(packet)
    # ----------------------------------------------------------------
    def test01_no_rank(self):
        self.service.startService()
        self.service.verbose = 6
        self.createUsers()
        user_serial = self.user1_serial
        table_serial = 606
        table_money = 140
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        # One client (user1) has a Client logged in
        client1 = TourneyManagerTestCase.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client1)
        self.service.spawnTourney(schedule)
        clear_all_messages()
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                game_id = tourney_serial))
        self.failUnless(search_output('tourneyRegister: UPDATE user2money SET amount = amount - 300000 WHERE user_serial = 4 AND        currency_serial = 1 AND        amount >= 300000'), "UPDATE user2money expected verbose output not found")
        self.failUnless(search_output('tourneyRegister: INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (4, 1, 1)'), "INSERT INTO user2tourney")
        self.assertEquals(len(client1.packets), 1)
        self.assertEquals(client1.packets[0].type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(client1.packets[0].serial, self.user1_serial)
        self.assertEquals(client1.packets[0].game_id, tourney_serial)
        client1.packets = []
        self.assertEquals(client1.tableJoined, None)
        self.service.db.db.query("INSERT INTO user2table VALUES (" + str(self.user1_serial) + ", " + str(table_serial) + ", " + str(table_money) + ", 0)")
        self.service.db.db.query("UPDATE user2tourney SET table_serial = " + str(table_serial))
        self.service.tourneys[tourney_serial].can_register = False
        clear_all_messages()
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEquals(get_messages(), [])
        self.assertEqual(tourney_serial, packet.tourney['serial'])
        self.assertNotEqual(None, packet.tourney['rank2prize'])
        self.assertEqual(1, packet.tourney['registered'])
        self.assertEqual({'4' : {'rank': -1,
                                 'table_serial': table_serial,
                                 'name' : 'user1',
                                 'money': table_money}}, packet.user2properties)
    # ----------------------------------------------------------------
    def test02_no_money_no_table(self):
        self.service.startService()
        self.createUsers()
        user_serial = self.user1_serial
        table_serial = 606
        table_money = 140
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        self.service.spawnTourney(schedule)
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                game_id = tourney_serial))
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEqual(tourney_serial, packet.tourney['serial'])
        self.assertEqual(1, packet.tourney['registered'])
        self.assertEqual({'4' : {'rank': -1,
                                 'table_serial': None,
                                 'name' : 'user1',
                                 'money': -1}}, packet.user2properties)
    # ----------------------------------------------------------------
    def test03_player_removed(self):
        self.service.startService()
        self.createUsers()
        user_serial = self.user1_serial
        table_serial = 606
        table_money = 140
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        self.service.spawnTourney(schedule)
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                game_id = tourney_serial))
        table_serial = -1
        self.service.db.db.query("UPDATE user2tourney SET table_serial = " + str(table_serial))
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEqual(tourney_serial, packet.tourney['serial'])
        self.assertEqual(1, packet.tourney['registered'])
        self.assertEqual(0, len(packet.table2serials))
    # ----------------------------------------------------------------
    def test04_coverOldMySQLByMockUp(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'INSERT INTO tourneys',
                                                  'UPDATE tourneys_schedule',
                                                  'REPLACE INTO route']
                cursorSelf.row = ()
                for cntType in cursorSelf.acceptedStatements:
                    cursorSelf.counts[cntType] = 0
            def insert_id(cSelf): return 15
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
                cursorSelf.rowcount = 0
                cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service.startService()
        self.createUsers()
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]

        oldDb = self.service.db
        self.service.db = MockDatabase()
        realSpawnTourneyInCore = self.service.spawnTourneyInCore
        self.service.spawnTourneyInCore = lambda a, x, y, z, zz: True

        clear_all_messages()
        self.service.spawnTourney(schedule)
        msgs = get_messages()
        self.assertEquals(len(msgs), 1)
        self.assertEquals(msgs[0].find("spawnTourney: {'"), 0)
        self.assertEquals(self.service.db.cursorValue.counts,
                          {'INSERT INTO tourneys': 1,
                           'UPDATE tourneys_schedule': 0, 'REPLACE INTO route': 1})
        self.service.db = oldDb
        self.service.spawnTourneyInCore = realSpawnTourneyInCore
    # ------------------------------------------------------------------------
    def test04_bogusTourneySerial(self):
        self.service.startService()
        self.createUsers()
        tourney_serial = 17731
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEquals(packet.type, PACKET_ERROR)
        self.assertEquals(packet.other_type, PACKET_POKER_GET_TOURNEY_MANAGER)
        self.failUnless(packet.message.find("%d" % tourney_serial) >= 0)
        self.assertEquals(packet.code, PacketPokerGetTourneyManager.DOES_NOT_EXIST)
    # ------------------------------------------------------------------------
    def test05_moreThanOneTourneyRow(self):
        validStatements = ["SELECT user_serial, table_serial, rank FROM user2tourney WHERE tourney_serial =",
                           'SELECT user_serial, name FROM user2tourney, users WHERE user2tourney.tourney_serial',
                           "SELECT * FROM tourneys WHERE serial = "
                           ]
        class MockCursor(MockCursorBase):
            def fetchall(mcSelf): return mcSelf.rows
            def statementActions(cursorSelf, sql, statement):
                if statement == "SELECT * FROM tourneys WHERE serial = ":
                    cursorSelf.rowcount = 6
                    cursorSelf.rows = []
                    cursorSelf.row = {'sit_n_go' : 'n', 'buy_in' : 0, 'prize_min' : 0,
                                      }
                else:
                    cursorSelf.rowcount = 0
                    cursorSelf.rows = [ ]
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)
        class MockDBWithDifferentCursorMethod(MockDatabase):
            def cursor(dbSelf, dummy = None):
                # Needed because tourneyManger() calls with argument "DictCursor"
                return MockDatabase.cursor(dbSelf)

        self.service = pokerservice.PokerService(self.settings)
        self.service.startService()

        oldDb = self.service.db
        self.service.db = MockDBWithDifferentCursorMethod(MockCursor)
        self.service.tourneys = {}
        tourney_serial = 17735
        clear_all_messages()
        packet = self.service.tourneyManager(tourney_serial)
        msgs = get_messages()
        self.failUnless(len(msgs) >= 1, "We should get at least one error message")
        self.assertEquals(msgs[0], 'tourneyManager: tourney_serial(17735) has more than one row in tourneys table, using first row returned')
        self.assertEquals(packet.type, PACKET_POKER_TOURNEY_MANAGER)

        self.service.db = oldDb
    # ------------------------------------------------------------------------
    def test06_prizes_tourney_regular(self):
        self.service.startService()
        self.createUsers()
        db = self.service.db.db
        tourney_serial = 11791
        db.query("INSERT INTO tourneys (serial, sit_n_go, state, buy_in) VALUES (%d, '%s', '%s', %d)" % (tourney_serial, 'n', 'complete', 1000))
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 1, 1, 1)")
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 2, 1, 2)")
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 3, 1, 3)")
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 4, 1, 4)")
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEquals(packet.type, PACKET_POKER_TOURNEY_MANAGER)
        rank2prize = packet.tourney['rank2prize']
        self.assertEquals(len(rank2prize), 2)
        self.assertEquals(int(rank2prize[0]), 2800)
        self.assertEquals(int(rank2prize[1]), 1200)
        self.assertEquals(packet.tourney['registered'], 4)

    # ------------------------------------------------------------------------
    def test07_prizes_tourney_sng(self):
        self.service.startService()
        self.createUsers()
        db = self.service.db.db
        tourney_serial = 11791
        db.query("INSERT INTO tourneys (serial, sit_n_go, state, buy_in, players_quota) VALUES (%d, '%s', '%s', %d, %d)" % (tourney_serial, 'y', 'complete', 1000, 10))
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEquals(packet.type, PACKET_POKER_TOURNEY_MANAGER)
        rank2prize = packet.tourney['rank2prize']
        self.assertEquals(len(rank2prize), 3)
        self.assertEquals(int(rank2prize[0]), 5000)
        self.assertEquals(int(rank2prize[1]), 3000)
        self.assertEquals(int(rank2prize[2]), 2000)
        self.assertEquals(packet.tourney['registered'], 0)

    # ------------------------------------------------------------------------
    def test08_prizes_guarantee_amount(self):
        self.service.startService()
        self.createUsers()
        db = self.service.db.db
        tourney_serial = 11791
        db.query("INSERT INTO tourneys (serial, sit_n_go, state, buy_in, players_quota, prize_min) VALUES (%d, '%s', '%s', %d, %d, %d)" % (tourney_serial, 'n', 'complete', 100, 1000, 10000))
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 1, 1, 1)")
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 2, 1, 2)")
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 3, 1, 3)")
        db.query("INSERT INTO user2tourney (tourney_serial, user_serial, table_serial, rank) VALUES (11791, 4, 1, 4)")
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEquals(packet.type, PACKET_POKER_TOURNEY_MANAGER)
        rank2prize = packet.tourney['rank2prize']
        self.assertEquals(len(rank2prize), 2)
        self.assertEquals(int(rank2prize[0]), 7000)
        self.assertEquals(int(rank2prize[1]), 3000)
        self.assertEquals(packet.tourney['registered'], 4)

###########################################################################
class TourneyCreateTestCase(PokerServiceTestCaseBase):

    def test01_create(self):
        self.service.startService()
        self.service.settings.headerSet("/server/@autodeal", "no")
        self.createUsers()
        tourney_name = 'testname'
        packet = PacketPokerCreateTourney(currency_serial = 1,
                                          name = tourney_name,
                                          players = [ self.user1_serial, self.user2_serial ])
        result = self.service.tourneyCreate(packet)
        self.assertEquals(PACKET_ACK, result.type)
        places = self.service.getPlayerPlaces(self.user1_serial)
        tourney = self.service.tourneys[places.tourneys[0]]
        self.assertEquals(tourney_name, tourney.name)

    def test02_register_failed(self):
        self.service.startService()
        self.createUsers()
        players = [ self.user1_serial, self.user2_serial ]
        packet = PacketPokerCreateTourney(currency_serial = 1,
                                          buy_in = self.default_money * 10,
                                          players = players)
        result = self.service.tourneyCreate(packet)
        self.assertEquals(PACKET_POKER_ERROR, result.type)
        self.assertSubstring(str(players), result.message)

###########################################################################
class TourneyMovePlayerTestCase(PokerServiceTestCaseBase):

    tourney_serial = 10

    class Tournament:
        def __init__(self):
            self.serial = TourneyMovePlayerTestCase.tourney_serial

    class Table:
        def __init__(self, testObject):
            self.avatar_collection = PokerAvatarCollection()
            self.testObj = testObject

        def movePlayer(self, client, serial, to_game_id, reason = ""):
            self.testObj.assertEquals(reason, PacketPokerTable.REASON_TOURNEY_MOVE)

    def test_ok(self):
        self.service.startService()
        self.service.getTable = lambda from_game_id: TourneyMovePlayerTestCase.Table(self)
        user_serial = 1
        table_serial = 100
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial, table_serial) VALUES (%d, %d, %d, %d)" % ( user_serial, 1, TourneyMovePlayerTestCase.tourney_serial, table_serial ))
        self.assertTrue(self.service.tourneyMovePlayer(TourneyMovePlayerTestCase.Tournament(), table_serial, 200, user_serial))
        cursor.close()

    def test_missing_db_record(self):
        self.service.startService()
        self.service.getTable = lambda from_game_id: TourneyMovePlayerTestCase.Table(self)
        user_serial = 1
        table_serial = 100
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial, table_serial) VALUES (%d, %d, %d, %d)" % ( user_serial, 1, TourneyMovePlayerTestCase.tourney_serial, table_serial ))
        wrong_user_serial = 2
        self.assertFalse(self.service.tourneyMovePlayer(TourneyMovePlayerTestCase.Tournament(), table_serial, 200, wrong_user_serial))
        cursor.close()

# ----------------------------------------------------------------
class TourneyNotifyTestCase(PokerServiceTestCaseBase):
    # ----------------------------------------------------------------
    def startTournament(self, table_serial, table_money):
        #
        # start tournament
        #
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        self.service.spawnTourney(schedule)
        self.service.tourneyRegister(PacketPokerTourneyRegister(serial = self.user1_serial,
                                                                game_id = tourney_serial))
        self.service.db.db.query("INSERT INTO user2table VALUES (" + str(self.user1_serial) + ", " + str(table_serial) + ", " + str(table_money) + ", 0)")
        self.service.db.db.query("UPDATE user2tourney SET table_serial = " + str(table_serial))
        self.service.tourneys[tourney_serial].can_register = False
        packet = self.service.tourneyManager(tourney_serial)
        self.assertEqual(tourney_serial, packet.tourney['serial'])
        self.assertNotEqual(None, packet.tourney['rank2prize'])
        self.assertEqual(1, packet.tourney['registered'])
        self.assertEqual({'4' : {'rank': -1,
                                 'table_serial': table_serial,
                                 'name' : 'user1',
                                 'money': table_money}}, packet.user2properties)

    def test01_notifyStart(self):
        self.service.startService()
        self.service.verbose = 6
        self.createUsers()
        user_serial = self.user1_serial
        table_serial = 606
        table_money = 140
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        #
        # user isLogged and in explain mode
        #
        avatar1 = self.service.createAvatar()
        avatar1.queuePackets()
        avatar1.relogin(self.user1_serial)
        avatar1.setExplain(True)
        #
        # user isLogged but not in explain mode
        #
        avatar2 = self.service.createAvatar()
        avatar1.queuePackets()
        avatar2.relogin(self.user2_serial)

        self.startTournament(table_serial, table_money)

        #
        # tourneyNotifyStart only notifies user1
        #
        avatar1.resetPacketsQueue()
        avatar2.resetPacketsQueue()
        self.assertEquals(1, len(self.service.tourneyNotifyStart(tourney_serial)))
        #
        # If user2 is notified, it will be called and raise an error
        #
        def deferredCanceled(packets):
            self.assertEqual(None, packets)

        def check(packets):
            self.assertEqual(1, len(packets))
            self.assertEqual(PACKET_POKER_TOURNEY_START, packets[0].type)
            self.assertEqual(tourney_serial, packets[0].tourney_serial)
            self.assertEqual(table_serial, packets[0].table_serial)
            self.assertEqual([], avatar2.resetPacketsQueue())
            self.assertEqual(0, avatar2.flushLongPollDeferred().called)
            avatar2.flushLongPollDeferred().callback(None)
            return packets
        d2 = avatar2.longpollDeferred()
        avatar2.longPollTimer.cancel()
        d2.addCallback(deferredCanceled)
        d1 = avatar1.longpollDeferred()
        avatar1.longPollTimer.cancel()
        d1.addCallback(check)
        return defer.DeferredList((d1, d2), fireOnOneErrback = True)

    def test02_no_explain(self):
        self.service.startService()
        self.service.verbose = 6
        self.createUsers()
        user_serial = self.user1_serial
        table_serial = 606
        table_money = 140
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        #
        # user isLogged and in explain mode
        #
        avatar1 = self.service.createAvatar()
        avatar1.queuePackets()
        avatar1.relogin(self.user1_serial)
        avatar1.setExplain(True)

        self.startTournament(table_serial, table_money)
        avatar1.resetPacketsQueue()
        self.assertEquals(1, len(self.service.tourneyNotifyStart(tourney_serial)))
        #
        # When the actual notification occurs (scheduled with callLater) it
        # will not be broadcasted because the avatar is no longer in explain mode.
        #
        avatar1.setExplain(None)
        #
        # If user1 is notified, it will be called and raise an error
        #
        def mustNotBeCalled(packets):
            self.assertEqual(None, packets)
        avatar1.longpollDeferred().addCallback(mustNotBeCalled)
        avatar1.longPollTimer.cancel()

    def test03_not_logged_in(self):
        self.service.startService()
        self.service.verbose = 6
        self.createUsers()
        user_serial = self.user1_serial
        table_serial = 606
        table_money = 140
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        #
        # user isLogged and in explain mode
        #
        avatar1 = self.service.createAvatar()
        avatar1.queuePackets()
        avatar1.relogin(self.user1_serial)
        avatar1.setExplain(True)

        self.startTournament(table_serial, table_money)
        self.assertEquals(1, len(self.service.tourneyNotifyStart(tourney_serial)))
        #
        # When the actual notification occurs (scheduled with callLater) it
        # will not be broadcasted because the avatar is no longer logged in.
        #
        avatar1.logout()
        avatar1.resetPacketsQueue()
        #
        # If user1 is notified, it will be called and raise an error
        #
        def mustNotBeCalled(packets):
            self.assertEqual(None, packets)
        avatar1.longpollDeferred().addCallback(mustNotBeCalled)
        avatar1.longPollTimer.cancel()

    def test04_wrong_tourney(self):
        self.service.startService()
        caughtIt = False
        try:
            self.service.tourneyNotifyStart(48484848)
            self.failIf(True, "We should have caught a UserWarning")
        except UserWarning:
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught a UserWarning!")

    def test05_broadcast_start(self):
        self.service.startService()
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        host = 'hostname'
        port = '80'
        tourney_serial = str(tourney_serial)
        self.service.db.db.query("INSERT INTO resthost (name, host, port) VALUES ('name', '%s', %s)" % ( host, port ))
        def getPage(url):
            self.assertEqual('http://' + host + ':' + port + '/TOURNEY_START?tourney_serial=' + tourney_serial, url)
        self.service.getPage = getPage
        self.service.tourneyBroadcastStart(tourney_serial)

    def test06_monitor(self):
        self.service.startService()
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        self.createUsers()
        table_serial = 606
        table_money = 140
        self.startTournament(table_serial, table_money)
        tourney = self.service.tourneys[tourney_serial]
        self.assertEqual(pokertournament.TOURNAMENT_STATE_REGISTERING, tourney.state)
        self.databaseEvent_called = False
        def databaseEvent(event = None, param1 = None, param2 = None, param3 = None):
            self.databaseEvent_called = True
            self.assertEqual(PacketPokerMonitorEvent.TOURNEY_START, event)
            self.assertEqual(tourney_serial, param1)
        self.service.databaseEvent = databaseEvent
        self.service.tourneyNewState(tourney, pokertournament.TOURNAMENT_STATE_REGISTERING, pokertournament.TOURNAMENT_STATE_RUNNING)
        self.assertEqual(True, self.databaseEvent_called)

class ListHandsTestCase(PokerServiceTestCaseBase):

    def test_ok(self):
        self.service.startService()
        ( total, hands ) = self.service.listHands("SELECT '1'", "SELECT '2'")
        self.assertEqual(["1"], hands)
        self.assertEqual("2", total)

class SetAccountTestCase(PokerServiceTestCaseBase):

    def test_insert_ok(self):
        self.service.startService()
        affiliate = 3
        info = self.service.setAccount(PacketPokerSetAccount(name = 'test08_1',
                                                             password = 'PASSWORD',
                                                             email = 'test08_1@HOME.COM',
                                                             affiliate = affiliate,
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        self.assertEquals(affiliate, info.affiliate)
        packed = info.pack()
        other_info = PacketPokerPersonalInfo()
        other_info.unpack(packed)
        self.assertEquals('1980-01-01', other_info.birthdate)

    def test_update_ok(self):
        self.service.startService()
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user1',
                                                             password = 'password1',
                                                             email = 'a@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        serial = info.serial
        info = self.service.setAccount(PacketPokerSetAccount(serial = serial,
                                                             name = 'user1',
                                                             password = 'password2',
                                                             email = 'a@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)

    def test_setPersonalInfo_fail(self):
        self.service.startService()
        self.service.setPersonalInfo = lambda x: False
        info = self.service.setAccount(PacketPokerSetAccount(name = 'test08_1',
                                                             password = 'PASSWORD',
                                                             email = 'test08_1@HOME.COM',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_ERROR, info.type)
        self.assertEquals("unable to set personal information", info.message)
        self.assertEquals(PacketPokerSetAccount.SERVER_ERROR, info.code)

    def test_name_already_exists(self):
        self.service.startService()
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user1',
                                                             password = 'password1',
                                                             email = 'a@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        serial = info.serial
        info = self.service.setAccount(PacketPokerSetAccount(serial = 10001,
                                                             email = 'a@b.c',
                                                             name = 'user1'))
        self.assertEquals(PACKET_ERROR, info.type)
        self.assertEquals(PacketPokerSetAccount.NAME_ALREADY_EXISTS, info.code)

    def test_email_already_exists(self):
        self.service.startService()
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user1',
                                                             password = 'password1',
                                                             email = '1@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        serial = info.serial
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user2',
                                                             password = 'password2',
                                                             email = '2@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        info = self.service.setAccount(PacketPokerSetAccount(serial = serial,
                                                             name = 'user1',
                                                             email = '2@b.c'))
        self.assertEquals(PACKET_ERROR, info.type)
        self.assertEquals(PacketPokerSetAccount.EMAIL_ALREADY_EXISTS, info.code)

    def test_update_duplicate_serial(self):
        self.service.startService()
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user1',
                                                             password = 'password1',
                                                             email = 'a@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        serial = info.serial
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user2',
                                                             password = 'password2',
                                                             email = '2@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        cursor = self.db.cursor()
        cursor.execute('ALTER TABLE users CHANGE COLUMN serial s1 INT UNSIGNED NOT NULL AUTO_INCREMENT')
        cursor.execute('ALTER TABLE users ADD COLUMN serial INT UNSIGNED NOT NULL')
        cursor.execute('DROP INDEX name_idx ON users')
        cursor.execute('DROP INDEX email_idx ON users')
        cursor.execute('UPDATE users SET serial = %d' % serial)
        info = self.service.setAccount(PacketPokerSetAccount(serial = serial,
                                                             name = 'user1',
                                                             password = 'password4',
                                                             email = 'a@b.c'))
        self.assertEquals(info.type, PACKET_ERROR)
        self.assertEquals(PacketPokerSetAccount.SERVER_ERROR, info.code)

    def test_name_error(self):
        info = self.service.setAccount(PacketPokerSetAccount(name = 'ab'))
        self.assertEquals(PACKET_ERROR, info.type)
        self.assertEquals(PacketPokerSetAccount.NAME_TOO_SHORT, info.code)

    def test_password_error(self):
        self.service.startService()
        info = self.service.setAccount(PacketPokerSetAccount(name = 'abcdef',
                                                             password = ''))
        self.assertEquals(PACKET_ERROR, info.type)
        self.assertEquals(PacketPokerSetAccount.PASSWORD_TOO_SHORT, info.code)

    def test_email_error(self):
        self.service.startService()
        info = self.service.setAccount(PacketPokerSetAccount(name = 'abcdef',
                                                             password = 'ABCDEF',
                                                             email = ''))
        self.assertEquals(PACKET_ERROR, info.type)
        self.assertEquals(PacketPokerSetAccount.INVALID_EMAIL, info.code)

    def test_email_duplicate(self):
        self.service.startService()
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user1',
                                                             password = 'password1',
                                                             email = 'a@b.c',
                                                             birthdate = '1980/01/01'))
        self.assertEquals(PACKET_POKER_PERSONAL_INFO, info.type)
        info = self.service.setAccount(PacketPokerSetAccount(name = 'user2',
                                                             password = 'password2',
                                                             email = 'a@b.c'))
        self.assertEquals(PACKET_ERROR, info.type)
        self.assertEquals(PacketPokerSetAccount.EMAIL_ALREADY_EXISTS, info.code)

    def test_user_private_duplicate(self):
        self.service.startService()
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO users_private (serial) VALUES (4)")
        cursor.close()
        raised = False
        try:
            info = self.service.setAccount(PacketPokerSetAccount(name = 'user1',
                                                                 password = 'password1',
                                                                 email = 'a@b.c',
                                                                 birthdate = '1980/01/01'))
        except IntegrityError:
            raised = True
        self.assertTrue(raised)

class ShutdownCheckTestCase(PokerServiceTestCaseBase):

    class PokerGame:
        def isEndOrNull(self):
            return not self.playing

    class PokerTable:
        def __init__(self):
            self.game = ShutdownCheckTestCase.PokerGame()


    def tearDown(self):
        pass

    def test_down(self):
        self.deferred_called = False
        def c(x):
            self.deferred_called = True
        d = defer.Deferred()
        d.addCallback(c)
        self.service.shutdown_deferred = d
        self.service.down = True
        self.service.shutdownCheck()
        self.assertTrue(self.deferred_called)
        del self.deferred_called

    def test_ok(self):
        table = ShutdownCheckTestCase.PokerTable()
        table.game.playing = True
        self.service.tables = { 1: table }
        self.service.down = False
        d = defer.Deferred()
        self.service.shutdown_deferred = d
        self.service.shutdownCheck()
        self.assertEqual(d, self.service.shutdown_deferred)
        table.game.playing = False
        def f(status):
            self.assertTrue(self.service.down)
            return status
        d.addCallback(f)
        return d

class TourneySatelliteTestCase(PokerServiceTestCaseBase):

    def test_lookup_nop(self):
        class Tournament:
            def __init__(self):
                self.satellite_of = 0

        self.service.startService()
        self.assertEqual((0, None), self.service.tourneySatelliteLookup(Tournament()), 'tourneySatelliteLookup does nothing')

    def test_lookup_not_found(self):
        class Tournament:
            def __init__(self):
                self.satellite_of = 12345

        self.service.startService()
        self.assertEqual((0, False), self.service.tourneySatelliteLookup(Tournament()), 'tourneySatelliteLookup does not find the tournament for which it is a satellite')

    def test_lookup_found_wrong_state(self):
        class Tournament:
            def __init__(self):
                self.serial = 234
                self.satellite_of = 12345

        class TournamentCandidate:
            def __init__(self):
                self.schedule_serial = 12345
                self.state = pokertournament.TOURNAMENT_STATE_RUNNING

        self.service.startService()
        self.service.tourneys = { 12345: TournamentCandidate() }
        self.assertEqual((0, pokertournament.TOURNAMENT_STATE_REGISTERING), self.service.tourneySatelliteLookup(Tournament()), 'tourneySatelliteLookup find a tournament which is not in the expected state')

    def test_lookup(self):
        class Tournament:
            def __init__(self):
                self.satellite_of = 12345

        class TournamentCandidate:
            def __init__(self):
                self.serial = 4343
                self.schedule_serial = 12345
                self.state = pokertournament.TOURNAMENT_STATE_REGISTERING

        self.service.startService()
        self.service.tourneys = { 12345: TournamentCandidate() }
        self.assertEqual((4343, None), self.service.tourneySatelliteLookup(Tournament()), 'tourneySatelliteLookup finds a tournament')

    def test_WaitingList_nop(self):
        class Tournament:
            def __init__(self):
                self.satellite_of = 0

        self.service.startService()
        self.assertEqual(False, self.service.tourneySatelliteWaitingList(Tournament()), 'tourneySatelliteWaitingList does nothing')

    def test_WaitingList_no_players_left(self):
        class Tournament:
            def __init__(self):
                self.satellite_of = 1
                self.satellite_registrations = [ 1 ]
                self.satellite_player_count = 1

        self.service.startService()
        self.assertEqual(False, self.service.tourneySatelliteWaitingList(Tournament()), 'tourneySatelliteWaitingList does nothing')

    def test_WaitingList(self):

        self.service.startService()
        self.createUsers()

        tourney_serial, tourney = self.service.tourneys.items()[0]
        tourney.players_quota = 10

        class Tournament:
            def __init__(Tself):
                Tself.satellite_of = tourney_serial
                Tself.satellite_registrations = [ ]
                Tself.satellite_player_count = 2
                Tself.winners = [ self.user2_serial, self.user1_serial, self.user3_serial, 200 ]

        tournament = Tournament()
        self.assertEqual(True, self.service.tourneySatelliteSelectPlayer(tournament, self.user2_serial, 1), 'tourneySatelliteSelectPlayer')
        self.assertEqual([self.user2_serial], tournament.satellite_registrations)
        tournament.satellite_registrations = [] # pretend the user was registered as a a side effect of a previous tournament
        self.failUnless(self.service.tourneySatelliteWaitingList(tournament), 'tourneySatelliteWaitingList adds player ' + str(self.user1_serial))
        self.assertEquals([self.user1_serial, self.user3_serial], tournament.satellite_registrations)
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM user2tourney WHERE user_serial = %d and tourney_serial = %d" % ( self.user1_serial, tourney_serial ))
        self.assertEqual(1, cursor.rowcount, 'user %d registered' % self.user1_serial)
        cursor.close()

    def test_SelectPlayer_nop(self):
        class Tournament:
            def __init__(self):
                self.satellite_of = 0

        self.service.startService()
        self.assertEqual(False, self.service.tourneySatelliteSelectPlayer(Tournament(), 0, 0), 'tourneySatelliteSelectPlayer does nothing')

    def test_SelectPlayer(self):
        class Tournament:
            def __init__(self):
                self.satellite_player_count = 10
                self.satellite_registrations = []

        self.service.startService()
        self.createUsers()
        tournament = Tournament()
        tourney_serial, schedule = self.service.tourneys.items()[0]
        tournament.satellite_of = tourney_serial

        rank = 1
        cursor = self.db.cursor()

        cursor.execute("SELECT * FROM user2tourney WHERE user_serial = %d and tourney_serial = %d" % ( self.user1_serial, tourney_serial ))
        self.assertEqual(0, cursor.rowcount, 'user %d not registered' % self.user1_serial)

        self.assertEqual(True, self.service.tourneySatelliteSelectPlayer(tournament, self.user1_serial, rank), 'tourneySatelliteSelectPlayer')

        self.assertEqual([ self.user1_serial ], tournament.satellite_registrations, 'registrations')
        cursor.execute("SELECT * FROM user2tourney WHERE user_serial = %d and tourney_serial = %d" % ( self.user1_serial, tourney_serial ))
        self.assertEqual(1, cursor.rowcount, 'user %d registered' % self.user1_serial)
        cursor.close()

    def test_SelectPlayer_duplicate_user(self):
        class Tournament:
            def __init__(self):
                self.satellite_player_count = 10
                self.satellite_registrations = []

        class ClientMockup:
            def __init__(self, serial):
                self.serial = serial
                self.packets = []

            def sendPacketVerbose(self, packet):
                self.packets.append(packet)

        self.service.startService()
        self.createUsers()
        client1 = ClientMockup(self.user1_serial)
        self.service.avatar_collection.add(self.user1_serial, client1)
        tournament = Tournament()
        tourney_serial, schedule = self.service.tourneys_schedule.items()[0]
        tournament.satellite_of = tourney_serial

        rank = 1
        cursor = self.db.cursor()

        cursor.execute("SELECT * FROM user2tourney WHERE user_serial = %d and tourney_serial = %d" % ( self.user1_serial, tourney_serial ))
        self.assertEqual(0, cursor.rowcount, 'user %d not registered' % self.user1_serial)

        #
        # The user is registered to satellite_of
        #
        self.assertEqual(True, self.service.tourneySatelliteSelectPlayer(tournament, self.user1_serial, rank), 'tourneySatelliteSelectPlayer')
        self.assertEqual(1, len(client1.packets))
        self.assertEqual(PACKET_POKER_TOURNEY_REGISTER, client1.packets[0].type)
        self.assertEqual([ self.user1_serial ], tournament.satellite_registrations, 'registrations')

        cursor.execute("SELECT * FROM user2tourney WHERE user_serial = %d and tourney_serial = %d" % ( self.user1_serial, tourney_serial ))
        self.assertEqual(1, cursor.rowcount, 'user %d registered' % self.user1_serial)

        #
        # Another attempt to register the same user returns an error packet
        #
        self.assertEqual(True, self.service.tourneySatelliteSelectPlayer(tournament, self.user1_serial, rank), 'tourneySatelliteSelectPlayer')
        self.assertEqual(2, len(client1.packets))
        self.assertEqual(PACKET_ERROR, client1.packets[1].type)
        self.assertEqual(PacketPokerTourneyRegister.ALREADY_REGISTERED, client1.packets[1].code)

        cursor.execute("SELECT * FROM user2tourney WHERE user_serial = %d and tourney_serial = %d" % ( self.user1_serial, tourney_serial ))
        self.assertEqual(1, cursor.rowcount, 'user %d registered' % self.user1_serial)
        cursor.close()

class TourneyFinishedTestCase(PokerServiceTestCaseBase):

    class ClientMockup:
        def __init__(self, serial, testObject):
            self.serial = serial
#            self.tableJoined = None
            self.packets = []
            self.testObject = testObject
            self.expectedReason = ""

        def join(self, table, reason = ""):
            self.tableJoined = table
            self.assertEquals(self.execptedReason, reason)

        def sendPacketVerbose(self, packet):
            self.packets.append(packet)

    def test_ok(self):
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = 0
                self.serial = 1
                self.players = []

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        client1 = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client1)
        tournament = Tournament()
        winner_serial = self.user1_serial
        tournament.winners = [ winner_serial ]
        tournament.bailor_serial = self.user2_serial
        self.service.tourneyFinished(tournament)
        cursor = self.db.cursor()
        cursor.execute("SELECT amount FROM user2money WHERE user_serial = %d" % winner_serial)
        (amount,) = cursor.fetchone()
        self.assertEqual(self.default_money + tournament.prize_min, amount)
        cursor.close()

    def test_prize_currency(self):
        prize_currency = 2
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = prize_currency
                self.serial = 1
                self.players = []
                self.bailor_serial = 0

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        client1 = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client1)
        tournament = Tournament()
        winner_serial = self.user1_serial
        tournament.winners = [ winner_serial ]
        self.service.tourneyFinished(tournament)
        cursor = self.db.cursor()
        cursor.execute("SELECT amount FROM user2money WHERE user_serial = %d AND currency_serial = %d" % ( winner_serial, prize_currency ))
        (amount,) = cursor.fetchone()
        self.assertEqual(tournament.prize_min, amount)
        cursor.close()

    def test_no_bailor(self):
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = 0
                self.serial = 1
                self.players = []

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        tournament = Tournament()
        winner_serial = 10
        tournament.winners = [ winner_serial ]
        tournament.bailor_serial = 2000
        self.assertEqual(False, self.service.tourneyFinished(tournament))
        if verbose < 0:
            self.assertTrue(search_output("bailor failed to provide requested money"))

    def test_bailor_zero(self):
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = 0
                self.serial = 1
                self.players = []

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        tournament = Tournament()
        winner_serial = 10
        tournament.winners = [ winner_serial ]
        tournament.bailor_serial = 0
        self.assertEqual(True, self.service.tourneyFinished(tournament))

    def test_tourney_finish(self):
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = 0
                self.serial = 1
                self.finish_time = testclock._seconds_value
                self.players = []

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        client1 = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client1)
        tournament = Tournament()
        winner_serial = self.user1_serial
        tournament.winners = [ winner_serial ]
        tournament.bailor_serial = self.user2_serial
        self.service.tourneyFinished(tournament)
        cursor = self.db.cursor()
        cursor.execute("SELECT finish_time FROM tourneys WHERE serial = %d" % tournament.serial)
        (finish_time,) = cursor.fetchone()
        self.failUnless(tournament.finish_time - finish_time < 1)
        cursor.close()

    def test_delete_route(self):
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = 0
                self.serial = 1
                self.players = []

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        client1 = self.ClientMockup(self.user1_serial, self)
        client1.tourneys = []
        client2 = self.ClientMockup(self.user2_serial, self)
        client2.tourneys = [1, 2]
        self.service.avatar_collection.add(self.user1_serial, client1)
        self.service.avatar_collection.add(self.user2_serial, client2)
        tournament = Tournament()
        winner_serial = self.user1_serial
        tournament.winners = [ winner_serial ]
        tournament.bailor_serial = self.user2_serial
        tournament.players = [ self.user1_serial, self.user2_serial ]
        self.service._ping_delay = 1
        d = defer.Deferred()
        d.addCallback(self.service.tourneyDeleteRouteActual)
        self.service.tourneyDeleteRouteActual = d.callback
        self.service.tourneyFinished(tournament)
        cursor = self.db.cursor()
        cursor.execute("SELECT tourney_serial FROM route WHERE tourney_serial = %s", tournament.serial)
        self.assertEqual(1, cursor.rowcount)
        (tournament_serial,) = cursor.fetchone()
        self.assertEqual(tournament.serial, tournament_serial)
        self.secondsStart = testclock._seconds_value
        def checkAvatarTourneys(x):
            self.assertEqual(True, 1 not in client1.tourneys)
            self.assertEqual(True, 1 not in client2.tourneys)
        def checkRoute(x):
            cursor.execute("SELECT tourney_serial FROM route WHERE tourney_serial = %s", tournament.serial)
            self.assertEqual(0, cursor.rowcount)
            self.assertEquals(testclock._seconds_value - self.secondsStart  >= self.service._ping_delay/1000.0, True)
            cursor.close()
        d.addCallback(checkAvatarTourneys)
        d.addCallback(checkRoute)
        return d

    def test_delete_route_table_delay(self):
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = 0
                self.serial = 1
                self.players = []

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        client1 = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client1)
        tournament = Tournament()
        winner_serial = self.user1_serial
        tournament.winners = [ winner_serial ]
        tournament.bailor_serial = self.user2_serial
        self.service._ping_delay = 1
        self.service.delays['extra_wait_tourney_finish'] = "40"
        d = defer.Deferred()
        d.addCallback(self.service.tourneyDeleteRouteActual)
        self.service.tourneyDeleteRouteActual = d.callback
        self.service.tourneyFinished(tournament)
        cursor = self.db.cursor()
        cursor.execute("SELECT tourney_serial FROM route WHERE tourney_serial = %s", tournament.serial)
        self.assertEqual(1, cursor.rowcount)
        (tournament_serial,) = cursor.fetchone()
        self.assertEqual(tournament.serial, tournament_serial)
        self.secondsStart = testclock._seconds_value
        def checkRoute(x):
            cursor.execute("SELECT tourney_serial FROM route WHERE tourney_serial = %s", tournament.serial)
            self.assertEqual(0, cursor.rowcount)
            self.assertEquals(testclock._seconds_value - self.secondsStart  >= int(self.service.delays['extra_wait_tourney_finish']), True)
        d.addCallback(checkRoute)
        return d

    def test_tourney_finish_packet(self):
        class Tournament:
            def __init__(self):
                self.prize_min = 10
                self.buy_in = 0
                self.registered = 2
                self.currency_serial = 1
                self.prize_currency = 0
                self.serial = 1
                self.players = []

            def prizes(self):
                return [self.prize_min]
        self.service.startService()
        self.createUsers()
        client1 = self.ClientMockup(self.user1_serial, self)
        self.service.avatar_collection.add(self.user1_serial, client1)
        client2 = self.ClientMockup(self.user2_serial, self)
        self.service.avatar_collection.add(self.user2_serial, client2)
        tournament = Tournament()
        winner_serial = self.user1_serial
        tournament.winners = [ winner_serial ]
        tournament.bailor_serial = self.user2_serial
        self.service.tourneyFinished(tournament)
        self.assertEqual(0, len(client1.packets))
        self.assertEqual(0, len(client2.packets))

##############################################################################
class BreakTestCase(PokerServiceTestCaseBase):
    class Table:
        def __init__(self):
            self.message = None
            self.type = None
            self.destroyCalled = 0

        def broadcastMessage(self, type, message):
            self.type = type
            self.message = message

        def scheduleAutoDeal(self):
            self.autodeal = 1

    class Database:
        class Cursor:
            def execute(self, sql):
                self.sql = sql
                self.rowcount = 1

            def close(self):
                pass

        def cursor(self):
            self._cursor = BreakTestCase.Database.Cursor()
            return self._cursor

        def close(self):
            pass

        def literal(self, args):
            pass

        class InternalDatabase:
            def query(self, args):
                pass
        db = InternalDatabase()

    class Tournament:
        def __init__(self):
            self.serial = 1
            self.start_time = 1
    # ------------------------------------------------------------------------
    def test01_tourneyNewState_simpleTransitions(self):
        def ok(tourney):
            self.callCount += 1
        def notok(tourney):
            self.failIf(1)

        saveDb = self.service.db
        self.callCount = 0

        self.service.db = BreakTestCase.Database()
        self.service.tourneyBreakCheck = notok
        self.service.tourneyDeal = notok
        self.service.tourneyBreakWait = notok
        self.service.tourneyBreakResume = notok
        self.service.tourneyDestroyGame = notok

        self.service.tourneyBreakWait = ok
        self.service.tourneyNewState(BreakTestCase.Tournament(),
             pokertournament.TOURNAMENT_STATE_RUNNING, pokertournament.TOURNAMENT_STATE_BREAK_WAIT)
        self.assertEquals(self.callCount, 1)
        self.service.tourneyBreakWait = notok
        self.callCount = 0
        self.service.db = saveDb
    # ------------------------------------------------------------------------
    def tourneyNewState_tourneyResumeAndDeal(self, waitMin, waitMax):
        """Helper function for testing tourneyResumeAndDeal state change.
        The wait for the action must be between waitMin and waitMax"""

        self.service.startService()
        saveDb = self.service.db

        # First, Setup functions that should not be caled and force them
        # to fail

        def notok(tourney):
            self.failIf(1)

        self.service.db = BreakTestCase.Database()
        self.service.tourneyBreakCheck = notok
        self.service.tourneyDeal = notok
        self.service.tourneyBreakWait = notok
        self.service.tourneyBreakResume = notok
        self.service.tourneyDestroyGame = notok

        # Next, create deferreds that must be called.  Since the deferred
        # callbacks are in the function, we will get a reactor 120 second
        # timeout error if these functions are not called.  They also use
        # callCount to make sure they aren't called too often.

        tourneyBreakResumeDeferred = defer.Deferred()
        def confirmTourneyBreakResume(tourney):
            # Note that when asserts in here fail, it is just a reactor error
            self.assertEquals(testclock._seconds_value - self.secondsStart  >= waitMin, True)
            self.assertEquals(testclock._seconds_value - self.secondsStart  <= waitMax, True)
            self.assertEquals(self.callCount, 0)
            self.callCount += 1
            tourneyBreakResumeDeferred.callback(True)

        tourneyDealDeferred = defer.Deferred()
        def confirmTourneyDeal(tourney):
            self.assertEquals(self.callCount, 1)
            self.callCount += 1
            tourneyDealDeferred.callback(True)

        self.callCount = 0
        self.service.tourneyBreakResume = confirmTourneyBreakResume
        self.service.tourneyDeal = confirmTourneyDeal
        self.secondsStart = testclock._seconds_value

        self.service.tourneyNewState(BreakTestCase.Tournament(), pokertournament.TOURNAMENT_STATE_BREAK, pokertournament.TOURNAMENT_STATE_RUNNING)

        self.service.db = saveDb
        return defer.DeferredList((tourneyBreakResumeDeferred, tourneyDealDeferred), fireOnOneErrback = True)

    def test02_tourneyNewState_tourneyResumeAndDeal_nowait(self):
        return self.tourneyNewState_tourneyResumeAndDeal(0, 5)

    def test03_tourneyNewState_tourneyResumeAndDeal_withWait(self):
        self.service.delays['extra_wait_tourney_break'] = "40"
        return self.tourneyNewState_tourneyResumeAndDeal(40, 45)
    # ------------------------------------------------------------------------
    def tourneyNewState_tourneyStart(self, waitMin, waitMax):
        """Helper function for testing tourney starting state change.
        The wait for the action must be between waitMin and waitMax"""

        self.service.startService()
        saveDb = self.service.db

        # First, Setup functions that should not be caled and force them
        # to fail

        def notok(tourney):
            self.failIf(1)

        self.service.db = BreakTestCase.Database()
        self.service.tourneyBreakCheck = notok
        self.service.tourneyDeal = notok
        self.service.tourneyBreakWait = notok
        self.service.tourneyBreakResume = notok
        self.service.tourneyDestroyGame = notok

        # Next, create deferreds that must be called.  Since the deferred
        # callbacks are in the function, we will get a reactor 120 second
        # timeout error if these functions are not called.  They also use
        # callCount to make sure they aren't called too often.

        def confirmTourneyDeal(tourney):
            self.assertEquals(testclock._seconds_value - self.secondsStart  >= waitMin, True)
            self.assertEquals(testclock._seconds_value - self.secondsStart  <= waitMax, True)
            self.assertEquals(self.callCount, 0)
            self.callCount += 1
            tourneyDealDeferred.callback(True)

        tourneyDealDeferred = defer.Deferred()

        self.callCount = 0
        self.service.tourneyDeal = confirmTourneyDeal
        self.secondsStart = testclock._seconds_value

        self.service.tourneyNewState(BreakTestCase.Tournament(), pokertournament.TOURNAMENT_STATE_REGISTERING, pokertournament.TOURNAMENT_STATE_RUNNING)

        self.service.db = saveDb
        return tourneyDealDeferred

    def test04_tourneyNewState_tourneyStart_nowait(self):
        return self.tourneyNewState_tourneyStart(0, 5)

    def test05_tourneyNewState_tourneyStart_withWait(self):
        self.service.delays['extra_wait_tourney_start'] = "40"
        return self.tourneyNewState_tourneyStart(40, 45)
    # ------------------------------------------------------------------------
    def tourneyFinish(self, waitMin, waitMax):
        """Helper function for testing tourney Finish callback.
        The wait for the action must be between waitMin and waitMax"""

        self.service.startService()
        saveDb = self.service.db
        saveTables = self.service.tables

        # Create a deferred that our MockTable will call when it is
        # destroyed, since that is the last function called by
        # tourneyDestroyGameActual().  If the callback isn't done, we will
        # get a reactor 120 second timeout error, so we can thus confirm
        # that DestroyGameActual got called

        tableDestroyDeferred = defer.Deferred()
        class MockTable:
            def __init__(self):
                self.destroyCalled = 0
            def destroy(table):
                self.assertEquals(testclock._seconds_value - self.secondsStart  >= waitMin, True)
                self.assertEquals(testclock._seconds_value - self.secondsStart  <= waitMax, True)
                self.assertEquals(table.destroyCalled, 0)
                table.destroyCalled += 1
                tableDestroyDeferred.callback(True)
                self.service.tables = saveTables

        ourTable  = MockTable()
        class MockGame:
            def __init__(game):
                game.id = 1102

        ourTable.game = MockGame()
        self.service.tables = { 1102: ourTable }

        def notok(tourney):
            self.failIf(1)

        self.service.db = BreakTestCase.Database()
        self.service.tourneyBreakCheck = notok
        self.service.tourneyDeal = notok
        self.service.tourneyBreakWait = notok
        self.service.tourneyBreakResume = notok
        self.service.tourneyDeal =  notok

        self.secondsStart = testclock._seconds_value
        self.service.tourneyDestroyGame(None, ourTable.game)

        self.service.db = saveDb
        return tableDestroyDeferred

    def test06_tourneyFinish_nowait(self):
        return self.tourneyFinish(0, 5)

    def test07_tourneyFinish_withWait(self):
        self.service.delays['extra_wait_tourney_finish'] = "40"
        return self.tourneyFinish(40, 45)
    # ------------------------------------------------------------------------
    def test08_tourneyNewState_tourneyBreak(self):
        """test08_tourneyNewState_tourneyBreak

        This test is a bit more complicated than the previous, since when
        entering the break state, we need to check to see that broadcast
        packets were sent."""
        def ok(tourney): self.callCount += 1
        def notok(tourney): self.failIf(1)

        saveDb = self.service.db
        self.callCount = 0

        # The complexity of this test requires mock-ups of its own,
        # specifically to handle the making sure the seconds to resume are
        # computed correctly and the packets are sent to the tables as
        # needed.

        class Table(BreakTestCase.Table):
            def __init__(self):
                self.broadcastedPackets = []
                BreakTestCase.Table.__init__(self)

            def broadcast(self, packet):
                self.broadcastedPackets.append(packet)
        tables = {}
        tables[1] = Table()
        tables[2] = Table()
        class Game:
            def __init__(self, newId=0):
                self.id = newId
            def getTable(gameId):
                if gameId == 1: return tables[1]
                elif  gameId == 2: return tables[2]
                else: self.failIf(True)

        breaks_duration = 120
        class Tournament(BreakTestCase.Tournament):
            def __init__(self, remainingSeconds = None):
                self.remaining_secs = remainingSeconds
                self.breaks_duration = breaks_duration
                self.games = [ Game(1), Game(2) ]
                BreakTestCase.Tournament.__init__(self)

            def remainingBreakSeconds(self):
                return self.remaining_secs

        self.service.db = BreakTestCase.Database()
        self.service.tables = { 1 : tables[1], 2 : tables[2] }
        self.service.tourneyBreakCheck = ok

        self.service.tourneyDeal = notok
        self.service.tourneyBreakWait = notok
        self.service.tourneyBreakResume = notok
        self.service.tourneyDestroyGame = notok

        # When we enter the break state, we should see Begin packets
        # sent.

        # First test here: see what happens when tourney.remaining_secs()
        # is None, thus yielding a return of None from
        # tourney.remainingBreakSeconds().  In this case, we should see
        # the resume_time as the current time, plus whatever
        # tourney.breaks_duration is.

        now = pokerservice.seconds()
        self.service.tourneyNewState(Tournament(), pokertournament.TOURNAMENT_STATE_RUNNING, pokertournament.TOURNAMENT_STATE_BREAK)
        self.assertEquals(self.callCount, 1)
        for ii in [ 1, 2 ]:
            self.assertEquals(len(tables[ii].broadcastedPackets), 1)
            pp = tables[ii].broadcastedPackets[0]
            self.assertEquals(pp.game_id, ii)
            self.assertEquals(pp.type, PACKET_POKER_TABLE_TOURNEY_BREAK_BEGIN)
            self.assertTrue(abs((pp.resume_time - now) - breaks_duration) < 1.0)

        # Reset for next test below
        self.callCount = 0
        for ii in [ 1, 2 ]: tables[ii].broadcastedPackets = []

        # Second test here: see what happens when
        # tourney.remainingBreakSeconds() can return an actual integer
        # value.  This is forced by setting tourney.remaining_secs to 111
        # in __init__.  We should get a resume_time of the current time
        # plus the remaining seconds.

        now = pokerservice.seconds()
        remainingSeconds = 111
        self.service.tourneyNewState(Tournament(remainingSeconds = remainingSeconds),
                                     pokertournament.TOURNAMENT_STATE_RUNNING, pokertournament.TOURNAMENT_STATE_BREAK)
        self.assertEquals(self.callCount, 1)
        for ii in [ 1, 2 ]:
            self.assertEquals(len(tables[ii].broadcastedPackets), 1)
            pp = tables[ii].broadcastedPackets[0]
            self.assertEquals(pp.game_id, ii)
            self.assertEquals(pp.type, PACKET_POKER_TABLE_TOURNEY_BREAK_BEGIN)
            self.assertTrue(abs((pp.resume_time - now) - remainingSeconds) < 1.0)
        self.callCount = 0

        self.service.tourneyBreakCheck = notok
        self.service.db = saveDb

    # ------------------------------------------------------------------------
    def test_tourneyDeal(self):
        class Game:

            def __init__(self):
                self.id = 1

        class Tournament:
            def __init__(self):
                self.games = [ Game() ]
                self.serial = 1

        tourney = Tournament()
        table = BreakTestCase.Table()
        table.game = tourney.games[0]
        self.service.tables = { 1: table }
        self.service.tourneyDeal(tourney)
        self.failUnless(hasattr(table, 'autodeal'))

    def test_tourneyBreakWait(self):
        class Game:

            def __init__(self):
                self.id = 1
                self.running = False

            def isRunning(self):
                return self.running

        class Tournament:
            def __init__(self):
                self.games = [ Game() ]
                self.serial = 1

        tourney = Tournament()
        table = BreakTestCase.Table()
        table.game = tourney.games[0]
        self.service.tables = { 1: table }
        tourney.games[0].running = True
        self.service.tourneyBreakWait(tourney)
        self.failUnless("at the end of the hand" in table.message)
        tourney.games[0].running = False
        self.service.tourneyBreakWait(tourney)
        self.failUnless("finish their hand" in table.message)
    # ------------------------------------------------------------------------
    def test11_tourneyBreakResume(self):
        class Table(BreakTestCase.Table):
            def __init__(self):
                self.broadcastedPackets = []
                BreakTestCase.Table.__init__(self)
            def broadcast(self, packet):
                self.broadcastedPackets.append(packet)
        tables = {}
        tables[1] = Table()
        tables[2] = Table()
        #the following gives me a syntax error
        #class  Game:
        class Game:
            def __init__(self, newId=0):
                self.id = newId
            def getTable(gameId):
                if gameId == 1: return tables[1]
                elif  gameId == 2: return tables[2]
                else: self.failIf(True)
        class Tournament(BreakTestCase.Tournament):
            def __init__(self):
                self.games = [ Game(1), Game(2) ]
                BreakTestCase.Tournament.__init__(self)

        tourney = Tournament()
        self.service.tables = { 1: tables[1], 2: tables[2] }

        self.service.tourneyBreakResume(tourney)
        for ii in [ 1, 2 ]:
            self.assertEqual(tables[ii].message, "Tournament resumes")
            self.assertEqual(tables[ii].type, PacketPokerGameMessage)
            self.assertEquals(len(tables[ii].broadcastedPackets), 1)
            pp = tables[ii].broadcastedPackets[0]
            self.assertEquals(pp.game_id, ii)
            self.assertEquals(pp.type, PACKET_POKER_TABLE_TOURNEY_BREAK_DONE)

    # ------------------------------------------------------------------------
    def test_tourneyBreakCheck(self):

        class Game:

            def __init__(self):
                self.id = 1

        class Tournament:

            def __init__(self):
                self.state = pokertournament.TOURNAMENT_STATE_RUNNING
                self.remaining = 0
                self.games = [ Game() ]
                self.serial = 1

            def remainingBreakSeconds(self):
                return self.remaining

            def updateBreak(self):
                pass

        tourney = Tournament()
        table = BreakTestCase.Table()
        table.game = tourney.games[0]
        self.service.tables = { 1: table }
        self.service.tourneyBreakCheck(tourney)
        self.failIf(table.message)
        tourney.state = pokertournament.TOURNAMENT_STATE_BREAK
        self.service.tourneyBreakCheck(tourney)
        self.failUnless("less than a minute" in table.message)
        tourney.remaining = 60
        self.service.tourneyBreakCheck(tourney)
        self.failUnless("one minute" in table.message)
        tourney.remaining = 120
        self.service.tourneyBreakCheck(tourney)
        self.failUnless("2 minute" in table.message)
##############################################################################
class UpdatePlayerRakeTestCase(PokerServiceTestCaseBase):

    def test_updatePlayerRake(self):
        self.service.startService()
        self.service.db = pokerdatabase.PokerDatabase(self.settings)
        cursor = self.db.cursor(DictCursor)
        cursor.execute("INSERT INTO user2money (user_serial, currency_serial, amount, points, rake) VALUES (101, 1, 10, 10, 10)")
        self.assertEqual(True, self.service.updatePlayerRake(1, 101, 5))
        cursor.execute("SELECT * FROM user2money WHERE user_serial = 101 AND currency_serial = 1")
        row = cursor.fetchone()
        self.assertEqual(15, row['rake'])
        self.assertEqual(15, row['points'])
        cursor.close()
##############################################################################
class PokerFactoryFromPokerServiceTestCase(unittest.TestCase):
    def test01_createService(self):
        class MockServiceSmall():
            def __init__(servSelf):
                servSelf.verbose = 9
                servSelf.createAvatarCount = 0
                servSelf.destroyAvatarCount = 0
            def createAvatar(servSelf):
                servSelf.createAvatarCount += 1
            def destroyAvatar(servSelf, mockAvatar):
                servSelf.destroyAvatarCount += 1
                self.assertEquals(mockAvatar, "MOCK MY AVATAR UP")

        mockServ = MockServiceSmall()
        pokerFactory = pokerservice.PokerFactoryFromPokerService(mockServ)
        self.assertEquals(pokerFactory.service, mockServ)
        self.assertEquals(pokerFactory.verbose, mockServ.verbose)
        self.assertEquals(mockServ.createAvatarCount, 0)
        self.assertEquals(mockServ.destroyAvatarCount, 0)

        pokerFactory.createAvatar()
        self.assertEquals(mockServ.createAvatarCount, 1)
        self.assertEquals(mockServ.destroyAvatarCount, 0)

        pokerFactory.destroyAvatar("MOCK MY AVATAR UP")
        self.assertEquals(mockServ.createAvatarCount, 1)
        self.assertEquals(mockServ.destroyAvatarCount, 1)

        self.assertEquals(pokerservice.PokerFactoryFromPokerService.protocol,
                          pokerservice.PokerServerProtocol)
        # FIXME?: cover registerAdapater line???
##############################################################################
class PokerServiceCoverageTests(unittest.TestCase):
    # ----------------------------------------------------------------
    def setUp(self):
        testclock._seconds_reset()
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        self.settings.header = self.settings.doc.xpathNewContext()
    # ----------------------------------------------------------------
    def tearDown(self):
        if hasattr(self, 'service'):
            d = self.service.stopService()
            return d
    # ----------------------------------------------------------------
    def test01_statsWithHands(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'SELECT MAX(serial)' ]
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
                if str == 'SELECT MAX(serial)' and cursorSelf.counts[str] == 1:
                    cursorSelf.rowcount = 1
                    cursorSelf.row = (8,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()
        self.service.avatars =  [ 'a', 'b', 'c' ]

        pack = self.service.stats("THIS ARG IS IGNORED")
        self.assertEquals(pack.players, 3)
        self.assertEquals(pack.hands, 8)
        self.assertEquals(pack.bytesin, 0)
        self.assertEquals(pack.bytesout, 0)
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test02_statsWithoutHands(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'SELECT MAX(serial)' ]
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
                if str == 'SELECT MAX(serial)' and cursorSelf.counts[str] == 1:
                    cursorSelf.rowcount = 0
                    cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()
        self.service.avatars =  [ 'a', 'b', 'c' ]

        pack = self.service.stats("THIS ARG IS IGNORED")
        self.assertEquals(pack.players, 3)
        self.assertEquals(pack.hands, 0)
        self.assertEquals(pack.bytesin, 0)
        self.assertEquals(pack.bytesout, 0)
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test04_createAvatar(self):
        from pokernetwork.pokeravatar import PokerAvatar
        self.service = pokerservice.PokerService(self.settings)
        self.service.avatars = []
        a = self.service.createAvatar()
        self.failUnless(isinstance(a, PokerAvatar))
        self.assertEquals(self.service.avatars, [a])
    # ----------------------------------------------------------------
    class MockAvatar:
        def __init__(maSelf):
            maSelf.connectionLostArgs = []
        def connectionLost(maSelf, val):
            maSelf.connectionLostArgs.append(val)
    # ----------------------------------------------------------------
    def test05_forceAvatarDestory_notInAnyList(self):
        self.service = pokerservice.PokerService(self.settings)
        ma = PokerServiceCoverageTests.MockAvatar()
        self.assertEquals(ma.connectionLostArgs, [])

        self.service.avatars = []
        self.service.monitors = []


        # This will cause a reactor timeout if this deferred is never
        # called back.
        testDestroyCalledDefer = defer.Deferred()
        def testDestroyCalled():
            msgs = get_messages()
            self.assertEquals(len(msgs), 1)
            self.assertEquals(msgs[0].find('*ERROR* avatar <__main__.MockAvatar instance at '), 0)
            self.failUnless(msgs[0].find(' is not in the list of known avatars') > 0)
            self.assertEquals(ma.connectionLostArgs, [ 'Disconnected' ])
            self.assertEquals(self.service.avatars, [])
            self.assertEquals(self.service.monitors, [])
            testDestroyCalledDefer.callback(True)

        clear_all_messages()
        self.service.forceAvatarDestroy(ma)
        reactor.callLater(5, testDestroyCalled)
        return testDestroyCalledDefer
    # ----------------------------------------------------------------
    def test06_forceAvatarDestory_inAvatarsListOnly(self):
        self.service = pokerservice.PokerService(self.settings)
        ma = PokerServiceCoverageTests.MockAvatar()
        self.assertEquals(ma.connectionLostArgs, [])

        self.service.avatars = [ma]
        self.service.monitors = []

        # This will cause a reactor timeout if this deferred is never
        # called back.
        testDestroyCalledDefer = defer.Deferred()
        def testDestroyCalled():
            self.assertEquals(get_messages(), [])
            self.assertEquals(ma.connectionLostArgs, [ 'Disconnected' ])
            self.assertEquals(self.service.avatars, [])
            self.assertEquals(self.service.monitors, [])
            testDestroyCalledDefer.callback(True)

        clear_all_messages()
        self.service.forceAvatarDestroy(ma)
        reactor.callLater(5, testDestroyCalled)

        return testDestroyCalledDefer
    # ----------------------------------------------------------------
    def test07_forceAvatarDestory_inMonitorsAndAvatars(self):
        self.service = pokerservice.PokerService(self.settings)
        ma = PokerServiceCoverageTests.MockAvatar()
        self.assertEquals(ma.connectionLostArgs, [])

        self.service.avatars = [ma]
        self.service.monitors = []
        pack = self.service.monitor(ma)
        self.assertEquals(pack.type, PACKET_ACK)
        self.assertEquals(self.service.monitors, [ma])

        # This will cause a reactor timeout if this deferred is never
        # called back.
        testDestroyCalledDefer = defer.Deferred()
        def testDestroyCalled():
            self.assertEquals(get_messages(), [])
            self.assertEquals(ma.connectionLostArgs, [ 'Disconnected' ])
            self.assertEquals(self.service.avatars, [])
            self.assertEquals(self.service.monitors, [])
            testDestroyCalledDefer.callback(True)

        clear_all_messages()
        self.service.forceAvatarDestroy(ma)
        reactor.callLater(5, testDestroyCalled)

        return testDestroyCalledDefer
    # ----------------------------------------------------------------
    def test08_sessionStartSucceed(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'insert into session' ]
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
                cursorSelf.rowcount = 1
                cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args):
                        return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()
        self.failUnless(self.service.sessionStart(5, '192.168.0.1'))
        self.assertEquals(get_messages(), ["sessionStart(5, 192.168.0.1): "])
        self.assertEquals(self.service.db.cursorValue.counts,
                          {'insert into session' : 1 })
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test09_sessionStartFail(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'insert into session' ]
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
                cursorSelf.rowcount = 0
                cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()
        self.failUnless(self.service.sessionStart(7, '192.168.0.2'))
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.assertEquals(msgs[0], 'sessionStart(7, 192.168.0.2): ')
        self.assertEquals(msgs[1].find("*ERROR* modified 0 rows (expected 1): insert into session ( user_serial, started, ip ) values ( 7, "), 0)
        self.failUnless(msgs[1].find(", '192.168.0.2')") > 0)

        self.assertEquals(self.service.db.cursorValue.counts,
                          {'insert into session' : 1 })
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test10_sessionEndSucceed(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'insert into session_history',
                                                  'delete from session']
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
                cursorSelf.rowcount = 1
                cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()
        self.failUnless(self.service.sessionEnd(9))
        self.assertEquals(get_messages(), ['sessionEnd(9): '])

        self.assertEquals(self.service.db.cursorValue.counts,
                          { 'insert into session_history' : 1,
                            'delete from session' : 1 })
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test11_sessionEndInsertFailsDeleteSucceeds(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'insert into session_history',
                                                  'delete from session']
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
                if sql[:len(str)] == 'insert into session_history':
                    cursorSelf.rowcount = 3
                else:
                    cursorSelf.rowcount = 1
                cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()
        self.failUnless(self.service.sessionEnd(9))
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.assertEquals(msgs[0], 'sessionEnd(9): ')
        self.assertEquals(msgs[1].find('*ERROR* a) modified 3 rows (expected 1): insert into session_history'), 0)
        self.assertEquals(self.service.db.cursorValue.counts,
                          { 'insert into session_history' : 1,
                            'delete from session' : 1 })
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test12_sessionEndAllSqlFails(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'insert into session_history',
                                                  'delete from session']
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
                cursorSelf.rowcount = 0
                cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()
        self.failUnless(self.service.sessionEnd(9))
        msgs = get_messages()
        self.assertEquals(len(msgs), 3)
        self.assertEquals(msgs[0], 'sessionEnd(9): ')
        self.assertEquals(msgs[1].find('*ERROR* a) modified 0 rows (expected 1): insert into session_history'), 0)
        self.assertEquals(msgs[2].find('*ERROR* b) modified 0 rows (expected 1): delete from session'), 0)
        self.assertEquals(self.service.db.cursorValue.counts,
                          { 'insert into session_history' : 1,
                            'delete from session' : 1 })
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test13_tourneyNewState_DBFail_forceTourneyDeal(self):
        self.callCount = 0
        def ok(tourney): self.callCount += 1
        def notok(tourney): self.failIf(1)

        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'update tourneys set']
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
                cursorSelf.rowcount = 8
                cursorSelf.row = (None,)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()

        self.service.tourneyBreakCheck = notok
        self.service.tourneyDeal = ok
        self.service.tourneyBreakWait = notok
        self.service.tourneyBreakResume = notok

        class MockTourney:
            def __init__(mtSelf):
                mtSelf.start_time = 5
                mtSelf.serial = 19
        self.service.tourneyNewState(MockTourney(),
                                     pokertournament.TOURNAMENT_STATE_BREAK_WAIT,
                                     pokertournament.TOURNAMENT_STATE_RUNNING)
        self.assertEquals(self.callCount, 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.assertEquals(msgs[0].find("tourneyNewState: update tourneys set state"), 0)
        self.assertEquals(msgs[1], "*ERROR* modified 8 rows (expected 1): update tourneys set state = 'running', start_time = 5 where serial = 19 ")

        self.assertEquals(self.service.db.cursorValue.counts,
                          {'update tourneys set': 1})
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test14_tourneyFinished_prizeNegative(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ 'UPDATE tourneys SET finish_time']

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
                        cursorSelf.rowcount = 1
                        found = True
                        break
                self.failUnless(found)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue
            def literal(dbSelf, val): return dbSelf.db.literal(val)
        class MockTourney:
            def prizes(mtSelf): return [-5]
            def __init__(mtSelf):
                mtSelf.serial = 15
                mtSelf.prize_min = 0
                mtSelf.prize_currency = 0
                mtSelf.currency_serial = 1
                mtSelf.buy_in = 5
                mtSelf.registered = 1
                mtSelf.winners = [9]

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        mockTourney = MockTourney()

        # Not worth making this test cover dbevent, other tests do
        oldDbEvent = self.service.databaseEvent
        def dbEventMock(event = None, param1 = None): pass
        self.service.databaseEvent = dbEventMock

        # Same with tourneyDeleteRoute -- we just check that it is called.
        oldTourneyDeleteRoute = self.service.tourneyDeleteRoute
        global tourneyDeleteRouteCount
        tourneyDeleteRouteCount = 0
        def mockTourneyDeleteRoute(tourney):
            global tourneyDeleteRouteCount
            tourneyDeleteRouteCount += 1
            self.assertEquals(tourney, mockTourney)
        self.service.tourneyDeleteRoute = mockTourneyDeleteRoute

        self.service.avatar_collection = PokerAvatarCollection()
        clear_all_messages()
        self.assertEquals(self.service.tourneyFinished(mockTourney), True)

        self.assertEquals(get_messages(), [])
        self.assertEquals(self.service.db.cursorValue.counts,
                          {'UPDATE tourneys SET finish_time' : 1})
        self.assertEquals(tourneyDeleteRouteCount, 1)
        self.service.db = oldDb
        self.service.databaseEvent = oldDbEvent
        self.service.tourneyDeleteRoute = oldTourneyDeleteRoute
    # ----------------------------------------------------------------
    def test15_tourneyGameFilled_updateTableFail(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ "update user2tourney set" ]
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
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue
        class MockTable:
            def __init__(mtSelf): mtSelf.updateCount = 0
            def update(mtSelf):   mtSelf.updateCount += 1

        class MockTourney:
            def prizes(mtSelf): return [-5]
            def __init__(mtSelf):
                mtSelf.serial = 15
                mtSelf.prize_min = 0
                mtSelf.buy_in = 5
                mtSelf.registered = 1
                mtSelf.winners = [9]
        class MockGame:
            class MockPlayer:
                def __init__(mpSelf): mpSelf.serial = 10
                def setUserData(mpSelf, values): pass
            def __init__(mgSelf): mgSelf.id = 22
            def playersAll(mgSelf): return [ MockGame.MockPlayer() ]
            def buyIn(mgSelf): return 100

        self.service = pokerservice.PokerService(self.settings)
        oldDb = self.service.db
        self.service.db = MockDatabase()

        oldSeatPlayer = self.service.seatPlayer
        def mySeatPlayer(x, y, z): pass
        self.service.seatPlayer = mySeatPlayer

        self.service.avatar_collection = PokerAvatarCollection()
        self.service.tables = { 22 : MockTable() }

        clear_all_messages()
        self.service.tourneyGameFilled(MockTourney(), MockGame())

        self.assertEquals(self.service.db.cursorValue.counts, {'update user2tourney set': 1})
        self.assertEquals(self.service.tables[22].updateCount, 1)

        msgs = get_messages()
        self.assertEquals(len(msgs), 3)
        self.assertEquals(msgs[0], 'tourneyGameFilled: player 10 disconnected')
        self.assertEquals(msgs[1].find('tourneyGameFilled: update user2tourney set'), 0)
        self.assertEquals(msgs[2].find('*ERROR* modified 0 rows (expected 1): update user2tourney set'), 0)

        self.service.db = oldDb
        self.service.seatPlayer = oldSeatPlayer
    # ----------------------------------------------------------------
    def test16_tourneyPlayersList_nonExistent(self):
        self.service = pokerservice.PokerService(self.settings)

        self.service.tourneys = {}

        pack = self.service.tourneyPlayersList(99)
        self.assertEquals(pack.type, PACKET_ERROR)
        self.assertEquals(pack.other_type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(pack.code, PacketPokerTourneyRegister.DOES_NOT_EXIST)
        self.assertEquals(pack.message, "Tournament 99 does not exist")
    # ----------------------------------------------------------------
    def test17_tourneyPlayersList_sucess(self):
        """Covers parts of tourneyPlayersList as well as getName()"""
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ "select name from users" ]
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
                if cursorSelf.counts[str] == 1:
                    cursorSelf.rowcount = 1
                    cursorSelf.row = ("joe",)
                else:
                    cursorSelf.rowcount = 0
                    cursorSelf.row = (None,)
                self.failUnless(found)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase()

        class MockTourney:
            def __init__(mtSelf): mtSelf.players = [ 5, 6, 0 ]

        self.service.tourneys = { 77: MockTourney() }

        clear_all_messages()
        pack = self.service.tourneyPlayersList(77)
        self.assertEquals(pack.players, [('joe', -1, 0),
                                         ('UNKNOWN', -1, 0), ('anonymous', -1, 0)])
        self.assertEquals(pack.type, PACKET_POKER_TOURNEY_PLAYERS_LIST)
        self.assertEquals(pack.serial, 77)
        self.assertEquals(get_messages(),
                          ['*ERROR* getName(6) expected one row got 0'])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test18_tourneyStats_sqlFails(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ "SELECT COUNT(*) FROM tourneys",
                                                  "SELECT COUNT(*) FROM user2tourney"]
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
                cursorSelf.rowcount = 0
                cursorSelf.row = (None,)
                self.failUnless(found)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()

        caughtIt = False
        try:
            self.service.tourneyStats()
            self.failIf(True)  # Should not be reached
        except TypeError, te:
            self.assertEquals(te.__str__(), "int() argument must be a string or a number, not 'NoneType'")
            caughtIt = True

        self.failUnless(caughtIt)
        self.assertEquals(get_messages(), [])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test19_tourneyStats_succeed(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ "SELECT COUNT(*) FROM tourneys",
                                                  "SELECT COUNT(*) FROM user2tourney"]
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
                cursorSelf.rowcount = 1
                cursorSelf.row = (9,)
                self.failUnless(found)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase()

        clear_all_messages()
        self.assertEquals(self.service.tourneyStats(), (9,9))
        self.assertEquals(get_messages(), [])

        self.assertEquals(self.service.db.cursorValue.counts,
                          {'SELECT COUNT(*) FROM user2tourney': 1,
                           'SELECT COUNT(*) FROM tourneys': 1})

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test20_tourneyRegister_tourneyMissing(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPacket = pack
        class MockPacket:
            def __init__(mpSelf):
                mpSelf.serial = 42
                mpSelf.game_id = 91

        client = MockClient()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(42, client)
        self.service.tourneys = { }

        clear_all_messages()

        self.failIf(self.service.tourneyRegister(MockPacket()))
        self.assertEquals(get_messages(),
                          ['*ERROR* type = ERROR(3) message = Tournament 91 does not exist, code = 1, other_type = POKER_TOURNEY_REGISTER'])
        self.failUnless(hasattr(client, "errorPacket"))
        self.assertEquals(client.errorPacket.type, PACKET_ERROR)
        self.assertEquals(client.errorPacket.code,
                          PacketPokerTourneyRegister.DOES_NOT_EXIST)
        self.assertEquals(client.errorPacket.message,
                          "Tournament 91 does not exist")
    # ----------------------------------------------------------------
    def test21_getPlayerInfo_validReturns(self):
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ "select locale,name,skin_url,skin_outfit"]
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
                cursorSelf.rowcount = 1
                cursorSelf.row = ('ourlocal','ourname','ourskinurl',None)
                self.failUnless(found)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase()

        pack = self.service.getPlayerInfo(5)
        self.assertEquals(pack.locale, 'ourlocal')
        self.assertEquals(pack.name, 'ourname')
        self.assertEquals(pack.url, 'ourskinurl')
        self.assertEquals(pack.outfit, 'random')

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test22_tourneyRegister_tourneyAlreadyRegistering(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def __init__(mcSelf): mcSelf.errorPackets = []
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPackets.append(pack)
        class MockPacket:
            def __init__(mpSelf):
                mpSelf.serial = 44
                mpSelf.game_id = 99
        class MockTourney:
            via_satellite = 0
            def isRegistered(mtSelf, serial):
                self.assertEquals(serial, 44)
                return True

        client = MockClient()
        tourney = MockTourney()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(44, client)
        self.service.tourneys = { 99 : tourney }

        clear_all_messages()

        self.failIf(self.service.tourneyRegister(MockPacket()))
        self.failUnless(hasattr(client, "errorPackets"))
        self.assertEquals(len(client.errorPackets), 1)
        pack = client.errorPackets[0]
        self.assertEquals(pack.type, PACKET_ERROR)
        self.failUnless(pack.message.find('Player 44 already registered in tournament 99') == 0)
        self.assertEquals(pack.other_type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(pack.code,
                          PacketPokerTourneyRegister.ALREADY_REGISTERED)
        msgs = get_messages()
        self.assertEquals(len(msgs), 1)
        self.failUnless(msgs[0].find('*ERROR* type = ERROR(3) message = Player 44 already registered in tournament 99')  == 0)
        self.failUnless(msgs[0].find('other_type = POKER_TOURNEY_REGISTER') >= 0)
    # ----------------------------------------------------------------
    def test23_tourneyRegister_tourneyRefuseRegistration(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def __init__(mcSelf): mcSelf.errorPackets = []
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPackets.append(pack)
        class MockPacket:
            def __init__(mpSelf):
                mpSelf.serial = 29
                mpSelf.game_id = 123
        class MockTourney:
            via_satellite = 0
            def isRegistered(mtSelf, serial):
                self.assertEquals(serial, 29)
                return False
            def canRegister(mtSelf, serial):
                self.assertEquals(serial, 29)
                return False

        client = MockClient()
        tourney = MockTourney()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(29, client)
        self.service.tourneys = { 123 : tourney }

        clear_all_messages()

        self.failIf(self.service.tourneyRegister(MockPacket()))
        self.failUnless(hasattr(client, "errorPackets"))
        self.assertEquals(len(client.errorPackets), 1)
        pack = client.errorPackets[0]
        self.assertEquals(pack.type, PACKET_ERROR)
        self.failUnless(pack.message.find('Registration refused in tournament 123') == 0)
        self.assertEquals(pack.other_type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(pack.code,
                          PacketPokerTourneyRegister.REGISTRATION_REFUSED)
        msgs = get_messages()
        self.assertEquals(len(msgs), 1)
        self.failUnless(msgs[0].find('*ERROR* type = ERROR(3) message = Registration refused in tournament 123')  == 0)

    # ----------------------------------------------------------------
    def test22_tourneyRegister_viaSatellite(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def __init__(mcSelf): mcSelf.errorPackets = []
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPackets.append(pack)
        class MockTourney:
            def __init__(self):
                self.via_satellite = 1

        client = MockClient()
        tourney = MockTourney()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(44, client)
        self.service.tourneys = { 99 : tourney }

        self.failIf(self.service.tourneyRegister(PacketPokerTourneyRegister(serial = 44, game_id = 99)))
        self.assertEquals(len(client.errorPackets), 1)
        pack = client.errorPackets[0]
        self.assertEquals(pack.type, PACKET_ERROR)
        self.assertEquals(pack.other_type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(pack.code,
                          PacketPokerTourneyRegister.VIA_SATELLITE)

    # ----------------------------------------------------------------
    def test24_tourneyRegister_tourneyNotEnoughMoneyToRegister(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def __init__(mcSelf): mcSelf.errorPackets = []
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPackets.append(pack)
        class MockPacket:
            def __init__(mpSelf):
                mpSelf.serial = 194
                mpSelf.game_id = 526
        class MockTourney:
            via_satellite = 0
            def __init__(mtSelf):
                mtSelf.currency_serial = mtSelf.buy_in = mtSelf.rake = 10
            def isRegistered(mtSelf, serial):
                self.assertEquals(serial, 194)
                return False
            def canRegister(mtSelf, serial):
                self.assertEquals(serial, 194)
                return True
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ "UPDATE user2money SET amount = amount"]
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
                cursorSelf.rowcount = 0
                cursorSelf.row = (None,)
                self.failUnless(found)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase()

        client = MockClient()
        tourney = MockTourney()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(194, client)
        self.service.tourneys = { 526 : tourney }

        clear_all_messages()

        self.failIf(self.service.tourneyRegister(MockPacket()))
        self.failUnless(hasattr(client, "errorPackets"))
        self.assertEquals(len(client.errorPackets), 1)
        pack = client.errorPackets[0]
        self.assertEquals(pack.type, PACKET_ERROR)
        self.failUnless(pack.message.find('Not enough money to enter the tournament 526') == 0)
        self.assertEquals(pack.other_type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(pack.code, PacketPokerTourneyRegister.NOT_ENOUGH_MONEY)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find('tourneyRegister: UPDATE user2money SET amount')  == 0)
        self.failUnless(msgs[1].find('*ERROR* type = ERROR(3) message = Not enough money to enter the tournament 526')  == 0)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test25_tourneyRegister_updateMoneyWeirdness(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def __init__(mcSelf): mcSelf.errorPackets = []
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPackets.append(pack)
        class MockPacket:
            def __init__(mpSelf):
                mpSelf.serial = 194
                mpSelf.game_id = 526
        class MockTourney:
            via_satellite = 0
            def __init__(mtSelf):
                mtSelf.currency_serial = mtSelf.buy_in = mtSelf.rake = 10
            def isRegistered(mtSelf, serial):
                self.assertEquals(serial, 194)
                return False
            def canRegister(mtSelf, serial):
                self.assertEquals(serial, 194)
                return True
        class MockCursor:
            def __init__(cursorSelf):
                cursorSelf.rowcount = 0
                cursorSelf.counts = {}
                cursorSelf.acceptedStatements = [ "UPDATE user2money SET amount = amount"]
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
                cursorSelf.rowcount = 2
                cursorSelf.row = (None,)
                self.failUnless(found)
                return cursorSelf.rowcount
            def fetchone(cursorSelf): return cursorSelf.row
        class MockDatabase:
            def __init__(dbSelf):
                class MockInternalDatabase:
                    def literal(intDBSelf, *args): return args[0]
                dbSelf.db = MockInternalDatabase()
                dbSelf.cursorValue = MockCursor()
            def cursor(dbSelf): return dbSelf.cursorValue

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase()

        client = MockClient()
        tourney = MockTourney()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(194, client)
        self.service.tourneys = { 526 : tourney }

        clear_all_messages()

        self.failIf(self.service.tourneyRegister(MockPacket()))
        self.failUnless(hasattr(client, "errorPackets"))
        self.assertEquals(len(client.errorPackets), 1)
        pack = client.errorPackets[0]
        self.assertEquals(pack.type, PACKET_ERROR)
        self.failUnless(pack.message.find('Server error') == 0)
        self.assertEquals(pack.other_type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(pack.code, PacketPokerTourneyRegister.SERVER_ERROR)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find('tourneyRegister: UPDATE user2money SET amount')  == 0)
        self.failUnless(msgs[1].find('*ERROR* modified 2 rows (expected 1): UPDATE user2money SET amount')  == 0)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test26_tourneyRegister_user2tourneyFailure(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockClient:
            def __init__(mcSelf): mcSelf.errorPackets = []
            def sendPacketVerbose(mcSelf, pack): mcSelf.errorPackets.append(pack)
        class MockPacket:
            def __init__(mpSelf):
                mpSelf.serial = 423
                mpSelf.game_id = 865
        class MockTourney:
            via_satellite = 0
            def __init__(mtSelf):
                mtSelf.currency_serial = mtSelf.buy_in = mtSelf.rake = 10
            def isRegistered(mtSelf, serial):
                self.assertEquals(serial, 423)
                return False
            def canRegister(mtSelf, serial):
                self.assertEquals(serial, 423)
                return True
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if sql[:len(statement)] == "UPDATE user2money SET amount = amount":
                    cursorSelf.rowcount = 1
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                        [ "UPDATE user2money SET amount = amount",
                                       "INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        client = MockClient()
        tourney = MockTourney()
        self.service.avatar_collection = PokerAvatarCollection()
        self.service.avatar_collection.add(423, client)
        self.service.tourneys = { 865 : tourney }

        # Not worth making this test cover dbevent, other tests do.  Here,
        # we make sure it is called as expected
        oldDbEvent = self.service.databaseEvent
        def dbEventMock(event = None, param1 = None, param2 = None, param3 = None):
            self.assertEquals(event, PacketPokerMonitorEvent.REGISTER)
            self.assertEquals(param1, 423)
            self.assertEquals(param2, 10)
            self.assertEquals(param3, 20)

        self.service.databaseEvent = dbEventMock

        clear_all_messages()

        self.failIf(self.service.tourneyRegister(MockPacket()))
        self.failUnless(hasattr(client, "errorPackets"))
        self.assertEquals(len(client.errorPackets), 1)
        pack = client.errorPackets[0]
        self.assertEquals(pack.type, PACKET_ERROR)
        self.failUnless(pack.message.find('Server error') == 0)
        self.assertEquals(pack.other_type, PACKET_POKER_TOURNEY_REGISTER)
        self.assertEquals(pack.code, PacketPokerTourneyRegister.SERVER_ERROR)
        msgs = get_messages()
        self.assertEquals(len(msgs), 3)
        self.failUnless(msgs[0].find('tourneyRegister: UPDATE user2money SET amount = amount - 20 WHERE user_serial = 423') >= 0)
        self.assertEquals(msgs[1], 'tourneyRegister: INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (423, 10, 865)')
        self.assertEquals(msgs[2], '*ERROR* insert 0 rows (expected 1): INSERT INTO user2tourney (user_serial, currency_serial, tourney_serial) VALUES (423, 10, 865) ')

        self.service.db = oldDb
        self.service.databaseEvent = oldDbEvent
    # ----------------------------------------------------------------
    def test27_loadHand_noRowFound(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                pass
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select description from hands where"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.loadHand(5), None)
        self.assertEquals(get_messages(), ['*ERROR* loadHand(5) expected one row got 0'])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test28_loadHand_row(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                cursorSelf.row = (']',)

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select description from hands where"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.loadHand(7), None)
        self.assertEquals(get_messages(), ['*ERROR* loadHand(7) eval failed for ]'])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test29_loadHand_confirm_backslash_r_replaced(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                cursorSelf.row = ("hand_serial\r+5",)

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select description from hands where"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.loadHand(9), 14)
        self.assertEquals(get_messages(),[])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test30_loadHand_confirm_working_code(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                # cute trick below... eventually, this gets evaled and the
                # hand_serial, the arg we send into loadHand() is set to
                # the arg hand_serial.  So, we can test later to see if
                # its value.
                cursorSelf.row = ("hand_serial+5",)

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select description from hands where"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.loadHand(3), 8)
        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test31_getHandSerial_coverCursorWithLastrowid(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                cursorSelf.row = ()
                cursorSelf.lastrowid = 9.7

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["INSERT INTO hands"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.getHandSerial(), 9)
        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test32_getHandSerial_coverCursorWithInsertID(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                cursorSelf.row = ()

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["INSERT INTO hands"])
            def insert_id(cursorSelf):  return 22.8

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.getHandSerial(), 22)
        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test33_getHandHistory_failedLoadHand(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                cursorSelf.row = ("None",)

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select description from hands where"])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        pack = self.service.getHandHistory(723, 99)
        self.assertEquals(pack.game_id, 723)
        self.assertEquals(pack.serial, 99)
        self.assertEquals(pack.code, PacketPokerHandHistory.NOT_FOUND)
        self.assertEquals(pack.other_type, PACKET_POKER_HAND_HISTORY)
        self.assertEquals(pack.message, "Hand 723 was not found in history of player 99")

        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test34_getHandHistory_playerProhibited(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                #!         (type, level, hand_serial, hands_count, time, variant, betting_structure, player_list, dealer, serial2chips)
                cursorSelf.row = ('[ ("foo", 3, 988, 1, 100, "he", "1-2-limit", [5, 6, 7], 8, {})]',)

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select description from hands where"])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        pack = self.service.getHandHistory(636, 222)
        # Note this interesting fact: getHandHistory() returns the
        # hand_history given in the row from the database, not the one you
        # passed it.  Theoretically, it should not generate a different
        # one, but this test confirms that the one from the DB is used
        # if they are.
        self.assertEquals(pack.game_id, 988)
        self.assertEquals(pack.serial, 222)
        self.assertEquals(pack.code, PacketPokerHandHistory.FORBIDDEN)
        self.assertEquals(pack.other_type, PACKET_POKER_HAND_HISTORY)
        self.assertEquals(pack.message, "Player 222 did not participate in hand 988")

        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test35_getHandHistory_succeedWithCardReplacement(self):
        from pokerengine.pokercards import PokerCards
        def mockLoseNotVisible(cardSelf): cardSelf.cards = -1
        PokerCards.loseNotVisible = mockLoseNotVisible
        saveFunc = PokerCards.loseNotVisible
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                if statement == "select description from hands where":
                    # (type, level, hand_serial, hands_count, time, variant, betting_structure, player_list, dealer, serial2chips)
                    cursorSelf.row = ("""[
("foo", 3, 988, 1, 100, "he", "1-2-limit", [113, 222], 8, {}),
("round", "preflop", [], { 113 : PokerCards("AsAh"),
222 : PokerCards("KsKd") }),
("showdown", [], { 113 : PokerCards("AsAh"),
222 : PokerCards("KsKd") }),
("neither", [], { 113 : PokerCards("AsAh"),
222 : PokerCards("KsKd") }),
]""",)
                else:
                    userSerial =  int(sql[len(statement):])
                    if userSerial == 113: cursorSelf.row = ("Doyle Brunson",)
                    elif userSerial == 222: cursorSelf.row = ("Stu Unger",)
                    else: self.fail("unknown user serial %d" % userSerial)

            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select description from hands where",
                                                         "select name from users where serial = "])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        pack = self.service.getHandHistory(696, 222)
        self.assertEquals(pack.history, "[('foo', 3, 988, 1, 100, 'he', '1-2-limit', [113, 222], 8, {}), ('round', 'preflop', [], {113: PokerCards(-1), 222: PokerCards([50])}), ('showdown', [], {113: PokerCards(-1), 222: PokerCards([50])}), ('neither', [], {113: PokerCards([51]), 222: PokerCards([50])})]")
        self.assertEquals(pack.serial2name, "{113: 'Doyle Brunson', 222: 'Stu Unger'}")
        self.assertEquals(pack.type, PACKET_POKER_HAND_HISTORY)
        self.assertEquals(pack.game_id, 988)
        self.assertEquals(pack.serial, 222)

        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
        PokerCards.loseNotVisible = saveFunc
    # ----------------------------------------------------------------
    def test36_saveHand_badRowcountOnUpdate(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 5
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["update hands set "])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        pack = self.service.saveHand([
                ("foo", 3, 991, 1, 100, "he", "1-2-limit", [113, 222], 8, {})], 991)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find("saveHand: update hands set  description = ") == 0)
        self.failUnless(msgs[1].find('*ERROR* modified 5 rows (expected 1 or 0): update hands') == 0)
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test37_saveHand_coverFailureOfInsert(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                # Make it always 1, so the update succeeds and insert fails
                cursorSelf.rowcount = 1
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["update hands set ",
                                                           "insert into user2hand values "])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        pack = self.service.saveHand([
                ("foo", 3, 991, 1, 100, "he", "1-2-limit", [113, 222], 8, {})], 991)
        msgs = get_messages()
        self.assertEquals(len(msgs), 3)
        self.failUnless(msgs[0].find("saveHand: update hands set  description = ") == 0)
        self.failUnless(msgs[1].find('saveHand: insert into user2hand') == 0)
        self.failUnless(msgs[2].find('*ERROR* inserted 1 rows (expected exactly 2): insert into user2hand values') == 0)
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test38_eventTable_serialZero(self):
        class MockCursor(MockCursorBase):
            def execute(cursorSelf, *args):
                MockCursorBase.execute(cursorSelf, *args)
                self.assertEquals(args[1][0], 99)
                self.assertEquals(args[1][1], 0)
            def statementActions(cursorSelf, sql, statement):
                pass
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["REPLACE INTO route"])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        class MockGame:
            def __init__(mgSelf):
                mgSelf.id = 99
        class MockTable:
            def __init__(mtSelf):
                mtSelf.game = MockGame()
                mtSelf.tourney = None

        self.service.eventTable(MockTable())
        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test39_statsTable(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                # Make it always 1, so the update succeeds and insert fails
                cursorSelf.rowcount = 1

                if statement == "SELECT COUNT(*) FROM pokertables":
                    cursorSelf.row = (1235,)
                elif statement == "SELECT COUNT(*) FROM user2table":
                    cursorSelf.row = (7356,)
                else:
                    self.failIf(1)
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["SELECT COUNT(*) FROM pokertables",
                                                           "SELECT COUNT(*) FROM user2table"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.statsTables(), (7356,1235))

        self.assertEquals(get_messages(), [])
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test40_cleanupTourneys_oneFoundFromPrimarySelect(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 0
                cursorSelf.row = []
                if statement == "SELECT * FROM tourneys":
                    if cursorSelf.counts[statement] <= 1:
                        cursorSelf.row = { 'buy_in' : 100, 'currency_serial' : 168,
                                           'serial' : 732 }
                        cursorSelf.rowcount = 1
                    # Second time method does select, we just want 0 rows returned.
                elif statement == "UPDATE user2money,user2tourney SET amount = amount":
                    # row count 0 is ok, next check for proper serials in statement
                    self.failUnless(sql.find("currency_serial = 168") > 0)
                    self.failUnless(sql.find("tourney_serial = 732") > 0)
                elif statement == "DELETE FROM tourneys WHERE serial =":
                    # row count 0 is ok, check for proper serial
                    self.failUnless(sql.find("serial = 732") > 0)
                elif statement == "DELETE FROM user2tourney WHERE tourney_serial =":
                    # row count 0 is ok, check for proper serial
                    self.failUnless(sql.find("serial = 732") > 0)
                else:
                    self.failIf(1, "unknown sql statement: " + statement + " " + sql)
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["SELECT * FROM tourneys",
                                    "UPDATE user2money,user2tourney SET amount = amount",
                                    "DELETE FROM tourneys WHERE serial =",
                                    "DELETE FROM user2tourney WHERE tourney_serial ="])
        class MockDBWithDifferentCursorMethod(MockDatabase):
            def cursor(dbSelf, dummy = None):
                # Needed because cleanupTourneys() calls with argument "DictCursor"
                return MockDatabase.cursor(dbSelf)

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDBWithDifferentCursorMethod(MockCursor)

        clear_all_messages()

        self.service.cleanupTourneys()

        # Make sure the right number of SQL statements got executed; the loop should
        # have only went once
        for expectJustOneStr in [ "UPDATE user2money,user2tourney SET amount = amount",
                                  "DELETE FROM tourneys WHERE serial =",
                                  "DELETE FROM user2tourney WHERE tourney_serial =" ]:
            self.assertEquals(self.service.db.cursorValue.counts[expectJustOneStr], 1)
        self.assertEquals(self.service.db.cursorValue.counts["SELECT * FROM tourneys"], 2)

        msgs = get_messages()
        self.assertEquals(len(msgs), 5)
        self.assertEquals(msgs[0].find("cleanupTourneys: SELECT * FROM tourneys WHERE"), 0)
        self.assertEquals(msgs[1].find('cleanupTourneys: UPDATE user2money,user2tourney'), 0)
        self.assertEquals(msgs[2].find('cleanupTourneys: DELETE FROM tourneys WHERE'), 0)
        self.assertEquals(msgs[3].find('cleanupTourneys: DELETE FROM user2tourney'), 0)
        self.assertEquals(msgs[4].find("cleanupTourneys: SELECT * FROM tourneys  WHERE"), 0)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test41_getMoney_bigRowCount(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 3
                cursorSelf.row = []
                self.failUnless(sql.find("user_serial = 7775") > 0, "user_serial wrong")
                self.failUnless(sql.find("currency_serial = 2356") > 0,
                                "currency_serial wrong")
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                        ["SELECT amount FROM user2money "])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(self.service.getMoney(7775, 2356), 0)

        self.assertEquals(self.service.db.cursorValue.counts["SELECT amount FROM user2money "], 1)
        self.assertEquals(self.service.db.cursorValue.closedCount, 1)

        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.assertEquals(msgs[0].find('SELECT amount FROM user2money'), 0)
        self.failUnless(msgs[0].find("user_serial = 7775") > 0)
        self.failUnless(msgs[0].find("currency_serial = 2356") > 0)
        self.assertEquals(msgs[1], '*ERROR* getMoney(7775) expected one row got 3')

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test42_cashQuery(self):
        class MockCashier():
            def cashQuery(cashierSelf, packet):
                cashierSelf.packet = packet
                return "Called"

        self.service = pokerservice.PokerService(self.settings)
        oldCashier = self.service.cashier

        cashier = MockCashier()
        self.service.cashier = cashier

        packet = 'Testing'
        self.assertEquals(self.service.cashQuery(packet), 'Called')
        self.assertEquals(cashier.packet, packet)

        self.service.cashier = oldCashier
    # ----------------------------------------------------------------
    def test43_cashOutCommit_commitFailure(self):
        class MockCashier():
            def cashOutCommit(cashierSelf, packet): return 8675309
        class MockPacket():
            def __init__(packetSelf): packetSelf.transaction_id = "Hi There"

        self.service = pokerservice.PokerService(self.settings)
        oldCashier = self.service.cashier

        cashier = MockCashier()
        self.service.cashier = cashier

        packet = self.service.cashOutCommit(MockPacket())
        self.assertEquals(packet.code, PacketPokerCashOutCommit.INVALID_TRANSACTION)
        self.assertEquals(packet.message, "transaction Hi There affected 8675309 rows instead of zero or one")
        self.assertEquals(packet.other_type, PACKET_POKER_CASH_OUT_COMMIT)
        self.assertEquals(packet.type, PACKET_ERROR)

        self.service.cashier = oldCashier
    # ----------------------------------------------------------------
    def test44_getPlayerInfo_serialIs0(self):
        self.service = pokerservice.PokerService(self.settings)
        packet = self.service.getPlayerInfo(0)
        self.assertEquals(packet.serial, 0)
        self.assertEquals(packet.name, "anonymous")
        self.assertEquals(packet.url, "random")
        self.assertEquals(packet.outfit, "random")
        # FIXME_PokerPlayerInfoLocale: (see also sr #2262 )
        # PokerService.getPlayerInfo() sends locale argument when creating
        # the PokerPlayerInfo() packet, but that argument is not used.
        # Should it be?  If it should be, then changes should be made to
        # pokerpackets.py to use it and the assert below should be put in.
#        self.assertEquals(packet.locale, "en_US")
    # ----------------------------------------------------------------
    def test45_getPlayerInfo_badRowCount(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 3
                cursorSelf.row = []
                self.failUnless(sql.find("serial = 235") > 0, "serial wrong")
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                      ["select locale,name,skin_url,skin_outfit from users"])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        packet = self.service.getPlayerInfo(235)
        self.assertEquals(get_messages(),
                          ['*ERROR* getPlayerInfo(235) expected one row got 3'])
        self.assertEquals(packet.serial, 235)
        self.assertEquals(packet.name, "anonymous")
        self.assertEquals(packet.url, "random")
        self.assertEquals(packet.outfit, "random")
        # FIXME_PokerPlayerInfoLocale: (see also sr #2262 )
        # PokerService.getPlayerInfo() sends locale argument when creating
        # the PokerPlayerInfo() packet, but that argument is not used.
        # Should it be?  If it should be, then changes should be made to
        # pokerpackets.py to use it and the assert below should be put in.
#        self.assertEquals(packet.locale, "en_US")

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test46_getUserInfo_badRowCount(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 3
                cursorSelf.row = []
                self.failUnless(sql.find("serial = 765") > 0, "serial wrong")
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                      ["SELECT rating,affiliate,email,name FROM users"])
        class MockDBWithDifferentCursorMethod(MockDatabase):
            def cursor(dbSelf, dummy = None):
                # Needed because getUserInfo() calls with argument "DictCursor"
                return MockDatabase.cursor(dbSelf)

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDBWithDifferentCursorMethod(MockCursor)

        clear_all_messages()

        packet = self.service.getUserInfo(765)
        self.assertEquals(get_messages(),
                          ['*ERROR* getUserInfo(765) expected one row got 3'])
        self.assertEquals(packet.serial, 765)
        self.assertEquals(packet.type, PACKET_POKER_USER_INFO)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test47_setPesonalInfo_badRowCount(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 3
                cursorSelf.row = []
                self.failUnless(sql.find("serial = 1854") > 0, "serial wrong")
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                      ["UPDATE users_private SET "])
        class MockPlayerInfo():
            def __init__(mpSelf):
                mpSelf.__dict__ = { 'serial' : 1854,
                                    'firstname' : '', 'lastname' : '', 'addr_street' : '',
                                    'addr_street2' : '', 'addr_zip' : '',
                                    'addr_town' : '', 'addr_state' : '',
                                    'addr_country' : '', 'phone' : '',
                                    'gender' : '', 'birthdate' : '' }

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failIf(self.service.setPersonalInfo(MockPlayerInfo()))
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.assertEquals(msgs[0].find("setPersonalInfo: UPDATE users_private SET"), 0)
        self.assertEquals(msgs[1].find("*ERROR* setPersonalInfo: modified 3 rows (expected 1 or 0): UPDATE users_private"), 0)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test48_setAccount_badRowcountOnInsert(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 0
                cursorSelf.row = []
                if sql == "SELECT serial FROM users WHERE":
                    self.failUnless(sql.find("name = 'OMGClayAiken'") > 0, "name wrong")
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                        ["SELECT serial FROM users WHERE",
                                         "INSERT INTO users"])
        self.service = pokerservice.PokerService(self.settings)

        class MockPacket():
            def __init__(mpSelf):
                mpSelf.name = "OMGClayAiken"
                mpSelf.email = "OMGClayAiken@example.org"
                mpSelf.password = "foobalg352"
                mpSelf.affiliate = 0
                mpSelf.type = PACKET_POKER_SET_ACCOUNT

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        packet = self.service.setAccount(MockPacket())
        self.assertEquals(packet.type, PACKET_ERROR)
        self.assertEquals(packet.message, 'inserted 0 rows (expected 1)')
        self.assertEquals(packet.code, PacketPokerSetAccount.SERVER_ERROR)
        self.assertEquals(packet.other_type, PACKET_POKER_SET_ACCOUNT)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test49_setAccount_lastrowidFailure(self):
        class MockCursor(MockCursorBase):
            def insert_id(mcSelf): return 22
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 0
                cursorSelf.row = []
                if statement == "SELECT serial FROM users WHERE name":
                    self.failUnless(sql.find("name = 'durrrr'") > 0, "name wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.row = []
                elif statement == "INSERT INTO users ":
                    cursorSelf.rowcount = 1
                    cursorSelf.row = []
                elif statement == "INSERT INTO users_private":
                    self.failUnless(sql.find("VALUES ('22')") > 0, "serial for users_private wrong")
                elif statement == "SELECT serial FROM users WHERE email":
                    self.failUnless(sql.find("email = 'durrrr@example.org'") > 0, "name wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self,
                                        ["SELECT serial FROM users WHERE name",
                                         "SELECT serial FROM users WHERE email",
                                         "INSERT INTO users ",
                                         "INSERT INTO users_private"])
        self.service = pokerservice.PokerService(self.settings)

        class MockPacket():
            def __init__(mpSelf):
                mpSelf.name = "durrrr"
                mpSelf.email = "durrrr@example.org"
                mpSelf.password = "blash535"
                mpSelf.affiliate = 0
                mpSelf.type = PACKET_POKER_SET_ACCOUNT

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        inputPacket = MockPacket()
        def mockSetPersonalInfo(packet):
            self.assertEquals(inputPacket, packet)
            return True
        def mockGetPersonalInfo(serial):
            self.assertEquals(22, serial)
            return "IT WORKED!!!"

        saveSetPersonalInfo = self.service.setPersonalInfo
        saveGetPersonalInfo = self.service.getPersonalInfo
        self.service.setPersonalInfo = mockSetPersonalInfo
        self.service.getPersonalInfo = mockGetPersonalInfo

        self.assertEquals("IT WORKED!!!",
                          self.service.setAccount(inputPacket))

        self.assertEquals(self.service.db.cursorValue.counts["SELECT serial FROM users WHERE name"], 1)
        self.assertEquals(self.service.db.cursorValue.counts["SELECT serial FROM users WHERE email"], 1)
        self.assertEquals(self.service.db.cursorValue.counts["INSERT INTO users "], 1)
        self.assertEquals(self.service.db.cursorValue.counts["INSERT INTO users_private"], 1)

        self.service.setPersonalInfo = saveSetPersonalInfo
        self.service.getPersonalInfo = saveGetPersonalInfo

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test50_setPlayerInfo_success(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                cursorSelf.rowcount = 1
                if statement == "update users set ":
                    self.failUnless(sql.find("name = 'Pham'") > 0, "name wrong")
                    self.failUnless(sql.find("skin_url = 'http://example.org'") > 0, "url wrong")
                    self.failUnless(sql.find("skin_outfit = 'naked'") > 0, "outfit wrong")
                    self.failUnless(sql.find("serial = 2891") > 0, "serial wrong")
                    cursorSelf.rowcount = 1
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["update users set "])
        self.service = pokerservice.PokerService(self.settings)

        class MockPlayerInfo():
            def __init__(mpSelf):
                mpSelf.name = 'Pham'
                mpSelf.url = 'http://example.org'
                mpSelf.outfit = 'naked'
                mpSelf.serial = 2891

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failUnless(self.service.setPlayerInfo(MockPlayerInfo()))
        self.assertEquals(self.service.db.cursorValue.counts["update users set "], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 1)
        self.failUnless(msgs[0].find('setPlayerInfo: update users set') == 0)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test51_setPlayerInfo_badUpdateValue(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "update users set ":
                    self.failUnless(sql.find("name = 'Pham'") > 0, "name wrong")
                    self.failUnless(sql.find("skin_url = 'http://example.org'") > 0, "url wrong")
                    self.failUnless(sql.find("skin_outfit = 'naked'") > 0, "outfit wrong")
                    self.failUnless(sql.find("serial = 2891") > 0, "serial wrong")
                    cursorSelf.rowcount = 3
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["update users set "])
        self.service = pokerservice.PokerService(self.settings)

        class MockPlayerInfo():
            def __init__(mpSelf):
                mpSelf.name = 'Pham'
                mpSelf.url = 'http://example.org'
                mpSelf.outfit = 'naked'
                mpSelf.serial = 2891

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failIf(self.service.setPlayerInfo(MockPlayerInfo()), "setPlayerInfo should fail here")
        self.assertEquals(self.service.db.cursorValue.counts["update users set "], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find('setPlayerInfo: update users set') == 0)
        self.failUnless(msgs[1].find('*ERROR* setPlayerInfo: modified 3 rows (expected 1 or 0): update users set') == 0)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test52_getPlayerImage_serial0(self):
        clear_all_messages()
        self.service = pokerservice.PokerService(self.settings)
        pack = self.service.getPlayerImage(0)
        self.assertEquals(pack.type, PACKET_POKER_PLAYER_IMAGE)
        self.assertEquals(pack.serial, 0)
        self.assertEquals(pack.image, '')
        self.assertEquals(pack.image_type, 'image/png')

        self.assertEquals(get_messages(), [])
    # ----------------------------------------------------------------
    def test53_getPlayerImage_selectRowCount3(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "select skin_image,":
                    self.failUnless(sql.find("serial = 825") > 0, "serial wrong")
                    cursorSelf.rowcount = 3
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["select skin_image,"])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        pack = self.service.getPlayerImage(825)
        self.assertEquals(pack.type, PACKET_POKER_PLAYER_IMAGE)
        self.assertEquals(pack.serial, 825)
        self.assertEquals(pack.image, '')
        self.assertEquals(pack.image_type, 'image/png')

        self.assertEquals(self.service.db.cursorValue.counts["select skin_image,"], 1)
        self.assertEquals(get_messages(), ['*ERROR* getPlayerImage(825) expected one row got 3'])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test54_setPlayerImage_rowcountwrong(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "update users set":
                    self.failUnless(sql.find("serial = 277") > 0, "serial wrong")
                    self.failUnless(sql.find("skin_image = 'Picture'") > 0, "skin_image wrong")
                    self.failUnless(sql.find("skin_image_type = 'image/png'") > 0, "image_type wrong")
                    cursorSelf.rowcount = 3
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["update users set"])
        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        class MockPlayerImage():
            def __init__(mpSelf):
                mpSelf.image = 'Picture'
                mpSelf.image_type = 'image/png'
                mpSelf.serial = 277

        clear_all_messages()

        self.failIf(self.service.setPlayerImage(MockPlayerImage()), 'with row returning 3, this should fail')

        self.assertEquals(self.service.db.cursorValue.counts["update users set"], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find("setPlayerInfo: update users set") == 0,
                        'first message should be verbose output')
        self.failUnless(msgs[1].find("*ERROR* setPlayerImage: modified 3 rows (expected 1 or 0): update users set") == 0,
                        'second message should be error about rows')


        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test55_buyInPlayer_currencySerialNone(self):
        self.service = pokerservice.PokerService(self.settings)
        self.assertEquals(self.service.buyInPlayer(775, 232, None, 2330), 2330)
    # ----------------------------------------------------------------
    def test56_buyInPlayer_updateRowcountBad(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "UPDATE user2money,user2table SET ":
                    self.failUnless(sql.find("user2table.money = user2table.money + 4") > 0, "money wrong")
                    self.failUnless(sql.find("user2money.amount = user2money.amount - 4") > 0, "amount wrong")
                    self.failUnless(sql.find("user2money.user_serial = 634") > 0, "serial wrong")
                    self.failUnless(sql.find("user2money.currency_serial = 222") > 0, "currency_serial wrong")
                    self.failUnless(sql.find("user2table.user_serial = 634") > 0, "serial wrong")
                    self.failUnless(sql.find("user2table.table_serial = 123") > 0, "table serial wrong")
                    cursorSelf.rowcount = 1
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["UPDATE user2money,user2table SET "])

        self.service = pokerservice.PokerService(self.settings)

        def mockGetMoney(serial, currency_serial): return 4
        def mockDBEvent(event, param1, param2, param3):
            self.assertEquals(param3, 4)
            self.assertEquals(param2, 123)
            self.assertEquals(param1, 634)
            self.assertEquals(event, PacketPokerMonitorEvent.BUY_IN)

        saveGetMoney = self.service.getMoney
        saveDBEvent = self.service.databaseEvent
        self.service.getMoney = mockGetMoney
        self.service.databaseEvent = mockDBEvent

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(4, self.service.buyInPlayer(634, 123, 222, 500))

        self.assertEquals(self.service.db.cursorValue.counts["UPDATE user2money,user2table SET "], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find("buyInPlayer: UPDATE user2money,user2table SET ") == 0,
                        'first message should be verbose output')
        self.failUnless(msgs[1].find("*ERROR* modified 1 rows (expected 0 or 2): UPDATE user2money,user2table SET ") == 0,
                        'second message should be error about rows')

        self.service.getMoney = saveGetMoney
        self.service.databaseEvent = saveDBEvent
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test57_seatPlayer_insertRowcountBad(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "INSERT INTO user2table":
                    self.failUnless(sql.find("654, 936, 100") > 0, "values wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["INSERT INTO user2table"])

        self.service = pokerservice.PokerService(self.settings)

        def mockDBEvent(event, param1, param2):
            self.assertEquals(param2, 936)
            self.assertEquals(param1, 654)
            self.assertEquals(event, PacketPokerMonitorEvent.SEAT)

        saveDBEvent = self.service.databaseEvent
        self.service.databaseEvent = mockDBEvent
        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failIf(self.service.seatPlayer(654, 936, 100), "bad rows should cause error")

        self.assertEquals(self.service.db.cursorValue.counts["INSERT INTO user2table"], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find("seatPlayer: INSERT INTO user2table") == 0,
                        'first message should be verbose output')
        self.failUnless(msgs[1].find("*ERROR* inserted 0 rows (expected 1): INSERT INTO user2table") == 0,
                        'second message should be error about rows')

        self.service.databaseEvent = saveDBEvent
        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test58_movePlayer_selectRowCount0WithMoneyNone(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "SELECT money FROM user2table":
                    self.failUnless(sql.find("user_serial = 9356") > 0, "user_serial wrong")
                    self.failUnless(sql.find("table_serial = 1249") > 0, "from_table_serial wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.row = (None,)
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["SELECT money FROM user2table"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(None, self.service.movePlayer(9356, 1249, 6752))
        self.assertEquals(self.service.db.cursorValue.counts["SELECT money FROM user2table"], 1)
        self.assertEquals(get_messages(), ["movePlayer(9356) expected one row got 0"])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test59_movePlayer_selectRowCount1WithMoneyPositiveUpdateRowCount3(self):
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                self.failUnless(sql.find("user_serial = 8356") > 0, "user_serial wrong")
                if statement == "SELECT money FROM user2table":
                    self.failUnless(sql.find("table_serial = 2249") > 0, "from_table_serial wrong")
                    cursorSelf.rowcount = 1
                    cursorSelf.row = (6000,)
                if statement == "UPDATE user2table":
                    self.failUnless(sql.find("table_serial = 2249") > 0, "from_table_serial wrong")
                    self.failUnless(sql.find("SET table_serial = 6752") > 0, "to_table_serial wrong")
                    cursorSelf.rowcount = 3
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, ["SELECT money FROM user2table",
                                                           "UPDATE user2table"])

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.assertEquals(-1, self.service.movePlayer(8356, 2249, 6752))
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.assertEquals(self.service.db.cursorValue.counts["SELECT money FROM user2table"], 1)
        self.failUnless(msgs[0].find("movePlayer: UPDATE user2table") == 0, "first message wrong")
        self.failUnless(msgs[1].find("*ERROR* modified 3 rows (expected 1): UPDATE user2table") == 0,
                        "second message wrong")

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test60_leavePlayer_updateRowCountTooHigh(self):
        validStatements = ["UPDATE user2money,user2table,pokertables",
                           'DELETE from user2table']
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == 'DELETE from user2table':
                    pass
                elif statement == "UPDATE user2money,user2table,pokertables":
                    self.failUnless(sql.find("tables.serial = 6543") > 0, "table_serial wrong")
                    self.failUnless(sql.find("table_serial = 6543") > 0, "table_serial wrong")
                    self.failUnless(sql.find("user_serial = 236") > 0, "user_serial wrong")
                    cursorSelf.rowcount = 12
                    cursorSelf.row = []
                elif statement == "UPDATE user2table":
                    self.failUnless(sql.find("table_serial = 2249") > 0, "from_table_serial wrong")
                    self.failUnless(sql.find("SET table_serial = 6752") > 0, "to_table_serial wrong")
                    cursorSelf.rowcount = 3
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)

        self.service = pokerservice.PokerService(self.settings)

        def mockDBEvent(event, param1, param2):
            self.assertEquals(param2, 6543)
            self.assertEquals(param1, 236)
            self.assertEquals(event, PacketPokerMonitorEvent.LEAVE)

        saveDBEvent = self.service.databaseEvent
        self.service.databaseEvent = mockDBEvent

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failIf(self.service.leavePlayer(236, 6543, 8999))
        for statement in validStatements:
            self.assertEquals(self.service.db.cursorValue.counts[statement], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 4)
        self.failUnless(msgs[0].find('leavePlayer UPDATE user2money,user2table,pokertables') == 0)
        self.failUnless(msgs[1].find('*ERROR* modified 12 rows (expected 0 or 1): UPDATE user2money,user2table,pokertables') == 0)
        self.failUnless(msgs[2].find('leavePlayer DELETE from user2table') == 0)
        self.failUnless(msgs[3].find('*ERROR* modified 0 rows (expected 1): DELETE from user2table') == 0)

        self.service.db = oldDb
        self.service.databaseEvent = saveDBEvent
    # ----------------------------------------------------------------
    def test61_updatePlayerRake_amountAsZero(self):
        self.service = pokerservice.PokerService(self.settings)
        clear_all_messages()
        self.failUnless(self.service.updatePlayerRake(7355, 1026, 0))
        self.assertEquals(get_messages(), [])
    # ----------------------------------------------------------------
    def test62_updatePlayerRake_updateReturns0Rows(self):
        validStatements = ["UPDATE user2money SET"]
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "UPDATE user2money SET":
                    self.failUnless(sql.find("rake + 77") > 0, "amount value wrong")
                    self.failUnless(sql.find("points + 77") > 0, "amount value wrong")
                    self.failUnless(sql.find("user_serial = 742") > 0, "user_serial wrong")
                    self.failUnless(sql.find("currency_serial = 852") > 0, "currency_serial wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failIf(self.service.updatePlayerRake(852, 742, 77))
        for statement in validStatements:
            self.assertEquals(self.service.db.cursorValue.counts[statement], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find('updatePlayerRake: UPDATE user2money SET') == 0,
                        "Missing expected string in: " + msgs[0])
        self.failUnless(msgs[1].find('*ERROR* modified 0 rows (expected 1): UPDATE user2money SET') == 0,
                        "Missing expected string in: " +  msgs[1])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test63_updatePlayerMoney_amountAsZero(self):
        self.service = pokerservice.PokerService(self.settings)
        clear_all_messages()
        self.failUnless(self.service.updatePlayerMoney(7355, 1026, 0))
        self.assertEquals(get_messages(), [])
    # ----------------------------------------------------------------
    def test64_updatePlayerMoney_updateReturns0Rows(self):
        validStatements = ["UPDATE user2table SET"]
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "UPDATE user2table SET":
                    self.failUnless(sql.find("money + 77") > 0, "amount value wrong")
                    self.failUnless(sql.find("bet - 77") > 0, "amount value wrong")
                    self.failUnless(sql.find("user_serial = 742") > 0, "user_serial wrong")
                    self.failUnless(sql.find("table_serial = 852") > 0, "currency_serial wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failIf(self.service.updatePlayerMoney(742, 852, 77))
        for statement in validStatements:
            self.assertEquals(self.service.db.cursorValue.counts[statement], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find('updatePlayerMoney: UPDATE user2table SET') == 0,
                        "Missing expected string in: " + msgs[0])
        self.failUnless(msgs[1].find('*ERROR* modified 0 rows (expected 1): UPDATE user2table SET') == 0,
                        "Missing expected string in: " +  msgs[1])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test64_updatePlayerMoney_updateReturns0Rows(self):
        validStatements = ["UPDATE user2table SET"]
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "UPDATE user2table SET":
                    self.failUnless(sql.find("money + 77") > 0, "amount value wrong")
                    self.failUnless(sql.find("bet - 77") > 0, "amount value wrong")
                    self.failUnless(sql.find("user_serial = 742") > 0, "user_serial wrong")
                    self.failUnless(sql.find("table_serial = 852") > 0, "currency_serial wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.failIf(self.service.updatePlayerMoney(742, 852, 77))
        for statement in validStatements:
            self.assertEquals(self.service.db.cursorValue.counts[statement], 1)
        msgs = get_messages()
        self.assertEquals(len(msgs), 2)
        self.failUnless(msgs[0].find('updatePlayerMoney: UPDATE user2table SET') == 0,
                        "Missing expected string in: " + msgs[0])
        self.failUnless(msgs[1].find('*ERROR* modified 0 rows (expected 1): UPDATE user2table SET') == 0,
                        "Missing expected string in: " +  msgs[1])

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test65_createTable_insertFailsAndLasRowNotThere(self):
        validStatements = ["INSERT pokertables", 'REPLACE INTO route']
        class MockCursor(MockCursorBase):
            def insert_id(mcBase): return 1567
            def statementActions(cursorSelf, sql, statement):
                if statement == "INSERT pokertables":
                    cursorSelf.rowcount = 0
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)


        self.service = pokerservice.PokerService(self.settings)
        self.service.dirs = ['%s/../conf' % SCRIPT_DIR]

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.service.tables = {}
        table = self.service.createTable("bobby", { 'seats' : 7, 'currency_serial' : 2663,
                                                    'name': "This", 'variant' : 'omaha',
                                                    'betting_structure' : "2-4-limit" })
        self.assertEquals(self.service.tables[1567], table)
        self.assertEquals(table.owner, 'bobby')
        self.assertEquals(table.game.name, "This")
        self.assertEquals(table.game.variant, "omaha")
        self.assertEquals(table.game.max_players, 7)
        self.assertEquals(table.currency_serial, 2663)

        for statement in validStatements:
            self.assertEquals(self.service.db.cursorValue.counts[statement], 1)
        msgs = get_messages()
        self.failUnless(len(msgs) >= 3, "There should be at least three output messages")
        self.failUnless(search_output('createTable: INSERT pokertables'))
        self.failUnless(search_output('*ERROR* inserted 0 rows (expected 1): INSERT pokertables'))
        self.failUnless(search_output('table created : This'))

        self.service.db = oldDb
    # ----------------------------------------------------------------
        # NOTE: these test below (65a) can be used to replace
        # the above test 65 above if sr #2273 is ever closed.

#     def test65a_createTable_insertFailsProperly(self):
#         validStatements = ["INSERT pokertables"]
#         class MockCursor(MockCursorBase):
#             def insert_id(mcBase): return 1567
#             def statementActions(cursorSelf, sql, statement):
#                 if statement == "INSERT pokertables":
#                     cursorSelf.rowcount = 0
#                     cursorSelf.row = []
#             def __init__(cursorSelf):
#                 MockCursorBase.__init__(cursorSelf, self, validStatements)


#         self.service = pokerservice.PokerService(self.settings)
#         self.service.dirs = ['%s/../conf' % SCRIPT_DIR]

#         oldDb = self.service.db
#         self.service.db = MockDatabase(MockCursor)

#         clear_all_messages()

#         self.service.tables = {}
#         table = self.service.createTable("bobby", { 'seats' : 7, 'currency_serial' : 2663,
#                                                     'name': "This", 'variant' : 'omaha',
#                                                     'betting_structure' : "2-4-limit" })
#         self.failIf(self.service.tables.has_key(1567), "Table Should not have been created, INSERT 0 rows!")
#         self.assertEquals(table, None)

#         for statement in validStatements:
#             self.assertEquals(self.service.db.cursorValue.counts[statement], 1)
#         msgs = get_messages()
#         self.failUnless(len(msgs) >= 2, "There should be at least two output messages")
#         self.failUnless(search_output('createTable: INSERT pokertables'))
#         self.failUnless(search_output('*ERROR* inserted 0 rows (expected 1): INSERT pokertables'))

#         self.service.db = oldDb
    # ----------------------------------------------------------------
    def test65b_createTable_insertSucceedsWithLargerThan1ReturnedWithLastRowThere(self):
        validStatements = ["INSERT pokertables", 'REPLACE INTO route']
        class MockCursor(MockCursorBase):
            def insert_id(mcBase): return 1567
            def statementActions(cursorSelf, sql, statement):
                if statement == "INSERT pokertables":
                    cursorSelf.rowcount = 3
                    cursorSelf.row = []
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)


        self.service = pokerservice.PokerService(self.settings)
        self.service.dirs = ['%s/../conf' % SCRIPT_DIR]

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        clear_all_messages()

        self.service.tables = {}
        table = self.service.createTable("bobby", { 'seats' : 7, 'currency_serial' : 2663,
                                                    'name': "This", 'variant' : 'omaha',
                                                    'betting_structure' : "2-4-limit" })
        self.assertEquals(self.service.tables[1567], table)
        self.assertEquals(table.owner, 'bobby')
        self.assertEquals(table.game.name, "This")
        self.assertEquals(table.game.variant, "omaha")
        self.assertEquals(table.game.max_players, 7)
        self.assertEquals(table.currency_serial, 2663)

        for statement in validStatements:
            self.assertEquals(self.service.db.cursorValue.counts[statement], 1)
        msgs = get_messages()
        self.failUnless(len(msgs) >= 3, "There should be at least three output messages")
        self.failUnless(search_output('createTable: INSERT pokertables'))
        self.failUnless(search_output('*ERROR* inserted 3 rows (expected 1): INSERT pokertables'))
        self.failUnless(search_output('table created : This'))

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test66_deleteTable_deleteRowsNot1(self):
        validStatements = ["delete from  pokertables"]
        class MockCursor(MockCursorBase):
            def statementActions(cursorSelf, sql, statement):
                if statement == "delete from  pokertables":
                    cursorSelf.rowcount = 3
                    cursorSelf.row = []
                    self.failUnless(sql.find("serial = 7775") > 0, "serial value wrong")
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        class MockGame():
            def __init__(mgSelf):
                mgSelf.id = 7775
                mgSelf.name =  "Mocky"
        game = MockGame()
        self.service.tables = {7775: game}
        class MockTable():
            def __init__(mtSelf): mtSelf.game = game

        clear_all_messages()

        table = self.service.deleteTable(MockTable())

        self.assertEquals(self.service.tables, {})

        for statement in validStatements:
            self.assertEquals(self.service.db.cursorValue.counts[statement], 1)

        msgs = get_messages()
        self.failUnless(len(msgs) == 3, "Expected excatly three messages")
        self.assertEquals(msgs[0], 'table Mocky/7775 removed from server')
        self.failUnless(msgs[1].find('deleteTable: delete from  pokertables') == 0)
        self.failUnless(msgs[2].find('*ERROR* deleted 3 rows (expected 1): delete from  pokertables') == 0)

        self.service.db = oldDb
    # ----------------------------------------------------------------
    def test67_broadcast(self):
        """test67_broadcast
        Full Coverage for the PokerService broadcast method"""
        class MockPacket(): pass
        packet = MockPacket()

        class MockAvatar():
            def __init__(maSelf, desc):
                maSelf.name = desc
                maSelf.packets = []
            def __str__(maSelf): return maSelf.name
            def setProtocol(maSelf, val): maSelf.protocol = val
            def sendPacketVerbose(maSelf, packet): maSelf.packets.append(packet)

        self.service = pokerservice.PokerService(self.settings)

        avatarList = []
        avatarList.append(MockAvatar("Without protocol"))
        avatarList.append(MockAvatar("Protocol is None"))
        avatarList[1].setProtocol(None)
        avatarList.append(MockAvatar("Protocol is False"))
        avatarList[2].setProtocol(False)
        avatarList.append(MockAvatar("Protocol is True"))
        avatarList[3].setProtocol(True)

        self.service.avatars = avatarList

        clear_all_messages()
        self.service.broadcast(packet)
        msgs = get_messages()

        for ii in [ 0, 1, 2]: self.assertEquals(avatarList[ii].packets, [])
        self.assertEquals(avatarList[3].packets, [packet])

        self.failUnless(len(msgs) == 3, "Expected exactly three messages")
        for (ii, value) in [ (0, "Without protocol"), (1, "Protocol is None"),
                             (2, "Protocol is False")]:
            self.assertEquals(msgs[ii], "broadcast: avatar %s excluded" % value)
    # ----------------------------------------------------------------
    def test68_messageCheck(self):
        validStatements = ["SELECT serial,message FROM messages",
                           "UPDATE messages SET"]
        class MockCursor(MockCursorBase):
            def fetchall(mcSelf): return mcSelf.rows
            def statementActions(cursorSelf, sql, statement):
                if statement == "SELECT serial,message FROM messages":
                    cursorSelf.rowcount = 2
                    cursorSelf.rows = [ (7325, "Greeting 1"), (22235, "Goodbye") ]
                elif statement == "UPDATE messages SET":
                    if cursorSelf.counts["UPDATE messages SET"] == 1:
                        self.failUnless(sql.find('serial = 7325') > 0, "first serial in update wrong")
                    else:
                        self.failUnless(sql.find('serial = 22235') > 0, "second serial in update wrong")
                    cursorSelf.rowcount = 0
                    cursorSelf.rows = [ ]
            def __init__(cursorSelf):
                MockCursorBase.__init__(cursorSelf, self, validStatements)
        class MockAvatar():
            def __init__(maSelf, desc):
                maSelf.name = desc
                maSelf.packets = []
                maSelf.protocol = True
            def sendPacketVerbose(maSelf, packet): maSelf.packets.append(packet)

        self.service = pokerservice.PokerService(self.settings)

        oldDb = self.service.db
        self.service.db = MockDatabase(MockCursor)

        self.service.avatars = [ MockAvatar("Joe") ]

        # Set up Deffered to be sure callback worked.  We should get a
        # reactor/deferred error on the test if the timer works wrong.
        deferredMessageCheck = defer.Deferred()
        def testThatMessageCheckTimerWorked():
            self.assertEquals(get_messages(), [])
            deferredMessageCheck.callback(True)
            self.service.db = oldDb

        # Set up fake message Check for callback.
        self.service.realMessageCheck = self.service.messageCheck
        self.service.messageCheck = testThatMessageCheckTimerWorked

        clear_all_messages()
        self.service.delays['messages'] = 3

        self.service.realMessageCheck()

        self.assertEquals(self.service.db.cursorValue.counts["SELECT serial,message FROM messages"], 1)
        self.assertEquals(self.service.db.cursorValue.counts["UPDATE messages SET"], 2)
        self.assertEquals(len(self.service.avatars[0].packets), 2)
        self.assertEquals(self.service.avatars[0].packets[0].string, "Greeting 1")
        self.assertEquals(self.service.avatars[0].packets[1].string, "Goodbye")

        self.assertEquals(get_messages(), [])

        clear_all_messages()
        return deferredMessageCheck
##############################################################################
class SSLContextFactoryCoverage(unittest.TestCase):
    # ----------------------------------------------------------------
    def test01_initNoHeader(self):
        class MockSettings():
            def headerGet(msSelf, path): return ""
        scf = pokerservice.SSLContextFactory(MockSettings())
        self.assertEquals(scf.pem_file, None)
    # ----------------------------------------------------------------
    def test02_initNoneExist(self):
        class MockSettings():
            def headerGet(msSelf, path): return "/this/goes/nowhere /and/this/does/not/either"
        scf = pokerservice.SSLContextFactory(MockSettings())
        self.assertEquals(scf.pem_file, None)
    # ----------------------------------------------------------------
    def test03_oneGoodFile(self):
        tmpdir = tempfile.mkdtemp()
        filename = os.path.join(tmpdir, "poker.pem")
        f = open(filename, "w")
        f.close()
        class MockSettings():
            def headerGet(msSelf, path): return tmpdir
        scf = pokerservice.SSLContextFactory(MockSettings())
        self.assertEquals(scf.pem_file, filename)

        shutil.rmtree(tmpdir)
    # ----------------------------------------------------------------
    def test04_secondFileFavored(self):
        tmpdir1 = tempfile.mkdtemp()
        filename1 = os.path.join(tmpdir1, "poker.pem")
        f = open(filename1, "w")
        f.close()
        tmpdir2 = tempfile.mkdtemp()
        filename2 = os.path.join(tmpdir2, "poker.pem")
        f = open(filename2, "w")
        f.close()
        class MockSettings():
            def headerGet(msSelf, path): return tmpdir1 + " " + tmpdir2
        scf = pokerservice.SSLContextFactory(MockSettings())
        self.assertEquals(scf.pem_file, filename2)

        shutil.rmtree(tmpdir1)
        shutil.rmtree(tmpdir2)
    # ----------------------------------------------------------------
    def test05_getContext(self):
        from OpenSSL import SSL
        tmpdir = tempfile.mkdtemp()
        filename = os.path.join(tmpdir, "poker.pem")
        f = open(filename, "w")
        f.close()

        class MockSettings():
            def headerGet(msSelf, path): return tmpdir

        scf = pokerservice.SSLContextFactory(MockSettings())
        self.assertEquals(scf.pem_file, filename)

        class MockContext():
            def __init__(mcSelf, val):
                self.assertEquals(SSL.SSLv23_METHOD, val)
                mcSelf.testerData = "Stuff"
            def use_certificate_file(mcSelf, file):
                self.assertEquals(scf.pem_file, file)
            def use_privatekey_file(mcSelf, file):
                self.assertEquals(scf.pem_file, file)

        saveContext = SSL.Context
        SSL.Context = MockContext

        context = scf.getContext()
        self.assertEquals(context.testerData, "Stuff")

        SSL.Context = saveContext
        shutil.rmtree(tmpdir)
##############################################################################
from pokernetwork.pokerservice import PokerTree, PokerSOAP, PokerREST, PokerXMLRPC
class MockRequestBase():
    def __init__(mrSelf):
        mrSelf.method = "GET"
class PokerTreeCoverageTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def setUp(self):
        testclock._seconds_reset()
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        self.settings.header = self.settings.doc.xpathNewContext()
    # ----------------------------------------------------------------
    def tearDown(self):
        if hasattr(self, 'service'):
            d = self.service.stopService()
            return d
    # ----------------------------------------------------------------
    def test01_init(self):
        self.service = pokerservice.PokerService(self.settings)
        pt = pokerservice.PokerTree(self.service)
        self.assertEquals(pt.service, self.service)
        for (child, cl) in [ ("RPC2", PokerXMLRPC), ("SOAP", PokerSOAP) ]:
            self.failUnless(pt.children.has_key(child), "Missing child of PokerTree: " + child)
            self.failUnless(isinstance(pt.children[child], cl))
            self.assertEquals(pt.getChildWithDefault(child, MockRequestBase()).service, self.service)
    # ----------------------------------------------------------------
    def test02_initNoSoap(self):
        self.service = pokerservice.PokerService(self.settings)
        class MockPokerSOAP():
            def __init__(mpsSelf, service):
                self.assertEquals(self.service, service)
                raise Exception("Force SOAP unavailable")
        savePokerSoap = pokerservice.PokerSOAP
        pokerservice.PokerSOAP = MockPokerSOAP

        pt = pokerservice.PokerTree(self.service)

        for (childStr, cl) in [ ("RPC2", PokerXMLRPC) ]:
            self.failUnless(pt.children.has_key(childStr), "Missing child of PokerTree: " + childStr)
            self.failUnless(isinstance(pt.children[childStr], cl))
            self.assertEquals(pt.getChildWithDefault(childStr, MockRequestBase()).service, self.service)

        self.failIf(pt.children.has_key("SOAP"), "SOAP should be disabled")
        child = pt.getChildWithDefault('SOAP', MockRequestBase())
        self.assertEquals(child.code, 404)
        self.assertEquals(child.brief, 'No Such Resource')

        pokerservice.PokerSOAP = savePokerSoap
    # ----------------------------------------------------------------
    def test03_render(self):
        self.service = pokerservice.PokerService(self.settings)
        pt = pokerservice.PokerTree(self.service)
        self.assertEquals(pt.render(MockRequestBase()), "Use /RPC2 or /SOAP")
##############################################################################
from pokernetwork.pokersite import PokerImageUpload, PokerAvatarResource, PokerResource
class PokerRestTreeCoverageTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def setUp(self):
        testclock._seconds_reset()
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        self.settings.header = self.settings.doc.xpathNewContext()
    # ----------------------------------------------------------------
    def tearDown(self):
        if hasattr(self, 'service'):
            d = self.service.stopService()
            return d
    # ----------------------------------------------------------------
    def test01_init(self):
        self.service = pokerservice.PokerService(self.settings)
        prt = pokerservice.PokerRestTree(self.service)
        self.assertEquals(prt.service, self.service)
        self.assertEquals(prt.verbose, self.service.verbose)
        for (child, cl) in [ ("POKER_REST", PokerResource), ("UPLOAD", PokerImageUpload),
                             ("AVATAR", PokerAvatarResource) ]:
            self.failUnless(prt.children.has_key(child), "Missing child of PokerTree: " + child)
            self.failUnless(isinstance(prt.children[child], cl))
            self.assertEquals(prt.getChildWithDefault(child, MockRequestBase()).service, self.service)
    # ----------------------------------------------------------------
    def test02_render(self):
        self.service = pokerservice.PokerService(self.settings)
        prt = pokerservice.PokerRestTree(self.service)
        self.assertEquals(prt.render(MockRequestBase()), "Use /POKER_REST or /UPLOAD or /AVATAR or /TOURNEY_START")
##############################################################################
# The following Mockups are used for PokerXML and its subclasses.

class MockAvatarForPokerXML():
    def __init__(self, val):
        self.name = val
        self.packetList = []
        self.packetsQueuedCount = 0
    def handlePacket(self, packet):
        self.packetList.append(packet)
        return [ PacketPing() ]
    def queuePackets(self):
        self.packetsQueuedCount += 1

class MockSessionForPokerXML():
    pass

# To use MockRequestForPokerXML, you should expect to test the contents of
# the following variables after running your test function:
#    service.avatar
#    service.createAvatarCount
#    service.oldAvatars
class MockServiceForPokerXML():
    def __init__(self, avatar = None):
        self.verbose = 6
        if avatar:
            self.avatar = avatar
        else:
            self.avatar = None
        self.createAvatarCount = 0
        self.oldAvatars = []
        self.destroyedAvatars = []

    def createAvatar(self):
        if hasattr(self, 'avatar') and self.avatar:
            self.oldAvatars.append(self.avatar)
        self.avatar = MockAvatarForPokerXML("MOCK_CREATE_AVATAR_%d" % self.createAvatarCount)
        self.createAvatarCount += 1
        return self.avatar

    def destroyAvatar(self, avatar):
        self.destroyedAvatars.append(avatar)

# To use MockRequestForPokerXML, you should expect to test the contents of
# the following variables after running your test function:
#    request.headerData
class MockRequestForPokerXML():
    def __init__(self, content):
        self.content = content
        self.headerData = {}

    def setHeader(self, header, value):
        if not self.headerData.has_key(header):
            self.headerData[header] = []
        self.headerData[header].append(value)

class MockContentForPokerXML():
    def __init__(self, data):
        self.data = data
    def read(self):
        return self.data
    def seek(self, start, finish):
        pass

class PokerXMLCoverageTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def setUp(self):
        testclock._seconds_reset()
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        self.settings.header = self.settings.doc.xpathNewContext()
    # ----------------------------------------------------------------
    def tearDown(self):
        if hasattr(self, 'service'):
            d = self.service.stopService()
            return d
    # ----------------------------------------------------------------
    def test01_getRequestCookie_hasInstanceVariable(self):
        class MockRequestWithCookie(MockRequestBase):
            def __init__(mrSelf):
                mrSelf.cookies = [ 'thisone', 'notthisone' ]

        self.assertEquals(pokerservice._getRequestCookie(MockRequestWithCookie()),
                          'thisone')
    # ----------------------------------------------------------------
    def test02_getRequestCookie_callsGetCookie(self):
        class MockRequestWithCookie(MockRequestBase):
            def __init__(mrSelf, val):
                mrSelf.cookies = None
                mrSelf.sitepath = val
            def getCookie(mrSelf, stuff):
                self.assertEquals(stuff, "TWISTED_SESSION_one_two_three")
                return "called_getcookie"

        caughtIt = False
        try:
            self.assertEquals(pokerservice._getRequestCookie(MockRequestWithCookie("notalist")),
                              'thisone')
            self.failIf(True, "We should have caught a TypeError")
        except TypeError, te:
            self.assertEquals(te.__str__(), 'can only concatenate list (not "str") to list')
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught a TypeError!")

        self.assertEquals(pokerservice._getRequestCookie(MockRequestWithCookie(['one', 'two', 'three'])),
                           "called_getcookie")
    # ----------------------------------------------------------------
    def test03_init(self):
        self.service = pokerservice.PokerService(self.settings)
        px = pokerservice.PokerXML(self.service)
        self.assertEquals(px.service, self.service)
        self.assertEquals(px.verbose, self.service.verbose)
        self.assertNotEquals(pokerservice.PokerXML.encoding, "")
        self.assertNotEquals(pokerservice.PokerXML.encoding, None)
    # ----------------------------------------------------------------
    def test04_render(self):
        service = MockServiceForPokerXML()
        pxml = pokerservice.PokerXML(service)
        request = MockRequestForPokerXML(MockContentForPokerXML("hello"))

        clear_all_messages()

        caughtIt = False
        try:
            pxml.render(request)
            self.failIf(True, "We should have caught a NotImplementedError")
        except NotImplementedError:
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught a NotImplementedError!")

        self.assertEquals(request.headerData,
                          {'Content-type': ['text/xml; charset="ISO-8859-1"']})
        self.failUnless(search_output('render hello'), "render hello should occur in output!")
    # ----------------------------------------------------------------
    def test04a_maps2result(self):
        service = MockServiceForPokerXML()
        pxml = pokerservice.PokerXML(service)
        request = MockRequestForPokerXML(MockContentForPokerXML("hello"))

        caughtIt = False
        try:
            pxml.maps2result(request, {})
            self.failIf(True, "We should have caught a NotImplementedError")
        except NotImplementedError:
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught a NotImplementedError!")
    # ----------------------------------------------------------------
    def test05_render_noEncoding(self):
        service = MockServiceForPokerXML()
        pxml = pokerservice.PokerXML(service)
        request = MockRequestForPokerXML(MockContentForPokerXML("hello"))

        clear_all_messages()

        caughtIt = False
        pxml.encoding = None
        try:
            pxml.render(request)
            self.failIf(True, "We should have caught a NotImplementedError")
        except NotImplementedError:
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught a NotImplementedError!")

        self.assertEquals(request.headerData, {'Content-type': ['text/xml']})

        self.assertEquals(get_messages(), ['render hello'])
    # ----------------------------------------------------------------
    def test06_errorFunction(self):
        service = MockServiceForPokerXML()
        pxml = pokerservice.PokerXML(service)

        clear_all_messages()
        pxml.error("Test an error")
        self.assertEquals(get_messages(), ['*ERROR* Test an error'])
##############################################################################
class PokerXMLRPCCoverageTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def test01_render_dummyXMLCall(self):
        service = MockServiceForPokerXML()
        pxmlrpc = pokerservice.PokerXMLRPC(service)
        request = MockRequestForPokerXML(MockContentForPokerXML("""<?xml version="1.0"?>
<methodCall>
<methodName>examples.Nothing</methodName>
<params>
<param>  <value><i4>41</i4></value>  </param>
</params></methodCall>"""))

        clear_all_messages()
        self.assertEquals(pxmlrpc.render(request), """<?xml version='1.0'?>
<methodResponse>
<params>
<param>
<value><array><data>
</data></array></value>
</param>
</params>
</methodResponse>
""")
        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.destroyedAvatars[0].name, "MOCK_CREATE_AVATAR_0")
        self.assertEquals(service.destroyedAvatars[0], service.avatar)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['138'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        msgs = get_messages()
        self.failUnless(len(msgs) >= 2, "Missing Message Output")
        self.failUnless(search_output('render '), "Missing render output")
        self.failUnless(search_output('result_string '), "Missing result_string output")
    # ----------------------------------------------------------------
##############################################################################
# Mock Ups for PokerREST

# Variables to check after tests for MockRequestForPokerREST
#   expireCount, notifyFunctions
#   (you should call each notifyFunction and make sure it DTRT

class MockRequestForPokerREST(MockRequestForPokerXML):
    def __init__(mrSelf, content):
        mrSelf.args = {}
        mrSelf.cookieRequests = []
        MockRequestForPokerXML.__init__(mrSelf, content)
    def getCookie(mrSelf, stuff):
        mrSelf.cookieRequests.append(stuff)
        return "DUMMY_COOKIE_%d" % len(mrSelf.cookieRequests)

# Variables to check after tests for MockSessionForPokerREST:
#   expireCount, notifyFunctions
#   (you should call each notifyFunction and make sure it DTRT
class MockSessionForPokerREST(MockSessionForPokerXML):
    def __init__(msSelf):
        msSelf.expireCount = 0
        msSelf.notifyFunctions = []
    def expire(msSelf): msSelf.expireCount += 1
    def notifyOnExpire(msSelf, fun):
        msSelf.notifyFunctions.append(fun)

class MockRequestForRESTWithSession(MockRequestForPokerREST):
    def getSession(mrSelf):
        if not hasattr(mrSelf, 'session') or not mrSelf.session:
            mrSelf.session = MockSessionForPokerREST()
        return mrSelf.session

class PokerRESTCoverageTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def test01_render_dummyRESTCall(self):
        service = MockServiceForPokerXML()
        prest = pokerservice.PokerREST(service)
        request = MockRequestForPokerREST(MockContentForPokerXML("""
{"type" : "41"}
"""))

        clear_all_messages()
        val = prest.render(request)
        self.assertEquals(val, """[{"message": "Invalid type name 41", "code": 0, "type": "PacketError", "other_type": 3}]""")

        self.assertEquals(request.cookieRequests, [])
        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.destroyedAvatars[0].name, "MOCK_CREATE_AVATAR_0")
        self.assertEquals(service.destroyedAvatars[0], service.avatar)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['88'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        msgs = get_messages()
        self.failUnless(len(msgs) >= 2, "Missing Message Output")
        self.failUnless(search_output('render '), "Missing render output")
        self.failUnless(search_output('result_string '), "Missing result_string output")
    # ----------------------------------------------------------------
    def test02_render_withNewSession_withjsonp(self):
        class MockServiceWithoutAvatar(MockServiceForPokerXML):
            def __init__(self, avatar = None):
                MockServiceForPokerXML.__init__(self, avatar)
                if hasattr(self, "avatar") and not avatar:
                    del self.avatar

        service = MockServiceWithoutAvatar()
        prest = pokerservice.PokerREST(service)
        request = MockRequestForRESTWithSession(MockContentForPokerXML("""
{"type" : "41"}
"""))
        request.args = { 'session' : ['new'], 'name' : ['joe'], 'jsonp' : ["JSON_PREFIX"],
                         'packet' : ["""{ "type" : "PacketPing" }"""] }

        clear_all_messages()
        val = prest.render(request)
        self.assertEquals(val, """JSON_PREFIX([{"type": "PacketPing"}])""")

        self.assertEquals(request.session.expireCount, 0)
        self.assertEquals(len(request.session.notifyFunctions), 1)
        self.failUnless(hasattr(request.session, 'avatar'))

        self.assertEquals("""JSON_PREFIX([{"type": "PacketPing"}])""", val)
        self.assertEquals(len(service.destroyedAvatars), 0)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(service.avatar.packetList), 1)
        self.assertEquals(service.avatar.packetList[0].type, PACKET_PING)
        self.assertEquals(service.avatar.packetsQueuedCount, 1)
        self.assertEquals(service.avatar.name, 'MOCK_CREATE_AVATAR_0')

        self.assertEquals(request.cookieRequests, ['TWISTED_SESSION_joe'])
        self.assertEquals(request.cookies, [])
        self.assertEquals(request.sitepath, ['joe'])

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['37'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        msgs = get_messages()
        self.failUnless(len(msgs) >= 2, "Missing Message Output")
        self.failUnless(search_output('render '), "Missing render output")
        self.failUnless(search_output('result_string JSON_PREFIX'), "Missing result_string output")

        # Now call the notifyFunction and see if does what is expected:
        request.session.notifyFunctions[0]()

        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)
        self.failIf(hasattr(request.session, 'avatar'))
    # ----------------------------------------------------------------
    def test03_render_withSessionYes_HandleMultiplePackets(self):
        class MockAvatarWithMultipleHandle(MockAvatarForPokerXML):
            def handlePacket(self, packet):
                MockAvatarForPokerXML.handlePacket(self, packet)
                return [PacketSerial(serial = 12), PacketPing()]

        class MockServiceWithMultipleHandleAvatar(MockServiceForPokerXML):
            def __init__(self, avatar = None):
                MockServiceForPokerXML.__init__(self, avatar)
                if hasattr(self, "avatar") and not avatar:
                    del self.avatar

            def createAvatar(self):
                if hasattr(self, 'avatar') and self.avatar:
                    self.oldAvatars.append(self.avatar)
                self.avatar = MockAvatarWithMultipleHandle("MOCK_CREATE_AVATAR_%d" % self.createAvatarCount)
                self.createAvatarCount += 1
                return self.avatar

        service = MockServiceWithMultipleHandleAvatar()
        prest = pokerservice.PokerREST(service)
        request = MockRequestForRESTWithSession(MockContentForPokerXML("""
{"type" : "41"}
"""))
        request.args = { 'session' : ['yes'], 'name' : ['joe'], 'jsonp' : ["JSON_PREFIX"],
                         'packet' : ["""{ "type" : "PacketPing" }"""] }
        request.cookies = None

        clear_all_messages()
        val = prest.render(request)

        self.assertEquals(request.session.expireCount, 0)
        self.assertEquals(len(request.session.notifyFunctions), 1)
        self.failUnless(hasattr(request.session, 'avatar'))

        self.assertEquals('JSON_PREFIX([{"type": "PacketSerial", "serial": 12, "cookie": "DUMMY_COOKIE_2"}, {"type": "PacketPing"}])', val)
        self.assertEquals(len(service.destroyedAvatars), 0)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(service.avatar.packetList), 1)
        self.assertEquals(service.avatar.packetList[0].type, PACKET_PING)
        self.assertEquals(service.avatar.packetsQueuedCount, 1)
        self.assertEquals(service.avatar.name, 'MOCK_CREATE_AVATAR_0')

        self.assertEquals(request.cookieRequests, ['TWISTED_SESSION_joe', 'TWISTED_SESSION_joe'])
        self.assertEquals(request.cookies, None)
        self.assertEquals(request.sitepath, ['joe'])

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['105'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        msgs = get_messages()
        self.failUnless(len(msgs) >= 3, "Missing Message Output")
        self.failUnless(search_output('receive session cookie DUMMY_COOKIE_1'),
                         'Missing receive session cookie')
        self.failUnless(search_output('send session cookie DUMMY_COOKIE_2'),
                         'Missing send session cookie')
        self.failUnless(search_output('render '), "Missing render output")
        self.failUnless(search_output('result_string JSON_PREFIX'), "Missing result_string output")

        # Now call the notifyFunction and see if does what is expected:
        request.session.notifyFunctions[0]()

        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)
        self.failIf(hasattr(request.session, 'avatar'))
    # ----------------------------------------------------------------
    def test04_render_withSessionYes_logout(self):
        class MockAvatarLogout(MockAvatarForPokerXML):
            def handlePacket(self, packet):
                MockAvatarForPokerXML.handlePacket(self, packet)
                return [PacketLogout()]

        class MockServiceLogout(MockServiceForPokerXML):
            def __init__(self, avatar = None):
                MockServiceForPokerXML.__init__(self, avatar)
                if hasattr(self, "avatar") and not avatar:
                    del self.avatar

            def createAvatar(self):
                if hasattr(self, 'avatar') and self.avatar:
                    self.oldAvatars.append(self.avatar)
                self.avatar = MockAvatarLogout("MOCK_CREATE_AVATAR_%d" % self.createAvatarCount)
                self.createAvatarCount += 1
                return self.avatar

        service = MockServiceLogout()
        prest = pokerservice.PokerREST(service)
        request = MockRequestForRESTWithSession(MockContentForPokerXML("""
{"type" : "41"}
"""))
        request.args = { 'session' : ['yes'], 'name' : ['joe'], 'jsonp' : ["JSON_PREFIX"],
                         'packet' : ["""{ "type" : "PacketLogout" }"""] }
        request.cookies = None

        clear_all_messages()
        val = prest.render(request)
        self.assertEquals(val, """JSON_PREFIX([{"type": "PacketLogout"}])""")

        self.assertEquals(request.session.expireCount, 1)
        self.assertEquals(len(request.session.notifyFunctions), 1)
        self.failUnless(hasattr(request.session, 'avatar'))

        self.assertEquals(len(service.destroyedAvatars), 0)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(service.avatar.packetList), 1)
        self.assertEquals(service.avatar.packetList[0].type, PACKET_LOGOUT)
        self.assertEquals(service.avatar.packetsQueuedCount, 0)
        self.assertEquals(service.avatar.name, 'MOCK_CREATE_AVATAR_0')

        self.assertEquals(request.cookieRequests, ['TWISTED_SESSION_joe'])
        self.assertEquals(request.cookies, None)
        self.assertEquals(request.sitepath, ['joe'])

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['39'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        msgs = get_messages()
        self.failUnless(len(msgs) >= 3, "Missing Message Output")
        self.failUnless(search_output('receive session cookie DUMMY_COOKIE_1'),
                         'Missing receive session cookie')
        self.failUnless(search_output('render '), "Missing render output")
        self.failUnless(search_output('result_string JSON_PREFIX'), "Missing result_string output")

        # Now call the notifyFunction and see if does what is expected:
        request.session.notifyFunctions[0]()

        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)
        self.failIf(hasattr(request.session, 'avatar'))
    # ----------------------------------------------------------------
    def test05_render_withSessionYes_Deferred(self):
        resultDeferred = defer.Deferred()
        class MockAvatarDeferred(MockAvatarForPokerXML):
            def handlePacket(self, packet):
                MockAvatarForPokerXML.handlePacket(self, packet)
                return [resultDeferred]

        class MockServiceDeferredAvatar(MockServiceForPokerXML):
            def __init__(self, avatar = None):
                MockServiceForPokerXML.__init__(self, avatar)
                if hasattr(self, "avatar") and not avatar:
                    del self.avatar

            def createAvatar(self):
                if hasattr(self, 'avatar') and self.avatar:
                    self.oldAvatars.append(self.avatar)
                self.avatar = MockAvatarDeferred("MOCK_CREATE_AVATAR_%d" % self.createAvatarCount)
                self.createAvatarCount += 1
                return self.avatar

        class MockRequestRESTForCallback(MockRequestForRESTWithSession):
            def __init__(mrSelf, data):
                MockRequestForRESTWithSession.__init__(mrSelf, data)
                mrSelf.finishCount = 0
                mrSelf.writtenData = ""
            def finish(mrSelf):
                mrSelf.finishCount += 1
            def write(mrSelf, data):
                mrSelf.writtenData += data

        service = MockServiceDeferredAvatar()
        prest = pokerservice.PokerREST(service)
        request = MockRequestRESTForCallback(MockContentForPokerXML("""
{"type" : "41"}
"""))
        request.args = { 'session' : ['yes'], 'name' : ['joe'], 'jsonp' : ["JSON_PREFIX"],
                         'packet' : ["""{ "type" : "PacketPing" }"""] }
        request.cookies = None

        clear_all_messages()
        val = prest.render(request)
        self.assertEquals(val, twisted.web.server.NOT_DONE_YET)

        self.assertEquals(request.session.expireCount, 0)
        self.assertEquals(len(request.session.notifyFunctions), 1)
        self.failUnless(hasattr(request.session, 'avatar'))

        self.assertEquals(len(service.destroyedAvatars), 0)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(service.avatar.packetList), 1)
        self.assertEquals(service.avatar.packetList[0].type, PACKET_PING)
        self.assertEquals(service.avatar.packetsQueuedCount, 0)
        self.assertEquals(service.avatar.name, 'MOCK_CREATE_AVATAR_0')

        self.assertEquals(request.cookieRequests, ['TWISTED_SESSION_joe'])
        self.assertEquals(request.cookies, None)
        self.assertEquals(request.sitepath, ['joe'])

        msgs = get_messages()
        self.failUnless(len(msgs) >= 2, "Missing Message Output")
        self.failUnless(search_output('receive session cookie DUMMY_COOKIE_1'),
                         'Missing receive session cookie')
        self.failUnless(search_output('render '), "Missing render output")

        # Now call the notifyFunction and see if does what is expected:
        request.session.notifyFunctions[0]()

        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)
        self.failIf(hasattr(request.session, 'avatar'))

        # Finally, let's make sure our deferred does the right thing,
        # first testing to verify it has not been rendered, and then
        # calling back and making sure it was rendered

        self.assertEquals(len(request.headerData.keys()), 1)
        self.failIf(request.headerData.has_key('Content-length'))
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        self.assertEquals(request.writtenData, "")
        self.assertEquals(request.finishCount, 0)

        resultDeferred.callback(PacketLogout())

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['39'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        self.assertEquals(request.writtenData, 'JSON_PREFIX([{"type": "PacketLogout"}])')
        self.assertEquals(request.finishCount, 1)
    # ----------------------------------------------------------------
    def test06_render_clearSessions(self):
        service = MockServiceForPokerXML()
        prest = pokerservice.PokerREST(service)
        request = MockRequestForRESTWithSession(MockContentForPokerXML("""
{"type" : "PacketPing"}
"""))
        request.args = { 'session' : ['clear'] }

        clear_all_messages()
        val = prest.render(request)
        self.assertEquals(val, '[{"type": "PacketPing"}]')

        self.assertEquals(request.cookieRequests, [])
        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.destroyedAvatars[0].name, "MOCK_CREATE_AVATAR_0")
        self.assertEquals(service.destroyedAvatars[0], service.avatar)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['24'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        msgs = get_messages()
        self.failUnless(len(msgs) >= 2, "Missing Message Output")
        self.failUnless(search_output('render '), "Missing render output")
        self.failUnless(search_output('result_string '), "Missing result_string output")
    # ----------------------------------------------------------------
##############################################################################
class PokerSOAPCoverageTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def test01_render_dummySOAPCall(self):
        service = MockServiceForPokerXML()
        psoap = pokerservice.PokerSOAP(service)
        request = MockRequestForPokerXML(MockContentForPokerXML("""<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:soapenc="http://schemas.xmlsoap.org/soap/encoding/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
<soap:Body soap:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<SomeMethod>
<Result>
<Packet>
   <type>PacketPing</type>
</Packet>
</Result>
</SomeMethod>
</soap:Body>
</soap:Envelope>"""))

        clear_all_messages()
        val = psoap.render(request)
        self.assertEquals(val, """<?xml version="1.0" encoding="ISO-8859-1"?>
<SOAP-ENV:Envelope
  SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
  xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/"
  xmlns:xsi="http://www.w3.org/1999/XMLSchema-instance"
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
>
<SOAP-ENV:Body>
<returnPacket SOAP-ENC:root="1">
<Result SOAP-ENC:arrayType="ns1:SOAPStruct[0]" xsi:type="SOAP-ENC:Array" xmlns:ns1="http://soapinterop.org/xsd">
</Result>
</returnPacket>
</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
""")
        self.assertEquals(len(service.destroyedAvatars), 1)
        self.assertEquals(service.destroyedAvatars[0].name, "MOCK_CREATE_AVATAR_0")
        self.assertEquals(service.destroyedAvatars[0], service.avatar)
        self.assertEquals(service.oldAvatars, [])
        self.assertEquals(service.createAvatarCount, 1)

        self.assertEquals(len(request.headerData.keys()), 2)
        self.assertEquals(request.headerData['Content-length'],  ['538'])
        self.assertEquals(request.headerData['Content-type'], ['text/xml; charset="ISO-8859-1"'])
        msgs = get_messages()
        self.failUnless(len(msgs) >= 2, "Missing Message Output")
        self.failUnless(search_output("args = [{'Packet': {'type': 'PacketPing'}}]"),
                        'Missing args')
        self.failUnless(search_output('render '), "Missing render output")
        self.failUnless(search_output('result_string '), "Missing result_string output")
    # ----------------------------------------------------------------
##############################################################################
class TourneySelectInfoTestCase(unittest.TestCase):

    def test01_not_found(self):
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <listen tcp="19480" />

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <tourney_select_info>UNLIKELY</tourney_select_info>
  <path>%s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % SCRIPT_DIR
        try:
            self.service = pokerservice.PokerService(xml)
            self.service.setupTourneySelectInfo()
            caught = False
        except exceptions.IOError:
            caught = True
        self.assertEqual(True, caught)

    def test02_no_init(self):
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <listen tcp="19480" />

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <path>%(script_dir)s/../conf</path>
  <tourney_select_info>%(script_dir)s/testfilter.py</tourney_select_info>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}
        try:
            self.service = pokerservice.PokerService(xml)
            self.service.setupTourneySelectInfo()
            caught = False
        except exceptions.AttributeError:
            caught = True
        self.assertEqual(True, caught)

    def test03_no_handle(self):
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <listen tcp="19480" />

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <path>%(script_dir)s/../conf</path>
  <tourney_select_info>%(script_dir)s/testtourney_select_info_no_call.py</tourney_select_info>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}
        try:
            self.service = pokerservice.PokerService(xml)
            self.service.setupTourneySelectInfo()
            caught = False
        except exceptions.AttributeError:
            caught = True
        self.assertEqual(True, caught)

    def test04_ok(self):
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <listen tcp="19480" />

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <tourney_select_info settings="%(script_dir)s/testsettings.xml">%(script_dir)s/testtourney_select_info.py</tourney_select_info>
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}
        self.service = pokerservice.PokerService(xml)
        self.service.setupTourneySelectInfo()
        self.assertEqual(PACKET_POKER_TOURNEY_INFO, self.service.tourneySelectInfo('packet', 'tourneys').type)
        self.assertEqual('tourneys', self.service.tourney_select_info.tourneys)
        self.assertEqual('packet', self.service.tourney_select_info.packet)
        self.assertTrue(self.service.tourney_select_info.settings.path.find('testsettings.xml'))

    def test05_non_specified(self):
        xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" max_joined="1000" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <listen tcp="19480" />

  <refill serial="1" amount="10000000" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <path>%s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % SCRIPT_DIR
        self.service = pokerservice.PokerService(xml)
        self.service.setupTourneySelectInfo()
        self.assertEqual(None, self.service.tourneySelectInfo('packet', 'tourneys'))
##############################################################################
class LadderTestCase(PokerServiceTestCaseBase):

    def createRank(self):
        self.db.db.query("CREATE TABLE rank ( " +
                          "  user_serial INT UNSIGNED NOT NULL," +
                          "  currency_serial INT UNSIGNED NOT NULL," +
                          "  amount BIGINT NOT NULL," +
                          "  rank INT UNSIGNED NOT NULL," +
                          "  percentile TINYINT UNSIGNED DEFAULT 0 NOT NULL )")

    def test01_setupLadder(self):
        self.createRank()
        self.service.startService()
        self.assertEqual(True, self.service.setupLadder())
        self.db.db.query("DROP TABLE rank")
        self.assertEqual(False, self.service.setupLadder())
        self.assertEqual(False, self.service.has_ladder)

    def test02_getLadder(self):
        self.createRank()
        self.service.startService()
        self.assertEqual(True, self.service.setupLadder())
        packet = self.service.getLadder(0, 0, 0)
        self.assertEqual(PACKET_POKER_ERROR, packet.type)
        self.db.db.query("INSERT INTO rank VALUES (1, 2, 3, 4, 5)")
        packet = self.service.getLadder(None, 2, 1)
        self.assertEqual(PACKET_POKER_PLAYER_STATS, packet.type)
        self.assertEqual(0, packet.game_id)
        game_id = 10
        packet = self.service.getLadder(game_id, 2, 1)
        self.assertEqual(game_id, packet.game_id)

# ----------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test07_"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerServiceTestCase))
    suite.addTest(loader.loadClass(RefillTestCase))
    suite.addTest(loader.loadClass(TimerTestCase))
    suite.addTest(loader.loadClass(BreakTestCase))
    suite.addTest(loader.loadClass(TourneyFinishedTestCase))
    suite.addTest(loader.loadClass(TourneyUnregisterTestCase))
    suite.addTest(loader.loadClass(TourneyMovePlayerTestCase))
    suite.addTest(loader.loadClass(TourneyCancelTestCase))
    suite.addTest(loader.loadClass(TourneySatelliteTestCase))
    suite.addTest(loader.loadClass(TourneyManagerTestCase))
    suite.addTest(loader.loadClass(TourneyCreateTestCase))
    suite.addTest(loader.loadClass(ShutdownCheckTestCase))
    suite.addTest(loader.loadClass(ListHandsTestCase))
    suite.addTest(loader.loadClass(SetAccountTestCase))
    suite.addTest(loader.loadClass(UpdatePlayerRakeTestCase))
    suite.addTest(loader.loadClass(MonitorTestCase))
    suite.addTest(loader.loadClass(ListTablesSearchTablesTestCases))
    suite.addTest(loader.loadClass(GetTableBestByCriteriaTestCase))
    suite.addTest(loader.loadClass(TourneySelectTestCase))
    suite.addTest(loader.loadClass(PlayerPlacesTestCase))
    suite.addTest(loader.loadClass(CleanUpTestCase))
    suite.addTest(loader.loadClass(ResthostTestCase))
    suite.addTest(loader.loadClass(PokerFactoryFromPokerServiceTestCase))
    suite.addTest(loader.loadClass(PokerServiceCoverageTests))
    suite.addTest(loader.loadClass(SSLContextFactoryCoverage))
    suite.addTest(loader.loadClass(PokerTreeCoverageTestCase))
    suite.addTest(loader.loadClass(PokerRestTreeCoverageTestCase))
    suite.addTest(loader.loadClass(PokerXMLCoverageTestCase))
    suite.addTest(loader.loadClass(PokerXMLRPCCoverageTestCase))
    suite.addTest(loader.loadClass(PokerRESTCoverageTestCase))
    suite.addTest(loader.loadClass(PokerSOAPCoverageTestCase))
    suite.addTest(loader.loadClass(TourneySelectInfoTestCase))
    suite.addTest(loader.loadClass(TourneyNotifyTestCase))
    suite.addTest(loader.loadClass(LadderTestCase))
    return runner.TrialRunner(
        reporter.VerboseTextReporter,
#       reporter.TextReporter,
#	tracebackFormat='verbose',
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
# compile-command: "( cd .. ; ./config.status tests/test-pokerservice.py tests/test-pokerservice-load.py ) ; ( cd ../tests ; make VERBOSE_T=-1 COVERAGE_FILES='../pokernetwork/pokerservice.py' TESTS='coverage-reset test-pokerservice.py test-pokerservice-load.py coverage-report' check )"
# End:
