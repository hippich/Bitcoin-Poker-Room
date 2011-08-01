# -*- mode: python -*-
#
# Note: this file is copyrighted by multiple entities; some license their
# copyrights under GPLv3-or-later and some under AGPLv3-or-later.  Read
# below for details.
#
# Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
# Copyright (C) 2008 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C) 2006 Mekensleep <licensing@mekensleep.com>
#                    24 rue vieille du temple 75004 Paris
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
#  Pierre-Andre (05/2006)
#  Loic Dachary <loic@gnu.org>
#  Johan Euphrosine <proppy@aminche.com>
#  Bradley M. Kuhn <bkuhn@ebb.org>
#

import sys, os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

import unittest
import os.path
import types

from tests.testmessages import silence_all_messages, clear_all_messages, get_messages, search_output
silence_all_messages()

from twisted.python.runtime import seconds

from pokernetwork import pokerauth
from pokernetwork.user import User
from pokernetwork import pokernetworkconfig
from pokernetwork.pokerdatabase import PokerDatabase
import libxml2

settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server auto_create_account="no" verbose="6" ping="300000" autodeal="yes" simultaneous="4" chat="yes" >
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19480" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <path>%(script_dir)s/../conf</path>
  <users temporary="BOT"/>
</server>
""" % {'script_dir': SCRIPT_DIR}

settings_alternate_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" simultaneous="4" chat="yes" >
  <delays autodeal="18" round="12" position="60" showdown="30" finish="18" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19480" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <path>NONE/share/poker-engine/conf NONE/etc/poker-network</path>
  <users temporary="BOT"/>
  <auth script="./test-pokerauth/pokerauth.py" />
</server>
"""

