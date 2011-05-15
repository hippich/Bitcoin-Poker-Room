#
# Copyright (C) 2006 - 2010 Loic Dachary <loic@dachary.org>
# Copyright (C) 2004, 2005, 2006 Mekensleep
#
# Mekensleep
# 26 rue des rosiers
# 75004 Paris
#       licensing@mekensleep.com
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
#  Henry Precheur <henry@precheur.org> (2004)
#

from types import *
from pokereval import PokerEval

def visible_card(card):
    return (card & PokerCards.VALUE_CARD_MASK)

def not_visible_card(card):
    return (card | PokerCards.NOT_VISIBLE_CARD)

def is_visible(card):
    return (card & PokerCards.VISIBLE_CARD_MASK) == PokerCards.VISIBLE_CARD

def card_value(card):
    return (card & PokerCards.VALUE_CARD_MASK)

letter2name = {
    'A': 'Ace',
    'K': 'King',
    'Q': 'Queen',
    'J': 'Jack',
    'T': 'Ten',
    '9': 'Nine',
    '8': 'Eight',
    '7': 'Seven',
    '6': 'Six',
    '5': 'Five',
    '4': 'Four',
    '3': 'Trey',
    '2': 'Deuce'
    }

letter2names = {
    'A': 'Aces',
    'K': 'Kings',
    'Q': 'Queens',
    'J': 'Jacks',
    'T': 'Tens',
    '9': 'Nines',
    '8': 'Eights',
    '7': 'Sevens',
    '6': 'Sixes',
    '5': 'Fives',
    '4': 'Fours',
    '3': 'Treys',
    '2': 'Deuces'
    }

class PokerCards:
    NOCARD = 255
    MAX_CARD = 64 # 64 > 52 cards 0x0100 0000
    NB_CARD = 52
    
    VALUE_CARD_MASK = MAX_CARD - 1 # 0x0011 1111

    VISIBLE_CARD_MASK = 0xC0 # ~(VALUE_CARD_MASK) # ~(0x0011 1111) = 0x1100 0000
    VISIBLE_CARD = 0
    NOT_VISIBLE_CARD = VISIBLE_CARD_MASK
    
    def __init__(self, cards = []):
        self.set(cards)

    def __eq__(self, other):
        if type(self) != type(other): return False
        
        cards = self.cards[:]
        cards.sort()
        other_cards = other.cards[:]
        other_cards.sort()
        return cards == other_cards

    def __ne__(self, other):
        return type(self) != type(other) or not self.__eq__(other)

    def __str__(self):
        return str([ "Card(%d, %s)" %
                     (x & PokerCards.VALUE_CARD_MASK,
                      (x & PokerCards.VISIBLE_CARD_MASK and "not visible") or "visible")
                     for x in self.cards ])
            
    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.cards)

    def nocard(self):
        return PokerCards.NOCARD

    def copy(self):
        other = PokerCards()
        other.cards = [ x for x in self.cards ]
        return other
        
    def getValue(self, card):
        value = None
        if type(card) is StringType:
            eval = PokerEval()
            try:
                value = eval.string2card(card)
            except RuntimeError:
                raise UserWarning, "Invalid card %s" %(card)
        else:
            if card != PokerCards.NOCARD:
                value = card & PokerCards.VALUE_CARD_MASK
                if (value < 0) or (value >= PokerCards.NB_CARD):
                    raise UserWarning, "Invalid card %s" %(card)
                
            value = card
                
        return value
        
    def set(self, cards):
        self.cards = []
        
        if isinstance(cards,PokerCards):
            self.cards = cards.cards[:]
            return
                
        if not type(cards) is ListType:
            cards = [cards]
            
        self.cards = map(self.getValue,cards)
            
    def add(self, card, visible):
        card_value = self.getValue(card)
        self.cards.append(card_value | ((not visible and PokerCards.NOT_VISIBLE_CARD) or PokerCards.VISIBLE_CARD))
        
    def allVisible(self):
        for i in xrange(len(self.cards)):
            self.cards[i] = visible_card(self.cards[i])
        
    def allHidden(self):
        for i in xrange(len(self.cards)):
            self.cards[i] = not_visible_card(self.cards[i])

    def hasCard(self, value):
        for card in self.cards:
            if value == self.nocard():
               if card == self.nocard():
                   return True
            elif card & PokerCards.VALUE_CARD_MASK == value:
                return True
        return False

    def areVisible(self):
        for card in self.cards:
            if card & PokerCards.NOT_VISIBLE_CARD:
                return False
        return True
        
    def areHidden(self):
        for card in self.cards:
            if is_visible(card):
                return False
        return True

    def areAllNocard(self):
        for card in self.cards:
            if card != PokerCards.NOCARD:
                return False
        return True
        
    def setVisible(self, value, visible):
        if value == self.nocard():
            return
            
        for i in xrange(len(self.cards)):
            if self.cards[i] & PokerCards.VALUE_CARD_MASK == value:
                if visible:
                    self.cards[i] = visible_card(value)
                else:
                    self.cards[i] = not_visible_card(value)

    def tolist(self, show_all):
        result = []
        for card in self.cards:
            if is_visible(card) or show_all and card != PokerCards.NOCARD:
                result.append(card_value(card))
            else:
                result.append(self.nocard())
        return result

    def toRawList(self):
        return self.cards[:]

    def getVisible(self):
        return filter(lambda card: is_visible(card), self.cards)
    
    def isEmpty(self):
        return len(self.cards) == 0

    def len(self):
        return len(self.cards)

    def loseNotVisible(self):
        self.cards = map(lambda card: card & PokerCards.NOT_VISIBLE_CARD and PokerCards.NOCARD or card, self.cards)
