#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C)       2009 Bradley M. Kuhn <bkuhn@ebb.org>
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
from struct import pack, unpack, calcsize

import testpackets

from pokerengine.pokercards import PokerCards
from pokerengine.pokerchips import PokerChips

from pokernetwork import packets
from pokernetwork import pokerclientpackets
from pokernetwork import OLDpokerclientpackets

class PokerClientPacketsTestCase(testpackets.PacketsTestBase):

    @staticmethod
    def copydict(packet):
        packet_dict = packet.__dict__.copy()
        if packet_dict.has_key('length'): del packet_dict['length']
        if packet_dict.has_key('type'): del packet_dict['type']
        return packet_dict

    def comparedict(self, packet, other_packet):
        packet_dict = self.copydict(packet)
        other_packet_dict = self.copydict(other_packet)
        self.assertEqual(packet_dict, other_packet_dict)

    def OLDpacketCheck(self, **kwargs):
        packet_type = kwargs['type']
        del kwargs['type']
        packet = packet_type(**kwargs)
        size = packet.calcsize()
        packed = packet.pack()
        self.assertEqual(size, len(packed))
        other_packet = packet_type()
        self.assertNotEqual(None, other_packet.unpack(packed))
        self.assertEqual(repr(packet), repr(other_packet))
        self.assertEqual(packet, other_packet)
        self.comparedict(packet, other_packet)
        self.assertEqual(packed, other_packet.pack())
        return packet
        
    #--------------------------------------------------------------    
    def test_packets(self):
        verbose = int(os.environ.get('VERBOSE_T', '-1'))
        for type in pokerclientpackets._TYPES:
            if pokerclientpackets.PacketFactory.has_key(type):
                if verbose > 0:
                    print pokerclientpackets.PacketNames[type]
                self.packetCheck(type = pokerclientpackets.PacketFactory[type])

    #--------------------------------------------------------------    
    def test_backward(self):
        for type_index in pokerclientpackets._TYPES:
            if type_index > 208:
                break
            self.assertEqual(pokerclientpackets.PacketFactory.has_key(type_index), OLDpokerclientpackets.PacketFactory.has_key(type_index))
            if pokerclientpackets.PacketFactory.has_key(type_index):
                if self.verbose > 0:
                    print pokerclientpackets.PacketNames[type_index]
                self.assertEqual(OLDpokerclientpackets.PacketNames[type_index], pokerclientpackets.PacketNames[type_index])
                self.OLDpacketCheck(type = OLDpokerclientpackets.PacketFactory[type_index])

                OLDtype = OLDpokerclientpackets.PacketFactory[type_index]
                type = pokerclientpackets.PacketFactory[type_index]
                #
                # Check that default fields are identical and set to the same values
                #
                OLDpacket = OLDtype()
                packet = type()
                if self.verbose > 2:
                    print "%s: %s == %s" % ( pokerclientpackets.PacketNames[type_index], str(self.copydict(OLDpacket)), str(self.copydict(packet)) )
                self.comparedict(packet, OLDpacket)
                #
                # Check that the serialization of packets with pack/unpack functions
                # did not change.
                #
                if OLDtype.__dict__.has_key('pack'):
                    if self.verbose > 0:
                        print pokerclientpackets.PacketNames[type_index] + " test pack"
                    self.assertEqual(OLDpacket.pack(), packet.pack())
                else:
                    if self.verbose > 0:
                        print pokerclientpackets.PacketNames[type_index] + " no pack function"

    #--------------------------------------------------------------    
    def test_chips2amount(self):
        self.assertEqual(10, pokerclientpackets.chips2amount([1, 2, 4, 2]))

    def test_chips2amount_old(self):
        self.assertEqual(10, OLDpokerclientpackets.chips2amount([1, 2, 4, 2]))

    def defineTestPacket(self):
        d = {}
        d['PacketFactory'] = {}
        d['PacketNames'] = {}
        
        class TestPacket(packets.Packet):
            info = packets.Packet.info + (('f1' , [1, 10], 'c'),
                                          ('f2' , [PokerChips([1],[3]), PokerCards([255,255]), ["a", 1]], 'j'),
                                          )
            fields = ( "\x0a", # type
                       "\0\0", # length
                       "\0\0\0\x0a", # f1
                       '\x00-[["Chips", 3], ["Cards", 255, 255], ["a", 1]]', # f2
                       )
            binary = fields[0] + pack('!H', len("".join(fields))) + "".join(fields[2:])

        d = {}
        d['PacketFactory'] = {}
        d['PacketNames'] = {}
        packets.Packet.infoDeclare(d, TestPacket, packets.Packet, 'NAME', 10)
        return TestPacket

    def test_infoPack(self):
        type = self.defineTestPacket()
        packet = type()
        self.assertEqual(type.binary, packet.infoPack())

    def test_infoPackFail(self):
        type = self.defineTestPacket()
        class Foo:
            pass
        type.info = packets.Packet.info + (('f1' , Foo(), 'j'),)
        self.failUnlessRaises(TypeError, type)

    def test_infoUnpack(self):
        type = self.defineTestPacket()
        packet = type()
        packet.infoUnpack(type.binary)
        self.failUnless(isinstance(packet.f2[0], PokerChips))
        self.failUnless(isinstance(packet.f2[1], PokerCards))
        self.assertEqual(type.binary, packet.infoPack())

    def test_infoCalcsize(self):
        type = self.defineTestPacket()
        packet = type()
        self.assertEqual(len(type.binary), packet.infoCalcsize())

#--------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PokerClientPacketsTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-pokerclientpackets.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokerclientpackets.py ../pokernetwork/OLDpokerclientpackets.py' TESTS='coverage-reset test-pokerclientpackets.py coverage-report' check )"
# End:
