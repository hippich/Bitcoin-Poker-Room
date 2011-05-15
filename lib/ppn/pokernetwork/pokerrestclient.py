#
# Copyright (C) 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2009 Johan Euphrosine <proppy@aminche.com>
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
from twisted.web import http, client
from twisted.python.util import InsensitiveDict
from twisted.python.runtime import seconds
from pokernetwork.pokerpackets import *

import pokersite

class RestClientFactory(protocol.ClientFactory):

    protocol = client.HTTPPageGetter
    
    def __init__(self, host, port, path, data, timeout = 60):
        self.timeout = timeout
        self.agent = "RestClient"
        self.headers = InsensitiveDict()
        self.headers.setdefault('Content-Length', len(data))
        self.headers.setdefault("connection", "close")
        self.method = 'POST'
        self.url = 'http://' + host + ':' + str(port) + path
        self.postdata = data
        self.host = host
        self.port = port
        self.path = path
        self.waiting = 1
        self.deferred = defer.Deferred()
        self.response_headers = None
        self.cookies = {}

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__, self.url)

    def buildProtocol(self, addr):
        p = protocol.ClientFactory.buildProtocol(self, addr)
        if self.timeout:
            timeoutCall = reactor.callLater(self.timeout, p.timeout)
            self.deferred.addBoth(self._cancelTimeout, timeoutCall)
        return p

    def _cancelTimeout(self, result, timeoutCall):
        if timeoutCall.active():
            timeoutCall.cancel()
        return result

    def gotHeaders(self, headers):
        self.response_headers = headers
        
    def gotStatus(self, version, status, message):
        self.version, self.status, self.message = version, status, message

    def page(self, page):
        if self.waiting:
            self.waiting = 0
            self.deferred.callback(page)

    def noPage(self, reason):
        if self.waiting:
            self.waiting = 0
            self.deferred.errback(reason)

    def clientConnectionFailed(self, _, reason):
        if self.waiting:
            self.waiting = 0
            self.deferred.errback(reason)

class PokerRestClient:
    DEFAULT_LONG_POLL_FREQUENCY = 0.1
    
    def __init__(self, host, port, path, longPollCallback, verbose = 0, timeout = 60):
        self.verbose = verbose
        self.queue = defer.succeed(True)
        self.pendingLongPoll = False
        self.minLongPollFrequency = 0.01
        self.sentTime = 0
        self.host = host
        self.port = port
        self.path = path
        self.timer = None
        self.timeout = timeout
        self.longPollCallback = longPollCallback
        if longPollCallback:
            self.longPollFrequency = PokerRestClient.DEFAULT_LONG_POLL_FREQUENCY
            self.scheduleLongPoll(0)
        else:
            self.longPollFrequency = -1

    def message(self, string):
        print 'PokerRestClient(%s) %s' % ( self.host + ':' + str(self.port), string )

    def sendPacket(self, packet, data):
        if self.pendingLongPoll:
            self.sendPacketData('{ "type": "PacketPokerLongPollReturn" }')
        d = defer.Deferred()
        d.addCallbacks(self.receivePacket, self.receiveError)
        self.queue.addCallback(lambda status: self.sendPacketData(data))
        self.queue.chainDeferred(d)
        if packet.type == PACKET_POKER_LONG_POLL:
            self.pendingLongPoll = True
        return d

    def receivePacket(self, data):
        if self.verbose > 3:
            self.message('receivePacket ' + data)
        if self.pendingLongPoll:
            self.scheduleLongPoll(0)
        self.pendingLongPoll = False
        args = simplejson.loads(data, encoding = 'UTF-8')
        args = pokersite.fromutf8(args)
        packets = pokersite.args2packets(args)
        return packets

    def receiveError(self, data):
        return [ PacketError(message = str(data)) ]
    
    def sendPacketData(self, data):
        if self.verbose > 3:
            self.message('sendPacketData ' + data)
        factory = RestClientFactory(self.host, self.port, self.path, data, self.timeout)
        reactor.connectTCP(self.host, self.port, factory)
        self.sentTime = seconds()
        return factory.deferred

    def clearTimeout(self):
        if self.timer and self.timer.active():
            self.timer.cancel()
        self.timer = None
        
    def scheduleLongPoll(self, delta):
        self.clearTimeout()
        self.timer = reactor.callLater(max(self.minLongPollFrequency, self.longPollFrequency - delta), self.longPoll)

    def longPoll(self):
        if self.longPollFrequency > 0:
            delta = seconds() - self.sentTime
            in_line = len(self.queue.callbacks)
            if in_line <= 0 and delta > self.longPollFrequency:
                self.clearTimeout()
                d = self.sendPacket(PacketPokerLongPoll(),'{ "type": "PacketPokerLongPoll" }')
                d.addCallback(self.longPollCallback)
            else:
                self.scheduleLongPoll(delta)
        
class PokerProxyClient(http.HTTPClient):
    """
    Used by PokerProxyClientFactory to implement a simple web proxy.
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

class PokerProxyClientFactory(protocol.ClientFactory):

    serial = 0
    
    protocol = PokerProxyClient

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
        PokerProxyClientFactory.serial += 1
        self.serial = PokerProxyClientFactory.serial

    def message(self, string):
        print 'PokerProxyRestClient(%d) %s' % ( self.serial, string )

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
