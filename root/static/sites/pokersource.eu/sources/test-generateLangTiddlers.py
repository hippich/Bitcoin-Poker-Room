#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301, USA.
#

import unittest
import os
import string
import uuid
import datetime

from generateLangTiddlers import GenerateLangTiddlers

class GenerateLangTiddlersGetTiddlerTestCase(unittest.TestCase):
    def test(self):
        langs = ['en', 'fr', 'ja']
        g = GenerateLangTiddlers()
        self.assertEquals('[[en|index.html]] | fr | [[ja|index-ja.html]]', g.getTiddler('fr', langs))
        self.assertEquals('en | [[fr|index-fr.html]] | [[ja|index-ja.html]]', g.getTiddler('en', langs))
        self.assertEquals('[[en|index.html]] | [[fr|index-fr.html]] | ja', g.getTiddler('ja', langs))

class GenerateLangTiddlersRunTestCase(unittest.TestCase):
    def setUp(self):
        self.path = "/tmp/%s" % uuid.uuid4()
        self.langs = ['en', 'fr', 'ja']
        os.mkdir(self.path)
        os.mkdir(self.path + '/index-fr')
        os.mkdir(self.path + '/l10n')
        f = open(self.path + '/l10n/LINGUAS', 'w')
        f.write(string.join(['#ignore']+self.langs+['\n'], '\n'))
        f.close()
        os.mkdir(self.path + '/markup')
    def test(self):
        time = datetime.datetime.today().strftime('%Y%m%d%H%M')
        g = GenerateLangTiddlers()
        g.run(self.path, time)
        for lang in self.langs:
            tiddler = g.getTiddler(lang, self.langs)
            directory = self.path + '/index-%s' % lang
            self.assertEquals(True, os.path.exists(directory))
            lang_tiddler = directory + '/lang.tiddler'
            self.assertEquals(True, os.path.exists(lang_tiddler))
            self.assertEquals(tiddler+'<<tiddler SiteStats>>', open(lang_tiddler).read())
            lang_tiddler_div = lang_tiddler + '.div'            
            self.assertEquals(True, os.path.exists(lang_tiddler_div))
            self.assertEquals('title="lang" modifier="script" created="%s" changecount="1"' % time, open(lang_tiddler_div).read())
            skin_lang_tiddler = directory + '/skin-lang.tiddler'
            self.assertEquals(True, os.path.exists(skin_lang_tiddler))
            self.assertEquals(tiddler, open(skin_lang_tiddler).read())
            skin_lang_tiddler_div = skin_lang_tiddler + '.div'            
            self.assertEquals(True, os.path.exists(skin_lang_tiddler_div))
            self.assertEquals('title="skin-lang" modifier="script" created="%s" changecount="1"' % time, open(skin_lang_tiddler_div).read())
            fake_translation_tiddler = directory + '/FakeTranslation.tiddler'
            self.assertEquals(lang != 'fr', os.path.exists(fake_translation_tiddler))
            if lang != 'fr':
                self.assertEquals('config.locale = "%s"; // W3C language tag' % lang, open(fake_translation_tiddler).read())
            fake_translation_tiddler_div = fake_translation_tiddler + '.div'       
            self.assertEquals(lang != 'fr', os.path.exists(fake_translation_tiddler_div))
            if lang != 'fr':
                self.assertEquals('title="FakeTranslation" modifier="script" created="%s" changecount="1" tags="systemConfig"' % time, open(fake_translation_tiddler_div).read())

if __name__ == '__main__':
    unittest.main()
