#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2009       Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C) 2006       Mekensleep <licensing@mekensleep.com>
#                          24 rue vieille du temple, 75004 Paris
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
#


import sys, os
sys.path.insert(0, "..")
sys.path.insert(0, "..")

from tests import testclock

from types import *

from twisted.python import failure
from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor
from twisted.internet import defer

twisted.internet.base.DelayedCall.debug = True

from urlparse import urlparse

from tests.testmessages import silence_all_messages, clear_all_messages, search_output, get_messages, restore_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from pokernetwork import currencyclient

class CurrencyClientTestCase(unittest.TestCase):

    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS currencytest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS currencytest'")

    # -----------------------------------------------------------------------------
    def setUp(self):
        self.destroyDb()
        self.client = currencyclient.CurrencyClient()
        self.client.getPage = self.getPage

    # -----------------------------------------------------------------------------
    def tearDown(self):
        del self.client
        self.destroyDb()

    def getPage(self, url):
        ( scheme, netloc, path, parameters, query, fragement ) = urlparse(url)
        cmd = """
cat <<'EOF' | QUERY_STRING='""" + query + """' /usr/bin/php --define extension=mysql.so
<?
  ini_set('include_path', './../../pokerweb/pages:' . ini_get('include_path'));
  $GLOBALS['currency_db_base'] = 'currencytest';
  $GLOBALS['currency_db_host'] = 'localhost';
  $GLOBALS['currency_db_user'] = 'root';
  $GLOBALS['currency_db_password'] = '';
  require 'currency.php';
  parse_str(getenv('QUERY_STRING'), $_GET);
  currency_main(False);
?>
EOF
"""
        #print cmd
        fd = os.popen(cmd)
        result = fd.read()
        fd.close()
        d = defer.Deferred()
        reactor.callLater(0, lambda: d.callback(result))
        return d

    # -----------------------------------------------------------------------------
    def getNote(self, url, value):
        d = self.client.getNote(url, value)
        if "?" in url:
            check_url = url[:url.index("?")]
        else:
            check_url = url
        def validate(result):
            if isinstance(result, failure.Failure): raise result
            note = result[0]
            self.assertEqual(check_url, note[0])
            self.assertEqual(40, len(note[2]))
            self.assertEqual(value, note[3])
            return result
        d.addBoth(validate)
        return d

    # -----------------------------------------------------------------------------
    def getCommitedNote(self, url, value):
        return self.commit(self.getNote(url, value))
    # -----------------------------------------------------------------------------
    def commit(self, d):
        def commit(result):
            if isinstance(result, failure.Failure): raise result
            first_note = result[0]
            d = self.client.commit(first_note[0], first_note[2])
            d.addCallback(lambda ignore: result)
            return d
        d.addBoth(commit)
        return d

    # -----------------------------------------------------------------------------
    def test01_getNote(self):
        d = self.getNote('http://fake/', 100)
        def validate(result):
            note = result[0]
            self.assertEqual(1, note[1])
            return result
        d.addCallback(validate)
        return d

    # -----------------------------------------------------------------------------
    def test02_commit(self):
        return self.getCommitedNote('http://fake/', 100)

    # -----------------------------------------------------------------------------
    def test03_checkNote(self):
        d = self.getCommitedNote('http://fake/', 100)

        def checkNote(result):
            #print "checkNote " + str(result)
            note_to_check = result[0]
            d = self.client.checkNote(note_to_check)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                checked_note = result[0]
                self.assertEqual(note_to_check, checked_note)
                return result
            d.addBoth(validate)
            return d

        d.addCallback(checkNote)
        return d

    # -----------------------------------------------------------------------------
    def test04_changeNote(self):
        d = self.getCommitedNote('http://fake/', 100)

        def changeNote(result):
            note_to_change = result[0]
            d = self.client.changeNote(note_to_change)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                changed_note = result[0]
                self.assertEqual("http://fake/", changed_note[0])
                self.assertEqual(note_to_change[1] + 1, changed_note[1])
                self.assertEqual(40, len(changed_note[2]))
                self.assertNotEqual(note_to_change[2], changed_note[2])
                self.assertEqual(note_to_change[3], changed_note[3])
                return result
            d.addBoth(validate)
            return d

        d.addCallback(changeNote)
        return d

    # -----------------------------------------------------------------------------
    def test05_mergeNotes(self):
        notes = []
        def addnote(result):
            notes.append(result[0])
            return result

        d1 = self.getCommitedNote('http://fake/', 100)
        d1.addCallback(addnote)

        d2 = self.getCommitedNote('http://fake/', 100)
        d2.addCallback(addnote)

        d = defer.DeferredList((d1, d2))

        def mergeNotes(note):
            self.assertEquals(2, len(notes))
            d = self.client.mergeNotes(*notes)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                self.assertEqual(1, len(result))
                note = result[0]
                self.assertEqual("http://fake/", note[0])
                self.assertEqual(1, note[1])
                self.assertEqual(40, len(note[2]))
                self.assertEqual(200, note[3])
                return result
            d.addBoth(validate)
            return d

        d.addCallback(mergeNotes)
        return self.commit(d)

    # -----------------------------------------------------------------------------
    def test06_meltNotes(self):
        notes = []
        def addnote(result):
            notes.append(result[0])
            return result

        d1 = self.getCommitedNote('http://fake/', 100)
        d1.addCallback(addnote)

        d2 = self.getCommitedNote('http://fake/', 500)
        d2.addCallback(addnote)

        d = defer.DeferredList((d1, d2))

        def meltNotes(note):
            self.assertEquals(2, len(notes))
            d = self.client.meltNotes(*notes)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                self.assertEqual(1, len(result))
                note = result[0]
                self.assertEqual("http://fake/", note[0])
                self.assertEqual(1, note[1])
                self.assertEqual(40, len(note[2]))
                self.assertEqual(600, note[3])
                return result
            d.addBoth(validate)
            return d

        d.addCallback(meltNotes)
        return self.commit(d)

    # -----------------------------------------------------------------------------
    def test07_breakNote(self):
        d = self.getCommitedNote('http://fake/', 100)

        def breakNote(result):
            #print "breakNote " + str(result)
            note_to_break = result[0]
            d = self.client.breakNote(note_to_break, 30, 10, 5)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                #print "broken notes " + str(result)
                notes = result
                self.assertEqual(4, len(notes))
                self.assertEqual(30, notes[0][3])
                self.assertEqual(30, notes[1][3])
                self.assertEqual(30, notes[2][3])
                self.assertEqual(10, notes[3][3])
                return result
            d.addBoth(validate)
            return d

        d.addCallback(breakNote)
        return d

    # -----------------------------------------------------------------------------
    def test07_1_breakNote_oddLeftOver(self):
        d = self.getCommitedNote('http://fake/', 100)

        def breakNote(result):
            #print "breakNote " + str(result)
            note_to_break = result[0]
            d = self.client.breakNote(note_to_break, 15, 3, 2)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                #print "broken notes " + str(result)
                notes = result
                self.assertEqual(10, len(notes))
                for ii in [ 0, 1, 2, 3, 4, 5 ]:
                    self.assertEqual(ii+1, notes[ii][1])
                    self.assertEqual(15, notes[ii][3])
                    self.assertEqual(40, len(notes[ii][2]))
                for ii in [ 6, 7, 8 ]:
                    self.assertEqual(ii+1, notes[ii][1])
                    self.assertEqual(3, notes[ii][3])
                    self.assertEqual(40, len(notes[ii][2]))

                lastNote = 1
                lastVal = 1
                if isinstance(self.client, currencyclient.FakeCurrencyClient):
                    lastNote = 10
                    lastVal = 2
                self.assertEqual(lastNote, notes[9][1])
                self.assertEqual(lastVal, notes[9][3])
                self.assertEqual(40, len(notes[9][2]))
                return result
            d.addBoth(validate)
            return d

        d.addCallback(breakNote)
        return d
    # -----------------------------------------------------------------------------
    def test08_breakNote_zero(self):
        d = self.getCommitedNote('http://fake/', 100)

        def breakNote(result):
            #print "breakNote " + str(result)
            note_to_break = result[0]
            d = self.client.breakNote(note_to_break, 100, 0)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                #print "broken notes " + str(result)
                notes = result
                self.assertEqual(2, len(notes))
                self.assertEqual(100, notes[0][3])
                self.assertEqual(0, notes[1][3])
                return result
            d.addBoth(validate)
            return d

        d.addCallback(breakNote)
        return d

    # -----------------------------------------------------------------------------
    def test09_getNote_with_id(self):
        d = self.getNote('http://fake/?id=1', 100)
        def validate(result):
            note = result[0]
            self.assertEqual(1, note[1])
            return result
        d.addCallback(validate)
        return d

