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
SHELL=/bin/bash
BINDIR=../binary
JPOKERDIR = ../../..
LANGDIR = ${JPOKERDIR}/l10n
THEMEDIR = ${JPOKERDIR}/themes/pokersource.eu-2009

all build install clobber clean maintainer-clean check::

build:: makedir cook check

check::
	python test-generateLangTiddlers.py

clean:: 
	rm -fr standalone-temp-* *.pyc

maintainer-clean:: clean
	rm -fr ${BINDIR}

clobber:: maintainer-clean
	rm -fr gems

makedir:
	mkdir -p ${BINDIR}/standalone

LINGUAS = $(shell grep -v ^\# ${LANGDIR}/LINGUAS)
STANDALONE_TW = $(LINGUAS:%=${BINDIR}/standalone/index-%.html)
# 
# because english is the default language, it has no
# associated .json file
#
LANG_JSON = $(LINGUAS:%=${LANGDIR}/jpoker-%.json)
LANG_TW = $(LINGUAS:%=${BINDIR}/index-%.html)

update_gems: 
	rm -fr gems
	${MAKE} gems/bin/tiddlywiki_cp

# retry at most 4 times if there is an error because gem randomly fails
gems/bin/tiddlywiki_cp: 
	gem install --include-dependencies --no-rdoc --no-ri --install-dir gems tiddlywiki_cp
	patch -d gems/gems/tiddlywiki_cp-0.5.3 -p1 < tiddlywiki_cp_locale2lang.patch
	# ruby1.8 & rubygems backward compatibility fix for when the gems is built with ruby1.9 and
	# used with ruby1.8
	# http://code.whytheluckystiff.net/list/shoes/2008/11/14/4469-re-hacking-shoes.html
	perl -pi -e 's/ s.respond_to\? :required_rubygems_version=/ s.public_methods.include?("required_rubygems_version=")/' gems/specifications/*.gemspec
	perl -pi -e 's/ s.respond_to\? :specification_version / s.public_methods.include?("specification_version=") /' gems/specifications/*.gemspec

${BINDIR}/index-%.html: gems/bin/tiddlywiki_cp 
${BINDIR}/index.html: gems/bin/tiddlywiki_cp 
#${BINDIR}/standalone/index-%.html : gems/bin/tiddlywiki_cp

GEMSCONTEXT=GEM_HOME=gems gems/bin/

EMPTY=tiddlywiki-2.3.html

${BINDIR}/index-%.html: JpokerPlugin/* index-*/* index/* tiddlers/* markup/*  gems/bin/tiddlywiki_cp
	cp ${EMPTY} $@
	${RUBY} ${GEMSCONTEXT}tiddlywiki_cp -a JpokerPlugin index-$* index tiddlers markup $@

${BINDIR}/index.html: ${BINDIR}/index-en.html
	cp ${BINDIR}/index-en.html ${BINDIR}/index.html

#
# Gather css, js and l10n files that are to be inlined in the TiddlyWiki
#
standalone-temp-% : markup/MarkupPostBody.tiddler ${JPOKERDIR}/js/* ${JPOKERDIR}/jquery/* ${THEMEDIR}/css/* tiddlers-standalone/*
	rm -fr $@ ; mkdir $@
	#
	# Parse MarkupPostBody for list of js files, copy them and create .div files.
	declare -i a=1 ; sed -ne 's/.*src="\([^"]*\)".*/\1/p' < markup/MarkupPostBody.tiddler | while read file ; do printf 'title="%02d_%s" author="script" tags="excludeLists excludeSearch systemConfig"\n' $$a "$$file" > standalone-temp-$*/$${file##*/}.div ; cp $$file standalone-temp-$*/; let a++ ; done
	#
	# Flatten all css files to one file and create a .div file
	ruby getcss.rb ${THEMEDIR}/css/jpoker.css -d $@/jpoker.css
	printf 'title="JpokerStyleSheet" author="script"\n' > $@/"jpoker.css.div";
	#
	# If lang is not en, convert json file to a plugin js file and create .div file
	if [ -a ${LANGDIR}/jpoker-$*.json ]; then sed "1i\$$.gt.setLang('$*');$$.gt.messages.$*=" ${LANGDIR}/jpoker-$*.json > $@/"jpoker-$*.js"; printf 'title="%s-JpokerJson" author="script" tags="excludeLists excludeSearch systemConfig"\n' $* > $@/"jpoker-$*.js.div"; fi

#
# Create standalone files with inlined CSS, JavaScript and l10n
#
${BINDIR}/standalone/images:
	cp -R -f ${THEMEDIR}/css/images ${BINDIR}/standalone

${BINDIR}/standalone/i:
	cp -R -f ${THEMEDIR}/css/jpoker_jquery_ui/i ${BINDIR}/standalone

${BINDIR}/standalone/index-%.html: JpokerPlugin/* index-*/* index/* tiddlers/* tiddlers-standalone/* standalone-temp-% gems/bin/tiddlywiki_cp ${BINDIR}/standalone/images ${BINDIR}/standalone/i
	cp -f ${EMPTY} $@
	${RUBY} ${GEMSCONTEXT}tiddlywiki_cp -a JpokerPlugin index-$* index tiddlers tiddlers-standalone/* standalone-temp-$*/* $@

${BINDIR}/standalone/index.html: ${BINDIR}/standalone/index-en.html
	cp ${BINDIR}/standalone/index-en.html $@

${BINDIR}/standalone: ${STANDALONE_TW} ${BINDIR}/standalone/index.html

cook: ${LANG_TW} ${BINDIR}/index.html ${BINDIR}/standalone
