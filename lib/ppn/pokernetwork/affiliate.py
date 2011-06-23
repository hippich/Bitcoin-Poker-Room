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
from urllib2 import urlopen, HTTPError

import MySQLdb

class Affiliate:
    def __init__(self, serial = 0, db = None):
        self.serial = serial
        self.db = db
        if db == None:
            self.balance = 0
            self.escrow = 0
            self.prefix = "BTC"
            self.serviceUrl = "http://example.com/"
            return

        cursor = db.cursor()
        sql = "SELECT serial,balance,escrow,prefix,service_url FROM affiliates WHERE serial = %s"
        cursor.execute(sql, serial)
        if cursor.rowcount == 0:
            return
        (self.serial,self.balance,self.escrow,self.prefix,self.serviceUrl) = cursor.fetchone()
        cursor.close()

    def getAvailable(self):
        return self.escrow + self.balance

    def getUserBalance(self, username):
        endpoint = "balance/" + username
        print "Affiliate: Getting balance from endpoint " + self.serviceUrl + endpoint
        try:
            u = urlopen(self.serviceUrl + endpoint)
            userBalance = int(u.read())
            return min(userBalance, self.getAvailable())
        except HTTPError:
            return 0

    def withdraw(self, user, amount):
        if (self.balance + self.escrow) < amount:
            return None

        endpoint = "withdraw/%s/%d" % (user.name, amount)
        print "Affiliate: Attempting withdraw of %d from endpoint %s" % (amount, self.serviceUrl + endpoint)
        try:
            u = urlopen(self.serviceUrl + endpoint)
            result = u.read().rstrip()
            if (result != "OK"):
                print "Affiliate: Received non-OK response: " + result
                return None
        except HTTPError:
            return None

        user.increaseBalance(amount, 1)
        self.decreaseBalance(amount)
        print "Affiliate: Successfully withdrew money"
        return amount

    def deposit(self, user, amount):
        if user.decreaseBalance(amount, 1) != 1:
            return None

        endpoint = "deposit/%s/%d" % (user.name, amount)
        
        print "Affiliate: Attempting deposit of %d to endpoint %s" % (amount, self.serviceUrl + endpoint)
        try:
            u = urlopen(self.serviceUrl + endpoint)
            result = u.read().rstrip()
            if (result != "OK"):
                user.increaseBalance(amount, 1)
                return None
        except HTTPError:
            user.increaseBalance(amount, 1)
            return None

        self.increaseBalance(amount)
        return amount

    def increaseBalance(self, amount):
        cursor = self.db.cursor()
        sql = "UPDATE affiliates SET balance = balance + %s WHERE serial = %s"
        cursor.execute(sql, (amount, self.serial))
        if cursor.rowcount != 1:
            return False

        return True

    def decreaseBalance(self, amount):
        cursor = self.db.cursor()
        sql = "UPDATE affiliates SET balance = balance - %s WHERE serial = %s"
        cursor.execute(sql, (amount, self.serial))
        if cursor.rowcount != 1:
            return False

        return True
