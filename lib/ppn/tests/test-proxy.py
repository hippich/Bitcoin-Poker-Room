#!/usr/bin/python
# -*- mode: python; coding: iso-8859-1 -*-
#
# Copyright (C) 2009 Bradley M. Kuhn <bkuhn@ebb.org>
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
#  Bradley M. Kuhn <bkuhn@ebb.org>
#
import sys, os, tempfile, shutil
sys.path.insert(0, "./..")
sys.path.insert(0, "..")

import time

from tests import testclock

from twisted.trial import unittest, runner, reporter
import twisted.internet.base
from twisted.internet import reactor, defer, address

from pokernetwork.proxy import ConnectProtocol, Client, Connector

twisted.internet.base.DelayedCall.debug = True

from tests.testmessages import silence_all_messages, search_output, clear_all_messages, get_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
silence_all_messages()
# ----------------------------------------------------------------
class MockTransport():
    def __init__(self, bufSize = None):
        self.bufferSize = bufSize
        self.writtenData = []
        self.proxyConnectDoneCallCount = 0
    def write(self, value):      self.writtenData.append(value)
    def _proxyConnectDone(self): self.proxyConnectDoneCallCount += 1
# ----------------------------------------------------------------
class ProxyConnectProtocolTestCase(unittest.TestCase):
    def test00_ConnectProtocol_init(self):
        cp = ConnectProtocol("myhost", "myport")
        self.assertEquals(cp.host, "myhost")
        self.assertEquals(cp.port, "myport")
        self.assertEquals(cp.buffer, "")
    # -------------------------------------------------------------------------
    def test01_ConnectProtocol_connectionMade(self):
        cp = ConnectProtocol("testhost", 3222)
        cp.transport = MockTransport(23)
        self.assertEquals(cp.transport.bufferSize, 23)
        self.assertEquals(cp.transport.writtenData, [])

        cp.connectionMade()
        self.assertEquals(cp.bufferSize, 23)
        self.assertEquals(cp.buffer, "")
        self.assertEquals(cp.transport.bufferSize, 1)
        self.assertEquals(cp.transport.writtenData,
                          ['CONNECT testhost:3222 HTTP/1.0\n\n'])
        self.assertEquals(cp.transport.proxyConnectDoneCallCount, 0)
    # -------------------------------------------------------------------------
    def test02_ConnectProtocol_dataReceived_noNewlinesThere(self):
        cp = ConnectProtocol("somewhere.example.org", 2723)
        cp.transport = MockTransport(99)
        self.assertEquals(cp.transport.bufferSize, 99)
        self.assertEquals(cp.transport.writtenData, [])

        cp.dataReceived("There are no newlines in this data\rbut has\rback-rs")
        self.failIf(hasattr(cp, 'bufferSize'),
                    "bufferSize not created by mere receive")
        self.assertEquals(cp.buffer,
                          "There are no newlines in this data\rbut has\rback-rs")
        self.assertEquals(cp.transport.bufferSize, 99)
        self.assertEquals(cp.transport.writtenData, [])
        self.assertEquals(cp.transport.proxyConnectDoneCallCount, 0)
    # -------------------------------------------------------------------------
    def test03_ConnectProtocol_dataReceived_newlinesThere_badString(self):
        cp = ConnectProtocol("somewhere.example.org", 2723)
        cp.transport = MockTransport(99)
        self.assertEquals(cp.transport.bufferSize, 99)
        self.assertEquals(cp.transport.writtenData, [])

        caughtIt = False
        try:
            cp.dataReceived("We got two newlines here\n\nBut we'll fail\rno HTTP")
            self.fail("previous line should have thrown exception")
        except Exception, e:
            self.assertEquals(e.__str__(), "We got two newlines here\n\nBut we'll failno HTTP")
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught an Exception")

        self.failIf(hasattr(cp, 'bufferSize'),
                    "bufferSize not created by mere receive")
        self.assertEquals(cp.buffer,
                          "We got two newlines here\n\nBut we'll fail\rno HTTP")
        self.assertEquals(cp.transport.bufferSize, 99)
        self.assertEquals(cp.transport.writtenData, [])
        self.assertEquals(cp.transport.proxyConnectDoneCallCount, 0)
    # -------------------------------------------------------------------------
    def test04_ConnectProtocol_dataReceived_newlinesThere_GoodHTTPString(self):
        cp = ConnectProtocol("another.example.org", 2222)
        cp.transport = MockTransport(26)
        self.assertEquals(cp.transport.bufferSize, 26)
        self.assertEquals(cp.transport.writtenData, [])

        cp.connectionMade()
        self.assertEquals(cp.bufferSize, 26)
        self.assertEquals(cp.buffer, "")
        self.assertEquals(cp.transport.bufferSize, 1)
        self.assertEquals(cp.transport.writtenData,
                          ['CONNECT another.example.org:2222 HTTP/1.0\n\n'])
        self.assertEquals(cp.transport.proxyConnectDoneCallCount, 0)

        cp.dataReceived("HT\rTP\r/9\r.9\r          266\r\r\r\r\n\r\r\n\r\r")

        self.assertEquals(cp.bufferSize, 26)
        self.assertEquals(cp.buffer, "HT\rTP\r/9\r.9\r          266\r\r\r\r\n\r\r\n\r\r")
        self.assertEquals(cp.bufferSize, cp.transport.bufferSize)
        self.assertEquals(cp.transport.proxyConnectDoneCallCount, 1)
        self.assertEquals(cp.transport.writtenData,
                          ['CONNECT another.example.org:2222 HTTP/1.0\n\n'])
    # -------------------------------------------------------------------------
    def test05_ConnectProtocol_dataReceived_HTTP10ConsideredHarmful(self):
        cp = ConnectProtocol("somewhere.example.org", 2723)
        cp.transport = MockTransport(99)
        self.assertEquals(cp.transport.bufferSize, 99)
        self.assertEquals(cp.transport.writtenData, [])

        caughtIt = False
        try:
            cp.dataReceived("HTTP/10.0 200\n\n")
            self.fail("previous line should have thrown exception")
        except Exception, e:
            self.assertEquals(e.__str__(), "HTTP/10.0 200\n\n")
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught an Exception")

        self.failIf(hasattr(cp, 'bufferSize'),
                    "bufferSize not created by mere receive")
        self.assertEquals(cp.buffer, "HTTP/10.0 200\n\n")
        self.assertEquals(cp.transport.bufferSize, 99)
        self.assertEquals(cp.transport.writtenData, [])
        self.assertEquals(cp.transport.proxyConnectDoneCallCount, 0)
