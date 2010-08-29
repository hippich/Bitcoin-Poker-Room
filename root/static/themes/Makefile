#
#     Copyright (C) 2010 Loic Dachary <loic@dachary.org>
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
# Each sub-directory is expected to have the following structure:
#
# name/css
# name/css/all.css # there must be nothing else necessary to include in 
#                  # the HTML page.
# name/css/images  # images supporting the CSS.
# name/js          # JS supporting the theme.
# name/sounds      # swf sound files required by jpoker.
# name/skin        # HTML files demonstrating each aspect of the theme.
#
THEMES=pokersource.eu-2009 pokersource.eu

all build install clobber clean maintainer-clean check::
	for i in ${THEMES} ; do ${MAKE} -C $$i $@ ; done