# -----------------------------------------------------------------------------
class FakeCurrencyClientTestCase(CurrencyClientTestCase):
    def setUp(self):
        currencyclient.Verbose = True
        currencyclient.CurrencyClient = currencyclient.FakeCurrencyClient
        self.destroyDb()
        self.client = currencyclient.FakeCurrencyClient()
        # Fake out the value on the starting serial so I can reuse the
        # tests completely from the previous test class.
        self.client.serial = 0
        self.client.getPage = self.getPage
        currencyclient.FakeCurrencyFailure = False
    # -----------------------------------------------------------------------------
    def getNote(self, url, value):
        clear_all_messages()
        d = self.client.getNote(url, value)
        self.assertEquals(search_output("_buildNote"), True)
        self.assertEquals(search_output("getNote"), True)
        if "?" in url:
            check_url = url[:url.index("?")]
        else:
            check_url = url
        def validate(result):
            if isinstance(result, failure.Failure): raise result
            # I wonder, actually, if FakeCurrencyClient is supposed to
            # return a list of a list as RealCurrencyClient does in this
            # instance.  I commented out:
            # note = result[0]
            # in favor of:
            note = result
            self.assertEqual(check_url, note[0])
            self.assertEqual(40, len(note[2]))
            self.assertEqual(value, note[3])
            return [result]
        d.addBoth(validate)
        return d
    # -----------------------------------------------------------------------------
    def getCommitedNote(self, url, value):
        clear_all_messages()
        def checkCommitVerboseOutput(result):
            self.assertEquals(search_output("commit"), True)
            return result
        ret = CurrencyClientTestCase.getCommitedNote(self, url, value)
        ret.addCallback(checkCommitVerboseOutput)
        return ret
    # -----------------------------------------------------------------------------
    # Had to ovveride all of test03, for the same reason discussed above, that
    #  there is another layer of list indirection missing in FakeCurrencyClient.
    def test03_checkNote(self):
        d = self.getCommitedNote('http://fake/', 100)

        def checkNote(result):
            clear_all_messages()
            note_to_check = result
            d = self.client.checkNote(note_to_check)
            self.assertEquals(search_output("checkNote"), True)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                checked_note = result
                self.assertEqual(note_to_check, checked_note)
                return result
            d.addBoth(validate)
            return d

        d.addCallback(checkNote)
        return d
    # -----------------------------------------------------------------------------
    def test05_mergeNotes(self):
        notes = []
        def addnote(result):
            notes.append(result[0])
            return result

        d1 = self.getCommitedNote('http://fake/', 100)
        d1.addCallback(addnote)

        d2 = self.getCommitedNote('http://fake/', 100)
        d2.addCallback(addnote)

        d = defer.DeferredList((d1, d2))

        def mergeNotes(note):
            self.assertEquals(2, len(notes))
            clear_all_messages()
            d = self.client.mergeNotes(*notes)
            self.assertEquals(search_output("mergeNotes"), True)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                self.assertEqual(1, len(result))
                note = result[0]
                self.assertEqual("http://fake/", note[0])
                self.assertEqual(3, note[1])
                self.assertEqual(40, len(note[2]))
                self.assertEqual(200, note[3])
                return result
            d.addBoth(validate)
            return d

        d.addCallback(mergeNotes)
        return self.commit(d)
    # -----------------------------------------------------------------------------
    def test06_meltNotes(self):
        notes = []
        def addnote(result):
            notes.append(result[0])
            return result

        d1 = self.getCommitedNote('http://fake/', 100)
        d1.addCallback(addnote)

        d2 = self.getCommitedNote('http://fake/', 500)
        d2.addCallback(addnote)

        d = defer.DeferredList((d1, d2))

        def meltNotes(note):
            self.assertEquals(2, len(notes))
            d = self.client.meltNotes(*notes)
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                self.assertEqual(1, len(result))
                note = result[0]
                self.assertEqual("http://fake/", note[0])
                self.assertEqual(3, note[1])
                self.assertEqual(40, len(note[2]))
                self.assertEqual(600, note[3])
                return result
            d.addBoth(validate)
            return d

        d.addCallback(meltNotes)
        return self.commit(d)

    def test04_changeNote(self):
        d = self.getCommitedNote('http://fake/', 100)
        clear_all_messages()
        def changeNote(result):
            class FakeNoteToChange:
                def copy(self):
                    return [8, 0, '']
            d = self.client.changeNote(FakeNoteToChange())
            def validate(result):
                if isinstance(result, failure.Failure): raise result
                self.assertEqual(result[0], 8)
                self.assertEqual(result[1], 2)
                self.assertEqual(40, len(result[2]))
                self.assertEquals(search_output("changeNote"), True)
                return result
            d.addBoth(validate)
            return d

        d.addCallback(changeNote)
        return d

    def test07_breakNote(self):
        clear_all_messages()
        d = CurrencyClientTestCase.test07_breakNote(self)
        def checkOutput(result):
            self.assertEquals(search_output("breakNote vaues"), True)
            return True

        d.addCallback(checkOutput)
        return d

    # -----------------------------------------------------------------------------
    def test09_getNote_with_id(self):
        return True
    # -----------------------------------------------------------------------------
    def test10_breakNote_FakeCurrencyFailure(self):
        currencyclient.FakeCurrencyFailure = True

        d = self.getCommitedNote('http://fake/', 100)

        mustBeCalledBackForSuccess = defer.Deferred()

        def breakNote(result):
            def failIfCalledBack(result):
                self.fail("should not have a normal callback in this situation")

            def expectedError(err):
                self.assertEquals(err.check(twisted.web.error.Error),
                                  twisted.web.error.Error)
                self.assertEquals(err.getErrorMessage(),
                              "500 breakNote: fake error")
                mustBeCalledBackForSuccess.callback(True)

            d = self.client.breakNote(result[0], 30, 10, 5)
            d.addCallback(failIfCalledBack)
            d.addErrback(expectedError)
            return d

        d.addCallback(breakNote)
        return defer.DeferredList((d, mustBeCalledBackForSuccess))
# -----------------------------------------------------------------------------
class ErrorCondtionsCurrencyClientTestCase(unittest.TestCase):
    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS currencytest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS currencytest'")
    # -----------------------------------------------------------------------------
    def setUp(self):
        self.destroyDb()
    # -----------------------------------------------------------------------------
    def tearDown(self):
        del self.client
        self.destroyDb()
    # -----------------------------------------------------------------------------
    def test01_parseResultNote_InvalidResult(self):
        from cStringIO import StringIO

        self.client = currencyclient.RealCurrencyClient()
        caughtIt = False

        oldStdio = sys.stdout
        sys.stdout = StringIO()
        try:
            self.client.parseResultNote("two\tfield")
            self.fail("Previous line should have caused exception")
        except Exception, e:
            self.assertEquals(e.__str__(), "expected notes got something else")
            caughtIt = True
        value = sys.stdout.getvalue()
        sys.stdout = oldStdio

        self.assertEquals(value, "RealCurrencyClient::parseResultNote ignore line: two\tfield\n")
        self.failUnless(caughtIt, "Should have caught an exception")
    # -----------------------------------------------------------------------------
    def test02_commit_multiLineResult(self):
        self.client = currencyclient.RealCurrencyClient()

        oldRequest = self.client.request
        requestDeferred = defer.Deferred()
        def myRequest(url = None, command = None, transaction_id = None):
            self.assertEquals(command, 'commit')
            self.assertEquals(url, "url_dummy")
            self.assertEquals(transaction_id, "transaction_dummy")
            return requestDeferred
        self.client.request = myRequest

        self.assertEquals(self.client.commit("url_dummy", "transaction_dummy"),
                          requestDeferred)


        confirmErrorFoundDeferred = defer.Deferred()
        def catchException(err):
            self.assertEquals(err.check(Exception), Exception)
            self.assertEquals(err.getErrorMessage(),
                              "expected a single line got two\nlines instead")
            confirmErrorFoundDeferred.callback(True)
        requestDeferred.addErrback(catchException)

        requestDeferred.callback("two\nlines")

        self.client.request = oldRequest
        return confirmErrorFoundDeferred
    # -----------------------------------------------------------------------------
    def test03_checkNote_checkNoteResultIsFalse(self):
        """test03_checkNote_checkNoteResultIsFalse

        The goal of this test is to cover the setting of result to
        failure.Failure() in checkNote().  We have to get a bit tricky
        with deferreds to cause this to happen.  Our chainBegin deferred
        is set up to raise an exception immediately in its callback, which
        will chain off to its own errBack.  Its errBack then calls
        checkNote.  Since there is already an error propogating through,
        the failure.Failure() will work properly to then, in turn, trigger
        the errBack of checkNotesDeferred.  Finally, we make sure the
        point is reached by having the usual rougue deferred that only
        gets called back by the verification process."""

        class PropogatedException(Exception): pass

        self.client = currencyclient.FakeCurrencyClient()
        self.client.check_note_result = False

        forceTimeoutErrorIfNotCalledBack = defer.Deferred()
        def verifyError(err):
            self.assertEquals(err.check(PropogatedException), PropogatedException)
            self.assertEquals(err.getErrorMessage(),
                              "this exception ends up in checknotes errback")
            forceTimeoutErrorIfNotCalledBack.callback(True)
            if hasattr(self, 'client'):
                self.client.check_note_result = True

        def executeCheckNote(value):
            self.assertEquals(value.check(PropogatedException), PropogatedException)
            self.assertEquals(value.getErrorMessage(),
                              "this exception ends up in checknotes errback")

            checkNotesDeferred = self.client.checkNote(None)
            checkNotesDeferred.addErrback(verifyError)
            return checkNotesDeferred

        def propogateError(value):
            raise PropogatedException("this exception ends up in checknotes errback")

        chainBegin = defer.Deferred()
        chainBegin.addCallback(propogateError)
        chainBegin.addErrback(executeCheckNote)
        chainBegin.callback(True)

        return forceTimeoutErrorIfNotCalledBack
    # -----------------------------------------------------------------------------
    def test04_commit_commitResultIsFalse(self):
        """test04_commit_commitResultIsFalse
        This test is nearly identical to
        test03_checkNote_checkNoteResultIsFalse, since the methods work
        very similarily."""

        class PropogatedException(Exception): pass

        self.client = currencyclient.FakeCurrencyClient()
        self.client.commit_result = False

        forceTimeoutErrorIfNotCalledBack = defer.Deferred()
        def verifyError(err):
            self.assertEquals(err.check(PropogatedException), PropogatedException)
            self.assertEquals(err.getErrorMessage(),
                              "this exception ends up in commit errback")
            forceTimeoutErrorIfNotCalledBack.callback(True)
            if hasattr(self, 'client'):
                self.client.commit_result = True

        def executeCommit(value):
            self.assertEquals(value.check(PropogatedException), PropogatedException)
            self.assertEquals(value.getErrorMessage(),
                              "this exception ends up in commit errback")

            commitDeferred = self.client.commit(None, None)
            commitDeferred.addErrback(verifyError)
            return commitDeferred

        def propogateError(value):
            raise PropogatedException("this exception ends up in commit errback")

        chainBegin = defer.Deferred()
        chainBegin.addCallback(propogateError)
        chainBegin.addErrback(executeCommit)
        chainBegin.callback(True)
        return forceTimeoutErrorIfNotCalledBack
# -----------------------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test07"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(CurrencyClientTestCase))
    suite.addTest(loader.loadClass(FakeCurrencyClientTestCase))
    suite.addTest(loader.loadClass(ErrorCondtionsCurrencyClientTestCase))
    return runner.TrialRunner(reporter.TextReporter,
#                              tracebackFormat='verbose',
                              tracebackFormat='default',
                              ).run(suite)

# -----------------------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-currencyclient.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/currencyclient.py' TESTS='coverage-reset test-currencyclient.py coverage-report' check )"
# End:
