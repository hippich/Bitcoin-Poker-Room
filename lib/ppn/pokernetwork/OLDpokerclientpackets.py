#
# HISTORICAL FILE FOR BACKWARD COMPATIBILITY
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
from pokernetwork.pokerpackets import *

PacketNames = {}
PacketFactory = {}

def chips2amount(chips):
    amount = 0
    for i in xrange(len(chips) / 2):
        amount += chips[i*2] * chips[i*2 + 1]
    return amount

########################################

PACKET_POKER_BEST_CARDS = 170 # 0xaa # %SEQ%
PacketNames[PACKET_POKER_BEST_CARDS] = "POKER_BEST_CARDS"

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

    type = PACKET_POKER_BEST_CARDS

    def __init__(self, *args, **kwargs):
        self.side = kwargs.get("side", "")
        self.hand = kwargs.get("hand", "")
        self.bestcards = kwargs.get("bestcards", [])
        self.board = kwargs.get("board", [])
        self.besthand = kwargs.get("besthand", 0)
        PacketPokerCards.__init__(self, *args, **kwargs)
        
    def __str__(self):
        return PacketPokerCards.__str__(self) + " side = %s, hand = %s, bestcards = %s, board = %s , besthand %s" % ( self.side, self.hand, str(self.bestcards), str(self.board), str(self.besthand) )

PacketFactory[PACKET_POKER_BEST_CARDS] = PacketPokerBestCards

########################################

PACKET_POKER_POT_CHIPS = 171 # 0xab # %SEQ%
PacketNames[PACKET_POKER_POT_CHIPS] = "POKER_POT_CHIPS"

class PacketPokerPotChips(Packet):
    """\
Semantics: the "bet" put in the "index" pot of the "game_id" game.

Direction: client <=> client

Context: this packet is sent at least each time the pot "index" is
updated.

bet: list of pairs ( chip_value, chip_count ).
index: integer uniquely identifying a side pot in the range [0,10[
game_id: integer uniquely identifying a game.
"""

    type = PACKET_POKER_POT_CHIPS

    def __init__(self, **kwargs):
        self.game_id = kwargs.get("game_id", 0)
        self.index = kwargs.get("index", 0)
        self.bet = kwargs.get("bet", [])

    def __str__(self):
        return Packet.__str__(self) + " game_id = %d, pot = %s, index = %d" % ( self.game_id, self.bet, self.index )

PacketFactory[PACKET_POKER_POT_CHIPS] = PacketPokerPotChips

########################################

PACKET_POKER_CLIENT_ACTION = 172 # 0xac # %SEQ%
PacketNames[PACKET_POKER_CLIENT_ACTION] = "POKER_CLIENT_ACTION"

class PacketPokerClientAction(PacketPokerId):
    """

    The action available/not available to the player
    
    """

    type = PACKET_POKER_CLIENT_ACTION

    format = "!B"
    format_size = calcsize(format)

    def __init__(self, *args, **kwargs):
        self.display = kwargs.get("display",0)
        self.action = kwargs.get("action","")
        PacketPokerId.__init__(self, *args, **kwargs)
        
    def pack(self):
        return PacketPokerId.pack(self) + pack(PacketPokerClientAction.format, self.display) + self.packstring(self.action)

    def unpack(self, block):
        block = PacketPokerId.unpack(self, block)
        (self.display,) = unpack(PacketPokerClientAction.format, block[:PacketPokerClientAction.format_size])
        block = block[PacketPokerClientAction.format_size:]
        (block, self.action) = self.unpackstring(block)
        return block

    def calcsize(self):
        return PacketPokerId.calcsize(self) + PacketPokerClientAction.format_size + self.calcsizestring(self.action)

    def __str__(self):
        return PacketPokerId.__str__(self) + " display = %d, action = %s" % ( self.display, self.action )

PacketFactory[PACKET_POKER_CLIENT_ACTION] = PacketPokerClientAction

########################################

PACKET_POKER_BET_LIMIT = 173 # 0xad # %SEQ%
PacketNames[PACKET_POKER_BET_LIMIT] = "POKER_BET_LIMIT"

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

    type = PACKET_POKER_BET_LIMIT

    format = "!IIIIII"
    format_size = calcsize(format)

    def __init__(self, *args, **kwargs):
        self.min = kwargs.get("min",0)
        self.max = kwargs.get("max",0)
        self.step = kwargs.get("step",0)
        self.call = kwargs.get("call",0)
        self.allin = kwargs.get("allin",0)
        self.pot = kwargs.get("pot",0)
        PacketPokerId.__init__(self, *args, **kwargs)

    def pack(self):
        return PacketPokerId.pack(self) + pack(PacketPokerBetLimit.format, self.min, self.max, self.step, self.call, self.allin, self.pot)

    def unpack(self, block):
        block = PacketPokerId.unpack(self, block)
        (self.min, self.max, self.step, self.call, self.allin, self.pot) = unpack(PacketPokerBetLimit.format, block[:PacketPokerBetLimit.format_size])
        return block[PacketPokerBetLimit.format_size:]

    def calcsize(self):
        return PacketPokerId.calcsize(self) + PacketPokerBetLimit.format_size

    def __str__(self):
        return PacketPokerId.__str__(self) + " min = %d, max = %d, step = %s, call = %s, allin = %s, pot = %s" % (self.min, self.max, self.step, self.call, self.allin, self.pot)

PacketFactory[PACKET_POKER_BET_LIMIT] = PacketPokerBetLimit

########################################

PACKET_POKER_SIT_REQUEST = 174 # 0xae # %SEQ%
PacketNames[PACKET_POKER_SIT_REQUEST] = "POKER_SIT_REQUEST"

class PacketPokerSitRequest(PacketPokerSit):

    type = PACKET_POKER_SIT_REQUEST

PacketFactory[PACKET_POKER_SIT_REQUEST] = PacketPokerSitRequest

########################################

PACKET_POKER_PLAYER_NO_CARDS = 175 # 0xaf # %SEQ%
PacketNames[PACKET_POKER_PLAYER_NO_CARDS] = "POKER_PLAYER_NO_CARDS"

class PacketPokerPlayerNoCards(PacketPokerId):
    """\
Semantics: the player "serial" has no cards in game "game_id".

Direction: client <=> client

Context: inferred at showdown.

serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""
    
    type = PACKET_POKER_PLAYER_NO_CARDS

PacketFactory[PACKET_POKER_PLAYER_NO_CARDS] = PacketPokerPlayerNoCards

######################################## 

PACKET_POKER_CHIPS_PLAYER2BET = 176 # 0xb0 # %SEQ%
PacketNames[PACKET_POKER_CHIPS_PLAYER2BET] = "POKER_CHIPS_PLAYER2BET"

class PacketPokerChipsPlayer2Bet(PacketPokerId):
    """\
Semantics: move "chips" from the player "serial" money chip stack
to the bet chip stack.

Direction: client <=> client

chips: 
serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""

    type = PACKET_POKER_CHIPS_PLAYER2BET

    def __init__(self, *args, **kwargs):
        PacketPokerId.__init__(self, *args, **kwargs)
        self.chips = kwargs.get("chips", [])
        
    def __str__(self):
        return PacketPokerId.__str__(self) + " chips = %s" % ( self.chips )

PacketFactory[PACKET_POKER_CHIPS_PLAYER2BET] = PacketPokerChipsPlayer2Bet

######################################## 

PACKET_POKER_CHIPS_BET2POT = 177 # 0xb1 # %SEQ%
PacketNames[PACKET_POKER_CHIPS_BET2POT] = "POKER_CHIPS_BET2POT"

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

    type = PACKET_POKER_CHIPS_BET2POT

    def __init__(self, *args, **kwargs):
        PacketPokerId.__init__(self, *args, **kwargs)
        self.chips = kwargs.get("chips", [])
        self.pot = kwargs.get("pot", -1)
        
    def __str__(self):
        return PacketPokerId.__str__(self) + " chips = %s, pot = %d" % ( self.chips, self.pot )
    
PacketFactory[PACKET_POKER_CHIPS_BET2POT] = PacketPokerChipsBet2Pot

######################################## Display packet

PACKET_POKER_CHIPS_POT2PLAYER = 178 # 0xb2 # %SEQ%
PacketNames[PACKET_POKER_CHIPS_POT2PLAYER] = "POKER_CHIPS_POT2PLAYER"

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

    type = PACKET_POKER_CHIPS_POT2PLAYER

    def __init__(self, *args, **kwargs):
        PacketPokerId.__init__(self, *args, **kwargs)
        self.chips = kwargs.get("chips", [])
        self.pot = kwargs.get("pot", -1)
        self.reason = kwargs.get("reason", "")
        
    def __str__(self):
        return PacketPokerId.__str__(self) + " chips = %s, pot = %d, reason = %s" % ( self.chips, self.pot, self.reason )
    
PacketFactory[PACKET_POKER_CHIPS_POT2PLAYER] = PacketPokerChipsPot2Player

######################################## Display packet

PACKET_POKER_CHIPS_POT_MERGE = 179 # 0xb3 # %SEQ%
PacketNames[PACKET_POKER_CHIPS_POT_MERGE] = "POKER_CHIPS_POT_MERGE"

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

    type = PACKET_POKER_CHIPS_POT_MERGE

    def __init__(self, *args, **kwargs):
        PacketPokerId.__init__(self, *args, **kwargs)
        self.sources = kwargs.get("sources", [])
        self.destination = kwargs.get("destination", 0)
        
    def __str__(self):
        return PacketPokerId.__str__(self) + " sources = %s, destination = %d" % ( self.sources, self.destination )

PacketFactory[PACKET_POKER_CHIPS_POT_MERGE] = PacketPokerChipsPotMerge

######################################## Display packet

PACKET_POKER_CHIPS_POT_RESET = 180 # 0xb4 # %SEQ%
PacketNames[PACKET_POKER_CHIPS_POT_RESET] = "POKER_CHIPS_POT_RESET"

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
    
    type = PACKET_POKER_CHIPS_POT_RESET

PacketFactory[PACKET_POKER_CHIPS_POT_RESET] = PacketPokerChipsPotReset

######################################## Display packet

PACKET_POKER_CHIPS_BET2PLAYER = 181 # 0xb5 # %SEQ%
PacketNames[PACKET_POKER_CHIPS_BET2PLAYER] = "POKER_CHIPS_BET2PLAYER"

class PacketPokerChipsBet2player(PacketPokerChipsPlayer2Bet):
    """chips move from bet to player"""

    type = PACKET_POKER_CHIPS_BET2PLAYER

PacketFactory[PACKET_POKER_CHIPS_BET2PLAYER] = PacketPokerChipsBet2player

######################################## Display packet

PACKET_POKER_END_ROUND = 182 # 0xb6 # %SEQ%
PacketNames[PACKET_POKER_END_ROUND] = "POKER_END_ROUND"

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
    
    type = PACKET_POKER_END_ROUND

PacketFactory[PACKET_POKER_END_ROUND] = PacketPokerEndRound

########################################

PACKET_POKER_DISPLAY_NODE = 183 # 0xb7 # %SEQ%
PacketNames[PACKET_POKER_DISPLAY_NODE] = "POKER_DISPLAY_NODE"

