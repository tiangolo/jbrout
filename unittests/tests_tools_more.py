#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

  More tests around PhotoCmd (only new one)

"""
import os
import sys
import shutil
######################################################### to be executed here
if os.path.basename(__file__) != "runtests.py":
    # execution from here
    PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jbrout")
    sys.path.append(PATH)
    FOLDER = "photos"
else:
    # execution from main jbrout folder
    FOLDER = "../unittests/photos"
###############################################################
from jbrout.tools import *  # NEW TOOLS
# ~ from jbrout.tools_old import *   # OLD TOOLS
from jbrout.common import cd2d

if __name__ == "__main__":

    # make an attribut list
    la = lambda x: [x.filedate, x.exifdate, x.comment, x.tags, x.isflash,
                    x.readonly, x.resolution]

    cpdate = lambda a, b: -3 <= int(a) - int(b) <= 3

    def _compare_(a1, a2, compareAll=True):
        if compareAll:
            return a1[1:] == a2[1:] and cpdate(a1[0], a2[0])
        else:
            return a1[2:] == a2[2:]

    #==================================================================
    # test PhotoCmd.giveMeANewName
    #==================================================================
    assert PhotoCmd.giveMeANewName("jo.jpg") == "jo(1).jpg"
    assert PhotoCmd.giveMeANewName(u"/kif/jo.jpg") == u"/kif/jo(1).jpg"
    assert PhotoCmd.giveMeANewName("/kif/jo (4).jpg") == "/kif/jo (5).jpg"
    assert PhotoCmd.giveMeANewName("c:\\kif\\jo (123).jpg") == \
        "c:\\kif\\jo (124).jpg"
    assert PhotoCmd.giveMeANewName("jo(44).txt") == "jo(45).txt"

    format = "photo_from_%Y_%m_%d_at_%H_%M_%S"
    folder = FOLDER + "_tmp"

    if os.path.isdir(folder):
        shutil.rmtree(folder)

    shutil.copytree(FOLDER, folder)  # create a temp folder to work in
    try:
        l = [os.path.join(folder, i).decode(sys.getfilesystemencoding())
             for i in os.listdir(folder) if i.lower().endswith(".jpg")]

        #==================================================================
        # assert photos are readable
        #==================================================================
        for f in l:
            p = PhotoCmd(f)
            assert not p.readonly
            assert p.file == f  # are not renamed
            assert p.exifdate  # and got exifdate

        #==================================================================
        # tests renaming
        #==================================================================
        for f in l:
            p = PhotoCmd(f, needAutoRename=True)
            assert p.file != f  # are renamed
            newNameShouldBe = cd2d(p.exifdate).strftime(PhotoCmd.format)
            assert newNameShouldBe in p.file  # right new name

        l = [os.path.join(folder, i).decode(sys.getfilesystemencoding())
             for i in os.listdir(folder) if i.lower().endswith(".jpg")]
        #==================================================================
        # tests Exifthumb after AUTOROTATE
        #==================================================================
        for f in l:
            p = PhotoCmd(f, needAutoRotation=True)
            if p.isThumbOk() == -1:
                p.rebuildExifTB()
            assert p.isThumbOk() == 1

        #==================================================================
        # tests Exifthumb after ROTATE
        #==================================================================
        for f in l:
            p = PhotoCmd(f)
            p.rebuildExifTB()
            assert p.isThumbOk() == 1
            p.rotate("R")
            assert p.isThumbOk() == 1
            p.rotate("L")
            assert p.isThumbOk() == 1

        # TODO: ... to be continued ...
    finally:
        shutil.rmtree(folder)  # delete tempfolder
