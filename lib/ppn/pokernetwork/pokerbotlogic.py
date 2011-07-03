#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
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
import sys
sys.path.insert(0, "..")

from os import popen
from string import rstrip
from random import randint

from twisted.internet import reactor

from pokerengine.pokertournament import *

from pokernetwork.user import checkName
from pokernetwork.pokerpackets import *
from pokernetwork.pokerclientpackets import *

LEVEL2ITERATIONS = {
    0: 10,
    1: 1000,
    2: 10000,
    3: 50000,
    4: 100000,
    5: 200000
    }

STATE_RUNNING = 0
STATE_RECONNECTING = 1
STATE_SEARCHING = 2
STATE_BATCH = 3

#
# If name generation is slow use /dev/urandom instead of
# /dev/random. apg will switch to /dev/urandom if it cannot
# open it for reading. chmod go-rw /dev/random will do this
# trick if not running the bots as root.
#

class Pool:

    def __init__(self, command):
        self.command = command
        self.pool = []
        self.max_tries = 5

    lines2pool = None
    
    def getLine(self):
        tries = 0
        while len(self.pool) == 0 and tries < self.max_tries:
            fd = popen(self.command)
            self.pool = self.lines2pool(fd.readlines())
            fd.close()
            tries += 1
        if tries >= self.max_tries:
            raise UserWarning, "pokerbotlogic:Pool too many failures running " + self.command
        return self.pool.pop()
    
class StringGenerator(Pool):

    def __init__(self, name_prefix):
        self.name_prefix = name_prefix
        Pool.__init__(self, "/usr/bin/apg -m 5 -x 10 -M ncl -q -n 500")

    def getName(self):
        return self.name_prefix + self.getLine()

    def lines2pool(self, lines):
        return filter(lambda string: checkName(string)[0], map(lambda string: string[:-1], lines))
    getPassword = Pool.getLine

class NoteGenerator(Pool):

    def lines2pool(self, lines):
        return map(lambda string: rstrip(string).split('\t'), lines)

    getNote = Pool.getLine
    
