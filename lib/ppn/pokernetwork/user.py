#
# Copyright (C) 2008 Loic Dachary
# Copyright (C) 2004, 2005, 2006 Mekensleep <licensing@mekensleep.com>
#                                24 rue vieille du temple, 75004 Paris
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
#  Henry Precheur <henry@precheur.org>
#  Loic Dachary <loic@dachary.org>
#
from re import match

from pokernetwork.pokerpackets import PacketPokerSetAccount

NAME_LENGTH_MAX = 50
NAME_LENGTH_MIN = 5

PASSWORD_LENGTH_MAX = 15
PASSWORD_LENGTH_MIN = 5

def checkName(name):
    if not match("^[a-zA-Z][a-zA-Z0-9_]{" + str(NAME_LENGTH_MIN - 1) + "," + str(NAME_LENGTH_MAX - 1) + "}$", name):
        if len(name) > NAME_LENGTH_MAX:
            return (False, PacketPokerSetAccount.NAME_TOO_LONG, "login name must be at most %d characters long" % NAME_LENGTH_MAX)
        elif len(name) < NAME_LENGTH_MIN:
            return (False, PacketPokerSetAccount.NAME_TOO_SHORT, "login name must be at least %d characters long" % NAME_LENGTH_MIN)
        elif not match("^[a-zA-Z]", name):
            return (False, PacketPokerSetAccount.NAME_MUST_START_WITH_LETTER, "login name must start with a letter")
        else:
            return (False, PacketPokerSetAccount.NAME_NOT_ALNUM, "login name must be all letters, digits or underscore ")

    return (True, None, None)

def checkPassword(password):
    if not match("^[a-zA-Z0-9]{" + str(PASSWORD_LENGTH_MIN) + "," + str(PASSWORD_LENGTH_MAX) + "}$", password):
        if len(password) > PASSWORD_LENGTH_MAX:
            return (False, PacketPokerSetAccount.PASSWORD_TOO_LONG, "password must be at most %d characters long" % PASSWORD_LENGTH_MAX)
        elif len(password) < PASSWORD_LENGTH_MIN:
            return (False, PacketPokerSetAccount.PASSWORD_TOO_SHORT, "password must be at least %d characters long" % PASSWORD_LENGTH_MIN)
        else:
            return (False, PacketPokerSetAccount.PASSWORD_NOT_ALNUM, "password must be all letters and digits")

    return (True, None, None)

def checkNameAndPassword(name, password):
    status = checkName(name)
    if status[0]:
        return checkPassword(password)
    else:
        return status

class User:
    REGULAR = 1
    ADMIN = 2

    def __init__(self, serial = 0):
        self.serial = serial
        self.name = "anonymous"
        self.url = "random"
        self.outfit = "random"
        self.privilege = None

    def logout(self):
        self.serial = 0
        self.name = "anonymous"
        self.url = "random"
        self.outfit = "random"
        self.privilege = None
        
    def isLogged(self):
        return not self.serial == 0

    def hasPrivilege(self, privilege):
        if not privilege:
            return True
        
        return self.privilege >= privilege

    def __str__(self):
        return "serial = %d, name = %s, url = %s, outfit = %s, privilege = %d" % ( self.serial, self.name, self.url, self.outfit, self.privilege )
