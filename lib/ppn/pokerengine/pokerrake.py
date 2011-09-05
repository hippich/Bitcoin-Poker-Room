#
# Copyright (C) 2006 - 2010 Loic Dachary <loic@dachary.org>
# Copyright (C) 2006 Mekensleep
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
#
from os import path
from decimal import *
import imp

class PokerRake:
    def __init__(self, game):
        self.change = Decimal('0')

    def getRake(self, game):
        """ implementation constraint of compute is as follows :
        for any game1.pot greater than game2.pot
        compute(game1.pot) MUST be greater or equal to compute(game2.pot) """
        if game.isTournament():
            return 0
        
        if game.getMaxBoardSize() > 0 and len(game.board.tolist(True)) == 0:
            if game.verbose >= 2: game.message("Rake: No Flop No Drop")
            return 0 # No Flop No Drop
        
        # TODO: Stud needs to handle 3rd street folds the same way

        if game.sitCount() == 2:
            absRakeCap = 500
            bbRakeCap = 5
        else:
            absRakeCap = 2500
            bbRakeCap = 10

        if game.blind_info:
            rakeCap = min(absRakeCap, game.blind_info["big"]*bbRakeCap)
        else:
            rakeCap = absRakeCap

        if game.verbose >= 2: game.message("Rake: calculated rake cap as %d units" % rakeCap)
        
        rakeablePot = (game.getPotAmount() - game.getUncalled())
        decimalRake = min(rakeCap, rakeablePot * Decimal('0.01')) + self.change


        if game.verbose >= 2: game.message("Rake: calculated rake from %d pot as %2.2f (%0.2f from change)" % (rakeablePot, decimalRake, self.change))

        self.change = decimalRake - decimalRake.to_integral_value(ROUND_DOWN)
        rake = int(decimalRake.to_integral_value(ROUND_DOWN))

        if game.verbose >= 2: game.message("Rake: taking %d rake" % rake)

        return max(0, rake)

_get_rake_instance = None

def get_rake_instance(game):
    global _get_rake_instance
    if _get_rake_instance == None:
        verbose = game.verbose
        for dir in game.dirs:
            file = dir + "/pokerrake.py"
            if path.exists(file):
                if verbose > 0: game.message("get_rake_instance: trying to load " + file)
                module = imp.load_source("user_defined_pokerrake", file)
                get_instance = getattr(module, "get_rake_instance")
                _get_rake_instance = get_instance
                break
            else:
                if verbose > 0: game.message("get_rake_instance: " + file + " does not exist")
        if _get_rake_instance == None:
            if verbose > 0: game.message("get_rake_instance: no pokerrake.py found in directories " + str(game.dirs))
            _get_rake_instance = lambda game: PokerRake(game)
        else:
            if verbose > 0: game.message("get_rake_instance: using custom implementation of get_rake_instance")
    return apply(_get_rake_instance, [game])
