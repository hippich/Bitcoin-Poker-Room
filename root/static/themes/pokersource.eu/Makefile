#
#     Copyright (C) 2008 - 2010 Loic Dachary <loic@dachary.org>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

SUBDIRS=sounds-sources

all:: 
	$(MAKE) ${LANG_JSON}

LINGUAS = $(shell grep -v ^\# l10n/LINGUAS)
LANG_DIR = l10n

# 
# because english is the default language, it has no
# associated .json file
#
LANG_JSON = $(LINGUAS:%=${LANG_DIR}/jpoker-%.json)

messages.pot: js/jpoker.js
	xgettext --extract-all \
		 --lang java \
		 --from-code=UTF-8 \
		 --copyright-holder='Loic Dachary <loic@dachary.org>' \
		 --output=$@ \
		 --sort-output \
		 $<

${LANG_DIR}/jpoker-%.po: messages.pot
	msgmerge -s -U $@ messages.pot
	touch $@
	: now edit with poedit $@

${LANG_DIR}/%.mo: ${LANG_DIR}/jpoker-%.po
	msgfmt --check --output-file $@ $<
	mkdir -p $*/LC_MESSAGES
	cp $@ $*/LC_MESSAGES

${LANG_DIR}/jpoker-%.json: ${LANG_DIR}/%.mo
	python ../../../mo2json.py $* > $@

maintainer-clean::
	rm -f messages.pot 
	rm -fr ${LINGUAS:%=%/} l10n/*.mo

# mimic when a new lang shows
#newlang: 
#	$(MAKE) messages.pot
#	msginit -l fr_FR -o l10n/jpoker-fr.po -i messages.pot

all build install clobber clean maintainer-clean check::
	for i in ${SUBDIRS} ; do ${MAKE} -C $$i $@ ; done