class PacketPokerDisplayNode(Packet):
    """request POKER_DISPLAY_NODE packet"""
    
    type = PACKET_POKER_DISPLAY_NODE

    def __init__(self, **kwargs):
        self.game_id = kwargs.get("game_id", 0)
        self.name = kwargs.get("name", "")
        self.state = kwargs.get("state", 0)
        self.style = kwargs.get("style", "")
        self.selection = kwargs.get("selection", None)

    def __str__(self):
        return Packet.__str__(self) + "game_id = %s, name = %s, state = %d, style = %s, selection = %s " % ( str(self.game_id), self.name, self.state, self.style, self.selection )

PacketFactory[PACKET_POKER_DISPLAY_NODE] = PacketPokerDisplayNode

######################################## Display packet

PACKET_POKER_DEAL_CARDS = 184 # 0xb8 # %SEQ%
PacketNames[PACKET_POKER_DEAL_CARDS] = "POKER_DEAL_CARDS"

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

    type = PACKET_POKER_DEAL_CARDS
    numberOfCards = 0
    serials = []

    def __init__(self, *args, **kwargs):
        self.numberOfCards = kwargs.get("numberOfCards", 2)
        self.serials = kwargs.get("serials", [])
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return PacketPokerId.__str__(self) + " number of cards = %d, serials = %s" % ( self.numberOfCards, self.serials )

PacketFactory[PACKET_POKER_DEAL_CARDS] = PacketPokerDealCards

########################################

PACKET_POKER_CHAT_HISTORY = 185 # 0xb9 # %SEQ%
PacketNames[PACKET_POKER_CHAT_HISTORY] = "POKER_CHAT_HISTORY"

class PacketPokerChatHistory(Packet):
    """chat history show"""

    type = PACKET_POKER_CHAT_HISTORY

    def __init__(self, **kwargs):
        self.show = kwargs.get("show", "no")

PacketFactory[PACKET_POKER_CHAT_HISTORY] = PacketPokerChatHistory


########################################

PACKET_POKER_DISPLAY_CARD = 186 # 0xba # %SEQ%
PacketNames[PACKET_POKER_DISPLAY_CARD] = "POKER_DISPLAY_CARD"

class PacketPokerDisplayCard(PacketPokerId):
    """Hide a player card"""

    type = PACKET_POKER_DISPLAY_CARD
    index = []
    display = 0

    def __init__(self, *args, **kwargs):
        PacketPokerId.__init__(self, *args, **kwargs)
        self.index = kwargs.get("index", [] )
        self.display = kwargs.get("display", 0 )

PacketFactory[PACKET_POKER_DISPLAY_CARD] = PacketPokerDisplayCard

########################################

PACKET_POKER_SELF_IN_POSITION = 187 # 0xbb # %SEQ%
PacketNames[PACKET_POKER_SELF_IN_POSITION] = "POKER_SELF_IN_POSITION"

class PacketPokerSelfInPosition(PacketPokerPosition):
    """\
Semantics: the player authenticated for this connection
is in position. Otherwise identical to PACKET_POKER_POSITION.

"""

    type = PACKET_POKER_SELF_IN_POSITION

PacketFactory[PACKET_POKER_SELF_IN_POSITION] = PacketPokerSelfInPosition

########################################

PACKET_POKER_SELF_LOST_POSITION = 188 # 0xbc # %SEQ%
PacketNames[PACKET_POKER_SELF_LOST_POSITION] = "POKER_SELF_LOST_POSITION"

class PacketPokerSelfLostPosition(PacketPokerPosition):
    """\
Semantics: the player authenticated for this connection
is in position. Otherwise identical to PACKET_POKER_POSITION.

"""

    type = PACKET_POKER_SELF_LOST_POSITION

PacketFactory[PACKET_POKER_SELF_LOST_POSITION] = PacketPokerSelfLostPosition

########################################

PACKET_POKER_HIGHEST_BET_INCREASE = 189 # 0xbd # %SEQ%
PacketNames[PACKET_POKER_HIGHEST_BET_INCREASE] = "POKER_HIGHEST_BET_INCREASE"

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
    
    type = PACKET_POKER_HIGHEST_BET_INCREASE

PacketFactory[PACKET_POKER_HIGHEST_BET_INCREASE] = PacketPokerHighestBetIncrease

########################################

PACKET_POKER_PLAYER_WIN = 190 # 0xbe # %SEQ%
PacketNames[PACKET_POKER_PLAYER_WIN] = "POKER_PLAYER_WIN"

class PacketPokerPlayerWin(PacketPokerId):
    """\
Semantics: the player "serial" win.

Direction: client <=> client

Context: when a PacketPokerWin arrive from server. The packet is generated
from PACKET_PLAYER_WIN. For each player that wins something a packet
PlayerWin is generated.

serial: integer uniquely identifying a player.
"""
    type = PACKET_POKER_PLAYER_WIN

PacketFactory[PACKET_POKER_PLAYER_WIN] = PacketPokerPlayerWin

########################################
PACKET_POKER_ANIMATION_PLAYER_NOISE = 191 # 0xbf # %SEQ%
PacketNames[PACKET_POKER_ANIMATION_PLAYER_NOISE] = "POKER_ANIMATION_PLAYER_NOISE"

class PacketPokerAnimationPlayerNoise(PacketPokerId):
    """\
Semantics: the player "serial" play or stop noise animation.

Direction: client <=> client

Context: a PacketPokerPlayerNoise is send to the client c++ to stop or start
player's noise animation.

serial: integer uniquely identifying a player.
action: string that contain "start" or "stop".
"""
    type = PACKET_POKER_ANIMATION_PLAYER_NOISE

    def __init__(self, *args, **kwargs):
        self.action = kwargs.get("action", 'start')
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return Packet.__str__(self) + " serial = %d, action = %s" % ( self.serial, self.action )
    
PacketFactory[PACKET_POKER_ANIMATION_PLAYER_NOISE] = PacketPokerAnimationPlayerNoise

########################################

PACKET_POKER_ANIMATION_PLAYER_FOLD = 192 # 0xc0 # %SEQ%
PacketNames[PACKET_POKER_ANIMATION_PLAYER_FOLD] = "POKER_ANIMATION_PLAYER_FOLD"

class PacketPokerAnimationPlayerFold(PacketPokerId):
    """\
Semantics: the player "serial" play an animation fold.

Direction: client <=> client

Context: a PacketPokerPlayerNoise is send to the client c++ to stop or start
player's noise animation.

serial: integer uniquely identifying a player.
animation: string used to select an animation fold.
"""
    type = PACKET_POKER_ANIMATION_PLAYER_FOLD

    def __init__(self, *args, **kwargs):
        self.animation = kwargs.get("animation","UNKNOWN")
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return PacketPokerId.__str__(self) + " serial = %d, animation fold = %s" % ( self.serial, self.animation )
    
PacketFactory[PACKET_POKER_ANIMATION_PLAYER_FOLD] = PacketPokerAnimationPlayerFold

########################################

PACKET_POKER_ANIMATION_PLAYER_BET = 193 # 0xc1 # %SEQ%
PacketNames[PACKET_POKER_ANIMATION_PLAYER_BET] = "POKER_ANIMATION_PLAYER_BET"

class PacketPokerAnimationPlayerBet(PacketPokerId):
    """\
"""
    type = PACKET_POKER_ANIMATION_PLAYER_BET

    def __init__(self, *args, **kwargs):
        self.animation = kwargs.get("animation", "")
        self.chips = kwargs.get("chips", [])
        self.amount = chips2amount(self.chips)
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return PacketPokerId.__str__(self) + " serial = %d, chips %s , animation %s" % ( self.serial ,self.animation, self.chips )
    
PacketFactory[PACKET_POKER_ANIMATION_PLAYER_BET] = PacketPokerAnimationPlayerBet

########################################

PACKET_POKER_ANIMATION_PLAYER_CHIPS = 194 # 0xc2 # %SEQ%
PacketNames[PACKET_POKER_ANIMATION_PLAYER_CHIPS] = "POKER_ANIMATION_PLAYER_CHIPS"

class PacketPokerAnimationPlayerChips(PacketPokerId):
    """\
"""
    type = PACKET_POKER_ANIMATION_PLAYER_CHIPS

    def __init__(self, *args, **kwargs):
        self.animation = kwargs.get("animation", "")
        self.chips = kwargs.get("chips", [])
        self.state = kwargs.get("state", "")
        self.amount = chips2amount(self.chips)
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return PacketPokerId.__str__(self) + " serial = %d, chips %s , animation %s" % ( self.serial ,self.animation, self.chips )
    
PacketFactory[PACKET_POKER_ANIMATION_PLAYER_CHIPS] = PacketPokerAnimationPlayerChips

########################################

PACKET_POKER_ANIMATION_DEALER_CHANGE = 195 # 0xc3 # %SEQ%
PacketNames[PACKET_POKER_ANIMATION_DEALER_CHANGE] = "POKER_ANIMATION_DEALER_CHANGE"

class PacketPokerAnimationDealerChange(PacketPokerId):
    """\
"""
    type = PACKET_POKER_ANIMATION_DEALER_CHANGE

    def __init__(self, *args, **kwargs):
        self.state = kwargs.get("state","UNKNOWN")
        
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return PacketPokerId.__str__(self) + " serial = %d, state %s" % ( self.serial , self.state )
    
PacketFactory[PACKET_POKER_ANIMATION_DEALER_CHANGE] = PacketPokerAnimationDealerChange

########################################

PACKET_POKER_ANIMATION_DEALER_BUTTON = 196 # 0xc4 # %SEQ%
PacketNames[PACKET_POKER_ANIMATION_DEALER_BUTTON] = "POKER_ANIMATION_DEALER_BUTTON"

class PacketPokerAnimationDealerButton(PacketPokerId):
    """\
"""
    type = PACKET_POKER_ANIMATION_DEALER_BUTTON

    def __init__(self, *args, **kwargs):
        self.state = kwargs.get("state","UNKNOWN")
        
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return PacketPokerId.__str__(self) + " serial = %d, state %s" % ( self.serial , self.state )
    
PacketFactory[PACKET_POKER_ANIMATION_DEALER_BUTTON] = PacketPokerAnimationDealerButton

########################################

PACKET_POKER_BEGIN_ROUND = 197 # 0xc5 # %SEQ%
PacketNames[PACKET_POKER_BEGIN_ROUND] = "POKER_BEGIN_ROUND"

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
    
    type = PACKET_POKER_BEGIN_ROUND

PacketFactory[PACKET_POKER_BEGIN_ROUND] = PacketPokerBeginRound

########################################

PACKET_POKER_CURRENT_GAMES = 198 # 0xc6 # %SEQ%
PacketNames[PACKET_POKER_CURRENT_GAMES] = "POKER_CURRENT_GAMES"

class PacketPokerCurrentGames(Packet):

    type = PACKET_POKER_CURRENT_GAMES

    format = "!B"
    format_size = calcsize(format)
    format_element = "!I"

    def __init__(self, **kwargs):
        self.game_ids = kwargs.get("game_ids", [])
        self.count = kwargs.get("count", 0)

    def pack(self):
        return Packet.pack(self) + self.packlist(self.game_ids, PacketPokerCurrentGames.format_element) + pack(PacketPokerCurrentGames.format, self.count)
        
    def unpack(self, block):
        block = Packet.unpack(self, block)
        (block, self.game_ids) = self.unpacklist(block, PacketPokerCurrentGames.format_element)
        (self.count,) = unpack(PacketPokerCurrentGames.format, block[:PacketPokerCurrentGames.format_size])
        return block[PacketPokerCurrentGames.format_size:]

    def calcsize(self):
        return Packet.calcsize(self) + self.calcsizelist(self.game_ids, PacketPokerCurrentGames.format_element) + PacketPokerCurrentGames.format_size

    def __str__(self):
        return Packet.__str__(self) + " count = %d, game_ids = %s" % ( self.count, self.game_ids )

PacketFactory[PACKET_POKER_CURRENT_GAMES] = PacketPokerCurrentGames

######################################## Display packet

PACKET_POKER_END_ROUND_LAST = 199 # 0xc7 # %SEQ%
PacketNames[PACKET_POKER_END_ROUND_LAST] = "POKER_END_ROUND_LAST"

class PacketPokerEndRoundLast(PacketPokerId):
    
    type = PACKET_POKER_END_ROUND_LAST

PacketFactory[PACKET_POKER_END_ROUND_LAST] = PacketPokerEndRoundLast

######################################## Stop or Start animation

PACKET_POKER_PYTHON_ANIMATION = 200 # 0xc8 # %SEQ%
PacketNames[PACKET_POKER_PYTHON_ANIMATION] = "POKER_PYTHON_ANIMATION"

class PacketPokerPythonAnimation(PacketPokerId):
    
    type = PACKET_POKER_PYTHON_ANIMATION

    def __init__(self, *args, **kwargs):
        self.animation =  kwargs.get("animation", "none")
        
        PacketPokerId.__init__(self, *args, **kwargs)

PacketFactory[PACKET_POKER_PYTHON_ANIMATION] = PacketPokerPythonAnimation

########################################

PACKET_POKER_SIT_OUT_NEXT_TURN = 201 # 0xc9 # %SEQ%
PacketNames[PACKET_POKER_SIT_OUT_NEXT_TURN] = "POKER_SIT_OUT_NEXT_TURN"

class PacketPokerSitOutNextTurn(PacketPokerSitOut):

    type = PACKET_POKER_SIT_OUT_NEXT_TURN

PacketFactory[PACKET_POKER_SIT_OUT_NEXT_TURN] = PacketPokerSitOutNextTurn

########################################

PACKET_POKER_RENDERER_STATE = 202 # 0xca # %SEQ%
PacketNames[PACKET_POKER_RENDERER_STATE] = "POKER_RENDERER_STATE"

class PacketPokerRendererState(Packet):

    type = PACKET_POKER_RENDERER_STATE

    def __init__(self, **kwargs):
        self.state =  kwargs.get("state", "idle")

PacketFactory[PACKET_POKER_RENDERER_STATE] = PacketPokerRendererState

########################################

PACKET_POKER_CHAT_WORD = 203 # 0xcb # %SEQ%
PacketNames[PACKET_POKER_CHAT_WORD] = "POKER_CHAT_WORD"

class PacketPokerChatWord(PacketPokerId):
    type = PACKET_POKER_CHAT_WORD

    def __init__(self, *args, **kwargs):
        self.word = kwargs.get("word", "no word")
        PacketPokerId.__init__(self, *args, **kwargs)

PacketFactory[PACKET_POKER_CHAT_WORD] = PacketPokerChatWord

########################################

PACKET_POKER_SHOWDOWN = 204 # 0xcc # %SEQ%
PacketNames[PACKET_POKER_SHOWDOWN] = "POKER_SHOWDOWN"

class PacketPokerShowdown(PacketPokerId):
    type = PACKET_POKER_SHOWDOWN

    def __init__(self, *args, **kwargs):
        self.showdown_stack = kwargs.get("showdown_stack", {})
        PacketPokerId.__init__(self, *args, **kwargs)

    def __str__(self):
        return PacketPokerId.__str__(self) + " showdown_stack = %s" % self.showdown_stack

PacketFactory[PACKET_POKER_SHOWDOWN] = PacketPokerShowdown

########################################

PACKET_POKER_CLIENT_PLAYER_CHIPS = 205 # 0xcd # %SEQ%
PacketNames[PACKET_POKER_CLIENT_PLAYER_CHIPS] = "POKER_CLIENT_PLAYER_CHIPS"

class PacketPokerClientPlayerChips(Packet):
    type = PACKET_POKER_CLIENT_PLAYER_CHIPS

    def __init__(self, **kwargs):
        self.game_id = kwargs.get("game_id", 0)
        self.serial = kwargs.get("serial", 0)
        self.bet = kwargs.get("bet", [])
        self.money = kwargs.get("money", [])

    def __str__(self):
        return Packet.__str__(self) + " game_id = %d, serial = %d, bet = %s, money = %s" % ( self.game_id, self.serial, self.bet, self.money )

PacketFactory[PACKET_POKER_CLIENT_PLAYER_CHIPS] = PacketPokerClientPlayerChips

########################################

PACKET_POKER_INTERFACE_COMMAND = 206 # 0xce # %SEQ%
PacketNames[PACKET_POKER_INTERFACE_COMMAND] = "POKER_INTERFACE_COMMAND"

class PacketPokerInterfaceCommand(Packet):
    type = PACKET_POKER_INTERFACE_COMMAND

    def __init__(self, **kwargs):
        self.window = kwargs.get("window", None)
        self.command = kwargs.get("command", None)

    def __str__(self):
        return Packet.__str__(self) + " window = %s, command = %s" % ( self.window, self.command )

PacketFactory[PACKET_POKER_INTERFACE_COMMAND] = PacketPokerInterfaceCommand


########################################
PACKET_POKER_PLAYER_ME_LOOK_CARDS = 207 # 0xcf # %SEQ%
PacketNames[PACKET_POKER_PLAYER_ME_LOOK_CARDS] = "POKER_PLAYER_ME_LOOK_CARDS"

class PacketPokerPlayerMeLookCards(PacketPokerId):
    """\
Semantics: the player "serial" is looking at his cards
in game "game_id".

Direction: client <=> client

serial: integer uniquely identifying a player.
game_id: integer uniquely identifying a game.
"""

    def __init__(self, *args, **kwargs):
        self.state = kwargs.get("state","UNKNOWN")
        self.when = kwargs.get("when", "now")
        PacketPokerId.__init__(self, *args, **kwargs)

    type = PACKET_POKER_PLAYER_ME_LOOK_CARDS

    def __str__(self):
        return PacketPokerId.__str__(self) + " state = %s" % ( self.state )

PacketFactory[PACKET_POKER_PLAYER_ME_LOOK_CARDS] = PacketPokerPlayerMeLookCards

########################################

PACKET_POKER_PLAYER_ME_IN_FIRST_PERSON = 208 # 0xd0 # %SEQ%
PacketNames[PACKET_POKER_PLAYER_ME_IN_FIRST_PERSON] = "POKER_PLAYER_ME_IN_FIRST_PERSON"

class PacketPokerPlayerMeInFirstPerson(PacketPokerId):
    def __init__(self, *args, **kwargs):
        self.state = kwargs.get("state","UNKNOWN")
        PacketPokerId.__init__(self, *args, **kwargs)

    type = PACKET_POKER_PLAYER_ME_IN_FIRST_PERSON

    def __str__(self):
        return PacketPokerId.__str__(self) + " state = %s" % ( self.state )

PacketFactory[PACKET_POKER_PLAYER_ME_IN_FIRST_PERSON] = PacketPokerPlayerMeInFirstPerson

_TYPES = range(170,254)

# Interpreted by emacs
# Local Variables:
# compile-command: "perl -pi -e 'if(/%SEQ%/) { $s = 169 if(!defined($s)); $s++; $h = sprintf(q/0x%x/, $s); s/\\d+[ \\w#]+#/$s # $h #/; }' pokerclientpackets.py"
# End:
