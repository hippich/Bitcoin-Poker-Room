# -*- py-indent-offset: 4; coding: iso-8859-1; mode: python -*-
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
from string import lower

from twisted.python.runtime import seconds

from pokerengine.pokerchips import PokerChips
from pokerengine.pokergame import history2messages

from pokernetwork.pokergameclient import PokerNetworkGameClient
from pokernetwork.pokerpackets import *
from pokernetwork.pokerclientpackets import *

DEFAULT_PLAYER_USER_DATA = { 'timeout': None }

class PokerGames:

    def __init__(self, **kwargs):
        self.games = {}
        self.dirs = kwargs.get("dirs", [])
        self.verbose = kwargs.get("verbose", 0)
        self.prefix = kwargs.get("prefix", "")
    
    def getGame(self, game_id):
        if not hasattr(self, "games") or not self.games.has_key(game_id):
            return False
        else:
            return self.games[game_id]

    def getGameByNameNoCase(self, name):
        name = lower(name)
        for (serial, game) in self.games.iteritems():
            if lower(game.name) == name:
                return game
        return None
    
    def getOrCreateGame(self, game_id):
        if not self.games.has_key(game_id):
            game = PokerNetworkGameClient("poker.%s.xml", self.dirs)
            game.prefix = self.prefix
            game.verbose = self.verbose
            game.id = game_id
            self.games[game_id] = game

        return self.games[game_id]

    def getGameIds(self):
        return self.games.keys()
    
    def deleteGame(self, game_id):
        del self.games[game_id]

    def packet2game(self, packet):
        if hasattr(packet, "game_id") and self.games.has_key(packet.game_id):
            return self.games[packet.game_id]
        else:
            return False

    def gameExists(self, game_id):
        return self.games.has_key(game_id)

    def getAll(self):
        return self.games.values()

class ListHintSubset(Exception):
    pass

class PokerExplain:
    """Expand poker packets for the caller when they know nothing about poker """

    def __init__(self, *args, **kwargs):
        self.serial = 0
        self.no_display_packets = False
        self.pending_auth_request = False
        self.forward_packets = []
        self.chips_values = [1, 2, 5, 10, 20, 25, 50, 100, 200, 500, 1000, 2000, 2500, 5000, 10000, 25000, 50000, 100000, 200000, 500000, 1000000, 2000000, 5000000, 10000000]
        self._prefix = ""
        self.games = PokerGames(**kwargs)
        self.setVerbose(kwargs.get('verbose', 0))
        self.what = kwargs.get("explain", PacketPokerExplain.ALL)

    def error(self, string):
        self.message("ERROR " + string)
        
    def message(self, string):
        print self._prefix + string
        
    def setPrefix(self, prefix):
        self._prefix = prefix
        self.games.prefix = prefix

    def setVerbose(self, verbose):
        self.verbose = verbose
        self.games.verbose = verbose
        for game in self.games.getAll():
            game.verbose = verbose

    def normalizeChips(self, game, chips):
        if game.unit in self.chips_values:
            values = self.chips_values[self.chips_values.index(game.unit):]
        else:
            values = []
        list = PokerChips(values, chips).tolist()
        if self.verbose > 4: self.message("normalizeChips: " + str(list) + " " + str(values))
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

            if chips == 0:
                chips = game.getPotAmount()

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
        if self.what & PacketPokerExplain.CHIPSTACKS:
            packets.append(self.explainPlayerChips(game, player))
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
        if self.what & PacketPokerExplain.CHIPSTACKS:
            packets.append(self.explainPlayerChips(game, player))
        return packets
        
    def chipsPot2Player(self, game, player, bet, pot_index, reason):
        packet = PacketPokerChipsPot2Player(game_id = game.id,
                                            serial = player.serial,
                                            chips = self.normalizeChips(game, bet),
                                            pot = pot_index,
                                            reason = reason)
        return packet
        
    def gameEvent(self, game_id, type, *args):
        if self.verbose > 4:
            self.message("gameEvent: game_id = %d, type = %s, args = %s" % ( game_id, type, str(args) ))

        forward_packets = self.forward_packets
        if not forward_packets:
            if self.verbose > 3:
                self.message("gameEvent: called outside _handleConnection for game %d, ignored" % game_id)
            return False

        game = self.games.getGame(game_id)
        if not game:
            if self.verbose > 3:
                self.message("gameEvent: called for unknown game %d, ignored" % game_id)
            return False

        if type == "end_round":
            forward_packets.append(PacketPokerEndRound(game_id = game_id))

        elif type == "end_round_last":
            forward_packets.append(PacketPokerEndRoundLast(game_id = game_id))

        elif type == "money2bet":
            ( serial, amount ) = args
            player = game.getPlayer(serial)
            last_action = game.historyGet()[-1][0]
            if ( last_action == "raise" or last_action == "call" ) :
                if not self.no_display_packets:
                    forward_packets.extend(self.updateBetLimit(game))
                if last_action == "raise":
                    forward_packets.append(PacketPokerHighestBetIncrease(game_id = game.id))
            if not self.no_display_packets:
                forward_packets.extend(self.chipsPlayer2Bet(game, player, amount))

        elif type == "bet2pot":
            ( serial, amount ) = args
            if not self.no_display_packets and game.isBlindAnteRound():
                player = game.getPlayer(serial)
                forward_packets.extend(self.chipsBet2Pot(game, player, amount, 0))

        elif type == "round_cap_decrease":
            if not self.no_display_packets:
                forward_packets.extend(self.updateBetLimit(game))

        elif type == "position":
            if game.inGameCount() < 2:
                forward_packets.append(PacketPokerAllinShowdown(game_id = game.id))
                
        return True

    def handleSerial(self, packet):
        self.serial = packet.serial
        if self._prefix == '':
            self.setPrefix('[%i]' % packet.serial)

    def getSerial(self):
        return self.serial

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
    
    def explain(self, packet):
        if self.verbose > 3: self.message("PokerExplain:explain: %s" % packet )
        
        self.forward_packets = [ packet ]
        forward_packets = self.forward_packets
        
        if packet.type == PACKET_POKER_TABLE:
            if packet.id == 0:
                self.error("Too many open tables")
            else:
                if self.games.getGame(packet.id):
                    self.games.deleteGame(packet.id)
                new_game = self.games.getOrCreateGame(packet.id)
                new_game.prefix = self._prefix
                new_game.name = packet.name
                new_game.setTime(0)
                new_game.setVariant(packet.variant)
                new_game.setBettingStructure(packet.betting_structure)
                new_game.setMaxPlayers(packet.seats)
                new_game.registerCallback(self.gameEvent)
                new_game.level_skin = packet.skin
                new_game.currency_serial = packet.currency_serial
                new_game.history_index = 0
                self.updatePotsChips(new_game, [])
                new_game.position_info = [ 0, 0 ]
                self.forward_packets.append(self.currentGames())

        elif packet.type == PACKET_SERIAL:
            self.handleSerial(packet)

        elif packet.type == PACKET_ERROR:
            self.error("Server reported error : %s" % packet)
            return False

        game = self.games.packet2game(packet)

        if game and packet.type == PACKET_POKER_TABLE_DESTROY:
            game = None

        if game:
            if packet.type == PACKET_POKER_START:
                if packet.hand_serial == 0:
                    self.error("game start was refused")
                    forward_packets.remove(packet)
                elif not game.isEndOrNull():
                    raise UserWarning, "you should not be here (state: %s)" % game.state
                else:
                    game.history_index = 0
                    game.setTime(packet.time)
                    game.setHandsCount(packet.hands_count)
                    game.setLevel(packet.level)
                    game.beginTurn(packet.hand_serial)
                    game.position_info[PokerNetworkGameClient.POSITION_OBSOLETE] = True
                    if not self.no_display_packets:
                        forward_packets.append(PacketPokerBoardCards(game_id = game.id, serial = self.getSerial()))
                        for serial in game.player_list:
                            forward_packets.append(self.updatePlayerChips(game, game.serial2player[serial]))
                            if self.what & PacketPokerExplain.CHIPSTACKS:
                                forward_packets.append(self.explainPlayerChips(game, game.serial2player[serial]))
                        forward_packets.extend(self.updatePotsChips(game, []))

            elif packet.type == PACKET_POKER_CANCELED:
                if not self.no_display_packets and packet.amount > 0:
                    player = game.getPlayer(packet.serial)
                    if player.bet > 0:
                        forward_packets.extend(self.chipsBet2Pot(game, player, player.bet, 0))
                    if packet.amount > 0:
                        forward_packets.append(self.chipsPot2Player(game, player, packet.amount, 0, "canceled"))
                game.canceled(packet.serial, packet.amount)
                forward_packets.append(PacketPokerPosition(game_id = game.id))

            elif packet.type == PACKET_POKER_PLAYER_ARRIVE:
                game.addPlayer(packet.serial, packet.seat)
                player = game.getPlayer(packet.serial)
                player.setUserData(DEFAULT_PLAYER_USER_DATA.copy())
                player.name = packet.name
                player.url = packet.url
                player.outfit = packet.outfit
                player.auto_blind_ante = packet.auto_blind_ante
                player.wait_for = packet.wait_for
                player.auto = packet.auto
                if not self.no_display_packets:
                    self.forward_packets.append(PacketPokerSeats(game_id = game.id,
                                                                 seats = game.seats()))

            elif ( packet.type == PACKET_POKER_PLAYER_LEAVE or
                   packet.type == PACKET_POKER_TABLE_MOVE ) :
                game.removePlayer(packet.serial)
                if packet.serial == self.getSerial():
                    self.games.deleteGame(game.id)
                if packet.type == PACKET_POKER_TABLE_MOVE:
                    forward_packets.append(PacketPokerPlayerLeave(game_id = packet.game_id,
                                                                  serial = packet.serial,
                                                                  seat = packet.seat))
                if not self.no_display_packets:
                    self.forward_packets.append(PacketPokerSeats(game_id = game.id,
                                                                 seats = game.seats()))

            elif packet.type == PACKET_POKER_PLAYER_SELF:
                ( serial_in_position, position_is_obsolete ) = game.position_info
                if serial_in_position == self.getSerial():
                    game.position_info = [ 0, True ]
                forward_packets.extend(self.updateBetLimit(game))

            elif packet.type == PACKET_POKER_POSITION:
                if game.isBlindAnteRound():
                    game.setPosition(packet.position)
                forward_packets.remove(packet)

            elif packet.type == PACKET_POKER_SEATS:
                forward_packets.remove(packet)

            elif packet.type == PACKET_POKER_PLAYER_CARDS:
                player = game.getPlayer(packet.serial)
                player.hand.set(packet.cards)

            elif packet.type == PACKET_POKER_BOARD_CARDS:
                game.board.set(packet.cards)

            elif packet.type == PACKET_POKER_DEALER:
                game.setDealer(packet.dealer)

            elif packet.type == PACKET_POKER_SIT_OUT:
                game.sitOut(packet.serial)

            elif packet.type == PACKET_POKER_AUTO_FOLD:
                game.autoPlayer(packet.serial)

            elif packet.type == PACKET_POKER_AUTO_BLIND_ANTE:
                game.autoBlindAnte(packet.serial)

            elif packet.type == PACKET_POKER_NOAUTO_BLIND_ANTE:
                game.noAutoBlindAnte(packet.serial)

            elif packet.type == PACKET_POKER_MUCK_REQUEST:                
                game.setMuckableSerials(packet.muckable_serials)
                
            elif packet.type == PACKET_POKER_SIT:
                game.sit(packet.serial)

            elif packet.type == PACKET_POKER_TIMEOUT_WARNING:
                if not self.setPlayerTimeout(game, packet):
                    forward_packets.remove(packet)
            
            elif packet.type == PACKET_POKER_TIMEOUT_NOTICE:
                self.unsetPlayerTimeout(game, packet.serial)

            elif packet.type == PACKET_POKER_WAIT_FOR:
                game.getPlayer(packet.serial).wait_for = packet.reason
                forward_packets.remove(packet)

            elif packet.type == PACKET_POKER_IN_GAME:
                game.setStaticPlayerList(packet.players)
                for serial in game.serialsAll():
                    player = game.getPlayer(serial)
                    wait_for = player.wait_for
                    in_game = serial in packet.players 
                    if in_game or wait_for:
                        auto = player.isAuto()
                        if not game.isSit(serial):
                            game.sit(serial)
                            forward_packets.append(PacketPokerSit(game_id = game.id,
                                                                  serial = serial))
                        if auto:
                            game.autoPlayer(serial)
                            forward_packets.append(PacketPokerAutoFold(game_id = game.id,
                                                                       serial = player.serial))

                        if wait_for:
                            if wait_for == True and not in_game and not game.isRunning():
                                #
                                # A player is waiting for the blind (big, late...)
                                # and the server says it will not participate to the
                                # blindAnte round. This only happens when the anteRound
                                # is already finished on the server (i.e. when connecting
                                # to a table in the middle of a game). 
                                #
                                player.wait_for = "first_round"
                            else:
                                player.wait_for = wait_for
                            forward_packets.append(PacketPokerWaitFor(game_id = game.id,
                                                                      serial = serial,
                                                                      reason = wait_for))
                    else:
                        if game.isSit(serial):
                            game.sitOut(serial)                            
                            forward_packets.append(PacketPokerSitOut(game_id = game.id,
                                                                     serial = serial))

            elif packet.type == PACKET_POKER_RAKE:
                game.setRakedAmount(packet.value)
                
            elif packet.type == PACKET_POKER_WIN:
                if not self.no_display_packets:
                    for serial in packet.serials:
                        forward_packets.append(PacketPokerPlayerWin(serial = serial, game_id = game.id))

                if game.winners:
                    #
                    # If we know the winners before an explicit call to the distributeMoney
                    # method, it means that there is no showdown.
                    #
                    if not self.no_display_packets:
                        if game.isGameEndInformationValid():
                            forward_packets.append(PacketPokerShowdown(game_id = game.id, showdown_stack = game.showdown_stack))
                        forward_packets.extend(self.packetsPot2Player(game))
                else:
                    game.distributeMoney()

                    winners = game.winners[:]
                    winners.sort()
                    packet.serials.sort()
                    if winners != packet.serials:
                        raise UserWarning, "game.winners %s != packet.serials %s" % (winners, packet.serials)
                    if not self.no_display_packets:
                        if game.isGameEndInformationValid():
                            forward_packets.extend(self.packetsShowdown(game))
                            forward_packets.append(PacketPokerShowdown(game_id = game.id, showdown_stack = game.showdown_stack))

                        forward_packets.extend(self.packetsPot2Player(game))
                    game.endTurn()
                forward_packets.append(PacketPokerPosition(game_id = game.id))

            elif packet.type == PACKET_POKER_REBUY:
                forward_packets.remove(packet)
                if game.rebuy(packet.serial, packet.amount):
                    #
                    # If the server says the player rebuys, assume he knows
                    # that the player can rightfully do so and therefore
                    # that the buy_in has already been paid. The client fail
                    # to notice that a player already paid the buy_in 
                    # when it connects to a table on which said player has
                    # no chips in front of him.
                    #
                    player = game.getPlayer(packet.serial)
                    player.buy_in_payed = True
                    forward_packets.append(self.updatePlayerChips(game, player))
                    if self.what & PacketPokerExplain.CHIPSTACKS:
                        forward_packets.append(self.explainPlayerChips(game, player))

            elif packet.type == PACKET_POKER_PLAYER_CHIPS:
                player = game.getPlayer(packet.serial)
                if player.buy_in_payed:
                    if player.bet != packet.bet:
                        if self.verbose > 1:
                            self.error("server says player %d has a bet of %d chips and client thinks it has %d" % ( packet.serial, packet.bet, player.bet))
                        player.bet = packet.bet
                    if player.money != packet.money:
                        if self.verbose > 1:
                            self.error("server says player %d has a money of %d chips and client thinks it has %d" % ( packet.serial, packet.money, player.money))
                        player.money = packet.money
                else:
                    #
                    # If server sends chips amount for a player that did not yet pay the buy in
                    # 
                    player.bet = packet.bet
                    player.money = packet.money
                    if player.money > 0:
                        player.buy_in_payed = True
                if self.what & PacketPokerExplain.CHIPSTACKS:
                    forward_packets.append(self.explainPlayerChips(game, player))

            elif packet.type == PACKET_POKER_FOLD:
                game.fold(packet.serial)
                if game.isSitOut(packet.serial):
                    forward_packets.append(PacketPokerSitOut(game_id = game.id,
                                                             serial = packet.serial))

            elif packet.type == PACKET_POKER_CALL:
                game.call(packet.serial)

            elif packet.type == PACKET_POKER_RAISE:
                game.callNraise(packet.serial, packet.amount)

            elif packet.type == PACKET_POKER_CHECK:
                game.check(packet.serial)

            elif packet.type == PACKET_POKER_BLIND:
                game.blind(packet.serial, packet.amount, packet.dead)

            elif packet.type == PACKET_POKER_BLIND_REQUEST:
                game.setPlayerBlind(packet.serial, packet.state)

            elif packet.type == PACKET_POKER_ANTE:
                game.ante(packet.serial, packet.amount)

            elif packet.type == PACKET_POKER_STATE:
                game.position_info[PokerNetworkGameClient.POSITION_OBSOLETE] = True

                if game.isBlindAnteRound():
                    game.blindAnteRoundEnd()
                    forward_packets.extend(self.updatePotsChips(game, game.getPots()))

                if packet.string == "end" and game.state != "null":
                    game.endState()

                #
                # A state change is received at the begining of each
                # betting round. No state change is received when
                # reaching showdown or otherwise terminating the hand.
                #
                if game.isFirstRound():
                    game.initRound()
                else:
                    if not self.no_display_packets:
                        if ( packet.string == "end" and
                             game.isSingleUncalledBet(game.side_pots) ):
                            forward_packets.extend(self.moveBet2Player(game))
                        else:
                            forward_packets.extend(self.moveBet2Pot(game))

                    if packet.string != "end":
                        game.initRound()

                if not self.no_display_packets:
                    if game.isRunning() and game.cardsDealt() and game.downCardsDealtThisRoundCount() > 0:
                        forward_packets.append(PacketPokerDealCards(game_id = game.id,
                                                                    numberOfCards = game.downCardsDealtThisRoundCount(),
                                                                    serials = game.serialsNotFold()))

                if game.isRunning() and game.cardsDealt() and game.cardsDealtThisRoundCount() :
                    for player in game.playersNotFold():
                        cards = player.hand.toRawList()
                        forward_packets.append(PacketPokerPlayerCards(game_id = game.id,
                                                                      serial = player.serial,
                                                                      cards = cards))

                if not self.no_display_packets:
                    if game.isRunning() and game.cardsDealt() and self.getSerial() != 0 and game.isPlaying(self.getSerial()) and (packet.string == "flop" or packet.string == "turn" or packet.string == "river"):
                        forward_packets.append(PacketPokerPlayerHandStrength(game_id = game.id,
                                                                             serial = self.getSerial(),
                                                                             hand = game.readablePlayerBestHands(self.getSerial())))

                if ( packet.string != "end" and not game.isBlindAnteRound() ):
                    if not self.no_display_packets:
                        forward_packets.extend(self.updateBetLimit(game))
                    forward_packets.append(PacketPokerBeginRound(game_id = game.id))

                if game.state != packet.string:
                    self.error("state = %s, expected %s instead " % ( game.state, packet.string ))


            ( serial_in_position, position_is_obsolete ) = game.position_info
            if game.isRunning():
                #
                # Build position related packets
                #
                position_changed = serial_in_position != game.getSerialInPosition()
                if position_is_obsolete or position_changed:
                    self_was_in_position = self.getSerial() != 0 and serial_in_position == self.getSerial()
                    serial_in_position = game.getSerialInPosition()
                    self_in_position = serial_in_position == self.getSerial()
                    if serial_in_position > 0:
                        if position_changed:
                            forward_packets.append(PacketPokerPosition(game_id = game.id,
                                                                       position = game.position,
                                                                       serial = serial_in_position))
                        if ( self_was_in_position and not self_in_position ):
                            self.unsetPlayerTimeout(game, self.getSerial())
                            if not game.isBlindAnteRound() or not game.getPlayer(self.getSerial()).isAutoBlindAnte():
                                forward_packets.append(PacketPokerSelfLostPosition(game_id = game.id,
                                                                                   serial = serial_in_position))
                        if ( ( not self_was_in_position or position_is_obsolete ) and self_in_position ):
                            if not game.isBlindAnteRound() or not game.getPlayer(self.getSerial()).isAutoBlindAnte():
                                forward_packets.append(PacketPokerSelfInPosition(game_id = game.id,
                                                                                 serial = serial_in_position))
                    elif self_was_in_position:
                        self.unsetPlayerTimeout(game, self.getSerial())
                        if not game.isBlindAnteRound() or not game.getPlayer(self.getSerial()).isAutoBlindAnte():
                            forward_packets.append(PacketPokerSelfLostPosition(game_id = game.id,
                                                                               serial = self.getSerial()))
            else:
                if serial_in_position > 0:
                    if not game.isBlindAnteRound() or not game.getPlayer(self.getSerial()).isAutoBlindAnte():
                        forward_packets.append(PacketPokerSelfLostPosition(game_id = game.id,
                                                                           serial = self.getSerial()))
                    serial_in_position = 0
            position_is_obsolete = False
            game.position_info = [ serial_in_position, position_is_obsolete ]
            #
            # Build dealer messages
            # Skip state = end because information is missing and will be received by the next packet (WIN)
            #
            if not ( packet.type == PACKET_POKER_STATE and packet.string == "end" ):
                (subject, messages) = history2messages(game, game.historyGet()[game.history_index:], serial2name = lambda serial: self.serial2name(game, serial))
                if messages or subject:
                    if messages:
                        message = "".join(map(lambda line: "Dealer: " + line + "\n", list(set(messages))))
                        forward_packets.append(PacketPokerChat(game_id = game.id,
                                                               message = message))
                game.history_index = len(game.historyGet())

        return True

    def serial2name(self, game, serial):
        player = game.getPlayer(serial)
        if player:
            return player.name
        else:
            if self.verbose >= 0:
                self.error("no player found for serial %d in game %d" % ( serial, game.id ))
            return "<unknown>"

    def moveBet2Pot(self, game):
        packets = []
        round_contributions = game.getLatestPotContributions()
        for (pot_index, pot_contribution) in round_contributions.iteritems():
            for (serial, amount) in pot_contribution.iteritems():
                player = game.getPlayer(serial)
                packets.extend(self.chipsBet2Pot(game, player, amount, pot_index))

        packets.extend(self.updatePotsChips(game, game.getPots()))
        return packets

    #
    # Should be move all bets back to players (for uncalled bets)
    # This is a border case we don't want to handle right now
    #
    moveBet2Player = moveBet2Pot
        
    def updateBetLimit(self, game):
        if ( self.getSerial() not in game.serialsPlaying() or
             game.isBlindAnteRound() ):
            return []
            
        packets = []
        serial = self.getSerial()
        (min_bet, max_bet, to_call) = game.betLimits(serial)
        found = None
        steps = self.chips_values[:]
        steps.reverse()
        #
        # Search for the lowest chip value by which all amounts can be divided
        #
        for step in steps:
            if min_bet % step == 0 and max_bet % step == 0 and to_call % step == 0:
                found = step
        if found:
            if self.verbose:
                self.message(" => bet min=%d, max=%d, step=%d, to_call=%d" % ( min_bet, max_bet, found, to_call))
            player = game.getPlayer(serial)
            bet = player.bet
            packets.append(PacketPokerBetLimit(game_id = game.id,
                                               min = min_bet + bet + to_call,
                                               max = max_bet + bet,
                                               step = game.getChipUnit(),
                                               call = to_call,
                                               allin = player.money + bet,
                                               pot = game.potAndBetsAmount() + to_call * 2))
        else:
            self.error("no chip value (%s) is suitable to step from min_bet = %d to max_bet = %d" % ( self.chips_values, min_bet, max_bet ))
        return packets

    def currentGames(self, exclude = None):
        games = self.games.getGameIds()
        if exclude:
            games.remove(exclude)
        return PacketPokerCurrentGames(game_ids = games,
                                       count = len(games))

    def explainPlayerChips(self, game, player):
        packet = PacketPokerClientPlayerChips(game_id = game.id,
                                              serial = player.serial,
                                              bet = self.normalizeChips(game, player.bet),
                                              money = self.normalizeChips(game, player.money) )
        return packet
                
        
    
    def packetsPot2Player(self, game):
        packets = []
        current_pot = 0
        game_state = game.showdown_stack[0]
        pots = game_state['side_pots']['pots']
        frame_count = len(game.showdown_stack) - 1
        for frame in game.showdown_stack:
            if frame['type'] == 'left_over':
                player = game.getPlayer(frame['serial'])
                packets.append(self.chipsPot2Player(game, player, frame['chips_left'], len(pots) - 1, "left_over"))
            elif frame['type'] == 'uncalled':
                player = game.getPlayer(frame['serial'])
                packets.append(self.chipsPot2Player(game, player, frame['uncalled'], len(pots) - 1, "uncalled"))
            elif frame['type'] == 'resolve':
                cumulated_pot_size = 0
                next_pot = current_pot
                for (pot_size, pot_total) in pots[current_pot:]:
                    cumulated_pot_size += pot_size
                    next_pot += 1
                    if cumulated_pot_size >= frame['pot']:
                        break
                if cumulated_pot_size != frame['pot']:
                    self.error("pot %d, total size = %d, expected %d" % ( current_pot, cumulated_pot_size, frame['pot'] )) #pragma: no cover
                merged_pot = next_pot - 1
                if merged_pot > current_pot:
                    merge = PacketPokerChipsPotMerge(game_id = game.id,
                                                     sources = range(current_pot, merged_pot),
                                                     destination = merged_pot)
                    if self.verbose > 2:
                        self.message("packetsPot2Player: %s" % merge)
                    packets.append(merge)
                if frame_count == 1 and len(frame['serial2share']) == 1:
                    #
                    # Happens quite often : single winner. Special case where
                    # we use the exact chips layout saved in game_state.
                    #
                    serial = frame['serial2share'].keys()[0]
                    packets.append(self.chipsPot2Player(game, game.getPlayer(serial), game_state['pot'], merged_pot, "win"))
                else:
                    #
                    # Possibly complex showdown, cannot avoid breaking chip stacks
                    #
                    for (serial, share) in frame['serial2share'].iteritems():
                        packets.append(self.chipsPot2Player(game, game.getPlayer(serial), share, merged_pot, "win"))
                current_pot = next_pot
            else:
                pass
                
        for player in game.serial2player.itervalues():
            packets.append(self.updatePlayerChips(game, player))
            if self.what & PacketPokerExplain.CHIPSTACKS:
                packets.append(self.explainPlayerChips(game, player))
        packets.extend(self.updatePotsChips(game, []))
        return packets
        
    def packetsShowdown(self, game):
        if not game.isGameEndInformationValid():
            return []

        game_state = game.showdown_stack[0]
        delta_max = -1
        serial_delta_max = -1
        for (serial, delta) in game_state['serial2delta'].iteritems():
            if delta_max < delta:
                delta_max = delta
                serial_delta_max = serial
        
        packets = []
        if game.variant == "7stud":
            for player in game.playersAll():
                packets.append(PacketPokerPlayerNoCards(game_id = game.id,
                                                        serial = player.serial))
                if player.hand.areVisible():
                    packet = PacketPokerPlayerCards(game_id = game.id,
                                                    serial = player.serial,
                                                    cards = player.hand.tolist(True))
                    packet.visibles = "hole"
                    packets.append(packet)

        for (serial, best) in game.serial2best.iteritems():
            for (side, (value, bestcards)) in best.iteritems():
                if serial in game.side2winners[side]:
                    if len(bestcards) > 1:
                        side = game.isHighLow() and side or ""
                        if side == "low":
                            hand = ""
                        else:
                            hand = game.readableHandValueShort(side, bestcards[0], bestcards[1:])
                        cards = game.getPlayer(serial).hand.toRawList()
                        best_hand = 0
                        if serial == serial_delta_max:
                            best_hand = 1
                        packets.append(PacketPokerBestCards(game_id = game.id,
                                                            serial = serial,
                                                            side = side,
                                                            cards = cards,
                                                            bestcards = bestcards[1:],
                                                            board = game.board.tolist(True),
                                                            hand = hand,
                                                            besthand = best_hand))
        return packets

    def packetsTableQuit(self, game):
        packets = []
        packets.append(PacketPokerBatchMode(game_id = game.id))
        for player in game.playersAll():
            packets.append(PacketPokerPlayerLeave(game_id = game.id,
                                                  serial = player.serial,
                                                  seat = player.seat))
        packets.append(PacketPokerStreamMode(game_id = game.id))
        packets.append(PacketPokerTableQuit(game_id = game.id,
                                            serial = self.getSerial()))
        packets.append(self.currentGames(game.id))
        return packets