class PokerBot:

    note_generator = NoteGenerator("exit 1")
    
    def __init__(self, factory):
        self.factory = factory
        self.state = STATE_RUNNING
        self.batch_end_action = None

    def lookForGame(self, protocol):
            join_info = self.factory.join_info
            if join_info['tournament']:
                protocol.sendPacket(PacketPokerTourneySelect(string = join_info["name"]))
            else:
                protocol.sendPacket(PacketPokerTableSelect(string = join_info["name"]))
            self.state = STATE_SEARCHING
            self.factory.can_disconnect = True

    def bootstrap(self, protocol):
        user = protocol.user
        protocol.sendPacket(PacketPokerSetRole(roles = PacketPokerRoles.PLAY))
        protocol.sendPacket(PacketLogin(name = user.name,
                                        password = user.password))
        protocol.sendPacket(PacketPokerTableSelect(string = "my"))
        self.state = STATE_RECONNECTING
        
    def _handleConnection(self, protocol, packet):

        if packet.type == PACKET_BOOTSTRAP:
            reactor.callLater(self.factory.serial * 0.1, lambda: self.bootstrap(protocol))
            
        elif packet.type == PACKET_POKER_BATCH_MODE:
            self.state = STATE_BATCH
            
        elif packet.type == PACKET_SERIAL:
            if self.factory.cash_in:
                note = PokerBot.note_generator.getNote()
                if self.factory.currency_id:
                    note[0] += "?id=" + self.factory.currency_id
                protocol.sendPacket(PacketPokerCashIn(serial = packet.serial,
                                                      note = note))
            
        elif packet.type == PACKET_POKER_STREAM_MODE:
            self.state = STATE_RUNNING
            if self.batch_end_action:
                self.batch_end_action()
                self.batch_end_action = None
            
        elif packet.type == PACKET_POKER_TABLE_LIST:
            if self.state == STATE_SEARCHING:
                found = False
                table_info = self.factory.join_info
                for table in packet.packets:
                    if table.name == table_info["name"]:
                        found = True
                        protocol.sendPacket(PacketPokerTableJoin(game_id = table.id,
                                                                 serial = protocol.getSerial()))
                        if not self.factory.watch:
                            protocol.sendPacket(PacketPokerSeat(game_id = table.id,
                                                                serial = protocol.getSerial()))
                            protocol.sendPacket(PacketPokerBuyIn(game_id = table.id,
                                                                 serial = protocol.getSerial()))
                            protocol.sendPacket(PacketPokerAutoBlindAnte(game_id = table.id,
                                                                         serial = protocol.getSerial()))
                            protocol.sendPacket(PacketPokerSit(game_id = table.id,
                                                               serial = protocol.getSerial()))
                        break

                if not found:
                    print "Unable to find table %s " % table_info["name"]
                    protocol.transport.loseConnection()

            elif self.state == STATE_RECONNECTING:
                tables = packet.packets
                if len(tables) == 0:
                    self.lookForGame(protocol)
                elif len(tables) == 1:
                    table = tables[0]
                    protocol.sendPacket(PacketPokerTableJoin(game_id = table.id,
                                                             serial = protocol.getSerial()))
                    protocol.sendPacket(PacketPokerSit(game_id = table.id,
                                                       serial = protocol.getSerial()))
                    self.state = STATE_RUNNING
                else:
                    print "Unexpected number of tables %d " % len(tables)
                    protocol.transport.loseConnection()

            else:
                print "Unexpected state %d" % self.state
                protocol.transport.loseConnection()

        elif packet.type == PACKET_POKER_TOURNEY_LIST:
            name = self.factory.join_info['name']
            if len(packet.packets) <= 0:
                print "Unable to find tournament %s " % name
            found = None
            for tourney in packet.packets:
                if tourney.state == TOURNAMENT_STATE_REGISTERING:
                    found = tourney.serial
                    break
            if not found:
                print "No %s tournament allows registration, try later " % name
                self.factory.can_disconnect = False
                reactor.callLater(10, lambda: self.lookForGame(protocol))
            else:
                protocol.sendPacket(PacketPokerTourneyRegister(serial = protocol.getSerial(),
                                                               game_id = found))
            self.state = STATE_RUNNING
            
        elif packet.type == PACKET_POKER_SEAT:
            if packet.seat == -1:
                print "Not allowed to get a seat, give up"
                protocol.transport.loseConnection()

        elif packet.type == PACKET_POKER_ERROR or packet.type == PACKET_ERROR:
            giveup = True
            if packet.other_type == PACKET_POKER_TOURNEY_REGISTER:
                if packet.code == PacketPokerTourneyRegister.NOT_ENOUGH_MONEY:
                    self.factory.went_broke = True
                elif packet.code == PacketPokerTourneyRegister.ALREADY_REGISTERED:
                    giveup = False
                else:
                    name = self.factory.join_info['name']
                    print "Registration refused for tournament %s, try later" % name
                    self.factory.can_disconnect = False
                    reactor.callLater(60, lambda: self.lookForGame(protocol))
                    giveup = False
            elif packet.other_type == PACKET_POKER_REBUY or packet.other_type == PACKET_POKER_BUY_IN:
                self.factory.went_broke = True

            if self.factory.verbose or giveup: print "ERROR: %s" % packet
            if giveup:
                protocol.transport.loseConnection()
            
        elif packet.type == PACKET_POKER_BLIND_REQUEST:
            if packet.serial == protocol.getSerial():
                protocol.sendPacket(PacketPokerBlind(game_id = packet.game_id,
                                                     serial = packet.serial))

        elif packet.type == PACKET_POKER_PLAYER_LEAVE:
            if packet.serial == protocol.getSerial():
                if self.factory.join_info['tournament']:
                    self.lookForGame(protocol)

        elif packet.type == PACKET_POKER_WIN:
            if self.factory.rebuy and self.state == STATE_RUNNING:
                #
                # Rebuy if necessary
                #
                if not self.factory.join_info['tournament'] and not self.factory.watch:
                    game = self.factory.packet2game(packet)
                    serial = protocol.getSerial()
                    if ( game and game.isBroke(serial) ):
                        protocol.sendPacket(PacketPokerRebuy(game_id = game.id,
                                                             serial = serial))
                        protocol.sendPacket(PacketPokerSit(game_id = game.id,
                                                           serial = serial))
            
        elif packet.type == PACKET_POKER_SELF_IN_POSITION:
            game = self.factory.packet2game(packet)
            if self.state == STATE_RUNNING:
                self.inPosition(protocol, game)
            elif self.state == STATE_BATCH:
                self.batch_end_action = lambda: self.inPosition(protocol, game)

        elif packet.type == PACKET_POKER_SELF_LOST_POSITION:
            if self.state == STATE_BATCH:
                self.batch_end_action = None
                
    def inPosition(self, protocol, game):
        if not game.isBlindAnteRound():
            if self.factory.wait > 0:
                self.factory.can_disconnect = False
                reactor.callLater(self.factory.wait, lambda: self.play(protocol, game))
            else:
                self.play(protocol, game)

    def eval(self, game, serial):
        if self.factory.level == 0:
            actions = ("check", "call", "raise")
            return (actions[randint(0, 2)], -1)

        ev = game.handEV(serial, LEVEL2ITERATIONS[self.factory.level])
        
        if game.state == "pre-flop":
            if ev < 100:
                action = "check"
            elif ev < 500:
                action = "call"
            else:
                action = "raise"
        elif game.state == "flop" or game.state == "third":
            if ev < 200:
                action = "check"
            elif ev < 600:
                action = "call"
            else:
                action = "raise"
        elif game.state == "turn" or game.state == "fourth":
            if ev < 300:
                action = "check"
            elif ev < 700:
                action = "call"
            else:
                action = "raise"
        else:
            if ev < 400:
                action = "check"
            elif ev < 800:
                action = "call"
            else:
                action = "raise"
            
        return (action, ev)
        
    def play(self, protocol, game):
        serial = protocol.getSerial()
        name = protocol.getName()
        if serial not in game.serialsNotFold():
            print name + ": the server must have decided to play on our behalf before we had a chance to decide (TIMEOUT happening at the exact same time we reconnected), most likely"
            return
        
        (desired_action, ev) = self.eval(game, serial)
        actions = game.possibleActions(serial)
        if self.factory.verbose:
            print "%s serial = %d, hand = %s, board = %s" % (name, serial, game.getHandAsString(serial), game.getBoardAsString())
            print "%s wants to %s (ev = %d)" % (name, desired_action, ev)
        while not desired_action in actions:
            if desired_action == "check":
                desired_action = "fold"
            elif desired_action == "call":
                desired_action = "check"
            elif desired_action == "raise":
                desired_action = "call"

        if desired_action == "fold":
            protocol.sendPacket(PacketPokerFold(game_id = game.id,
                                                serial = serial))
        elif desired_action == "check":
            protocol.sendPacket(PacketPokerCheck(game_id = game.id,
                                                 serial = serial))
        elif desired_action == "call":
            protocol.sendPacket(PacketPokerCall(game_id = game.id,
                                                serial = serial))
        elif desired_action == "raise":
            (min_bet, max_bet, to_call) = game.betLimits(serial)
            
            player = game.serial2player[serial]
            raiseAmount = min_bet * 2

            raiseTo = min(max_bet, raiseAmount) + player.bet + to_call

            if raiseTo > (player.money + player.bet): raiseTo = (player.money + player.bet)

            protocol.sendPacket(PacketPokerRaise(game_id = game.id,
                                                 serial = serial,
                                                 amount = raiseTo))
        else:
            print "=> unexpected actions = %s" % actions
        self.factory.can_disconnect = True

