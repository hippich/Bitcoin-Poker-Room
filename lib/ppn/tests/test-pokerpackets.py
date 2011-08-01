#!/usr/bin/python
# -*- mode: python -*-
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
import sys, os
sys.path.insert(0, "..")
sys.path.insert(0, ".")
sys.path.insert(0, "..")

import unittest

from pokernetwork import pokerpackets
import testpackets

class PokerPacketsTestCase(testpackets.PacketsTestBase):

    @staticmethod
    def polute(packet):
        if packet.type == pokerpackets.PACKET_POKER_USER_INFO:
            packet.money = {5: (1,2,3), 10: (10,11,12)}
        else:
            testpackets.PacketsTestBase.polute(packet)
        
    def packUnpack(self, packet, field):
        packed = packet.pack()
        other_packet = pokerpackets.PacketFactory[packet.type]()
        other_packet.unpack(packed)
        self.assertEqual(packed, other_packet.pack())
        self.assertEqual(packet.__dict__[field], other_packet.__dict__[field])
        info_packet = pokerpackets.PacketFactory[packet.type]()
        info_packet.infoUnpack(packed);
        self.assertEqual(packed, info_packet.infoPack())
        
    #--------------------------------------------------------------    
    def test_all(self):
        verbose = int(os.environ.get('VERBOSE_T', '-1'))
        for type_index in pokerpackets._TYPES:
            if pokerpackets.PacketFactory.has_key(type_index):
                if verbose > 0:
                    print pokerpackets.PacketNames[type_index]
                self.packetCheck(type = pokerpackets.PacketFactory[type_index])

    #--------------------------------------------------------------    
    def test_PacketPokerPlayerArrive(self):
        packet = pokerpackets.PacketPokerPlayerArrive(seat = 1)
        self.packUnpack(packet, 'seat')
        packet = pokerpackets.PacketPokerPlayerArrive(blind = None)
        self.packUnpack(packet, 'blind')
        packet = pokerpackets.PacketPokerPlayerArrive(blind = False)
        self.packUnpack(packet, 'blind')

    #--------------------------------------------------------------    
    def test_PacketPokerUserInfo(self):
        packet = pokerpackets.PacketPokerUserInfo(money = {1: (2, 3, 4), 10: (20, 30, 40)})
        self.packUnpack(packet, 'money')
        self.failUnless("20/30/40" in str(packet))

    #--------------------------------------------------------------    
    def test_PacketPokerPlayersList(self):
        packet = pokerpackets.PacketPokerPlayersList(players = [('name', 10, 20)])
        self.packUnpack(packet, 'players')
        self.failUnless("name|10|20" in str(packet))
        
    #--------------------------------------------------------------    
    def test_PacketPokerMoneyTransfert(self):
        packet = pokerpackets.PacketPokerCashIn(note = ('url', 10, 'name', 20))
        self.packUnpack(packet, 'name')
        self.failUnless("name = name" in str(packet))        

    #--------------------------------------------------------------    
    def test_verifyfactory(self):
        from pokernetwork.pokerpackets import PacketNames, PacketFactory
        for packid in PacketNames.keys():
            self.failUnless(PacketFactory.has_key(packid))
            self.assertEquals(PacketFactory[packid].type, packid)
        for packid in PacketFactory.keys():
            self.failUnless(PacketNames.has_key(packid))
    #--------------------------------------------------------------    
    def test_PacketPokerTable(self):
        packet = pokerpackets.PacketPokerTable(tourney_serial = 2)
        self.failUnless("tourney_serial = 2" in str(packet))
    #--------------------------------------------------------------    
    def test_PacketPokerSetLocale(self):
        packet = pokerpackets.PacketPokerSetLocale(serial = 42, locale = "fr_FR", game_id = 100)
        self.packUnpack(packet, 'game_id')
        self.failUnless("100" in str(packet))
#--------------------------------------------------------------    
    def test_verifyfactory(self):
        from pokernetwork.pokerpackets import PacketNames, PacketFactory
        for packid in PacketNames.keys():
            self.failUnless(PacketFactory.has_key(packid))
            self.assertEquals(PacketFactory[packid].type, packid)
        for packid in PacketFactory.keys():
            self.failUnless(PacketNames.has_key(packid))
                            


#--------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PokerPacketsTestCase))
    return suite
    
#--------------------------------------------------------------
def Run(verbose = 2):
    return unittest.TextTestRunner(verbosity=verbose).run(GetTestSuite())
    
#--------------------------------------------------------------
if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokerpackets.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerpackets.py' TESTS='coverage-reset test-pokerpackets.py coverage-report' check )"
# End:
