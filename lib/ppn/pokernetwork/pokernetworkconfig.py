#
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
#
from pokerengine import pokerengineconfig
from pokernetwork.version import version
import libxml2

class Config(pokerengineconfig.Config):

    upgrades_repository = None
    verbose = 0

    def __init__(self, *args, **kwargs):
        pokerengineconfig.Config.__init__(self, *args, **kwargs)
        self.version = version
        self.notify_updates = []

    def loadFromString(self, string):
        self.path = "<string>"
        self.doc = libxml2.parseMemory(string, len(string))
        self.header = self.doc.xpathNewContext()

    def load(self, path):
        status = pokerengineconfig.Config.load(self, path)
        if Config.upgrades_repository:
            if self.checkVersion("poker_network_version", version, Config.upgrades_repository):
                return status
            else:
                return False
        else:
            return status

    def notifyUpdates(self, method):
        if method not in self.notify_updates:
            self.notify_updates.append(method)

    def denotifyUpdates(self, method):
        if method in self.notify_updates:
            self.notify_updates.remove(method)
        
    def headerSet(self, name, value):
        result = pokerengineconfig.Config.headerSet(self, name, value)
        for method in self.notify_updates:
            method(self)
        return result
