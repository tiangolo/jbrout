# -*- coding: UTF-8 -*-
##
##    Copyright (C) 2007 Rob Wallace rob[at]wallace(dot)gen(dot)nz
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
    """ Plugin to display the full exif/iptc info contained in one ore more photos """
    __author__ = "Rob Wallace"
    __version__ = "0.0.3"

    @JPlugin.Entry.PhotosProcess( _("Display Meta Data"),order=5000,alter=False )
    def viewExif(self,list):
        from viewExif import WinViewExif

        win = WinViewExif(list)

        win.loop()

        return False
