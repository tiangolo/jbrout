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

class Plugin(JPlugin):
    """Plugin to perform mass tagging changes"""

    __author__ = "Rob Wallace"
    __version__ = "0.1"

    #def menuEntries(self,l):
    #    return [(8000,_("Unify Tags"),True,self.unifyTags,None),
    #            (8001,_("Bulk Tag"),True,self.bulkTag,None)]


    def readTags(self,imgList):
        """Returns a list of the tags used in the given image list"""
        tags=[]
        for i in imgList:
            self.showProgress(imgList.index(i), len(imgList), _("Reading Tags"))
            for tag in i.tags:
                if tag not in tags:
                    tags.append(tag)
        self.showProgress()
        return tags

    def writeTags(self,imgList, tags):
        """Writes a list of tags to the given set of images"""
        for i in imgList:
            self.showProgress(imgList.index(i), len(imgList), _("Tagging"))
            i.addTags(tags)
        self.showProgress()

    @JPlugin.Entry.PhotosProcess( _("Unify Tags"), order=8000 )
    def unifyTags(self,list):
        """Unifys tags between the selected list of photos (makes the Tags all the same)"""
        tags = self.readTags(list)
        if len(tags) != 0:
            msg = "Are you sure you whish to add the following tags to the selected images:\n" + ", ".join(tags)
            if self.InputQuestion(msg,title=_("Unify Tags")):
                self.writeTags(list, tags)
                ret = True
            else:
                ret = False
        else:
            ret = False
        return ret

    @JPlugin.Entry.PhotosProcess( _("Bulk Tag"), order=8001 )
    def bulkTag(self,list):
        """Tool for tagging a number of images with a set of tags"""
        from bulkTag import WinBulkTag
        tags = self.readTags(list)
        winBulkTag = WinBulkTag(tags)
        ok, tags = winBulkTag.loop()
        if ok and len(tags) > 0:
            self.writeTags(list, tags)
            return True
        else:
            return False

