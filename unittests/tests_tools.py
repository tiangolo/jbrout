#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
from datetime import datetime
############################################################### to be executed here
if os.path.basename(__file__) != "runtests.py":
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

        #TODO: test isflash
        #TODO: test isreadonly

        #==================================================================
        # test NormalizeName, format, and renaming according dates
        # without modification of attributes
        #==================================================================
        PhotoCmd.setNormalizeNameFormat(format)
        for f in l:
            p=PhotoCmd(f,needAutoRename=True)
            attrsBefore=la(p)

            if p.exifdate:
                d=p.exifdate
            else:   # if not exif date date file is taken
                d=p.filedate

            newNameShouldBe=cd2d(d).strftime(format)
            assert newNameShouldBe in p.file

            attrsAfter=la(p)
            assert _compare_(attrsAfter,attrsBefore)

        #==================================================================
        # test autorotation,
        # without modification of attributes
        #==================================================================
        l=[os.path.join(folder,i).decode(sys.getfilesystemencoding()) for i in os.listdir(folder) if i.lower().endswith(".jpg")]
        for f in l:
            p=PhotoCmd(f,needAutoRotation=True)
            p.addTags([u"àùù",])
            p.addComment(u"àçç")
            attrsBefore=la(p)
            w,h=[int(i.strip()) for i in p.resolution.split("x")]

            w2,h2=[int(i.strip()) for i in p.resolution.split("x")]
            attrsAfter=la(p)
            if attrsAfter[-1] != attrsBefore[-1]:
                assert w2==h and h2==w
            assert _compare_( attrsAfter[:-1],attrsBefore[:-1])
            p.clear()
            p.addComment(u"")


        #==================================================================
        # test tags
        # without modification of attributes
        #==================================================================
        for file in l:
            p=PhotoCmd(file)
            attrsBefore=la(p)
            p.clear()
            assert p.tags==[]
            p.add(u"kéké")
            assert u"kéké" in p.tags
            assert len(p.tags)==1

            p.addTags([u"kéké",u"çàlé"])
            assert u"kéké" in p.tags
            assert u"çàlé" in p.tags
            assert len(p.tags)==2

            p.sub(u"çàlé")
            assert u"kéké" in p.tags
            assert len(p.tags)==1

            p.subTags([u"kéké",u"çàlé"])
            assert len(p.tags)==0
            attrsAfter=la(p)
            assert _compare_(attrsAfter,attrsBefore)

        #==================================================================
        # test comment
        # without modification of attributes
        #==================================================================
        for file in l:
            p=PhotoCmd(file)
            p.add(u"kàkà")
            attrsBefore=la(p)

            p.addComment(u"kélàçù")
            assert p.comment == u"kélàçù"

            p.addComment(u"")
            assert p.comment == ""
            attrsAfter=la(p)
            assert _compare_(attrsAfter,attrsBefore)


        #==================================================================
        # test redate, normalizename
        # without modification of attributes
        #==================================================================
        nd=lambda d : (cd2d(d)+timedelta(weeks=1, days=1,hours=1,minutes=1,seconds=1)).strftime("%Y%m%d%H%M%S")
        for file in l:
            p=PhotoCmd(file,needAutoRename=True)
            p.addComment(u"kélàçù")
            p.add(u"kàkà")
            attrsBefore=la(p)

            name= p.file
            exifdate = p.exifdate
            filedate = p.filedate
            p.redate(1,1,1,1,1)
            assert p.file == name                       # don't change his name after redate
            

            attrsAfter=la(p)
            assert _compare_(attrsAfter,attrsBefore,False)  # don't compare dates (done before)


            p=PhotoCmd(file,needAutoRename=True)
            newNameShouldBe=cd2d(p.exifdate).strftime(format)
            attrsAfter=la(p)
            assert _compare_(attrsAfter,attrsBefore,False)  # don't compare dates (done before)
            assert newNameShouldBe in p.file
            p.addComment(u"")
            p.clear()


        #==================================================================
        # test rotate
        # without modification of attributes
        #==================================================================
        l=[os.path.join(folder,i).decode(sys.getfilesystemencoding()) for i in os.listdir(folder) if i.lower().endswith(".jpg")]
        for file in l:
            p=PhotoCmd(file)
            p.addComment(u"kélàçù")
            p.add(u"kàkà")
            attrsBefore=la(p)

            p.rotate("R")
            attrsAfter=la(p)
            assert attrsAfter[-1] != attrsBefore[-1]
            assert _compare_(attrsAfter[:-1],attrsBefore[:-1]) # don't compare resol

            p.rotate("L")
            attrsAfter=la(p)

            assert _compare_(attrsAfter,attrsBefore)
            p.addComment(u"")
            p.clear()

        #==================================================================
        # test rotate
        # without modification of attributes
        #==================================================================
        for file in l:
            p=PhotoCmd(file)
            p.addComment(u"kélàçù")
            p.add(u"kàkà")
            attrsBefore=la(p)

            p.rebuildExifTB()
            attrsAfter=la(p)

            assert _compare_(attrsAfter,attrsBefore)
            p.addComment(u"")
            p.clear()

        #==================================================================
        # test same renaming, destroyInfo, copyInfoTo
        # without modification of attributes
        #==================================================================
        for f1 in l:
            p1=PhotoCmd(f1)
            p1.addComment(u"kélàçù")
            p1.add(u"kàkà")
            
            f2= u"../unittests/photos_tmp/jojo.jpg"
            print f1,"--->",f2
            shutil.copy(f1,f2)
            p2=PhotoCmd(f2,needAutoRename=True)
            assert _compare_(la(p1),la(p2))     # ensure same attrs
            assert "(1)" in p2.file             # ensure indice

            assert len(p2.tags)==1
            assert len(p2.comment)>0
            p2.destroyInfo()
            assert len(p2.tags)==0
            assert len(p2.comment)==0

            p2=p1.copyInfoTo(p2.file)
            assert _compare_(la(p1),la(p2))

    finally:
        shutil.rmtree(folder)   # delete tempfolder
