# -*- coding: UTF-8 -*-
##
##    Copyright (C) 2009 Rob Wallace rob[at]wallace(dot)gen(dot)nz
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
from jbrout.tools import XMPUpdater

class Plugin(JPlugin):
    """Plugin to perform mass tagging changes"""

    __author__ = "Thierry Benita"
    __version__ = "0.1"

    def menuEntries(self,l):
        return [(8100,_("Import Tags"),True,self.importTags,None)]

    def albumEntries(self,l):
        return [(300,_("Import Tags"),True,self.importAlbumTags)]

    def importTags(self,imgList):
        """Import tags used in the given image list (IPTC and XMP) and merge them together"""
        self.showProgress( 0, 1 , _("Importing Tags") )
        XMPUpdater(imgList).SyncXmpIptc()
        self.showProgress()
        return True

    def importAlbumTags(self,imgList):
        """Import tags used in the given image list (IPTC and XMP) and merge them together"""
        self.showProgress( 0, 1 , _("Importing Tags") )
        XMPUpdater([imgList.file]).SyncXmpIptc()
        self.showProgress()
        return True
