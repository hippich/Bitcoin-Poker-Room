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
# 
from twisted.internet import reactor, protocol, error, defer
from struct import pack, unpack

from pokernetwork.packets import *
from pokernetwork.protocol import UGAMEProtocol
from pokernetwork.user import User

class UGAMEClientProtocol(UGAMEProtocol):
    """ """
    def __init__(self):
        self._ping_timer = None
        self.user = User()
        self.bufferized_packets = []
        UGAMEProtocol.__init__(self)
        self._ping_delay = 5
        self.connection_lost_deferred = defer.Deferred()

    def getSerial(self):
        return self.user.serial

    def getName(self):
        return self.user.name

    def getUrl(self):
        return self.user.url

    def getOutfit(self):
        return self.user.outfit

    def isLogged(self):
        return self.user.isLogged()
    
    def sendPacket(self, packet):
        if self.established != 0:
            self.ping()
            if self.factory.verbose > 2:
                self.message("%ssendPacket(%d) %s " % ( self._prefix, self.user.serial, packet ))
            self.dataWrite(packet.pack())
        else:
            if self.factory.verbose > 2:
                self.message("%ssendPacket bufferized %s " % ( self._prefix, packet ))
            self.bufferized_packets.append(packet)

    def ping(self):
        if not hasattr(self, "_ping_timer") or not self._ping_timer:
            return

        if self._ping_timer.active():
            self._ping_timer.reset(self._ping_delay)
        else:
            if self.factory.verbose > 6:
                self.message("%ssend ping" % self._prefix)
            self.dataWrite(PacketPing().pack())
            self._ping_timer = reactor.callLater(self._ping_delay, self.ping)
        
    def protocolEstablished(self):
        self._ping_timer = reactor.callLater(self._ping_delay, self.ping)
        d = self.factory.established_deferred
        self.factory.established_deferred = None
        d.callback(self)
        for packet in self.bufferized_packets:
            self.sendPacket(packet)
        self.bufferized_packets = []
        self.factory.established_deferred = defer.Deferred()

    def protocolInvalid(self, server, client):
        # FIXME: I am not completely sure this method makes sense.  You'll
        # note in ClientServer.test09 in test-clientserver.py.in where I
        # cover this code, it seems that 'server' and 'client' arguments
        # are something different entirely.  This is because the code that
        # calls protocolInvalid() in protocol.connectionLost() and
        # protocol._handleVersion() send strings as 'server' and 'client'.
        # The test assumes this is the case, but I think someone should
        # reexamine this code at some point and make sure it is doing what
        # we really expect. -- bkuhn, 2008-10-13
        if not self.factory.established_deferred.called:
            self.factory.established_deferred.errback((self, server, client),)
            
    def connectionLost(self, reason):
        if hasattr(self, "_ping_timer") and self._ping_timer and self._ping_timer.active():
            self._ping_timer.cancel()
        self._ping_timer = None
        self.factory.protocol_instance = None
        UGAMEProtocol.connectionLost(self, reason)
        if not reason.check(error.ConnectionDone) and self.factory.verbose > 3:
            self.message("UGAMEClient.connectionLost %s" % reason)
        d = self.connection_lost_deferred
        self.connection_lost_deferred = None
        d.callback(self)
        self.connection_lost_deferred = defer.Deferred()

class UGAMEClientFactory(protocol.ClientFactory):

    def __init__(self, *args, **kwargs):
        self.protocol = UGAMEClientProtocol
        self.protocol_instance = None
        self.verbose = 0
        self.established_deferred = defer.Deferred()

    def error(self, string):
        self.message("ERROR " + string)
        
    def message(self, string):
        print string
        
    def buildProtocol(self, addr):
        instance = self.protocol()
        instance.factory = self
        self.protocol_instance = instance
        return instance

    def clientConnectionLost(self, connector, reason):
        pass
