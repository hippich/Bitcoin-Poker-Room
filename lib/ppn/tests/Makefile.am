#
# Copyright (C) 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2005, 2006 Mekensleep <licensing@mekensleep.com>
#                          24 rue vieille du temple, 75004 Paris
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
#
MAINTAINERCLEANFILES = Makefile.in

EXTRA_DIST = \
	createdatabase \
	schema.sql \
	poker.server.xml \
	pokersql.xml \
	pokersqlfail.xml \
	poker.test18pokerclient.xml \
	conf/poker.bot.xml.in \
	conf/poker.server.xml.in \
	poker-engine/poker.1-2-no-limit.xml \
	poker-engine/poker.holdem.xml \
	test-pokerauth/pokerauth.py \
	coverage.py \
	monitorplugin.py \
	testfilter.py \
	testtourney_select_info.py \
	testtourney_select_info_no_call.py \
	testerrorfilter.py \
	finishedfilter.py \
	testpackets.py \
	testmessages.py \
	testsettings.xml \
	test-leak.py.in \
	test-leak-no-trial.py.in \
	test-leak-reference.py.in \
	test-leak-exarkun.py.in \
	test-pokerdatabase \
	testclock.py \
	testlock.py \
	__init__.py \
	setupMysqlVariables \
	chameleon.png

TESTS_ENVIRONMENT = ./run
#
# Do NOT sort entries because the order matters 
#
TESTS = coverage-reset \
	upgrade \
	test-clientserver.py \
	test-currencyclient.py \
	test-packets.py \
	test-pokeravatar.py \
	test-pokerpackets.py \
	test-pokerclientpackets.py \
	test-pokerbotlogic.py \
	test-pokerbot.py \
	test-pokerdatabase.py \
	test-pokerservice.py \
	test-pokerservice-load.py \
	test-pokersql.py \
	test-pokerauth.py \
	test-user.py \
	test-pokertable.py \
	test-pokerclient.py \
	test-pokerexplain.py \
	test-pokergameclient.py \
	test-pokerlock.py \
	test-pokercashier.py \
	test-webservice.py \
	test-protocol.py \
	test-pokersite.py \
	test-pokermemcache.py \
	test-pokernetworkconfig.py \
	test-proxyfilter.py \
	test-nullfilter.py \
	test-sessionproxyfilter.py \
	test-proxy.py \
	test-pokerserver.py \
	test-pokerserver-run-load.py \
	test-pokerrestclient.py \
	testcurrency.php \
	testpoker.php \
	testbirthday.php \
	testwebservice.php \
	coverage-report      

# Regarding XFAIL_TESTS: the only items we typically list here are tests
# designed to cover open bugs.  We expect them to fail until the bug is
# closed.  If you close a bug, be sure to remove the test-bug-NUMBER.py
# entry from XFAIL_TESTS below.

export XFAIL_TESTS := 

.PHONY: coverage-reset coverage-report

export top_srcdir
export MYSQL_TEST_DBHOST
export MYSQL_TEST_DBROOT
export MYSQL_TEST_DBROOT_PASSWORD
export MYSQL

clean-local:
	rm -fr .coverage annotated _trial_temp phpunit
