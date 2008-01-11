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



class Plugin(JPlugin):
    """Plugin pour rotationner les photos ou rebuilder leurs thumbnails"""

    __author__ = "manatlan"
    __version__ = "1.0"

    def menuEntries(self,l):
        return [
                (1000,_("Rotate Right"),True,self.rotateRight,"gfx/rotate-right.png"),
                (1001,_("Rotate Left"),True,self.rotateLeft,"gfx/rotate-left.png"),
                (1002,_("Rebuild thumbnail"),True,self.rebuildThumb,None)
               ]

    def rotateRight(self,l):
        return self.__rotate(l,"R")

    def rotateLeft(self,l):
        return self.__rotate(l,"L")

    def __rotate(self,list,sens):
        try:
            for i in list:
                self.showProgress( list.index(i), len(list) , _("Rotating") )
                i.rotate(sens)
        finally:
            self.showProgress()
        return True

    def rebuildThumb(self,list):
        try:
            for i in list:
                self.showProgress( list.index(i), len(list)  , _("Rebuilding thumbs") )
                i.rebuildThumbnail()
        finally:
            self.showProgress()
        return True
