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

import os
import string
import uuid
import datetime

class GenerateLangTiddlers:
    def getTiddler(self, lang, langs):
        def lang2wiki(l):
            if l == lang: return l
            elif l == 'en': return '[[en|index.html]]'
            else: return '[[%s|index-%s.html]]' % (l, l)
        return string.join([lang2wiki(l) for l in langs], ' | ')

    def run(self, path, time=datetime.datetime.today().strftime('%Y%m%d%H%M')):
        f = open(path + '/l10n/LINGUAS')
        langs = [l for l in f.read().strip().split('\n') if '#' not in l]
        f.close()
        for lang in langs:
            directory = path + '/index-%s' % lang
            if not os.path.exists(directory):
                os.mkdir(directory)
                fake_translation_tiddler = directory + '/FakeTranslation.tiddler'
                fake_translation_tiddler_div = fake_translation_tiddler + '.div'
                f = open(fake_translation_tiddler, 'w')
                f.write('config.locale = "%s"; // W3C language tag' % lang)
                f.close()
                f = open(fake_translation_tiddler_div, 'w')
                f.write('title="FakeTranslation" modifier="script" created="%s" changecount="1" tags="systemConfig"' % time)
                f.close()
            lang_tiddler = directory + '/lang.tiddler'
            lang_tiddler_div = lang_tiddler + '.div'
            skin_lang_tiddler = directory + '/skin-lang.tiddler'
            skin_lang_tiddler_div = skin_lang_tiddler + '.div'
            tiddler = self.getTiddler(lang, langs)
            f = open(lang_tiddler, 'w')
            f.write(tiddler+'<<tiddler SiteStats>>')
            f.close()
            f = open(lang_tiddler_div, 'w')
            f.write('title="lang" modifier="script" created="%s" changecount="1"' % time)
            f.close()
            f = open(skin_lang_tiddler, 'w')
            f.write(tiddler)
            f.close()
            f = open(skin_lang_tiddler_div, 'w')
            f.write('title="skin-lang" modifier="script" created="%s" changecount="1"' % time)
            f.close()

if __name__ == '__main__':
    g = GenerateLangTiddlers()
    g.run('jpoker')
