# -*- coding: cp1252 -*-

##
##    Copyright (C) 2009 manatlan manatlan[at]gmail(dot)com
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

class Plugin(JPlugin):
    """Plugin nouveau format """

    __author__ = "manatlan"
    __version__ = "0.1"

    @JPlugin.Entry.AlbumProcess( _("Do nothing on album"),order=999999 )
    @JPlugin.Entry.AlbumProcessDontAlter    # this method is available in view only mode, because it doesn't alter db/photos
    def justDoThis(self,folderNode):
        print "this is the album", folderNode
        return False # dont redraw anything (nothing has changed)

    @JPlugin.Entry.PhotosProcess( _("Do nothing on photos"), order=999999 )
    @JPlugin.Entry.PhotosProcessDontAlter
    def justDoThat(self,photoNodes): # this method is available in view only mode, because it doesn't alter db/photos
        print "this is the list of photos", photoNodes
        return False # dont redraw anything (nothing has changed)
