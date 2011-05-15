#
# -*- py-indent-offset: 4; coding: iso-8859-1 -*-
#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2008             Johan Euphrosine <proppy@aminche.com>
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
#  Loic Dachary <loic@dachary.org>
#  Johan Euphrosine <proppy@aminche.com>
#  Henry Precheur <henry@precheur.org> (2004)
#  Cedric Pinson <mornifle@plopbyte.net> (2004-2006)

from pokernetwork.user import User
from twisted.python.runtime import seconds

def message(string):
    print "PokerAuth: " + string
    
class PokerAuth:

    def __init__(self, db, settings):
        self.db = db
        self.type2auth = {}
        self.verbose = settings.headerGetInt("/server/@verbose")
        self.auto_create_account = settings.headerGet("/server/@auto_create_account") != 'no'

    def message(self, string):
        print "PokerAuth: " + string

    def error(self, string):
        self.message("*ERROR* " + string)
            
    def SetLevel(self, type, level):
        self.type2auth[type] = level

    def GetLevel(self, type):
        return self.type2auth.has_key(type) and self.type2auth[type]

    def auth(self, name, password):
        cursor = self.db.cursor()
        cursor.execute("SELECT serial, password, privilege FROM users "
                       "WHERE name = '%s'" % name)
        numrows = int(cursor.rowcount)
        serial = 0
        privilege = User.REGULAR
        if numrows <= 0:
            if self.auto_create_account:
                if self.verbose > 1:
                    self.message("user %s does not exist, create it" % name)
                serial = self.userCreate(name, password)
                cursor.close()
            else:
                if self.verbose > 1:
                    self.message("user %s does not exist" % name)
                cursor.close()
                return ( False, "Invalid login or password" )
        elif numrows > 1:
            self.error("more than one row for %s" % name)
            cursor.close()
            return ( False, "Invalid login or password" )
        else:
            (serial, password_sql, privilege) = cursor.fetchone()
            cursor.close()
            if password_sql != password:
                self.message("password mismatch for %s" % name)
                return ( False, "Invalid login or password" )

        return ( (serial, name, privilege), None )

    def userCreate(self, name, password):
        if self.verbose:
            self.message("creating user %s" % name)
        cursor = self.db.cursor()
        cursor.execute("INSERT INTO users (created, name, password) values (%d, '%s', '%s')" %
                       (seconds(), name, password))
        #
        # Accomodate for MySQLdb versions < 1.1
        #
        if hasattr(cursor, "lastrowid"):
            serial = cursor.lastrowid
        else:
            serial = cursor.insert_id()
        if self.verbose:
            self.message("create user with serial %s" % serial)
        cursor.execute("INSERT INTO users_private (serial) values ('%d')" % serial)
        cursor.close()
        return int(serial)

_get_auth_instance = None
def get_auth_instance(db, settings):
    global _get_auth_instance
    if _get_auth_instance == None:
        verbose = settings.headerGetInt("/server/@verbose")
        import imp
        script = settings.headerGet("/server/auth/@script")
        try:
            if verbose > 1:
                message("get_auth_instance: trying to load: '%s'" % script)
            module = imp.load_source("user_defined_pokerauth", script)
            get_instance = getattr(module, "get_auth_instance")
            if verbose > 1:
                message("get_auth_instance: using custom implementation of get_auth_instance: %s" % script)
            _get_auth_instance = get_instance
        except:
            if verbose > 1:
                message("get_auth_instance: falling back on pokerauth.get_auth_instance, script not found: '%s'" % script)
            _get_auth_instance = lambda db, settings: PokerAuth(db, settings)
    return apply(_get_auth_instance, [db, settings])