class PokerAuthTestCase(unittest.TestCase):

    # -----------------------------------------------------------------------------------------------------
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
    # -----------------------------------------------------------------------------------------------------
    def tearDown(self):
        pokerauth._get_auth_instance = None
    # -----------------------------------------------------------------------------------------------------
    def test01_Init(self):
        """test01_Init
        Test Poker auth : get_auth_instance"""
        db = None
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        auth = pokerauth.get_auth_instance(db, settings)

    # -----------------------------------------------------------------------------------------------------
    def test02_AlternatePokerAuth(self):
        """test02_AlternatePokerAuth
        Test Poker auth : get_auth_instance alternate PokerAuth"""
        db = None
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_alternate_xml, len(settings_alternate_xml))
        settings.header = settings.doc.xpathNewContext()
        auth = pokerauth.get_auth_instance(db, settings)
        self.failUnless(hasattr(auth, 'gotcha'))
    # -----------------------------------------------------------------------------------------------------
    def checkIfUserExistsInDB(self, name, selectString = "SELECT serial from users where name = '%s'"):
        cursor = self.db.cursor()
        cursor.execute(selectString % name)
        if cursor.rowcount == 1:
            (serial,) = cursor.fetchone()
            cursor.close()
            return [serial]
        elif cursor.rowcount == 0:
            cursor.close()
            return []
        else:
            serials = []
            for row in cursor.fetchall(): serials.append(row['serial'])
            cursor.close()
            return serials
    # -----------------------------------------------------------------------------------------------------
    def test03_authWithAutoCreate(self):
        """test03_authWithAutoCreate
        Test Poker auth : Try basic auth with autocreate on"""
        db = self.db
        settings = pokernetworkconfig.Config([])
        autocreate_xml = settings_xml.replace('<server auto_create_account="no" ', '<server ')
        settings.doc = libxml2.parseMemory(autocreate_xml, len(autocreate_xml))
        settings.header = settings.doc.xpathNewContext()
        auth = pokerauth.get_auth_instance(db, settings)

        clear_all_messages()
        self.assertEquals(auth.auth('joe_schmoe', 'foo'), ((4, 'joe_schmoe', 1), None))
        self.assertEquals(get_messages(), ['user joe_schmoe does not exist, create it',
                                       'creating user joe_schmoe', 'create user with serial 4'])
        self.failUnless(len(self.checkIfUserExistsInDB('joe_schmoe')) == 1)
    # -----------------------------------------------------------------------------------------------------
    def test04_authWithoutAutoCreate(self, expectedMessage = 'user john_smith does not exist'):
        """test04_authWithoutAutoCreate
        Test Poker auth : Try basic auth with autocreate on"""
        auth = pokerauth.get_auth_instance(self.db, self.settings)

        clear_all_messages()

        self.assertEquals(auth.auth('john_smith', 'blah'), (False, 'Invalid login or password'))
        if expectedMessage:
            self.assertTrue(search_output(expectedMessage))
        self.failUnless(len(self.checkIfUserExistsInDB('john_smith')) == 0)
    # -----------------------------------------------------------------------------------------------------
    def test05_authWhenDoubleEntry(self):
        """test05_authWhenDoubleEntry
        Tests case in fallback authentication where more than one entry exists.
        """
        cursor = self.db.cursor()
        cursor.execute("DROP TABLE users")
        cursor.execute("""CREATE TABLE users (
 	    serial int unsigned not null auto_increment,
	    name varchar(32), password varchar(32), privilege int default 1,
            primary key (serial))""")
        for ii in [ 1 , 2 ]:
            cursor.execute("INSERT INTO users (name, password) values ('%s', '%s')" %
                           ('doyle_brunson', 'foo'))
        cursor.close()

        auth = pokerauth.get_auth_instance(self.db, self.settings)

        clear_all_messages()
        self.assertEquals(auth.auth('doyle_brunson', 'foo'), (False, "Invalid login or password"))
        self.assertEquals(get_messages(), ['*ERROR* more than one row for doyle_brunson'])
    # -----------------------------------------------------------------------------------------------------
    def test06_validAuthWhenEntryExists(self):
        """test06_validAuthWhenEntryExists
        Tests case for single-row returned existing auth, both success and failure.
        """
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO users (created, name, password) values (%d, '%s', '%s')" %
                       (seconds(), 'dan_harrington', 'bar'))
        cursor.close()

        auth = pokerauth.get_auth_instance(self.db, self.settings)

        clear_all_messages()
        self.assertEquals(auth.auth('dan_harrington', 'bar'), ((4L, 'dan_harrington', 1L), None))
        self.assertEquals(get_messages(), [])

        clear_all_messages()
        self.assertEquals(auth.auth('dan_harrington', 'wrongpass'), (False, 'Invalid login or password'))
        self.assertEquals(get_messages(), ['password mismatch for dan_harrington'])
    # -----------------------------------------------------------------------------------------------------
    def test07_mysql11userCreate(self):
        """test07_mysql11userCreate
        Tests userCreate() as it will behave under MySQL 1.1 by mocking up
        the situation.
        """
        class MockCursor:
            def execute(self, str): pass
            def insert_id(self):    return 4815
            def close(self):        pass
        class MockDatabase:
            def cursor(self):    return MockCursor()

        clear_all_messages()
        auth = pokerauth.get_auth_instance(MockDatabase(), self.settings)
        self.assertEquals(auth.userCreate("nobody", "nothing"), 4815)
        self.assertTrue(search_output('creating user nobody'))
        self.assertTrue(search_output('create user with serial 4815'))
    # -----------------------------------------------------------------------------------------------------
    def test08_mysqlbeyond11userCreate(self):
        """test08_mysqlbeyond11userCreate
        Tests userCreate() as it will behave under MySQL > 1.1 by mocking up
        the situation.
        """
        class MockCursor:
            def __init__(self):
                self.lastrowid = 162342
            def execute(self, str): pass
            def insert_id(self):    self.failIf(1)
            def close(self):        pass
        class MockDatabase:
            def cursor(self):    return MockCursor()

        clear_all_messages()
        auth = pokerauth.get_auth_instance(MockDatabase(), self.settings)
        self.assertEquals(auth.userCreate("somebody", "something"), 162342)
        self.assertTrue(search_output('creating user somebody'))
        self.assertTrue(search_output('create user with serial 162342'))
    # -----------------------------------------------------------------------------------------------------
    def test09_setAndGetLevel(self):
        """test09_setAndGetLevel
        Tests the SetLevel and GetLevel methods.
        """
        auth = pokerauth.get_auth_instance(self.db, self.settings)

        self.assertEquals(auth.GetLevel('first'), False)
        self.assertEquals(auth.SetLevel('first', 7), None)
        self.assertEquals(auth.GetLevel('first'), 7)
        self.assertEquals(auth.GetLevel('second'), False)
# -----------------------------------------------------------------------------------------------------
settings_mysql_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
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
  <auth script="%(script_dir)s/../pokernetwork/pokerauthmysql.py" host="localhost" user="root" password="" db="testpokerauthmysql" table="users"/>
