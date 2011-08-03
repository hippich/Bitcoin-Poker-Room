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

from pokernetwork.pokergameclient import PokerNetworkGameClient

class PokerNetworkGameClientTestCase(unittest.TestCase):

    def setUp(self):
        self.game = PokerNetworkGameClient("poker.%s.xml", [])
        self.game.verbose = int(os.environ.get('VERBOSE_T', '-1'))

    def test_init(self):
        for key in ( 'currency_serial', 'history_index', 'position_info' ):
            self.failUnless(hasattr(self.game, key))

    def test_reset(self):
        player_list = ['oups']
        self.game.setStaticPlayerList(player_list)
        self.game.reset()
        self.assertEqual(None, self.game.getStaticPlayerList())

    def test_endState(self):
        player_list = ['oups']
        self.game.setStaticPlayerList(player_list)
        self.game.endTurn = lambda: True
        self.game.endState()
        self.assertEqual(None, self.game.getStaticPlayerList())

    def test_cancelState(self):
        player_list = ['oups']
        self.game.setStaticPlayerList(player_list)
        self.game.cancelState()
        self.assertEqual(None, self.game.getStaticPlayerList())

    def test_buildPlayerList(self):
        player_serial = 10
        player_list = [10]
        self.failUnless(self.game.addPlayer(player_serial, 1))
        self.game.getPlayer(player_serial).sit_out = False
        self.game.setStaticPlayerList(player_list)
        self.failUnless(self.game.buildPlayerList(True))
        self.assertEqual(self.game.getStaticPlayerList(), self.game.player_list)
        self.failUnless(self.game.buildPlayerList(False))
        self.assertEqual(self.game.getStaticPlayerList(), self.game.player_list)
        self.game.getPlayer(player_serial).sit_out = True
        self.assertRaises(AssertionError, self.game.buildPlayerList, True)
        self.game.setStaticPlayerList([200])
        self.assertRaises(KeyError, self.game.buildPlayerList, True)

# ----------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test14"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerNetworkGameClientTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-pokergameclient.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokergameclient.py' VERBOSE_T=-1 TESTS='coverage-reset test-pokergameclient.py coverage-report' check )"
# End:

