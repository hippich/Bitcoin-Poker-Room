#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2004, 2005, 2006 Mekensleep <licensing@mekensleep.com>
#                                24 rue vieille du temple, 75004 Paris
#       
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
#  Henry Precheur <henry@precheur.org> (2004)
#
import sys
sys.path.insert(0, "..")

from os import popen
from os.path import exists
from string import split, rstrip
from random import randint
from traceback import print_exc

from twisted.application import internet, service, app
from twisted.internet import pollreactor
if not sys.modules.has_key('twisted.internet.reactor'):
    print "installing poll reactor"
    pollreactor.install()
else:
    print "poll reactor already installed"
from twisted.internet import reactor
from twisted.python import components
from twisted.persisted import sob
from twisted.internet import error

from pokerengine.pokertournament import *

from pokernetwork import pokernetworkconfig
from pokernetwork.pokerclientpackets import *
from pokernetwork.pokerclient import PokerClientFactory, PokerClientProtocol
from pokernetwork.user import checkName
from pokernetwork.pokerbotlogic import StringGenerator, NoteGenerator, PokerBot

class PokerBotProtocol(PokerClientProtocol):

    def protocolEstablished(self):
        PokerClientProtocol.protocolEstablished(self)
        self.setPrefix(self.user.name + " ")
        if self.factory.disconnect_delay:
            delay = randint(*self.factory.disconnect_delay)
            print self.user.name + ": will disconnect in %d seconds (for kicks)" % delay
            reactor.callLater(delay, lambda: self.disconnectMyself(self.user.name))

    def disconnectMyself(self, name):
        if name == self.user.name:
            if self.factory.can_disconnect:
                self.factory.disconnected_volontarily = True
                print self.user.name + ": disconnecting (for kicks)"
                self.transport.loseConnection()
            else:
                delay = randint(*self.factory.disconnect_delay)
                print self.user.name + ": scheduled disconnection not allowed, will try again in %d seconds (for kicks)" % delay
                reactor.callLater(delay, lambda: self.disconnectMyself(self.user.name))
        
class PokerBotFactory(PokerClientFactory):

    string_generator = None

    def __init__(self, *args, **kwargs):
        PokerClientFactory.__init__(self, *args, **kwargs)
        self.protocol = PokerBotProtocol
        self.join_info = kwargs["join_info"]
        self.serial = kwargs["serial"]
        settings = kwargs["settings"]
        self.level = settings.headerGetInt("/settings/@level")
        self.reconnect = settings.headerGet("/settings/@reconnect") == "yes"
        self.rebuy = settings.headerGet("/settings/@rebuy") == "yes"
        self.watch = settings.headerGet("/settings/@watch") == "yes"
        self.cash_in = settings.headerGet("/settings/@cash_in") != "no"
        self.wait = settings.headerGetInt("/settings/@wait")
        self.disconnect_delay = settings.headerGet("/settings/@disconnect_delay")
        if self.disconnect_delay:
            self.disconnect_delay = tuple(map(lambda x: int(x), split(self.disconnect_delay, ",")))
        self.reconnect_delay = settings.headerGet("/settings/@reconnect_delay")
        if self.reconnect_delay:
            self.reconnect_delay = tuple(map(lambda x: int(x), split(self.reconnect_delay, ",")))
        self.currency = settings.headerGetInt("/settings/currency")
        self.currency_id = settings.headerGet("/settings/currency/@id")
        self.verbose = settings.headerGetInt("/settings/@verbose")
        self.bot = None
        self.went_broke = False
        self.disconnected_volontarily = False
        self.can_disconnect = True
        self.name = PokerBotFactory.string_generator.getName()
        self.password = PokerBotFactory.string_generator.getPassword()
        
    def buildProtocol(self, addr):
        protocol = PokerClientFactory.buildProtocol(self, addr)
        pokerbot = PokerBot(self)
        protocol._poll = False
        protocol.registerHandler(True, PACKET_BOOTSTRAP, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_ERROR, pokerbot._handleConnection)
        protocol.registerHandler('outbound', PACKET_SERIAL, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_BATCH_MODE, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_STREAM_MODE, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_ERROR, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_TABLE_LIST, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_TOURNEY_LIST, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_WIN, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_PLAYER_LEAVE, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_SEAT, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_BLIND_REQUEST, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_SELF_IN_POSITION, pokerbot._handleConnection)
        protocol.registerHandler(True, PACKET_POKER_SELF_LOST_POSITION, pokerbot._handleConnection)
        return protocol

    def clientConnectionFailed(self, connector, reason):
        print "Failed to establish connection to table %s" % self.join_info["name"]
        print reason
        self.bot.parent.removeService(self.bot)
        
    def clientConnectionLost(self, connector, reason):
        reconnect = False
        if self.reconnect:
            if self.went_broke:
                self.name = PokerBotFactory.string_generator.getName()
                print "Re-establishing (get more money)."
                self.went_broke = False
                reactor.callLater(self.wait, connector.connect)
            elif self.disconnected_volontarily:
                delay = randint(*self.reconnect_delay)
                print self.name + " Re-establishing in %d seconds." % delay
                self.disconnected_volontarily = False
                reactor.callLater(delay, connector.connect)
                reconnect = True
        else:
            print "The bot server connection to %s was closed" % self.join_info["name"]
            if not reason.check(error.ConnectionDone):
                print reason
        if not reconnect:
            self.bot.parent.removeService(self.bot)

