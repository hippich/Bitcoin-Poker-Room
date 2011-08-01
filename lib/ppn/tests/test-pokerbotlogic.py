#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
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
import os
import sys
sys.path.insert(0, "./..")
sys.path.insert(0, "..")

from twisted.trial import unittest, runner, reporter

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from pokernetwork.pokerbotlogic import StringGenerator, NoteGenerator, PokerBot

class StringGeneratorTestCase(unittest.TestCase):

    def test_all(self):
        generator = StringGenerator("PREFIX")
        generator.command = "echo USERONE ; echo USERTWO"
        self.assertEqual("PREFIXUSERTWO", generator.getName())
        self.assertEqual(1, len(generator.pool))
        self.assertEqual("USERONE", generator.getPassword())
        self.assertEqual(0, len(generator.pool))
        generator.command = ""
        self.failUnlessRaises(UserWarning, generator.getName)

class NoteGeneratorTestCase(unittest.TestCase):

    def test_all(self):
        generator = NoteGenerator("printf 'one\ttwo\n' ; printf 'three\tfour\n'")
        self.assertEqual(['three', 'four'], generator.getNote())
        self.assertEqual(['one', 'two'], generator.getNote())
        generator.command = ""
        self.failUnlessRaises(UserWarning, generator.getNote)

# ----------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test40"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(StringGeneratorTestCase))
    suite.addTest(loader.loadClass(NoteGeneratorTestCase))
    return runner.TrialRunner(
        reporter.VerboseTextReporter,
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
# compile-command: "( cd .. ; ./config.status tests/test-pokerbotlogic.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerbotlogic.py' TESTS='coverage-reset test-pokerbotlogic.py coverage-report' check )"
# End:

