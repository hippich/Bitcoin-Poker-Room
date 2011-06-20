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
from re import match
import urllib

import MySQLdb

def getAffiliateInfo(db, serial):
    cursor = db.cursor()
    sql = "SELECT serial,balance,escrow,prefix,service_url FROM affiliates WHERE serial = %d"
    cursor.execute(sql, serial)
    if cursor.rowcount == 0:
        return Affiliate()

    (serial,balance,escrow,prefix,serviceUrl) = cursor.fetchone()
    cursor.close()

    a = Affiliate(serial)
    a.balance = balance
    a.escrow = escrow
    a.prefix = prefix
    a.serviceUrl = serviceUrl
    a.db = db
    return a

class Affiliate:
    def __init__(self, serial = 0):
        self.serial = serial
        self.balance = 0
        self.escrow = 0
        self.prefix = "BTC"
        self.serviceUrl = "http://example.com/"
        self.db = None

    def getUserBalance(self, username):
        endpoint = "balance/" + username
        u = urllib.urlopen(self.serviceUrl + endpoint)
        return int(u.read())

    def withdraw(self, user, amount):
        if (self.balance + self.escrow) < amount:
            return None

        endpoint = "withdraw/" + user.name + "/" + amount
        u = urllib.urlopen(self.serviceUrl + endpoint)
        result = u.read()
        if (result != "OK"):
            return None

        user.increaseBalance(amount, 1)
        self.decreaseBalance(amount)

    def deposit(self, user, amount):
        if user.decreaseBalance(amount, 1) != 1:
            return None

        endpoint = "deposit/%s/%d" % (user.name, amount)
        u = urllib.urlopen(self.serviceUrl + endpoint)
        result = u.read()
        if (result != "OK"):
            user.increaseBalance(amount, 1)
            return None

        self.increaseBalance(amount)
        return amount

    def increaseBalance(self, amount):
        cursor = db.cursor()
        sql = "UPDATE affiliates SET balance = balance + %d WHERE serial = %d"
        cursor.execute(sql, (amount, self.serial))
        if cursor.rowcount != 1:
            return False

        return True

    def decreaseBalance(self, amount):
        cursor = db.cursor()
        sql = "UPDATE affiliates SET balance = balance - %d WHERE serial = %d"
        cursor.execute(sql, (amount, self.serial))
        if cursor.rowcount != 1:
            return False

        return True
