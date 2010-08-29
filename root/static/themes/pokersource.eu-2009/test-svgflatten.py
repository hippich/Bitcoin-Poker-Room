#!/usr/bin/python
# -*- mode: python -*-
#
# Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
# Copyright (C) 2008 Loic Dachary <loic@dachary.org>
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
import difflib
import sys

from svgflatten import flatten

class flattentest(unittest.TestCase):
    def test_flatten(self):
#<svg xmlns:xlink="http://www.w3.org/1999/xlink" height="800" id="game_window" width="800">       
        svg_string = """\
<?xml version="1.0" encoding="UTF-8"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->
<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="800" height="800" id="game_window">
	<g id="group0">
		<image height="3" id="group0_image0" width="2" x="1" xlink:href="test.png" y="1"/>
	</g>
	<use id="group1" transform="translate(-10.0e-6,-10)" xlink:href="#group0"/>
</svg>
"""
        html_string = """\
<?xml version="1.0" encoding="UTF-8"?>
<!-- Created with Inkscape (http://www.inkscape.org/) -->
<svg xmlns:svg="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.0" width="800" height="800" id="game_window">
	<g id="group0">
		<image height="3" id="group0_image0" width="2" x="1" xlink:href="test.png" y="1"/>
	</g>
	<g id="group1">
		<image height="3" id="group1_image0" width="2" x="1" xlink:href="test.png" y="-9"/>
	</g>
</svg>
"""
        out = flatten(svg_string)
        #print difflib.HtmlDiff().make_file(out.split("\n"), html_string.split("\n"))
        sys.stderr.writelines(difflib.unified_diff(out.split("\n"), html_string.split("\n")))
        self.assertEquals(html_string, out)
        
if __name__ == '__main__':
    unittest.main()

# Interpreted by emacs
# Local Variables:
# compile-command: "python test-svgflatten.py"
# End:
