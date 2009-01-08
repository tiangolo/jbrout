#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    this will build the Windows launched and installer
"""
import os
import re
from libs import run,megarun

baseVersion = '0.3'
basePath = os.path.realpath(os.path.join(os.path.dirname(__file__),".."))


def mkWin():
    mkWinLauncher()
    mkWinStandAlone()

def writeVersionFiles():
    megarun(""" rm -f jbrout/data/version.txt""")
    if os.path.isdir(os.path.join(basepath, '.git')):
        infoCmd = ["git","svn","info"]
    else:
        infoCmd = ["svn","info"]
    try:
        version=baseVersion + "." + re.search("(?<=Revision\: )\d+", run(infoCmd)).group()
        open("jbrout/data/version.txt","w").write(version)
    except:
        print "Unable to build windows version without version number from svn"
        exit(1)


def mkWinLauncher():
    megarun('makensis %s'% os.path.join('dist','launcher.nsi'))

def mkWinStandAlone():
    megarun('makensis %s'% os.path.join('dist','StandAlone-py2.5.nsi'))

if __name__ == "__main__":
    
    os.chdir(basePath)

    mkWin()
