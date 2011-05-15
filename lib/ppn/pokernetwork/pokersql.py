#
# -*- coding: iso-8859-1 -*-
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
import sys
import cgi
import cgitb
from MySQLdb.cursors import DictCursor
try:
        import json # native in python-2.6
except:
        import simplejson as json
sys.path.insert(0, ".")
sys.path.insert(0, "..")

from pokernetwork.pokernetworkconfig import Config
from pokernetwork.pokerdatabase import PokerDatabase

def getPath(argv):
    default_path = "/etc/poker-network/poker.server.xml"
    return argv[-1][-4:] == ".xml" and argv[-1] or default_path    
        
def getSettings(path):
    settings = Config([''])
    settings.load(path)
    assert settings.headerGet("/server/@admin") in ( "yes", "true" ), "set <server admin='yes'> in %s to enable this CGI. It means anyone with access to the CGI will be able to inject arbitrary SQL code in the MySQL server" % path
    return settings

def runQuery(settings):
    if not settings.headerGet('/server/database/@name'):
            return "Content-type: text/plain\n\n"
    settings.headerSet('/server/@verbose', '0')
    db = PokerDatabase(settings)
    cgitb.enable()
    form = cgi.FieldStorage()
    cursor = db.cursor(DictCursor)
    cursor.execute(form["query"].value)
    if not form.has_key('output'):
            result = cursor.rowcount
    elif form["output"].value == "rows":
            result = cursor.fetchall()
    elif form["output"].value == "lastrowid":
            result = cursor.lastrowid
    else:
            result = cursor.rowcount
    cursor.close()
    return "Content-type: text/plain\n\n" + json.dumps(result)

def run(argv):
    settings = getSettings(getPath(argv))
    return runQuery(settings)

if __name__ == '__main__': print run(sys.argv)
