# -*- coding: utf-8 -*-
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


import os,time,shutil


class Plugin(JPlugin):
    """ Instant share on the web """

    __author__ = "manatlan"
    __version__ = "1.1"
    #
    #def menuEntries(self,l):
    #    return [(3200,_("Web Share"),False,self.share,None)]


    @JPlugin.Entry.PhotosProcess( _("Web Share"), order=3200,alter=False )
    def share(self,list):
        from instantweb import Winweb

        win = Winweb()
        win.setNodes(list)
        win.cb_originals.set_active( (self.conf["accessOriginals"] or 0)==1 )
        win.cb_albums.set_active( (self.conf["modeAlbum"] or 0)==1 )

        win.loop()
        self.conf["modeAlbum"] = win.cb_albums.get_active() and 1 or 0
        self.conf["accessOriginals"] = win.cb_originals.get_active() and 1 or 0
        return False
