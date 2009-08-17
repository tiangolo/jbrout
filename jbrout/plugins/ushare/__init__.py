# -*- coding: cp1252 -*-

##
##    Copyright (C) 2005 manatlan manatlan[at]gmail(dot)com
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 2 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##

from __main__ import JPlugin

import os
import tempfile
import shutil
from subprocess import Popen,PIPE

def run(cmd):
    p = Popen(cmd, shell=True,stdout=PIPE,stderr=PIPE)
    return "".join(p.stdout.readlines() ).strip()

def isUshareInstalled():
    return run("which ushare").startswith("/")


class Plugin(JPlugin):
    """Share media accross upnp/dlna devices (linux only, need ushare)"""

    __author__ = "manatlan"
    __version__ = "0.1"

    @JPlugin.Entry.PhotosProcess( _("media share"), order=8900 )
    def exposePhotos(self,l):
        if isUshareInstalled():
            p=tempfile.mkdtemp()
            try:
                for photo in l:
                    os.symlink(photo.file,os.path.join(p,os.path.basename(photo.file)))

                cmd=Popen(["ushare","-f","ushare.conf","-c",p])
                self.MessageBox(_("Sharing %d photo(s)") % len(l),_("Media Share"))
                print "Terminate ushare"
                cmd.terminate()

            finally:
                shutil.rmtree(p)
        else:
            raise Exception("ushare is not installed")

        return False

    @JPlugin.Entry.AlbumProcess( _("media share"), order=8900 )
    def exposeAlbum(self,a):
        if isUshareInstalled():
            cmd=Popen(["ushare","-f","ushare.conf","-c",a.file])
            self.MessageBox(_("Sharing album '%s'") % a.name,_("Media Share"))
            print "Terminate ushare"
            cmd.terminate()
        else:
            raise Exception("ushare is not installed")

        return False
