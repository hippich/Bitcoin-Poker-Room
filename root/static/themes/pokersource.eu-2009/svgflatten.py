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

import re
import libxml2
from StringIO import StringIO

def flatten(string):
    doc = libxml2.parseDoc(string)
    context = doc.xpathNewContext()
    result = context.xpathEval("//use")
    for orig in result:
        xlink = orig.prop('href')
        id = orig.prop('id')
        id_length = len(id)
        nodes = context.xpathEval('//g[@id="'+xlink[1:]+'"]')
        if len(nodes) == 0:
            nodes = context.xpathEval('//image[@id="'+xlink[1:]+'"]')
        node = nodes[0]
        copy = node.copyNode(extended=True)
        copy.removeNsDef(None)
        copy_context = doc.xpathNewContext()
        copy_context.setContextNode(copy)
        for copy_id in copy_context.xpathEval('.//@id'):
            copy_id.setContent(id + copy_id.content[id_length:])
        tx, ty = re.match('translate\((-?\d+\.?\d*.*),(-?\d+\.?\d*.*)\)', orig.prop('transform')).groups()
        transform = { 'x': float(tx), 'y': float(ty) }
        for c in [ 'x', 'y' ]:
            for coord in copy_context.xpathEval('.//@' + c):
                coord.setContent(str(int(round(float(coord.content) + transform[c]))))
        orig.replaceNode(copy)

    f = StringIO()
    buf = libxml2.createOutputBuffer(f, None)
    doc.saveFileTo(buf, None)
    return f.getvalue()
    
if __name__ == '__main__':
    import sys
    print flatten(sys.stdin.read())
    sys.exit(0)
