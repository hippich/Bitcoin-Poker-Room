#
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
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

from twisted.internet import defer, protocol, reactor, error
from twisted.web import http

from pokernetwork.pokerpackets import PacketPokerTableJoin

local_reactor = reactor

class ProxyClient(http.HTTPClient):
    """
    Used by ProxyClientFactory to implement a simple web proxy.
    """

    def __init__(self, command, rest, version, headers, data, father):
        self.father = father
        self.command = command
        self.rest = rest
        if "proxy-connection" in headers:
            del headers["proxy-connection"]
        headers["connection"] = "close"
        self.headers = headers
        self.data = data

    def connectionMade(self):
        self.sendCommand(self.command, self.rest)
        for header, value in self.headers.items():
            self.sendHeader(header, value)
        self.endHeaders()
        self.transport.write(self.data)

    def handleStatus(self, version, code, message):
        self.father.setResponseCode(int(code), message)

    def handleHeader(self, key, value):
        self.father.setHeader(key, value)

    def handleResponse(self, buffer):
        self.father.write(buffer)
        
    def connectionLost(self, reason):
        self.father.finish()

class ProxyClientFactory(protocol.ClientFactory):

    serial = 0
    
    protocol = ProxyClient

    def __init__(self, command, rest, version, headers, data, father, verbose, destination):
        self.father = father
        self.command = command
        self.rest = rest
        self.headers = headers
        self.data = data
        self.version = version
        self.deferred = defer.Deferred()
        self.verbose = verbose
        self.noisy = False
        self.destination = destination
        ProxyClientFactory.serial += 1
        self.serial = ProxyClientFactory.serial

    def message(self, string):
        print 'Proxy(%d) %s' % ( self.serial, string )

    def doStart(self):
        if self.verbose >= 3:
            self.message('START %s => %s' % ( self.data, self.destination ))
        protocol.ClientFactory.doStart(self)

    def doStop(self):
        if self.verbose >= 3:
            self.message('STOP')
        protocol.ClientFactory.doStop(self)

#    def error(self, string):
#	self.message("*ERROR* " + str(string))

    def buildProtocol(self, addr):
        return self.protocol(self.command, self.rest, self.version,
                             self.headers, self.data, self.father)

    def clientConnectionFailed(self, connector, reason):
        if not self.deferred.called:
            self.deferred.errback(reason)

    def clientConnectionLost(self, connector, reason):
        if not self.deferred.called:
            if reason.check(error.ConnectionDone):
                self.deferred.callback(True)
            else:
                self.deferred.errback(reason)
        
#
# return a value if all actions were complete
#
def rest_filter(site, request, packet):
    if request.finished:
        #
        # the request has been answered by a filter earlier in the chain
        #
        return True
    service = site.resource.service
    resthost, game_id = service.packet2resthost(packet)
    if resthost:
        ( host, port, path ) = resthost
        parts = request.uri.split('?', 1)
        if len(parts) > 1:
            path += '?' + parts[1]
        request.content.seek(0, 0)
        clientFactory = ProxyClientFactory(
            request.method, path, request.clientproto,
            request.getAllHeaders(), request.content.read(), request,
            service.verbose, host + ':' + str(port) + path)
        local_reactor.connectTCP(host, int(port), clientFactory)
        return clientFactory.deferred
    return True
