#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

  More tests around PhotoCmd (only new one)

"""
import os
import sys
import shutil
from datetime import datetime
############################################################### to be executed here
if __file__ != "runtests.py":
    # execution from here
    PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"jbrout")
    sys.path.append( PATH )
    FOLDER="photos"
else:
    # execution from main jbrout folder
    FOLDER="../unittests/photos"
###############################################################
from jbrout.tools import *   # NEW TOOLS
#~ from jbrout.tools_old import *   # OLD TOOLS
from jbrout.common import cd2d

if __name__ == "__main__":

    # make an attribut list
    la=lambda x: [x.filedate,x.exifdate,x.comment,x.tags,x.isflash,x.readonly,x.resolution]


    cpdate=lambda a,b: -3<=int(a)-int(b)<=3
    def _compare_(a1,a2,compareAll=True):
        if compareAll:
            return a1[1:]==a2[1:] and cpdate(a1[0],a2[0])
        else:
            return a1[2:]==a2[2:]


    format="photo_from_%Y_%m_%d_at_%H_%M_%S"
    folder=FOLDER+"_tmp"

    if os.path.isdir(folder):
        shutil.rmtree(folder)

    shutil.copytree(FOLDER,folder)  # create a temp folder to work in
    try:
        l=[os.path.join(folder,i).decode(sys.getfilesystemencoding()) for i in os.listdir(folder) if i.lower().endswith(".jpg")]

        #==================================================================
        # assert photos are readable
        #==================================================================
        for f in l:
            p=PhotoCmd(f)
            assert p.file == f
            assert not p.readonly

        #==================================================================
        # tests Exifthumb after AUTOROTATE
        #==================================================================
        for f in l:
            f2=PhotoCmd.prepareFile(f,True,True)
            p=PhotoCmd(f2)
            ret=p.isThumbOk()
            if ret>-1:
                assert ret==1

        l=[os.path.join(folder,i).decode(sys.getfilesystemencoding()) for i in os.listdir(folder) if i.lower().endswith(".jpg")]
        #==================================================================
        # tests Exifthumb after ROTATE
        #==================================================================
        for f in l:
            p=PhotoCmd(f)
            p.rebuildExifTB()
            assert p.isThumbOk()==1
            p.rotate("R")
            assert p.isThumbOk()==1
            p.rotate("L")
            assert p.isThumbOk()==1


        #TODO: ... to be continued ...

    finally:
        shutil.rmtree(folder)   # delete tempfolder
