#!@PYTHON@
# -*- py-indent-offset: 4; coding: iso-8859-1; mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
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
# Tweak poker-engine & twisted to use a fake clock so that
# the tests are immune to the performances of the machine
# running the test, even when testing timeouts or other delays.
#
import time, os
from twisted.python import runtime
from twisted.internet import reactor, base
from pokerengine import pokertournament

#
# unless otherwise specified, implementation is for twisted versions < 8.0.1
#
_seconds_value = time.time()
def _seconds_reset():
    global _seconds_original
    _seconds_original = _seconds_value
_seconds_reset()
_seconds_verbose = int(os.environ.get('VERBOSE_T', '3'))
def _seconds_tick():
    global _seconds_value
    if _seconds_verbose > 3:
        print "tick: %.01f" % ( _seconds_value - _seconds_original )
    _seconds_value += 0.1
    return _seconds_value

reactor.seconds = _seconds_tick # twisted >= 8.0.1
base.seconds = _seconds_tick
#
# select timeout must return immediately, it makes no sense
# to wait while testing.
#
reactor.timeout = lambda: 0
runtime.seconds = _seconds_tick
pokertournament.tournament_seconds = _seconds_tick

from pokernetwork.pokerlock import PokerLock
PokerLock.acquire_sleep = 0.01
