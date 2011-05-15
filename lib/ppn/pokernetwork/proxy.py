#
# Copyright (C) 2006 Mekensleep
#
# Mekensleep
# 24 rue vieille du temple
# 75004 Paris
#       licensing@mekensleep.com
#
# MIT License
# 
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Authors:
#  Loic Dachary <loic@gnu.org>
#
from twisted.internet import base, tcp, ssl, interfaces, protocol, address
from re import match

#
# implements draft-luotonen-web-proxy-tunneling-01.txt
#
class ConnectProtocol(protocol.Protocol):

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.buffer = ""

    def connectionMade(self):
        self.transport.write('CONNECT %s:%d HTTP/1.0\n\n' % ( self.host, self.port ) )
        self.bufferSize = self.transport.bufferSize
        #
        # Read bytes one by one because we don't want to read
        # ONE too many byte from the input (this extra byte will
        # be the first of the protocol being proxied).
        #
        self.transport.bufferSize = 1

    def dataReceived(self, data):
        self.buffer += data
        buffer = self.buffer.replace('\r','')
        if '\n\n' in buffer:
            if not match("^HTTP/\d\.\d\s+2\d\d", buffer):
                raise Exception, buffer
            self.transport.bufferSize = self.bufferSize
            self.transport._proxyConnectDone()

class Client(ssl.Client):

    def __init__(self, host, port, bindAddress, contextFactory, connector, proxy, reactor=None):
        self.contextFactory = contextFactory
        self.proxy = proxy
        ssl.Client.__init__(self, host, port, bindAddress, contextFactory, connector, reactor)

    def getHost(self):
        h, p = self.socket.getsockname()
        bwHack = self.contextFactory and 'SSL' or 'INET'
        return address.IPv4Address('TCP', h, p, bwHack)

    def getPeer(self):
        bwHack = self.contextFactory and 'SSL' or 'INET'
        return address.IPv4Address('TCP', self.addr[0], self.addr[1], bwHack)

    def _connectDone(self):
        if self.proxy:
            self.protocol = ConnectProtocol(*self.proxy)
            self.connected = 1
            self.protocol.makeConnection(self)
            self.logstr = self.protocol.__class__.__name__+",client"
            self.startReading()
        else:
            self._proxyConnectDone()
            
    def _proxyConnectDone(self):
        #
        # Will be reset by Client._connecDone but do it anyway to 
        # remind ourselves that the proxy protocol is to be discarded
        #
        self.protocol = None
        if self.contextFactory:
            self.startTLS(self.contextFactory)
            self.startWriting()
        tcp.Client._connectDone(self)

class Connector(ssl.Connector):
    """
    TCP Connector (with or without SSL) that is able to connect thru a transparent proxy.
    Example usage:

    c = Connector(host = "foo.com", port = 25, factory = client_factory,
                  contextFactory = ssl.ClientContextFactory(),
                  timeout = 60, bindAddress = None, reactor = reactor)
    c.setProxyHost("myproxy.com:80")
    c.connect()

    The connector will connect to myproxy.com and send it a request to connect to foo.com:25.
    When myproxy.com acknoledges that the connection to foo.com:25 is established, the
    connector behaves exactly as if a direct connection to foo.com:25 was made. Except that
    foo.com:25 will see a connection from myproxy.com instead.

    This transparent proxy method is documented in draft-luotonen-web-proxy-tunneling-01.txt
    and implemented in the mod_proxy apache module (look for the AllowCONNECT directive in
    the documentation).

    """
    def __init__(self, host, port, factory, contextFactory, timeout, bindAddress, reactor=None):
        self.host = host
        self.port = port
        self.proxy = None
        ssl.Connector.__init__(self, host, port, factory, contextFactory, timeout, bindAddress, reactor)

    def setProxyHost(self, host):
        host = host.split(':')
        self.proxy = ( host[0], int(host[1]) )
                     
    def _makeTransport(self):
        return Client(self.host, self.port, self.bindAddress, self.contextFactory, self, self.proxy, self.reactor)

    def getDestination(self):
        bwHack = self.contextFactory and 'SSL' or 'INET'
        return address.IPv4Address('TCP', self.host, self.port, bwHack)
