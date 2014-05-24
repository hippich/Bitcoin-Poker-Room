#!/usr/bin/env python
# coding: utf-8

import calendar
import datetime
import unittest

from utils.handhistory import *

from pokerengine.pokercards import PokerCards

class TestParseBettingStructure(unittest.TestCase):
    def test_can_parse_limit_ante_structure(self):
        structure = 'ante-10-20-limit'
        expected = BettingStructure(limit=Limit.FIXED_LIMIT,
                                    small_blind=1000,
                                    big_blind=2000)
        actual = parse_betting_structure(structure)
        self.assertEquals(actual, expected)

    def test_can_no_limit_structure_without_ante(self):
        structure = 'ante-10-20-no-limit'
        expected = BettingStructure(limit=Limit.NO_LIMIT,
                                    small_blind=1000,
                                    big_blind=2000)
        actual = parse_betting_structure(structure)
        self.assertEquals(actual, expected)

    def test_can_parse_pot_limit_structure_with_ante(self):
        structure = 'ante-10-20-pot-limit'
        expected = BettingStructure(limit=Limit.POT_LIMIT,
                                    small_blind=1000,
                                    big_blind=2000)
        actual = parse_betting_structure(structure)
        self.assertEquals(actual, expected)

    def test_can_parse_decimal_blind_amounts(self):
        structure = '.10-.25-pot-limit'
        expected = BettingStructure(limit=Limit.POT_LIMIT,
                                    small_blind=10,
                                    big_blind=25)
        actual = parse_betting_structure(structure)
        self.assertEquals(actual, expected)


class TestPokerCardsConverter(unittest.TestCase):
    def test_convert_upcard(self):
        self.assertEquals(pokercards_adapter(PokerCards([0])),
                          [Upcard(RankTwo, SuitHearts)])


class HandHistoryIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.hand_id = 195
        # Hand description without showdown (HU; SB folded preflop)
        hand_description = [
            ('game', 0, 174, 4, 194.87623190879822, 'holdem',
             '.10-.25-no-limit', [22, 23], 0, {22: 1262, 23: 1237}),

            ('position', 0), ('blind', 22, 12, 0), ('position', 1),
            ('blind', 23, 25, 0), ('position', -1),

            ('round', 'pre-flop', PokerCards([]), {22: PokerCards([231, 201]),
            23: PokerCards([234, 211])}),

            ('position', 0), ('fold', 22), ('position', 1), ('position', -1),

            ('showdown', None, {23: PokerCards([234, 211])}),

            ('end', [23], [{'serial2delta': {22: -12, 23: 12}, 'player_list': [22, 23],
            'serial2rake': {23: 0}, 'pot': 37, 'serial2share': {23: 37},
            'type': 'game_state', 'foldwin': True, 'side_pots': {'building': 0,
            'pots': [[37, 37]], 'last_round': 0, 'contributions': {0: {0: {22: 12, 23: 25}},
            'total': {22: 12, 23: 25}}}}, {'serials': [23], 'pot': 37, 'type': 'resolve',
            'serial2share': {23: 37}}])]
        hand_datetime = datetime.datetime(2011, 7, 8, 1, 10, 30)
        hand_timestamp = calendar.timegm(hand_datetime.utctimetuple())
        player_names = {22: 'Alice', 23: 'Bob'}
        self.pokerengine_hand = PokerEngineHand(hand_description,
                                                hand_timestamp, player_names)

    def test_generate_admin_hand_history(self):
        hand_history = generate_hand_history(self.pokerengine_hand,
                                             generator=HandHistoryGenerator())
        print hand_history
        assert len(hand_history) > 0

    def test_generate_observer_hand_history(self):
        hand_history = generate_hand_history(
            self.pokerengine_hand, generator=ObserverHandHistoryGenerator())
        print hand_history
        assert len(hand_history) > 0


class TestGenericPokerEventGenerator(unittest.TestCase):
    def setUp(self):
        def dummy_adapter(pokercards):
            return pokercards
        self.generator = GenericPokerEventGenerator(
            pokercards_converter=lambda x: x)

    def assertGenerateFromEvent(self, event, expected, context=None):
        actual = list(self.generator.generate_from_event(event, context))
        self.assertEquals(actual, expected)

    def test_generate_events_from_GameEvent(self):
        event = GameEvent(level=0, hand_id=1, hands_count=0,
                          hand_timestamp=12345678, variant='holdem',
                          betting_structure='.10-.25-no-limit', players=[0, 1],
                          button_seat=4, player_chips={0: 100, 1: 175})
        hand_datetime = datetime.datetime(2011, 7, 8, 1, 10, 30)
        hand_timestamp = calendar.timegm(hand_datetime.utctimetuple())
        expected = [HandStarted(hand_id=1, hand_timestamp=hand_timestamp,
                                variant='holdem',
                                betting_structure=BettingStructure(
                                    limit=Limit.NO_LIMIT,
                                    small_blind=10,
                                    big_blind=25),
                                players=[Player(player_id=0, name='Alice',
                                                seat_number=0, chips=100),
                                         Player(player_id=1, name='Bob',
                                                seat_number=1, chips=175)])]
        context = Context()
        context.hand_timestamp = hand_timestamp
        context.player_names = {0: 'Alice', 1: 'Bob'}
        self.assertGenerateFromEvent(event, expected, context)
        self.assertEquals(context.small_blind, 10)
        self.assertEquals(context.big_blind, 25)

    def test_generate_events_from_preflop_RoundEvent(self):
        event = RoundEvent(round_name='pre-flop',
                                 community_cards=PokerCards([]),
                                 dealt_cards={
                                     0: [Downcard(RankAce, SuitClubs),
                                         Downcard(RankKing, SuitClubs)],
                                     1: [Downcard(RankQueen, SuitClubs),
                                         Downcard(RankQueen, SuitDiamonds)]})
        expected = [PreflopRoundStarted(),
                    CardsDealtToPlayer(player_id=0,
                                       cards=event.dealt_cards[0]),
                    CardsDealtToPlayer(player_id=1,
                                       cards=event.dealt_cards[1])]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_flop_RoundEvent(self):
        event = RoundEvent(round_name='flop',
                                 community_cards=[
                                     Upcard(RankTen, SuitDiamonds),
                                     Upcard(RankSix, SuitSpades),
                                     Upcard(RankEight, SuitSpades)],
                                 dealt_cards={})
        expected = [FlopDealt(flop_cards=event.community_cards) ]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_turn_RoundEvent(self):
        event = RoundEvent(round_name='turn',
                                 community_cards=[Upcard(RankTen,
                                                         SuitDiamonds)],
                                 dealt_cards={})
        expected = [TurnDealt(turn_card=event.community_cards[0])]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_river_RoundEvent(self):
        event = RoundEvent(round_name='river',
                                 community_cards=[Upcard(RankNine,
                                                         SuitClubs)],
                                 dealt_cards={})
        expected = [RiverDealt(river_card=event.community_cards[0])]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_small_blind_BlindEvent(self):
        event = BlindEvent(player_id=0, blind_amount=10, dead_amount=0)
        context = Context()
        context.small_blind = 10
        context.big_blind = 25
        expected = [PlayerPostedSmallBlind(player_id=0,
                                           amount=10)]
        self.assertGenerateFromEvent(event, expected, context)

    def test_generate_events_from_big_and_small_blinds_BlindEvent(self):
        event = BlindEvent(player_id=0, blind_amount=25, dead_amount=10)
        context = Context()
        context.small_blind = 10
        context.big_blind = 25
        expected = [PlayerPostedBigAndSmallBlinds(player_id=0,
                                                  big_blind_amount=25,
                                                  small_blind_amount=10)]
        self.assertGenerateFromEvent(event, expected, context)

    def test_generate_events_from_big_blind_BlindEvent(self):
        event = BlindEvent(player_id=0, blind_amount=25, dead_amount=0)
        context = Context()
        context.small_blind = 10
        context.big_blind = 25
        expected = [PlayerPostedBigBlind(player_id=0, amount=25)]
        self.assertGenerateFromEvent(event, expected, context)

    def test_generate_events_from_AnteEvent(self):
        event = AnteEvent(player_id=0, ante_amount=5)
        expected = [PlayerPostedAnte(player_id=0, amount=5)]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_AllInEvent(self):
        event = AllInEvent(player_id=5)
        expected = [PlayerWentAllIn(player_id=5)]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_CallEvent(self):
        event = CallEvent(player_id=1, call_amount=5)
        expected = [PlayerCalled(player_id=1, amount=5)]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_CheckEvent(self):
        event = CheckEvent(player_id=1)
        expected = [PlayerChecked(player_id=1)]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_FoldEvent(self):
        event = FoldEvent(player_id=1)
        expected = [PlayerFolded(player_id=1)]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_RaiseEvent(self):
        event = RaiseEvent(player_id=1, raise_to_amount=20, pay_amount=10,
                           raise_by_amount=10)
        expected = [PlayerRaised(player_id=1, by_amount=10, to_amount=20)]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_ShowdownEvent(self):
        event = ShowdownEvent(
            player_cards={0: [Upcard(RankAce, SuitClubs),
                              Upcard(RankAce, SuitDiamonds)],
                          1: [Upcard(RankKing, SuitDiamonds),
                              Upcard(RankKing, SuitSpades)]},
            community_cards=None)
        context = Context()
        expected = [Showdown()]
        self.assertGenerateFromEvent(event, expected, context)
        self.assertEquals(context.player_cards, event.player_cards)

    def test_generate_events_from_CanceledEvent(self):
        event = CanceledEvent(player_id=1, returned_amount=50)
        expected = [HandCanceled(),
                    UncalledBetReturnedToPlayer(player_id=1, amount=50)]
        self.assertGenerateFromEvent(event, expected)

    def test_generate_events_from_EndEvent(self):
        winners = [23]
        showdown_stack = [
                {'serial2delta': {22: -25, 23: 25}, 'player_list': [23, 22],
                 'serial2rake': {23: 0}, 'serial2share': {23: 50}, 'pot': 50,
                 'serial2best': {22: {'hi': [694100, ['NoPair', 36, 9, 7, 31,
                                                      4]]},
                                 23: {'hi': [694117, ['NoPair', 49, 9, 7, 6,
                                                      31]]}},
                 'type': 'game_state',
                 'side_pots': {
                     'building': 0, 'pots': [[50, 50]], 'last_round': 3,
                     'contributions': {0: {0: {22: 25, 23: 25}}, 1: {}, 2: {},
                                       'total': {22: 25, 23: 25}, 3: {}}}
                },
                {'serials': [23, 22], 'pot': 50, 'hi': [23], 'chips_left': 0,
                 'type': 'resolve', 'serial2share': {23: 50}}
            ]
        context = Context()
        context.player_cards = {23: [Downcard(RankQueen, SuitSpades),
                                     Downcard(RankJack, SuitHearts)],
                                22: [Downcard(RankNine, SuitHearts),
                                    Downcard(RankSix, SuitHearts)]}
        event = EndEvent(winners, showdown_stack)
        expected = [
            PlayerShowedHand(player_id=23,
                             cards=[Downcard(RankQueen, SuitSpades),
                                    Downcard(RankJack, SuitHearts)],
                             high_hand=Hand(cards=[Card(RankQueen, SuitSpades),
                                              Card(RankJack, SuitHearts),
                                              Card(RankNine, SuitHearts),
                                              Card(RankEight, SuitHearts),
                                              Card(RankSeven, SuitClubs)],
                                    pokereval_ranking=694117),
                             low_hand=None),
            PlayerShowedHand(player_id=22,
                             cards=[Downcard(RankNine, SuitHearts),
                                    Downcard(RankSix, SuitHearts)],
                             high_hand=Hand(cards=[Card(RankQueen, SuitClubs),
                                                   Card(RankJack, SuitHearts),
                                                   Card(RankNine, SuitHearts),
                                                   Card(RankSeven, SuitClubs),
                                                   Card(RankSix, SuitHearts)],
                                    pokereval_ranking=694100),
                              low_hand=None),
            PlayerCollectedFromMainPot(player_id=23, amount=50),
            HandEnded(pots=[ResolvedPot(pot_amount=50,
                                        eligible_players=[23,22],
                                        winners={23: 50})],
                      player_rake={23: 0})]
        self.assertGenerateFromEvent(event, expected, context)


class TestHandHistoryGenerator(unittest.TestCase):
    def setUp(self):
        self.generator = HandHistoryGenerator(
            site_name='Bitcoin Poker Room')

    def assertGenerateFromEvent(self, event, expected, context=None):
        actual = list(self.generator.generate_from_event(event, context))
        self.assertEquals(actual, expected)

    def test_build_string_from_HandStarted(self):
        hand_datetime = datetime.datetime(2011, 7, 8, 1, 10, 30)
        hand_timestamp = calendar.timegm(hand_datetime.utctimetuple())
        event = HandStarted(
            hand_id=1,
            hand_timestamp=hand_timestamp,
            variant='holdem',
            betting_structure=BettingStructure(limit=Limit.NO_LIMIT,
                                               small_blind=10, big_blind=25),
            players=[Player(player_id=0, name='Alice', seat_number=0,
                            chips=100),
                     Player(player_id=1, name='Bob', seat_number=1, chips=75)])
        expected = ["Bitcoin Poker Room Game #1:  Hold'em No Limit (10/25) - "\
                    "2011/07/08 - 01:10:30 (UTC)",
                    "Seat 1: Alice (100 in chips)",
                    "Seat 2: Bob (75 in chips)"]
        context = Context()
        self.assertGenerateFromEvent(event, expected, context)
        self.assertEquals(context.player_names, {0: 'Alice', 1: 'Bob'})

    def test_build_string_from_PlayerPostedSmallBlind(self):
        event = PlayerPostedSmallBlind(player_id=1,
                                       amount=10)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: posts small blind 10']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerPostedSmallBlind_all_in(self):
        event = PlayerPostedSmallBlind(player_id=1,
                                       amount=10)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.all_in = True
        expected = ['Bob: posts small blind 10 and is all-in']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerPostedBigBlind(self):
        event = PlayerPostedBigBlind(player_id=1, amount=25)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: posts big blind 25']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerPostedBigBlind_all_in(self):
        event = PlayerPostedBigBlind(player_id=1, amount=25)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.all_in = True
        expected = ['Bob: posts big blind 25 and is all-in']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerPostedBigAndSmallBlinds(self):
        event = PlayerPostedBigAndSmallBlinds(player_id=1,
                                              big_blind_amount=25,
                                              small_blind_amount=10)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: posts small & big blinds 35']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerPostedBigAndSmallBlinds_all_in(self):
        event = PlayerPostedBigAndSmallBlinds(player_id=1,
                                              big_blind_amount=25,
                                              small_blind_amount=10)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.all_in = True
        expected = ['Bob: posts small & big blinds 35 and is all-in']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerPostedAnte(self):
        event = PlayerPostedAnte(player_id=1, amount=5)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: posts the ante 5']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerPostedAnte_all_in(self):
        event = PlayerPostedAnte(player_id=1, amount=5)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.all_in = True
        expected = ['Bob: posts the ante 5 and is all-in']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PreflopRoundStarted(self):
        event = PreflopRoundStarted()
        expected = ['*** HOLE CARDS ***']
        self.assertGenerateFromEvent(event, expected)

    def test_build_string_from_CardsDealtToPlayer(self):
        event = CardsDealtToPlayer(player_id=1, cards=[Downcard(RankAce,
                                                                SuitClubs),
                                                       Downcard(RankKing,
                                                                SuitDiamonds)])
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Dealt to Bob [Ac Kd]']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_FlopDealt(self):
        event = FlopDealt(flop_cards=[Upcard(RankTwo, SuitDiamonds),
                                      Upcard(RankSeven, SuitClubs),
                                      Upcard(RankFour, SuitHearts)])
        context = Context()
        expected = ['*** FLOP *** [2d 7c 4h]']
        self.assertGenerateFromEvent(event, expected, context)
        self.assertEquals(context.community_cards,
                          [Upcard(RankTwo, SuitDiamonds),
                           Upcard(RankSeven, SuitClubs),
                           Upcard(RankFour, SuitHearts)])

    def test_build_string_from_TurnDealt(self):
        event = TurnDealt(turn_card=Upcard(RankSix, SuitSpades))
        context = Context()
        context.community_cards = [Upcard(RankTwo, SuitDiamonds),
                                   Upcard(RankSeven, SuitClubs),
                                   Upcard(RankFour, SuitHearts)]
        expected = ['*** TURN *** [2d 7c 4h] [6s]']
        self.assertGenerateFromEvent(event, expected, context)
        self.assertEquals(context.community_cards,
                          [Upcard(RankTwo, SuitDiamonds),
                           Upcard(RankSeven, SuitClubs),
                           Upcard(RankFour, SuitHearts),
                           Upcard(RankSix, SuitSpades)])

    def test_build_string_from_RiverDealt(self):
        event = RiverDealt(river_card=Upcard(RankAce, SuitHearts))
        context = Context()
        context.community_cards = [Upcard(RankTwo, SuitDiamonds),
                                   Upcard(RankSeven, SuitClubs),
                                   Upcard(RankFour, SuitHearts),
                                   Upcard(RankSix, SuitSpades)]
        expected = ['*** RIVER *** [2d 7c 4h 6s] [Ah]']
        self.assertGenerateFromEvent(event, expected, context)
        self.assertEquals(context.community_cards,
                          [Upcard(RankTwo, SuitDiamonds),
                           Upcard(RankSeven, SuitClubs),
                           Upcard(RankFour, SuitHearts),
                           Upcard(RankSix, SuitSpades),
                           Upcard(RankAce, SuitHearts)])

    def test_build_string_from_PlayerCalled(self):
        event = PlayerCalled(player_id=1, amount=500)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: calls 500']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerCalled_all_in(self):
        event = PlayerCalled(player_id=1, amount=500)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.all_in = True
        expected = ['Bob: calls 500 and is all-in']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerChecked(self):
        event = PlayerChecked(player_id=1)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: checks']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerFolded(self):
        event = PlayerFolded(player_id=1)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: folds']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerRaised(self):
        event = PlayerRaised(player_id=1, by_amount=10, to_amount=30)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: raises 10 to 30']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerRaised_all_in(self):
        event = PlayerRaised(player_id=1, by_amount=10, to_amount=30)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.all_in = True
        expected = ['Bob: raises 10 to 30 and is all-in']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerRaised_bet(self):
        event = PlayerRaised(player_id=1, by_amount=10, to_amount=10)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Bob: bets 10']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerRaised_bet_all_in(self):
        event = PlayerRaised(player_id=1, by_amount=10, to_amount=10)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.all_in = True
        expected = ['Bob: bets 10 and is all-in']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerWentAllIn(self):
        event = PlayerWentAllIn(player_id=1)
        self.assertGenerateFromEvent(event, [])

    def test_build_string_from_UncalledBetReturnedToPlayer(self):
        event = UncalledBetReturnedToPlayer(player_id=1, amount=49)
        context = Context()
        context.player_names = {1: 'Bob'}
        expected = ['Uncalled bet (49) returned to Bob']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_HandCanceled(self):
        event = HandCanceled()
        self.assertGenerateFromEvent(event, [])

    def test_build_string_from_PlayerShowedHand_high_hand_only(self):
        high_hand = Flush(cards=[Card(RankJack, SuitClubs),
                                 Card(RankTen, SuitClubs),
                                 Card(RankSeven, SuitClubs),
                                 Card(RankSix, SuitClubs),
                                 Card(RankFour, SuitClubs)],
                          pokereval_ranking=None)
        low_hand = None
        context = Context()
        context.player_names = {1: 'Bob'}
        event = PlayerShowedHand(player_id=1,
                                 cards=[Downcard(RankJack, SuitClubs),
                                        Downcard(RankTen, SuitClubs)],
                                 high_hand=high_hand,
                                 low_hand=low_hand)
        expected = ['Bob: shows [Jc Tc] (a flush, Jack high)']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_PlayerShowedHand_high_and_low_hands(self):
        high_hand = OnePair(cards=[Card(RankTen, SuitClubs),
                                   Card(RankTen, SuitDiamonds),
                                   Card(RankKing, SuitSpades),
                                   Card(RankSix, SuitClubs),
                                   Card(RankFour, SuitClubs)],
                          pokereval_ranking=None)
        low_hand = LowHand(cards=[Card(RankSeven, SuitSpades),
                                  Card(RankSix, SuitDiamonds),
                                  Card(RankFour, SuitHearts),
                                  Card(RankThree, SuitHearts),
                                  Card(RankAce, SuitClubs)],
                           pokereval_ranking=None)
        context = Context()
        context.player_names = {1: 'Bob'}
        context.player_cards = {1: [Downcard(RankJack, SuitClubs),
                                    Downcard(RankTen, SuitClubs)]}
        event = PlayerShowedHand(player_id=1,
                                 cards=[Downcard(RankJack, SuitClubs),
                                        Downcard(RankTen, SuitClubs)],
                                 high_hand=high_hand,
                                 low_hand=low_hand)
        expected = ['Bob: shows [Jc Tc] (HI: a pair of Tens; LO: 7,6,4,3,A)']
        self.assertGenerateFromEvent(event, expected, context)

    def test_build_string_from_HandEnded(self):
        event = HandEnded(pots=[ResolvedPot(pot_amount=50,
                                            eligible_players=[0,1],
                                            winners={1: 50})],
                          player_rake={0:0})
        context = Context()
        context.community_cards = [Upcard(RankSeven, SuitSpades),
                                   Upcard(RankSeven, SuitDiamonds),
                                   Upcard(RankQueen, SuitHearts),
                                   Upcard(RankNine, SuitClubs),
                                   Upcard(RankThree, SuitClubs)]
        expected = ['*** SUMMARY ***',
                    'Total pot 50 Main pot 50. | Rake 0',
                    'Board [7s 7d Qh 9c 3c]']
        self.assertGenerateFromEvent(event, expected, context)

