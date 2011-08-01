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
# Authors:
#  Bradley M. Kuhn <bkuhn@ebb.org>
#
import sys, os, tempfile, shutil

import unittest
from cStringIO import StringIO

sys.path.insert(0, "./..")
sys.path.insert(0, "..")

tmpdir = tempfile.mkdtemp()
open(os.path.join(tmpdir, "__init__.py"), "w").close()

# Dummy up the OpenSSL file so that OpenSSL.SSL won't import.

openSslFile = os.path.join(tmpdir, "OpenSSL.py")
open(openSslFile, "w").close()

# Dummy up the OpenSSL file so that OpenSSL.SSL won't import.

soapFile = os.path.join(tmpdir, "SOAPpy.py")
soapFH = open(soapFile, "w")
soapFH.write("""raise NotImplementedError("overriden to force error")\n""")
soapFH.close()
        
# Note, you very much need the below for this test.  This is because
# inside each test, the cwd is different and the above relative pathnames
# don't work.
sys.path[:] = map(os.path.abspath, sys.path)

##############################################################################
class LogicThatOccursDuringLoadTestCase(unittest.TestCase):
    # ----------------------------------------------------------------
    def test01_openSSLMissing_badTwistedLoad_soapPyMissing(self):
        """test01_openSSLMissing_badTwistedLoad_soapPyMissing"""
        import sys

        oldPath = sys.path
        sys.path.insert(0, tmpdir)

        from twisted.application import service
        from twisted.internet import protocol, reactor, defer
        from twisted.python.runtime import seconds
        from twisted.web import server, resource, util, http
        from zope.interface import Interface as ZopeRealInterface

        import twisted.python.components as comps

        comps.Interface = ZopeRealInterface

        # Now, do something super-nasty.  It's setting up the test for the
        # zope.interface.implements stuff by delete those things from
        # zope.

        fh = open(openSslFile, "w")
        fh.write("from zope import interface as MockChopInterface\nsaveMe = MockChopInterface.implements\ndel MockChopInterface.implements\n")
        fh.close()

        for mod in ['OpenSSL', 'pokernetwork', 'pokerservice']:
            if sys.modules.has_key(mod): del sys.modules[mod]

        oldStout = sys.stdout
        sys.stdout = StringIO()

        from pokernetwork import pokerservice as ps

        value = sys.stdout.getvalue()
        sys.stdout = oldStout

        self.failIf(ps.HAS_OPENSSL, "HAS_OPENSSL should be False when OpenSSL.SSL is not available")
        self.assertEquals(value, 'openSSL not available.\nPython SOAP module not available\n')

        oldStout = sys.stdout
        sys.stdout = StringIO()

        # Cleanup the loading weirness to fail twisted
        import OpenSSL
        OpenSSL.MockChopInterface.implements = OpenSSL.saveMe

        # Next, we'll test ps.implements that was defined 

        saveGetFrame = sys._getframe
        
        class MockFrameFirstRaise():
            def __init__(self):
                self.f_locals = ['testing']
                self.f_globals = ['something else' ]
        def getFirstRaiseFrame(x): return MockFrameFirstRaise()

        sys._getframe = getFirstRaiseFrame
        gotError = False
        try:
            ps.implements(None)
            self.failIf(True, "should not reach this point, TypeError should occur")
        except TypeError, te:
            self.assertEquals(te.__str__(), " can be used only from a class definition.")
            gotError = True
        self.failUnless(gotError, "Should have caught a TypeError")

        class MockFrameSecondRaise():
            def __init__(self):
                self.f_locals = ['__implements__', '__module__']
                self.f_globals = ['something else']

        def getSecondRaiseFrame(x): return MockFrameSecondRaise()
        
        sys._getframe = getSecondRaiseFrame

        gotError = False
        try:
            ps.implements(None)
            self.failIf(True, "should not reach this point, TypeError should occur")
        except TypeError, te:
            self.assertEquals(te.__str__(), " can be used only once in a class definition.")
            gotError = True
        self.failUnless(gotError, "Should have caught a TypeError")
        sys._getframe = saveGetFrame

##############################################################################
class CleanupTempDir(unittest.TestCase):
    def test01_cleanupTempDir(self):
        shutil.rmtree(tmpdir)
##############################################################################
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LogicThatOccursDuringLoadTestCase))
    suite.addTest(unittest.makeSuite(CleanupTempDir))
    # Comment out above and use line below this when you wish to run just
    # one test by itself (changing prefix as needed).
#    suite.addTest(unittest.makeSuite(PokerChipsTestCase, prefix = "test2"))
    return suite
# ----------------------------------------------------------------
def GetTestedModule():
    return pokerservice
# ----------------------------------------------------------------
def Run(verbose):
    return unittest.TextTestRunner(verbosity=verbose).run(GetTestSuite())
# ----------------------------------------------------------------
if __name__ == '__main__':
    if Run(2).wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokerservice.py tests/test-pokerservice-load.py ) ; ( cd ../tests ; make VERBOSE_T=-1 COVERAGE_FILES='../pokernetwork/pokerservice.py' TESTS='coverage-reset test-pokerservice-load.py test-pokerservice.py coverage-report' check )"
# End:

