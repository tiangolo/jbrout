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
    __version__ = "1.1"

    #def menuEntries(self,l):
        
        # I had commented theses new operations
        # I think we will let them available when we will have a preference dialog
        # which will let the user choose what entries he wants ... no ?
        # because it "bloats" the contectual menu now ... no ?
        
        #return [
        #        (1000,_("Auto Rotate"),True,self.auto,None),
        #        (1001,_("Rotate Right 90"),True,self.rotate90,"gfx/rotate-right.png"),
        #        #(1002,_("Rotate Right 180"),True,self.rotate180,None),
        #        (1003,_("Rotate Left 90"),True,self.rotate270,"gfx/rotate-left.png"),
        #        #(1004,_("Flip Horizontal"),True,self.flipHorizontal,None),
        #        #(1005,_("Flip Vertical"),True,self.flipVertical,None),
        #        #(1006,_("Transpose"),True,self.transpose,None),
        #        #(1007,_("Transverse"),True,self.transverse,None),
        #        (1008,_("Rebuild thumbnail"),True,self.rebuildThumb,None)
        #       ]

    @JPlugin.Entry.PhotosProcess( _("Auto Rotate"), order=1000 )
    def auto(self,l):
        return self.__transform(l,"auto")
    
    @JPlugin.Entry.PhotosProcess( _("Rotate Right 90"), order=1001, icon="gfx/rotate-right.png",key="r" )
    def rotate90(self,l):
        return self.__transform(l,"rotate90")

    @JPlugin.Entry.PhotosProcess( _("Rotate Right 180"), order=1002 )
    def rotate180(self,l):
        return self.__transform(l,"rotate180")
    
    @JPlugin.Entry.PhotosProcess( _("Rotate Left 90"), order=1003, icon="gfx/rotate-left.png", key="l" )
    def rotate270(self,l):
        return self.__transform(l,"rotate270")
    
    @JPlugin.Entry.PhotosProcess( _("Flip Horizontal"), order=1004 )
    def flipHorizontal(self,l):
        return self.__transform(l,"flipHorizontal")

    @JPlugin.Entry.PhotosProcess( _("Flip Vertical"), order=1005 )
    def flipVertical(self,l):
        return self.__transform(l,"flipVertical")

    @JPlugin.Entry.PhotosProcess( _("Transpose"), order=1006 )
    def transpose(self,l):
        return self.__transform(l,"transpose")
        
    @JPlugin.Entry.PhotosProcess( _("Transverse"), order=1007 )
    def transverse(self,l):
        return self.__transform(l,"transverse")

    def __transform(self,list,sens):
        try:
            for i in list:
                self.showProgress( list.index(i), len(list) , _("Transforming Image") )
                i.transform(sens)
        finally:
            self.showProgress()
        return True

    @JPlugin.Entry.PhotosProcess( _("Rebuild thumbnail"), order=1008 )
    def rebuildThumb(self,list):
        try:
            for i in list:
                self.showProgress( list.index(i), len(list)  , _("Rebuild thumbnail") )
                i.rebuildThumbnail()
        finally:
            self.showProgress()
        return True
