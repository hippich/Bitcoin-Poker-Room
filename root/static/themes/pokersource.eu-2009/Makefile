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

JPOKERDIR=../..

all build install clobber clean maintainer-clean check::
	for i in ${SUBDIRS} ; do ${MAKE} -C $$i $@ ; done

check::
	python test-svg2html.py
	python test-svgflatten.py

clean::
	rm -f mockup.html
	rm -f *.pyc

clobber:: clean
	rm -f images/mockup_plain.svg
	rm -f mockup.html

build:: all

all:: mockup.html

mockup.html: images/mockup_plain.svg
	( \
		echo "// generated with make mockup, DO NOT EDIT" ; \
		echo -n '$$.jpoker.plugins.table.templates.room = ' ; \
		python svgflatten.py < images/mockup_plain.svg | python svg2html.py --json || true ; \
	)  > ${JPOKERDIR}/js/mockup.js
	python svgflatten.py < images/mockup_plain.svg | python svg2html.py --html | tidy -indent 2>/dev/null > mockup.html || true
	perl -pi -e 's:</head>:<link href="css/jpoker_table_layout.css" rel="stylesheet" type="text/css" /></head>:' mockup.html
	python svgflatten.py < images/mockup_plain.svg | python svg2html.py --css > css/jpoker_table_layout.css

images/mockup_plain.svg: images/mockup.svg
	inkscape --without-gui --vacuum-defs --export-plain-svg=images/mockup_plain.svg images/mockup.svg
	perl -pi -e 's/xmlns="http:\/\/www.w3.org\/2000\/svg"//' images/mockup_plain.svg