</server>
""" % {'script_dir': SCRIPT_DIR}
import MySQLdb

class PokerAuthMysqlTestCase(PokerAuthTestCase):
    # -----------------------------------------------------------------------------------------------------
    def setUp(self):
        self.settings = pokernetworkconfig.Config([])
        self.settings.doc = libxml2.parseMemory(settings_mysql_xml, len(settings_mysql_xml))
        self.settings.header = self.settings.doc.xpathNewContext()

        self.parameters = self.settings.headerGetProperties("/server/auth")[0]
        self.db = MySQLdb.connect(host = self.parameters["host"],
                                  port = int(self.parameters.get("port", '3306')),
                                  user = self.parameters["user"],
                                  passwd = self.parameters["password"])
        self.db.query("CREATE DATABASE %s" % self.parameters["db"])
        self.db.query("USE %s" % self.parameters["db"])
        self.db.query("CREATE TABLE %s (username varchar(20), password varchar(20), privilege int)" % self.parameters["table"])
        self.db.query("INSERT INTO users (username, password, privilege) VALUES ('testuser', 'testpassword', %i)" % User.REGULAR)
    # -----------------------------------------------------------------------------------------------------
    def tearDown(self):
        self.db.query("DROP DATABASE %s" % self.parameters["db"])
        pokerauth._get_auth_instance = None
    # -----------------------------------------------------------------------------------------------------
    def checkIfUserExistsInDB(self, name, selectString = ""):
        return PokerAuthTestCase.checkIfUserExistsInDB(self, name,
                             selectString = "SELECT username from " + self.parameters["table"]
                                                +  " where username = '%s'")
    # -----------------------------------------------------------------------------------------------------
    def test01_Init(self):
        """test01_Init
        Test initalizing pokerauthmysql"""
        db = None
        auth = pokerauth.get_auth_instance(db, self.settings)
        result, message = auth.auth("testuser", "testpassword")
        self.assertNotEquals(False, result)
    # -----------------------------------------------------------------------------------------------------
    def test03_authWithAutoCreate(self):
        """test03_authWithAutoCreateis not needed for MySQLAUTH"""
        pass
    # -----------------------------------------------------------------------------------------------------
    def test04_authWithoutAutoCreate(self):
        """test04_authWithoutAutoCreate
        Test Poker auth : Try basic auth with autocreate on"""
        PokerAuthTestCase.test04_authWithoutAutoCreate(self, expectedMessage = '')
    # -----------------------------------------------------------------------------------------------------
    def test05_authWhenDoubleEntry(self):
        """test05_authWhenDoubleEntry
        Tests case in fallback authentication where more than one entry exists.
        """
        cursor = self.db.cursor()
        for ii in [ 1 , 2 ]:
            cursor.execute("INSERT INTO %s (username, password, privilege) values ('%s', '%s', %i)" %
                           (self.parameters["table"], 'doyle_brunson', 'foo', User.REGULAR))
        cursor.close()

        auth = pokerauth.get_auth_instance(self.db, self.settings)

        clear_all_messages()
        self.assertEquals(auth.auth('doyle_brunson', 'foo'), (False, "Invalid login or password"))
        self.assertEquals(get_messages(), [])
    # -----------------------------------------------------------------------------------------------------
    def test06_validAuthWhenEntryExists(self):
        """test06_validAuthWhenEntryExists
        Tests case for single-row returned existing auth, both success and failure.
        """
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO %s (username, password, privilege) values ('%s', '%s', %i)" %
                           (self.parameters["table"], 'dan_harrington', 'bar', User.REGULAR))
        cursor.close()

        auth = pokerauth.get_auth_instance(self.db, self.settings)

        clear_all_messages()
        self.assertEquals(auth.auth('dan_harrington', 'bar'), (('dan_harrington', 'dan_harrington', 1L), None))
        self.assertEquals(get_messages(), [])

        clear_all_messages()
        self.assertEquals(auth.auth('dan_harrington', 'wrongpass'), (False, 'Invalid login or password'))
        self.assertEquals(get_messages(), [])
    # -----------------------------------------------------------------------------------------------------
    def test07_mysql11userCreate(self):
        """test08_mysqlbeyond11userCreate is not needed for MySQLAUTH"""
        pass
    # -----------------------------------------------------------------------------------------------------
    def test08_mysqlbeyond11userCreate(self):
        """test08_mysqlbeyond11userCreate is not needed for MySQLAUTH"""
        pass
# -----------------------------------------------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PokerAuthTestCase))
    suite.addTest(unittest.makeSuite(PokerAuthMysqlTestCase))
    # Comment out above and use line below this when you wish to run just
    # one test by itself (changing prefix as needed).
#    suite.addTest(unittest.makeSuite(PokerAuthTestCase, prefix = "test09"))
    return suite

# -----------------------------------------------------------------------------------------------------
def Run(verbose):
    suite = GetTestSuite()
    verbosity = int(os.environ.get('VERBOSE_T', 2))
    return unittest.TextTestRunner(verbosity=verbose).run(suite)

# -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    if Run(int(os.environ.get('VERBOSE_T', 2))).wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokerauth.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerauth.py ../pokernetwork/pokerauthmysql.py' TESTS='coverage-reset test-pokerauth.py coverage-report' check )"
# End:
