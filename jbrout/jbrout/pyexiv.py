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
import re
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
        self._md["Iptc.Envelope.CharacterSet"] = ['\x1b%G',] # set Charset as UTF8
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
            return [None,l[0]]
        else:
            return []

    def setThumbnailData(self,o):
        if pyexiv2.version_info > (0,2,2):
            self._md.exif_thumbnail.data = o
        else:
            print "***WARNING*** : not implemented : setThumbnailData (you need pyexiv2>0.2.2)"
    def deleteThumbnail(self):
        if pyexiv2.version_info > (0,2,2):
            self._md.exif_thumbnail.erase()
        else:
            print "***WARNING*** : not implemented : deleteThumbnail (you need pyexiv2>0.2.2)"

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
        # Authoritative reference
        # http://www.iptc.org/std/Iptc4xmpCore/1.0/documentation/Iptc4xmpCore_1.0-doc-CpanelsUserGuide_13.pdf
        # however
        # http://metadataworkinggroup.com/pdf/mwg_guidance.pdf says on page 35 that
        ## IPTC Keywords is mapped to XMP (dc:subject)
        # It seems that the latter is true ... at least according to
        # http://trac.yorba.org/wiki/PhotoTags

        li=[]
        if "Iptc.Application2.Keywords" in self._md.iptc_keys:
            li=[str(i.strip("\x00")) for i in self._md["Iptc.Application2.Keywords"].value]    #digikam patch
            # assume UTF8
        lk = []
        if "Xmp.iptc.Keywords" in self._md.xmp_keys:
            for xel in self._md["Xmp.iptc.Keywords"].value:
                lk.extend([x.strip() for x in xel.encode("utf-8").split(",")])
            # assume UTF8
        lx = []
        if "Xmp.dc.subject" in self._md.xmp_keys:
            for xel in self._md["Xmp.dc.subject"].value:
                lx.extend([x.strip() for x in xel.encode("utf-8").split(",")])

        ll=list(set(li+lx+lk))
        ll.sort()
        return ll


    def setTags(self,l):
        for i in l:
            assert type(i)==unicode

        if l:
            self._md["Iptc.Application2.Keywords"] = [i.encode("utf_8") for i in l]
            self._md["Xmp.dc.subject"] = [",".join(l)]
        else:
            del self._md["Iptc.Application2.Keywords"]
            del self._md["Xmp.dc.subject"]
        if 'Xmp.iptc.Keywords' in self._md.xmp_keys:
            del self._md['Xmp.iptc.Keywords']


    def clearTags(self):
        if "Iptc.Application2.Keywords" in self._md.iptc_keys:
            del self._md["Iptc.Application2.Keywords"]
        if "Xmp.dc.subject" in self._md.xmp_keys:
            del self._md["Xmp.dc.subject"]
        if 'Xmp.iptc.Keywords' in self._md.xmp_keys:
            del self._md['Xmp.iptc.Keywords']


    def copyToFile(self, destFilename, exif=True, iptc=True, xmp=True, comment=True):
        dest = pyexiv2.ImageMetadata(destFilename)
        dest.read()
        self._md.copy(dest, exif, iptc, xmp, comment)
        dest.write()

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


    def writeMetadata(self):
        self["Iptc.Envelope.CharacterSet"] = ['\x1b%G',]   # set Charset as UTF8
        return pyexiv2.Image.writeMetadata(self)


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


    def copyToFile(self, destFilename, exif=True, iptc=True, xmp=True, comment=True):
        dest = pyexiv2.Image(destFilename)
        dest.readMetadata()
        # delete all tags :
        for i in (dest.exifKeys() + dest.iptcKeys()):
            try:
                del dest[i]
            except KeyError: # 'tag not set'
                # the tag seems not to be here, so
                # we don't need to clear it, no ?
                pass

        dest.deleteThumbnail()   # seems not needed !
        dest.clearComment()

        # copy all exif/iptc/xmp/comment info as directed
        l = []
        if exif: l= l+self.exifKeys()
        if exif: l= l+self.iptcKeys()
        for i in l:
            if i not in ["Exif.Photo.UserComment",]: # key "Exif.Photo.UserComment" bugs always ?!
                if not i.startswith("Exif.Thumbnail"):  # don't need exif.thumb things because it's copied after
                    if len(re.findall('0x0',i))==0: # Work around to fix error in pyev2 with most unknown makernoite tags
                        # TODO: fix nasty bodge to get around pyexiv2 issues with multi part exif fields
                        # known not to copy the following:
                        #   - unknown maker not fields
                        #   - lens data for canon
                        try:
                            dest[i] =self[i]
                        except:
                            print "Problems copying %s keyword" %i

        # copy comment
        if comment:
            dest.setComment( self.getComment() )

        # copy exif thumbnail
        if exif:
            dest.setThumbnailData(self.getThumbnailData()[1])
        dest.writeMetadata()
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-



def Image(f):
    if hasattr(pyexiv2,"ImageMetadata"):
        # pyexiv2 >= 0.2
        return Exiv2Metadata(pyexiv2.ImageMetadata(f))
    else:
        # pyexiv2 < 0.2
        return Exiv1Metadata(f)

def Check():
    if hasattr(pyexiv2,"ImageMetadata"):
        # pyexiv2 >= 0.2
        print "***WARNING*** : YOU ARE USING pyexiv2>0.2 (jbrout doesn't support very well this new version ! not fully tested ! some things are not implemented !!!)"

if __name__ == "__main__":
    t=Image("/home/manatlan/Documents/python/tests_libs_python/TestJPG/p20030830_130202 (copie).jpg")
    #~ t=Image("/home/manatlan/Documents/python/tests_libs_python/TestJPG/p20030830_130202.jpg")
    #~ t=Image("/home/manatlan/Desktop/fotaux/autorot/p20020115_173654(1).jpg")
    t.readMetadata()

    ##----
    #aa=t._image["Xmp.dc.subject"].raw_value[0]
    #import chardet; print chardet.detect(aa) # in fact, it's latin1 encoded as utf8
    #print aa.decode("utf_8").encode("latin1")
    ##----

    #t.setThumbnailData("")

    L=t.getTags()
    print "===>",L

    #t=Image("/home/manatlan/Desktop/fotaux/autorot/jpg/p20090319_061423.jpg")
    #t.readMetadata()
    #t.deleteThumbnail()
    #t.writeMetadata()