# ----------------------------------------------------------------
class MockSocket():
    def getsockname(self):
        return ("mocksocket.example.org", 923)

from twisted.internet import ssl, tcp

class ProxyClientTestCase(unittest.TestCase):
    # -------------------------------------------------------------------------
    # setUp creates MockUp methods for pokernetwork.proxy.Client class.
    # Note that many of the tests.  
    def setUp(self):
        self.client = None
        self.saveMethods = {}

        def sslClientInit(clientSelf, host, port, bindAddress, contextFactory, connector, reactor):
            clientSelf.callCounts = {}
            for ss in ['startReading', 'makeConnection', 'startWriting',                       'startTLS', 'connectionDone', 'tcpConnectDone' ]:
                clientSelf.callCounts[ss] = 0

            clientSelf.addr = (host, port)
            clientSelf.socket = MockSocket()
            self.assertEquals(contextFactory, clientSelf.contextFactory)

        def sslClientStartReading(clientSelf):
            clientSelf.callCounts['startReading'] += 1

        def sslClientStartWriting(clientSelf):
            clientSelf.callCounts['startWriting'] += 1

        def sslClientStartTLS(clientSelf, contextFactory):
            clientSelf.callCounts['startTLS'] += 1
            self.assertEquals(clientSelf.contextFactory, contextFactory)

        def connectProtocolMakeConnection(connectionSelf, clientSelf):
            self.assertEquals(clientSelf, self.client)
            clientSelf.callCounts['makeConnection'] += 1

        def tcpClientConnectDone(clientSelf):
            self.assertEquals(clientSelf, self.client)
            clientSelf.callCounts['tcpConnectDone'] += 1

        self.saveMethods['sslClientInit'] = ssl.Client.__init__
        self.saveMethods['sslClientStartTLS'] = ssl.Client.startTLS
        self.saveMethods['sslClientStartWriting'] = ssl.Client.startWriting
        self.saveMethods['sslClientStartReading'] = ssl.Client.startReading
        self.saveMethods['cpMakeConnection'] = ConnectProtocol.makeConnection
        self.saveMethods['tcpClientConnectDone'] = tcp.Client._connectDone
        ssl.Client.__init__ = sslClientInit
        ssl.Client.startReading = sslClientStartReading
        ConnectProtocol.makeConnection = connectProtocolMakeConnection
        ssl.Client.startTLS = sslClientStartTLS
        ssl.Client.startWriting = sslClientStartWriting
        tcp.Client._connectDone = tcpClientConnectDone
    # -------------------------------------------------------------------------
    def tearDown(self):
        ssl.Client.__init__ = self.saveMethods['sslClientInit']
        ssl.Client.startReading = self.saveMethods['sslClientStartReading']
        ConnectProtocol.makeConnection = self.saveMethods['cpMakeConnection']
        ssl.Client.startTLS = self.saveMethods['sslClientStartTLS']
        ssl.Client.startWriting = self.saveMethods['sslClientStartWriting']
        tcp.Client._connectDone = self.saveMethods['tcpClientConnectDone']
    # -------------------------------------------------------------------------
    def test00_Client_init(self):
        self.client = Client("testhost", 7677, "bindaddr", "fakecontext", 
                             "fakeconnector", "fakeproxy")
        self.assertEquals(self.client.proxy, "fakeproxy")
        self.assertEquals(self.client.contextFactory, "fakecontext")
    # -------------------------------------------------------------------------
    def test01_Client_getHost_contextIsNone(self):
        self.client = Client("testhost", 7677, "bindaddr", None, 
                             "fakeconnector", "fakeproxy")
        host = self.client.getHost()
        self.assertEquals(host._bwHack, 'INET')
        self.assertEquals(host.host, 'mocksocket.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 923)
    # -------------------------------------------------------------------------
    def test02_Client_getHost_contextIsFalse(self):
        self.client = Client("testhost", 7677, "bindaddr", False, 
                             "fakeconnector", "fakeproxy")
        host = self.client.getHost()
        self.assertEquals(host._bwHack, 'INET')
        self.assertEquals(host.host, 'mocksocket.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 923)
    # -------------------------------------------------------------------------
    def test03_Client_getHost_contextIsString(self):
        self.client = Client("testhost", 7677, "bindaddr", "ContextISString", 
                             "fakeconnector", "fakeproxy")
        host = self.client.getHost()
        self.assertEquals(host._bwHack, 'SSL')
        self.assertEquals(host.host, 'mocksocket.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 923)
    # -------------------------------------------------------------------------
    def test04_Client_getHost_contextIsTrue(self):
        self.client = Client("testhost", 7677, "bindaddr", True,
                             "fakeconnector", "fakeproxy")
        host = self.client.getHost()
        self.assertEquals(host._bwHack, 'SSL')
        self.assertEquals(host.host, 'mocksocket.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 923)
    # -------------------------------------------------------------------------
    def test05_Client_getPeer_contextIsNone(self):
        self.client = Client("testhost", 7677, "bindaddr", None, 
                             "fakeconnector", "fakeproxy")
        host = self.client.getPeer()
        self.assertEquals(host._bwHack, 'INET')
        self.assertEquals(host.host, 'testhost')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 7677)
    # -------------------------------------------------------------------------
    def test06_Client_getPeer_contextIsFalse(self):
        self.client = Client("testhost", 7677, "bindaddr", False, 
                             "fakeconnector", "fakeproxy")
        host = self.client.getPeer()
        self.assertEquals(host._bwHack, 'INET')
        self.assertEquals(host.host, 'testhost')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 7677)
    # -------------------------------------------------------------------------
    def test07_Client_getPeer_contextIsString(self):
        self.client = Client("testhost", 7677, "bindaddr", "ContextISString", 
                             "fakeconnector", "fakeproxy")
        host = self.client.getPeer()
        self.assertEquals(host._bwHack, 'SSL')
        self.assertEquals(host.host, 'testhost')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 7677)
    # -------------------------------------------------------------------------
    def test08_Client_getPeer_contextIsTrue(self):
        self.client = Client("testhost", 7677, "bindaddr", True,
                             "fakeconnector", "fakeproxy")
        host = self.client.getPeer()
        self.assertEquals(host._bwHack, 'SSL')
        self.assertEquals(host.host, 'testhost')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 7677)
    # -------------------------------------------------------------------------
    def test09_Client_connectDone_usesProxy(self):
        self.client = Client("testhost", 7677, "bindaddr", True,
                             "fakeconnector", "fakeproxy")
        self.client.proxy = ("proxy.example.org", 215)
        host = self.client._connectDone()
        self.assertEquals(self.client.connected, 1)
        self.assertEquals(self.client.logstr, 'ConnectProtocol,client')

        for ss in self.client.callCounts.keys():
            val = 0
            if ss == 'startReading' or ss == 'makeConnection': val = 1
            self.assertEquals(self.client.callCounts[ss], val)
    # -------------------------------------------------------------------------
    def test09_Client_connectDone_usesProxy(self):
        self.client = Client("testhost", 7677, "bindaddr", True,
                             "fakeconnector", "fakeproxy")
        self.client.proxy = ("proxy.example.org", 215)
        host = self.client._connectDone()
        self.assertEquals(self.client.connected, 1)
        self.assertEquals(self.client.logstr, 'ConnectProtocol,client')

        for ss in self.client.callCounts.keys():
            val = 0
            if ss == 'startReading' or ss == 'makeConnection': val = 1
            self.assertEquals(self.client.callCounts[ss], val)

        self.assertEquals(self.client.protocol.host, "proxy.example.org")
        self.assertEquals(self.client.protocol.port, 215)
    # -------------------------------------------------------------------------
    def test10_Client_connectDone_noProxy_noContextFactory(self):
        self.client = Client("testhost", 7677, "bindaddr", None,
                             "fakeconnector", "fakeproxy")
        self.client.proxy = None
        host = self.client._connectDone()

        self.assertEquals(self.client.connected, 0)
        self.assertEquals(self.client.logstr, 'Uninitialized')
        self.assertEquals(self.client.protocol, None)

        for ss in self.client.callCounts.keys():
            val = 0
            if ss == 'tcpConnectDone': val = 1
            self.assertEquals(self.client.callCounts[ss], val)
    # -------------------------------------------------------------------------
    def test11_Client_connectDone_noProxy_withContextFactory(self):
        self.client = Client("testhost", 7677, "bindaddr", "FakeContextFactory",
                             "fakeconnector", "fakeproxy")
        self.client.proxy = None
        host = self.client._connectDone()

        self.assertEquals(self.client.connected, 0)
        self.assertEquals(self.client.logstr, 'Uninitialized')
        self.assertEquals(self.client.protocol, None)

        for ss in self.client.callCounts.keys():
            val = 0
            if ss == 'tcpConnectDone' or ss == 'startTLS' or ss == 'startWriting':
               val = 1
            self.assertEquals(self.client.callCounts[ss], val)
