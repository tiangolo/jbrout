#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    this will upload packages to jbrout.free.fr
"""
import sys
import ftplib

if __name__ == "__main__":
    print "NOT FINISHED"
    sys.exit()

    megarun("""
        mv -f jbrout_*.deb binary
        dpkg-scanpackages binary /dev/null | gzip -9c > binary/Packages.gz
        """ % locals() )


    """ upload all packages to the jbrout ftp"""
    version = open(DEST+D_SOURCE+"/version.txt").read().strip()

    s = ftplib.FTP('ftpperso.free.fr','jbrout',open("~/.jbroutpassword").read())

    file = DEST+"jbrout-"+version+".sources.tar.gz"
    if os.path.isfile(file):
        print "upload",os.path.basename(file)
        s.cwd("download/sources")
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

    file = find("jbrout_.*"+version+".*\.deb",DEST+"binary")
    if file:
        s.cwd("download/debian/binary")

        print "upload",os.path.basename(file)
        f = open(file,'rb')
        s.storbinary('STOR '+os.path.basename(file), f)

        file = DEST+"binary/Packages.gz"
        print "upload",os.path.basename(file)
        f = open(file,'rb')
        s.storbinary('STOR '+os.path.basename(file), f)

        s.cwd("../../..")


    file=find("jbrout-.*"+version+".*\.rpm",DEST)
    if file:
        print "upload",os.path.basename(file)
        s.cwd("download/rpm")
        f = open(file,'rb')
        s.storbinary('STOR '+os.path.basename(file), f)
        s.cwd("../..")

    s.quit()
