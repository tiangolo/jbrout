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

from __main__ import JPlugin,runWith
import os
import sys

class Plugin(JPlugin):
    """ Plugin to open the folder in (nautilus/linux) or (explorer/windows) """

    __author__ = "manatlan"
    __version__ = "1.0"

    #def menuEntries(self,l):
    #    if len(l)==1:
    #        return [(1010,_("Open in explorer"),False,self.open,None)]
    #    else:
    #        return []
    #    
    #def albumEntries(self,n):
    #    return [(90,_("Open in explorer"),False,self.openFromAlbum)]

    @JPlugin.Entry.AlbumProcess( _("Open in explorer"),order=90,alter=False )
    def openFromAlbum(self,node):
        runWith(["xdg-open","nautilus","rox","konqueror","explorer.exe"],unicode(node.file))    # path of folder
        return False    # no visual modif
        
    @JPlugin.Entry.PhotosProcess( _("Open in explorer"),order=90,alter=False )
    def open(self,list):
        path = os.path.dirname(list[0].file)
        #~ path = path.encode(sys.getfilesystemencoding())
        runWith(["xdg-open","nautilus","rox","konqueror","explorer.exe"],path)

        return False    # no visual modif
