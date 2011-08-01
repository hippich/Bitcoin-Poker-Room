#
# -*- coding: iso-8859-1 -*-
#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
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

import sys
sys.path.insert(0, ".")
sys.path.insert(0, "..")

import platform
from os.path import exists
from types import *

try:
        from OpenSSL import SSL
        from pokernetwork.pokerservice import SSLContextFactory
        HAS_OPENSSL=True
except:
        print "openSSL not available."
        HAS_OPENSSL=False


from twisted.application import internet, service, app
from twisted.web import resource,server

from pokernetwork import pokerdatabase
from pokernetwork.pokernetworkconfig import Config
from pokernetwork.pokerservice import PokerTree, PokerRestTree, PokerService, IPokerFactory
from pokernetwork.pokersite import PokerSite
from twisted.manhole import telnet

DEFAULT_CONFIG_PATH = '/etc/poker-network/poker.server.xml'

def makeService(configuration):
    settings = Config([''])
    settings.load(configuration)
    if not settings.header:
        sys.exit(1)

    serviceCollection = service.MultiService()

    poker_service = PokerService(settings)
    poker_service.setServiceParent(serviceCollection)

    poker_factory = IPokerFactory(poker_service)

    #
    # Poker protocol (with or without SSL)
    #
    tcp_port = settings.headerGetInt("/server/listen/@tcp")
    internet.TCPServer(tcp_port, poker_factory
                       ).setServiceParent(serviceCollection)

    tcp_ssl_port = settings.headerGetInt("/server/listen/@tcp_ssl")
    if HAS_OPENSSL and tcp_ssl_port:
            internet.SSLServer(tcp_ssl_port, poker_factory, SSLContextFactory(settings)
                           ).setServiceParent(serviceCollection)

    rest_site = PokerSite(settings, PokerRestTree(poker_service))

    #
    # HTTP (with or without SLL) that implements REST
    #
    rest_port = settings.headerGetInt("/server/listen/@rest")
    if rest_port:
            internet.TCPServer(rest_port, rest_site
                               ).setServiceParent(serviceCollection)

    rest_ssl_port = settings.headerGetInt("/server/listen/@rest_ssl")
    if HAS_OPENSSL and rest_ssl_port:
            internet.SSLServer(rest_ssl_port, rest_site, SSLContextFactory(settings)
                               ).setServiceParent(serviceCollection)

    http_site = server.Site(PokerTree(poker_service))

    #
    # HTTP (with or without SLL) that implements XML-RPC and SOAP
    #
    http_port = settings.headerGetInt("/server/listen/@http")
    if http_port:
            internet.TCPServer(http_port, http_site
                               ).setServiceParent(serviceCollection)

    http_ssl_port = settings.headerGetInt("/server/listen/@http_ssl")
    if HAS_OPENSSL and http_ssl_port:
            internet.SSLServer(http_ssl_port, http_site, SSLContextFactory(settings)
                               ).setServiceParent(serviceCollection)

    # API
    api_ssl_port = settings.headerGetInt("/server/listen/@api_ssl")
    if HAS_OPENSSL and api_ssl_port:
        from pokernetwork import apiserver, apiservice
        poker_database = pokerdatabase.PokerDatabase(settings)
        secret_store = apiserver.APIUserStore(poker_database)
        api_service = apiservice.APIService(poker_service)
        api_site = server.Site(apiserver.Root(api_service, secret_store))
        internet.SSLServer(api_ssl_port, api_site, SSLContextFactory(settings)
                          ).setServiceParent(serviceCollection)
    else:
        print 'Could not create API service!'

    #
    # TELNET twisted.manhole (without SSL)
    #
    manhole_port = settings.headerGetInt("/server/listen/@manhole")
    if manhole_port:
	    manhole_factory = telnet.ShellFactory()
	    manhole_factory.namespace['poker_service'] = poker_service
	    manhole_factory.namespace['poker_site'] = rest_site
	    manhole_service = internet.TCPServer(manhole_port, manhole_factory, interface = '127.0.0.1')
	    manhole_service.setName("manhole")
	    manhole_service.setServiceParent(serviceCollection)
	    if settings.headerGetInt("/server/@verbose") > 0:
		    print  "PokerManhole: manhole is useful for debugging, use with telnet admin/admin, however, it can be a security risk and should be used only during debugging"

    return serviceCollection


def makeApplication(argv):
    default_path = "/etc/poker-network" + sys.version[:3] + "/poker.server.xml"
    if not exists(default_path):
        default_path = DEFAULT_CONFIG_PATH
    configuration = argv[-1][-4:] == ".xml" and argv[-1] or default_path
    application = service.Application('poker')
    serviceCollection = service.IServiceCollection(application)
    poker_service = makeService(configuration)
    poker_service.setServiceParent(serviceCollection)
    return application


def run():
    if platform.system() != "Windows":
        if not sys.modules.has_key('twisted.internet.reactor'):
                print "installing poll reactor"
                from twisted.internet import pollreactor
                pollreactor.install()
        else:
                print "poll reactor already installed"
    from twisted.internet import reactor
    application = makeApplication(sys.argv)
    app.startApplication(application, None)
    reactor.run()

if __name__ == '__main__':
    run() # pragma: no cover
          # Do not need coverage since we call run directly in the tests.
