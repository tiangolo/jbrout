#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    this will upload packages to jbrout.free.fr
"""
import sys,os,shutil
import ftplib
from libs import run, megarun
from glob import glob

if __name__ == "__main__":
    #==========================================================================
    # CHDIR at the root of svn (to able to read full changelog, and make
    # relaative path for py2deb)
    #==========================================================================
    os.chdir(os.path.join(os.path.dirname(__file__),".."))

    if os.path.isdir("packages"):
        try:
            deb=glob("packages/*.deb")[0]
        except:
            deb=None
        try:
            src=glob("packages/*.tar.gz")[0]
        except:
            src=None
        try:
            rpm=glob("packages/*.rpm")[0]
        except:
            rpm=None

        if deb:
            # make the 'binary' repository
            if not os.path.isdir("packages/binary"):
                os.makedirs("packages/binary")
            shutil.copy2(deb,"packages/binary")
            megarun("""
                cd packages && dpkg-scanpackages binary /dev/null | gzip -9c > binary/Packages.gz
                """  )
            debs=glob("packages/binary/*")
        else:
            debs=[]

        print "-"*75
        print "DEBIAN : ",debs
        print "RPM : ",rpm
        print "SOURCE : ",src
        print "-"*75
    else:
        print "packages are not here ?!?"

    home=os.environ['HOME']
 
    s = ftplib.FTP('ftpperso.free.fr','jbrout',open(os.path.join(home,".jbroutpassword")).read())
    
    if src:
        file = src
        print "upload",os.path.basename(file)
        s.cwd("download/sources")
        f = open(file,'rb')
        s.storbinary('STOR '+os.path.basename(file), f)
        s.cwd("../..")


    if rpm:
        file=rpm
        print "upload",os.path.basename(file)
        s.cwd("download/rpm")
        f = open(file,'rb')
        s.storbinary('STOR '+os.path.basename(file), f)
        s.cwd("../..")

    #~ file = DEST+"jbrout-"+version+".win32.zip"
    #~ if os.path.isfile(file):
        #~ print "upload",os.path.basename(file)
        #~ s.cwd("download/win32")
        #~ f = open(file,'rb')
        #~ s.storbinary('STOR '+os.path.basename(file), f)
        #~ s.cwd("../..")

    if debs:
        for file in debs:
            s.cwd("download/debian/binary")
    
            print "upload",os.path.basename(file)
            f = open(file,'rb')
            s.storbinary('STOR '+os.path.basename(file), f)
    
            s.cwd("../../..")

    s.quit()
