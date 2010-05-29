#!/usr/bin/env python
# -*- coding: utf-8 -*-

##
##    Copyright (C) 2010 manatlan manatlan[at]gmail(dot)com
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published
## by the Free Software Foundation; version 2 only.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##load
## URL : http://jbrout.googlecode.com

"""
pyexiv2 wrapper
===============

map old methods/objects from pyexiv2(<2), to be able to work with versions 1 & 2

"""
import sys

try:
    import pyexiv2
except:
    print "You should install pyexiv2 (>=0.1.2)"
    sys.exit(-1)

class ExivMetadata(object):
    def __init__(self,md):
        self._md=md
    def readMetadata(self):
        return self._md.read()
    def writeMetadata(self):
        return self._md.write()
    def __getitem__(self,k):
        v=self._md[k]
        if hasattr(v,"value"):
            return v.value
        elif hasattr(v,"values"):
            return tuple(v.values)
        else:
            raise
    def __setitem__(self,k,v):
        self._md[k]=v
    def __delitem__(self,k):
        del self._md[k]
    def getComment(self):
        return self._md.comment
    def setComment(self,v):
        self._md.comment=v
    def clearComment(self):
        self._md.comment=None

    def getThumbnailData(self):
        l=[i.data for i in self._md.previews]
        if l:
            return [None,l[-1]] # to be able to get the item 1
        else:
            return []

    def setThumbnailData(self,o):
        #TODO: finnish here
        print "***WARNING*** : not implemented : setThumbnailData"
    def deleteThumbnail(self):
        self._md.previews=[]


    def exifKeys(self):
        return self._md.exif_keys
    def iptcKeys(self):
        return self._md.iptc_keys

    def tagDetails(self,v):               # see viewexif plugin
        #TODO: finnish here
        print "***WARNING*** : not implemented : tagDetails"
        return None
    def interpretedExifValue(self,v):   # see viewexif plugin
        #TODO: finnish here
        print "***WARNING*** : not implemented : interpretedExifValue"
        return None

def Image(f):
    if hasattr(pyexiv2,"ImageMetadata"):
        # pyexiv2 >= 0.2
        print "***WARNING*** : YOU ARE USING pyexiv2>0.2 (jbrout doesn't support well this newer version ! not fully tested ! some things are not implemented !!!)"
        return ExivMetadata(pyexiv2.ImageMetadata(f))
    else:
        # pyexiv2 < 0.2
        return pyexiv2.Image(f)

if __name__ == "__main__":
    pass
