#
# Copyright (C) 2006 - 2010 Loic Dachary <loic@dachary.org>
# Copyright (C) 2008, 2009 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C) 2004, 2005, 2006 Mekensleep <licensing@mekensleep.com>
#                                26 rue des rosiers, 75004 Paris
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors:
#  Loic Dachary <loic@dachary.org>
#  Bradley M. Kuhn <bkuhn@ebb.org>
#
from math import ceil
from types import StringType
from pprint import pformat
import time, sys, random

def tournament_seconds():
    return time.time()

shuffler = random

from pokerengine.pokergame import PokerGameServer
from pokerengine import pokerprizes

TOURNAMENT_STATE_ANNOUNCED = "announced"
TOURNAMENT_STATE_REGISTERING = "registering"
TOURNAMENT_STATE_RUNNING = "running"
TOURNAMENT_STATE_BREAK_WAIT = "breakwait"
TOURNAMENT_STATE_BREAK = "break"
TOURNAMENT_STATE_COMPLETE = "complete"
TOURNAMENT_STATE_CANCELED = "canceled"
            
def equalizeCandidates(games):
    #
    # Games less than 70% full are willing to steal players from other
    # games. Games that are more than 70% full and that are not
    # running are willing to provide players to others.
    #
    want_players = []
    provide_players = []
    for game in games:
        threshold = int(game.max_players * .7)
        count = game.allCount()
        if count < threshold:
            want_players.append([ game.id, game.max_players - count ])
        elif game.isEndOrNull():
            serials = game.serialsAllSorted()
            provide_players.append((game.id, serials[:count - threshold]))
    return ( want_players, provide_players )

def equalizeGames(games, verbose = 0, log_message = None):
    ( want_players, provide_players ) = equalizeCandidates(games)

    results = []

    if len(want_players) <= 0:
        return results

    consumer_index = 0
    for (id, serials) in provide_players:
        want_players.sort(lambda a,b: int(a[1] - b[1]))
        if want_players[0][1] == 0:
            #
            # All satisfied, stop looping
            #
            break

        while len(serials) > 0:
            distributed = False
            for i in xrange(len(want_players)):
                consumer = want_players[consumer_index]
                consumer_index = ( consumer_index + 1 ) % len(want_players)
                if consumer[1] > 0:
                    consumer[1] -= 1
                    serial = serials.pop(0)
                    results.append(( id, consumer[0], serial ))
                    distributed = True
                    if len(serials) <= 0:
                        break
            if not distributed:
                break

    if log_message and verbose > 0 and len(results) > 0:
        log_message("balanceGames equalizeGames: " + pformat(results))

    return results

def breakGames(games, verbose = 0, log_message = None):
    if len(games) < 2:
        return []

    games = games[:]
    #
    # Games not running first, then games running.
    # Each is sorted with games that have least players first.
    #
    games.sort(lambda a,b: b.isEndOrNull() - a.isEndOrNull() or int(a.allCount() - b.allCount()) )

    to_break = [ {
        "id": game.id,
        "seats_left": game.max_players - game.allCount(),
        "serials": game.serialsAll(),
        "to_add": [],
        "running": not game.isEndOrNull() } for game in games ]

    if verbose > 2: log_message("balanceGames breakGames: %s" % to_break)
    results = []
    while True:
        result = breakGame(to_break[0], to_break[1:], verbose, log_message)
        to_break = filter(lambda game: game["seats_left"] > 0, to_break[1:])
        if result == False:
            break
        results.extend(result)
        if len(to_break) < 2:
            break

    if log_message and verbose > 0 and len(results) > 0:
        log_message("balanceGames breakGames: " + pformat(results))

    return results

def breakGame(to_break, to_fill, verbose = 0, log_message = None):
    #
    # Can't break a game in which players were moved or
    # that are running.
    #
    if len(to_break["to_add"]) > 0 or to_break["running"]:
        return False
    
    seats_left = sum([ game["seats_left"] for game in to_fill ])
    serials = to_break["serials"]
    id = to_break["id"]
    #
    # Don't break a game if there is not enough seats at the
    # other games
    #
    if seats_left < len(serials):
        return False

    #
    # Fill the largest games first, in the hope that the smallest
    # games can be broken later.
    #
    to_fill.reverse()
    result = []
    for game in to_fill:
        if game["seats_left"] > 0:
            count = min(game["seats_left"], len(serials))
            game["to_add"].extend(serials[:count])
            game["seats_left"] -= count
            result.append((id, game["id"], serials[:count]))
            serials = serials[count:]
            if len(serials) <= 0:
                break;

    return result

class PokerTournament:

    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', 'no name')
        self.description_short = kwargs.get('description_short', 'nodescription_short')
        self.description_long = kwargs.get('description_long', 'nodescription_long')
        self.serial = kwargs.get('serial', 1)
        self.verbose = kwargs.get('verbose', 0)
        self.players_quota = kwargs.get('players_quota', 10)
        self.players_min = kwargs.get('players_min', 2)
        self.variant = kwargs.get('variant', 'holdem')
        self.betting_structure = kwargs.get('betting_structure', 'level-15-30-no-limit')
        self.dirs = kwargs.get('dirs', [])
        self.seats_per_game = kwargs.get('seats_per_game', 10)
        self.sit_n_go = kwargs.get('sit_n_go', 'y')
        self.register_time = kwargs.get('register_time', 0)
        self.start_time = kwargs.get('start_time', 0)
        self.breaks_first = kwargs.get('breaks_first', 7200)
        self.breaks_interval = kwargs.get('breaks_interval', 3600)
        self.breaks_duration = kwargs.get('breaks_duration', 300)
        self.breaks_running_since = -1
        self.breaks_since = -1
        self.breaks_count = 0
        self.buy_in = int(kwargs.get('buy_in', 0))
        self.rake = int(kwargs.get('rake', 0))
        self.rebuy_delay = kwargs.get('rebuy_delay', 0)
        self.add_on = kwargs.get('add_on', 0)
        self.add_on_delay = kwargs.get('add_on_delay', 60)
        self.prize_min = kwargs.get('prize_min', 0)
        self.prizes_specs = kwargs.get('prizes_specs', "table")
        self.rank2prize = None
        self.finish_time = -1
        if type(self.start_time) is StringType:
            self.start_time = int(time.mktime(time.strptime(self.start_time, "%Y/%m/%d %H:%M")))
        self.prefix = ""
        
        self.players = []
        self.need_balance = False
        self.registered = 0
        self.winners = []
        self.state = TOURNAMENT_STATE_ANNOUNCED
        self.can_register = False
        self.games = []
        self.id2game = {}
        
        self.callback_new_state = lambda tournament, old_state, new_state: True
        self.callback_create_game = lambda tournament: PokerGameServer("poker.%s.xml", tournament.dirs)
        # I think callback_game_filled() is a misnomer because it's not
        # about the table being "filled" (i.e., the table could have less
        # than the max seated at it).  What really happens is that the
        # callback_game_filled() is made when the table is deemed to have
        # the number of players at it the tourney manager has decided
        # belong there (which may or may not be "filled").
        self.callback_game_filled = lambda tournament, game: True
        self.callback_destroy_game = lambda tournament, game: True
        self.callback_move_player = lambda tournament, from_game_id, to_game_id, serial: self.movePlayer(from_game_id, to_game_id, serial)
        self.callback_remove_player = lambda tournament, game_id, serial: self.removePlayer(game_id, serial)
        self.callback_cancel = lambda tournament: True
        self.loadPayouts()
        self.updateRegistering()

    def loadPayouts(self):
        if self.sit_n_go == 'y':
            player_count = self.players_quota
        else:
            player_count = self.registered
        self.prizes_object =  pokerprizes.__dict__['PokerPrizes' + self.prizes_specs.capitalize()](buy_in_amount = self.buy_in, player_count = player_count, guarantee_amount = self.prize_min, config_dirs = self.dirs)

    def message(self, message):
        print self.prefix + "[PokerTournament %s] " % self.name + message
        
    def canRun(self):
        if self.start_time < tournament_seconds():
            if self.sit_n_go == 'y' and self.registered >= self.players_quota:
                return True
            elif self.sit_n_go == 'n':
                if self.registered >= self.players_min:
                    return True
                else:
                    return None
            else:
                return False
        else:
            return False

    def getRank(self, serial):
        try:
            winners_count = len(self.winners)
            rank_first = self.registered - winners_count
            return self.winners.index(serial) + rank_first + 1
        except:
            return -1
        
    def updateRegistering(self):
        if self.state == TOURNAMENT_STATE_ANNOUNCED:
            now = tournament_seconds()
            if now - self.register_time > 0.0:
                self.changeState(TOURNAMENT_STATE_REGISTERING)
                return -1
            else:
                return self.register_time - now
        else:
            if self.verbose > 0: self.message("updateRegistering: should not be called while tournament is not in announced state")
            return -1

    def updateRunning(self):
        if self.state == TOURNAMENT_STATE_REGISTERING:
            ready = self.canRun()
            if ready == True:
                self.changeState(TOURNAMENT_STATE_RUNNING)
            elif ready == None:
                self.changeState(TOURNAMENT_STATE_CANCELED)
            elif ready == False:
                pass

    def remainingBreakSeconds(self):
        if self.breaks_since > 0:
            return self.breaks_duration - ( tournament_seconds() - self.breaks_since )
        else:
            return None
        
    def updateBreak(self, game_id = None):
        if self.breaks_duration <= 0:
            return False

        if self.state == TOURNAMENT_STATE_RUNNING:
            running_duration = tournament_seconds() - self.breaks_running_since
            if self.breaks_count > 0:
                running_max = self.breaks_interval
            else:
                running_max = self.breaks_first
            if running_duration >= running_max:
                self.breaks_games_id = []
                self.changeState(TOURNAMENT_STATE_BREAK_WAIT)
                
        if self.state == TOURNAMENT_STATE_BREAK_WAIT:
            #
            # game_id is 0 when updateBreak is called after a table was destroyed
            # as a side effect of balanceGames
            #
            if game_id > 0:
                self.breaks_games_id.append(game_id)
            on_break = True
            for game in self.games:
                #
                # games with a single player must not be taken into account because
                # nothing happens on them. Either it is the last game with a single
                # player and must be considered ready to enter the break. Or there
                # are still other tables playing and the game with a single player
                # may be broken and the player moved to another table when the hand
                # finishes at one of the other tables.
                #
                # If the games with a single player are not ignored, a two game
                # tournament would enter a deadlock in the following situation:
		#        1) table T1 finishes its hand and only has one player left
		#           tournament is not on BREAK_WAIT
		#        2) tournament break time is reached
		#        3) table T2 finishes its hand, no player is busted.
		#           endTurn is called and tournament enters BREAK_WAIT
		#           T2 is added to the list of tables for which there
		#           is not need to wait before declaring the tournament
		#           on break. Because T1 has only one player left and
		#           all other tables are expecting the break (i.e. no
		#           hand will be played), it can be added to the list
		#           of tables ready for the break.
		#                
                #
                if game.id not in self.breaks_games_id and len(game.playersAll()) > 1:
                    on_break = False
                    break
            if on_break:
                del self.breaks_games_id
                self.changeState(TOURNAMENT_STATE_BREAK)

        if self.state == TOURNAMENT_STATE_BREAK:
            if self.remainingBreakSeconds() <= 0:
                self.changeState(TOURNAMENT_STATE_RUNNING)

        if self.state not in (TOURNAMENT_STATE_RUNNING, TOURNAMENT_STATE_BREAK_WAIT, TOURNAMENT_STATE_BREAK):
            if self.verbose >= 0: print "PokerTournament:updateBreak: is not supposed to be called while in state %s" % self.state
            return None
        
        return True
        
    def changeState(self, state):
        if self.state == TOURNAMENT_STATE_ANNOUNCED and state == TOURNAMENT_STATE_REGISTERING:
            self.can_register = True
        elif self.state == TOURNAMENT_STATE_RUNNING and state == TOURNAMENT_STATE_BREAK_WAIT:
            pass
        elif self.state == TOURNAMENT_STATE_BREAK_WAIT and state == TOURNAMENT_STATE_BREAK:
            self.breaks_since = tournament_seconds()
        elif self.state == TOURNAMENT_STATE_BREAK and state == TOURNAMENT_STATE_RUNNING:
            self.breaks_since = -1
            self.breaks_running_since = tournament_seconds()
        elif self.state == TOURNAMENT_STATE_REGISTERING and state == TOURNAMENT_STATE_RUNNING:
            self.start_time = tournament_seconds()
            self.breaks_running_since = self.start_time
            self.createGames()
            self.can_register = False
        elif self.state == TOURNAMENT_STATE_REGISTERING and state == TOURNAMENT_STATE_CANCELED:
            self.can_register = False
            self.cancel()
            self.finish_time = tournament_seconds()
        elif ( self.state in ( TOURNAMENT_STATE_RUNNING, TOURNAMENT_STATE_BREAK_WAIT ) and
               state == TOURNAMENT_STATE_COMPLETE ):
            self.finish_time = tournament_seconds()
        else:
            if self.verbose >= 0: print "PokerTournament:changeState: cannot change from state %s to state %s" % ( self.state, state )
            return
        if self.verbose > 2: self.message("state change %s => %s" % ( self.state, state ))
        old_state = self.state
        self.state = state
        self.callback_new_state(self, old_state, self.state)

    def isRegistered(self, serial):
        return serial in self.players
        
    def canRegister(self, serial):
        if self.can_register and self.registered < self.players_quota:
            return not self.isRegistered(serial)
        else:
            return False

    def canUnregister(self, serial):
        return self.isRegistered(serial) and self.state == TOURNAMENT_STATE_REGISTERING
        
    def register(self, serial):
        if self.can_register:
            self.players.append(serial)
            self.registered += 1
            if self.sit_n_go != 'y':
                self.prizes_object.addPlayer()
                self.rank2prize = None
            if self.state == TOURNAMENT_STATE_REGISTERING:
                self.updateRunning()
            elif self.state == TOURNAMENT_STATE_RUNNING:
                self.sitPlayer(serial)
            return True
        else:
            return False

    def unregister(self, serial):
        if self.state == TOURNAMENT_STATE_REGISTERING:
            self.players.remove(serial)
            self.registered -= 1
            if self.sit_n_go != 'y':
                self.prizes_object.removePlayer()
                self.rank2prize = None
            return True
        else:
            return False

    def cancel(self):
        if self.state == TOURNAMENT_STATE_REGISTERING:
            self.callback_cancel(self)
            self.players = []
            self.registered = 0
            return True
        else:
            return False
        
    def sitPlayer(self, serial):
        pass

    def removePlayer(self, game_id, serial):
        game = self.id2game[game_id]
        game.removePlayer(serial)

    def movePlayer(self, from_game_id, to_game_id, serial):
        from_game = self.id2game[from_game_id]
        to_game = self.id2game[to_game_id]
        from_game.open()
        to_game.open()
        from_player = from_game.getPlayer(serial)
        to_game.addPlayer(serial)
        to_player = to_game.getPlayer(serial)
        to_game.payBuyIn(serial, from_player.money)
        to_game.sit(serial)
        to_game.autoBlindAnte(serial)
        to_player.name = from_player.name
        to_player.setUserData(from_player.getUserData())
        if(from_player.isSitOut()): to_game.sitOut(serial)
        if(from_player.isBot()): to_game.botPlayer(serial)
        from_game.removePlayer(serial)
        from_game.close()
        to_game.close()
    
    def createGames(self):
        games_count = int(ceil(self.registered / float(self.seats_per_game)))
        self.players_quota = games_count * self.seats_per_game
        players = self.players[:]
        shuffler.shuffle(players)
        for id in xrange(1, games_count + 1):
            game = self.callback_create_game(self)
            game.verbose = self.verbose
            game.setTime(0)
            game.setVariant(self.variant)
            game.setBettingStructure(self.betting_structure)
            game.setMaxPlayers(self.seats_per_game)
            if game.id == 0: game.id = id

            buy_in = game.buyIn()
            for seat in xrange(self.seats_per_game):
                if not players: break
                    
                player = players.pop()
                game.addPlayer(player)
                game.payBuyIn(player, buy_in)
                game.sit(player)
                game.autoBlindAnte(player)
                
            self.games.append(game)
        self.id2game = dict(zip([ game.id for game in self.games ], self.games))
        # Next, need to call balance games, because the table assignment
        # algorithm above does not account for scenarios where the last
        # few people end up a table too small.
        self.balanceGames()
        # Next, we can now notify via callback that all the games in
        # self.games have been "filled".
        for game in self.games:
            self.callback_game_filled(self, game)
            game.close()

    def endTurn(self, game_id):
        game = self.id2game[game_id]
        loosers = game.serialsBroke()
        loosers_count = len(loosers)

        for serial in loosers:
            self.winners.insert(0, serial)
            self.callback_remove_player(self, game_id, serial)
        if self.verbose > 2: self.message("winners %s" % self.winners)
        
        if len(self.winners) + 1 == self.registered:
            game = self.games[0]
            player = game.playersAll()[0]
            self.winners.insert(0, player.serial)
            self.callback_remove_player(self, game.id, player.serial)
            money = player.money
            player.money = 0
            expected = game.buyIn() * self.registered
            if money != expected and self.verbose >= 0:
                self.message("ERROR winner has %d chips and should have %d chips" % ( money, expected ))
            if self.verbose > 0: self.message("winners %s" % self.winners)
            self.callback_destroy_game(self, game)
            self.games = []
            self.id2game = {}
            self.changeState(TOURNAMENT_STATE_COMPLETE)
            return False
        else:
            if loosers_count > 0 or self.need_balance:
                self.balanceGames()
            if self.id2game.has_key(game_id):
                self.updateBreak(game_id)
            else:
                #
                # This happens if game_id was destroyed by the call to balanceGames above
                #
                self.updateBreak(0)
            return True
        
    def balanceGames(self):
        self.need_balance = False
        if len(self.games) < 2: return
        if self.verbose > 2: self.message("balanceGames")
        to_break = breakGames(self.games, self.verbose, self.message)
        games_broken = {}
        for (from_id, to_id, serials) in to_break:
            for serial in serials:
                if self.verbose > 2: self.message("balanceGames: player %d moved from %d to %d" % ( serial, from_id, to_id ))
                if self.state == TOURNAMENT_STATE_REGISTERING:
                    self.movePlayer(from_id, to_id, serial)
                else:
                    self.callback_move_player(self, from_id, to_id, serial)
            games_broken[from_id] = True

        if len(to_break) > 0:
            for game_id in games_broken.keys():
                game = self.id2game[game_id]
                self.callback_destroy_game(self, game)
                self.games.remove(game)
                del self.id2game[game.id]
            if self.verbose > 0: self.message("balanceGames: broke tables %s" % to_break)
            return True
        
        to_equalize = equalizeGames(self.games, self.verbose, self.message)
        for (from_id, to_id, serial) in to_equalize:
            if self.verbose > 2: self.message("balanceGames: player %d moved from %d to %d" % ( serial, from_id, to_id ))
            if self.state == TOURNAMENT_STATE_REGISTERING:
                self.movePlayer(from_id, to_id, serial)
            else:
                self.callback_move_player(self, from_id, to_id, serial)

        ( want_players, provide_players ) = equalizeCandidates(self.games)
        self.need_balance = want_players and not provide_players
        if self.need_balance and self.verbose > 2: self.message("balanceGames: postponed game equalization")
        
        return len(to_equalize) > 0

    def prizes(self):
        if not self.rank2prize:
            self.rank2prize = self.prizes_object.getPrizes()
        return self.rank2prize
