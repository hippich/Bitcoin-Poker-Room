#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
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
sys.path.insert(0, "..")
sys.path.insert(0, "..")

import unittest
import simplejson
from struct import pack, unpack, calcsize

from pokernetwork import pokerclientpackets

class JavaScriptGenerator:
    def __init__(self, type):
        self.type = type

    
class JavaScriptGeneratorTestCase(unittest.TestCase):

    #--------------------------------------------------------------    
    def test_all(self):
        result = []
        for (index, name) in pokerclientpackets.PacketNames.iteritems():
            result.append(name + ": "  + str(index))
        print "{ " + ", ".join(result) + " }";

#--------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(JavaScriptGeneratorTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-javascript.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/packets.py' TESTS='coverage-reset test-javascript.py coverage-report' check )"
# End:
