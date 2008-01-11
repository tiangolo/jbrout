#!/usr/bin/python
# -*- coding: utf-8 -*-

from jbrout.externaltools import *


assert splitCommandLine("""/bin/toto   " to fork" -aa """) == \
               ['/bin/toto', ' to fork', '-aa']

assert splitCommandLine(""" /bin/toto  " to fork " -aa " h l " -i "9" """) == \
                ['/bin/toto', ' to fork ', '-aa', ' h l ', '-i', '9']

assert splitCommandLine("""  /bin/to to   -s 'ko ko '""") == \
               ['/bin/to','to', '-s',"'ko","ko","'"]

assert splitCommandLine("""  /bin/toto "ko """) == \
               ['/bin/toto','ko']

assert splitCommandLine("""  /bin/toto "ki ki " "ko """) == \
               ['/bin/toto',"ki ki ",'ko']

assert splitCommandLine("""  /bin/toto ko" """) == \
               ['/bin/toto','ko']

assert splitCommandLine("""  /bin/toto ko"ka """) == \
               ['/bin/toto','ko"ka']

assert splitCommandLine("""  /bin/toto " ko ka"ku """) == None
assert splitCommandLine("""  /bin/toto ku" ko ka" """) == None
assert splitCommandLine("""  /bin/toto " ko ka"-ku """) == None
assert splitCommandLine("""  /bin/toto -ku" ko ka" """) == None
assert splitCommandLine("") == []
