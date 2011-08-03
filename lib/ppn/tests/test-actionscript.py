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
sys.path.insert(0, "..")

import unittest
import simplejson
from struct import pack, unpack, calcsize

from pokernetwork import pokerclientpackets

class ActionScriptGenerator:
    def __init__(self, type):
        self.type = type

    @staticmethod
    def pack_type2as_type(pack_type):
        if pack_type in ('I', 'B', 'b', 'H', 'c', 'bool', 'cbool', 'Bnone'):
            return 'int'
        elif pack_type in ('s', 'j'):
            return 'String'
        elif pack_type in ('Bl', 'Hl', 'Il', 'pl', 'players'):
            return 'Array'
        elif pack_type in ('money'):
            return 'Dictionary'
        else:
            raise UserWarning, "unknown type " + pack_type

    @staticmethod
    def field2as_unpack(field):
        (variable, default, pack_type) = field
        code = []
        if pack_type in ('I', 'c'):
            code.append('this.' + variable + " = bytes.readUnsignedInt();")
        elif pack_type == 'H':
            code.append('this.' + variable + " = bytes.readUnsignedShort();")
        elif pack_type in ('B', 'bool', 'cbool', 'Bnone'):
            code.append('this.' + variable + " = bytes.readUnsignedByte();")
        elif pack_type == 'b':
            code.append('this.' + variable + " = bytes.readUnsignedByte();")
            code.append('if(this.' + variable + " == 255) this." + variable + " = -1")
        elif pack_type in ('s', 'j'):
            code.append('{')
            code.append('\tvar size:int = bytes.readUnsignedShort();')
            code.append('\tthis.' + variable + ' = bytes.readUTFBytes(size);')
            code.append('}')
        elif pack_type in ('Il', 'Hl', 'Bl'):
            code.append('{')
            code.append('\tvar size:int = bytes.readUnsignedByte();')
            code.append('\tfor(var i:int = 0; i < size; i++)')
            code.append('\t{')
            if pack_type == 'Il':
                code.append('\t\tthis.' + variable + ".push(bytes.readUnsignedInt());")
            elif pack_type == 'Hl':
                code.append('\t\tthis.' + variable + ".push(bytes.readUnsignedShort());")
            elif pack_type == 'Bl':
                code.append('\t\tthis.' + variable + ".push(bytes.readUnsignedByte());")
            code.append('\t}')
            code.append('}')
        elif pack_type in ('players',):
            code.append('{')
            code.append('\tvar nplayers:int = bytes.readUnsignedShort();')
            code.append('\tthis.' + variable + ' = new Array();')
            code.append('\tfor(var i:int = 0; i < nplayers; i++)')
            code.append('\t{')
            code.append('\t\tvar size:int = bytes.readUnsignedByte();')
            code.append('\t\tvar player:Array = new Array();')
            code.append('\t\tplayer.push(bytes.readUTFBytes(size));')
            code.append('\t\tplayer.push(bytes.readUnsignedInt());')
            code.append('\t\tplayer.push(bytes.readUnsignedByte());')
            code.append('\t\tthis.' + variable + ".push(player);")
            code.append('\t}')
            code.append('}')
        elif pack_type in ('money',):
            code.append('{')
            code.append('\tvar ncurrencies:int = bytes.readUnsignedShort();')
            code.append('\tthis.' + variable + ' = new Dictionary();')
            code.append('\tfor(var i:int = 0; i < ncurrencies; i++)')
            code.append('\t{')
            code.append('\t\tvar currency:Array = new Array();')
            code.append('\t\tvar id:int = bytes.readUnsignedInt();')
            code.append('\t\tcurrency.push(bytes.readUnsignedInt()); // bankroll')
            code.append('\t\tcurrency.push(bytes.readUnsignedInt()); // ingame')
            code.append('\t\tcurrency.push(bytes.readUnsignedInt()); // points')
            code.append('\t\tthis.' + variable + "[id] = currency;")
            code.append('\t}')
            code.append('}')
        elif pack_type in ('pl',):
            code.append('{')
            code.append('\tvar npackets:int = bytes.readUnsignedByte();')
            code.append('\tthis.' + variable + ' = new Array();')
            code.append('\tfor(var i:int = 0; i < npackets; i++)')
            code.append('\t{')
            code.append('\t\tvar type:int = bytes.readUnsignedByte();')
            code.append('\t\tvar length:int = bytes.readUnsignedShort();')
            code.append('\t\tvar packet:Packet = new Packet.types[type]();')
            code.append('\t\tbytes.position -= 3; // rewind to the beginning of packet')
            code.append('\t\tpacket.bytes = new ByteArray(bytes.readUnsignedBytes(length));')
            code.append('\t\tpacket.unpack();')
            code.append('\t\tthis.' + variable + ".push(packet);")
            code.append('\t}')
            code.append('}')
        else:
            code.append("// implement " + variable + " of type " + pack_type)
        return code
            
    @staticmethod
    def field2as_pack(field):
        (variable, default, pack_type) = field
        code = []
        if pack_type in ('I', 'c'):
            code.append('bytes.writeUnsignedInt(this.' + variable + ');')
        elif pack_type == 'H':
            code.append('bytes.writeUnsignedShort(this.' + variable + ');')
        elif pack_type in ('B', 'bool', 'cbool', 'Bnone'):
            code.append('bytes.writeUnsignedByte(this.' + variable + ');')
        elif pack_type == 'b':
            code.append('if(this.' + variable + ' == -1)')
            code.append('\tbytes.writeUnsignedByte(255);')
            code.append('else')
            code.append('\tbytes.writeUnsignedByte(this.' + variable + ');')
        elif pack_type in ('s', 'j'):
            code.append('bytes.writeUnsignedShort(this.' + variable + '.length);')
            code.append('bytes.writeUTFBytes(this.' + variable + ', this.' + variable + '.length)')
        elif pack_type in ('Il', 'Hl', 'Bl'):
            code.append('bytes.writeUnsignedByte(this.' + variable + '.length);')
            code.append('for(var i:int = 0; i < this.' + variable + '.length; i++)')
            code.append('{')
            if pack_type == 'Il':
                code.append('\tbytes.writeUnsignedInt(this.' + variable + ');')
            elif pack_type == 'Hl':
                code.append('\tbytes.writeUnsignedShort(this.' + variable + ');')
            elif pack_type == 'Bl':
                code.append('\tbytes.writeUnsignedByte(this.' + variable + ');')
            code.append('}')
        elif pack_type in ('players',):
            code.append('bytes.writeUnsignedShort(this.' + variable + '.length);')
            code.append('for(var i:int = 0; i < this.' + variable + '.length; i++)')
            code.append('{')
            code.append('\t\tvar player:Array = this.' + variable + '[i];')
            code.append('\tbytes.writeUnsignedByte(player[0].length);')
            code.append('\tbytes.writeUTFBytes(player[0])')
            code.append('\tbytes.writeUnsignedInt(player[1]);')
            code.append('\tbytes.writeUnsignedByte(player[2]);')
            code.append('}')
        elif pack_type in ('money',):
            code.append('// money not implemented')
        elif pack_type in ('pl',):
            code.append('// pl not implemented')
        else:
            code.append("// implement " + variable + " of type " + pack_type)
        return code
            
    @staticmethod
    def field2as_calcsize(field):
        (variable, default, pack_type) = field
        code = []
        if pack_type in ('I', 'c'):
            code.append('size += 4; // ' + variable)
        elif pack_type == 'H':
            code.append('size += 2; // ' + variable)
        elif pack_type in ('B', 'bool', 'cbool', 'Bnone', 'b'):
            code.append('size += 1; // ' + variable)
        elif pack_type in ('s', 'j'):
            code.append('size += 2 + this.' + variable + '.length;')
        elif pack_type in ('Il', 'Hl', 'Bl'):
            code = []
            code.append('size += 1; // length of ' + variable)
            if pack_type == 'Il':
                code.append('size += 4 * this.' + variable + '.length;')
            elif pack_type == 'Hl':
                code.append('size += 2 * this.' + variable + '.length;')
            elif pack_type == 'Bl':
                code.append('size += 1 * this.' + variable + '.length;')
        elif pack_type in ('players',):
            code.append('// players not implemented')
        elif pack_type in ('money',):
            code.append('// money not implemented')
        elif pack_type in ('pl',):
            code.append('// pl not implemented')
        else:
            code.append("// implement " + variable + " of type " + pack_type)
        return code
            
    def generate(self):
        if self.type.type in ( pokerclientpackets.PACKET_NONE,
                               pokerclientpackets.PACKET_BOOTSTRAP ):
            return
        info = self.type.info[2:]
        print "// code for " + pokerclientpackets.PacketNames[self.type.type] + " "  + str(info)
        print "public class " + self.type.__name__ + " extends Packet"
        print "{"
        for (variable, default, pack_type) in info:
            if pack_type == 'no net':
                continue
            print "\tpublic var " + variable + ":" + self.pack_type2as_type(pack_type) + ";"
        print 
        print "\tpublic override function unpack(bytes:ByteArray):ByteArray"
        print "\t{"
        print "\t\tbytes = super.unpack(bytes);"
        for field in info:
            if field[2] == 'no net':
                continue
            for line in self.field2as_unpack(field):
                print "\t\t" + line
        print "\t\treturn bytes;"
        print "\t}"
        print 
        print "\tpublic override function pack():ByteArray"
        print "\t{"
        print "\t\tvar bytes:ByteArray = super.pack();"
        for field in info:
            if field[2] == 'no net':
                continue
            for line in self.field2as_pack(field):
                print "\t\t" + line
        print "\t\treturn bytes;"
        print "\t}"
        print 
        print "\tpublic override function calcsize():int"
        print "\t{"
        print "\t\tvar size:int = super.calcsize();"
        for field in info:
            if field[2] == 'no net':
                continue
            for line in self.field2as_calcsize(field):
                print "\t\t" + line
        print "\t\treturn size;"
        print "\t}"

        print "}"
        
    
class ActionScriptGeneratorTestCase(unittest.TestCase):

    #--------------------------------------------------------------    
    def test_all(self):
        classes = []
        for type in xrange(0, 255):
            if pokerclientpackets.PacketFactory.has_key(type):
                c = pokerclientpackets.PacketFactory[type].__name__
                classes.append(c)
            else:
                classes.append('null')
        print "Packet.types = Array(" + ", ".join(classes) + ");"

        print """
public class Packet
{
        public static var types:Array = new Array();

        public var type:int;
        public var length:int;

	public function unpack(bytes:ByteArray):ByteArray
        {
    		this.type = bytes.readUnsignedByte();
    		this.length = bytes.readUnsignedShort();
                return bytes;
        }

	public function pack():ByteArray
        {
    		var bytes:ByteArray = new ByteArray();
                bytes.writeUnsignedByte(this.type);
                bytes.writeUnsignedShort(this.calcsize());
                return bytes;
        }

	public function calcsize():int
        {
                return 3;
        }
}
"""
        for type in xrange(0, 255):
            if pokerclientpackets.PacketFactory.has_key(type):
                as = ActionScriptGenerator(pokerclientpackets.PacketFactory[type])
                as.generate()

#--------------------------------------------------------------
def GetTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ActionScriptGeneratorTestCase))
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
# compile-command: "( cd .. ; ./config.status tests/test-actionscript.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/packets.py' TESTS='coverage-reset test-actionscript.py coverage-report' check )"
# End:
