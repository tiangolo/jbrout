#!/usr/bin/env python
# -*- coding: utf-8 -*-

__builtins__.__dict__["_"] = lambda x:x

import os
import sys
import shutil
from datetime import datetime
from glob import glob
############################################################### to be executed here
if __file__ != "runtests.py":
    # execution from here
    PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "jbrout")
    sys.path.append(PATH)
    FOLDER = unicode(os.path.join(os.path.dirname(os.path.abspath(__file__)), "photos"))
    os.chdir(PATH)
else:
    # execution from main jbrout folder
    FOLDER = unicode(os.path.abspath("../unittests/photos"))
###############################################################
from jbrout.db import *

if __name__ == "__main__":

    folder = FOLDER + "_tmp"
    if os.path.isdir(folder):
        shutil.rmtree(folder)

    shutil.copytree(FOLDER, folder)  # create a temp folder to work in
    try:

        dbfile = os.path.join(folder, "db.xml")
        db = DBPhotos(dbfile)
        l = [i for i in glob(os.path.join(folder, "*.*")) if i.lower().endswith(".jpg")]

        gen = db.add(folder)
        tot = gen.next()
        assert tot == len(l)
        for i in gen:
            pass

        #===========================================================
        # tests FolderNode
        #===========================================================
        fn = i  # last is the foldernode
        assert fn.name == os.path.basename(folder)
        assert fn.file == folder

        assert fn.setComment(u"héllà")
        assert os.path.isfile(os.path.join(folder, FolderNode.commentFile))
        assert fn.comment == u"héllà"

        assert fn.setComment(u"")
        assert not os.path.isfile(os.path.join(folder, FolderNode.commentFile))

        assert len(fn.getPhotos()) == len(l)
        assert len(fn.getParent().getPhotos()) == 0  # there shouldn't be photos in exec path
        assert len(fn.getParent().getAllPhotos()) == len(l)
        assert len(fn._select("//photo")) == len(l)
        assert len(fn.getFolders()) == 0  # there shouldn't be folder in photo temp folder

        pn = fn.getPhotos()[0]

        # create a "tmp1" folder
        nfn1 = fn.createNewFolder(u"tmp1")
        assert nfn1.name == u"tmp1"
        assert nfn1.file == os.path.join(folder, u"tmp1")
        assert os.path.isdir(os.path.join(folder, u"tmp1"))

        assert len(fn.getFolders()) == 1

        nfn2 = fn.createNewFolder(u"tmp1")
        assert nfn2 == False  # because tmp1 should already exists

        nfn2 = fn.createNewFolder(pn.file)
        assert nfn2 == False  # because this is a photo, and the file already exists

        # create a "tmp2" folder
        nfn2 = fn.createNewFolder(u"tmp2")
        assert nfn2.name == u"tmp2"

        assert len(fn.getFolders()) == 2, [i.name for i in fn.getFolders()]

        # move a photo to "tmp1" folder
        assert pn.moveToFolder(nfn1) == True
        assert len(nfn1.getPhotos()) == 1
        assert len(fn.getPhotos()) == len(l) - 1
        assert pn.folder == os.path.join(folder, u"tmp1")

        # move folder "tmp1" to "tmp2" folder
        nfn1 = nfn1.moveToFolder(nfn2)
        assert nfn1
        assert pn.folder == nfn1.file
        assert nfn1.name == u"tmp1"

        assert len(nfn2.getFolders()) == 1  # should be nfn1
        assert len(nfn2.getPhotos()) == 0
        assert len(nfn2.getAllPhotos()) == 1


        #===========================================================
        # tests PhotoNode
        #===========================================================
        # TODO: ... to be continued ...
        pn.setComment(u"éàé")
        assert pn.comment == u"éàé"


        # ~ fn.rename(u"jo")
        # ~ print fn.name
        # ~ print fn.file
        # ~ print db.toXml()


    finally:
        shutil.rmtree(folder)  # delete tempfolder

