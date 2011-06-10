# -*- py-indent-offset: 4; coding: iso-8859-1; mode: python -*-
#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
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
#  Henry Precheur <henry@precheur.org> (2004)
#

from string import split, lower
from re import match
import platform

from twisted.internet import reactor, defer
from twisted.python.runtime import seconds

from pokereval import PokerEval
from pokerengine.pokergame import PokerGameClient, PokerPlayer, history2messages
from pokerengine.pokercards import PokerCards
from pokerengine.pokerchips import PokerChips

from pokerengine.pokerengineconfig import Config
from pokernetwork.client import UGAMEClientProtocol, UGAMEClientFactory
from pokernetwork.pokerclientpackets import *
from pokernetwork.pokergameclient import PokerNetworkGameClient
from pokernetwork.pokerexplain import PokerGames, PokerExplain

DEFAULT_PLAYER_USER_DATA = { 'delay': 0, 'timeout': None }

class PokerSkin:
    """Poker Skin"""

    def __init__(self, *args, **kwargs):
        self.settings = kwargs['settings']
        ( self.url, self.outfit ) = self.interpret("random", "random")

    def destroy(self):
        pass

    def interpret(self, url, outfit):
        return (url, outfit)
    
    def getUrl(self):
        return self.url

    def setUrl(self, url):
        self.url = url

    def getOutfit(self):
        return self.outfit

    def setOutfit(self, outfit):
        self.outfit = outfit

    def hideOutfitEditor(self):
        pass

    def showOutfitEditor(self, select_callback):
        pass

#
# Set a flag when an error is logged
#
from twisted.python import log

log.error_occurred = False
log_err = log.err

def err(*args, **kwargs):
    global log_err
    log_err(*args, **kwargs)
    log.error_occurred = True

log.err = err
log.deferr = err

class PokerClientFactory(UGAMEClientFactory):
    "client factory"

    def __init__(self, *args, **kwargs):
        UGAMEClientFactory.__init__(self, *args, **kwargs)
        self.settings = kwargs["settings"]
        self.config = kwargs.get("config", None)
        #
        # Make sure the attributes exists, should an exception occur before
        # it is initialized. This is done
        # so that the caller does not have to check the existence of the
        # attribute when catching an exception.
        #
        self.crashing = False

        settings = self.settings
        self.ping_delay = settings.headerGetInt("/settings/@ping")
        self.no_display_packets = settings.headerGet("/settings/@no_display_packets")
        self.name = settings.headerGet("/settings/name")
        self.password = settings.headerGet("/settings/passwd")
        if self.config:
            chips_values = self.config.headerGet("/sequence/chips")
            if not chips_values:
                raise UserWarning, "PokerClientFactory: no /sequence/chips found in %s" % self.config.path
            self.chips_values = map(int, chips_values.split())
        else:
            self.chips_values = [1]
        self.host = "unknown"
        self.port = 0
        self.remember = settings.headerGet("/settings/remember") == "yes"
        self.chat_config = settings.headerGetProperties("/settings/chat")
        if self.chat_config:
            self.chat_config = self.chat_config[0]
            for (key, value) in self.chat_config.iteritems():
                self.chat_config[key] = int(value)
        else:
            self.chat_config = {}
        self.dirs = split(self.settings.headerGet("/settings/path"))
        self.verbose = self.settings.headerGetInt("/settings/@verbose")
        self.delays = self.settings.headerGetProperties("/settings/delays")
        if self.delays:
            self.delays = self.delays[0]
            for (key, value) in self.delays.iteritems():
                self.delays[key] = float(value)
            if self.delays.has_key("round"):
                self.delays["end_round"] = self.delays["round"]
                self.delays["begin_round"] = self.delays["round"]
                del self.delays["round"]
            if not self.delays.has_key("blind_ante_position"):
                self.delays["blind_ante_position"] = self.delays["position"]
        else:
            self.delays = {}
        if self.verbose > 2:
            self.message("PokerClient: delays %s" % self.delays)
        self.delays_enable = self.settings.headerGet("/settings/@delays") == "true"
        self.skin = PokerSkin(settings = self.settings)
        self.protocol = PokerClientProtocol
        self.games = PokerGames(dirs = self.dirs, verbose = self.verbose)
        self.file2name = {}
        self.first_time = self.settings.headerGet("/settings/name") == "username"
        self.played_time = self.settings.headerGet("/settings/played_time")

    def __del__(self):
        if hasattr(self, "games"):
            del self.games

    def buildProtocol(self, addr):
        protocol = UGAMEClientFactory.buildProtocol(self, addr)
        protocol.explain.chips_values = self.chips_values
        protocol.explain.games = self.games
        protocol.explain.setVerbose(self.verbose)
        return protocol

    def resolve(self, url):
        return reactor.resolve(url,(1,1))

    def checkNetwork(self, url):
        d = self.resolve(url)
        d.addCallback(self.hostResolved).addErrback(self.hostNotResolved)
        return d
    
    def hostNotResolved(self, d):
        self.networkNotAvailable()
        
    def hostResolved(self, d):
        self.networkAvailable()

    def networkNotAvailable(self):
        pass #pragma: no cover
    
    def networkAvailable(self):
        pass #pragma: no cover
        
    def restart(self):
        reactor.disconnectAll()
        import sys
        import os
        argv = [ sys.executable ]
        argv.extend(sys.argv)
        os.execv(sys.executable, argv)

    def quit(self):
        #
        # !!! The order MATTERS here !!! the renderer must be notified last
        # otherwise leak detection won't be happy. Inverting the two
        # is not fatal and the data will be freed eventually. However,
        # debugging is made much harder because leak detection can't
        # check as much as it could.
        #        
        self.skin.destroy()

    def getSkin(self):
        return self.skin
    
    def getUrl(self):
        return self.skin.getUrl()

    def setUrl(self,url):
        return self.skin.setUrl(url)

    def getOutfit(self):
        return self.skin.getOutfit()
    
    def setOutfit(self,outfit):
        return self.skin.setOutfit(outfit)
    
    def translateFile2Name(self, file):
        if not self.file2name.has_key(file):
            config = Config(self.dirs)
            config.load("poker.%s.xml" % file)
            name = config.headerGet("/bet/description")
            if not name:
                name = config.headerGet("/poker/variant/@name")
                if not name:
                    self.error("*CRITICAL* can't find readable name for %s" % file)
                    name = file
            self.file2name[file] = name
        return self.file2name[file]

    def saveAuthToFile(self, name, password, remember):
        settings = self.settings
        self.name = name
        self.password = password
        self.remember = remember
        if remember:
            remember = "yes"
        else:
            remember = "no"
            name = ""
            password = ""
        settings.headerSet("/settings/remember", remember)
        settings.headerSet("/settings/name", name)
        settings.headerSet("/settings/passwd", password)
        settings.save()
        settings.headerSet("/settings/name", self.name)
        settings.headerSet("/settings/passwd", self.password)

    def isOutbound(self, packet):
        return ( packet.type == PACKET_ERROR or
                 packet.type == PACKET_MESSAGE or
                 packet.type == PACKET_POKER_HAND_LIST or
                 packet.type == PACKET_POKER_PLAYER_INFO or
                 packet.type == PACKET_POKER_USER_INFO or
                 packet.type == PACKET_POKER_HAND_HISTORY or
                 packet.type == PACKET_POKER_PLAYERS_LIST or
                 packet.type == PACKET_POKER_TOURNEY_PLAYERS_LIST or
                 packet.type == PACKET_POKER_TOURNEY_UNREGISTER or
                 packet.type == PACKET_POKER_TOURNEY_REGISTER )

    def isAlwaysHandled(self, packet):
        return ( packet.type == PACKET_POKER_PLAYER_CHIPS or
                 packet.type == PACKET_POKER_CHAT )
    
    def isConnectionLess(self, packet):
        return ( packet.type == PACKET_PROTOCOL_ERROR or
                 packet.type == PACKET_QUIT )

    def getGame(self, game_id):
        return self.games.getGame(game_id)

    def getGameByNameNoCase(self, name):
        return self.games.getGameByNameNoCase(name)
    
    def getOrCreateGame(self, game_id):
        return self.games.getOrCreateGame(game_id)

    def getGameIds(self):
        return self.games.getGameIds()
    
    def deleteGame(self, game_id):
        return self.games.deleteGame(game_id)

    def packet2game(self, packet):
        if not self.isOutbound(packet):
            return self.games.packet2game(packet)
        else:
            return False

    def gameExists(self, game_id):
        return self.games.gameExists(game_id)

ABSOLUTE_LAGMAX = 120
DEFAULT_LAGMAX = 15

class PokerClientProtocol(UGAMEClientProtocol):
    """Poker client"""

    def __init__(self):
        UGAMEClientProtocol.__init__(self)
        self.callbacks = {
            'current': {},
            'not_current': {},
            'outbound': {}
            }
        self.setCurrentGameId(None)
        self.pending_auth_request = False
        self.publish_packets = []
        self.input_packets = []
        self.publish_timer = None
        self.publish_time = 0
        self.publishPackets()
        self.lag = DEFAULT_LAGMAX
        self.lagmax_callbacks = []
        self.explain = PokerExplain()

    def setPrefix(self, prefix):
        self._prefix = prefix
        self.explain.setPrefix(prefix)
        
    def setCurrentGameId(self, game_id):
        if hasattr(self.factory, 'verbose') and self.factory.verbose > 2: self.message("setCurrentGameId(%s)" % game_id)
        self.hold(0)
        self.currentGameId = game_id

    def getCurrentGameId(self):
        return self.currentGameId
    
    def connectionMade(self):
        "connectionMade"
        if self.factory.delays_enable:
            self._lagmax = ABSOLUTE_LAGMAX
            self.lag = self.factory.delays.get("lag", DEFAULT_LAGMAX)
        self.no_display_packets = self.factory.no_display_packets
        UGAMEClientProtocol.connectionMade(self)

    def packetDeferred(self, what, name):
        d = defer.Deferred()
        def fire(client, packet):
            d.callback((client, packet))
        self.registerHandler(what, name, fire)
        def unregister(arg):
            self.unregisterHandler(what, name, fire)
            return  arg
        d.addCallback(unregister)
        return d
        
    def registerHandler(self, what, name, meth):
        if name:
            names = [ name ]
        else:
            names = PacketNames.keys()
        if what != True:
            whats = [ what ]
        else:
            whats = [ 'current', 'not_current', 'outbound' ]
        for what in whats:
            callbacks = self.callbacks[what]
            for name in names:
                callbacks.setdefault(name, []).append(meth)
        
    def unregisterHandler(self, what, name, meth):
        if name:
            names = [ name ]
        else:
            names = PacketNames.keys()
        if what != True:
            whats = [ what ]
        else:
            whats = [ 'current', 'not_current', 'outbound' ]
        for what in whats:
            callbacks = self.callbacks[what]
            for name in names:
                callbacks[name].remove(meth)
        
    def normalizeChips(self, game, chips):
        if game.unit in self.factory.chips_values:
            values = self.factory.chips_values[self.factory.chips_values.index(game.unit):]
        else:
            values = []
        list = PokerChips(values, chips).tolist()
        if self.factory.verbose > 4:
            self.message("normalizeChips: " + str(list) + " " + str(values))
        return list
            
    def updatePlayerChips(self, game, player):
        packet = PacketPokerPlayerChips(game_id = game.id,
                                        serial = player.serial,
                                        bet = player.bet,
                                        money = player.money)
        return packet

    def updatePotsChips(self, game, side_pots):
        packets = []
        
        if not side_pots:
            packet = PacketPokerChipsPotReset(game_id = game.id)
            return [ packet ]
        
        index = 0
        for (amount, total) in side_pots['pots']:
            chips = amount
            bet = self.normalizeChips(game, chips)
            pot = PacketPokerPotChips(game_id = game.id,
                                      index = index,
                                      bet = bet)
            packets.append(pot)
            index += 1
        return packets

    def chipsPlayer2Bet(self, game, player, chips):
        packets = []
        packet = PacketPokerChipsPlayer2Bet(game_id = game.id,
                                            serial = player.serial,
                                            chips = self.normalizeChips(game, chips))
        packets.append(packet)
        packets.append(self.updatePlayerChips(game, player))
        return packets

    def chipsBet2Pot(self, game, player, bet, pot_index):
        packets = []
        if ( pot_index == 0 and
             player.dead > 0 and
             game.isSecondRound() ):
            #
            # The ante or the dead are already in the pot
            #
            bet -= player.dead
        packet = PacketPokerChipsBet2Pot(game_id = game.id,
                                         serial = player.serial,
                                         chips = self.normalizeChips(game, bet),
                                         pot = pot_index)
        packets.append(packet)
        packets.append(self.updatePlayerChips(game, player))
        return packets
        
    def chipsPot2Player(self, game, player, bet, pot_index, reason):
        packet = PacketPokerChipsPot2Player(game_id = game.id,
                                            serial = player.serial,
                                            chips = self.normalizeChips(game, bet),
                                            pot = pot_index,
                                            reason = reason)
        return packet
        
    def handleUserInfo(self, packet):
        if self.factory.verbose > 2:
            self.message("handleUserInfo: " + str(packet))
        self.user_info = packet

    def handlePersonalInfo(self, packet):
        self.handleUserInfo(packet)
        self.personal_info = packet

    def handleSerial(self, packet):
        self.user.serial = packet.serial
        self.sendPacket(PacketPokerGetUserInfo(serial = packet.serial))

    def handlePlayerInfo(self, packet):
        skin = self.factory.getSkin()
        #
        # Check that the implementation of the outfit is still valid. If it
        # needs upgrade, send it back to the server.
        #
        ( url, outfit ) = skin.interpret(packet.url, packet.outfit)
        if url != packet.url or outfit != packet.outfit:
            ( url_check, outfit_check ) = self.factory.getSkin().interpret(url, outfit)
            #
            # Make sure that we wont loop indefinitely because of an instability of the interpret
            # function. In normal operation the url and outfit returned by interpret must be
            # returned as is when fed to interpret again. If the implementation of interpret
            # fails to implement this stability, don't enter a loop because sending PokerPlayerInfo
            # will return us a PokerPlayerInfo for confirmation of the success.
            #
            if url_check != url or outfit_check != outfit:
                self.error("*CRITICAL*: PACKET_POKER_PLAYER_INFO: may enter loop packet.url = %s\n url = %s\n url_check = %s\npacket.outfit = %s\n outfit = %s\n outfit_check = %s" % ( packet.url, url, url_check, packet.outfit, outfit, outfit_check ))
            else:
                packet.url = url
                packet.outfit = outfit
                self.sendPacket(packet)
        skin.setUrl(url)
        skin.setOutfit(outfit)

    def logout(self):
        self.sendPacket(PacketLogout())
        self.user.logout()

    def setPlayerDelay(self, game, serial, value):
        player = game.getPlayer(serial)
        if player == None:
            self.message("WARNING setPlayerDelay for a non-existing player %d" % serial)
        else:
            player.getUserData()['delay'] = seconds() + value

    def getPlayerDelay(self, game, serial):
        if not game: return 0
        player = game.getPlayer(serial)
        if not player: return 0
        user_data = player.getUserData()
        if not user_data or not user_data.has_key('delay'): return 0
        return user_data['delay']

    def canHandlePacket(self, packet):
        if not self.factory.isAlwaysHandled(packet) and hasattr(packet, "game_id") and hasattr(packet, "serial"):
            delay = self.getPlayerDelay(self.factory.packet2game(packet), packet.serial)
            if delay <= seconds():
                return ( True, 0 )
            else:
                return ( False, delay )
        else:
            return ( True, 0 )

    def resendPlayerTimeoutWarning(self, game):
        if game.isRunning() and game.getSerialInPosition() == self.getSerial():
            player = game.getPlayer(self.getSerial())
            if player.user_data['timeout']:
                ( when, timeout ) = player.user_data['timeout']
                now = seconds()
                timeout = timeout - ( now - when )
                if timeout > 0:
                    return ( PacketPokerTimeoutWarning(game_id = game.id,
                                                       serial = self.getSerial(),
                                                       timeout = int(timeout),
                                                       when = int(now) ), )
        return ()
        
    def setPlayerTimeout(self, game, packet):
        packet.timeout -= int(self.getLag())
        if packet.timeout > 0:
            packet.when = int(seconds())
            player = game.getPlayer(packet.serial)
            player.getUserData()['timeout'] = ( packet.when, packet.timeout )
            return True
        else:
            return False
        
    def unsetPlayerTimeout(self, game, serial):
        player = game.getPlayer(serial)
        player.getUserData()['timeout'] = None
    
    def postMuck(self, game, want_to_muck):
        if game:            
            packet_type = want_to_muck and PacketPokerMuckAccept or PacketPokerMuckDeny
            self.sendPacket(packet_type(game_id = game.id, 
                                        serial  = self.getSerial()) )
    
    def _handleConnection(self, packet):
        if self.factory.verbose > 3: self.message("PokerClientProtocol:handleConnection: %s" % packet )

        if packet.type == PACKET_POKER_TIMEOUT_WARNING:
            packet.timeout -= int(self.getLag())

        elif packet.type == PACKET_POKER_USER_INFO:
            self.handleUserInfo(packet)

        elif packet.type == PACKET_POKER_PERSONAL_INFO:
            self.handlePersonalInfo(packet)

        elif packet.type == PACKET_POKER_TABLE:
            self.setCurrentGameId(packet.id)

        elif packet.type == PACKET_SERIAL:
            self.handleSerial(packet)
            self.sendPacket(PacketPokerGetPlayerInfo())

        elif packet.type == PACKET_POKER_PLAYER_INFO:
            self.handlePlayerInfo(packet)

        game = self.factory.packet2game(packet)

        if game and packet.type == PACKET_POKER_TABLE_DESTROY:
            self.scheduleTableQuit(game)
            game = None

        #
        # It is possible to receive packets related to a game that we know nothing
        # about after quitting a table. When quitting a table the client deletes
        # all information related to the game without waiting confirmation from
        # the server. Therefore the server may keep sending packets related to
        # the game before noticing TABLE_QUIT packet.
        #
        if game:
            if packet.type == PACKET_POKER_SEAT:
                if packet.seat == -1:
                    self.error("This seat is busy")
                else:
                    if game.isTournament():
                        self.sendPacket(PacketPokerSit(serial = self.getSerial(),
                                                       game_id = game.id))

            elif packet.type == PACKET_POKER_MUCK_REQUEST:                
                if packet.game_id != self.getCurrentGameId():
                   self.postMuck(game, True)

        self.explain.explain(packet)

        if game:
            if packet.type == PACKET_POKER_PLAYER_ARRIVE:
                player = game.getPlayer(packet.serial)
                player.setUserData(DEFAULT_PLAYER_USER_DATA.copy())
        
        for forward_packet in self.explain.forward_packets:
            self.schedulePacket(forward_packet)
        self.explain.forward_packets = None

    def currentGames(self, exclude = None):
        games = self.factory.getGameIds()
        if exclude:
            games.remove(exclude)
        return PacketPokerCurrentGames(game_ids = games,
                                       count = len(games))
    
    def connectionLost(self, reason):
        if self.factory.crashing:
            self.message("connectionLost: crashing, just return.")
            return
        if self.factory.verbose:
            self.message("connectionLost: noticed, aborting all tables.")
        self.abortAllTables()
        UGAMEClientProtocol.connectionLost(self, reason)
        
    def abortAllTables(self):
        for game in self.factory.games.getAll():
            self.scheduleTableAbort(game)

    def scheduleTableAbort(self, game):
        game_id = game.id
        def thisgame(packet):
            return hasattr(packet, "game_id") and packet.game_id == game_id
        self.unschedulePackets(thisgame)
        self.discardPackets(game_id)
        self.scheduleTableQuit(game)

    def scheduleTableQuit(self, game):
        self.schedulePacket(PacketPokerBatchMode(game_id = game.id))
        for player in game.playersAll():
            packet = PacketPokerPlayerLeave(game_id = game.id,
                                            serial = player.serial,
                                            seat = player.seat)
            self.schedulePacket(packet)
        self.schedulePacket(PacketPokerStreamMode(game_id = game.id))
        self.schedulePacket(PacketPokerTableQuit(game_id = game.id,
                                                serial = self.getSerial()))
        self.schedulePacket(self.currentGames(game.id))
        self.publishAllPackets()

    def resendPackets(self, game_id):
        self.publishAllPackets()
        game = self.getGame(game_id)
        self.setCurrentGameId(game.id)
        packets = []
        packet = PacketPokerTable(id = game.id,
                                  name = game.name,
                                  variant = game.variant,
                                  seats = game.max_players,
                                  betting_structure = game.betting_structure,
                                  players = game.allCount(),
                                  # observers ?
                                  # waiting ?
                                  # player_timeout ?
                                  # muck_timeout ?
                                  hands_per_hour = game.stats["hands_per_hour"],                                  
                                  average_pot = game.stats["average_pot"],
                                  percent_flop = game.stats["percent_flop"],
                                  skin = game.level_skin
                                  )
        packets.append(PacketPokerBatchMode(game_id = game.id))
        packet.seats_all = game.seats_all
        packets.append(packet)
        packets.append(PacketPokerBuyInLimits(game_id = game.id,
                                              min = game.buyIn(self.getSerial()),
                                              max = game.maxBuyIn(self.getSerial()),
                                              best = game.bestBuyIn(self.getSerial()),
                                              rebuy_min = game.minMoney()))
        packets.append(PacketPokerDealer(game_id = game.id, dealer = game.dealer_seat))
        for player in game.playersAll():
            packets.append(PacketPokerPlayerArrive(game_id = game.id,
                                                   serial = player.serial,
                                                   name = player.name,
                                                   url = player.url,
                                                   outfit = player.outfit,
                                                   blind = player.blind,
                                                   remove_next_turn = player.remove_next_turn,
                                                   sit_out = player.sit_out,
                                                   sit_out_next_turn = player.sit_out_next_turn,
                                                   auto = player.auto,
                                                   auto_blind_ante = player.auto_blind_ante,
                                                   wait_for = player.wait_for,
                                                   seat = player.seat))
            # FIXME: Should a PokerPlayerStats() packet be sent here?
            if player.isSit():
                packets.append(PacketPokerSit(game_id = game.id,
                                              serial = player.serial))
            else:
                packets.append(PacketPokerSitOut(game_id = game.id,
                                                 serial = player.serial))
            packets.append(self.updatePlayerChips(game, player))
        packets.append(PacketPokerSeats(game_id = game.id,
                                        seats = game.seats()))
        packets.append(PacketPokerStart(game_id = game.id,
                                        hand_serial = game.hand_serial))
        if game.isRunning():
            players_with_cards = game.playersNotFold()
        elif  game.isGameEndInformationValid():
            players_with_cards = game.playersWinner()
        else:
            players_with_cards = []

        if players_with_cards:
            for player in players_with_cards:
                packet = PacketPokerPlayerCards(game_id = game.id,
                                                serial = player.serial,
                                                cards = player.hand.toRawList())
                packets.append(packet)
            packets.append(PacketPokerBoardCards(game_id = game.id,
                                                 cards = game.board.tolist(False)))
        if game.isRunning():
            if not self.no_display_packets:
                packets.extend(self.updatePotsChips(game, game.getPots()))
            packets.append(PacketPokerPosition(game_id = game.id,
                                               serial = game.getSerialInPosition()))
            if not self.no_display_packets:
                packets.extend(self.updateBetLimit(game))
        else:
            if not self.no_display_packets and game.isGameEndInformationValid():
                packets.extend(self.packetsShowdown(game))
                packets.append(PacketPokerShowdown(game_id = game.id, showdown_stack = game.showdown_stack))
        packets.append(PacketPokerStreamMode(game_id = game.id))
        packets.extend(self.resendPlayerTimeoutWarning(game))
        
        for packet in packets:
            self.schedulePacket(packet)

    def deleteGames(self):
        self.setCurrentGameId(None)
        for game_id in self.factory.getGameIds():
            self.deleteGame(game_id)
        
    def deleteGame(self, game_id):
        if self.factory.verbose > 2: self.message("deleteGame: %d" % game_id)
        self.factory.deleteGame(game_id)
        def thisgame(packet):
            return hasattr(packet, "game_id") and packet.game_id == game_id
        self.unschedulePackets(thisgame)
        self.discardPackets(game_id)

    def getGame(self, game_id):
        return self.factory.getGame(game_id)

    def sendPacket(self, packet):
        if packet.type == PACKET_POKER_TABLE_QUIT:
            self.scheduleTableAbort(self.getGame(packet.game_id))
        elif packet.type == PACKET_POKER_SIT_OUT:
            game = self.getGame(packet.game_id)
            if game:
                game.sitOutNextTurn(packet.serial)
            self.schedulePacket(PacketPokerSitOutNextTurn(game_id = packet.game_id,
                                                          serial = packet.serial))
        elif packet.type == PACKET_POKER_SIT:
            game = self.getGame(packet.game_id)
            if game:
                game.sitRequested(packet.serial)
            self.schedulePacket(PacketPokerSitRequest(game_id = packet.game_id,
                                                      serial = packet.serial))
        elif packet.type == PACKET_QUIT:
            self.ignoreIncomingData()
            self.abortAllTables()

        UGAMEClientProtocol.sendPacket(self, packet)

    def protocolEstablished(self):
        self.setPingDelay(self.factory.ping_delay)
        poll_frequency = self.factory.settings.headerGet("/settings/@poll_frequency")
        if poll_frequency:
            self._poll_frequency = float(poll_frequency)
        self.user.name = self.factory.name
        self.user.password = self.factory.password
        self._packet2id = self.packet2id
        self._packet2front = self.packet2front
        self.schedulePacket(PacketBootstrap())
        UGAMEClientProtocol.protocolEstablished(self)

    def packet2front(self, packet):
        if ( hasattr(packet, "game_id") and
             self.getGame(packet.game_id) ):
            if ( packet.type == PACKET_POKER_CHAT ):
                return True

            elif packet.type == PACKET_POKER_MESSAGE:
                return True

            elif ( packet.type == PACKET_POKER_PLAYER_ARRIVE and
                   packet.serial == self.getSerial() ):
                return True

        return False

    def registerLagmax(self, method):
        self.lagmax_callbacks.append(method)

    def unregisterLagmax(self, method):
        self.lagmax_callbacks.remove(method)
        
    def triggerLagmax(self, packet):
        for method in self.lagmax_callbacks:
            method(packet)
    
    def packet2id(self, packet):
        self.triggerLagmax(packet)
        if not self.factory.isOutbound(packet) and hasattr(packet, "game_id"):
            return packet.game_id
        elif packet.type == PACKET_POKER_TABLE:
            return packet.id
        else:
            return 0
        
    def protocolInvalid(self, server, client):
        self.schedulePacket(PacketProtocolError(message = "Upgrade the client from\nhttp://mekensleep.org/\nServer version is %s\nClient version is %s" % ( server, client ) ))
        self.publishAllPackets()
        UGAMEClientProtocol.protocolInvalid(self, server, client)

    def publishDelay(self, delay):
        if self.factory.verbose > 2: self.message("publishDelay: %f delay" % delay)
        publish_time = seconds() + delay
        if publish_time > self.publish_time:
            self.publish_time = publish_time
            
    def schedulePacket(self, packet):
        if not self.factory.isOutbound(packet) and hasattr(packet, "game_id") and not self.factory.gameExists(packet.game_id):
            return
        self.publish_packets.append(packet)
        if not self._poll:
            self.publishPacket()
        else:
            self.publishPacketTriggerTimer()
            
    def unschedulePackets(self, predicate):
        self.publish_packets = filter(lambda packet: not predicate(packet), self.publish_packets)
        if self._poll:
            self.publishPacketTriggerTimer()
        
    def publishPackets(self):
        if not self._poll:
            return

        delay = 0.01
        if len(self.publish_packets) > 0:
            #
            # If time has not come, make sure we are called at a later time
            # to reconsider the situation
            #
            wait_for = self.publish_time - seconds()
            if wait_for > 0:
                if self.factory.verbose > 2:
                    self.message("publishPackets: %f before next packet is sent" % wait_for)
                delay = wait_for
                self.block()
            else:
                self.publishPacket()
                if len(self.publish_packets) > 0:
                    self.block()
                else:
                    self.unblock()
        else:
            self.unblock()
            
        self.publishPacketTriggerTimer(delay)

    def publishPacketTriggerTimer(self, delay = 0.01):
        if not self.publish_timer or not self.publish_timer.active():
            if len(self.publish_packets) > 0:
                self.publish_timer = reactor.callLater(delay, self.publishPackets)

    def publishPacket(self):
        packet = self.publish_packets[0]
        if not self.established and not self.factory.isConnectionLess(packet):
            if self.factory.verbose > 5:
                self.message("publishPacket: skip because connection not established")
            return
        self.publish_packets.pop(0)
        what = 'outbound'
        if hasattr(packet, "game_id"):
            if self.factory.isOutbound(packet):
                what = 'outbound'
            else:
                if packet.game_id == self.getCurrentGameId():
                    what = 'current'
                else:
                    what = 'not_current'
        elif ( packet.type == PACKET_POKER_TABLE or
               packet.type == PACKET_POKER_TABLE_QUIT ):
            what = 'current'
        else:
            what = 'outbound'

        if self.factory.verbose > 2: self.message("publishPacket(%d): %s: %s" % ( self.getSerial(), what, packet ) )
        if self.callbacks[what].has_key(packet.type):
            callbacks = self.callbacks[what][packet.type]
            for callback in callbacks:
                callback(self, packet)
        
    def publishAllPackets(self):
        while len(self.publish_packets) > 0:
            self.publishPacket()
