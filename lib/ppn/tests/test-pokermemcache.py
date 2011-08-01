#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
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
import sys, os
sys.path.insert(0, "./..")
sys.path.insert(0, "..")

import unittest

from pokernetwork.pokermemcache import MemcacheMockup

class MemcacheTestCase(unittest.TestCase):

      def test01(self):
            memcache = MemcacheMockup.Client([''])
            memcache.set('a', 'b')
            self.assertEqual(None, memcache.get('c'))
            self.assertEqual('b', memcache.get('a'))
            self.assertEqual(0, memcache.add('a', 'd'))
            self.assertEqual(1, memcache.add('f', 'g'))
            self.assertEqual(0, memcache.replace('z', 'k'))
            self.assertEqual(1, memcache.replace('f', 'l'))
            self.assertEqual(0, memcache.delete('r'))
            self.assertEqual(1, memcache.delete('f'))
            map = {'A': '1', 'B':'2'}
            self.assertEqual([], memcache.set_multi(map))
            self.assertEqual(map, memcache.get_multi(map.keys()))
            self.assertEqual(1, memcache.delete_multi(map.keys()))
            self.assertEqual({}, memcache.get_multi(map.keys()))
      def test02(self):
            memcache = MemcacheMockup.Client([''])
            memcache.set('a', 'b', time = 1)
            self.assertEqual(1, memcache.expiration['a'])
            map = {'A': 'x', 'B':'y'}
            self.assertEqual([], memcache.set_multi(map, time = 2))
            self.assertEqual(2, memcache.expiration['A'])
            self.assertEqual(2, memcache.expiration['B'])
            memcache.replace('A', 'z', time = 1)
            self.assertEqual(1, memcache.expiration['A'])
            memcache.add('C', 'x', time = 3)
            self.assertEqual(3, memcache.expiration['C'])            
      def test03_checkKeyNoString(self):
            from pokernetwork.pokermemcache import MemcachedStringEncodingError
            from pokernetwork.pokermemcache import check_key
            caughtIt = False
            try:
                  check_key(u'\ufeff')
                  self.fail("Previous line should have caused exception")
            except MemcachedStringEncodingError, mse:
                  self.assertEquals(mse.__str__(),
                  "Keys must be str()'s, notunicode.  Convert your unicode strings using mystring.encode(charset)!")
                  caughtIt = True
            self.failUnless(caughtIt, "MemcachedStringEncodingError was not caught")
      def test04_log(self):
            memcache = MemcacheMockup.Client([''])
            memcache.log = []
            memcache.set('a', 'b', time = 1)
            memcache.set('a', 'c', time = 2)
            self.assertEquals(memcache.log, [('set', ('a', 'b', 1)), ('set', ('a', 'c', 2))])

#--------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(MemcacheTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-pokermemcache.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokermemcache.py' TESTS='coverage-reset test-pokermemcache.py coverage-report' check )"
# End:
