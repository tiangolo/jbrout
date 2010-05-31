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




###############################################################################
class Exiv2Metadata(object):
###############################################################################
    """ pyexiv2 > 0.2 """
    def __init__(self,md):
        self._md=md
    #============================================== V 0.1 api
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

    def tagDetails(self,k):               # see viewexif plugin
        md=self._md[k]
        if hasattr(md,"label"):
            lbl=getattr(md,"label")
        elif hasattr(md,"title"):
            lbl=getattr(md,"title")
        return [lbl,md.description,]

    def interpretedExifValue(self,k):   # see viewexif plugin
        return self._md[k].human_value
    #==============================================

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- new apis
    def xmpKeys(self):
        return self._md.xmp_keys


    def getTags(self):
        """ return a list of merged tags (xmp+iptc) (list of str)"""
        try:
            li=[str(i.strip("\x00")) for i in self._md["Iptc.Application2.Keywords"].values]    #digikam patch
            # assume UTF8
        except KeyError:
            li=[]
        try:
            lx=[i.encode("utf_8") for i in self._md["Xmp.dc.subject"].value]
        except KeyError:
            lx=[]
        ll=list(set(li+lx))
        ll.sort()
        return ll


    def setTags(self,l):
        for i in l:
            assert type(i)==unicode

        self._md["Iptc.Application2.Keywords"] = [i.encode("utf_8") for i in l]
        self._md["Xmp.dc.subject"]=l


    def clearTags(self):
        try:
            del self._md["Iptc.Application2.Keywords"]
        except:
            pass
        try:
            del self._md["Xmp.dc.subject"]
        except:
            pass
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-












if not hasattr(pyexiv2,"Image"):    # Only here to make the following code
    class Fake(object):             # compliant with old objects from 0.1
        def __init__(self,f):       # when using 0.2 version
            pass                    # else it can't compile ;-)
    pyexiv2.Image=Fake

###############################################################################
class Exiv1Metadata(pyexiv2.Image):
###############################################################################
    """ pyexiv2 < 0.2 """
    def __init__(self,f):
        pyexiv2.Image.__init__(self,f)

    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- new apis
    def xmpKeys(self):
        return []

    def getTags(self):
        try:
            l=self["Iptc.Application2.Keywords"]
            if type(l) == tuple:
                ll = [i.strip("\x00") for i in l] # strip("\x00") = digikam patch
                ll.sort()
            else:
                ll = [l.strip("\x00"),]
        except KeyError:
            ll = []
        return ll   # many case = list of utf8 strings

    def setTags(self,l):
        for i in l:
            assert type(i)==unicode

        self["Iptc.Application2.Keywords"] = [i.encode("utf_8") for i in l]

    def clearTags(self):
        try:
            prec = self["Iptc.Application2.Keywords"] #TODO: to bypass a bug in pyexiv2
            self["Iptc.Application2.Keywords"] = []
        except:
            pass
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-



def Image(f):
    if hasattr(pyexiv2,"ImageMetadata"):
        # pyexiv2 >= 0.2
        print "***WARNING*** : YOU ARE USING pyexiv2>0.2 (jbrout doesn't support very well this new version ! not fully tested ! some things are not implemented !!!)"
        return Exiv2Metadata(pyexiv2.ImageMetadata(f))
    else:
        # pyexiv2 < 0.2
        return Exiv1Metadata(f)

if __name__ == "__main__":
    t=Image("/home/manatlan/Documents/python/tests_libs_python/TestJPG/p20030830_130202 (copie).jpg")
    #~ t=Image("/home/manatlan/Documents/python/tests_libs_python/TestJPG/p20030830_130202.jpg")
    #~ t=Image("/home/manatlan/Desktop/fotaux/autorot/p20020115_173654(1).jpg")
    t.readMetadata()

    #----
    aa=t._md["Xmp.dc.subject"].raw_value[0]
    import chardet; print chardet.detect(aa) # in fact, it's latin1 encoded as utf8
    print aa.decode("utf_8").encode("latin1")
    #----

    L=t.getTags()
    print "===>",L
