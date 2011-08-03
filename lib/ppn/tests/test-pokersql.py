#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2009 Loic Dachary <loic@dachary.org>
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

import sys, os
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, SCRIPT_DIR)
sys.path.insert(0, "..")

import unittest
import simplejson

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
silence_all_messages()

settings_xml_server = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="3" admin="yes">

  <database name="pokernetworktest" host="localhost" user="pokernetworktest" password="pokernetwork"
            root_user="root" root_password="" schema="%(script_dir)s/../database/schema.sql" command="/usr/bin/mysql" />
</server>
""" % {'script_dir': SCRIPT_DIR}

from pokernetwork import pokersql
from pokernetwork import pokernetworkconfig

class SqlTestCase(unittest.TestCase):

    def destroyDb(self):
        if len("") > 0:
            os.system("/usr/bin/mysql -u root --password='' -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")
        else:
            os.system("/usr/bin/mysql -u root -h 'localhost' -e 'DROP DATABASE IF EXISTS pokernetworktest'")

    def setUp(self):
        self.destroyDb()

    def tearDown(self):
        self.destroyDb()

    def test01_getPath(self):
        self.assertTrue("poker.server.xml" in pokersql.getPath(['a/b/foo.bar']))
        self.assertTrue("config.xml" in pokersql.getPath(['a/b/config.xml']))

    def test02_getSettings(self):
        settings = pokersql.getSettings('%s/pokersql.xml' % SCRIPT_DIR)
        self.assertEquals('true', settings.headerGet("/server/@admin"))
        caught = False
        try:
            pokersql.getSettings('%s/pokersqlfail.xml' % SCRIPT_DIR)
        except AssertionError, e:
            self.assertTrue('enable' in str(e))
            caught = True
        self.assertTrue(caught)

    def test03_runQuery(self):
        settings = pokernetworkconfig.Config([])
        settings.loadFromString(settings_xml_server)
        #
        # return selected rows
        #
        value = '4242'
        os.environ['QUERY_STRING'] = 'query=select%20' + value + '&output=rows'
        output = pokersql.runQuery(settings)
        self.assertTrue('Content-type:' in output, output)
        self.assertTrue(value in output, output)
        #
        # return the number of affected rows
        #
        os.environ['QUERY_STRING'] = 'query=select%200' + value
        output = pokersql.runQuery(settings)
        self.assertTrue('Content-type:' in output, output)
        self.assertTrue('\n1' in output, output)
        os.environ['QUERY_STRING'] = 'query=select%200' + value + '&output=rowcount'
        output = pokersql.runQuery(settings)
        self.assertTrue('Content-type:' in output, output)
        self.assertTrue('\n1' in output, output)
        #
        # return the latest autoincrement
        #
        os.environ['QUERY_STRING'] = 'query=INSERT%20INTO%20messages()VALUES()&output=lastrowid'
        output = pokersql.runQuery(settings)
        self.assertTrue('Content-type:' in output, output)
        self.assertTrue('\n1' in output, output)
        os.environ['QUERY_STRING'] = 'query=INSERT%20INTO%20messages()VALUES()&output=lastrowid'
        output = pokersql.runQuery(settings)
        self.assertTrue('Content-type:' in output, output)
        self.assertTrue('\n2' in output, output)

    def test04_run(self):
        self.assertEquals("Content-type: text/plain\n\n",
                          pokersql.run(['%s/pokersql.xml' % SCRIPT_DIR]))

#--------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SqlTestCase))
    return suite

#--------------------------------------------------------------
def Run(verbose = 2):
    return unittest.TextTestRunner(verbosity=verbose).run(GetTestSuite())

#--------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokersql.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokersql.py' TESTS='coverage-reset test-pokersql.py coverage-report' check )"
# End:
