#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2004, 2005, 2006 Mekensleep <licensing@mekensleep.com>
#                                24 rue vieille du temple, 75004 Paris
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
#  Loic Dachary <loic@dachary.org>
#  Henry Precheur <henry@precheur.org> (2004)
#
from struct import pack, unpack, calcsize
import simplejson
from string import join

PacketFactory = {}
PacketNames = {}

PACKET_NONE = 0
PacketNames[PACKET_NONE] = "NONE"

def json_encode_decimal(obj):
    if isinstance(obj, decimal.Decimal):
        return str(obj)
    raise TypeError(repr(obj) + " is not JSON serializable")

class Packet:
    """

     Packet base class
    
    """
    JSON = simplejson.JSONEncoder(default=json_encode_decimal)
    
    type = PACKET_NONE
    length = -1
    format = "!BH"
    format_size = calcsize(format)

    format_list_length = "!B"

    def infoInit(self, **kwargs):
        info = self.info
        for (field, default, format) in self.info:
            if field == 'type':
                self.type = self.type # type is now in __dict__, for serialization 
            if not self.__dict__.has_key(field):
                self.__dict__[field] = kwargs.get(field, default)
        self.length = self.infoCalcsize()
        return None
            
    def pack(self):
        return pack(Packet.format, self.type, self.calcsize())

        
              
    def infoPack(self):
        blocks = []
        info = self.info
        self.length = self.infoCalcsize()
        for (field, default, format) in self.info:
            if format != 'no net':
                packer = self.format_info[format]['pack']
                blocks.append(packer(self.__dict__[field]))
        return "".join(blocks)
            
    def unpack(self, block):
        (self.type,self.length) = unpack(Packet.format, block[:Packet.format_size])
        return block[Packet.format_size:]

    def infoUnpack(self, block):
        blocks = []
        info = self.info
        for (field, default, format) in self.info:
            if format != 'no net':
                unpacker = self.format_info[format]['unpack']
                ( block, self.__dict__[field] ) = unpacker(block)
        return block

    @staticmethod
    def infoUnpackerb(block):
        value = unpack('B', block[0])[0]
        if value == 255: value = -1
        return ( block[1:], value )
    
    @staticmethod
    def infoPackerb(data):
        if data == -1: data = 255
        return pack('B', data)
    
    @staticmethod
    def infoUnpackerBnone(block):
        value = unpack('B', block[0])[0]
        if value == 255: value = None
        return ( block[1:], value )
    
    @staticmethod
    def infoPackerBnone(data):
        if data == None: data = 255
        return pack('B', data)
    
    @staticmethod
    def infoUnpackerBool(block):
        value = unpack('B', block[0])[0]
        if value != 0: value = True
        else: value = False
        return ( block[1:], value )
    
    @staticmethod
    def infoPackerBool(data):
        if data: data = 1
        else: data = 0
        return pack('B', data)
    
    @staticmethod
    def infoUnpackerCBool(block):
        value = unpack('B', block[0])[0]
        if value != 0: value = 'y'
        else: value = 'n'
        return ( block[1:], value )
    
    @staticmethod
    def infoPackerCBool(data):
        if data == 'y': data = 1
        else: data = 0
        return pack('B', data)
    
    def calcsize(self):
        return Packet.format_size

    def infoCalcsize(self):
        size = 0
        for (field, default, format) in self.info:
            if format != 'no net':
                calcsize = self.format_info[format]['calcsize']
                size += calcsize(self.__dict__[field])
        return size

    @staticmethod
    def packlist(l, format):
        block = pack(Packet.format_list_length, len(l))
        for value in l:
            block += pack(format, value)
        return block

    @staticmethod
    def unpacklist(block, format):
        (length,) = unpack(Packet.format_list_length, block[:calcsize(Packet.format_list_length)])
        format_size = calcsize(format)
        block = block[calcsize(Packet.format_list_length):]
        l = []
        for i in xrange(length):
            l.append(unpack(format, block[:format_size])[0])
            block = block[format_size:]
        return (block, l)

    @staticmethod
    def calcsizelist(l, format):
        return calcsize(Packet.format_list_length) + len(l) * calcsize(format)

    @staticmethod
    def packstring(string):
        return pack("!H", len(string)) + string

    @staticmethod
    def unpackstring(block):
        offset = calcsize("!H")
        (length,) = unpack("!H", block[:offset])
        string = block[offset:offset + length]
        return (block[offset + length:], string)

    @staticmethod
    def calcsizestring(string):
        return calcsize("!H") + len(string)

    @staticmethod
    def packjson(object):
        return Packet.packstring(Packet.JSON.encode(object))

    @staticmethod
    def unpackjson(block):
        ( block, string ) = Packet.unpackstring(block)
        object = simplejson.loads(string)
        if hasattr(Packet.JSON, 'decode_objects'):
            return ( block, Packet.JSON.decode_objects(object) )
        else:
            return ( block, object )

    @staticmethod
    def calcsizejson(object):
        return len(Packet.packjson(object))

    @staticmethod
    def packpackets(packets):
        block = pack('!H', len(packets))
        for packet in packets:
            block += packet.pack()
        return block

    @staticmethod
    def unpackpackets(block):
        (length,) = unpack('!H', block[0:2])
        block = block[2:]
        t = Packet()
        count = 0
        packets = []
        while len(block) > 0 and count < length:
            t.unpack(block)
            if not PacketFactory.has_key(t.type):
                print " *ERROR* unknown packet type %d (known types are %s)" % ( t.type, PacketNames)
                return None
            packet = PacketFactory[t.type]()
            block = packet.unpack(block)
            count += 1
            packets.append(packet)
        if count != length:
            print " *ERROR* expected a list of %d packets but found only %d" % ( length, count)
            return None
        return ( block, packets )

    @staticmethod
    def calcsizepackets(packets):
        return 2 + sum([ packet.calcsize() for packet in packets ])
    
    def __str__(self):
        return "type = %s(%d)" % ( PacketNames[self.type], self.type )

    def infoStr(self):
        strings = [ PacketNames[self.type] + " " ]
        for (field, default, format) in self.info:
            strings.append(field + " = " + str(self.__dict__[field]))
        return " ".join(strings)

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return isinstance(other, Packet) and self.type == other.type

    @staticmethod
    def infoDeclare(dictionary, type, base_type, name, index):
        dictionary['PacketNames'][index] = name
        dictionary['PacketFactory'][index] = type
        dictionary['PACKET_' + name] = index
        type.type = index
        type.__init__ = Packet.infoInit
        type.pack = Packet.infoPack
        type.unpack = Packet.infoUnpack
        type.calcsize = Packet.infoCalcsize
        type.__str__ = Packet.infoStr

Packet.info = (
    ('type', PACKET_NONE, 'B'),
    ('length', -1, 'H'),
    )
    
Packet.format_info = {
    #
    # Not transfered over the network.
    #
    'no net': None,
    #
    # Unsigned integer, int, 4 bytes, network order (big endian).
    # Example: 1 <=> \x00\x00\x00\x01
    #
    'I': {'pack': lambda data: pack('!I', data),
          'unpack': lambda block: ( block[4:], int(unpack('!I', block[:4])[0]) ),
          'calcsize': lambda data: 4,
          },
    #
    # Unsigned integer, char, 1 byte
    # Example: 1 <=> \x01
    #
    'B': {'pack': lambda data: pack('B', data),
          'unpack': lambda block: ( block[1:], unpack('B', block[0])[0] ),
          'calcsize': lambda data: 1,
          },
    #
    # Integer range [-1..254], char, 1 byte
    # -1 is 255
    # Example: 1 <=> \x01, -1 <=> \xff, 254 <=> \xfe
    #
    'b': {'pack': Packet.infoPackerb,
          'unpack': Packet.infoUnpackerb,
          'calcsize': lambda data: 1,
          },
    #
    # Integer range [0..254, None], char, 1 byte
    # None is 255
    # Example: 1 <=> \x01, None <=> \xff, 254 <=> \xfe
    #
    'Bnone': {'pack': Packet.infoPackerBnone,
              'unpack': Packet.infoUnpackerBnone,
              'calcsize': lambda data: 1,
          },
    #
    # Integer range [0,1], char, 1 byte
    # True is 1, False is 0
    # Example: True <=> \x01, False <=> \x00
    #
    'bool': {'pack': Packet.infoPackerBool,
             'unpack': Packet.infoUnpackerBool,
             'calcsize': lambda data: 1,
          },
    #
    # Integer range ['n','y'], char, 1 byte
    # 'y' is 1, 'n' is 0
    # Example: 'y' <=> \x01, 'n' <=> \x00
    #
    'cbool': {'pack': Packet.infoPackerCBool,
              'unpack': Packet.infoUnpackerCBool,
              'calcsize': lambda data: 1,
              },
    #
    # Unsigned integer, short, 2 bytes, network order (big endian).
    # Example: 1 <=> \x00\x01
    #
    'H': {'pack': lambda data: pack('!H', data),
          'unpack': lambda block: ( block[2:], unpack('!H', block[:2])[0] ),
          'calcsize': lambda data: 2,
          },
    #
    # Character string, length as a 2 bytes integer, network order (big endian)
    #   followed by the content of the string.
    # Example: "abc" <=> \x00\x03abc
    #          "a" <=> \x00\x01a
    #          "" <=> \x00\x00
    #
    's': {'pack': Packet.packstring,
          'unpack': Packet.unpackstring,
          'calcsize': Packet.calcsizestring,
          },
    #
    # JSon.org encoded string, length as a 2 bytes integer, network order (big endian)
    #   followed by the content of the string.
    # Example: "{'a':1}" <=> \x00\x07{'a':1}
    #
    'j': {'pack': Packet.packjson,
          'unpack': Packet.unpackjson,
          'calcsize': Packet.calcsizejson,
          },
    #
    # List of integer, length of the list as a 1 byte unsigned integer in the range [0-255]
    # Each integer is a 1 byte unsigned value in the range [0-255]
    # Example: [] <=> \x00
    #          [5] <=> \x01\x05
    #          [5, 255] <=> \x02\x05\xff
    #
    'Bl': {'pack': lambda data: Packet.packlist(data, 'B'),
           'unpack': lambda block: Packet.unpacklist(block, 'B'),
           'calcsize': lambda data: Packet.calcsizelist(data, 'B'),
           },
    #
    # List of integer, length of the list as a 1 byte unsigned integer in the range [0-255]
    # Each integer is a 2 bytes unsigned value in network order (big endian)
    # Example: [] <=> \x00
    #          [5] <=> \x01\x00\x05
    #          [5, 255] <=> \x02\x00\x05\x00\xff
    #
    'Hl': {'pack': lambda data: Packet.packlist(data, '!H'),
           'unpack': lambda block: Packet.unpacklist(block, '!H'),
           'calcsize': lambda data: Packet.calcsizelist(data, '!H'),
           },
    #
    # List of integer, length of the list as a 1 byte unsigned integer in the range [0-255]
    # Each integer is a 4 bytes unsigned value in network order (big endian)
    # Example: [] <=> \x00
    #          [5] <=> \x01\x00\x00\x00\x05
    #          [5, 255] <=> \x02\x00\x00\x00\x05\x00\x00\x00\xff
    #
    'Il': {'pack': lambda data: Packet.packlist(data, '!I'),
           'unpack': lambda block: Packet.unpacklist(block, '!I'),
           'calcsize': lambda data: Packet.calcsizelist(data, '!I'),
           },

    #
    # List of packets, length of the list as a short unsigned integer in the range [0-65535]
    # Each packet is a derived from Packet
    # Example: [] <=> \x00\x00
    #          [PacketPing()] <=> \x00\x01\x05\x00\x03
    #          [PacketPing(), PacketPing()] <=> \x00\x02\x05\x00\x03\x05\x00\x03
    #
    'pl': {'pack': Packet.packpackets,
           'unpack': Packet.unpackpackets,
           'calcsize': Packet.calcsizepackets,
           },
    }

PacketFactory[PACKET_NONE] = Packet

########################################

PACKET_STRING = 1
PacketNames[PACKET_STRING] = "STRING"

class PacketString(Packet):
    """

    Packet containing a single string
    
    """

    type = PACKET_STRING

    info = Packet.info + ( ( 'string', '', 's' ), )
                           
    def __init__(self, **kwargs):
        self.string = kwargs.get("string", "")

    def pack(self):
        return Packet.pack(self) + self.packstring(self.string)

    def unpack(self, block):
        block = Packet.unpack(self, block)
        (block, self.string) = self.unpackstring(block)
        return block

    def calcsize(self):
        return Packet.calcsize(self) + self.calcsizestring(self.string)

    def __str__(self):
        return Packet.__str__(self) + " string = %s" % self.string

PacketFactory[PACKET_STRING] = PacketString

########################################

PACKET_INT = 2
PacketNames[PACKET_INT] = "INT"

class PacketInt(Packet):
    """

    Packet containing an unsigned integer value
    
    """

    type = PACKET_INT

    info = Packet.info + ( ( 'value', 0, 'I' ), )
    
    format = "!I"
    format_size = calcsize(format)
    
    def __init__(self, **kwargs):
        self.value = kwargs.get("value", 0)

    def pack(self):
        return Packet.pack(self) + pack(PacketInt.format, self.value)

    def unpack(self, block):
        block = Packet.unpack(self, block)
        (self.value,) = unpack(PacketInt.format, block[:PacketInt.format_size])
        return block[PacketInt.format_size:]

    def calcsize(self):
        return Packet.calcsize(self) + PacketInt.format_size

    def __str__(self):
        return Packet.__str__(self) + " value = %d" % self.value

PacketFactory[PACKET_INT] = PacketInt

########################################

PACKET_ERROR = 3
PacketNames[PACKET_ERROR] = "ERROR"

class PacketError(Packet, Exception):
    """

    Packet describing an error
    
    """
    
    type = PACKET_ERROR

    info = Packet.info + ( ('message', 'no message', 's'),
                           ('code', 0, 'I' ),
                           ('other_type', PACKET_ERROR, 'B'),
                           )
    
    format = "!IB"
    format_size = calcsize(format)

    def __init__(self, **kwargs):
        self.message = kwargs.get("message", "no message")
        self.code = kwargs.get("code", 0)
        self.other_type = kwargs.get("other_type", PACKET_ERROR)
        Exception.__init__(self)

    def pack(self):
        return Packet.pack(self) + self.packstring(self.message) + pack(PacketError.format, self.code, self.other_type)

    def unpack(self, block):
        block = Packet.unpack(self, block)
        (block, self.message) = self.unpackstring(block)
        (self.code, self.other_type) = unpack(PacketError.format, block[:PacketError.format_size])
        return block[PacketError.format_size:]

    def calcsize(self):
        return Packet.calcsize(self) + self.calcsizestring(self.message) + PacketError.format_size

    def __str__(self):
        return Packet.__str__(self) + " message = %s, code = %d, other_type = %s" % (self.message, self.code, PacketNames[self.other_type])

PacketFactory[PACKET_ERROR] = PacketError

########################################

PACKET_ACK = 4
PacketNames[PACKET_ACK] = "ACK"

class PacketAck(Packet):
    ""

    type = PACKET_ACK

PacketFactory[PACKET_ACK] = PacketAck

########################################

PACKET_PING = 5
PacketNames[PACKET_PING] = "PING"

class PacketPing(Packet):
    ""

    type = PACKET_PING

PacketFactory[PACKET_PING] = PacketPing

########################################

PACKET_SERIAL = 6
PacketNames[PACKET_SERIAL] = "SERIAL"

class PacketSerial(Packet):
    """\
Semantics: the serial number of the authenticated user
           associated to the client after a PacketLogin
           was sent. This packet is sent to the client
           after the PacketAuthOk acknowledging the success
           of the authentication.

Direction: server => client

serial: the unique number associated to the user.
    """

    type = PACKET_SERIAL

    info = Packet.info + ( ('serial', 0, 'I'),
                           ('cookie', '', 'no net') )
    
    format = "!I"
    format_size = calcsize(format)
    
    def __init__(self, **kwargs):
        self.serial = kwargs.get("serial", 0)
        self.cookie = kwargs.get("cookie", "") # not present in client/server dialog

    def pack(self):
        return Packet.pack(self) + pack(PacketSerial.format, self.serial)

    def unpack(self, block):
        block = Packet.unpack(self, block)
        self.serial = int(unpack(PacketSerial.format, block[:PacketSerial.format_size])[0])
        return block[PacketSerial.format_size:]

    def calcsize(self):
        return Packet.calcsize(self) + PacketSerial.format_size

    def __str__(self):
        return Packet.__str__(self) + " serial = %d" % self.serial
        
PacketFactory[PACKET_SERIAL] = PacketSerial

########################################

PACKET_QUIT = 7
PacketNames[PACKET_QUIT] = "QUIT"

class PacketQuit(Packet):
    """
    Client tells the server it will leave
    """

    type = PACKET_QUIT

PacketFactory[PACKET_QUIT] = PacketQuit

########################################

PACKET_AUTH_OK = 8
PacketNames[PACKET_AUTH_OK] = "AUTH_OK"

class PacketAuthOk(Packet):
    """\
Semantics: authentication request succeeded.

Direction: server => client
    """

    type = PACKET_AUTH_OK

PacketFactory[PACKET_AUTH_OK] = PacketAuthOk

########################################

PACKET_AUTH_REFUSED = 9
PacketNames[PACKET_AUTH_REFUSED] = "AUTH_REFUSED"

class PacketAuthRefused(PacketError):
    """\
Semantics: authentication request was refused by the server.

Direction: server => client

message: human readable reason for the authentication failure
code: machine readable code matching the human readable message
      the list of which can be found in the PacketPokerSetAccount
      packet definition
other_type: the type of the packet that triggered the authentication
            error, i.e. PACKET_LOGIN
    """

    type = PACKET_AUTH_REFUSED

PacketFactory[PACKET_AUTH_REFUSED] = PacketAuthRefused

########################################

PACKET_LOGIN = 10
PacketNames[PACKET_LOGIN] = "LOGIN"

class PacketLogin(Packet):
    """\
Semantics: authentify user "name" with "password".

Direction: server <= client

If the user/password combination is valid, the
PacketAuthOk packet will be sent back to the client,
immediately followed by the PacketSerial packet that
holds the serial number of the user.

If the user/password combination is invalid, the
PacketAuthRefused packet will be sent back to the client.
If the user is already logged in, a PacketError is sent
with code set to PacketLogin.LOGGED.

name: valid user name as a string
password: matching password string
    """

    LOGGED = 1
    
    type = PACKET_LOGIN

    info = Packet.info + ( ('name', 'unknown', 's'),
                           ('password', 'unknown', 's') )
    
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "unknown")
        self.password = kwargs.get("password", "unknown")

    def pack(self):
        return Packet.pack(self) + self.packstring(self.name) + self.packstring(self.password)

    def unpack(self, block):
        block = Packet.unpack(self, block)
        (block, self.name) = self.unpackstring(block)
        (block, self.password) = self.unpackstring(block)
        return block

    def calcsize(self):
        return Packet.calcsize(self) + self.calcsizestring(self.name) + self.calcsizestring(self.password)

    def __str__(self):
        return Packet.__str__(self) + " name = %s, password = %s" % (self.name, self.password)

PacketFactory[PACKET_LOGIN] = PacketLogin

########################################

PACKET_AUTH_REQUEST = 11
PacketNames[PACKET_AUTH_REQUEST] = "AUTH_REQUEST"

class PacketAuthRequest(Packet):
    """
    Packet to ask authentification from the client
    """

    type = PACKET_AUTH_REQUEST

PacketFactory[PACKET_AUTH_REQUEST] = PacketAuthRequest

########################################

PACKET_LIST = 12
PacketNames[PACKET_LIST] = "LIST"

class PacketList(Packet):
    """

    Packet containing a list of packets
    
    """

    type = PACKET_LIST

    info = Packet.info + ( ('packets', [], 'pl'), )
    
    packets = []
    format = "!H"
    format_size = calcsize(format)

    def __init__(self, **kwargs):
        self.packets = kwargs.get("packets", [])

    def pack(self):
        block = Packet.pack(self) + pack(PacketList.format, len(self.packets))
        for packet in self.packets:
            block += packet.pack()
        return block

    def unpack(self, block):
        block = Packet.unpack(self, block)
        (length,) = unpack(PacketList.format, block[:PacketList.format_size])
        block = block[PacketList.format_size:]
        t = Packet()
        count = 0
        self.packets = []
        while len(block) > 0 and count < length:
            t.unpack(block)
            if not PacketFactory.has_key(t.type):
                print " *ERROR* unknown packet type %d (known types are %s)" % ( t.type, PacketNames)
                return
            packet = PacketFactory[t.type]()
            block = packet.unpack(block)
            count += 1
            self.packets.append(packet)
        if count != length:
            print " *ERROR* expected a list of %d packets but found only %d" % ( length, count)
        return block

    def calcsize(self):
        return Packet.calcsize(self) + PacketList.format_size + sum([ packet.calcsize() for packet in self.packets ])

    def __str__(self):
        return Packet.__str__(self) + join([packet.__str__() for packet in self.packets ])

PacketFactory[PACKET_LIST] = PacketList

########################################

PACKET_LOGOUT = 13
PacketNames[PACKET_LOGOUT] = "LOGOUT"

class PacketLogout(Packet):
    """
    Login out
    """

    NOT_LOGGED_IN = 1
    
    type = PACKET_LOGOUT

PacketFactory[PACKET_LOGOUT] = PacketLogout

########################################

PACKET_BOOTSTRAP = 14
PacketNames[PACKET_BOOTSTRAP] = "BOOTSTRAP"

class PacketBootstrap(Packet):
    ""

    type = PACKET_BOOTSTRAP

PacketFactory[PACKET_BOOTSTRAP] = PacketBootstrap

########################################

PACKET_PROTOCOL_ERROR = 15
PacketNames[PACKET_PROTOCOL_ERROR] = "PROTOCOL_ERROR"

class PacketProtocolError(PacketError):
    """
    Client protocol version does not match server protocol version.
    """

    type = PACKET_PROTOCOL_ERROR

PacketFactory[PACKET_PROTOCOL_ERROR] = PacketProtocolError

########################################

PACKET_MESSAGE = 16
PacketNames[PACKET_MESSAGE] = "MESSAGE"

class PacketMessage(PacketString):
    """
    server => client
    Informative messages
    """

    type = PACKET_MESSAGE

PacketFactory[PACKET_MESSAGE] = PacketMessage

_TYPES = range(0,39)

### !!!!!! NO SERIAL >= 50 !!!!!! ####
