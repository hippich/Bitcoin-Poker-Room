#
# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C)       2008, 2009 Bradley M. Kuhn <bkuhn@ebb.org>
# Copyright (C)             2008 Johan Euphrosine <proppy@aminche.com>
# Copyright (C) 2004, 2005, 2006 Mekensleep
#                                24 rue vieille du temple 75004 Paris
#                                <licensing@mekensleep.com>
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
#  Loic Dachary <loic@gnu.org>
#  Bradley M. Kuhn <bkuhn@ebb.org> (2008)
#  Johan Euphrosine <proppy@aminche.com> (2008)
#  Henry Precheur <henry@precheur.org> (2004)

from string import join
import sets
import re

from twisted.internet import defer

from types import *
from traceback import format_exc

from pokerengine import pokergame
from pokernetwork.user import User, checkNameAndPassword
from pokernetwork.pokerpackets import *
from pokernetwork.pokerexplain import PokerExplain
from pokernetwork.pokerrestclient import PokerRestClient
from twisted.internet import protocol, reactor, defer

DEFAULT_PLAYER_USER_DATA = { 'ready': True }

class PokerAvatar:

    def __init__(self, service):
        self.protocol = None
        self.packet_id = 0
        self.localeFunc = None
        self.roles = sets.Set()
        self.service = service
        self.tables = {}
        self.user = User()
        self._packets_queue = []
        self.warnedPacketExcess = False
        self.tourneys = []
        self.setExplain(0)
        self.has_session = False
        self.bugous_processing_hand = False
        self.noqueuePackets()
        self._block_longpoll_deferred = False
        self._longpoll_deferred = None
        self.game_id2rest_client = {}
        self.distributed_args = '?explain=no'
        self.longPollTimer = None
        self._flush_next_longpoll = False

    def setDistributedArgs(self, uid, auth):
        self.distributed_args = '?explain=no&uid=%s&auth=%s' % ( uid, auth )
        
    def __str__(self):
        return "PokerAvatar serial = %s, name = %s" % ( self.getSerial(), self.getName() )

    def setExplain(self, what):
        if what:
            if self.explain == None:
                if self.tables:
                    self.error("setExplain must be called when not connected to any table")
                    return False

                self.explain = PokerExplain(dirs = self.service.dirs,
                                            verbose = self.service.verbose,
                                            explain = what)
        else:
            self.explain = None
        return True

    def _setDefaultLocale(self, locale):
        """Set self.localFunc using locale iff. it is not already set.
        Typically, this method is only used for a locale found for the
        user in the database.  If the client sends a
        PacketPokerSetLocale(), that will always take precedent and should
        not use this method, but self.setLocale() instead."""
        if not self.localeFunc:
            return self.setLocale(locale)
        else:
            return None
            
    def setLocale(self, locale):
        if locale:
            # 'ISO-8859-1' is currently enforced for all setLocale()
            # requests.  This is primarily because the JSON interface
            # implemented in pokersite.py *assumes* that all strings must
            # be 'ISO-8859-1' and encodes them to unicode.  We should
            # actually find a way to be knowledgeable about the needed
            # encoding, because there is probably pointless conversion
            # between ISO and UTF-8 happening in this process.  Also, we
            # cannot currently support any languages that are non
            # 'ISO-8859-1', so that's a huge FIXME!  --bkuhn, 2008-10-28
            self.localeFunc = self.service.locale2translationFunc(locale, 'ISO-8859-1')
        return self.localeFunc

    def setProtocol(self, protocol):
        self.protocol = protocol

#    def __del__(self):
#       self.message("instance deleted")

    def error(self, string):
        self.message("ERROR " + str(string))
        
    def message(self, string):
        print "PokerAvatar: " + str(string)
        
    def isAuthorized(self, type):
        return self.user.hasPrivilege(self.service.poker_auth.GetLevel(type))

    def relogin(self, serial):
        player_info = self.service.getPlayerInfo(serial)
        self.user.serial = serial
        self.user.name = player_info.name
        self.user.privilege = User.REGULAR
        self.user.url = player_info.url
        self.user.outfit = player_info.outfit
        self._setDefaultLocale(player_info.locale)

        if self.explain:
            self.explain.handleSerial(PacketSerial(serial = serial))
        self.service.avatar_collection.add(serial, self)
        self.tourneyUpdates(serial)
        self.loginTableUpdates(serial)
    
    def login(self, info):
        (serial, name, privilege) = info
        self.user.serial = serial
        self.user.name = name
        self.user.privilege = privilege

        player_info = self.service.getPlayerInfo(serial)
        self.user.url = player_info.url
        self.user.outfit = player_info.outfit
        self._setDefaultLocale(player_info.locale)

        self.sendPacketVerbose(PacketSerial(serial = self.user.serial))
        if PacketPokerRoles.PLAY in self.roles:
            self.service.avatar_collection.add(serial, self)
        if self.service.verbose:
            self.message("user %s/%d logged in" % ( self.user.name, self.user.serial ))
        if self.protocol:
            self.has_session = self.service.sessionStart(self.getSerial(), str(self.protocol.transport.client[0]))
        self.tourneyUpdates(serial)
        self.loginTableUpdates(serial)

    def tourneyUpdates(self, serial):
        places = self.service.getPlayerPlaces(serial)
        self.tourneys = places.tourneys

    def loginTableUpdates(self, serial):
        #
        # Send player updates if it turns out that the player was already
        # seated at a known table.
        #
        for table in self.tables.values():
            if table.possibleObserverLoggedIn(self, serial):
                game = table.game
                self.sendPacketVerbose(PacketPokerPlayerCards(game_id = game.id,
                                                              serial = serial,
                                                              cards = game.getPlayer(serial).hand.toRawList()))
                self.sendPacketVerbose(PacketPokerPlayerSelf(game_id = game.id,
                                                             serial = serial))
                pending_blind_request = game.isBlindRequested(serial)
                pending_ante_request = game.isAnteRequested(serial)
                if pending_blind_request or pending_ante_request:
                    if pending_blind_request:
                        (amount, dead, state) = game.blindAmount(serial)
                        self.sendPacketVerbose(PacketPokerBlindRequest(game_id = game.id,
                                                                       serial = serial,
                                                                       amount = amount,
                                                                       dead = dead,
                                                                       state = state))
                    if pending_ante_request:
                        self.sendPacketVerbose(PacketPokerAnteRequest(game_id = game.id,
                                                                      serial = serial,
                                                                      amount = game.ante_info["value"]))

    def logout(self):
        if self.user.serial:
            if PacketPokerRoles.PLAY in self.roles:
                self.service.avatar_collection.remove(self.user.serial, self)
            if self.has_session:
                self.service.sessionEnd(self.getSerial())
            self.user.logout()
        
    def auth(self, packet):
        status = checkNameAndPassword(packet.name, packet.password)
        if status[0]:
            ( info, reason ) = self.service.auth(packet.name, packet.password, self.roles)
            code = 0
        else:
            self.message("auth: failure " + str(status))
            reason = status[2]
            code = status[1]
            info = False
        if info:
            self.sendPacketVerbose(PacketAuthOk())
            self.login(info)
        else:
            self.sendPacketVerbose(PacketAuthRefused(message = reason,
                                                     code = code,
                                                     other_type = PACKET_LOGIN))

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

    def queuePackets(self):
        self._queue_packets = True

    def noqueuePackets(self):
        self._queue_packets = False

    def extendPacketsQueue(self, newPackets):
        """takes PokerAvatar object and a newPackets as arguments, and
        extends the self._queue_packets variable by that packet.  Checking
        is done to make sure we haven't exceeded server-wide limits on
        packet queue length.  PokerAvatar will be force-disconnected if
        the packets exceed the value of
        self.service.getClientQueuedPacketMax().  A warning will be
        printed when the packet queue reaches 75% of the limit imposed by
        self.service.getClientQueuedPacketMax()"""
        # This method was introduced when we added the force-disconnect as
        # the stop-gap.
        self._packets_queue.extend(newPackets)
        self.flushLongPollDeferred()
        warnVal = int(.75 * self.service.getClientQueuedPacketMax())
        if len(self._packets_queue) >= warnVal:
            # If we have not warned yet that packet queue is getting long, warn now.
            if not self.warnedPacketExcess:
                self.warnedPacketExcess = True
                self.error("WARNING: user %d has more than %d packets queued; will force-disconnect when %d are queued" % (self.getSerial(), warnVal, self.service.getClientQueuedPacketMax()))
            if len(self._packets_queue) >= self.service.getClientQueuedPacketMax():
                self.service.forceAvatarDestroy(self)

    def resetPacketsQueue(self):
        self.warnedPacketExcess = False
        queue = self._packets_queue
        self._packets_queue = []
        return queue

    def removeGamePacketsQueue(self, game_id):
        self._packets_queue = filter(lambda packet: not hasattr(packet, "game_id") or packet.game_id != game_id, self._packets_queue)

    def sendPacket(self, packet):
        self.packet_id += 1
        if self.packet_id > 4000000000:
          self.packet_id = 1
        packet.packet_id = self.packet_id

        from pokerengine.pokergame import init_i18n as pokergame_init_i18n
        # Note on special processing of locales on packet send:
        #    Ideally, clients would do their own locale work.  However, in
        #    particular when PokerExplain is in effect, some clients are
        #    requiring explanation strings coming from the server about
        #    what is happening in the game.  (Indeed, PokerExplain exists
        #    for precisely that scenario.)  Therefore, every time we send a
        #    packet via PokerAvatar, we need to make sure the local in
        #    poker-engine's pokergame localization is set properly to the
        #    localization requested by the client (iff. they have
        #    requested one via PacketPokerSetLocale).  Note that because
        #    global variables are effectively only file-wide, the _() that
        #    we create here propagates only as wide as this file.  the
        #    call to pokergame_init_i18n() is what actually changes the
        #    _() defined in pokergame.py.
        #
        #    It is in some ways overkill to redefine our own _() here,
        #    particularly because at the time of writing, we don't
        #    actually have localization strings in the functions in this
        #    file.  However, should we have them later, we'd obviously
        #    want those strings to be localized for the client, at least
        #    during packet sending.
        #
        #    Note that _ default value depends of locale installation
        #    by pokerservice, as
        #    http://docs.python.org/library/gettext.html point out,
        #    gettext.install installs the function _() in Python’s
        #    builtins namespace. Assigning it to self.localeFunc
        #    convert it to a global that is file wise (as pointed
        #    above).

        global _
        if self.localeFunc:
            # First, if our _() has never been defined, we simply set it to None
            try:
                self._avatarSavedUnder = _
            except NameError:
                self._avatarSavedUnder = None
            _ = self.localeFunc
            pokergameSavedUnder = pokergame_init_i18n('', self.localeFunc)
	if self.explain and not isinstance(packet, defer.Deferred) and packet.type != PACKET_ERROR:
            try:
                self.explain.explain(packet)
                packets = self.explain.forward_packets
            except:
                packets = [ PacketError(other_type = PACKET_NONE, message = format_exc()) ]
                if self.service.verbose >= 0:
                    self.message(packets[0].message)
                self.explain = None # disabling the explain instance
                                    # that issued the exception, as it
                                    # may be in an inconsistent state,
                                    # and used before the avatar
                                    # destruction
                self.service.forceAvatarDestroy(self)
	else:
	    packets = [ packet ]
        if self._queue_packets:
            self.extendPacketsQueue(packets)
        else:
	    for packet in packets:
                self.protocol.sendPacket(packet)
        if self.localeFunc:
            _ = self._avatarSavedUnder
            pokergame_init_i18n('', pokergameSavedUnder)

    # Below, we assign the method queueDeferred() is the same as
    # sendPacket().  Be careful not to indent the line below; if you
    # aren't paying attention, you might think it belongs inside the
    # previous function.  It doesn't. ...  Ok, so I never got over the
    # "whitespace indentation matters" thing in Python, and I get careless
    # sometimes, then after I do I proceed to write warning comments that
    # normal Python programmers probably don't need. :-p -- bkuhn
    queueDeferred = sendPacket
    
    def sendPacketVerbose(self, packet):
        if self.service.verbose > 1 and hasattr(packet, 'type') and packet.type != PACKET_PING or self.service.verbose > 5:
            self.message("sendPacket(%d): %s" % ( self.getSerial(), str(packet) ))
        self.sendPacket(packet)
        
    def packet2table(self, packet):
        if hasattr(packet, "game_id") and self.tables.has_key(packet.game_id):
            return self.tables[packet.game_id]
        else:
            return False

    def longpollDeferred(self):
        self._longpoll_deferred = defer.Deferred()
        d = self.flushLongPollDeferred()
        if not d.called:
            def longPollDeferredTimeout():
                self.longPollTimer = None
                self._longpoll_deferred = None
                packets = self.resetPacketsQueue()
                if self.service.verbose > 3:
                    self.message("longPollDeferredTimeout(%s): " % str(packets))
                d.callback(packets)
            self.longPollTimer = reactor.callLater(self.service.long_poll_timeout, longPollDeferredTimeout)
        return d

    def blockLongPollDeferred(self):
        self._block_longpoll_deferred = True
        
    def unblockLongPollDeferred(self):
        self._block_longpoll_deferred = False
        self.flushLongPollDeferred()

    def flushLongPollDeferred(self):
        if self._block_longpoll_deferred == False and self._longpoll_deferred and (len(self._packets_queue) > 0 or self._flush_next_longpoll):
            self._flush_next_longpoll = False
            packets = self.resetPacketsQueue()
            if self.service.verbose > 3:
                self.message("flushLongPollDeferred(%s): " % str(packets))
            d = self._longpoll_deferred
            self._longpoll_deferred = None
            d.callback(packets)
            if self.longPollTimer and self.longPollTimer.active():
                self.longPollTimer.cancel()
            return d
        return self._longpoll_deferred

    def longPollReturn(self):
        if self._longpoll_deferred:
            packets = self.resetPacketsQueue()
            if self.service.verbose > 3:
                self.message("longPollReturn(%s): " % str(packets))
            d = self._longpoll_deferred
            self._longpoll_deferred = None
            d.callback(packets)
            if self.longPollTimer and self.longPollTimer.active():
                self.longPollTimer.cancel()
        else:
            self._flush_next_longpoll = True
            
    def handleDistributedPacket(self, request, packet, data):
        resthost, game_id = self.service.packet2resthost(packet)
        if resthost:
            return self.distributePacket(packet, data, resthost, game_id)
        else:
            return self.handlePacketDefer(packet)

    def getOrCreateRestClient(self, resthost, game_id):
        #
        # no game_id means the request must be delegated for tournament
        # registration or creation. Not for table interaction.
        #
        ( host, port, path ) = resthost
        path += self.distributed_args
        if self.service.verbose > 3:
            self.message("getOrCreateRestClient(%s, %d, %s, %s)" % ( host, port, path, str(game_id) ))
        if game_id:
            if not self.game_id2rest_client.has_key(game_id):
                if self.service.verbose > 1:
                    self.message("getOrCreateRestClient(%s, %d, %s, %s): create" % ( host, port, path, str(game_id) ))
                self.game_id2rest_client[game_id] = PokerRestClient(host, port, path, longPollCallback = lambda packets: self.incomingDistributedPackets(packets, game_id), verbose = self.service.verbose)
            client = self.game_id2rest_client[game_id]
        else:
            client = PokerRestClient(host, port, path, longPollCallback = None, verbose = self.service.verbose)
        return client
            
    def distributePacket(self, packet, data, resthost, game_id):
        ( host, port, path ) = resthost
        client = self.getOrCreateRestClient(resthost, game_id)
        d = client.sendPacket(packet, data)
        d.addCallback(lambda packets: self.incomingDistributedPackets(packets, game_id))
        d.addCallback(lambda x: self.resetPacketsQueue())
        return d
            
    def incomingDistributedPackets(self, packets, game_id):
        if self.service.verbose > 3:
            self.message("incomingDistributedPackets(%s, %s)" % ( str(packets), str(game_id) ))
        self.blockLongPollDeferred()
        for packet in packets:
            self.sendPacket(packet)
        self.unblockLongPollDeferred()
        if game_id:
            if game_id not in self.tables and (not(self.explain) or not(self.explain.games.gameExists(game_id))):
                #
                # discard client if nothing pending and not in the list
                # of active tables
                #
                client = self.game_id2rest_client[game_id]
                if ( len(client.queue.callbacks) <= 0 or
                     client.pendingLongPoll ):
                    if self.service.verbose > 1:
                        self.message("incomingDistributedPackets: del %d" % game_id)
                    self.game_id2rest_client[game_id].clearTimeout()
                    del self.game_id2rest_client[game_id]

    def handlePacketDefer(self, packet):
        if self.service.verbose > 2:
            self.message("handlePacketDefer(%d): " % self.getSerial() + str(packet))

        self.queuePackets()

        if packet.type == PACKET_POKER_LONG_POLL:
            return self.longpollDeferred()

        self.handlePacketLogic(packet)
        packets = self.resetPacketsQueue()
        if len(packets) == 1 and isinstance(packets[0], defer.Deferred):
            d = packets[0]
            #
            # turn the return value into an List if it is not
            #
            def packetList(result):
                if type(result) == ListType:
                    return result
                else:
                    return [ result ]
            d.addCallback(packetList)
            return d
        else:
            return packets

    def handlePacket(self, packet):
        self.queuePackets()
        self.handlePacketLogic(packet)
        self.noqueuePackets()
        return self.resetPacketsQueue()

    def handlePacketLogic(self, packet):
        if self.service.verbose > 2 and packet.type != PACKET_PING:
            self.message("handlePacketLogic(%d): " % self.getSerial() + str(packet))

        if packet.type == PACKET_POKER_LONG_POLL_RETURN:
            self.longPollReturn()
            return

        if packet.type == PACKET_POKER_EXPLAIN:
            if self.setExplain(packet.value):
                self.sendPacketVerbose(PacketAck())
            else:
                self.sendPacketVerbose(PacketError(other_type = PACKET_POKER_EXPLAIN))
            return
        
        if packet.type == PACKET_POKER_SET_LOCALE:
            if self.setLocale(packet.locale):
                self.sendPacketVerbose(PacketAck())
            else:
                self.sendPacketVerbose(PacketPokerError(serial = self.getSerial(),
                                                        other_type = PACKET_POKER_SET_LOCALE))
            return

        if packet.type == PACKET_POKER_STATS_QUERY:
            self.sendPacketVerbose(self.service.stats(packet.string))
            return
        
        if packet.type == PACKET_POKER_MONITOR:
            self.sendPacketVerbose(self.service.monitor(self))
            return
        
        if packet.type == PACKET_PING:
            return
        
        if packet.type == PACKET_POKER_POLL:
            if packet.tourney_serial != 0 and not (packet.tourney_serial in self.tourneys):
                self.sendPacketVerbose(PacketPokerTourneyFinish(tourney_serial = packet.tourney_serial))
            return
        
        if not self.isAuthorized(packet.type):
            self.sendPacketVerbose(PacketAuthRequest())
            return

        if packet.type == PACKET_LOGIN:
            if self.isLogged():
                self.sendPacketVerbose(PacketError(other_type = PACKET_LOGIN,
                                                   code = PacketLogin.LOGGED,
                                                   message = "already logged in"))
            else:
                self.auth(packet)
            return

        if packet.type == PACKET_POKER_GET_PLAYER_PLACES:
            if packet.serial != 0:
                self.sendPacketVerbose(self.service.getPlayerPlaces(packet.serial))
            else:
                self.sendPacketVerbose(self.service.getPlayerPlacesByName(packet.name))
            return

        if packet.type == PACKET_POKER_GET_PLAYER_INFO:
            self.sendPacketVerbose(self.getPlayerInfo())
            return

        if packet.type == PACKET_POKER_GET_PLAYER_IMAGE:
            self.sendPacketVerbose(self.service.getPlayerImage(packet.serial))
            return

        if packet.type == PACKET_POKER_GET_USER_INFO:
            if self.getSerial() == packet.serial:
                self.getUserInfo(packet.serial)
            else:
                self.message("attempt to get user info for user %d by user %d" % ( packet.serial, self.getSerial() ))
            return

        elif packet.type == PACKET_POKER_GET_PERSONAL_INFO:
            if self.getSerial() == packet.serial:
                self.getPersonalInfo(packet.serial)
            else:
                self.message("attempt to get personal info for user %d by user %d" % ( packet.serial, self.getSerial() ))
                self.sendPacketVerbose(PacketAuthRequest())
            return

        elif packet.type == PACKET_POKER_PLAYER_INFO:
            if self.getSerial() == packet.serial:
                if self.setPlayerInfo(packet):
                    self.sendPacketVerbose(packet)
                else:
                    self.sendPacketVerbose(PacketError(other_type = PACKET_POKER_PLAYER_INFO,
                                                       code = PACKET_POKER_PLAYER_INFO,
                                                       message = "Failed to save set player information"))
            else:
                self.message("attempt to set player info for player %d by player %d" % ( packet.serial, self.getSerial() ))
            return
                
        elif packet.type == PACKET_POKER_PLAYER_IMAGE:
            if self.getSerial() == packet.serial:
                if self.service.setPlayerImage(packet):
                    self.sendPacketVerbose(PacketAck())
                else:
                    self.sendPacketVerbose(PacketError(other_type = PACKET_POKER_PLAYER_IMAGE,
                                                       code = PACKET_POKER_PLAYER_IMAGE,
                                                       message = "Failed to save set player image"))
            else:
                self.message("attempt to set player image for player %d by player %d" % ( packet.serial, self.getSerial() ))
            return
                
        elif packet.type == PACKET_POKER_PERSONAL_INFO:
            if self.getSerial() == packet.serial:
                self.setPersonalInfo(packet)
            else:
                self.message("attempt to set player info for player %d by player %d" % ( packet.serial, self.getSerial() ))
            return

        elif packet.type == PACKET_POKER_CASH_IN:
            if self.getSerial() == packet.serial:
                self.queueDeferred(self.service.cashIn(packet))
            else:
                self.message("attempt to cash in for user %d by user %d" % ( packet.serial, self.getSerial() ))
                self.sendPacketVerbose(PacketPokerError(serial = self.getSerial(),
                                                        other_type = PACKET_POKER_CASH_IN))
            return

        elif packet.type == PACKET_POKER_CASH_OUT:
            if self.getSerial() == packet.serial:
                self.sendPacketVerbose(self.service.cashOut(packet))
            else:
                self.message("attempt to cash out for user %d by user %d" % ( packet.serial, self.getSerial() ))
                self.sendPacketVerbose(PacketPokerError(serial = self.getSerial(),
                                                        other_type = PACKET_POKER_CASH_OUT))
            return

        elif packet.type == PACKET_POKER_CASH_QUERY:
            self.sendPacketVerbose(self.service.cashQuery(packet))
            return

        elif packet.type == PACKET_POKER_CASH_OUT_COMMIT:
            self.sendPacketVerbose(self.service.cashOutCommit(packet))
            return

        elif packet.type == PACKET_POKER_SET_ROLE:
            self.sendPacketVerbose(self.setRole(packet))
            return 

        elif ( packet.type == PACKET_POKER_SET_ACCOUNT or
               packet.type == PACKET_POKER_CREATE_ACCOUNT ):
            if self.getSerial() != packet.serial:
                packet.serial = 0
            self.sendPacketVerbose(self.service.setAccount(packet))
            return

        elif packet.type == PACKET_POKER_CREATE_TOURNEY:
            if self.getSerial() == packet.serial:
                self.sendPacketVerbose(self.service.tourneyCreate(packet))
            else:
                self.message("attempt to create tourney for player %d by player %d" % ( packet.serial, self.getSerial() ))
                self.sendPacketVerbose(PacketAuthRequest())
            return

        if packet.type == PACKET_POKER_TOURNEY_SELECT:
            ( playerCount, tourneyCount ) = self.service.tourneyStats()
            tourneyList = PacketPokerTourneyList(players = playerCount,
                                              tourneys = tourneyCount)
            tourneys = self.service.tourneySelect(packet.string)
            for tourney in tourneys:
                tourneyList.packets.append(PacketPokerTourney(**tourney))
            self.sendPacketVerbose(tourneyList)
            tourneyInfo = self.service.tourneySelectInfo(packet, tourneys)
            if tourneyInfo:
                self.sendPacketVerbose(tourneyInfo)
            return
        
        elif packet.type == PACKET_POKER_TOURNEY_REQUEST_PLAYERS_LIST:
            self.sendPacketVerbose(self.service.tourneyPlayersList(packet.game_id))
            return

        elif packet.type == PACKET_POKER_GET_TOURNEY_MANAGER:
            self.sendPacketVerbose(self.service.tourneyManager(packet.tourney_serial))
            return

        elif packet.type == PACKET_POKER_TOURNEY_REGISTER:
            if self.getSerial() == packet.serial:
                self.service.autorefill(packet.serial)
                self.service.tourneyRegister(packet)
                self.tourneyUpdates(packet.serial)
            else:
                self.message("attempt to register in tournament %d for player %d by player %d" % ( packet.game_id, packet.serial, self.getSerial() ))
            return
            
        elif packet.type == PACKET_POKER_TOURNEY_UNREGISTER:
            if self.getSerial() == packet.serial:
                self.sendPacketVerbose(self.service.tourneyUnregister(packet))
                self.tourneyUpdates(packet.serial)
            else:
                self.message("attempt to unregister from tournament %d for player %d by player %d" % ( packet.game_id, packet.serial, self.getSerial() ))
            return
            
        elif packet.type == PACKET_POKER_TABLE_REQUEST_PLAYERS_LIST:
            self.listPlayers(packet)
            return

        elif packet.type == PACKET_POKER_TABLE_SELECT:
            self.listTables(packet)
            return

        elif packet.type == PACKET_POKER_HAND_SELECT:
            self.listHands(packet, self.getSerial())
            return

        elif packet.type == PACKET_POKER_HAND_HISTORY:
            if self.getSerial() == packet.serial:
                self.sendPacketVerbose(self.service.getHandHistory(packet.game_id, packet.serial))
            else:
                self.message("attempt to get history of player %d by player %d" % ( packet.serial, self.getSerial() ))
            return

        elif packet.type == PACKET_POKER_HAND_SELECT_ALL:
            self.listHands(packet, None)
            return

        elif packet.type == PACKET_POKER_TABLE_JOIN:
            self.performPacketPokerTableJoin(packet)

            return

        elif packet.type == PACKET_POKER_TABLE_PICKER:
            self.performPacketPokerTablePicker(packet)
            return

        table = self.packet2table(packet)
            
        if table:
            if self.service.verbose > 2:
                self.message("packet for table " + str(table.game.id))
            game = table.game

            if packet.type == PACKET_POKER_READY_TO_PLAY:
                if self.getSerial() == packet.serial:
                    self.sendPacketVerbose(table.readyToPlay(packet.serial))
                else:
                    self.message("attempt to set ready to play for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_PROCESSING_HAND:
                if self.getSerial() == packet.serial:
                    if not self.bugous_processing_hand:
                        self.sendPacketVerbose(table.processingHand(packet.serial))
                    else:
                        self.sendPacketVerbose(PacketPokerError(game_id = game.id,
                                                                serial = self.getSerial(),
                                                                other_type = PACKET_POKER_PROCESSING_HAND))
                else:
                    self.message("attempt to set processing hand for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_START:
                if not game.isEndOrNull():
                    self.message("player %d tried to start a new game while in game " % self.getSerial())
                    self.sendPacketVerbose(PacketPokerStart(game_id = game.id))
                elif self.service.shutting_down:
                    self.message("server shutting down")
                elif table.owner != 0:
                    if self.getSerial() != table.owner:
                        self.message("player %d tried to start a new game but is not the owner of the table" % self.getSerial())
                        self.sendPacketVerbose(PacketPokerStart(game_id = game.id))
                    else:
                        table.beginTurn()
                else:
                    self.message("player %d tried to start a new game but is not the owner of the table" % self.getSerial())

            elif packet.type == PACKET_POKER_SEAT:
                self.performPacketPokerSeat(packet, table, game)

            elif packet.type == PACKET_POKER_BUY_IN:
                self.performPacketPokerBuyIn(packet, table, game)

            elif packet.type == PACKET_POKER_REBUY:
                if self.getSerial() == packet.serial:
                    self.service.autorefill(packet.serial)
                    if not table.rebuyPlayerRequest(self, packet.amount):
                        self.sendPacketVerbose(PacketPokerError(game_id = game.id,
                                                                serial = packet.serial,
                                                                other_type = PACKET_POKER_REBUY))
                else:
                    self.message("attempt to rebuy for player %d by player %d" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_CHAT:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    table.chatPlayer(self, packet.serial, packet.message[:128])
                else:
                    self.message("attempt chat for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_PLAYER_LEAVE:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    table.leavePlayer(self, packet.serial)
                else:
                    self.message("attempt to leave for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_SIT:
                self.performPacketPokerSit(packet, table)
                
            elif packet.type == PACKET_POKER_SIT_OUT:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:

                    table.sitOutPlayer(self, packet.serial)
                else:
                    self.message("attempt to sit out for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))
                
            elif packet.type == PACKET_POKER_AUTO_BLIND_ANTE:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    table.autoBlindAnte(self, packet.serial, True)
                else:
                    self.message("attempt to set auto blind/ante for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))
                
            elif packet.type == PACKET_POKER_NOAUTO_BLIND_ANTE:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    table.autoBlindAnte(self, packet.serial, False)
                else:
                    self.message("attempt to set auto blind/ante for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))
            
            elif packet.type == PACKET_POKER_AUTO_MUCK:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    if table.game.getPlayer(packet.serial):
                        table.game.autoMuck(packet.serial, packet.auto_muck)
                else:
                    self.message("attempt to set auto muck for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() )             )
                
            elif packet.type == PACKET_POKER_MUCK_ACCEPT:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    table.muckAccept(self, packet.serial)
                else:
                    self.message("attempt to accept muck for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))
                    
            elif packet.type == PACKET_POKER_MUCK_DENY:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    table.muckDeny(self, packet.serial)
                else:
                    self.message("attempt to deny muck for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))
                
            elif packet.type == PACKET_POKER_BLIND:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    game.blind(packet.serial)
                else:
                    self.message("attempt to pay the blind of player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_WAIT_BIG_BLIND:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    game.waitBigBlind(packet.serial)
                else:
                    self.message("attempt to wait for big blind of player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_ANTE:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    game.ante(packet.serial)
                else:
                    self.message("attempt to pay the ante of player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_LOOK_CARDS:
                table.broadcast(packet)
                
            elif packet.type == PACKET_POKER_FOLD:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    
                    game.fold(packet.serial)
                else:
                    self.message("attempt to fold player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_CALL:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    
                    game.call(packet.serial)
                else:
                    self.message("attempt to call for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_RAISE:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    
                    game.callNraise(packet.serial, packet.amount)
                else:
                    self.message("attempt to raise for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_CHECK:
                if self.getSerial() == packet.serial or self.getSerial() == table.owner:
                    
                    game.check(packet.serial)
                else:
                    self.message("attempt to check for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))

            elif packet.type == PACKET_POKER_TABLE_QUIT:
                table.quitPlayer(self, self.getSerial())

            elif packet.type == PACKET_POKER_HAND_REPLAY:
                table.handReplay(self, packet.serial)

            table.update()

        elif not table and packet.type == PACKET_POKER_HAND_REPLAY:
            table = self.createTable(PacketPokerTable(
                        reason = PacketPokerTable.REASON_HAND_REPLAY))
            if table:
                table.handReplay(self, packet.serial)

        elif packet.type == PACKET_POKER_TABLE:
            packet.reason = PacketPokerTable.REASON_TABLE_CREATE
            table = self.createTable(packet)
            if table:
                table.joinPlayer(self, self.getSerial(),
                                 reason = PacketPokerTable.REASON_TABLE_CREATE)
            
        elif packet.type == PACKET_QUIT:
            for table in self.tables.values():
                table.quitPlayer(self, self.getSerial())

        elif packet.type == PACKET_LOGOUT:
            if self.isLogged():
                for table in self.tables.values():
                    table.quitPlayer(self, self.getSerial())
                self.logout()
            else:
                self.sendPacketVerbose(PacketError(code = PacketLogout.NOT_LOGGED_IN,
                                                   message = "Not logged in",
                                                   other_type = PACKET_LOGOUT))

    # The "perform" methods below are designed so that the a minimal
    # amount of code related to receiving a packet that appears in the
    # handlePacketLogic() giant if statement above.  The primary motive
    # for this is for things like PacketTablePicker(), that need to
    # perform operations *as if* the client has sent additional packets.
    # The desire is to keep completely parity between what the individual
    # packets do by themselves, and what "super-packets" like
    # PacketTablePicker() do.  A secondary benefit is that it makes that
    # giant if statement in handlePacketLogic() above a bit smaller.
    # -------------------------------------------------------------------------
    def performPacketPokerTableJoin(self, packet, table = None,
                                    deprecatedEmptyTableBehavior = True,
                                    requestorPacketType = PACKET_POKER_TABLE_JOIN,
                                    reason = PacketPokerTable.REASON_TABLE_JOIN):
        """Perform the operations that must occur when a
        PACKET_POKER_TABLE_JOIN is received."""
        
        if not table:
            table = self.service.getTable(packet.game_id)
        if table:
            self.removeGamePacketsQueue(packet.game_id)
            if not table.joinPlayer(self, self.getSerial(),
                                    reason = reason):
                if deprecatedEmptyTableBehavior:
                    self.sendPacketVerbose(PacketPokerTable(reason = reason))
                self.sendPacketVerbose(
                  PacketPokerError(code = PacketPokerTableJoin.GENERAL_FAILURE,
                                   message = "Unable to join table for unknown reason",
                                   other_type = requestorPacketType,
                                   serial     = self.getSerial(),
                                   game_id    = 0))
        return table
    # -------------------------------------------------------------------------
    def performPacketPokerSeat(self, packet, table, game):
        """Perform the operations that must occur when a PACKET_POKER_SEAT
        is received."""

        if PacketPokerRoles.PLAY not in self.roles:
            self.sendPacketVerbose(PacketPokerError(game_id = game.id,
                                                    serial = packet.serial,
                                                    code = PacketPokerSeat.ROLE_PLAY,
                                                    message = "PACKET_POKER_ROLES must set the role to PLAY before chosing a seat",
                                                    other_type = PACKET_POKER_SEAT))
            return False
        elif ( self.getSerial() == packet.serial or self.getSerial() == table.owner ):
            if not table.seatPlayer(self, packet.serial, packet.seat):
                packet.seat = -1
            else:
                packet.seat = game.getPlayer(packet.serial).seat
            self.getUserInfo(packet.serial)
            self.sendPacketVerbose(packet)
            return (packet.seat != -1)
        else:
            self.message("attempt to get seat for player '%s' by player '%s' that is not the owner of the game" % ( str(packet.serial), str(self.getSerial()) ))
            return False
    # -------------------------------------------------------------------------
    def performPacketPokerBuyIn(self, packet, table, game):
        if self.getSerial() == packet.serial:
            self.service.autorefill(packet.serial)
            if not table.buyInPlayer(self, packet.amount):
                self.sendPacketVerbose(PacketPokerError(game_id = game.id,
                                                        serial = packet.serial,
                                                        other_type = PACKET_POKER_BUY_IN))
                return False
            else:
                self.updateBuyinLimits(game)
                return True
        else:
            self.message("attempt to bring money for player %d by player %d" % ( packet.serial, self.getSerial() ))
            return False
    # -------------------------------------------------------------------------
    def performPacketPokerSit(self, packet, table):
        if self.getSerial() == packet.serial or self.getSerial() == table.owner:
            table.sitPlayer(self, packet.serial)
            return True
        else:
            self.message("attempt to sit back for player %d by player %d that is not the owner of the game" % ( packet.serial, self.getSerial() ))
            return False
    # -------------------------------------------------------------------------
    def performPacketPokerTablePicker(self, packet):
        mySerial = self.getSerial()
        if mySerial != packet.serial:
            errMsg = "attempt to run table picker for player %d by player %d" % ( packet.serial, mySerial )
            self.message(errMsg)
            self.sendPacketVerbose(
                PacketPokerError(code       = PacketPokerTableJoin.GENERAL_FAILURE,
                                 message    = errMsg,
                                 other_type = PACKET_POKER_TABLE_PICKER,
                                 serial     = mySerial,
                                 game_id    = 0))
        else:
            # Call autorefill() first before checking for a table,
            # since the amount of money we have left will impact the
            # table selection, and in a play-money scenario, we want
            # to have whatever play-money we can get before picking.
            self.service.autorefill(packet.serial)

            table = self.service.getTableBestByCriteria(mySerial,
                      min_players = packet.min_players, currency_serial = packet.currency_serial,
                      variant = packet.variant, betting_structure = packet.betting_structure)

            if not table:
                # If we cannot find a table, tell user we were unable to
                # find a table matching their criteria
                self.sendPacketVerbose(
                  PacketPokerError(code       = PacketPokerTableJoin.GENERAL_FAILURE,
                                   message    = "No table found matching given criteria",
                                   other_type = PACKET_POKER_TABLE_PICKER,
                                   serial     = mySerial,
                                   game_id    = 0))
            elif not table.game.canAddPlayer(mySerial):
                # If the table we found just can't take us, tell user we
                # could not add them.
                self.sendPacketVerbose(
                  PacketPokerError(code      = PacketPokerTableJoin.GENERAL_FAILURE,
                                   message   = "Found matching table, but unable to join it.",
                                   other_type = PACKET_POKER_TABLE_PICKER,
                                   serial     = mySerial,
                                   game_id    = table.game.id))
            else:
                # Otherwise, we perform the sequence of operations
                # that is defined by the semantics of this packet in
                # pokerpacket.py.  Basically, we perform:
                #   PacketTableJoin(), and if it succeeds,
                #   PacketPokerSeat(), and if it succeeds,
                #   We figure out our best buy-in choice, buyIn, then perform:
                #   PacketPokerBuyIn(amount = buyIn), and if it succeeds, 
                #   PacketPokerSit()
                if self.performPacketPokerTableJoin(
                     PacketPokerTableJoin(serial = mySerial,
                                          game_id = table.game.id), table,
                       deprecatedEmptyTableBehavior = False,
                       reason = PacketPokerTable.REASON_TABLE_PICKER):

                    # Giving no seat argument at all for the packet should cause
                    # us to get any available seat.
                    if self.performPacketPokerSeat(
                        PacketPokerSeat(serial = mySerial, game_id = table.game.id),
                        table, table.game):

                        # Next, determine if player can afford the "best"
                        # buy in.  If the player can't, give them the
                        # minimum buyin.

                        buyIn = table.game.bestBuyIn()
                        if self.service.getMoney(mySerial, table.currency_serial) < buyIn:
                            buyIn = table.game.buyIn(mySerial)
                            # No need to check above if we have that,
                            # since our answer on this table came from
                            # self.service.getTableByBestCriteria(), which
                            # promises us that we have at least minimum.
                        if self.performPacketPokerBuyIn(
                            PacketPokerBuyIn(serial = mySerial, amount = buyIn,
                                 game_id = table.game.id), table, table.game):
                            if packet.auto_blind_ante:
                                table.autoBlindAnte(self, packet.serial, True)
                            self.performPacketPokerSit(
                               PacketPokerSit(serial = mySerial, game_id = table.game.id),
                               table)
                            table.update()

    # -------------------------------------------------------------------------
    def setPlayerInfo(self, packet):
        self.user.url = packet.url
        self.user.outfit = packet.outfit
        return self.service.setPlayerInfo(packet)

    def setPersonalInfo(self, packet):
        self.personal_info = packet
        self.service.setPersonalInfo(packet)

    def setRole(self, packet):
        if packet.roles not in PacketPokerRoles.ROLES:
            return PacketError(code = PacketPokerSetRole.UNKNOWN_ROLE,
                               message = "role %s is unknown (roles = %s)" % ( packet.roles, PacketPokerRoles.ROLES),
                               other_type = PACKET_POKER_SET_ROLE)

        if packet.roles in self.roles:
            return PacketError(code = PacketPokerSetRole.NOT_AVAILABLE,
                               message = "another client already has role %s" % packet.roles,
                               other_type = PACKET_POKER_SET_ROLE)
        self.roles.add(packet.roles)
        return PacketPokerRoles(serial = packet.serial,
                                roles = join(self.roles, " "))
            
    def getPlayerInfo(self):
        if self.user.isLogged():
            return PacketPokerPlayerInfo(serial = self.getSerial(),
                                         name = self.getName(),
                                         url = self.user.url,
                                         outfit = self.user.outfit)
        else:
            return PacketError(code = PacketPokerGetPlayerInfo.NOT_LOGGED,
                               message = "Not logged in",
                               other_type = PACKET_POKER_GET_PLAYER_INFO)
    
    def listPlayers(self, packet):
        table = self.service.getTable(packet.game_id)
        if table:
            players = table.listPlayers()
            self.sendPacketVerbose(PacketPokerPlayersList(game_id = packet.game_id,
                                                          players = players))
        
    def listTables(self, packet):
        packets = []
        for table in self.service.listTables(packet.string, self.getSerial()):
            packet = PacketPokerTable(id = int(table['serial']),
                                      name = table['name'],
                                      variant = table['variant'],
                                      betting_structure = table['betting_structure'],
                                      seats = int(table['seats']),
                                      players = int(table['players']),
                                      hands_per_hour = int(table['hands_per_hour']),
                                      average_pot = int(table['average_pot']),
                                      percent_flop = int(table['percent_flop']),
                                      player_timeout = int(table['player_timeout']),
                                      muck_timeout = int(table['muck_timeout']),
                                      observers = int(table['observers']),
                                      waiting = int(table['waiting']),
                                      skin = table['skin'],
                                      currency_serial = int(table['currency_serial']),
                                      reason = PacketPokerTable.REASON_TABLE_LIST,
                                      )
            packet.tourney_serial = int(table['tourney_serial'])
            packets.append(packet)
        ( players, tables ) = self.service.statsTables()
        self.sendPacketVerbose(PacketPokerTableList(players = players,
                                                    tables = tables,
                                                    packets = packets))

    def listHands(self, packet, serial):
        if packet.type != PACKET_POKER_HAND_SELECT_ALL:
            start = packet.start
            count = min(packet.count, 200)
        if serial != None:
            select_list = "select distinct hands.serial from hands,user2hand "
            select_total = "select count(distinct hands.serial) from hands,user2hand "
            where  = " where user2hand.hand_serial = hands.serial "
            where += " and user2hand.user_serial = %d " % serial
            if packet.string:
                where += " and " + packet.string
        else:
            select_list = "select serial from hands "
            select_total = "select count(serial) from hands "
            where = ""
            if packet.string:
                where = "where " + packet.string
        where += " order by hands.serial desc"
        if packet.type != PACKET_POKER_HAND_SELECT_ALL:
            limit = " limit %d,%d " % ( start, count )
        else:
            limit = '';
        (total, hands) = self.service.listHands(select_list + where + limit, select_total + where)
        if packet.type == PACKET_POKER_HAND_SELECT_ALL:
            start = 0
            count = total
        self.sendPacketVerbose(PacketPokerHandList(string = packet.string,
                                                   start = start,
                                                   count = count,
                                                   hands = hands,
                                                   total = total))

    def createTable(self, packet):
        table = self.service.createTable(self.getSerial(), {
            "seats": packet.seats,
            "name": packet.name,
            "variant": packet.variant,
            "betting_structure": packet.betting_structure,
            "player_timeout": packet.player_timeout,
            "muck_timeout": packet.muck_timeout,
            "currency_serial": packet.currency_serial,
            "skin": packet.skin,
            "reason" : packet.reason})
        if not table:
            self.sendPacket(PacketPokerTable(reason = packet.reason))
        return table            

    def updateBuyinLimits(self, game):
        serial = self.getSerial()
        self.sendPacketVerbose(PacketPokerBuyInLimits(game_id = game.id,
                                                      min = game.buyIn(serial),
                                                      max = game.maxBuyIn(serial),
                                                      best = game.bestBuyIn(serial),
                                                      rebuy_min = game.minMoney()))

    def join(self, table, reason = ""):
        game = table.game
        
        self.tables[game.id] = table

        packet = table.toPacket()
        packet.reason = reason
        self.sendPacketVerbose(packet)
        self.updateBuyinLimits(game)
        self.sendPacketVerbose(PacketPokerBatchMode(game_id = game.id))
        nochips = 0
        for player in game.serial2player.values():
            player_info = table.getPlayerInfo(player.serial)
            self.sendPacketVerbose(PacketPokerPlayerArrive(game_id = game.id,
                                                           serial = player.serial,
                                                           name = player_info.name,
                                                           url = player_info.url,
                                                           outfit = player_info.outfit,
                                                           blind = player.blind,
                                                           remove_next_turn = player.remove_next_turn,
                                                           sit_out = player.sit_out,
                                                           sit_out_next_turn = player.sit_out_next_turn,
                                                           auto = player.auto,
                                                           auto_blind_ante = player.auto_blind_ante,
                                                           wait_for = player.wait_for,
                                                           seat = player.seat))
            if self.service.has_ladder:
                packet = self.service.getLadder(game.id, table.currency_serial, player.serial)
                if packet.type == PACKET_POKER_PLAYER_STATS:
                    self.sendPacketVerbose(packet)
            if not game.isPlaying(player.serial):
                self.sendPacketVerbose(PacketPokerPlayerChips(game_id = game.id,
                                                              serial = player.serial,
                                                              bet = nochips,
                                                              money = player.money))
                if game.isSit(player.serial):
                    self.sendPacketVerbose(PacketPokerSit(game_id = game.id,
                                                          serial = player.serial))
                if player.isAuto():
                    self.sendPacketVerbose(PacketPokerAutoFold(game_id = game.id,
                                                          serial = player.serial))                    

        self.sendPacketVerbose(PacketPokerSeats(game_id = game.id,
                                                seats = game.seats()))
        if not game.isEndOrNull():
            #
            # If a game is running, replay it.
            #
            # If a player reconnects, his serial number will match
            # the serial of some packets, for instance the cards
            # of his hand. We rely on private2public to turn the
            # packet containing cards custom cards into placeholders
            # in this case.
            #
            for past_packet in table.history2packets(game.historyGet(), game.id, table.createCache()):
                self.sendPacketVerbose(table.private2public(past_packet, self.getSerial()))
        self.sendPacketVerbose(PacketPokerStreamMode(game_id = game.id))

    def addPlayer(self, table, seat):
        serial = self.getSerial()
        game = table.game
        if game.addPlayer(serial, seat):
            player = game.getPlayer(serial)
            player.setUserData(DEFAULT_PLAYER_USER_DATA.copy())
        table.sendNewPlayerInformation(serial)
        
    def connectionLost(self, reason):
        if self.service.verbose > 3:
            self.message("connection lost for %s/%d: %s" % ( self.getName(), self.getSerial(), reason ))
        for table in self.tables.values():
            table.disconnectPlayer(self, self.getSerial())
        self.logout()

    def getUserInfo(self, serial):
        self.service.autorefill(serial)
        self.sendPacketVerbose(self.service.getUserInfo(serial))

    def getPersonalInfo(self, serial):
        self.service.autorefill(serial)
        self.sendPacketVerbose(self.service.getPersonalInfo(serial))

    def removePlayer(self, table, serial):
        game = table.game
        player = game.getPlayer(serial)
        seat = player and player.seat
        avatars = table.avatar_collection.get(serial)
        self_is_last_avatar = len(avatars) == 1 and avatars[0] == self
        if self_is_last_avatar and game.removePlayer(serial):
            #
            # If the player is not in a game, the removal will be effective
            # immediately and can be announced to all players, including
            # the one that will be removed.
            #
            packet = PacketPokerPlayerLeave(game_id = game.id, serial = serial, seat = seat)
            self.sendPacketVerbose(packet)
            table.broadcast(packet)
            return True
        else:
            return False

    def sitPlayer(self, table, serial):
        game = table.game

        if table.isOpen():
            #
            # It does not harm to sit if already sit and it
            # resets the autoPlayer/wait_for flag.
            #
            if game.sit(serial):
                self.message("game.sit success - game_id: %d, serial: %d" % (game.id, serial))
                table.broadcast(PacketPokerSit(game_id = game.id,
                                               serial = serial))
            else:
                self.message("game.sit NOT success - game_id: %d, serial: %d" % (game.id, serial))
        else:
            game.comeBack(serial)
            table.broadcast(PacketPokerSit(game_id = game.id,
                                           serial = serial))


    def sitOutPlayer(self, table, serial):
        game = table.game
        if table.isOpen():
            if game.sitOutNextTurn(serial):
                table.broadcast(PacketPokerSitOut(game_id = game.id,
                                                  serial = serial))
        else:
            game.autoPlayer(serial)
            table.broadcast(PacketPokerAutoFold(game_id = game.id,
                                                serial = serial))

    def autoBlindAnte(self, table, serial, auto):
        game = table.game
        if game.isTournament():
            return
        game.getPlayer(serial).auto_blind_ante = auto
        if auto:
            self.sendPacketVerbose(PacketPokerAutoBlindAnte(game_id = game.id,
                                                            serial = serial))
        else:
            self.sendPacketVerbose(PacketPokerNoautoBlindAnte(game_id = game.id,
                                                              serial = serial))
                                                              
    def setMoney(self, table, amount):
        game = table.game

        if game.payBuyIn(self.getSerial(), amount):
            player = game.getPlayer(self.getSerial())
            nochips = 0
            table.broadcast(PacketPokerPlayerChips(game_id = game.id,
                                                   serial = self.getSerial(),
                                                   bet = nochips,
                                                   money = player.money))
            return True
        else:
            return False
        