# ----------------------------------------------------------------
class ConnectorTestCase(unittest.TestCase):
    def setUp(self):
        self.connector = None
        self.saveMethods = {}

        def sslConnectorInit(conSelf, host, port, factory, contextFactory, timeout, bindAddr, reactor):
            self.assertEquals(conSelf.proxy, None)
            self.assertEquals(conSelf.host, host)
            self.assertEquals(conSelf.port, port)
            conSelf.bindAddress = bindAddr
            conSelf.contextFactory = contextFactory
            conSelf.reactor = reactor

        def sslClientInit(clientSelf, host, port, bindAddress, contextFactory, connector, reactor):
            self.assertEquals(contextFactory, clientSelf.contextFactory)
            self.assertEquals(contextFactory, self.connector.contextFactory)
            self.assertEquals(bindAddress, self.connector.bindAddress)
            self.assertEquals(reactor, self.connector.reactor)
            self.assertEquals(host, self.connector.host)
            self.assertEquals(port, self.connector.port)

        self.saveMethods['sslClientInit'] = ssl.Client.__init__
        ssl.Client.__init__ = sslClientInit
        self.saveMethods['sslConnectorInit'] = ssl.Connector.__init__
        ssl.Connector.__init__ = sslConnectorInit
    # -------------------------------------------------------------------------
    def tearDown(self):
        ssl.Client.__init__ = self.saveMethods['sslClientInit']
        ssl.Connector.__init__ = self.saveMethods['sslConnectorInit']
    # -------------------------------------------------------------------------
    def test00_connector_init(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   None, None, None)
    # -------------------------------------------------------------------------
    def test01_connector_setProxyHost_noColon(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   None, None, None)
        self.assertEquals(self.connector.proxy, None)
        caughtIt = False
        try:
            self.connector.setProxyHost("proxy.example.org")
        except IndexError, ie:
            self.assertEquals(ie.__str__(), "list index out of range")
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught an IndexError")
    # -------------------------------------------------------------------------
    def test02_connector_setProxyHost_colonOnRight(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   None, None, None)
        self.assertEquals(self.connector.proxy, None)
        caughtIt = False
        try:
            self.connector.setProxyHost("proxy.example.org:")
        except ValueError, ve:
            self.assertEquals(ve.__str__(),
                              "invalid literal for int() with base 10: ''")
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught an ValueError")
    # -------------------------------------------------------------------------
    def test03_connector_setProxyHost_portIsNotInt(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   None, None, None)
        self.assertEquals(self.connector.proxy, None)
        caughtIt = False
        try:
            self.connector.setProxyHost("proxy.example.org:my22port22")
        except ValueError, ve:
            self.assertEquals(ve.__str__(),
                        "invalid literal for int() with base 10: 'my22port22'")
            caughtIt = True
        self.failUnless(caughtIt, "Should have caught an ValueError")
    # -------------------------------------------------------------------------
    def test04_connector_setProxyHost_colonOnLeft(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   None, None, None)
        self.assertEquals(self.connector.proxy, None)

        self.connector.setProxyHost(":555")

        self.assertEquals(self.connector.proxy, ('', 555))
    # -------------------------------------------------------------------------
    def test05_connector_setProxyHost_fullyValid(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   None, None, None)
        self.assertEquals(self.connector.proxy, None)

        self.connector.setProxyHost("myproxy.example.org:274")

        self.assertEquals(self.connector.proxy, ('myproxy.example.org', 274))
    # -------------------------------------------------------------------------
    def test06_connector_makeTransport(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   "conextFactoryDummy", None, 7634)
        client = self.connector._makeTransport()
        # Note: other checks in the setUp() init.
        self.assertEquals(client.contextFactory, "conextFactoryDummy")
    # -------------------------------------------------------------------------
    def test07_connector_getDestination_contextIsNone(self):
        self.connector = Connector("fake.example.org", 1233, None,
                                   None, None, 7634)

        host = self.connector.getDestination()
        self.assertEquals(host._bwHack, 'INET')
        self.assertEquals(host.host, 'fake.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 1233)
    # -------------------------------------------------------------------------
    def test08_connector_getDestination_contextIsFalse(self):
        self.connector = Connector("fake.example.org", 1234, None,
                                   False, None, 7634)
        host = self.connector.getDestination()
        self.assertEquals(host._bwHack, 'INET')
        self.assertEquals(host.host, 'fake.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 1234)
    # -------------------------------------------------------------------------
    def test09_connector_getDestination_contextIsString(self):
        self.connector = Connector("myfake.example.org", 1235, None,
                                   "conextFactoryDummy", None, 7634)
        host = self.connector.getDestination()
        self.assertEquals(host._bwHack, 'SSL')
        self.assertEquals(host.host, 'myfake.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 1235)
    # -------------------------------------------------------------------------
    def test10_connector_getDestination_contextIsTrue(self):
        self.connector = Connector("afake.example.org", 1400, None,
                                   True, None, 7634)
        host = self.connector.getDestination()
        self.assertEquals(host._bwHack, 'SSL')
        self.assertEquals(host.host, 'afake.example.org')
        self.assertEquals(host.type, 'TCP')
        self.assertEquals(host.port, 1400)
# ----------------------------------------------------------------
def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test_trynow"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(ProxyConnectProtocolTestCase))
    suite.addTest(loader.loadClass(ProxyClientTestCase))
    suite.addTest(loader.loadClass(ConnectorTestCase))
    return runner.TrialRunner(
        reporter.VerboseTextReporter,
#       reporter.TextReporter,
#	tracebackFormat='verbose',
        tracebackFormat='default',
        ).run(suite)

# ----------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)


# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-proxy.py ) ; ( cd ../tests ; make VERBOSE_T=-1 COVERAGE_FILES='../pokernetwork/proxy.py' TESTS='coverage-reset test-proxy.py coverage-report' check )"
# End:
