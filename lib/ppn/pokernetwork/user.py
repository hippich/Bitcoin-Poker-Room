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
from pokernetwork.affiliate import *
from MySQLdb.cursors import DictCursor

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

    def __init__(self, serial = 0, db = None):
        self.db = db
        self.serial = serial
        self.name = "anonymous"
        self.email = ""
        self.url = "random"
        self.outfit = "random"
        self.affiliate = 0
        self.privilege = None
        
        if db != None:
            cursor = self.db.cursor(DictCursor)
            sql = "SELECT name,email,skin_url,skin_outfit,affiliate,privilege FROM users WHERE serial = %s"
            cursor.execute(sql, self.serial)
            if cursor.rowcount != 1:
                print "ERROR: couldn't find serial " + self.serial
                return

            row = cursor.fetchone()
            if row['email'] != None: self.email = row['email']
            if row['affiliate'] != None: self.affiliate = row['affiliate']
            self.name = row['name']
            self.url = row['skin_url']
            self.outfit = row['skin_outfit']
            self.privilege = row['privilege']

            

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

    def getBalance(self, currency_serial):
        money = 0
        print "Getting balance for user with affiliate %d" % self.affiliate
        if self.affiliate != 0:
            # TODO: currency serial?
            affiliate = Affiliate(self.affiliate, self.db)
            money += affiliate.getUserBalance(self.name)

        cursor = self.db.cursor()
        sql = ( "SELECT amount FROM user2money " +
                "WHERE user_serial = %s AND currency_serial = %s" )
        cursor.execute(sql, (self.serial, currency_serial))
        if cursor.rowcount > 1:
            self.error("getBalance(%s) expected one row got %s" % ( self.serial, cursor.rowcount ))
            cursor.close()
            return 0
        elif cursor.rowcount == 1:
            (dbMoney,) = cursor.fetchone()
            money += dbMoney

        cursor.close()
        return money

    def increaseBalance(self, amount, currency_serial):
        cursor = self.db.cursor()
        sql = "UPDATE user2money SET amount = amount + %s WHERE user_serial = %s AND currency_serial = %s"
        cursor.execute(sql, (amount, self.serial, currency_serial))
        if cursor.rowcount == 0:
            sql = "INSERT INTO user2money (user_serial, currency_serial, amount) VALUES (%s, %s, %s)"
            cursor.execute(sql, ( self.serial, currency_serial, amount ))
        #TODO: this could use more auditing
        return True

    def decreaseBalance(self, amount, currency_serial):
        cursor = self.db.cursor()
        sql = ( "UPDATE user2money SET amount = amount - %s" +
                " WHERE user_serial = %s AND currency_serial = %s AND amount >= %s"
              )
        cursor.execute(sql, (amount, self.serial, currency_serial, amount))
        return cursor.rowcount


    def __str__(self):
        return "serial = %s, name = %s, url = %s, outfit = %s, privilege = %s, affiliate = %s" % ( self.serial, self.name, self.url, self.outfit, self.privilege, self.affiliate )