class Bots(service.MultiService):

    def setSettings(self, settings):
        self.count = 0
        self.settings = settings
        self.verbose = settings.headerGetInt("/settings/@verbose")

    def addService(self, _service):
        service.MultiService.addService(self, _service)
        self.check()

    def removeService(self, _service):
        service.MultiService.removeService(self, _service)
        self.check()

    def check(self):
        if self.verbose > 1:
            print "%d bots currently active" % len(self.services)
        if len(self.services) <= 0 and reactor.running:
            reactor.callLater(0, reactor.stop)

def Application(name, uid=None, gid=None):
    """Return a compound class.

    Return an object supporting the C{IService}, C{IServiceCollection},
    C{IProcess} and C{sob.IPersistable} interfaces, with the given
    parameters. Always access the return value by explicit casting to
    one of the interfaces.
    """
    ret = components.Componentized()
    for comp in (Bots(), sob.Persistent(ret, name), service.Process(uid, gid)):
        ret.addComponent(comp, ignoreClass=1)
    service.IService(ret).setName(name)
    return ret

class Bot(internet.TCPClient):

    def stopService(self):
        #
        # If the connection is still available (i.e. the bots
        # were stopped because of a SIGINT signal), properly
        # close it before exiting.
        #
        if(hasattr(self._connection.transport, "protocol")):
            protocol = self._connection.transport.protocol
            #
            # If the connection fails, the transport exists but
            # the protocol is not set
            #
            if protocol:
                self._connection.transport.protocol.sendPacket(PacketQuit())
        return internet.TCPClient.stopService(self)

def makeApplication(argv):
    default_path = "/etc/poker-network" + sys.version[:3] + "/poker.bot.xml"
    if not exists(default_path):
        default_path = "/etc/poker-network/poker.bot.xml"
    configuration = sys.argv[-1][-4:] == ".xml" and sys.argv[-1] or default_path

    settings = pokernetworkconfig.Config([''])
    settings.load(configuration)

    PokerBotFactory.string_generator = StringGenerator(settings.headerGet("/settings/@name_prefix"))
    PokerBot.note_generator = NoteGenerator(settings.headerGet("/settings/currency"))

    ( host, port ) = split(settings.headerGet("/settings/servers"), ":")
    port = int(port)

    bots = Application('pokerbot')
    bots.verbose = settings.headerGetInt("/settings/@verbose")
    services = service.IServiceCollection(bots)
    services.setSettings(settings)

    bots_count = 0
    for table in settings.headerGetProperties("/settings/table"):
        for i in range(0, int(table["count"])):
            bots_count += 1
            table['tournament'] = False
            factory = PokerBotFactory(settings = settings,
                                      join_info = table,
                                      serial = bots_count)
            bot = Bot(host, port, factory)
            factory.bot = bot
            bot.setServiceParent(services)
    for tournament in settings.headerGetProperties("/settings/tournament"):
        for i in range(0, int(tournament["count"])):
            bots_count += 1
            tournament['tournament'] = True
            factory = PokerBotFactory(settings = settings,
                                      join_info = tournament,
                                      serial = bots_count)
            bot = Bot(host, port, factory)
            factory.bot = bot
            bot.setServiceParent(services)
    return bots

application = makeApplication(sys.argv[1:])

def run():
    app.startApplication(application, None)
    reactor.run()

if __name__ == '__main__':
    run()
