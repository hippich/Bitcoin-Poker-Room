#
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2009 Johan Euphrosine <proppy@aminche.com>
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

from twisted.internet import reactor
from pokernetwork.pokerrestclient import PokerProxyClientFactory

local_reactor = reactor
        
#                                                                               
# return a value if all actions were complete
#
def rest_filter(site, request, packet):
    if request.finished:                                                        #pragma: no cover
        #
        # the request has been answered by a filter earlier in the chain
        #
        return True                                                             #pragma: no cover
    service = site.resource.service                                             #pragma: no cover
    uid = request.args.get('uid', [''])[0]                                      #pragma: no cover

    if uid:                                                                     #pragma: no cover
        resthost = site.memcache.get(uid)                                       #pragma: no cover
        if resthost:                                                            #pragma: no cover
            (host, port, path) = [str(s) for s in resthost]                     #pragma: no cover
            parts = request.uri.split('?', 1)                                   #pragma: no cover
            if len(parts) > 1:                                                  #pragma: no cover
                path += '?' + parts[1]                                          #pragma: no cover
            request.content.seek(0, 0)                                          #pragma: no cover
            header = request.getAllHeaders()                                    #pragma: no cover
            data = request.content.read()                                       #pragma: no cover
            clientFactory = PokerProxyClientFactory(                            #pragma: no cover
                request.method, path, request.clientproto,                      #pragma: no cover
                header, data, request,                                          #pragma: no cover
                service.verbose, host + ':' + str(port) + path)                 #pragma: no cover
            local_reactor.connectTCP(host, int(port), clientFactory)            #pragma: no cover
            return clientFactory.deferred                                       #pragma: no cover
    return True                                                                 #pragma: no cover
