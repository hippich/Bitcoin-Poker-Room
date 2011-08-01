#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2008, 2009 Bradley M. Kuhn <bkuhn@ebb.org>
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

from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor

twisted.internet.base.DelayedCall.debug = True
import libxml2
import re

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from pokernetwork import pokerdatabase
from pokernetwork import pokernetworkconfig
from pokernetwork import version

actualSchemaFile = "%s/../database/schema.sql" % SCRIPT_DIR

settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="4">
  <database name="pokernetworktest" host="localhost" user="pokernettestuser" password="mytestuser"
            root_user="root" root_password="" schema="%s" command="/usr/bin/mysql" />
</server>
""" % actualSchemaFile
settings_missing_schema_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="4">
  <database name="pokernetworktest" host="localhost" user="pokernetworktestuser" password="mytestuser"
            root_user="root" root_password="" schema="/this/is/not/a/file/and/should/not/be/there/not-my-schema-go-away.sql" command="/usr/bin/mysql" />
</server>
"""
settings_root_both_users_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="4">
  <database name="pokernetworktest" host="localhost" user="root" password=""
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
</server>
""" % {'script_dir': SCRIPT_DIR}
settings_missing_root_users_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="4">
  <database name="pokernetworktest" host="localhost" user="root" password=""
  schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
</server>
""" % {'script_dir': SCRIPT_DIR}
class PokerDatabaseTestCase(unittest.TestCase):
    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password=''  -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
    # ----------------------------------------------------------------------------
    def setUp(self):
        self.tearDown()
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        r = re.compile("""INSERT\s+INTO\s+server\s+\(\s*version\s*\)\s+VALUES\s*\("([\d\.]+)"\s*\)""", flags=re.I)
        infile = open(actualSchemaFile, "r")
        self.pokerdbVersion = "0.0.0"
        for line in infile:
            m = re.match(r, line)
            if m:
                self.pokerdbVersion = m.group(1)
                break
        infile.close()
        # We should be able to find the version number
        self.assertNotEquals(self.pokerdbVersion, "0.0.0")
    # ----------------------------------------------------------------------------
    def tearDown(self):
        try:
            self.db.close()
        except:
            pass
        try:
            import MySQLdb
            settings = pokernetworkconfig.Config([])
            settings.doc = libxml2.parseMemory(settings_xml,
                                           len(settings_xml))
            settings.header = settings.doc.xpathNewContext()
            parameters = settings.headerGetProperties("/server/database")[0]
            db = MySQLdb.connect(host = parameters["host"],
                                 port = int(parameters.get("port", '3306')),
                                 user = parameters["root_user"],
                                 passwd = parameters["root_password"],
                                 db = 'mysql')
            try:
                db.query("REVOKE ALL PRIVILEGES, GRANT OPTION FROM '%s'" % parameters['user'])
                db.query("drop user '%s'" % parameters['user'])
            except:
                db.query("delete from user where user = '%s'" % parameters['user'])

            db.query("FLUSH PRIVILEGES")
            db.close()
        except Exception, e:
            print e
            assert("Unable to delete the user, " + parameters["user"] + "; some tests will fail incorrectly.")
        try:
            del self.db
        except:
            pass
        try:
            self.destroyDb()
        except:
            pass
    # ----------------------------------------------------------------------------
    def test01_upgrade(self):
        self.db = pokerdatabase.PokerDatabase(self.settings)
        self.db.setVersionInDatabase("0.0.0")
        self.db.version = version.Version("0.0.0")
        good = '%s/test-pokerdatabase/good' % SCRIPT_DIR
        self.db.upgrade(good, False)
        self.assertEquals(self.db.getVersion(), self.pokerdbVersion)
    # ----------------------------------------------------------------------------
    def test02_dbVersionTooOld(self):
        import MySQLdb
        class DummyMySQL:
            def get_server_info(self):
                return "3.2.5"
            def query(self, string):
                return string
            def close(self):
                pass
        def dummyConnect(host, port, user, passwd, db='mysql', reconnect=1):
            parameters = self.settings.headerGetProperties("/server/database")[0]
            if user == parameters['user']:
                raise SqlError
            else:
                return DummyMySQL()
        realconnect = MySQLdb.connect
        MySQLdb.connect = dummyConnect
        try:
            self.db = pokerdatabase.PokerDatabase(self.settings)
        except UserWarning, uw:
            self.assertEqual(uw.args[0], "PokerDatabase: MySQL server version is 3.2.5 but version >= 5.0 is required")
        MySQLdb.connect = realconnect
    # ----------------------------------------------------------------------------
    def test03_schemaFileMissing(self):
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_missing_schema_xml,
                                           len(settings_missing_schema_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        try:
            self.db = pokerdatabase.PokerDatabase(self.settings)
            assert("Schema file was missing so this line should not be reached.")
        except UserWarning, uw:
            self.assertEqual(uw.args[0], "PokerDatabase: schema /this/is/not/a/file/and/should/not/be/there/not-my-schema-go-away.sql file not found")
    # ----------------------------------------------------------------------------
    def test04_rootBothUsers(self):
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_root_both_users_xml,
                                           len(settings_root_both_users_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        try:
            self.db = pokerdatabase.PokerDatabase(self.settings)
        except OperationalError, oe:
            self.assertEquals(oe.args[0], 1396)
            self.assertEquals(oe.args[1], "Operation CREATE USER failed for 'root'@'%'")
        self.assertEquals(self.db.getVersion(), self.pokerdbVersion)
    # ----------------------------------------------------------------------------
    def test05_missingRootUser(self):
        import MySQLdb

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_missing_root_users_xml,
                                           len(settings_missing_root_users_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        try:
            self.db = pokerdatabase.PokerDatabase(self.settings)
            assert("Root user information was missing so this line should not be reached.")
        except MySQLdb.OperationalError, oe: # handle trouble
            self.assertEquals(oe.args[1], "Unknown database 'pokernetworktest'")
            self.assertEquals(oe.args[0], 1049)
    # ----------------------------------------------------------------------------
    def test06_databaseAlreadyExists(self):
        """Test for when the database already exists"""
        import MySQLdb
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_root_both_users_xml,
                                           len(settings_root_both_users_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        parameters = settings.headerGetProperties("/server/database")[0]
        db = MySQLdb.connect(host = parameters["host"],
                             port = int(parameters.get("port", '3306')),
                             user = parameters["root_user"],
                             passwd = parameters["root_password"])
        db.query("CREATE DATABASE " + parameters["name"])
        db.close()
        self.db = pokerdatabase.PokerDatabase(self.settings)
        self.assertEquals(self.db.getVersion(), '1.0.5')
    # ----------------------------------------------------------------------------
    def test07_multipleRowsInVersionTable(self):
        """Test for when the database already exists"""
        import MySQLdb
        from pokernetwork.pokerdatabase import ExceptionUpgradeFailed

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml,
                                           len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        parameters = settings.headerGetProperties("/server/database")[0]

        self.db = pokerdatabase.PokerDatabase(self.settings)

        self.db.db.query("DROP TABLE IF EXISTS server;")
        self.db.db.query("""CREATE TABLE server (version VARCHAR(16) NOT NULL)
                            ENGINE=InnoDB CHARSET=utf8;""")
        self.db.db.query("""INSERT INTO server (version) VALUES ("1.1.0");""")
        self.db.db.query("""INSERT INTO server (version) VALUES ("1.2.0");""")
        try:
            self.db.setVersionInDatabase("1.3.0")
        except ExceptionUpgradeFailed, euf: # handle trouble
            self.assertEquals(euf.args[0], "update server set version = '1.3.0': changed 2 rows, expected one or zero")
    # ----------------------------------------------------------------------------
    def test08_forceTestDatabaseTooOld(self):
        import pokernetwork.version
        ver = pokernetwork.version.Version("32767.32767.32767")
        realDBVersion = pokerdatabase.version
        pokerdatabase.version = ver

        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        parameters = settings.headerGetProperties("/server/database")[0]

        try:
            self.db = pokerdatabase.PokerDatabase(self.settings)
            self.db.checkVersion()
            assert("Should have gotten ExceptionDatabaseTooOld and this line should not have been reached.")
        except pokerdatabase.ExceptionDatabaseTooOld, edto:
            self.assertEquals(edto.args, ())
            pokerdatabase.version = realDBVersion  # Restore original version
    # ----------------------------------------------------------------------------
    def test09_forceTestPokerNetworkTooOld(self):
        settings = pokernetworkconfig.Config([])
        settings.doc = libxml2.parseMemory(settings_xml, len(settings_xml))
        settings.header = settings.doc.xpathNewContext()
        self.settings = settings
        parameters = settings.headerGetProperties("/server/database")[0]
        try:
            self.db = pokerdatabase.PokerDatabase(self.settings)
            import pokernetwork.version
            ver = pokernetwork.version.Version("32767.32767.32767")
            realDBVersion = self.db.version
            self.db.version = ver

            self.db.checkVersion()
            assert("Should have gotten ExceptionSoftwareTooOld and this line should not have been reached.")
        except pokerdatabase.ExceptionSoftwareTooOld, edto:
            self.assertEquals(edto.args, ())
            self.db.version = realDBVersion  # Restore original version
    # ----------------------------------------------------------------------------
    def test10_badUpgradeSqlFiles(self):
        self.db = pokerdatabase.PokerDatabase(self.settings)
        self.db.setVersionInDatabase("0.0.5")
        self.db.version = version.Version("0.0.5")
        try:
            bad = '%s/test-pokerdatabase/bad' % SCRIPT_DIR
            self.db.upgrade(bad, False)
            assert("Should have gotten ExceptionUpgradeFailed and this line should not have been reached.")
        except pokerdatabase.ExceptionUpgradeFailed, euf:
            self.assertEquals(euf.args[0], "upgrade failed")
        self.assertEquals(self.db.getVersion(), "0.0.5")
    # ----------------------------------------------------------------------------
    def test11_confirmLiteralMethodPassThrough(self):
        """test11_confirmLiteralMethodPassThrough
        The method "literal" in the database class should simply pass
        through to the internal representation method of the same name."""
        class MockDatabaseWithOnlyLiteral():
            def literal(mdSelf, args): return "LITERAL TEST " + args

        self.db = pokerdatabase.PokerDatabase(self.settings)
        saveRealDb = self.db.db
        self.db.db = MockDatabaseWithOnlyLiteral()

        self.assertEquals(self.db.literal("ahoy hoy!"),  "LITERAL TEST ahoy hoy!")
        self.db.db = saveRealDb

# --------------------------------------------------------------------------------
def GetTestSuite():
    suite = runner.TestSuite(PokerDatabaseTestCase)
    suite.addTest(unittest.makeSuite(PokerDatabaseTestCase))
    return suite
# --------------------------------------------------------------------------------
def GetTestedModule():
    return pokerdatabase

# --------------------------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test08"
    os.environ['VERBOSE_T'] = '4'

    suite = loader.loadClass(PokerDatabaseTestCase)
    return runner.TrialRunner(reporter.VerboseTextReporter,
#                              tracebackFormat='verbose',
                              tracebackFormat='default',
                              ).run(suite)
# --------------------------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokerdatabase.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerdatabase.py' TESTS='coverage-reset test-pokerdatabase.py coverage-report' check )"
# End:
