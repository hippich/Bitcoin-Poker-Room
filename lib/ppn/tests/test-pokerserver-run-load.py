#!/usr/bin/python
# -*- mode: python; coding: iso-8859-1 -*-
# more information about the above line at http://www.python.org/dev/peps/pep-0263/
#
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

import sys, os, tempfile, shutil
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

import unittest
from twisted.internet import reactor, defer

from cStringIO import StringIO

settings_xml_server_open_options = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" ping="300000" autodeal="yes" simultaneous="4" chat="yes" >
  <delays autodeal="20" round="0" position="0" showdown="0" autodeal_max="1" finish="0" messages="60" />

  <table name="Table1" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />
  <table name="Table2" variant="holdem" betting_structure="100-200-no-limit" seats="10" player_timeout="60" currency_serial="1" />

  <listen tcp="19481" %(listen_options)s />
  <resthost host="127.0.0.1" port="19481" path="/POKER_REST" />

  <cashier acquire_timeout="5" pokerlock_queue_timeout="30" user_create="yes" />
  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
  <path>%(script_dir)s/../conf %(additional_path)s</path>
  <users temporary="BOT"/>
</server>
"""
# ------------------------------------------------------------
class PokerServerRunTestCase(unittest.TestCase):
    def destroyDb(self, arg = None):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -e 'DROP DATABASE IF EXISTS pokernetworktest'")
    # -------------------------------------------------------------------------
    def setUp(self):
        self.destroyDb()
        self.tmpdir = tempfile.mkdtemp()
        self.saveSysout = None
        self.saveArgv = None
    # -------------------------------------------------------------------------
    def tearDown(self):
        shutil.rmtree(self.tmpdir)
        if self.saveSysout:
            value = sys.stdout.getvalue()
            if self.expectedOutput:
                self.failUnless(value.find(self.expectedOutput) >= 0,
                                "Unable to find " + self.expectedOutput + " in " + value)
            sys.stdout = self.saveSysout
        if self.saveArgv:
            sys.argv = self.saveArgv
    # -------------------------------------------------------------------------
    def holdStdout(self):
        self.saveSysout = sys.stdout
        sys.stdout = StringIO()
    # -------------------------------------------------------------------------
    def setArgv(self, newArgv):
        self.saveArgv = sys.argv
        sys.argv = newArgv
    # -------------------------------------------------------------------------
    def test01_validConfig_mockupStartApplication(self):
        """test01_validConfig_mockupStartApplication
        Test that the pokerserver application runs properly.  Since the
        reactor.run() is called by pokerserver's run(), this test might
        HANG INDEFINITELY for some types of test failures.  Unlikely but
        possible."""
        from pokernetwork.pokerserver import run as pokerServerRun

        from twisted.application import app
        configFile = os.path.join(self.tmpdir, "ourconfig.xml")
        configFH = open(configFile, "w")
        configFH.write(settings_xml_server_open_options %\
                       { 'listen_options' : '',
                        'additional_path' : self.tmpdir,
                        'script_dir': SCRIPT_DIR})
        self.setArgv([configFile])
        configFH.close()

        def mockStartApplication(application, val):
            from twisted.python.components import Componentized
            self.failUnless(isinstance(application, Componentized))
            self.assertEquals(val, None)
        savedStartApplication = app.startApplication
        app.startApplication = mockStartApplication

        def doCallback(val):
            self.assertEquals(val, "done")
            app.startApplication = savedStartApplication
            reactor.stop()

        defferedStillRunningMeansReactorNotStarted = defer.Deferred()
        defferedStillRunningMeansReactorNotStarted.addCallback(doCallback)

        reactor.callLater(1, lambda: defferedStillRunningMeansReactorNotStarted.callback("done"))
        pokerServerRun()
# ------------------------------------------------------------
class PokerServerLoadingSSLTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def test01_openSSLMissing(self):
        """test01_openSSLMissing"""
        import sys

        for mod in ['OpenSSL', 'pokernetwork', 'pokerserver']:
            if sys.modules.has_key(mod): del sys.modules[mod]

        realImporter = __builtins__.__import__

        def failSSLImport(moduleName, *args, **kwargs):
            if moduleName == "OpenSSL":
                raise Exception("SSL was imported")
            else:
                return realImporter(moduleName, *args, **kwargs)

        __builtins__.__import__  = failSSLImport

        oldStout = sys.stdout
        sys.stdout = StringIO()

        from pokernetwork import pokerserver as ps

        value = sys.stdout.getvalue()
        sys.stdout = oldStout

        self.failIf(ps.HAS_OPENSSL, "HAS_OPENSSL should be False when OpenSSL.SSL is not available")
        self.failUnless('openSSL not available.' in value)

        __builtins__.__import__  = realImporter
# ------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    # Make sure you do the LoadingSSLTestCase FIRST.
    suite.addTest(unittest.makeSuite(PokerServerLoadingSSLTestCase))
    suite.addTest(unittest.makeSuite(PokerServerRunTestCase))

    # Comment out above and use line below this when you wish to run just
    # one test by itself (changing prefix as needed).
#    suite.addTest(unittest.makeSuite(PokerGameHistoryTestCase, prefix = "test2"))
    return suite
# -----------------------------------------------------------------------------
def Run(verbose = 2):
    return unittest.TextTestRunner(verbosity=verbose).run(GetTestSuite())
# -----------------------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokerserver-run-load.py tests/test-pokerserver.py ) ; ( cd ../tests ; make VERBOSE_T=-1 COVERAGE_FILES='../pokernetwork/pokerserver.py' TESTS='coverage-reset test-pokerserver-run-load.py test-pokerserver.py coverage-report' check )"
# End:
