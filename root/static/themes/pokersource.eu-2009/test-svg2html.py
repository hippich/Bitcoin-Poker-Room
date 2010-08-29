#!@PYTHON@
# -*- mode: python -*-
#
# Copyright (C) 2008 Johan Euphrosine <proppy@aminche.com>
# Copyright (C) 2008 Loic Dachary <loic@dachary.org>
# Copyright (C) 2006 Mekensleep
#
# Mekensleep
# 24 rue vieille du temple
# 75004 Paris
#       licensing@mekensleep.com
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

from svg2html import *

class SVG2Gtk(unittest.TestCase):
    def test_SVG2HTML(self):
        svg_string = '<svg xmlns:xlink="http://www.w3.org/1999/xlink" id="game_window" width="800" height="782"><g id="g1"><image id="test" x="0" y="1" width="2" height="3" xlink:href="test.png"/></g></svg>'
        html_string = '<html><head></head><body><div id="game_window" class="jpoker_ptable jpoker_table"><div id="g1"><div id="test" class="jpoker_ptable_test"></div></div></div></body></html>'
        self.assertEquals(html_string, str(SVG2HTML(svg_string)))
    def test_SVG2JSON(self):
        svg_string = '<svg xmlns:xlink="http://www.w3.org/1999/xlink" id="game_window" width="800" height="782"><g id="g1"><image id="test" x="0" y="1" width="2" height="3" xlink:href="test.png"/></g></svg>'
        html_string = "<div id=\\'game_window{id}\\' class=\\'jpoker_ptable jpoker_table\\'><div id=\\'g1{id}\\'><div id=\\'test{id}\\' class=\\'jpoker_ptable_test\\'></div></div></div>"
        self.assertEquals(html_string, str(SVG2JSON(svg_string)))
    def test_SVG2CSS(self):
        svg_string = '<svg xmlns:xlink="http://www.w3.org/1999/xlink" id="game_window" width="800" height="782"><g><image id="test" x="0" y="1" width="2" height="3" xlink:href="../css/images/jpoker_table/test.png"/><image id="test1" x="0" y="1" width="2" height="3" xlink:href="../css/images/jpoker_table/money.png"/></g></svg>'
        css_string = '.jpoker_table .jpoker_ptable { width:800px; height:782px; position:relative; background-image:url("images/jpoker_table/table_background.png"); }\n.jpoker_table .jpoker_ptable_test { width:2px; height:3px; position:absolute; top:1px; left:0px; background-image:url("images/jpoker_table/test.png");}\n.jpoker_table .jpoker_ptable_test1 { width:2px; height:3px; position:absolute; top:1px; left:0px; }\n'
        self.assertEquals(css_string, str(SVG2CSS(svg_string)))
    def test_SVG2CSS_image_translate(self):
        svg_string = '<svg xmlns:xlink="http://www.w3.org/1999/xlink" id="game_window" width="800" height="800"><g><image id="test" x="0" y="1" transform="translate(2, 2)" width="2" height="3" xlink:href="../css/images/jpoker_table/test.png"/><image id="test1" x="0" y="1" transform="translate(3, -1)" width="2" height="3" xlink:href="../css/images/jpoker_table/money.png"/></g></svg>'
        css_string = '.jpoker_table .jpoker_ptable { width:800px; height:800px; position:relative; background-image:url("images/jpoker_table/table_background.png"); }\n.jpoker_table .jpoker_ptable_test { width:2px; height:3px; position:absolute; top:3px; left:2px; background-image:url("images/jpoker_table/test.png");}\n.jpoker_table .jpoker_ptable_test1 { width:2px; height:3px; position:absolute; top:0px; left:3px; }\n'
        self.assertEquals(css_string, str(SVG2CSS(svg_string)))
    def test_SVG2CSS_group_translate(self):
        svg_string = '<svg xmlns:xlink="http://www.w3.org/1999/xlink" id="game_window" width="800" height="800"><g transform="translate(10, 10)"><image id="test" x="0" y="1" transform="translate(2, 2)" width="2" height="3" xlink:href="../css/images/jpoker_table/test.png"/><g transform="translate(5, 5)"><image id="test1" x="0" y="1" transform="translate(3, -1)" width="2" height="3" xlink:href="../css/images/jpoker_table/money.png"/></g></g></svg>'
        css_string = '.jpoker_table .jpoker_ptable { width:800px; height:800px; position:relative; background-image:url("images/jpoker_table/table_background.png"); }\n.jpoker_table .jpoker_ptable_test { width:2px; height:3px; position:absolute; top:13px; left:12px; background-image:url("images/jpoker_table/test.png");}\n.jpoker_table .jpoker_ptable_test1 { width:2px; height:3px; position:absolute; top:15px; left:18px; }\n'
        self.assertEquals(css_string, str(SVG2CSS(svg_string)))        
        
if __name__ == '__main__':
    unittest.main()

# Interpreted by emacs
# Local Variables:
# compile-command: "python test-svg2html.py"
# End:
