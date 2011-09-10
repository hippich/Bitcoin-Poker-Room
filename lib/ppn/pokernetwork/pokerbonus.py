#
# Copyright (C) 2011 Pavel Karoukin <pavel@karoukin.us>
#                1st May str., Borisov, Belarus, 222518
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
#  Pavel Karoukin <pavel@karoukin.us>
#
# 

import math

class PokerBonus:

    def __init__(self):

        self.position_rules = {
            2: { 0: 120, 1: 10 },
            3: { 0: 100, 1: 20, 2: 10 },
            4: { 0: 80, 1: 40, 2: 20, 3: 10 },
            5: { 0: 80, 1: 60, 2: 40, 3: 20, 4: 10 },
            6: { 0: 100, 1: 80, 2: 60, 3: 40, 4: 20, 5: 10 },
            7: { 0: 120, 1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 10 },
            8: { 0: 120, 1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 10, 7: 10 },
            9: { 0: 120, 1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 10, 7: 10, 8: 10 },
            10: { 0: 120, 1: 100, 2: 80, 3: 60, 4: 40, 5: 20, 6: 10, 7: 10, 8: 10, 9: 10 }
        }
        
    
    def message(self, string):
        print "PokerBonus: " + string

    def getPoints(self, serial, game, rake):

        points = 0
        
        # Position-based bonus points calculation.
        player_position = game.player_list.index(serial)
        total_players = len(game.player_list)

        position_bonus = self.position_rules[total_players][player_position]
        position_points = float(rake) / 100 * position_bonus

        self.message(
            "Serial: %d in position %d/%d, game: %d, rake: %d, position points awarded: %d with %.4f%% bonus" % 
            ( serial, player_position, total_players, game.id, rake, position_points, position_bonus )
        )

        points += position_points
        
        return points
