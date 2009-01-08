#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This will build the Windows launcher and installer
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
    if os.path.isdir(os.path.join(basePath, '.git')):
        infoCmd = ["git","svn","info"]
    else:
        infoCmd = ["svn","info"]
    try:
        version=baseVersion + "." + re.search("(?<=Revision\: )\d+", run(infoCmd)).group()
        megarun(""" rm -f jbrout/data/version.txt
                    rm -f dist/version.nsi""")
        open("jbrout/data/version.txt","w").write(version)
        open("dist/version.nsi","w").write('!define PRODUCT_VERSION "' + version + '"')
    except:
        print """Unable to build windows version without version number from svn,
                 attempting to run with existing files, if this fails to build
                 please create version files manually"""


def mkWinLauncher():
    megarun('rm -f dist/jBrout.exe')
    megarun('makensis %s'% os.path.join('dist','launcher.nsi'))

def mkWinStandAlone():
    megarun('rm -f dist/jBrout-*-Setup.exe')
    megarun('makensis %s'% os.path.join('dist','StandAlone-py2.5.nsi'))

if __name__ == "__main__":
    
    os.chdir(basePath)
    
    writeVersionFiles()
    
    mkWin()
