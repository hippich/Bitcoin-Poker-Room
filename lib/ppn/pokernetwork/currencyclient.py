#
# Copyright (C) 2006, 2007, 2008, 2009 Loic Dachary <loic@dachary.org>
# Copyright (C) 2006             Mekensleep <licensing@mekensleep.com>
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
#
from types import *
from twisted.web import client
from twisted.internet import defer, reactor

class RealCurrencyClient:

    def __init__(self):
        self.verbose = 0
        self.getPage = client.getPage

    def request(self, *args, **kwargs):
        base = kwargs['url']
        if "?" in base:
            base += '&'
        else:
            base += '?'
            
        args = [ base + "command=" + kwargs.get('command', 'get_note') ]
        for key in ('name', 'serial', 'value', 'transaction_id'):
            if kwargs.has_key(key): 
                arg = kwargs[key]
                args.append("%s=%s" % ( key, arg ))

        if kwargs.has_key('notes'):
            index = 0
            for (url, serial, name, value) in kwargs['notes']:
                args.append("name[%d]=%s" % ( index, name ) )
                args.append("serial[%d]=%s" % ( index, serial ) )
                args.append("value[%d]=%s" % ( index, value ) )
                index += 1
                
        if kwargs.has_key('note'):
            (url, serial, name, value) = kwargs['note']
            args.append("name=%s" % name )
            args.append("serial=%s" % serial )
            args.append("value=%s" % value )
                
        if kwargs.has_key('values'):
            index = 0
            for value in kwargs['values']:
                args.append("values[%d]=%d" % ( index, value ))
                index += 1
        url = "&".join(args)
        #print "RealCurrencyClient: " + url
        return self.getPage(url)

    def parseResultNote(self, result):
	has_error = False
        notes = []
        for line in result.split("\n"):
            note = line.split("\t")
            if len(note) == 4:
                notes.append(( note[0], int(note[1]), note[2], int(note[3]) ),)
            else:
                print "RealCurrencyClient::parseResultNote ignore line: " + line
		has_error = True
	if has_error:
		raise Exception("expected notes got something else")
        return notes

    def mergeNotes(self, *args):
        deferred = self.request(url = args[0][0], command = 'merge_notes', notes = args)
        deferred.addCallback(self.parseResultNote)
        return deferred

    def meltNotes(self, *notes):
        values = sum(map(lambda note: note[3], notes))
        deferred = self.request(url = notes[0][0], command = 'merge_notes', notes = notes, values = [ values ])
        deferred.addCallback(self.parseResultNote)
        return deferred

    def changeNote(self, note):
        deferred = self.request(url = note[0], command = 'change_note', note = note)
        deferred.addCallback(self.parseResultNote)
        return deferred

    def getNote(self, url, value):
        deferred = self.request(url = url, command = 'get_note', value = value)
        deferred.addCallback(self.parseResultNote)
        return deferred

    def checkNote(self, note):
        deferred = self.request(url = note[0], command = 'check_note', note = note)
        deferred.addCallback(self.parseResultNote)
        return deferred

    def breakNote(self, note, *values):
        deferred = False
        if len(values) == 2:
            numeric_values = map(int, values)
            numeric_values.sort()
            if numeric_values[0] == 0:
                notes = [ note, [ note[0], 0, '', 0 ] ]
                deferred = defer.Deferred()
                reactor.callLater(0, lambda: deferred.callback(notes))
        if not deferred:
            deferred = self.request(url = note[0], command = 'break_note', note = note, values = values)
            deferred.addCallback(self.parseResultNote)
        return deferred

    def commit(self, url, transaction_id):
	def validate(result):
            if self.verbose > 2: print "CurrencyClient::commit " + str(result)
            if len(result.split("\n")) > 1:
                raise Exception("expected a single line got " + str(result) + " instead")
            return result
        deferred = self.request(url = url, command = 'commit', transaction_id = transaction_id)
	deferred.addCallback(validate)
	return deferred
        
from twisted.python import failure
from twisted.web import error

CurrencyClient = RealCurrencyClient

FakeCurrencyFailure = False

Verbose = False

class FakeCurrencyClient:

    def __init__(self):
        self.serial = 1
        self.check_note_result = True
        self.commit_result = True
        
    def message(self, string):
        print "FakeCurrencyClient: " + string
        
    def breakNote(self, (url, serial, name, value), *values):
        if Verbose: self.message("breakNote vaues %s" % str(values))
        if values: 
            values = map(int, values)
            values.sort()
            values.reverse()

        notes = []
        if values[-1] == 0:
            notes.append((url, serial, name, value))
            notes.append((url, 0, '', 0))
        else:
            for note_value in values:
                if value < note_value: continue
                count = value / note_value
                value %= note_value
                for i in xrange(count):
                    notes.append((url, self.serial, "%040d" % self.serial, note_value))
                    self.serial += 1
                if value <= 0: break
            if value > 0:
                notes.append((url, self.serial, "%040d" % self.serial, note_value))
                self.serial += 1
        d = defer.Deferred()
        if FakeCurrencyFailure:
            reactor.callLater(0, lambda: d.errback(failure.Failure(error.Error(500, "breakNote: fake error", "(page content)"))))
        else:
            reactor.callLater(0, lambda: d.callback(notes))
        return d

    def mergeNotes(self, *notes):
        if Verbose: self.message("mergeNotes")
        self.serial += 1
        result = list(notes[0])
        result[1] = self.serial
        result[2] = "%040d" % self.serial
        result[3] = sum(map(lambda x: x[3], notes))
        d = defer.Deferred()
        reactor.callLater(0, lambda: d.callback([result]))
        return d

    meltNotes = mergeNotes

    def changeNote(self, note):
        if Verbose: self.message("changeNote")
        self.serial += 1
        result = note.copy()
        result[1] = self.serial
        result[2] = "%040d" % self.serial
        d = defer.Deferred()
        reactor.callLater(0, lambda: d.callback(result))
        return d

    def _buildNote(self, url, value):
        if Verbose: self.message("_buildNote")
        self.serial += 1
        name = "%040d" % self.serial
        return ( url, self.serial, name, value )

    def getNote(self, url, value):
        if Verbose: self.message("getNote")
        note = self._buildNote(url, value)
        d = defer.Deferred()
        reactor.callLater(0, lambda: d.callback(note))
        return d

    def checkNote(self, note):
        if Verbose: self.message("checkNote")
        if self.check_note_result:
            result = note
        else:
            result = failure.Failure()
        d = defer.Deferred()
        reactor.callLater(0, lambda: d.callback(result))
        return d

    def commit(self, url, transaction_id):
        if Verbose: self.message("commit")
        if self.commit_result:
            result = "OK"
        else:
            result = failure.Failure()
        d = defer.Deferred()
        reactor.callLater(0, lambda: d.callback(result))
        return d

