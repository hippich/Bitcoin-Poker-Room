#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2010 Johan Euphrosine <proppy@aminche.com>
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

import tempfile
from pokernetwork import pokerbot
from twisted.application import service
from twisted.internet import defer

settings_xml_bots_generated = """<?xml version="1.0" encoding="ISO-8859-1"?>
<settings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="poker-bot.xsd" delays="false" wait="1" reconnect="yes" watch="no" level="1" cash_in="no" ping="10" verbose="0" no_display_packets="yes" rebuy="yes" name_prefix="BOT" poker_network_version="2.0.0">
  <delays position="0" begin_round="0" end_round="0" end_round_last="0" showdown="5" lag="15"/>
  <name>test</name>
  <passwd>test</passwd>
  <servers>hostname:19380</servers>
  <muck>yes</muck>
  <auto_post>yes</auto_post>
  <currency id="1">/usr/bin/wget wget --quiet -O - 'http://pokersource.info/poker-web/currency_one.php?id=1&amp;command=get_note&amp;value=5000000&amp;count=100&amp;autocommit=yes'</currency>
  <path>/etc/poker-engine</path>

  <table name="One" count="4"/>

  <tournament name="sitngo4" count="4"/>

</settings>
"""

settings_xml_bots_named = """<?xml version="1.0" encoding="ISO-8859-1"?>
<settings xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="poker-bot.xsd" delays="false" wait="1" reconnect="yes" watch="no" level="1" cash_in="no" ping="10" verbose="0" no_display_packets="yes" rebuy="yes" name_prefix="BOT" poker_network_version="2.0.0">
  <delays position="0" begin_round="0" end_round="0" end_round_last="0" showdown="5" lag="15"/>
  <name>test</name>
  <passwd>test</passwd>
  <servers>hostname:19380</servers>
  <muck>yes</muck>
  <auto_post>yes</auto_post>
  <currency id="1">/usr/bin/wget wget --quiet -O - 'http://pokersource.info/poker-web/currency_one.php?id=1&amp;command=get_note&amp;value=5000000&amp;count=100&amp;autocommit=yes'</currency>
  <path>/etc/poker-engine</path>

  <table name="One">
        <bot name="foo1" password="bar1" />
        <bot name="foo2" password="bar2" />
        <bot name="foo3" password="bar3" />
  </table>

  <tournament name="sitngo4">
        <bot name="foo4" password="bar4" />
        <bot name="foo5" password="bar5" />
  </tournament>

</settings>
"""

class PokerBotTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.filename = os.path.join(self.tmpdir, "poker.server.xml")

    def createConfig(self, config):
        f = open(self.filename, "w")
        f.write(config)
        f.close()

    def test01_generated(self):
        self.createConfig(settings_xml_bots_generated)
        services = pokerbot.makeService(self.filename)
        self.assertEquals(8, len([s for s in services]))

    def test02_named(self):
        self.createConfig(settings_xml_bots_named)
        services = pokerbot.makeService(self.filename)
        factories = [s.args[2] for s in services]
        self.assertEquals(5, len(factories))
        for i, f in enumerate(factories):
            self.assertEquals('foo%s' % (i+1), f.name)
            self.assertEquals('bar%s' % (i+1), f.password)
        factories[0].reconnect = True
        factories[0].went_broke = True
        d = defer.Deferred()
        class DummyConnector:
            def connect(self):
                d.callback(None)
        factories[0].clientConnectionLost(DummyConnector(), 'reason')
        self.assertEquals('foo1', factories[0].name)
        return d

# ----------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test01"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(PokerBotTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-pokerbot.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerbot.py' TESTS='coverage-reset test-pokerbot.py coverage-report' check )"
# End:

