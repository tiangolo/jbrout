#!/usr/bin/python
# -*- coding: utf-8 -*-

from core.common import *

assert cd2rd("20071114111000") == "14/11/2007 11:10:00"
assert cd2rd("20071114") == "14/11/2007"
assert cd2rd("") == ""
assert cd2rd(None) == None

from datetime import datetime
assert cd2d("20071114111000") == datetime(2007,11,14,11,10,0)

assert format_file_size_for_display(0) == "0 bytes"
assert format_file_size_for_display(189) == "189 bytes"
assert format_file_size_for_display(18566) == "18.1 KB"
assert format_file_size_for_display(256618566)== "244.7 MB"
assert format_file_size_for_display(116618552266) == "108.6 GB"

