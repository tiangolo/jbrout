#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
#####################################################################
Run unitests of jbrout
#####################################################################

Install the minimum life of jbrout and run all files which looks
like "tests_*.py" in the current folder.

#####################################################################
"""
import os
import sys
PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "jbrout")

# install the "_" function
__builtins__.__dict__["_"] = lambda x: x

# make the import path good
sys.path.append(PATH)

if __name__ == "__main__":
    l = [i for i in os.listdir(".")
         if i.startswith(u"tests_") and i.endswith(u".py")]
    l.sort()
    os.chdir("../jbrout")
    for i in l:
        print "--- Tests", i
        execfile("../unittests/" + i)
