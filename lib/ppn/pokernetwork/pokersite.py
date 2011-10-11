#
# -*- py-indent-offset: 4; coding: iso-8859-1 -*-
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
import simplejson
import re
import imp
import time
import base64
from types import *

from traceback import format_exc

from twisted.web import server, resource, util, http
from twisted.internet import defer
from twisted.python import log
from twisted.python.runtime import seconds

from pokernetwork.pokerpackets import *
from pokernetwork import pokermemcache

# FIXME: I don't think these next two functions should assume 'ISO-8859-1'
# like they do.  This is related to another FIXME about this issue you'll
# find in pokeravatar.py -- bkuhn, 2008-11-28
def fromutf8(tree, encoding = 'ISO-8859-1'):
    return __walk(tree, lambda x: x.encode(encoding))

def toutf8(tree, encoding = 'ISO-8859-1'):
    # make sure we do not decode a string that is already Unicode, otherwise
    # we'll get a "TypeError: decoding Unicode is not supported"
    def convert(s):
        if isinstance(s, unicode):
            return s
        return unicode(s, encoding)
    return __walk(tree, convert)

def __walk(tree, convert):
    if type(tree) is TupleType or type(tree) is ListType:
        result = map(lambda x: __walk(x, convert), tree)
        if type(tree) is TupleType:
            return tuple(result)
        else:
            return result
    elif type(tree) is DictionaryType:
        new_tree = {}
        for (key, value) in tree.iteritems():
            converted_key = convert(str(key))
            new_tree[converted_key] = __walk(value, convert)
        return new_tree
    elif ( type(tree) is UnicodeType or type(tree) is StringType ):
        return convert(tree)
    else:
        return tree

def packets2maps(packets):
    maps = []
    for packet in packets:
        attributes = packet.__dict__.copy()
        if isinstance(packet, PacketList):
            attributes['packets'] = packets2maps(attributes['packets'])
        if 'message' in dir(packet):
            attributes['message'] = getattr(packet, 'message')
        #
        # It is forbiden to set a map key to a numeric (native
        # numeric or string made of digits). Taint the map entries
        # that are numeric and hope the client will figure it out.
        #
        for (key, value) in packet.__dict__.iteritems():
            if type(value) == DictType:
                    for ( subkey, subvalue ) in value.items():
                            del value[subkey]
                            new_subkey = str(subkey)
                            if new_subkey.isdigit():
                                    new_subkey = "X" + new_subkey
                            value[new_subkey] = subvalue
        attributes['type'] = packet.__class__.__name__
        maps.append(attributes)
    return maps

def args2packets(args):
    packets = []
    for arg in args:
        if re.match("^[a-zA-Z]+$", arg['type']):
            try:
                fun_args = len(arg) > 1 and '(**arg)' or '()'
                packets.append(eval(arg['type'] + fun_args))
            except:
                packets.append(PacketError(message = "Unable to instantiate %s(%s): %s" % ( arg['type'], arg, format_exc() )))
        else:
            packets.append(PacketError(message = "Invalid type name %s" % arg['type']))
    return packets

class Request(server.Request):

    def getSession(self):
        uid = self.args.get('uid', [None])[0]
        auth = self.args.get('auth', [None])[0]
        explain = self.args.get('explain', ['yes'])[0] == 'yes'

        if uid == None: uid = self.site._mkuid()
        if auth == None: auth = self.site._mkuid()

        try:
            self.session = self.site.getSession(uid, auth, explain)
        except KeyError:
            self.session = self.site.makeSession(0, auth, explain)
        self.session.touch()
        return self.session

    def findProxiedIP(self):
        """Return the IP address of the client who submitted this request,
        making an attempt to determine the actual IP through the proxy.
        Returns	the client IP address (type: str )"""

        # FIXME: we shouldn't trust these headers so completely because
        # they can be easily forged.  Loic had the idea that we should
        # have a list of trusted proxies.  bkuhn was thinking we should
        # figure a way to log both the real IP and proxier IP.  Anyway,
        # sr#2157 remains open for this reason.

        if self.getHeader('x-forwarded-for'):
            return ('x-forwarded-for', self.getHeader('x-forwarded-for'))
        elif self.getHeader('x-cluster-client-ip'):
            return ('x-cluster-client-ip', self.getHeader('x-cluster-client-ip'))
        else:
            return ('client-ip', server.Request.getClientIP(self))

class Session(server.Session):

    def __init__(self, site, uid, auth, explain):
        server.Session.__init__(self, site, uid)
        self.auth = auth
        self.avatar = site.resource.service.createAvatar()
        self.explain_default = explain
        self.avatar.queuePackets()
        self.avatar.setDistributedArgs(uid, auth)
        if self.explain_default:
            self.avatar.setExplain(PacketPokerExplain.ALL)
        self.avatar.roles.add(PacketPokerRoles.PLAY)
        self.expired = False

    def expire(self):
        server.Session.expire(self)
        self.site.resource.service.destroyAvatar(self.avatar)
        del self.avatar
        self.expired = True

    def checkExpired(self):
        try:
            #
            # The session may expire as a side effect of the
            # verifications made by getSession against memcache.
            # When this happens an exception is thrown and checkExpire
            # is not called : this is intended because the
            # session already expired.
            #
            self.site.getSession(self.uid, self.auth, self.explain_default)
            server.Session.checkExpired(self)
            return True
        except KeyError:
            return False

class PokerResource(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service
        self.verbose = service.verbose
        self.isLeaf = True

    def message(self, string):
        print "PokerResource: " + string

    def error(self, string):
        self.message("*ERROR* " + string)

    def render(self, request):
        request.content.seek(0, 0)
        jsonp = request.args.get('jsonp', [''])[0]
        if jsonp:
            data = request.args.get('packet', [''])[0]
        elif request.args.has_key('packet'):
            data = request.args['packet'][0];
        else:
            data = request.content.read()
        if self.verbose >= 3:
            if "PacketPing" not in data or self.verbose > 3:
                self.message("(%s:%s) " % request.findProxiedIP() + "render " + data)

        try:
            args = simplejson.loads(data, encoding = 'UTF-8')
        except:
            return "Unable to decode JSON."

        if hasattr(Packet.JSON, 'decode_objects'): # backward compatibility
            args = Packet.JSON.decode_objects(args)
        args = fromutf8(args)
        packet = args2packets([args])[0]

        deferred = defer.succeed(None)

        if request.site.pipes:
            request.site.pipe(deferred, request, packet)

        def pipesFailed(reason):
            #
            # Report only if the request has not been finished already.
            # It is the responsibility of each filter to handle errors
            # either by passing them on the errback chain or by filling
            # the request with a proper report.
            #
            body = reason.getTraceback()
            if not request.finished:
                request.setResponseCode(http.INTERNAL_SERVER_ERROR)
                request.setHeader('content-type',"text/html")
                request.setHeader('content-length', str(len(body)))
                request.write(body)
            if self.verbose >= 0 and request.code != 200:
                self.error("(%s:%s) " % request.findProxiedIP() + str(body))
            if not request.finished:
                request.finish()
                return twisted.web.server.NOT_DONE_YET

            #
            # Return a value that is not a Failure so that the next
            # incoming request is accepted (otherwise the server keeps
            # returning error on every request)
            #
            return True

        deferred.addCallback(lambda result: self.deferRender(request, jsonp, packet, data))
        deferred.addErrback(pipesFailed)
        return server.NOT_DONE_YET

    def deferRender(self, request, jsonp, packet, data):
        if request.finished:
            #
            # For instance : the request was reverse-proxied to a server.
            #
            return True
        session = request.getSession()
        d = defer.maybeDeferred(session.avatar.handleDistributedPacket, request, packet, data)
        def render(packets):
            if self.verbose > 3:
                self.message("(%s:%s) " % request.findProxiedIP() + "render " + data + " returns " + str(packets))
            #
            # update the session information if the avatar changed
            #
            # *do not* update/expire/persist session if handling
            # PacketPokerLongPollReturn
            #
            if packet.type != PACKET_POKER_LONG_POLL_RETURN:
                session.site.updateSession(session)
                #session.site.persistSession(session)
            #
            # Format answer
            #
            maps = toutf8(packets2maps(packets))
            if jsonp:
                result_string = jsonp + '(' + str(Packet.JSON.encode(maps)) + ')'
            else:
                result_string = str(Packet.JSON.encode(maps))
            request.setHeader("content-length", str(len(result_string)))
            request.setHeader("content-type", 'text/plain; charset="UTF-8"')
            request.write(result_string)
            request.finish()
            return True
        def processingFailed(reason):
            body = reason.getTraceback()
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.setHeader('content-length', str(len(body)))
            request.setHeader('content-type',"text/html")
            request.write(body)
            request.finish()
            session.expire()
            if self.verbose >= 0:
                self.error("(%s:%s) " % request.findProxiedIP() + str(body))
            return True
        d.addCallbacks(render, processingFailed)
        return d

class PokerImageUpload(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service
        self.verbose = service.verbose
        self.deferred = defer.succeed(None)
        self.isLeaf = True

    def message(self, string):
        print "PokerImageUpload: " + string

    def error(self, string):
        self.message("*ERROR* " + string)

    def render(self, request):
        if self.verbose > 3:
            self.message("render " + request.content.read())
        request.content.seek(0, 0)
        self.deferred.addCallback(lambda result: self.deferRender(request))
        def failed(reason):
            body = reason.getTraceback()
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.setHeader('content-type',"text/html")
            request.setHeader('content-length', str(len(body)))
            request.write(body)
            request.connectionLost(reason)
            if self.verbose >= 0:
                self.error(str(body))
            return True
        self.deferred.addErrback(failed)
        return server.NOT_DONE_YET

    def deferRender(self, request):
        session = request.getSession()
        if session.avatar.isLogged():
            serial = request.getSession().avatar.getSerial()
            data = request.args['filename'][0]
            packet = PacketPokerPlayerImage(image = base64.b64encode(data), serial = serial)
            self.service.setPlayerImage(packet)
            result_string = 'image uploaded'
            request.setHeader("Content-length", str(len(result_string)))
            request.setHeader("Content-type", 'text/plain; charset="UTF-8"')
            request.write(result_string)
            request.finish()
            return
        else:
            session.expire()
            body = 'not logged'
            request.setResponseCode(http.UNAUTHORIZED)
            request.setHeader('content-type',"text/html")
            request.setHeader('content-length', str(len(body)))
            request.write(body)
            request.finish()
            return

class PokerTourneyStartResource(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service
        self.verbose = service.verbose
        self.deferred = defer.succeed(None)
        self.isLeaf = True

    def message(self, string):
        print "PokerTourneyStart: " + string

    def render(self, request):
        if self.verbose > 3:
            self.message("render " + str(request))

        try:
            tourney_serial = request.args['tourney_serial'][0]
            self.service.tourneyNotifyStart(int(tourney_serial))
        except:
            return "not found"

        body = 'OK'
        request.setHeader('content-type',"text/html")
        request.setHeader('content-length', str(len(body)))
        request.write(body)
        return True

class PokerAvatarResource(resource.Resource):

    def __init__(self, service):
        resource.Resource.__init__(self)
        self.service = service
        self.verbose = service.verbose
        self.deferred = defer.succeed(None)
        self.isLeaf = True

    def message(self, string):
        print "PokerAvatarResource: " + string

    def error(self, string):
        self.message("*ERROR* " + string)

    def render(self, request):
        if self.verbose > 3:
            self.message("render " + request.content.read())
        request.content.seek(0, 0)

        try:
            serial = int(request.path.split('/')[-1])
        except:
            return "not found"

        self.deferred.addCallback(lambda result: self.deferRender(request, serial))
        def failed(reason):
            body = reason.getTraceback()
            request.setResponseCode(http.INTERNAL_SERVER_ERROR)
            request.setHeader('content-type',"text/html")
            request.setHeader('content-length', str(len(body)))
            request.write(body)
            request.connectionLost(reason)
            if self.verbose >= 0:
                self.error(str(body))
            return True
        self.deferred.addErrback(failed)
        return server.NOT_DONE_YET

    def deferRender(self, request, serial):
        packet  = self.service.getPlayerImage(serial)
        if len(packet.image):
            result_string = base64.b64decode(packet.image)
            request.setHeader("Content-length", str(len(result_string)))
            request.setHeader("Content-type", packet.image_type)
            request.write(result_string)
            request.finish()
            return
        else:
            body = 'not found'
            request.setResponseCode(http.NOT_FOUND)
            request.setHeader('content-type',"text/html")
            request.setHeader('content-length', str(len(body)))
            request.write(body)
            request.finish()
            return

class PokerSite(server.Site):

    requestFactory = Request
    sessionFactory = Session

    def __init__(self, settings, resource, **kwargs):
        server.Site.__init__(self, resource, **kwargs)
        self.verbose = self.resource.verbose
        cookieTimeout = settings.headerGetInt("/server/@cookie_timeout")
        if cookieTimeout > 0:
            self.cookieTimeout = cookieTimeout
        else:
            self.cookieTimeout = 1200
        sessionTimeout = settings.headerGetInt("/server/@session_timeout")
        if sessionTimeout > 0:
            self.sessionFactory.sessionTimeout = sessionTimeout
        sessionCheckTime = settings.headerGetInt("/server/@session_check")
        if sessionCheckTime > 0:
            self.sessionCheckTime = sessionCheckTime
        memcache_address = settings.headerGet("/server/@memcached")
        if memcache_address:
            self.memcache = pokermemcache.memcache.Client([memcache_address])
        else:
            self.memcache = pokermemcache.MemcacheMockup.Client([])
        self.pipes = []
        for path in settings.header.xpathEval("/server/rest_filter"):
            module = imp.load_source("poker_pipe", path.content)
            self.pipes.append(getattr(module, "rest_filter"))
        resthost = settings.headerGetProperties("/server/resthost")
        if resthost:
            resthost = resthost[0]
            self.resthost = ( resthost['name'], resthost['host'], int(resthost['port']), resthost['path'] )
        else:
            self.resthost = None

    def message(self, string):
        print "PokerSite: " + string

    def error(self, string):
        self.message("*ERROR* " + string)

    def pipe(self, d, request, packet):
        if self.pipes:
            for pipe in self.pipes:
                d.addCallback(lambda x: defer.maybeDeferred(pipe, self, request, packet))

    #
    # prevent calling the startFactory method of site.Server
    # to disable loging.
    #
    def startFactory(self):
        pass

    def stopFactory(self):
        for key in self.sessions.keys():
            self.sessions[key].expire()

    def persistSession(self, session):
        try:
            if len(session.avatar.tables) <= 0 and len(session.avatar.tourneys) <= 0 and (not session.avatar.explain or len(session.avatar.explain.games.getAll()) <= 0):
                session.expire()
                if self.resthost:
                    self.memcache.delete(session.uid)
                return False
        except AttributeError:
            return False

        if self.resthost:
            self.memcache.set(session.uid, self.resthost, time = self.cookieTimeout)
        return True

    def updateSession(self, session):
        try:
          serial = session.avatar.getSerial()
        except AttributeError:
          serial = 0
        #
        # There is no need to consider the case where session.memcache_serial is
        # zero because nothing needs updating in memcache.
        #
        if session.memcache_serial > 0:
            if serial == 0:
                #
                # if the user has logged out, unbind the serial that was in memcache
                #
                self.memcache.replace(session.auth, '0', time = self.cookieTimeout)
            #
            # for consistency, so that updateSession can be called multiple times without
            # side effects
            #
            session.memcache_serial = serial

        if serial > 0:
            #
            # refresh the memcache entry each time a request is handled
            # because it is how each poker server is informed that
            # a given user is logged in
            #
            self.memcache.set(session.auth, str(serial), time = self.cookieTimeout)

    def getSession(self, uid, auth, explain):
        if not isinstance(uid, str):
            raise Exception("uid is not str: '%s' %s" % (uid, type(uid)))
        if not isinstance(auth, str):
            raise Exception("auth is not str: '%s' %s" % (auth, type(auth)))
        memcache_serial = self.memcache.get(auth)
        if memcache_serial == None:
            #
            # If the memcache session is gone, trash the current session
            # if it exists.
            #
            self.message("Memcached returned None for auth: %s, uid: %s" % (auth, uid))
            if self.sessions.has_key(uid):
                self.sessions[uid].expire()
        else:
            memcache_serial = int(memcache_serial)
            #
            # If a session exists, make sure it is in sync with the memcache
            # serial.
            #
            if self.sessions.has_key(uid):
                session = self.sessions[uid]
                session.memcache_serial = memcache_serial
                if session.avatar.getSerial() == 0:
                    #
                    # If the user has been authed by an external application
                    # (i.e. another poker server or a third party program)
                    # act as if a login was just sent and was successfully
                    # authed.
                    #
                    if memcache_serial > 0:
                        session.avatar.relogin(memcache_serial)
                else:
                    #
                    # If the avatar logout or logged into another serial,
                    # expire the session
                    #
                    if session.avatar.getSerial() != memcache_serial:
                        session.expire()
            if not self.sessions.has_key(uid):
                #
                # Create a session with an uid that matches the memcache
                # key
                #
                self.makeSessionFromUidAuth(uid, auth, explain).memcache_serial = memcache_serial
                if memcache_serial > 0:
                    self.sessions[uid].avatar.relogin(memcache_serial)

        return self.sessions[uid]

    def makeSessionFromUidAuth(self, uid, auth, explain):
        session = self.sessions[uid] = self.sessionFactory(self, uid, auth, explain)
        session.startCheckingExpiration(self.sessionCheckTime)
        return session

    def makeSession(self, uid, auth, explain):
        session = self.makeSessionFromUidAuth(uid, auth, explain)
        session.memcache_serial = 0
        self.memcache.add(auth, str(session.memcache_serial))
        return session
