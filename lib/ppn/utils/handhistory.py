#!/usr/bin/env python
# coding: utf-8

from collections import deque, namedtuple
from decimal import Decimal
import functools
import itertools
import re
import sys
import time

import pokerengine.pokercards
from pokernetwork.pokerdatabase import PokerDatabase
from pokernetwork.pokerservice import PokerService
from pokernetwork.pokernetworkconfig import Config
from pokernetwork.pokerserver import DEFAULT_CONFIG_PATH


class Limit:
    FIXED_LIMIT = 'Limit'
    POT_LIMIT = 'Pot Limit'
    NO_LIMIT = 'No Limit'


class Variant:
    HOLDEM = "Hold'em"
    OMAHA = 'Omaha'
    OMAHA_8 = 'Omaha Hi/Lo'


_CardIdentifier = namedtuple('CardIdentifier', ['name', 'abbreviation'])


class Rank(namedtuple('Rank', ['name', 'abbreviation'])):
    __slots__ = ()

    def __str__(self):
        return self.name


class Suit(namedtuple('Suit', ['name', 'abbreviation'])):
    __slots__ = ()


_Card = namedtuple('Card', ['rank', 'suit'])


class Card(_Card):
    __slots__ = ()

    def __str__(self):
        return '{0}{1}'.format(self.rank.abbreviation, self.suit.abbreviation)


class Upcard(Card):
    __slots__ = ()
    is_faceup = True


class Downcard(Card):
    __slots__ = ()
    is_faceup = False


RankAce = Rank('Ace', 'A')
RankKing = Rank('King', 'K')
RankQueen = Rank('Queen', 'Q')
RankJack = Rank('Jack', 'J')
RankTen = Rank('Ten', 'T')
RankNine = Rank('Nine', '9')
RankEight = Rank('Eight', '8')
RankSeven = Rank('Seven', '7')
RankSix = Rank('Six', '6')
RankFive = Rank('Five', '5')
RankFour = Rank('Four', '4')
RankThree = Rank('Three', '3')
RankTwo = Rank('Two', '2')

SuitClubs = Suit('clubs', 'c')
SuitDiamonds = Suit('diamonds', 'd')
SuitHearts = Suit('hearts', 'h')
SuitSpades = Suit('spades', 's')

BettingStructure = namedtuple('BettingStructure', ['limit', 'small_blind',
                                                   'big_blind'])

Player = namedtuple('Player', ['player_id', 'name', 'seat_number', 'chips'])

BestHands = namedtuple('BestHands', ['high', 'low'])

ResolvedPot = namedtuple('ResolvedPot', ['pot_amount', 'eligible_players',
                                         'winners'])

_Hand = namedtuple('Hand', ['cards', 'pokereval_ranking'])


class Hand(_Hand):
    __slots__ = ()


class HighHand(Hand):
    __slots__ = ()

    def is_better_than(self, other_hand):
        return self.pokereval_ranking > other_hand.pokereval_ranking

    def is_worse_than(self, other_hand):
        return not self.is_better_than(other_hand)

    def __eq__(self, other_hand):
        return self.pokereval_ranking == other_hand.pokereval_ranking

    def __ne__(self, other_hand):
        return not self == other_hand


class StraightFlush(HighHand):
    def __str__(self):
        if self.cards[0].rank == RankAce:
            return 'a Royal Flush'
        else:
            return 'a straight flush, {low_rank} to {high_rank}'.format(
                low_rank=self.cards[4].rank.name,
                high_rank=self.cards[0].rank.name)


class FourOfAKind(HighHand):
    def __str__(self):
        return 'four of a kind, {0}s'.format(self.cards[0].rank.name)


class FullHouse(HighHand):
    def __str__(self):
        return 'a full house, {0}s full of {0}s'.format(
            rank_one=self.cards[0].rank.name, rank_two=self.cards[3].rank.name)


class Flush(HighHand):
    def __str__(self):
        return 'a flush, {0} high'.format(self.cards[0].rank.name)


class Straight(HighHand):
    def __str__(self):
        return 'a straight, {low_rank} to {high_rank}'.format(
            low_rank=self.cards[4].rank.name,
            high_rank=self.cards[0].rank.name)


class ThreeOfAKind(HighHand):
    def __str__(self):
        return 'three of a kind, {1}s'.format(self.cards[0].rank.name)


class TwoPair(HighHand):
    def __str__(self):
        return 'two pair, {0}s and {1}s'.format(self.cards[0].rank.name,
                                                self.cards[2].rank.name)


class OnePair(HighHand):
    def __str__(self):
        return 'a pair of {0}s'.format(self.cards[0].rank.name)


class HighCard(HighHand):
    def __str__(self):
        return 'high card {0}'.format(self.cards[0].rank.name)


class LowHand(Hand):
    def is_better_than(self, other_hand):
        return self.pokereval_ranking < other_hand.pokereval_ranking

    def is_worse_than(self, other_hand):
        return not self.is_better_than(other_hand)

    def __eq__(self, other_low_hand):
        return self.pokereval_ranking == other_low_hand.pokereval_ranking

    def __ne__(self, other_low_hand):
        return not self == other_low_hand

    def __str__(self):
        return ','.join(card.rank.abbreviation for card in self.cards)



_HandHistory = namedtuple('HandHistory', ['hand_id', 'hand_timestamp',
                                          'variant', 'betting_structure',
                                          'table', 'players', 'button_seat',
                                          'currency', 'chip_scale_factor',
                                          'hand_events'])

PokerEngineHand = namedtuple('PokerEngineHand', ['hand_description',
                                                 'hand_timestamp',
                                                 'player_names'])

GameEvent = namedtuple('GameEvent', ['level', 'hand_id', 'hands_count',
                                     'hand_timestamp', 'variant',
                                     'betting_structure', 'players',
                                     'button_seat', 'player_chips'])

RoundEvent = namedtuple('RoundEvent', ['round_name', 'community_cards',
                                       'dealt_cards'])

BlindEvent = namedtuple('BlindEvent', ['player_id', 'blind_amount',
                                       'dead_amount'])

AnteEvent = namedtuple('AnteEvent', ['player_id', 'ante_amount'])

AllInEvent = namedtuple('AllInEvent', ['player_id'])

CallEvent = namedtuple('CallEvent', ['player_id', 'call_amount'])

CheckEvent = namedtuple('CheckEvent', ['player_id'])

FoldEvent = namedtuple('FoldEvent', ['player_id'])

RaiseEvent = namedtuple('RaiseEvent', ['player_id', 'raise_to_amount',
                                       'pay_amount', 'raise_by_amount'])

ShowdownEvent = namedtuple('ShowdownEvent', ['community_cards', 'player_cards'])

CanceledEvent = namedtuple('CanceledEvent', ['player_id', 'returned_amount'])

EndEvent = namedtuple('EndEvent', ['winners', 'showdown_stack'])


POKEREVAL_SUIT_ADAPTER_LOOKUP = {
    0: SuitHearts,
    1: SuitDiamonds,
    2: SuitClubs,
    3: SuitSpades
}

POKEREVAL_RANK_ADAPTER_LOOKUP = {
    0: RankTwo,
    1: RankThree,
    2: RankFour,
    3: RankFive,
    4: RankSix,
    5: RankSeven,
    6: RankEight,
    7: RankNine,
    8: RankTen,
    9: RankJack,
    10: RankQueen,
    11: RankKing,
    12: RankAce
}

def pokercards_adapter(pokercards):
    if isinstance(pokercards, pokerengine.pokercards.PokerCards):
        return [pokereval_card_adapter(pokercard)
                for pokercard in pokercards.cards
                if pokercard != pokerengine.pokercards.PokerCards.NOCARD]
    else:
        return [pokereval_card_adapter(pokercard) for pokercard in pokercards]


def pokereval_card_adapter(pokercard):
    """
    Converts pokercard into an Upcard or Downcard.

    PokerEval maps integers to cards as follows (see
    pypokereval/pokereval.py):

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
    """
    def card_index(card):
        return pokerengine.pokercards.visible_card(pokercard)

    card_index = card_index(pokercard)

    rank = POKEREVAL_RANK_ADAPTER_LOOKUP[card_index % 13]
    suit = POKEREVAL_SUIT_ADAPTER_LOOKUP[card_index / 13]

    if pokerengine.pokercards.is_visible(pokercard):
        return Upcard(rank, suit)
    else:
        return Downcard(rank, suit)


POKEREVAL_HAND_ADAPTER_LOOKUP = {
    'Nothing': LowHand,
    'NoPair': HighCard,
    'TwoPair': TwoPair,
    'Trips': ThreeOfAKind,
    'Straight': Straight,
    'Flush': Flush,
    'FlHouse': FullHouse,
    'Quads': FourOfAKind,
    'StFlush': StraightFlush
}

def pokereval_best_hand_adapter(pokereval_hand):
    """
    `pokereval_hand`: list

    The first element is the numerical value of the hand (better
    hands have higher values if "side" is "hi" and lower values if
    "side" is "low"). The second element is a list whose first
    element is the strength of the hand among the following:

    Nothing (only if "side" equals "low")
    NoPair
    TwoPair
    Trips
    Straight
    Flush
    FlHouse
    Quads
    StFlush

    The last five elements are numbers describing the best hand
    properly sorted (for instance the ace is at the end for no pair
    if "side" is low or at the beginning if "side" high).

    Examples:

    [134414336, ['StFlush', 29, 28, 27, 26, 38]] is the wheel five to ace, clubs
    [475920, ['NoPair', 45, 29, 41, 39, 51]] is As, 8s, 5c, 4s, 2s
    [268435455, ['Nothing']] means there is no qualifying low
    """
    cards = pokercards_adapter(pokereval_hand[1][1:])
    if not cards:
        return None

    pokereval_ranking = pokereval_hand[0]
    hand_category = pokereval_hand[1][0]
    return POKEREVAL_HAND_ADAPTER_LOOKUP[hand_category](cards,
                                                        pokereval_ranking)


class Context(object):
    pass


class Generator(object):
    def event_handler(self, event):
        return 'handle_' + event.__class__.__name__

    def generate_from_event(self, event, context=None):
        try:
            handler = self.event_handler(event)
            generator = getattr(self, handler)(event, context)
            return generator if generator else ()
        except AttributeError:
            return ()

    def generate(self, events, context=None):
        if not context:
            context = Context()
        return (generated
                for event in events
                for generated in self.generate_from_event(event, context))


class PokerEngineEventGenerator(Generator):
    """
    Each pokerengine event is represented as a tuple. The first element in each
    event tuple is a string that indicates the event type.

    Event types:
    - 'game': corresponds to the start of a hand.
        ('game', level, hand_serial, hands_count, utc_timestamp, variant,
         betting_structure, players, button_seat, serial2chips,
         game_info)

        `level`: integer
            The tournament level or 0 if the game is not a tournament.

        `hand_serial`: integer
            Unique hand identifier.

        `hands_count`: integer
            The number of hands that were played at the table; used for
            statistical purposes.

        `utc_timestamp`: integer
            UNIX timestamp (seconds since epoch) when the hand was started.

        `variant`: string
            The game variant. Possible values:
                - 'holdem'
                - 'omaha'
                - 'omaha8'
                - '7stud'
                - 'razz'

        `betting_structure`: string
            Has the following format: '{small_bet}-{big_bet}-{limit}'
                small_bet: integer or decimal string
                big_bet: integer or decimal string
                limit: string
                    Possible values:
                        - 'limit'
                        - 'no-limit'
                        - 'pot-limit'

        `players`: list of integers
            List of player ids of players seated at the table at the start
            of the hand (before any forced bets).

        `button_seat`: integer
            Button seat number (indexed from 0).

        `serial2chips`: dict mapping integer to integer.
            Maps a player id to the amount of chips the player has.

        `game_info`: dict
            Additional game information.

            Contains the following keys:
                `currency`: string
                    Currency code of the currency being used.

                `chip_scale_factor`: integer
                    Used to convert between units of chips and currency. In
                    a tournament or play money game, `chip_scale_factor` is
                    typically 1. In a cash game, `chip_scale_factor` is
                    typically 100 (100 chips = 1 USD).

                `small_bet`: integer
                    The small bet (or small blind) in units of chips.

                `big_bet`: integer
                    The big bet (or big blind) in units of chips.

                `table`: string
                    Table identifier; typically the table name.

                `num_seats`: integer
                    The total number of seats at the table.

                `button_seat`: integer
                    The seat number of the button.

                `players`: list of dicts
                    List of player dictionaries corresponding to players
                    involved in the hand. Each player dictionary has the
                    following keys:

                        `name`: string
                            Unique player identifier.

                        `chips`: integer
                            The amount of chips the player has at the start
                            of the hand.

                        `seat`: integer
                            The player's seat number.

        Example:

            ('game', 0, 170, 0, 1314572444, 'holdem', '.10-.25-no-limit',
             [22, 23], 0, {22: 1250, 23: 1250})


    - 'round': corresponds to the start of a betting round.
        ('round', round_name, board, pockets)

        `round_name`: string
            Possible values:
                - 'blindAnte'
                - 'pre-flop'
                - 'flop'
                - 'turn'
                - 'river'
                - 'third'
                - 'fourth'
                - 'fifth'

        `board`: pokerengine.PokerCards object, or None if the game variant
                 does not use community cards.

        `pockets`: dict mapping player ids to pokerengine.PokerCards objects
                   (holecards), or None if no cards were dealt to players.

        Examples:

            ('round', 'pre-flop', PokerCards([]),
             {22: PokerCards([210, 208]), 23: PokerCards([228, 215])})

            ('round', 'flop', PokerCards([7, 49, 14]), None)


    - 'position': corresponds to a player's turn to act.
        ('position', index)

        `index`: 0-based index into the `serials` list of the 'game_state'
                 event (the id of the player whose turn it is to act), or -1
                 to indicate the end of a betting round.

        Examples:

            ('position', 0)

            ('position', -1)


    - 'blind': a player posted a blind
        ('blind', player_id, amount, dead)

        `player_id`: integer
            The id of the player that posted the blind.

        `amount`: integer
            Blind amount in chips.

        `dead`: integer
            Dead blind amount in chips.

        Example:

            ('blind', 22, 12, 0)


    - 'ante': a player posted an ante
        ('ante', player_id, amount)

        `player_id`: integer
            The id of the player that posted the blind.

        `amount`: integer
            Blind amount in chips.

        Example:

            ('ante', 22, 2)


    - 'all-in': a player went all-in
        ('all-in', player_id)

        `player_id`: integer
            The id of the player that went all-in.

        The 'all-in' event occurs immediately after a player action
        event of type: 'call', 'raise', 'blind', or 'ante'.

        Example:

            # player with id of 22 calls a raise and is all-in
            ('call', 22, 100)
            ('all-in', 22)


    - 'call': a player called
        ('call', player_id, amount)

        `player_id`: integer
            The id of the player that called.

        `amount`: integer
            Amount of chips called.

        Example:

            ('call', 22, 13)


    - 'check': a player checked
        ('check', player_id)

        `player_id`: integer
            The id of the player that checked.

        Example:

            ('check', 22)


    - 'fold': a player folded
        ('fold', player_id)

        `player_id`: integer
            The id of the player that folded.

        Example:

            ('fold', 22)


    - 'raise': a player raised
        ('raise', player_id, raise_to, pay_amount, raise_amount)

        `player_id`: integer
            The id of the player that raised.

        `raise_to`: integer
            The amount of chips that other players must contribute to the
            pot to continue playing the hand.

            In holdem: at the start of the preflop betting round, `raise_to`
            is set to the big blind amount; at the start of each postflop
            betting round, `raise_to` is 0.

        `pay_amount`: integer
            The amount of chips the player contributed to the pot to perform
            the raise.

        `raise_amount`: integer
            The chip difference between the previous `raise_to` and the
            current `raise_to`.


    - 'rake': contains information about the amount of rake paid
        ('rake', amount, player_id_to_rake)

        `amount`: integer
            The total amount of chips raked in the pot.

        `player_id_to_rake`: dict
            Maps player ids to the amount of rake paid.

        Example:

            ('rake', 1, {22: 1, 23: 0})


    - 'showdown': indicates the completion of the last betting round; there
                  *may* be a showdown (only if 2 or more players remain in
                  the hand).
        ('showdown', board, holecards)

        `board`: pokerengine.PokerCards object or None if the poker variant
                 does not use community cards (i.e. stud or razz).
            Community cards.

        `holecards`: dict
            Maps player ids to pokerengine.PokerCards objects (holecards)

        Example:

            ('showdown', None,
             {22: PokerCards([210, 208]), 23: PokerCards([36, 23])}),


    - 'canceled': chips were returned to a player because the hand was
                   canceled.
        ('canceled', player_id, amount)

        `player_id`: integer
            The id of the player who receives the returned chips.

        `amount`: integer
            The amount of chips that were returned.

        Example (player with id of 22 is returned 50 chips):

            ('canceled', 22, 50)


    - 'end': the hand has ended; declare the winners.
        ('end', winners, showdown_stack)

        `winners`: list of integers
            List of player ids corresponding to players who won a share of
            the pot.

        `showdown_stack`: list of dicts
            Each dict contains showdown information.

            Each dict has a `type` key that indicates its type:
                `type`: string
                    Possible values:
                        - 'game_state'
                        - 'left_over'
                        - 'uncalled'
                        - 'resolve'

            The first element in the list is a dict with type 'game_state';

            A 'game_state' dict contains information about the conclusion of
            a hand:
                `type`: 'game_state'

                `serial2best`: dict mapping integers to dicts (*optional*)
                    Maps player ids to dicts containing their best hi and
                    lo hand. This key is only present when there was
                    a showdown.

                    Example:

                        'serial2best': {
                            22: {'hi': [17147696,
                                       ['OnePair', 31, 18, 49, 7, 16]],
                                 'low': [26821302,
                                        ['7, 6, 5, 4, 2', 5, 4, 3, 2, 0]]},
                            23: {'hi': [51016960,
                                       ['Trips', 49, 36, 23, 7, 31]]}
                        }

                    Deconstructing the example:

                        - The player with an id of 22 has a hi hand with
                        a pokersource hand ranking of 17147696. The hi hand
                        has a a description of 'OnePair' and is comprised of
                        the following 5-cards (as pokersource indices):
                            31, 18, 49, 7, 16.
                        Furthermore, he also has a low hand with ranking
                        26821302. The low hand has a description of
                        '7, 6, 5, 4, 2', and is comprised of the following
                        5-cards (as pokersource indices):
                            5, 4, 3, 2, 0.

                        - The player with an id of 23 only has a hi hand (he
                        could not make a low hand).


                `player_list`: list of integers
                    List of player ids corresponding to players that
                    were dealt into the hand.

                `foldwin`: boolean
                    True if the winner of the hand won because everyone else
                    folded.

                    *Note: this key is not present if there was a showdown.*

                `side_pots`: dict
                    Contains unraked pot information.

                    keys:
                        `building`:

                        `pots`:

                        `last_round`: integer
                            Index of the last betting round:
                                0 => preflop/third street
                                1 => flop/fourth street
                                2 => turn/fifth street
                                3 => river/sixth street

                        `contributions`: dict
                            each key maps to a dict that maps
                            player_ids to the amount of chips
                            contributed in a particular betting
                            round.

                            keys:
                                0 => preflop/3rd street contributions
                                1 => flop/fourth street contributions
                                2 => turn/fifth street contributions
                                3 => river/sixth street contributions
                                total => total contributions

                    Example:

                        'side_pots': {
                            'building': 0,
                            'pots': [[50, 50]],
                            'last_round': 3,
                            'contributions': {
                                0: {0: {22: 25, 23: 25}},
                                1: {},
                                2: {},
                                3: {},
                                'total': {22: 25, 23: 25}
                            }
                        }

                `pot`: integer
                    The amount of chips in all pots combined, before
                    rake.

                `serial2share`: dict
                    Maps player ids to the total amount of chips they won.

                    Example:

                        'serial2share': {23: 50}

                `serial2delta`: dict
                    Maps player ids to the amount of chips they won or lost.

                    Example:

                        'serial2delta': {22: -25, 23: 25}

                `serial2rake`: dict
                    Maps player ids to the amount of chips they contributed
                    to the rake.

                    Example:

                        'serial2rake': {23: 0}

            A 'left_over' dict entry corresponds to a situation where there
            are leftover chips because pots could not be divided evenly:
                `type`: 'left_over'

                `chips_left`: integer
                    The amount of chips remaining.

                `serial`: integer
                    The id of the player that receives the leftover chips.

            A 'uncalled' dict entry corresponds to a situation where
            a player receives uncalled chips; he wins back what he bet:
                `type`: 'uncalled'

                `serial`: integer
                    The id of the player who received uncalled chips.

                `uncalled`: integer
                    The amount of uncalled chips received.

            A 'resolve' dict entry contains information about the winner(s)
            of a pot.
                `type`: 'resolve'

                `serials`: list of integers
                    List of player ids that were eligible for the pot.

                `pot`: integer
                    The amount of chips in the pot.

                `serial2share`: dict
                    Maps player ids to the amount of chips they received
                    from the pot.

                `chips_left`: integer
                    The amount of leftover chips remaining after dividing
                    the pot among the winners.

                `hi`: list of integers
                    List of players that won the hi pot.

                    *Note: this key is only present if there is a hi pot.*

                `lo`: list of integers
                    List of players that won the lo pot.

                    *Note: this key is only present if there is a lo pot.*
    """
    EVENT_MAP = {
        'game': GameEvent,
        'round': RoundEvent,
        'blind': BlindEvent,
        'ante': AnteEvent,
        'all-in': AllInEvent,
        'call': CallEvent,
        'check': CheckEvent,
        'fold': FoldEvent,
        'raise': RaiseEvent,
        'showdown': ShowdownEvent,
        'canceled': CanceledEvent,
        'end': EndEvent
    }

    def generate_from_event(self, event, context=None):
        event_label = event[0]
        try:
            return (self.EVENT_MAP[event_label](*event[1:]),)
        except KeyError:
            return ()


def amount_string_to_int(amount_string, scale_factor=100):
    return int(Decimal(amount_string)*scale_factor)


def parse_betting_structure(betting_structure):
    """
    Parses a pokerengine betting structure string into a BettingLimit.

    Example `betting_structure` strings:
        '.10-.25-no-limit'
        'ante-10-20-limit'
    """
    LIMIT_MAP = {'limit': Limit.FIXED_LIMIT,
                 'no-limit': Limit.NO_LIMIT,
                 'pot-limit': Limit.POT_LIMIT}

    small_blind, big_blind, limit = re.match(
        r'(ante-)?([0-9]?\.?[0-9]+)-([0-9]?\.?[0-9]+)-(.+)',
        betting_structure).groups()[-3:]

    return BettingStructure(limit=LIMIT_MAP[limit],
                            small_blind=amount_string_to_int(small_blind),
                            big_blind=amount_string_to_int(big_blind))


class GenericPokerEventGenerator(Generator):
    def __init__(self, pokercards_converter=pokercards_adapter,
                 pokereval_best_hand_converter=pokereval_best_hand_adapter):
        self.pokercards_converter = pokercards_converter
        self.pokereval_best_hand_converter = pokereval_best_hand_converter

    def _convert_pokercards(self, pokercards):
        return self.pokercards_converter(pokercards)

    def _convert_pokereval_best_hand(self, pokereval_best_hand):
        return self.pokereval_best_hand_converter(pokereval_best_hand)

    def handle_GameEvent(self, event, context):
        players = [Player(player_id=player_id,
                          name=context.player_names[player_id],
                          seat_number=seat_number,
                          chips=event.player_chips[player_id])
                   for (seat_number, player_id) in enumerate(event.players)]

        # TODO: small_blind and big_blind should be properties of GameEvent
        # and should not require parsing the betting structure string.
        # In fact, the parsed small_blind and big_blind may differ from the
        # actual amounts (i.e. the actual small_blind from '.10-.25-no-limit'
        # is 12, not 10).
        betting_structure = parse_betting_structure(event.betting_structure)

        context.small_blind = betting_structure.small_blind
        context.big_blind = betting_structure.big_blind

        yield HandStarted(hand_id=event.hand_id,
                          hand_timestamp=context.hand_timestamp,
                          variant=event.variant,
                          betting_structure=betting_structure,
                          players=players)

    def handle_RoundEvent(self, event, context):
        community_cards = self._convert_pokercards(event.community_cards)

        if event.round_name == 'pre-flop':
            yield PreflopRoundStarted()
        elif event.round_name == 'flop':
            yield FlopDealt(flop_cards=community_cards)
        elif event.round_name == 'turn':
            yield TurnDealt(turn_card=community_cards[-1])
        elif event.round_name == 'river':
            yield RiverDealt(river_card=community_cards[-1])

        if event.dealt_cards:
            for player_id, cards in event.dealt_cards.iteritems():
                cards = self._convert_pokercards(cards)
                yield CardsDealtToPlayer(player_id=player_id, cards=cards)


    def handle_BlindEvent(self, event, context):
        if event.dead_amount == context.small_blind\
           and event.blind_amount == context.big_blind:
            yield PlayerPostedBigAndSmallBlinds(player_id=event.player_id,
                                                small_blind_amount=event.dead_amount,
                                                big_blind_amount=event.blind_amount)
        elif event.blind_amount == context.small_blind \
                or event.blind_amount <= context.big_blind/2:
            yield PlayerPostedSmallBlind(player_id=event.player_id,
                                         amount=event.blind_amount)
        elif event.blind_amount <= context.big_blind:
            yield PlayerPostedBigBlind(player_id=event.player_id,
                                       amount=event.blind_amount)

    def handle_AnteEvent(self, event, context):
        yield PlayerPostedAnte(player_id=event.player_id,
                               amount=event.ante_amount)

    def handle_AllInEvent(self, event, context):
        yield PlayerWentAllIn(player_id=event.player_id)

    def handle_CallEvent(self, event, context):
        yield PlayerCalled(player_id=event.player_id,
                           amount=event.call_amount)

    def handle_CheckEvent(self, event, context):
        yield PlayerChecked(player_id=event.player_id)

    def handle_FoldEvent(self, event, context):
        yield PlayerFolded(player_id=event.player_id)

    def handle_RaiseEvent(self, event, context):
        yield PlayerRaised(player_id=event.player_id,
                           to_amount=event.raise_to_amount,
                           by_amount=event.raise_by_amount)

    def handle_ShowdownEvent(self, event, context):
        context.player_cards = {
            player_id: self._convert_pokercards(cards)
            for player_id, cards in event.player_cards.iteritems()}
        if len(event.player_cards) > 1:
            yield Showdown()

    def handle_CanceledEvent(self, event, context):
        yield HandCanceled()
        yield UncalledBetReturnedToPlayer(player_id=event.player_id,
                                          amount=event.returned_amount)

    # TODO: refactor this method!
    def handle_EndEvent(self, event, context):
        def get_best_hands(end_state):
            if 'serial2best' not in end_state:
                return None

            best_hands = dict()
            for player_id, hands in end_state['serial2best'].iteritems():
                high_hand = None
                low_hand = None
                for hand_type, pokereval_best_hand in hands.iteritems():
                    hand = self._convert_pokereval_best_hand(
                        pokereval_best_hand)
                    if hand_type == 'hi':
                        high_hand = hand
                    elif hand_type == 'low':
                        low_hand = hand
                best_hands[player_id] = BestHands(high=high_hand,
                                                  low=low_hand)
            return best_hands

        players_that_showed = set()
        players_that_mucked = set()

        def player_should_show(player_id, player_hands, best_high_hand,
                               best_low_hand):
            high_hand = player_hands.high
            low_hand = player_hands.low

            def player_has_best_low_hand():
                return low_hand and low_hand.is_better_than(best_low_hand)\
                        or low_hand == best_low_hand

            def player_has_best_high_hand():
                return high_hand and high_hand.is_better_than(best_high_hand)\
                        or high_hand == best_high_hand

            return (player_id not in players_that_showed and
            (player_has_best_high_hand() or player_has_best_low_hand()))

        def resolved_pot_events(pot, best_hands, player_collected_from_pot):
            best_high_hand = HighHand([], -1)
            best_low_hand = LowHand([], sys.maxint)

            if best_hands:
                for player_id in pot.eligible_players:
                    player_hands = best_hands[player_id]
                    if player_should_show(player_id, player_hands,
                                          best_high_hand, best_low_hand):
                        yield PlayerShowedHand(player_id,
                                               context.player_cards[player_id],
                                               player_hands.high,
                                               player_hands.low)
                        players_that_showed.add(player_id)
                    elif player_id not in players_that_mucked:
                        yield PlayerMuckedHand(player_id,
                                               context.player_cards[player_id],
                                               player_hands.high,
                                               player_hands.low)
                        players_that_mucked.add(player_id)

            for player_id, won_amount in pot.winners.iteritems():
                yield player_collected_from_pot(player_id, won_amount)

        def get_player_rake(end_state):
            player_rake = {}
            for playerid, rake_amount in end_state['serial2rake'].iteritems():
                player_rake[playerid] = rake_amount
            return player_rake

        def resolved_pot(resolve_pot_event):
            eligible_players = resolve_pot_event['serials']
            pot_amount = resolve_pot_event['pot']
            winners = resolve_pot_event['serial2share']
            return ResolvedPot(pot_amount, eligible_players, winners)

        def player_collected_from_side_pot(player_id, amount, side_pot_index):
            return PlayerCollectedFromSidePot(player_id, amount,
                                              side_pot_index)

        def player_collected_from_main_pot(player_id, amount):
            return PlayerCollectedFromMainPot(player_id, amount)

        end_state = event.showdown_stack[0]

        best_hands = get_best_hands(end_state)

        pots = deque()

        num_pots = len(end_state['side_pots']['pots'])
        main_pot_index = num_pots - 1

        for event in event.showdown_stack[1:]:
            side_pot_index = len(pots)
            if side_pot_index == main_pot_index:
                player_collected_from_pot = player_collected_from_main_pot
            else:
                player_collected_from_pot = functools.partial(
                    player_collected_from_side_pot,
                    side_pot_index=side_pot_index)

            event_type = event['type']
            if event_type == 'resolve':
                pot = resolved_pot(event)
                for showdown_event in resolved_pot_events(
                    pot, best_hands, player_collected_from_pot):
                    yield showdown_event
                pots.appendleft(pot)
            elif event_type == 'uncalled':
                yield UncalledBetReturnedToPlayer(player_id=event['serial'],
                                                  amount=event['uncalled'])
            elif event_type == 'left_over':
                yield player_collected_from_pot(player_id=event['serial'],
                                                amount=['chips_left'])

        pots = list(pots)
        player_rake = get_player_rake(end_state)
        yield HandEnded(pots=pots, player_rake=player_rake)


class HandHistoryGenerator(Generator):
    def __init__(self, site_name='Bitcoin Poker Network',
                 date_format='%Y/%m/%d - %H:%M:%S'):
        self.site_name = site_name
        self.date_format = date_format

    def generate(self, events):
        def pairwise(iterable):
            """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
            a, b = itertools.tee(iterable)
            next(b, None)
            return itertools.izip(a, b)

        def do_generate(events, context):
            last_event = None
            for event, next_event in pairwise(events):
                context.all_in = next_event.__class__ == PlayerWentAllIn
                last_event = next_event
                for string in self.generate_from_event(event, context):
                    yield string
            context.all_in = False
            for string in self.generate_from_event(last_event, context):
                yield string

        return '\n'.join(do_generate(events, Context()))

    def player_action(self, player_id, action, context):
        player_name = context.player_names[player_id]
        action_string = '{0}: {1}'.format(player_name, action)
        if hasattr(context, 'all_in') and context.all_in:
            action_string += ' and is all-in'
        return action_string

    def cards_string(self, cards):
        return '[{0}]'.format(' '.join(str(card) for card in cards))

    def hand_description(self, high_hand, low_hand):
        if high_hand and low_hand:
            return 'HI: {0}; LO: {1}'.format(high_hand, low_hand)
        elif high_hand:
            return str(high_hand)
        else:
            return str(low_hand)

    def handle_HandStarted(self, event, context):
        """
        Returns the hand history header. For example:

            PokerStars Game #19448592333:  Hold'em No Limit ($0.10/$0.25) - 2008/08/08 - 01:10:30 (ET)
            Table 'Jubilatrix II' 6-max Seat #1 is the button
            Seat 1: biggtyme112 ($17.95 in chips)
            Seat 2: SauceH ($25.10 in chips)
            Seat 3: Solsek ($25.40 in chips)
            Seat 4: 357m@gnum ($22.05 in chips)
            Seat 5: jinzilla ($30.10 in chips)
            Seat 6: Sick M ($27.75 in chips)

        `header_dict`: dictionary containing the following keys: TODO
        `site_name`: poker site name, i.e. 'PokerStars' or 'PartyPoker'
        """
        VARIANT_MAP = {'holdem': "Hold'em",
                       'omaha': 'Omaha',
                       'omaha8': 'Omaha Hi/Lo'}
        date_string = time.strftime(self.date_format,
                                    time.gmtime(event.hand_timestamp))

        yield "{site_name} Game #{hand_id:d}:  {variant} {limit} "\
              "({small_blind}/{big_blind}) - {date} (UTC)".format(
                  site_name=self.site_name, hand_id=event.hand_id,
                  variant=VARIANT_MAP[event.variant],
                  limit=event.betting_structure.limit,
                  small_blind=event.betting_structure.small_blind,
                  big_blind=event.betting_structure.big_blind,
                  date=date_string)

        context.player_names = {}

        for player in event.players:
            context.player_names[player.player_id] = player.name
            yield 'Seat {seat_number:d}: {name} ({chips} in chips)'.format(
                seat_number=player.seat_number + 1, name=player.name,
                chips=player.chips)

    def handle_PlayerPostedSmallBlind(self, event, context):
        action_string = 'posts small blind {0}'.format(event.amount)
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerPostedBigBlind(self, event, context):
        action_string = 'posts big blind {0}'.format(event.amount)
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerPostedBigAndSmallBlinds(self, event, context):
        action_string = 'posts small & big blinds {0}'.format(
            event.big_blind_amount + event.small_blind_amount)
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerPostedAnte(self, event, context):
        action_string = 'posts the ante {0}'.format(event.amount)
        yield self.player_action(event.player_id, action_string, context)

    def handle_PreflopRoundStarted(self, event, context):
        yield '*** HOLE CARDS ***'

    def handle_CardsDealtToPlayer(self, event, context):
        player = context.player_names[event.player_id]

        if not hasattr(context, 'player_cards'):
            context.player_cards = dict()
        context.player_cards[event.player_id] = event.cards

        yield 'Dealt to {0} {1}'.format(player, self.cards_string(event.cards))

    def handle_FlopDealt(self, event, context):
        context.community_cards = list(event.flop_cards)
        yield '*** FLOP *** {0}'.format(self.cards_string(event.flop_cards))

    def handle_TurnDealt(self, event, context):
        previous_community_cards = self.cards_string(context.community_cards)
        turn_card_string = self.cards_string([event.turn_card])
        context.community_cards.append(event.turn_card)
        yield '*** TURN *** {0} {1}'.format(previous_community_cards,
                                            turn_card_string)

    def handle_RiverDealt(self, event, context):
        previous_community_cards = self.cards_string(context.community_cards)
        river_card_string = self.cards_string([event.river_card])
        context.community_cards.append(event.river_card)
        yield '*** RIVER *** {0} {1}'.format(previous_community_cards,
                                             river_card_string)

    def handle_PlayerCalled(self, event, context):
        action_string = 'calls {0}'.format(event.amount)
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerChecked(self, event, context):
        action_string = 'checks'
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerFolded(self, event, context):
        action_string = 'folds'
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerRaised(self, event, context):
        if event.by_amount == event.to_amount:
            action_string = 'bets {0}'.format(event.by_amount)
        else:
            action_string = 'raises {0} to {1}'.format(event.by_amount,
                                                       event.to_amount)
        yield self.player_action(event.player_id, action_string, context)

    def handle_UncalledBetReturnedToPlayer(self, event, context):
        yield 'Uncalled bet ({0}) returned to {1}'.format(
            event.amount, context.player_names[event.player_id])

    def handle_Showdown(self, event, context):
        yield '*** SHOW DOWN ***'

    def handle_PlayerShowedHand(self, event, context):
        action_string = 'shows {0} ({1})'.format(
            self.cards_string(event.cards),
            self.hand_description(event.high_hand, event.low_hand))
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerMuckedHand(self, event, context):
        action_string = 'mucks'.format(
            self.cards_string(context.player_cards[event.player_id]))
        yield self.player_action(event.player_id, action_string, context)

    def handle_PlayerCollectedFromSidePot(self, event, context):
        yield '{0} collected {1} from side pot-{2}'.format(
            context.player_names[event.player_id], event.amount,
            event.side_pot_index + 1)

    def handle_PlayerCollectedFromMainPot(self, event, context):
        yield '{0} collected {1} from main pot'.format(
            context.player_names[event.player_id], event.amount)

    def _pot_summary(self, resolved_pots, player_rake):
        total_pot = sum(pot.pot_amount for pot in resolved_pots)
        pot_summary = 'Total pot {total_pot} Main pot {main_pot}.'.format(
            total_pot=total_pot, main_pot=resolved_pots[0].pot_amount)
        for side_pot_index, side_pot in enumerate(resolved_pots[1:]):
            pot_summary += ' Side pot-{0} {1}.'.format(
                side_pot_index + 1, side_pot.pot_amount)
        pot_summary += ' | Rake {0}'.format(sum(player_rake.values()))
        return pot_summary

    def _player_summaries(self, winners, context):
        # player folded on some street (possibly didn't bet)
        # player showed and won
        # player showed and lost
        # player mucked
        # player collected from pot
        pass

    def handle_HandEnded(self, event, context):
        yield '*** SUMMARY ***'
        yield self._pot_summary(event.pots, event.player_rake)
        if hasattr(context, 'community_cards'):
            yield 'Board {0}'.format(self.cards_string(context.community_cards))
        #yield self._player_summaries(event.winning_players)


class ObserverHandHistoryGenerator(HandHistoryGenerator):
    def handle_CardsDealtToPlayer(self, event, context):
        pass


class PlayerHandHistoryGenerator(HandHistoryGenerator):
    def __init__(self, player_id):
        self.player_id = player_id

    def handle_CardsDealtToPlayer(self, event, context):
        if event.player_id == self.player_id:
            super(HandHistoryGenerator, self).handle_CardsDealtToPlayer(self,
                                                                        event,
                                                                        context)


HandStarted = namedtuple('HandStarted', ['hand_id', 'hand_timestamp',
                                         'variant', 'betting_structure',
                                         'players'])

PlayerPostedSmallBlind = namedtuple('PlayerPostedSmallBlind', ['player_id',
                                                               'amount'])
PlayerPostedBigBlind = namedtuple('PlayerPostedBigBlind', ['player_id',
                                                           'amount'])
PlayerPostedBigAndSmallBlinds = namedtuple('PlayerPostedBigAndSmallBlinds',
                                           ['player_id', 'big_blind_amount',
                                            'small_blind_amount'])
PlayerPostedAnte = namedtuple('PlayerPostedAnte', ['player_id', 'amount'])

CardsDealtToPlayer = namedtuple('CardsDealtToPlayer', ['player_id', 'cards'])

PreflopRoundStarted = namedtuple('PreflopRoundStarted', [])
FlopDealt = namedtuple('FlopDealt', 'flop_cards')
TurnDealt = namedtuple('TurnDealt', 'turn_card')
RiverDealt = namedtuple('RiverDealt', 'river_card')
Showdown = namedtuple('Showdown', '')

PlayerCalled = namedtuple('PlayerCalled', ['player_id', 'amount'])
PlayerChecked = namedtuple('PlayerChecked', ['player_id'])
PlayerFolded = namedtuple('PlayerFolded', ['player_id'])
PlayerRaised = namedtuple('PlayerRaised', ['player_id', 'by_amount',
                                           'to_amount'])
PlayerWentAllIn = namedtuple('PlayerWentAllIn', ['player_id'])

UncalledBetReturnedToPlayer = namedtuple('UncalledBetReturnedToPlayer',
                                         ['player_id', 'amount'])

PlayerShowedHand = namedtuple('PlayerShowedHand', ['player_id', 'cards',
                                                   'high_hand', 'low_hand'])
PlayerMuckedHand = namedtuple('PlayerMuckedHand', ['player_id', 'cards',
                                                   'high_hand', 'low_hand'])
PlayerCollectedFromSidePot = namedtuple('PlayerCollectedFromSidePot',
                                        ['player_id', 'amount',
                                         'side_pot_index'])
PlayerCollectedFromMainPot = namedtuple('PlayerCollectedFromMainPot',
                                        ['player_id', 'amount'])

HandCanceled = namedtuple('HandCanceled', '')
HandEnded = namedtuple('HandEnded', ['pots', 'player_rake'])


def load_pokerengine_hand(hand_id):
    config = Config([''])
    config.load(DEFAULT_CONFIG_PATH)
    service = PokerService(config)
    service.db = PokerDatabase(config)
    hand_description = service.loadHand(hand_id)
    hand_timestamp = service.getHandTimestamp(hand_id)
    player_names = service.getPlayerNamesFromHand(hand_id)
    return PokerEngineHand(hand_description=hand_description,
                           hand_timestamp=hand_timestamp,
                           player_names=player_names)


def generate_hand_history(pokerengine_hand,
                          generator=HandHistoryGenerator()):
    pokerengine_events = PokerEngineEventGenerator().generate(
        pokerengine_hand.hand_description)

    context = Context()
    context.player_names = pokerengine_hand.player_names
    context.hand_timestamp = pokerengine_hand.hand_timestamp

    generic_generator = GenericPokerEventGenerator(pokercards_adapter)
    generic_events = generic_generator.generate(pokerengine_events, context)

    hand_history = generator.generate(generic_events)
    return hand_history

