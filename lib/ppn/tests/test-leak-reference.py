#!/usr/bin/python2.5
# -*- mode: python -*-
#
# Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
# Copyright (C) 2008, 2009 Loic Dachary <loic@dachary.org>
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

from twisted.trial import unittest, runner, reporter
from twisted.web import client, http

from twisted.web import server, resource
from twisted.internet import reactor, defer

class Simple(resource.Resource):
        isLeaf = True
        def render_GET(self, request):
		print request		
		return "<html>Hello, world!</html>"
	
class LeakReferenceTestCase(unittest.TestCase):
	def setUp(self):
		self.site = server.Site(Simple())
		self.port = reactor.listenTCP(8080, self.site)
	def tearDown(self):
		return self.port.stopListening()    
	def test01_get_page(self):
		def f(ignored):
			d = client.getPage("http://localhost:8080/")
			d.addCallback(f)
		f(None)
		d = defer.Deferred()
		return d
	def test02_get_page_guppy(self):
		import guppy, gc
		hpy = guppy.hpy()
		def f(ignored, last, first):
			gc.collect()
			next = hpy.heap()
			print 'SINCE LAST TIME'
			print next - last
			print 'SINCE FOREVER'
			print last - first
			d = client.getPage("http://localhost:8080/")
			d.addCallback(f, next, first)
		first = hpy.heap()			
		f(None, first, first)
		d = defer.Deferred()
		return d
def Run():
      loader = runner.TestLoader()
      loader.methodPrefix = "test02"
      suite = loader.suiteFactory()
      suite.addTest(loader.loadClass(LeakReferenceTestCase))
      return runner.TrialRunner(
            reporter.VerboseTextReporter,
            tracebackFormat='default',
#            logfile = '-',
            ).run(suite)

if __name__ == '__main__':
      if Run().wasSuccessful():
            sys.exit(0)
      else:
            sys.exit(1)

# Interpreted by emacs
# Local Variables:
# compile-command: "( cd .. ; ./config.status tests/test-leak-reference.py ) ; ( cd ../tests ; make VERBOSE_T=-1 TESTS='test-leak-reference.py' check )"
# End:
