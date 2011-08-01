#!/usr/bin/python
# -*- py-indent-offset: 4; coding: iso-8859-1; mode: python -*-
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
# Authors:
#  Loic Dachary <loic@dachary.org>
#
import sys, os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

import libxml2

from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor, defer, error
from twisted.python import failure

twisted.internet.base.DelayedCall.debug = True

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from twisted.python.runtime import seconds

from pokernetwork import pokerservice
from pokernetwork import pokernetworkconfig
from pokernetwork.pokerdatabase import PokerDatabase

settings_xml_server = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="3" ping="300000" autodeal="yes" simultaneous="4" chat="yes" >
  <delays autodeal="20" round="0" position="0" showdown="0" autodeal_max="1" finish="0" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="4" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="4" currency_serial="1" />

  <listen tcp="19480" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

class PokerCrashTestCase(unittest.TestCase):

    def destroyDb(self, arg = None):
        os.system("/usr/bin/mysql -u root -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    def setUpServer(self):
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml_server, len(settings_xml_server))
        settings.header = settings.doc.xpathNewContext()
        #
        # Setup database
        #
        self.db = PokerDatabase(settings)
        #
        # Setup server
        #
        self.service = pokerservice.PokerService(settings)
        self.service.verbose = 6

    # -------------------------------------------------
    def setUp(self):
        self.destroyDb()
        self.setUpServer()

    def tearDown(self):
        self.db.close()
        return self.service.stopService()

    def test01_cleanupCrashedTables(self):
        cursor = self.db.cursor()
        #
        # Although the name is not in the configuration file (settings),
        # it has a matching resthost_serial and is cleanedup
        #
        cursor.execute('INSERT INTO pokertables (serial, name, variant, betting_structure, currency_serial) VALUES (142, "one", "holdem", "2-4", 1)')
        cursor.execute('INSERT INTO user2table (user_serial, table_serial, money, bet) VALUES (1000, 142, 10, 1)')
        cursor.execute("INSERT INTO users (serial, created, name) VALUES (1000, 0, 'testuser')")
        cursor.execute("INSERT INTO user2money (user_serial, currency_serial, amount) VALUES (1000, 1, 0)")
        #
        # resthost_serial does not match, the records are left untouched
        #
        cursor.execute('INSERT INTO pokertables (serial, name, variant, betting_structure, currency_serial, resthost_serial) VALUES (202, "two", "holdem", "2-4", 1, 10)')
        cursor.execute('INSERT INTO user2table (user_serial, table_serial, money, bet) VALUES (1000, 202, 10, 1)')
        #
        # Table1 is in the configuration file and cleaned up even though
        # resthost_serial does not match
        #
        cursor.execute('INSERT INTO pokertables (serial, name, variant, betting_structure, currency_serial, resthost_serial) VALUES (303, "Table1", "holdem", "2-4", 1, 44)')
        self.service.startService()
        cursor.execute("SELECT user_serial,table_serial FROM user2table")
        self.assertEqual(1, cursor.rowcount)
        self.assertEqual((1000, 202), cursor.fetchone())
        cursor.execute("SELECT serial FROM pokertables")
        self.assertEqual((202,), cursor.fetchone())
        cursor.execute("SELECT amount FROM user2money")
        self.assertEqual(11, cursor.fetchone()[0])
        cursor.close()

    def test02_cleanupTourneys_refund(self):
        tourney_serial = '10'
        user_serial = '200'
        buy_in = '300'
        currency_serial = '44'
        cursor = self.db.cursor()
        cursor.execute('INSERT INTO tourneys (serial,name,buy_in,currency_serial) VALUES (%s, "one", %s, %s)', ( tourney_serial, buy_in, currency_serial ))
        cursor.execute('INSERT INTO user2tourney (user_serial,currency_serial,tourney_serial) VALUES (%s,1,%s)', ( user_serial, tourney_serial ))
        cursor.execute('INSERT INTO user2money (user_serial,currency_serial) VALUES (%s,%s)', ( user_serial, currency_serial ))
        cursor.execute('SELECT * FROM tourneys WHERE serial = ' + tourney_serial)
        self.assertEqual(1, cursor.rowcount)
        cursor.execute('SELECT amount FROM user2money WHERE user_serial = %s AND currency_serial = %s', ( user_serial, currency_serial ))
        self.assertEqual((0,), cursor.fetchone())
        self.service.startService()
        cursor.execute('SELECT * FROM tourneys WHERE serial = ' + tourney_serial)
        self.assertEqual(0, cursor.rowcount)
        cursor.execute('SELECT amount FROM user2money WHERE user_serial = %s AND currency_serial = %s', ( user_serial, currency_serial ))
        self.assertEqual((300,), cursor.fetchone())
        cursor.close()

    def test02_cleanupTourneys_restore(self):
        regular_tourney_serial = '10'
        sng_tourney_serial = '40'
        user_serial = '200'
        cursor = self.db.cursor()
        cursor.execute("DELETE FROM tourneys_schedule")
        #
        # Sit and go in 'registering' state is trashed
        #
        cursor.execute('INSERT INTO tourneys (serial,name) VALUES (%s, "one")', sng_tourney_serial)
        cursor.execute('INSERT INTO user2tourney (user_serial,currency_serial,tourney_serial) VALUES (%s,1,%s)', ( user_serial, sng_tourney_serial ))
        cursor.execute('SELECT * FROM tourneys WHERE serial = ' + sng_tourney_serial)
        self.assertEqual(1, cursor.rowcount)
        #
        # Regular in 'registering' state is kept
        #
        cursor.execute('INSERT INTO tourneys (serial,name,sit_n_go,start_time) VALUES (%s, "one", "n", %s)', ( regular_tourney_serial, seconds() + 2000))
        cursor.execute('INSERT INTO user2tourney (user_serial,currency_serial,tourney_serial) VALUES (%s,1,%s)', ( user_serial, regular_tourney_serial ))
        cursor.execute('SELECT * FROM tourneys WHERE serial = ' + regular_tourney_serial)
        self.assertEqual(1, cursor.rowcount)
        #
        # Run cleanupTourneys as a side effect
        #
        self.service.startService()
        #
        # Sanity checks
        #
        self.assertEqual([int(regular_tourney_serial)], self.service.tourneys.keys())
        cursor.execute('SELECT * FROM user2tourney WHERE tourney_serial = %s', regular_tourney_serial)
        self.assertEqual(1, cursor.rowcount)
        cursor.execute('SELECT * FROM user2tourney WHERE tourney_serial = %s', sng_tourney_serial)
        self.assertEqual(0, cursor.rowcount)
        cursor.execute('SELECT * FROM user2tourney')
        self.assertEqual(1, cursor.rowcount)
        cursor.execute('SELECT * FROM tourneys')
        self.assertEqual(1, cursor.rowcount)
        cursor.close()

# -----------------------------------------------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test09"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerCrashTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-servercrash.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokertable.py ../pokernetwork/pokerservice.py  ../pokernetwork/pokerserver.py' TESTS='coverage-reset test-servercrash.py coverage-report' check )"
# End:
