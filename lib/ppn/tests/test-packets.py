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
import simplejson
from struct import pack, unpack, calcsize

import testpackets

from pokernetwork import packets

class PacketsTestCase(testpackets.PacketsTestBase):

    def test_unpack(self):
        class TestPacket(packets.Packet):
            def __init__(self):
                self.type = 77

        class TestPacketList(packets.PacketList):
            def __init__(self):
                self.type = 254
                packets.PacketList.__init__(self, packets = [TestPacket()])

        self.assertEqual(None, self.packetCheck(type = TestPacketList))

        class TestPacketList(packets.PacketList):
            def __init__(self):
                self.type = 253
                packets.PacketList.__init__(self, packets = [packets.Packet()])

            def unpack(self, block):
                packets.PacketList.unpack(self, block[:-3])

        self.assertEqual(None, self.packetCheck(type = TestPacketList))
        
    #--------------------------------------------------------------    
    def test_all(self):
        for type_index in packets._TYPES:
            if packets.PacketFactory.has_key(type_index):
                if self.verbose > 0:
                    print packets.PacketNames[type_index]
                self.packetCheck(type = packets.PacketFactory[type_index])

        class TestPacketList(packets.PacketList):
            def __init__(self):
                packets.PacketList.__init__(self, packets = [packets.Packet()])
        self.packetCheck(type = TestPacketList)

        packets.PacketNames[253] = 'TestPacketFieldList'
        
        class TestPacketFieldList(packets.Packet):
            type = 253

            info = packets.Packet.info + ( ('serials', [1], 'Il'), )
            
            serials = []

            format_element = "!I"

            def __init__(self, *args, **kwargs):
                self.serials = kwargs.get("serials", [])

            def pack(self):
                block = packets.Packet.pack(self)
                block += self.packlist(self.serials, TestPacketFieldList.format_element)
                return block

            def unpack(self, block):
                block = packets.Packet.unpack(self, block)
                (block, self.serials) = self.unpacklist(block, TestPacketFieldList.format_element)
                return block

            def calcsize(self):
                return packets.Packet.calcsize(self) + self.calcsizelist(self.serials, TestPacketFieldList.format_element)

            def __str__(self):
                return packets.Packet.__str__(self) + " serials = %s" % self.serials

        self.packetCheck(type = TestPacketFieldList, serials = [1])

    def defineTestPacket(self):
        d = {}
        d['PacketFactory'] = {}
        d['PacketNames'] = {}
        
        class TestPacket(packets.Packet):
            info = packets.Packet.info + (('b' , 10, 'B'),
                                          ('a', 20, 'I'),
                                          ('c', 'ABC', 's'),
                                          ('d', [1,2,3], 'Bl'),
                                          ('e', -1, 'b'),
                                          ('f', None, 'no net'),
                                          ('g', [{'a': [1,2]}, None, True], 'j'),
                                          ('h', [packets.PacketPing(), packets.PacketPing()], 'pl'),
                                          ('i', True, 'bool'),
                                          ('i1', False, 'bool'),
                                          ('j', 'n', 'cbool'),
                                          ('j1', 'y', 'cbool'),
                                          ('k', None, 'Bnone'),
                                          )
            fields = ( "\x0a", # type
                       "\0\0", # length
                       "\x02", # b
                       "\0\0\0\x01", # a
                       "\0\x03ABC", # c
                       "\x03\x01\x02\x03", # d
                       "\xff", # e
                       '\x00\x1b[{"a": [1, 2]}, null, true]', # g
                       "\x00\x02\x05\x00\x03\x05\x00\x03", # h
                       "\x01", # i
                       "\x00", # i1
                       "\x00", # j
                       "\x01", # j1
                       "\xff", # k
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
        packet.a = 1
        packet.b = 2
        self.assertEqual(type.binary, packet.infoPack())

    def test_infoUnpack(self):
        type = self.defineTestPacket()
        packet = type()
        packet.infoUnpack(type.binary)
        self.assertEqual(1, packet.a)
        self.assertEqual(2, packet.b)

    def test_infoUnpackJSON(self):
        type = self.defineTestPacket()
        packet = type()
        class TestJSON(simplejson.JSONEncoder):
            @staticmethod
            def decode_objects(something):
                return something
        old_JSON = packets.Packet.JSON
        packets.Packet.JSON = TestJSON()
        packet.infoUnpack(type.binary)
        packets.Packet.JSON = old_JSON
        self.assertEqual(1, packet.a)
        self.assertEqual(2, packet.b)

    def test_infoCalcsize(self):
        type = self.defineTestPacket()
        packet = type()
        self.assertEqual(len(type.binary), packet.infoCalcsize())

    def test_infoDeclare(self):
        d = {}
        d['PacketFactory'] = {}
        d['PacketNames'] = {}
        class TestPacketClass(packets.Packet):
            pass
        index = 11
        packets.Packet.infoDeclare(d, TestPacketClass, packets.Packet, 'NAME', index)
        self.assertEqual(TestPacketClass, d['PacketFactory'][index])
        self.assertEqual('NAME', d['PacketNames'][index])
        self.assertEqual(TestPacketClass.type, index)
        test_packet = TestPacketClass()
        packet = packets.Packet()
        self.assertEqual(packet.calcsize(), test_packet.calcsize())
        self.assertEqual("AUTH_REQUEST  type = 11 length = 3", str(test_packet))

    def test_unpackpackets_errors(self):
        #
        # Unknown packet type
        #
        self.assertEqual(None, packets.Packet.unpackpackets('\x00\x01\xff\x00\x03'));
        #
        # Pretend there are 2 packets although only one is present
        #
        self.assertEqual(None, packets.Packet.unpackpackets('\x00\x02\x00\x00\x03'));

#--------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(PacketsTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-packets.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/packets.py' TESTS='coverage-reset test-packets.py coverage-report' check )"
# End:
