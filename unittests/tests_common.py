#!/usr/bin/python
# -*- coding: utf-8 -*-
if __name__ == "__main__":
    import sys
    import os
    PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "jbrout")
    sys.path.append(PATH)

from jbrout.common import *

assert cd2rd("20071114111000") == "14/11/2007 11:10:00"
assert cd2rd("20071114") == "14/11/2007"
assert cd2rd("") == ""
assert cd2rd(None) is None

from datetime import datetime
assert cd2d("20071114111000") == datetime(2007, 11, 14, 11, 10, 0)

assert format_file_size_for_display(0) == "0 bytes"
assert format_file_size_for_display(189) == "189 bytes"
assert format_file_size_for_display(18566) == "18.1 KB"
assert format_file_size_for_display(256618566) == "244.7 MB"
assert format_file_size_for_display(116618552266) == "108.6 GB"


assert xpathquoter("foo") == "'foo'"
assert xpathquoter("fo'o") == '''"fo'o"'''
assert xpathquoter("fo'o'o") == '''"fo'o'o"'''
assert xpathquoter('fo"o') == """'fo"o'"""
assert xpathquoter('fo"o"o') == """'fo"o"o'"""
assert xpathquoter("""l'eau "de" la""") == \
    """concat("l'eau ",'"','de','"',' la')"""

from lxml.etree import fromstring, Element


def test(val):
    print "test", (val,)
    xml = fromstring("""<root/>""")
    xml.append(Element("a", {"key": val}))
    assert len(xml.xpath("""//a[@key=%s]""" % xpathquoter(val))) == 1


test("""value""")
test("""&""")
test("""&amp;""")
test("""<""")
test(""">""")
test("""&quot;""")
test('\\')
test('/')
test('"')
test('\"')
test('\\"')
test("'")
test("\'")
test("\\'")
test("""l'eau "de" l'a""")
test("""l'e"a'u" "d'e" "l''a""")
test("""l'e"a\'u" \"d'a" \\"l'\\'oa""")
test(u"""l'ê"a\'u" \"d'à" \\"l'\\'ôa""")
