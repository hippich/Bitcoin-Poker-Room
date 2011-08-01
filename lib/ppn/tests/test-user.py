# -*- mode: python -*-
#
# Copyright (C)             2008 Bradley M. Kuhn <bkuhn@ebb.org>
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

import sys, os
sys.path.insert(0, "..")

import unittest
import os.path
import types

from tests.testmessages import silence_all_messages, clear_all_messages, get_messages
silence_all_messages()

from pokernetwork.user import User
from pokernetwork import user as userClass
from pokernetwork.pokerpackets import PacketPokerSetAccount as mylimits

class PokerUserTestCase(unittest.TestCase):
        
    # -----------------------------------------------------------------------------------------------------
    def setUp(self):
        pass
    # -----------------------------------------------------------------------------------------------------    
    def tearDown(self):
        pass
    # -----------------------------------------------------------------------------------------------------    
    def test01_init(self):
        """test01_init
        test initialization of object"""

        user = User(4815162342)
        self.assertEquals(user.isLogged(), True)
        self.assertEquals(user.serial, 4815162342)
        self.assertEquals(user.name, 'anonymous')
        self.assertEquals(user.url, 'random')
        self.assertEquals(user.outfit, 'random')
        self.assertEquals(user.privilege, None)
    # -----------------------------------------------------------------------------------------------------    
    def test02_logout(self):
        """test02_logout
        test logout, isLogged, and __str__ methods"""

        user = User(4815162342)
        self.assertEquals(user.isLogged(), True)
        user.name = "Joe"
        user.url = "http://example.org/"
        user.outfit = "naked"
        user.privilege = User.ADMIN
        self.assertEquals(user.isLogged(), True)

        # Test __str__
        self.assertEquals("%s" % user, 'serial = 4815162342, name = Joe, url = http://example.org/, outfit = naked, privilege = %d' % User.ADMIN)

        user.logout()
        self.assertEquals(user.isLogged(), False)
        self.assertEquals(user.serial, 0)
        self.assertEquals(user.name, 'anonymous')
        self.assertEquals(user.url, 'random')
        self.assertEquals(user.outfit, 'random')
        self.assertEquals(user.privilege, None)
    # -----------------------------------------------------------------------------------------------------    
    def test03_hasPrivilege(self):
        """test03_hasPrivilege
        test hasPrivilege method"""
        user = User(4815162342)
        self.assertEquals(user.hasPrivilege(None), True)
        self.assertEquals(user.hasPrivilege(User.ADMIN), False)
        self.assertEquals(user.hasPrivilege(User.REGULAR), False)
        user.privilege = User.REGULAR
        self.assertEquals(user.hasPrivilege(None), True)
        self.assertEquals(user.hasPrivilege(User.ADMIN), False)
        self.assertEquals(user.hasPrivilege(User.REGULAR), True)
        user.privilege = User.ADMIN
        self.assertEquals(user.hasPrivilege(None), True)
        self.assertEquals(user.hasPrivilege(User.ADMIN), True)
        self.assertEquals(user.hasPrivilege(User.REGULAR), True)
        user.logout()
        self.assertEquals(user.hasPrivilege(None), True)
        self.assertEquals(user.hasPrivilege(User.ADMIN), False)
        self.assertEquals(user.hasPrivilege(User.REGULAR), False)
    # -----------------------------------------------------------------------------------------------------    
    def test04_checkName(self):
        """test04_checkName
        test checkName static function"""

        # Empty string.
        self.assertEquals(userClass.checkName(""),
                          (False, mylimits.NAME_TOO_SHORT, 'login name must be at least 5 characters long'))


        # First, loops to test length only.  All generated strings should be valid

        #                                 [A-Z]          [a-z]     
        atoZ = [ chr(xx) for xx in range(65, 91) + range(97,123) ]
        underbar =  [ '_' ]
        #                             [0-9]
        nums = [ chr(xx) for xx in range(48, 58) ]
        weirdChars =  [ chr(xx) for xx in range(33, 48) + range(91, 94) ]

        # SPEED NOTE: replaced atoZ with [ 'a', 'z', 'h', 'H', 'A', 'Z' ] for speed
        for first in [ 'a', 'z', 'h', 'H', 'A', 'Z' ]:
            for cc in  [ 'a', 'z', 'A', 'Z' ] + nums + underbar:
                name = first
                while len(name) < userClass.NAME_LENGTH_MIN:
                    self.assertEquals(userClass.checkName(name),
                                      (False, mylimits.NAME_TOO_SHORT, 'login name must be at least 5 characters long'))
                    name += cc
                while len(name) <= userClass.NAME_LENGTH_MAX:
                    self.assertEquals(userClass.checkName(name), (True, None, None))
                    if len(name) < userClass.NAME_LENGTH_MAX:
                        for dd in underbar + nums:
                            self.assertEquals(userClass.checkName(dd + name),
                                              (False, mylimits.NAME_MUST_START_WITH_LETTER,
                                               'login name must start with a letter'))
                            self.assertEquals(userClass.checkName(name + dd), (True, None, None))
                        for dd in weirdChars:
                            self.assertEquals(userClass.checkName(dd + name),
                                              (False, mylimits.NAME_MUST_START_WITH_LETTER,
                                               'login name must start with a letter'))
                            self.assertEquals(userClass.checkName(name + dd),
                                              (False, mylimits.NAME_NOT_ALNUM,
                                               'login name must be all letters, digits or underscore '))
                    name += cc
                for kk in range(20):
                    self.assertEquals(userClass.checkName(name), 
                                      (False, mylimits.NAME_TOO_LONG, 'login name must be at most 50 characters long'))
    # -----------------------------------------------------------------------------------------------------    
    def test05_checkPassword(self):
        """test05_checkPassword
        test checkPassword static function"""

        # Empty string.
        self.assertEquals(userClass.checkPassword(""),
                          (False, mylimits.PASSWORD_TOO_SHORT, 'password must be at least %d characters long' % userClass.PASSWORD_LENGTH_MIN))


        # First, loops to test length only.  All generated strings should be valid

        #                                 [A-Z]          [a-z]     
        atoZ = [ chr(xx) for xx in range(65, 91) + range(97,123) ]
        underbar =  [ '_' ]
        #                             [0-9]
        nums = [ chr(xx) for xx in range(48, 58) ]
        weirdChars =  [ chr(xx) for xx in range(33, 48) + range(91, 94) ]

        # SPEED NOTE: replaced atoZ with [ 'a', 'z', 'h', 'H', 'A', 'Z' ] for speed
        for cc in  [ 'a', 'z', 'H', 'h' 'A', 'Z' ] + nums:
            pw = cc
            while len(pw) < userClass.PASSWORD_LENGTH_MIN:
                self.assertEquals(userClass.checkPassword(pw),
                                  (False, mylimits.PASSWORD_TOO_SHORT, 'password must be at least %d characters long' % userClass.PASSWORD_LENGTH_MIN))
                pw += cc
            while len(pw) <= userClass.PASSWORD_LENGTH_MAX:
                self.assertEquals(userClass.checkPassword(pw), (True, None, None))
                if len(pw) < userClass.PASSWORD_LENGTH_MAX:
                    for dd in weirdChars:
                        self.assertEquals(userClass.checkPassword(pw + dd),
                                          (False, mylimits.PASSWORD_NOT_ALNUM,
                                           'password must be all letters and digits'))
                pw += cc
            for kk in range(20):
                self.assertEquals(userClass.checkPassword(pw), 
                                  (False, mylimits.PASSWORD_TOO_LONG, 'password must be at most %d characters long' % userClass.PASSWORD_LENGTH_MAX))
    # -----------------------------------------------------------------------------------------------------    
    def test06_checkNameAndPassword(self):
        """test06_checkNameAndPassword
        make sure check and password name"""
        global thisCount
        thisCount = 0
        def firstOneNone(name):
            return (None, "one", "one")
        def firstOneFalse(name):
            return (False, "two", "two")
        def firstOneTrue(name):
            return (True, "three", "three")
        def countCall(password):
            global thisCount
            thisCount += 1
            return (True, "FOUND", "FOUND")

        saveCheckName = userClass.checkName
        saveCheckPassword = userClass.checkPassword

        userClass.checkPassword = countCall

        userClass.checkName = firstOneNone
        self.assertEquals(userClass.checkNameAndPassword("dummy", "dummy"), (None, "one", "one"))
        self.assertEquals(thisCount, 0)

        userClass.checkName = firstOneFalse
        self.assertEquals(userClass.checkNameAndPassword("dummy", "dummy"), (False, "two", "two"))
        self.assertEquals(thisCount, 0)

        userClass.checkName = firstOneTrue
        self.assertEquals(userClass.checkNameAndPassword("dummy", "dummy"), (True, "FOUND", "FOUND"))
        self.assertEquals(thisCount, 1)

        userClass.checkName = saveCheckName 
        userClass.checkPassword = saveCheckPassword 
# -----------------------------------------------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PokerUserTestCase))
    # Comment out above and use line below this when you wish to run just
    # one test by itself (changing prefix as needed).
#    suite.addTest(unittest.makeSuite(PokerUserTestCase, prefix = "test05"))
    return suite
# -----------------------------------------------------------------------------------------------------
def Run(verbose):
    suite = GetTestSuite()
    verbosity = int(os.environ.get('VERBOSE_T', 2))
    return unittest.TextTestRunner(verbosity=verbose).run(suite)
    
# -----------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    if Run(int(os.environ.get('VERBOSE_T', 2))).wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-user.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/user.py' TESTS='coverage-reset test-user.py coverage-report' check )"
# End:
