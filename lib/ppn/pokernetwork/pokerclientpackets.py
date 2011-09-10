#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
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
# Which packets describe where the chips go ?
#
# PACKET_POKER_CHIPS_PLAYER2BET
# PACKET_POKER_CHIPS_BET2POT
# PACKET_POKER_CHIPS_POT2PLAYER
# PACKET_POKER_CHIPS_BET2PLAYER
# PACKET_POKER_CHIPS_POT_MERGE
#
from struct import pack, unpack
import simplejson
import types
import decimal

from pokerengine.pokercards import PokerCards
from pokerengine.pokerchips import PokerChips

from pokernetwork.packets import Packet
from pokernetwork.pokerpackets import *

def chips2amount(chips):
    amount = 0
    for i in xrange(len(chips) / 2):
        amount += chips[i*2] * chips[i*2 + 1]
    return amount

class PokerClientPacketJSON(simplejson.JSONEncoder):

    def default(self, object):
        if isinstance(object, PokerCards):
            return ['Cards'] + [255] * len(object.cards)
        elif isinstance(object, PokerChips):
            return ['Chips', object.toint()]
        elif isinstance(object, decimal.Decimal):
            return str(object)
        else:
            return simplejson.JSONEncoder.default(self, object)

    @staticmethod
    def decode_objects(something):
        if type(something) is types.ListType:
            if something[0] in ('Cards', 'Chips'):
                if something[0] == 'Cards':
                    return PokerCards(something[1:])
                elif something[0] == 'Chips':
                    return PokerChips([1],[something[1]])
            else:
                return map(PokerClientPacketJSON.decode_objects, something)
        elif type(something) is types.DictType:
            return dict(map(lambda (k, v): [k, PokerClientPacketJSON.decode_objects(v)], something.iteritems()))
        else:
            return something
    
Packet.JSON = PokerClientPacketJSON()

class PokerClientPackets:
    @staticmethod
    def unpackchips(block):
        amount = int(unpack('!I', block[:4])[0])
        if amount > 0:
            chips = (1, amount)
        else:
            chips = []
        return ( block[4:], chips )
    
Packet.format_info['c'] = {
    'pack': lambda data: pack('!I', chips2amount(data)),
    'unpack': PokerClientPackets.unpackchips,
    'calcsize': lambda data: 4,
    }

########################################

class PacketPokerBestCards(PacketPokerCards):
    """\
Semantics: ordered list  of five "bestcards" hand for
player "serial" in game "game_id" that won the "side"
side of the pot. The "board", if not empty, is the list
of community cards at showdown. Also provides the
"cards" of the player.

Direction: client <=> client

cards: list of integers describing the player cards:

       2h/00  2d/13  2c/26  2s/39
       3h/01  3d/14  3c/27  3s/40
       4h/02  4d/15  4c/28  4s/41
       5h/03  5d/16  5c/29  5s/42
       6h/04  6d/17  6c/30  6s/43
       7h/05  7d/18  7c/31  7s/44
       8h/06  8d/19  8c/32  8s/45
       9h/07  9d/20  9c/33  9s/46
       Th/08  Td/21  Tc/34  Ts/47
       Jh/09  Jd/22  Jc/35  Js/48
       Qh/10  Qd/23  Qc/36  Qs/49
       Kh/11  Kd/24  Kc/37  Ks/50
       Ah/12  Ad/25  Ac/38  As/51
       
bestcards: list of integers describing the winning combination cards:
board: list of integers describing the community cards:
hand: readable string of the name best hand
besthand: 0 if it's not the best hand and 1 if it's the best hand
         best hand is the hand that win the most money
       
serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""

    info = PacketPokerCards.info + ( ("side", "", 's'),
                                     ("hand", "", 's'),
                                     ("bestcards", [], 'Bl'),
                                     ("board", [], 'Bl'),
                                     ("besthand", 0, 'B'),
                                     )

Packet.infoDeclare(globals(), PacketPokerBestCards, PacketPokerCards, 'POKER_BEST_CARDS', 170) # 0xaa # %SEQ%

########################################

class PacketPokerPotChips(Packet):
    """\
Semantics: the "bet" put in the "index" pot of the "game_id" game.

Direction: client <=> client

context: this packet is sent at least each time the pot index is
updated.

bet: list of pairs ( chip_value, chip_count ).
index: integer uniquely identifying a side pot in the range [0,10[
game_id: integer uniquely identifying a game.
"""

    info = Packet.info + ( ("game_id", 0, 'I'),
                           ("index", 0, 'B'),
                           ("bet", [], 'c'),
                           )

Packet.infoDeclare(globals(), PacketPokerPotChips, Packet, 'POKER_POT_CHIPS', 171) # 0xab # %SEQ%

########################################

class PacketPokerClientAction(PacketPokerId):
    """

    The action available/not available to the player
    
    """

    info = PacketPokerId.info + ( ("display", 0, 'B'),
                                  ("action", "", 's'),
                                  )

Packet.infoDeclare(globals(), PacketPokerClientAction, PacketPokerId, 'POKER_CLIENT_ACTION', 172) # 0xac # %SEQ%

########################################

class PacketPokerBetLimit(PacketPokerId):
    """\
Semantics: a raise must be at least "min" and most "max".
A call means wagering an amount of "call". The suggested
step to slide between "min" and "max" is "step". The step
is guaranteed to be an integral divisor of "call". The
player would be allin for the amount "allin". The player
would match the pot if betting "pot".

Context: this packet is issued each time a position change
occurs.

Direction: client <=> client

min: the minimum amount of a raise.
max: the maximum amount of a raise.
step: a hint for sliding in the [min, max] interval.
call: the amount of a call.
allin: the amount for which the player goes allin.
pot: the amount in the pot.
game_id: integer uniquely identifying a game.
"""

    info = PacketPokerId.info + ( ("min", 0, 'I'),
                                  ("max", 0, 'I'),
                                  ("step", 0, 'I'),
                                  ("call", 0, 'I'),
                                  ("allin", 0, 'I'),
                                  ("pot", 0, 'I'),
                                  )

Packet.infoDeclare(globals(), PacketPokerBetLimit, PacketPokerId, 'POKER_BET_LIMIT', 173) # 0xad # %SEQ%

########################################

class PacketPokerSitRequest(PacketPokerSit):
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerSitRequest, PacketPokerId, "POKER_SIT_REQUEST", 174) # 0xae # %SEQ%

########################################

class PacketPokerPlayerNoCards(PacketPokerId):
    """\
Semantics: the player "serial" has no cards in game "game_id".

Direction: client <=> client

Context: inferred at showdown.

serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerPlayerNoCards, PacketPokerId, "POKER_PLAYER_NO_CARDS", 175) # 0xaf # %SEQ%

######################################## 

class PacketPokerChipsPlayer2Bet(PacketPokerId):
    """\
Semantics: move "chips" from the player "serial" money chip stack
to the bet chip stack.

Direction: client <=> client

chips: list of pairs ( chip_value, chip_count ).
serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""

    info = PacketPokerId.info + (
        ('chips', [], 'c' ),
        )
    
Packet.infoDeclare(globals(), PacketPokerChipsPlayer2Bet, PacketPokerId, 'POKER_CHIPS_PLAYER2BET', 176) # 0xb0 # %SEQ%

######################################## 

class PacketPokerChipsBet2Pot(PacketPokerId):
    """\
Semantics: move "chips" from the player "serial" bet chip stack
to the "pot" pot.

Direction: client <=> client

Context: the pot index is by definition in the range [0,9] because
it starts at 0 and because there cannot be more pots than players.
The creation of side pots is inferred by the client when a player
is all-in and it is guaranteed that pots are numbered sequentially.

pot: the pot index in the range [0,9].
chips: list of integers counting the number of chips to move.
     The value of each chip is, respectively:
     1 2 5 10 20 25 50 100 250 500 1000 2000 5000.
serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""
    info = PacketPokerId.info + (
        ('chips', [], 'c' ),
        ('pot', -1, 'b' ),
        )
    
Packet.infoDeclare(globals(), PacketPokerChipsBet2Pot, PacketPokerId, 'POKER_CHIPS_BET2POT', 177) # 0xb1 # %SEQ%

######################################## Display packet

class PacketPokerChipsPot2Player(PacketPokerId):
    """\
Semantics: move "chips" from the pot "pot" to the player "serial"
money chip stack. The string "reason" explains why these chips 
are granted to the player. If reason is "win", it means the player
won the chips either because all other players folded or because
he had the best hand at showdown. If reason is "uncalled", it means
the chips are returned to him because no other player was will or
able to call his wager. If reason is "left-over", it means the chips
are granted to him because there was an odd chip while splitting the pot.

Direction: client <=> client

Context: the pot index is by definition in the range [0,9] because
it starts at 0 and because there cannot be more pots than players.
The creation of side pots is inferred by the client when a player
is all-in and it is guaranteed that pots are numbered sequentially.

reason: may be one of "win", "uncalled", "left-over"
pot: the pot index in the range [0,9].
chips: list of integers counting the number of chips to move.
     The value of each chip is, respectively:
     1 2 5 10 20 25 50 100 250 500 1000 2000 5000.
serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""

    info = PacketPokerId.info + (
        ('chips', [], 'c' ),
        ('pot', -1, 'b' ),
        ('reason', '', 's' ),
        )

Packet.infoDeclare(globals(), PacketPokerChipsPot2Player, PacketPokerId, 'POKER_CHIPS_POT2PLAYER', 178) # 0xb2 # %SEQ%

######################################## Display packet

class PacketPokerChipsPotMerge(PacketPokerId):
    """\
Semantics: merge the pots whose indexes are listed in
"sources" into a single pot at index "destination" in game "game_id".

Direction: client <=> client

Context: when generating PACKET_POKER_CHIPS_POT2PLAYER packets, if
multiple packet can be avoided by merging pots (e.g. when one player
wins all the pots).

destination: a pot index in the range [0,9].
sources: list of pot indexes in the range [0,9].
game_id: integer uniquely identifying a game.
"""

    info = PacketPokerId.info + (
        ('sources', [], 'Bl' ),
        ('destination', 0, 'B' ),
        )

Packet.infoDeclare(globals(), PacketPokerChipsPotMerge, PacketPokerId, 'POKER_CHIPS_POT_MERGE', 179) # 0xb3 # %SEQ%

######################################## Display packet

class PacketPokerChipsPotReset(PacketPokerId):
    """\
Semantics: all pots for game "game_id" are set to zero.

Direction: client <=> client

Context: it is inferred after a PACKET_POKER_TABLE or a
 PACKET_POKER_START packet is sent by the server. It is inferred
after the pot is distributed (i.e. after the game terminates
because a PACKET_POKER_WIN or PACKET_POKER_CANCELED is received).

game_id: integer uniquely identifying a game.
"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerChipsPotReset, PacketPokerId, "POKER_CHIPS_POT_RESET", 180) # 0xb4 # %SEQ%

######################################## Display packet

class PacketPokerChipsBet2player(PacketPokerChipsPlayer2Bet):
    """chips move from bet to player"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerChipsBet2player, PacketPokerChipsPlayer2Bet, "POKER_CHIPS_BET2PLAYER", 181) # 0xb5 # %SEQ%

######################################## Display packet

class PacketPokerEndRound(PacketPokerId):
    """\
Semantics: closes a betting round for game "game_id".

Direction: client <=> client

Context: inferred at the end of a sequence of packet related to
a betting round. Paying the blind / ante is not considered a
betting round. This packet is sent when the client side
knows that the round is finished but before the corresponding
packet (PACKET_POKER_STATE) has been received from the server.
It will be followed by the POKER_BEGIN_ROUND packet, either
immediatly if the server has no delay between betting rounds
or later if the server waits a few seconds between two betting
rounds.
It is not inferred at the end of the last betting round.

game_id: integer uniquely identifying a game.
"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerEndRound, PacketPokerId, "POKER_END_ROUND", 182) # 0xb6 # %SEQ%

########################################

class PacketPokerDisplayNode(Packet):
    """request POKER_DISPLAY_NODE packet"""

    info = Packet.info + (
        ('game_id', 0, 'I'),
        ('name', '', 's'),
        ('state', 0, 'I'),
        ('style', '', 's'),
        ('selection', None, 'no net'),
        )
    
Packet.infoDeclare(globals(), PacketPokerDisplayNode, Packet, 'POKER_DISPLAY_NODE', 183) # 0xb7 # %SEQ%

######################################## Display packet

class PacketPokerDealCards(PacketPokerId):
    """\
Semantics: deal "numberOfCards" down cards for each player listed
in "serials" in game "game_id".

Direction: client <=> client

Context: inferred after the beginning of a betting round (i.e.
after the PACKET_POKER_STATE packet is received) and after
the chips involved in the previous betting round have been
sorted (i.e. after PACKET_POKER_CHIPS_BET2POT packets are
inferred). Contrary to the PACKET_POKER_PLAYER_CARDS,
this packet is only sent if cards must be dealt. It
is guaranteed that this packet will always occur before
the PACKET_POKER_PLAYER_CARDS that specify the cards to
be dealt and that these packets will follow immediately
after it (no other packet will be inserted between this packet
and the first PACKET_POKER_PLAYER_CARDS). It is also guaranteed
that exactly one PACKET_POKER_PLAYER_CARDS will occur for each
serial listed in "serials".

numberOfCards: number of cards to be dealt.
serials: integers uniquely identifying players.
game_id: integer uniquely identifying a game.
"""
    info = PacketPokerId.info + (
        ('numberOfCards', 2, 'B'),
        ('serials', [], 'Il'),
        )

Packet.infoDeclare(globals(), PacketPokerDealCards, PacketPokerId, 'POKER_DEAL_CARDS', 184) # 0xb8 # %SEQ%

########################################

class PacketPokerChatHistory(Packet):
    """chat history show"""

    info = Packet.info + (
        ('show', 'no', 's'),
        )

Packet.infoDeclare(globals(), PacketPokerChatHistory, Packet, "POKER_CHAT_HISTORY", 185) # 0xb9 # %SEQ%
    
########################################

class PacketPokerDisplayCard(PacketPokerId):
    """Hide a player card"""

    info = PacketPokerId.info + (
        ('index', [], 'Bl'),
        ('display', 0, 'B'),
        )

Packet.infoDeclare(globals(), PacketPokerDisplayCard, PacketPokerId, "POKER_DISPLAY_CARD", 186) # 0xba # %SEQ%

########################################

class PacketPokerSelfInPosition(PacketPokerPosition):
    """\
Semantics: the player authenticated for this connection
is in position. Otherwise identical to PACKET_POKER_POSITION.

"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerSelfInPosition, PacketPokerPosition, "POKER_SELF_IN_POSITION", 187) # 0xbb # %SEQ%

########################################

class PacketPokerSelfLostPosition(PacketPokerPosition):
    """\
Semantics: the player authenticated for this connection
is in position. Otherwise identical to PACKET_POKER_POSITION.

"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerSelfLostPosition, PacketPokerPosition, "POKER_SELF_LOST_POSITION", 188) # 0xbc # %SEQ%

########################################

class PacketPokerHighestBetIncrease(PacketPokerId):
    """\
Semantics: a wager was made in game "game_id" that increases
the highest bet amount. 

Direction: client <=> client

Context: inferred whenever a wager is made that changes
the highest bet (live blinds are considered a wager, antes are not).
Inferred once per blindAnte round: when the
first big blind is posted. It is therefore guaranteed not to be posted
if a game is canceled because noone wanted to pay the big blind, even
if someone already posted the small blind. In all other betting rounds it
is inferred for each raise.

game_id: integer uniquely identifying a game.
"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerHighestBetIncrease, PacketPokerId, "POKER_HIGHEST_BET_INCREASE", 189) # 0xbd # %SEQ%

########################################

class PacketPokerPlayerWin(PacketPokerId):
    """\
Semantics: the player "serial" win.

Direction: client <=> client

Context: when a PacketPokerWin arrive from server. The packet is generated
from PACKET_PLAYER_WIN. For each player that wins something a packet
PlayerWin is generated.

serial: integer uniquely identifying a player.
"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerPlayerWin, PacketPokerId, "POKER_PLAYER_WIN", 190) # 0xbe # %SEQ%

########################################

class PacketPokerAnimationPlayerNoise(PacketPokerId):
    """\
Semantics: the player "serial" play or stop noise animation.

Direction: client <=> client

Context: a PacketPokerPlayerNoise is send to the client c++ to stop or start
player's noise animation.

serial: integer uniquely identifying a player.
action: string that contain "start" or "stop".
"""

    info = PacketPokerId.info + (
        ('action', 'start', 's'),
        )
    
Packet.infoDeclare(globals(), PacketPokerAnimationPlayerNoise, PacketPokerId, "POKER_ANIMATION_PLAYER_NOISE", 191) # 0xbf # %SEQ%

########################################

class PacketPokerAnimationPlayerFold(PacketPokerId):
    """\
Semantics: the player "serial" play an animation fold.

Direction: client <=> client

Context: a PacketPokerPlayerNoise is send to the client c++ to stop or start
player's noise animation.

serial: integer uniquely identifying a player.
animation: string used to select an animation fold.
"""

    info = PacketPokerId.info + (
        ('animation', 'UNKNOWN', 's'),
        )

Packet.infoDeclare(globals(), PacketPokerAnimationPlayerFold, PacketPokerId, "POKER_ANIMATION_PLAYER_FOLD", 192) # 0xc0 # %SEQ%

########################################

class PacketPokerAnimationPlayerBet(PacketPokerId):
    """\
"""

    info = PacketPokerId.info + (
        ('animation', '', 's'),
        ('chips', [], 'c'),
        ('amount', 0, 'I'),
        )

    def infoInit(self, **kwargs):
        Packet.infoInit(self, **kwargs)
        self.amount = chips2amount(self.chips)
        
Packet.infoDeclare(globals(), PacketPokerAnimationPlayerBet, PacketPokerId, "POKER_ANIMATION_PLAYER_BET", 193) # 0xc1 # %SEQ%

########################################

class PacketPokerAnimationPlayerChips(PacketPokerId):
    """\
"""
    info = PacketPokerId.info + (
        ('animation', '', 's'),
        ('chips', [], 'c'),
        ('state', '', 's'),
        ('amount', 0, 'I'),
        )

    def infoInit(self, **kwargs):
        Packet.infoInit(self, **kwargs)
        self.amount = chips2amount(self.chips)
        
Packet.infoDeclare(globals(), PacketPokerAnimationPlayerChips, PacketPokerId, "POKER_ANIMATION_PLAYER_CHIPS", 194) # 0xc2 # %SEQ%

########################################

class PacketPokerAnimationDealerChange(PacketPokerId):
    """\
"""

    info = PacketPokerId.info + (
        ('state', 'UNKNOWN', 's'),
        )

Packet.infoDeclare(globals(), PacketPokerAnimationDealerChange, PacketPokerId, "POKER_ANIMATION_DEALER_CHANGE", 195) # 0xc3 # %SEQ%

########################################

class PacketPokerAnimationDealerButton(PacketPokerId):
    """\
"""

    info = PacketPokerId.info + (
        ('state', 'UNKNOWN', 's'),
        )

Packet.infoDeclare(globals(), PacketPokerAnimationDealerButton, PacketPokerId, "POKER_ANIMATION_DEALER_BUTTON", 196) # 0xc4 # %SEQ%

########################################

class PacketPokerBeginRound(PacketPokerId):
    """\
Semantics: opens a betting round for game "game_id".

Direction: client <=> client

Context: inferred when the client knows that a betting round will
begin although it does not yet received information from the server to
initialize it. Paying the blind / ante is not considered a betting
round. It follows the POKER_END_ROUND packet, either
immediatly if the server has no delay between betting rounds
or later if the server waits a few seconds between two betting
rounds.

Example applied to holdem:

         state

         blind     END
BEGIN    preflop   END
BEGIN    flop      END
BEGIN    turn      END
BEGIN    river
         end

game_id: integer uniquely identifying a game.
"""
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerBeginRound, PacketPokerId, "POKER_BEGIN_ROUND", 197) # 0xc5 # %SEQ%

########################################

class PacketPokerCurrentGames(Packet):
    """\
Semantics: "game_ids" contains the the list of games to 
which the client is connected. "count" is the length of
the "game_ids" list.

Direction: client <=> client

Context: inferred when the client receives a POKER_TABLE packet (for
instance, a POKER_TABLE packet is sent to the client when a
POKER_TABLE_JOIN was sent to the server).  The list of game ids
contains the id matching the POKER_TABLE packet that was just
received.

Note to applications embedding the poker-network python library:
When not in the context of a POKER_EXPLAIN server mode,
the packet is also inferred as a side effect of the 
PokerExplain.packetsTableQuit method that is called by the application 
when the user decides to leave the table.

game_ids: integers uniquely identifying a game.
count: length of game_ids.
"""

    info = Packet.info + (
        ('game_ids', [], 'Il'),
        ('count', 0, 'B'),
        )

Packet.infoDeclare(globals(), PacketPokerCurrentGames, Packet, "POKER_CURRENT_GAMES", 198) # 0xc6 # %SEQ%

######################################## Display packet

class PacketPokerEndRoundLast(PacketPokerId):
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerEndRoundLast, PacketPokerId, "POKER_END_ROUND_LAST", 199) # 0xc7 # %SEQ%

######################################## Stop or Start animation

class PacketPokerPythonAnimation(PacketPokerId):

    info = PacketPokerId.info + (
        ('animation', 'none', 's'),
        )
    
Packet.infoDeclare(globals(), PacketPokerPythonAnimation, PacketPokerId, "POKER_PYTHON_ANIMATION", 200) # 0xc8 # %SEQ%

########################################

class PacketPokerSitOutNextTurn(PacketPokerSitOut):
    pass #pragma: no cover

Packet.infoDeclare(globals(), PacketPokerSitOutNextTurn, PacketPokerId, "POKER_SIT_OUT_NEXT_TURN", 201) # 0xc9 # %SEQ%

########################################

class PacketPokerRendererState(Packet):

    info = Packet.info + (
        ('state', 'idle', 's'),
        )
    
Packet.infoDeclare(globals(), PacketPokerRendererState, Packet, "POKER_RENDERER_STATE", 202) # 0xca # %SEQ%

########################################

class PacketPokerChatWord(PacketPokerId):

    info = PacketPokerId.info + (
        ('word', 'no word', 's'),
        )
    
Packet.infoDeclare(globals(), PacketPokerChatWord, PacketPokerId, "POKER_CHAT_WORD", 203) # 0xcb # %SEQ%

########################################

class PacketPokerShowdown(PacketPokerId):

    info = PacketPokerId.info + (
        ('showdown_stack', {}, 'j'),
        )

Packet.infoDeclare(globals(), PacketPokerShowdown, PacketPokerId, "POKER_SHOWDOWN", 204) # 0xcc # %SEQ%

########################################

class PacketPokerClientPlayerChips(Packet):

    info = Packet.info + (
        ('game_id', 0, 'I'),
        ('serial', 0, 'I'),
        ('bet', [], 'c'),
        ('money', [], 'c'),
        )

Packet.infoDeclare(globals(), PacketPokerClientPlayerChips, Packet, "POKER_CLIENT_PLAYER_CHIPS", 205) # 0xcd # %SEQ%

########################################

class PacketPokerInterfaceCommand(Packet):

    info = Packet.info + (
        ('window', None, 'no net'),
        ('command', None, 'no net'),
        )

Packet.infoDeclare(globals(), PacketPokerInterfaceCommand, Packet, "POKER_INTERFACE_COMMAND", 206) # 0xce # %SEQ%

########################################

class PacketPokerPlayerMeLookCards(PacketPokerId):
    """\
Semantics: the player "serial" is looking at his cards
in game "game_id".

Direction: client <=> client

serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""
    info = PacketPokerId.info + (
        ('state', 'UNKNOWN', 's'),
        ('when', 'now', 's'),
        )

Packet.infoDeclare(globals(), PacketPokerPlayerMeLookCards, PacketPokerId, "POKER_PLAYER_ME_LOOK_CARDS", 207) # 0xcf # %SEQ%

########################################

class PacketPokerPlayerMeInFirstPerson(PacketPokerId):

    info = PacketPokerId.info + (
        ('state', 'UNKNOWN', 's'),
        )

Packet.infoDeclare(globals(), PacketPokerPlayerMeInFirstPerson, PacketPokerId, "POKER_PLAYER_ME_IN_FIRST_PERSON", 208) # 0xd0 # %SEQ%

########################################

class PacketPokerAllinShowdown(Packet):
    """\
Semantics: the game "game_id" will automatically go to showdown

Direction: client <=> client

Context: when all players are all-in, the board cards will be
dealt automatically. The POKER_ALLIN_SHOWDOWN packet is created
as soon as such a situation is detected. The client can chose
to behave differently, for instance to postpone the display of
the board cards until after the muck phase of the game.

game_id: integer uniquely identifying a game.
"""
    info = Packet.info + ( ( 'game_id', 0, 'I'), )

Packet.infoDeclare(globals(), PacketPokerAllinShowdown, Packet, "POKER_ALLIN_SHOWDOWN", 209) # 0xd1 # %SEQ%

########################################

class PacketPokerPlayerHandStrength(PacketPokerId):
    """\
Semantics: "hand" is the human-readable description of the best
possible poker hand the player (represented by "serial") can currently
make in current hand being played in game, "game_id".  This
description includes only 'made' poker hands, not draws or potential
hands.  This description will be sent in the the language of the
players currently set locale (see PacketPokerSetLocale()), or "en.US"
if no translation is available.

Direction: client <=> client

Context: inferred on each street.

serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
hand: readable player best hand.
"""

    info = PacketPokerId.info + (
        ('hand', '', 's'),
        )

Packet.infoDeclare(globals(), PacketPokerPlayerHandStrength, PacketPokerId, "POKER_PLAYER_HAND_STRENGTH", 210) # 0xd2 # %SEQ%

_TYPES = range(170,254)

# Interpreted by emacs
# Local Variables:
# compile-command: "perl -pi -e 'if(/%SEQ%/) { $s = 169 if(!defined($s)); $s++; $h = sprintf(q/0x%x/, $s); s/\\d+[) \\w#]+#/$s) # $h #/; }' pokerclientpackets.py"
# End:
