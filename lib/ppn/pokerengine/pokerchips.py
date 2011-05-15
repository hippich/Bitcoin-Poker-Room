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
import sys
from types import *

MAX_CHIPS_PER_STACK = 23
INT2CHIPS_FACTOR = 0.3

class PokerChips:

    def __init__(self, values, what = False):
        self.remainder = 0
        self.values = values
        self.size = len(self.values)
        if what == False:
            self.reset()
            return
        
        if type(what) is IntType or type(what) is LongType:
            ( self.chips, self.remainder ) = PokerChips.int2chips(values, INT2CHIPS_FACTOR, what)
            self.limitChips()
        elif type(what) is ListType:
            self.chips = what[:]
            self.remainder = 0
            self.limitChips()
        else:
            self.chips = what.chips[:]
            self.remainder = what.remainder

    def __eq__(self, other):
        if isinstance(other, PokerChips):
            return self.chips == other.chips and self.remainder == other.remainder
        else:
            return False

    def __ne__(self, other):
        if isinstance(other, PokerChips):
            return self.chips != other.chips or self.remainder != other.remainder
        else:
            return True

    def __str__(self):
        return "PokerChips(%s) = %d (-%d)" % (self.chips, self.toint(), self.remainder)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__, self.chips)

    def copy(self):
        return PokerChips(self.values, self)
    
    def reset(self):
        self.chips = [ 0 ] * self.size
        self.remainder = 0

    def set(self, chips):
        #
        # Must copy because if chips is a PokerChips object it
        # will be a reference to a chips data member used in another
        # object.
        #
        converted = PokerChips.convert(self.values, chips)
        self.chips = converted.chips
        self.remainder = converted.remainder
        self.limitChips()

    def convert(values, what):
        remainder = 0
        if type(what) is IntType or type(what) is LongType:
            ( what, remainder ) = PokerChips.int2chips(values, INT2CHIPS_FACTOR, what)
        if type(what) is ListType:
            chips = PokerChips(values, what)
            chips.remainder += remainder
            return chips
        else:
            return what
        
    convert = staticmethod(convert)

    def add(self, other):
        other = PokerChips.convert(self.values, other)
        self.chips = [ self.chips[i] + other.chips[i] for i in xrange(self.size) ]
        self.remainder += other.remainder
        self.limitChips()

    def subtract(self, other):
        other = PokerChips.convert(self.values, other)
        chips = [ self.chips[i] - other.chips[i] for i in xrange(self.size) ]
        self.remainder -= other.remainder
        if len(filter(lambda x: x < 0, chips)) != 0 or self.remainder < 0:
            res = self.toint() - other.toint()
            if res < 0:
                self.reset()
            else:
                self.set(res)
        else:
            self.chips = chips

    def toint(self):
        return int(sum([ self.chips[i] * self.values[i] for i in xrange(self.size) ])) + self.remainder

    def tolist(self):
        chips = self.chips[:]
        list = []
        for value in self.values:
            count = chips.pop(0)
            if count > 0:
                list.append(value)
                list.append(count)

        if self.remainder > 0:
            if list:
                if list[0] == 1:                
                    # Can not be tested
                    # If the first value is equal to 1, the remainder can not be different than 0
                    raise UserWarning, "pokerchips.py:tolist unexpected remainder > 0 when first chip value is 1 : " + str(self) #pragma: no cover
                else:
                    list.insert(0, self.remainder)
                    list.insert(0, 1)
            else:
                list = [ 1, self.remainder ]
        
        return list

    def tostring(value):
        string = str(value)
        if value == 0:
            return string
        elif value < 10:
            return "0.0" + string
        elif value < 100:
            return "0." + string
        elif value % 100 == 0:
            return string[:-2]
        else:
            return string[:-2] + '.' + string[-2:]

    tostring = staticmethod(tostring)
                     
    def tofloat(value):
        return value / 100.0

    tofloat = staticmethod(tofloat)
    
    def int2chips(values, factor, money):

        if len(values) > 0:
            chips = [0] * len(values)

            for i in range(len(values) - 1, -1, -1):
                if i == 0:
                    to_distribute = money
                else:
                    to_distribute = money - int(values[i] / factor)
                if to_distribute > 0:
                    chips[i] = to_distribute / values[i]
                    money -= to_distribute - to_distribute % values[i]
        else:
            chips = []

        return ( chips, money )

    int2chips = staticmethod(int2chips)

    def limitChips(self):
        def lcm(a, b):
            def gcm(x, y):
                if y == 0:
                    return x
                else:
                    return gcm(y, x % y)
            return (a * b) / gcm(a, b)
        for i in xrange(len(self.chips) - 1):
            if self.chips[i] > MAX_CHIPS_PER_STACK:
                _lcm = lcm(self.values[i], self.values[i + 1])
                too_many = ( self.chips[i] - MAX_CHIPS_PER_STACK ) * self.values[i]
                moving = too_many - too_many % _lcm
                if moving > 0:
                    self.chips[i] -= moving / self.values[i]
                    self.chips[i + 1] += moving / self.values[i + 1]
