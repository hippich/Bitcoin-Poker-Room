#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2009 Johan Euphrosine <proppy@aminche.com>
# Copyright (C) 2008 Bradley M. Kuhn <bkuhn@ebb.org>
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
sys.path.insert(0, "./..")
sys.path.insert(0, "..")

import libxml2
import base64
import cgi

from twisted.trial import unittest, runner, reporter
from twisted.internet import defer
from twisted.python import failure
import twisted.internet.base
twisted.internet.base.DelayedCall.debug = True

from tests.testmessages import silence_all_messages
verbose = int(os.environ.get('VERBOSE_T', '-1'))
if verbose < 0: silence_all_messages()

from tests import testclock

from pokernetwork import pokermemcache
from pokernetwork import pokersite
from pokernetwork import pokernetworkconfig
from pokernetwork import pokeravatar
from pokernetwork.pokertable import PokerAvatarCollection
from pokernetwork.pokerpackets import *

class PokerServiceMockup:

      def __init__(self):
            self.verbose = 6
            self.avatar_collection = PokerAvatarCollection()
            self.dirs = []

      def getPlayerInfo(self, serial):
            packet = PacketPokerPlayerInfo(serial = serial)
            packet.locale = 'en_US.UTF-8'
            return packet

      def locale2translationFunc(self, locale, codeset = ""):
            return None
      
      def createAvatar(self):
            return pokeravatar.PokerAvatar(self)

      def destroyAvatar(self, avatar):
            pass

      def getPlayerPlaces(self, serial):
            return PacketPokerPlayerPlaces(serial = serial)

      def tourneyNotifyStart(self, tourney_serial):
            self.tourney_serial = tourney_serial
      
      player_image = None
      def setPlayerImage(self, player_image):
            self.player_image = player_image      

      player_serial = None
      def getPlayerImage(self, serial):
            self.player_serial = serial
            return self.player_image

      def getClientQueuedPacketMax(self):
            return 2000

      def packet2resthost(self, packet):
            return (None, None)

class HelpersTestCase(unittest.TestCase):

      def test_fromutf8(self):
            self.assertEqual(['b', {'a': 'c'}, ('d',), 1], pokersite.fromutf8([u'b', {u'a': u'c'}, (u'd',), 1]))
            self.assertEqual([u'b', {u'a': u'c'}, (u'd',), 1], pokersite.toutf8(['b', {'a': 'c'}, ('d',), 1]))
                             
      def test_args2packets(self):
            self.assertEqual([PacketPing()], pokersite.args2packets([{'type':'PacketPing'}]))
            packets = pokersite.args2packets([{'type':'BadPacket'}])
            self.assertSubstring('Unable to instantiate', packets[0].message)
            packets = pokersite.args2packets([{'type':'0'}])
            self.assertSubstring('Invalid type', packets[0].message)

      def test_packets2maps(self):
            self.assertEqual([{'type': 'PacketPing'}], pokersite.packets2maps([PacketPing()]))
            self.assertEqual([{'packets': [{'type': 'PacketPing'}], 'type': 'PacketList'}], pokersite.packets2maps([PacketList(packets = [PacketPing()])]))
            packet = Packet()
            packet.message = "MESSAGE"
            packet.what = { 0: 1 }
            self.assertEqual([{'message': 'MESSAGE', 'type': 'Packet', 'what': {'X0': 1}}], pokersite.packets2maps([packet]))

class PokerSiteBase(unittest.TestCase):

      def setUp(self):
            testclock._seconds_reset()        
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" />
"""
            self.settings = pokernetworkconfig.Config([])
            self.settings.loadFromString(settings_xml)
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            pokermemcache.memcache_singleton.clear()
            pokermemcache.memcache_expiration_singleton.clear()
            self.service = PokerServiceMockup()
            self.site = pokersite.PokerSite(self.settings, pokersite.PokerResource(self.service))

      def tearDown(self):
            self.site.stopFactory()

class PokerResourceTestCase(PokerSiteBase):

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerResourceTestCase.Transport()
                  self.site = site

            def requestDone(self, request):
                  pass

      def test01_render(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.queued = 0
            d = r.notifyFinish()
            def finish(result):
                  self.assertSubstring('\r\n\r\n[]', r.transport.getvalue())
            d.addCallback(finish)
            r.requestReceived('GET', '/', '')
            return d
      
      def test02_render_error(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.queued = 0
            error_pattern = 'UNLIKELY'
            def handlePacketLogic(packet):
                  raise UserWarning, error_pattern
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            r.getSession().avatar.handlePacketLogic = handlePacketLogic
            r.requestReceived('GET', '/?uid=uid&auth=auth', '')
            self.assertSubstring(error_pattern, r.transport.getvalue())

      def test03_render_simultaneous(self):
            """
            requests that are received while another request is being
            handled (this may happen if the packet logic returned a
            deferred) are not blocked by the first request.
            """
            channel = self.Channel(self.site)
            r1 = pokersite.Request(channel, True)
            r1.site = r1.channel.site
            input = '{"type": "PacketPing"}'
            r1.gotLength(len(input))
            r1.handleContentChunk(input)
            r1.queued = 0
            d1 = defer.Deferred()
            r1.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            avatar1 = r1.getSession().avatar
            def handlePacketLogic1(packet):
                  avatar1.sendPacket(d1)
            avatar1.handlePacketLogic = handlePacketLogic1
            r1.requestReceived('GET', '/?uid=uid&auth=auth', '')

            r2 = pokersite.Request(channel, True)
            r2.site = r2.channel.site
            input = '{"type": "PacketPing"}'
            r2.gotLength(len(input))
            r2.handleContentChunk(input)
            r2.queued = 0
            r2.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            avatar2 = r2.getSession().avatar
            def handlePacketLogic2(packet):
                  avatar2.sendPacket(PacketPing())
            r2.getSession().avatar.handlePacketLogic = handlePacketLogic2
            r2.requestReceived('GET', '/?uid=uid&auth=auth', '')

            #
            # r1 not complete yet
            #
            self.assertEqual('', r1.transport.getvalue())
            #
            # r2 complete
            #
            self.assertSubstring('PacketPing', r2.transport.getvalue())
            #
            # r1 complete
            #
            d1.callback(PacketAck())
            self.assertSubstring('PacketAck', r1.transport.getvalue())

      def test04_render_jsonp(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.gotLength(0)
            r.handleContentChunk('')
            r.queued = 0
            r.requestReceived('GET', '/?jsonp=FUN&packet={"type":"PacketPing"}', '')

            self.assertSubstring('\r\n\r\nFUN([])', r.transport.getvalue())

      def test05_render_content(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.gotLength(0)
            r.handleContentChunk('')
            r.queued = 0
            r.requestReceived('GET', '/?packet={"type":"PacketPing"}', '')

            self.assertSubstring('\r\n\r\n[]', r.transport.getvalue())

      def test06_render_expire_logged(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.queued = 0
            session = 'session'
            serial = '5'
            r.received_cookies['TWISTED_SESSION'] = session
            r.site.memcache.set(session, serial)
            d = r.notifyFinish()
            def finish(result):
                  self.assertSubstring('\r\n\r\n[]', r.transport.getvalue())
                  self.failIfSubstring('Expire', r.transport.getvalue())
            d.addCallback(finish)
            r.requestReceived('GET', '/', '')
            return d

      def test06_1_render_do_not_expire_session_if_long_poll_return(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = '{"type": "PacketPokerLongPollReturn"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.queued = 0
            d = r.notifyFinish()
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            session = r.getSession()
            def finish(result):
                  self.assertEqual(False, session.expired)
            d.addCallback(finish)
            r.requestReceived('GET', '/?uid=uid&auth=auth', '')
            return d

      def test06_2_render_do_not_update_session_if_long_poll_return(self):
            def longPoll():
                  r = pokersite.Request(self.Channel(self.site), True)
                  r.site = r.channel.site
                  input = '{"type": "PacketPokerLongPoll"}'
                  r.gotLength(len(input))
                  r.handleContentChunk(input)
                  r.queued = 0
                  d = r.notifyFinish()
                  r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
                  session = r.getSession()
                  r.requestReceived('GET', '/?uid=uid&auth=auth', '')
                  return d
            def longPollReturn():
                  r = pokersite.Request(self.Channel(self.site), True)
                  r.site = r.channel.site
                  input = '{"type": "PacketPokerLongPollReturn"}'
                  r.gotLength(len(input))
                  r.handleContentChunk(input)
                  r.queued = 0
                  d = r.notifyFinish()
                  r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
                  session = r.getSession()
                  def finish(result):                        
                        self.failIfSubstring('Session instance has no attribute \'avatar\'', r.transport.getvalue())
                  d.addCallback(finish)
                  r.requestReceived('GET', '/?uid=uid&auth=auth', '')
                  return d
            dl = defer.DeferredList([longPoll(), longPollReturn()])
            return dl

      def test07_message_prefix(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.received_headers['x-forwarded-for'] = '1.2.3.4'
            r.site.resource.message = lambda message: self.assertSubstring('1.2.3.4', message)
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.queued = 0
            d = r.notifyFinish()
            r.requestReceived('GET', '/', '')
            return d

      def test08_error_prefix(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.received_headers['x-forwarded-for'] = '1.2.3.4'
            d = defer.Deferred()
            d.addCallback(lambda error: self.assertSubstring('1.2.3.4', error))
            r.site.resource.error = d.callback
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.queued = 0
            error_pattern = 'UNLIKELY'
            def handlePacketLogic(packet):
                  raise UserWarning, error_pattern
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            r.getSession().avatar.handlePacketLogic = handlePacketLogic
            r.requestReceived('GET', '/?uid=uid&auth=auth', '')
            return d

class PokerTourneyStartTestCase(unittest.TestCase):

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerTourneyStartTestCase.Transport()
                  self.site = site

      def setUp(self):
            testclock._seconds_reset()        
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" />
"""
            self.settings = pokernetworkconfig.Config([])
            self.settings.loadFromString(settings_xml)
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            pokermemcache.memcache_singleton.clear()
            pokermemcache.memcache_expiration_singleton.clear()
            self.service = PokerServiceMockup()
            self.site = pokersite.PokerSite(self.settings, pokersite.PokerTourneyStartResource(self.service))

      def tearDown(self):
            pass

      def test01_render(self):            
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = ''
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.requestReceived('GET', '/?tourney_serial=666', '')
            self.assertSubstring('\nOK', r.transport.getvalue())
            self.assertEquals(666, self.service.tourney_serial)
            r.getSession().expire()

class PokerImageUploadTestCase(unittest.TestCase):

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerImageUploadTestCase.Transport()
                  self.site = site

      def setUp(self):
            testclock._seconds_reset()        
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" />
"""
            self.settings = pokernetworkconfig.Config([])
            self.settings.loadFromString(settings_xml)
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            pokermemcache.memcache_singleton.clear()
            pokermemcache.memcache_expiration_singleton.clear()
            self.service = PokerServiceMockup()
            self.site = pokersite.PokerSite(self.settings, pokersite.PokerImageUpload(self.service))
            self.image_data = "image data"
            def parse_multipart_mockup(content, dict):
                  return {'filename':[self.image_data]}
            self.cgi_parse_multipart = cgi.parse_multipart
            cgi.parse_multipart = parse_multipart_mockup
            
      def tearDown(self):
            cgi.parse_multipart = self.cgi_parse_multipart

      def test01_render(self):            
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            r.site.memcache.set('auth', '111')
            self.assertEquals(True, r.getSession().avatar.isLogged());

            image_data = "image data"
            r.received_headers['content-type'] = 'multipart/form-data'
            input = ''
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.requestReceived('POST', '/?uid=uid&auth=auth', '')
            self.assertSubstring('image uploaded', r.transport.getvalue())
            self.assertEquals(base64.b64encode(self.image_data),
                              self.service.player_image.image)
            r.getSession().expire()

      def test02_unauthorized(self):            
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            self.assertEquals(False, r.getSession().avatar.isLogged());

            r.received_headers['content-type'] = 'multipart/form-data'
            input = ''
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.requestReceived('POST', '/?uid=uid&auth=auth', '')
            self.assertSubstring('not logged', r.transport.getvalue())
            self.assertEquals(None, self.service.player_image)
      
      def test03_error(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            r.site.memcache.set('auth', '111')
            self.assertEquals(True, r.getSession().avatar.isLogged());

            image_data = "image data"
            r.received_headers['content-type'] = 'multipart/form-data'
            input = ''
            r.gotLength(len(input))
            r.handleContentChunk(input)
            error_pattern = 'UNLIKELY'
            def setPlayerImageFailed(player_image):
                  raise UserWarning, error_pattern
            self.service.setPlayerImage = setPlayerImageFailed
            r.requestReceived('POST', '/?uid=uid&auth=auth', '')
            self.assertSubstring(error_pattern, r.transport.getvalue())
            self.assertEquals(None, self.service.player_image)
            r.getSession().expire()

class PokerAvatarResourceTestCase(unittest.TestCase):

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerAvatarResourceTestCase.Transport()
                  self.site = site

      def setUp(self):
            testclock._seconds_reset()        
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" />
"""
            self.settings = pokernetworkconfig.Config([])
            self.settings.loadFromString(settings_xml)
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            self.service = PokerServiceMockup()
            self.site = pokersite.PokerSite(self.settings, pokersite.PokerAvatarResource(self.service))

      def test01_render(self):
            data = 'image data'
            serial = 64
            self.service.setPlayerImage(PacketPokerPlayerImage(image = base64.b64encode(data), serial = serial))
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.gotLength(0)
            r.handleContentChunk('')
            r.requestReceived('GET', '/%i' % serial, '')
            self.assertSubstring('\r\n\r\n%s' % data, r.transport.getvalue())
            self.assertEquals(serial, self.service.player_serial)

      def test02_not_found(self):
            serial = 100
            self.service.setPlayerImage(PacketPokerPlayerImage(image = '', serial = serial))
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.gotLength(0)
            r.handleContentChunk('')
            r.requestReceived('GET', '/%i' % serial, '')
            self.assertSubstring('not found', r.transport.getvalue())
            self.assertEquals(serial, self.service.player_serial)

      def test03_error(self):
            data = 'image data'
            serial = 64
            self.service.setPlayerImage(PacketPokerPlayerImage(image = base64.b64encode(data), serial = serial))
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.gotLength(0)
            r.handleContentChunk('')
            error_pattern = 'UNLIKELY'
            def getPlayerImageFailed(player_serial):
                  raise UserWarning, error_pattern
            self.service.getPlayerImage = getPlayerImageFailed
            r.requestReceived('GET', '/%i' % serial, '')
            self.assertSubstring('error_pattern', r.transport.getvalue())
            self.assertEquals(None, self.service.player_serial)

class FilterTestCase(unittest.TestCase):

      def setUp(self):
            testclock._seconds_reset()        
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" >
<rest_filter>.././testfilter.py</rest_filter>
<rest_filter>.././../pokernetwork/nullfilter.py</rest_filter>
</server>
"""
            self.settings = pokernetworkconfig.Config([])
            self.settings.loadFromString(settings_xml)
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            self.service = PokerServiceMockup()
            self.site = pokersite.PokerSite(self.settings, pokersite.PokerResource(self.service))

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerResourceTestCase.Transport()
                  self.site = site

      def test01_render(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.requestReceived('GET', '/', '')
            
            self.assertSubstring('\r\n\r\n[]', r.transport.getvalue())
            self.assertEqual(True, hasattr(r, "HERE"))

class FilterErrorTestCase(unittest.TestCase):

      def setUp(self):
            testclock._seconds_reset()        
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" >
<rest_filter>.././testerrorfilter.py</rest_filter>
</server>
"""
            self.settings = pokernetworkconfig.Config([])
            self.settings.loadFromString(settings_xml)
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            self.service = PokerServiceMockup()
            self.site = pokersite.PokerSite(self.settings, pokersite.PokerResource(self.service))

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerResourceTestCase.Transport()
                  self.site = site

      def test01_render(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            
            d = r.notifyFinish()
            def finish(reason):
                  self.assertSubstring('UNLIKELY', r.transport.getvalue())
                  return True
            d.addBoth(finish)
            r.requestReceived('GET', '/', '')
            return d

      def test02_error_prefix(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            r.received_headers['x-forwarded-for'] = '1.2.3.4'
            d = defer.Deferred()            
            d.addCallback(lambda error: self.assertSubstring('1.2.3.4', error))
            r.site.resource.error = d.callback
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)            
            r.requestReceived('GET', '/', '')
            return d

class FilterFinishTestCase(unittest.TestCase):

      def setUp(self):
            testclock._seconds_reset()        
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" >
<rest_filter>.././finishedfilter.py</rest_filter>
</server>
"""
            self.settings = pokernetworkconfig.Config([])
            self.settings.loadFromString(settings_xml)
            pokermemcache.memcache = pokermemcache.MemcacheMockup
            self.service = PokerServiceMockup()
            self.site = pokersite.PokerSite(self.settings, pokersite.PokerResource(self.service))

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerResourceTestCase.Transport()
                  self.site = site

            def requestDone(self, request):
                  pass

      def test01_render(self):
            r = pokersite.Request(self.Channel(self.site), True)
            r.site = r.channel.site
            input = '{"type": "PacketPing"}'
            r.gotLength(len(input))
            r.handleContentChunk(input)
            r.queued = 0
            d = r.notifyFinish()
            def finish(reason):
                  self.assertSubstring('FINISHED', r.transport.getvalue())
                  return True
            d.addCallback(finish)
            r.requestReceived('GET', '/', '')
            return d

class SessionTestCase(PokerSiteBase):

      def test01_checkExpired(self):
            uid = 'uid'
            auth = 'auth'
            session = self.site.makeSessionFromUidAuth(uid, auth, False)
            self.site.memcache.set(auth, '0')
            self.assertEqual(True, session.checkExpired())
            self.site.memcache.delete(auth)
            self.assertEqual(False, session.checkExpired())

      def test02_checkDistributedArgs(self):
            uid = 'ZUID'
            auth = 'ZAUTH'
            session = self.site.makeSessionFromUidAuth(uid, auth, False)
            self.failUnlessSubstring(uid, session.avatar.distributed_args)
            self.failUnlessSubstring(auth, session.avatar.distributed_args)
            session.expire()

class SessionExplainTestCase(PokerSiteBase):

      def test01_explain_missing_yes(self):
            class Channel:
                  def __init__(self, site):
                        self.site = site
            
            r = pokersite.Request(Channel(self.site), True)
            r.site = r.channel.site
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            session = r.getSession()
            self.assertNotEquals(None, session.avatar.explain)
            session.expire()
            self.assertEqual(True, session.expired)

      def test02_explain_yes(self):
            class Channel:
                  def __init__(self, site):
                        self.site = site
            
            r = pokersite.Request(Channel(self.site), True)
            r.site = r.channel.site
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'], 'explain': ['yes'] }
            session = r.getSession()
            self.assertNotEquals(None, session.avatar.explain)
            session.expire()
            self.assertEqual(True, session.expired)

      def test02_explain_no(self):
            class Channel:
                  def __init__(self, site):
                        self.site = site
            
            r = pokersite.Request(Channel(self.site), True)
            r.site = r.channel.site
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'], 'explain': ['no'] }
            session = r.getSession()
            self.assertEquals(None, session.avatar.explain)
            session.expire()
            self.assertEqual(True, session.expired)

      def test02_expireFromTwisted(self):
            uid = 'uid'
            auth = 'auth'
            session = self.site.makeSessionFromUidAuth(uid, auth, 'yes')
            self.site.memcache.set(uid, '0')
            self.site.memcache.set(auth, '0')
            session.lastModified = 0
            session.expire()
            session.checkExpired()

      def test03_replaceFromGetSession(self):
            uid = 'uid'
            auth = 'auth'
            session = self.site.makeSessionFromUidAuth(uid, auth, 'yes')
            session.avatar.user.serial = 5
            session.lastModified = 0
            self.site.memcache.set(uid, '0')
            self.site.memcache.set(auth, '0')
            self.assertEqual(False, session.checkExpired())

class RequestTestCase(PokerSiteBase):

      def test01_name(self):
            class Channel:
                  def __init__(self, site):
                        self.site = site
            
            r = pokersite.Request(Channel(self.site), True)
            r.site = r.channel.site
            r.args = { 'uid': [ 'uid' ], 'auth': ['auth'] }
            session = r.getSession()
            session.expire()
            self.assertEqual(True, session.expired)

      def test02_ipNumberProxy(self):
            from twisted.internet import address

            class Channel:
                  def __init__(self, site):
                        self.site = site
            class MockClient:
                  pass
                  
            addr = address.IPv4Address('TCP', 'proxy.example.org', 7775)
            r = pokersite.Request(Channel(self.site), True)
            r.client = addr
            self.assertEquals(r.findProxiedIP(), ('client-ip', 'proxy.example.org'))

            # received_headers will become requestHeaders RSN, according to:
            # http://python.net/crew/mwh/apidocs/twisted.web.http.Request.html

            r.received_headers['x-cluster-client-ip'] = 'cluster-player.example.com'

            self.assertEquals(r.findProxiedIP(), ('x-cluster-client-ip', 'cluster-player.example.com'))
            
            r.received_headers['x-forwarded-for'] = 'forward-player.example.com'
            self.assertEquals(r.findProxiedIP(), ('x-forwarded-for', 'forward-player.example.com'))


class PokerSiteTestCase(PokerSiteBase):

      def test01_init_full(self):
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6" memcached="127.0.0.1:11211" session_timeout="60" session_check="10" cookie_timeout="120" />
"""
            settings = pokernetworkconfig.Config([])
            settings.loadFromString(settings_xml)
            service = PokerServiceMockup()
            site = pokersite.PokerSite(settings, pokersite.PokerResource(service))
            self.assertEqual([ '127.0.0.1:11211' ], site.memcache.addresses)
            self.assertEqual(60, site.sessionFactory.sessionTimeout)
            self.assertEqual(10, site.sessionCheckTime)
            self.assertEqual(120, site.cookieTimeout)

      def test02_init_default(self):
            sessionTimeout = pokersite.PokerSite.sessionFactory.sessionTimeout
            sessionCheckTime = pokersite.PokerSite.sessionCheckTime
            service = PokerServiceMockup()
            site = pokersite.PokerSite(self.settings, pokersite.PokerResource(service))
            self.assertEqual([ ], site.memcache.addresses)
            self.assertEqual(sessionTimeout, site.sessionFactory.sessionTimeout)
            self.assertEqual(sessionCheckTime, site.sessionCheckTime)

      def test03_01_getSession(self):
            """
            A session exists in core but not in memcache :
            the in core session expires
            """
            uid = 'uid'
            auth = 'auth'
            session = self.site.makeSession(uid, auth, False)
            self.site.memcache.delete(auth)
            exception = False
            try:
                  self.site.getSession(session.uid, session.auth, False)
            except KeyError:
                  exception = True
            self.assertEqual(True, exception)
            self.assertEqual(True, session.expired)

      def test03_01_getSession_uid_not_string(self):
            """
            Try to get a session with a numeric uid instead of a string
            """
            uid = 111
            auth = 'auth'
            exception = False
            try:
                  self.site.getSession(uid, auth, False)
            except Exception, e:
                  self.failUnlessSubstring('uid is not str', str(e))
                  exception = True
            self.assertEqual(True, exception)

      def test03_01_getSession_auth_not_string(self):
            """
            Try to get a session with a numeric auth instead of a string
            """
            uid = 'uid'
            auth = 111
            exception = False
            try:
                  self.site.getSession(uid, auth, False)
            except Exception, e:
                  self.failUnlessSubstring('auth is not str', str(e))
                  exception = True
            self.assertEqual(True, exception)

      def test03_02_getSession(self):
            """
            A session exists in core and in memcache. The memcache serial
            is set from the outside.
            """
            session = self.site.makeSession('uid', 'auth', True)
            serial = 111
            self.site.memcache.set(session.auth, str(serial))
            self.site.getSession(session.uid, session.auth, True)
            self.assertEquals(serial, session.avatar.getSerial())
            self.assertNotEquals(None, session.avatar.explain)
            self.assertEquals(serial, session.avatar.explain.serial)
            self.assertEquals(True, PacketPokerRoles.PLAY in session.avatar.roles)
            """
            Memcache serial changed and becomes inconsistent.
            """
            self.site.memcache.set(session.auth, str(serial + 1))
            session = self.site.getSession(session.uid, session.auth, True)
            self.assertEquals(serial + 1, session.avatar.getSerial())

      def test04_updateSession_noop(self):
            """
            nothing happened and user logged out
            """
            session = self.site.makeSession('uid', 'auth', False)
            self.site.updateSession(session)
            self.assertEquals('0', self.site.memcache.get(session.auth))

      def test04_updateSession_login(self):
            """
            memcache serial is 0 and serial is > 0, meaning the user logged in.
            The memcache must be updated accordingly by updating the session id
            entry with the serial
            """
            session = self.site.makeSession('uid', 'auth', False)
            serial = 100
            session.avatar.user.serial = serial
            self.site.updateSession(session)
            self.assertEquals(serial, int(self.site.memcache.get(session.auth)))
            self.assertEquals(self.site.cookieTimeout, self.site.memcache.expiration[session.auth])
            
      def test04_updateSession_logout(self):
            """
            memcache serial is > 0 and serial is == 0, meaning the user logged out
            the memcache must be updated by setting the session id entry to 0
            """
            session = self.site.makeSession('uid', 'auth', False)
            #
            # login
            #
            serial = 100
            session.avatar.user.serial = serial
            session.avatar.tables[1] = 'table'
            self.site.updateSession(session)
            self.assertEquals(serial, int(self.site.memcache.get(session.auth)))
            self.assertEquals(self.site.cookieTimeout, self.site.memcache.expiration[session.auth])
            #
            # logout
            #
            session.memcache_serial = serial # would be set by getSession()
            session.avatar.user.serial = 0
            self.site.updateSession(session)
            self.assertEquals(0, int(self.site.memcache.get(session.auth)))

      def test04_updateSession_inconsistent_serial(self):
            """
            memcache serial is > 0 and serial is > 0 and memcache_serial != serial, 
            serial wins and take over
            """
            session = self.site.makeSession('uid', 'auth', False)
            #
            # login
            #
            serial = 100
            session.avatar.user.serial = serial
            session.avatar.tables[1] = 'table'
            self.site.updateSession(session)
            self.assertEquals(serial, int(self.site.memcache.get(session.auth)))
            #
            # inconsistency in serial, previous serial is discarded
            #
            new_serial = 200
            session.memcache_serial = serial # would be set by getSession()
            session.avatar.user.serial = new_serial
            self.site.updateSession(session)
            self.assertEquals(new_serial, int(self.site.memcache.get(session.auth)))
            self.assertEquals(session.memcache_serial, new_serial)

      def test05_startFactory(self):
            self.site.startFactory()
            self.assertEqual(False, hasattr(self.site, "logFile"))

      class Transport:
            def getPeer(self):
                  return None
            def getHost(self):
                  return None

      class Channel:
            def __init__(self, site):
                  self.transport = PokerResourceTestCase.Transport()
                  self.site = site

      def test08_memcache_key_not_string(self):
            exceptionCaught = False
            session = self.site.makeSession('uid', 'auth', False)
            self.assertRaises(Exception, self.site.memcache.get, unicode(session.auth))
            self.assertRaises(Exception, self.site.getSession, unicode(session.uid), session.auth)
            self.assertRaises(Exception, self.site.getSession, session.uid, unicode(session.auth))

      def test09_error_coverage(self):
            self.site.message = lambda text: self.assertSubstring("*ERROR*", text)
            self.site.error('foo')

      def test10_persistSession(self):
            """
            the session expires after persistSession, unless there are tables
            """
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6">
<resthost host="HOST" port="7777" path="PATH" />
</server>"""
            settings = pokernetworkconfig.Config([])
            settings.loadFromString(settings_xml)
            service = PokerServiceMockup()
            site = pokersite.PokerSite(settings, pokersite.PokerResource(service))

            session = self.site.makeSession('uid', 'auth', False)
            session.avatar.tables[1] = 'table'
            self.assertEquals(True, site.persistSession(session))
            self.assertEquals(False, session.expired)
            # persistSession should not set memcache entry if avatar has no explain bug#14883
            self.assertEquals(None, site.memcache.get('uid'))
            session.avatar.tables = []
            self.assertEquals(False, site.persistSession(session))
            self.assertEquals(True, session.expired)
            self.assertEquals(None, site.memcache.get('uid'))

      def test10_persistSessionExplain(self):
            """
            the session expires after persistSession, unless there are games in explain
            """
            settings_xml = """<?xml version="1.0" encoding="ISO-8859-1"?>
<server verbose="6">
<resthost host="HOST" port="7777" path="PATH" />
</server>"""
            settings = pokernetworkconfig.Config([])
            settings.loadFromString(settings_xml)
            service = PokerServiceMockup()
            site = pokersite.PokerSite(settings, pokersite.PokerResource(service))
            
            session = self.site.makeSession('uid', 'auth', False)
            session.avatar.tables = []
            session.avatar.setExplain(PacketPokerExplain.ALL)
            session.avatar.explain.games.games[1] = 'table'
            self.assertEquals(True, site.persistSession(session))
            self.assertEquals(False, session.expired)
            self.assertEquals(('HOST', 7777, 'PATH'), site.memcache.get('uid'))

            session.avatar.explain.games.games = {}
            self.assertEquals(False, site.persistSession(session))
            self.assertEquals(True, session.expired)
            self.assertEquals(None, site.memcache.get('uid'))

            session = self.site.makeSession('uid', 'auth', False)
            session.avatar.explain = None
            self.assertEquals(False, site.persistSession(session))
            self.assertEquals(True, session.expired)
            self.assertEquals(None, site.memcache.get('uid'))
            

def Run():
    loader = runner.TestLoader()
#    loader.methodPrefix = "test01"
    suite = loader.suiteFactory()
    suite.addTest(loader.loadClass(FilterErrorTestCase))
    suite.addTest(loader.loadClass(FilterTestCase))
    suite.addTest(loader.loadClass(FilterFinishTestCase))
    suite.addTest(loader.loadClass(PokerResourceTestCase))
    suite.addTest(loader.loadClass(PokerImageUploadTestCase))
    suite.addTest(loader.loadClass(PokerAvatarResourceTestCase))
    suite.addTest(loader.loadClass(SessionTestCase))
    suite.addTest(loader.loadClass(SessionExplainTestCase))
    suite.addTest(loader.loadClass(RequestTestCase))
    suite.addTest(loader.loadClass(PokerSiteTestCase))
    suite.addTest(loader.loadClass(HelpersTestCase))
    suite.addTest(loader.loadClass(PokerTourneyStartTestCase))
    return runner.TrialRunner(
        reporter.VerboseTextReporter,
        tracebackFormat='default',
        ).run(suite)

if __name__ == '__main__':
    if Run().wasSuccessful():
        sys.exit(0)
    else:
        sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-pokersite.py ) ; ( cd ../tests ; make COVERAGE_FILES='../pokernetwork/pokersite.py' VERBOSE_T=-1 TESTS='coverage-reset test-pokersite.py coverage-report' check )"
# End:
