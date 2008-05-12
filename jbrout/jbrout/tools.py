#!/usr/bin/python
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

"""
MAJOR CHANGES :
  - unlike old tools, filedate is modified at each operation which modify picture
    (so tools for backup, like rsync should work)
  - always an exifdate, when no exif date : create exif date with filedate m_time
    (so destroyinfo leave exifdate in place)
  - use only jpegtran/exiftran tools (for LOSSLESS rotation)
  - api are the same than old one (but should change in the future)
  - thumbnail are created in python (pil+pyexiv2)
  - autorot only available on LINUX (was bugued in windows in old tools)
"""
import os,sys
try:
    import pyexiv2
except:
    print "You should install pyexiv2 (>=0.1.2)"
    sys.exit(-1)

import time
from datetime import datetime,timedelta
from PIL import Image
import StringIO

import string,re
from subprocess import Popen,PIPE


def ed2cd(f): #yyyy/mm/dd hh:ii:ss -> yyyymmddhhiiss
   if f:
      return f[:4]+f[5:7]+f[8:10]+f[11:13]+f[14:16]+f[17:19]
   else:
      return f


# ##############################################################################################
class _Command:
# ##############################################################################################
   """ low-level access (wrapper) to external tools used in jbrout
   """
   isWin=(sys.platform[:3] == "win")
   __path =os.path.join(os.getcwdu(),u"data/tools")

   err=""
   if isWin:
      # set windows path
      _exiftran = None
      _jpegtran = os.path.join(__path,"jpegtran.exe")

      if not os.path.isfile(_jpegtran):
          err+="jpegtran is not present in 'tools'\n"
   else:
      # set "non windows" path (needs 'which')
      _exiftran = u"".join(os.popen("which exiftran").readlines()).strip()
      _jpegtran = None

      if not os.path.isfile(_exiftran):
          err+="exiftran is not present, please install 'exiftran'(fbida)\n"

   if err:
      raise CommandException(err)



   @staticmethod
   def _run(cmds):
        #~ print cmds
        cmdline = str( [" ".join(cmds)] ) # to output easily (with strange chars)
        try:
            cmds = [i.encode(sys.getfilesystemencoding()) for i in cmds]
        except:
            raise CommandException( cmdline +"\n encoding trouble")

        p = Popen(cmds, shell=False,stdout=PIPE,stderr=PIPE)
        time.sleep(0.01)    # to avoid "IOError: [Errno 4] Interrupted system call"
        out = string.join(p.stdout.readlines() ).strip()
        outerr = string.join(p.stderr.readlines() ).strip()

        if "exiftran" in cmdline:
           if "processing" in outerr:
               # exiftran output process in stderr ;-(
               outerr=""

        if outerr:
           raise CommandException( cmdline +"\n OUTPUT ERROR:"+outerr)
        else:
           try:
              out = out.decode("utf_8") # recupere les infos en UTF_8
           except:
              try:
                  out = out.decode("latin_1")  # recupere les anciens infos (en latin_1)
              except UnicodeDecodeError:
                  try:
                      out = out.decode(sys.getfilesystemencoding())
                  except UnicodeDecodeError:
                      raise CommandException( cmdline +"\n decoding trouble")

           return out #unicode





class NotImplemented(Exception): pass

class PhotoCmd(object):
    
    file = property(lambda self: self.__file)
    exifdate = property(lambda self:self.__exifdate)
    filedate = property(lambda self:self.__filedate)
    readonly = property(lambda self:self.__readonly)
    isflash = property(lambda self:self.__isflash)
    resolution = property(lambda self:self.__resolution)
    comment = property(lambda self:self.__comment)
    tags = property(lambda self:self.__tags)
    isreal = property(lambda self:self.__isreal)

    # static
    format="p%Y%m%d_%H%M%S"
    
    def debug(self,m):
        print m
        #pass
    
    def __init__(self,file,needAutoRename=False,needAutoRotation=False):
        assert type(file)==unicode
        assert os.path.isfile(file)


        self.__readonly = not os.access( file, os.W_OK)

        # pre-read
        info = pyexiv2.Image(file.encode("utf_8"))
        info.readMetadata()

        if self.readonly:
            self.debug( "*WARNING* File %s is READONLY" % file )
        else:
            #-----------------------------------------------------------
            # try to correct exif date if wrong
            #-----------------------------------------------------------
            # if no exifdate ---> put the filedate in exifdate
            # SO exifdate=filedate FOR ALL
            try:
                info["Exif.Image.DateTime"].strftime("%Y%m%d%H%M%S")
                isDateExifOk=True
            except KeyError:        # tag exif datetime not present
                isDateExifOk=False
            except AttributeError:  # content of tag exif datetime is not a datetime
                isDateExifOk=False
    
            if not isDateExifOk:
                self.debug( "*WARNING* File %s had wrong exif date -> corrected" % file )
                
                fd=datetime.fromtimestamp(os.stat(file).st_mtime)
                info["Exif.Image.Make"]="jBrout" # mark exif made by jbrout
                info["Exif.Image.DateTime"]=fd
                info["Exif.Photo.DateTimeOriginal"]=fd
                info["Exif.Photo.DateTimeDigitized"]=fd
                info.writeMetadata()        

            exifdate = info["Exif.Image.DateTime"]

            #-----------------------------------------------------------
            # try to autorot, if wanted
            #-----------------------------------------------------------
            if needAutoRotation :
                try:
                    orientation=int(info["Exif.Image.Orientation"])
                    #http://sylvana.net/jpegcrop/exif_orientation.html
                    #~ 1) transform="";;
                    #~ 2) transform="-flip horizontal";;
                    #~ 3) transform="-rotate 180";;
                    #~ 4) transform="-flip vertical";;
                    #~ 5) transform="-transpose";;
                    #~ 6) transform="-rotate 90";;      # R
                    #~ 7) transform="-transverse";;
                    #~ 8) transform="-rotate 270";;     # L
                except KeyError:
                    orientation=0

                if orientation!=1:
                    if _Command.isWin:
                        # do nothing
                        # -> because no gpl tools which rotate well (img+thumb) automatically according exif
                        #    if you provide me one, i'll integrate here
                        self.debug( "*WARNING* File %s needs autorotate -> not done (windows)" % file )
                        pass
                    else:
                        ret=_Command._run( [_Command._exiftran,'-ai',file] ) # tag is corrected by exiftran !
                        if ret.strip()!="":
                            self.debug("*WARNING* exiftran autorotate output=%s"%ret)
                        self.debug( "*WARNING* File %s needs autorotate -> done " % file )

            #-----------------------------------------------------------
            # try to autorename, if wanted
            #-----------------------------------------------------------
            if needAutoRename :
                newname = unicode(exifdate.strftime(PhotoCmd.format)+".jpg")
                if os.path.basename(file) != newname:
                    folder=os.path.dirname(file)
                    while os.path.isfile(os.path.join(folder,newname) ):
                        newname=PhotoCmd.giveMeANewName(newname)

        
                    newfile = os.path.join(folder,newname)
        
                    os.rename(file,newfile)
                    file = newfile
                    self.debug( "*WARNING* File %s needs to be renamed -> %s" % (file,newfile) )
                                    
        self.__file = file
        self.__refresh()

    def __refresh(self):
        self.__info = pyexiv2.Image(self.__file.encode("utf_8"))
        self.__info.readMetadata()

        try:
            self.__isreal   = (self.__info["Exif.Image.Make"]!="jBrout")    # except if a cam maker is named jBrout (currently, it doesn't exist ;-)
        except:
            # can only be here after a destroyInfo()
            self.__isreal = False
            
        try:
            self.__exifdate = self.__info["Exif.Image.DateTime"].strftime("%Y%m%d%H%M%S")
        except:
            # can only be here after a destroyInfo()
            self.__exifdate=""
            
        self.__filedate = self.__exifdate

        w,h= Image.open(self.__file).size
        self.__resolution = "%d x %d" % (w,h) # REAL SIZE !

            #~ 0x9209: ('Flash', {0:  'No',
                               #~ 1:  'Fired',
                               #~ 5:  'Fired (?)', # no return sensed
                               #~ 7:  'Fired (!)', # return sensed
                               #~ 9:  'Fill Fired',
                               #~ 13: 'Fill Fired (?)',
                               #~ 15: 'Fill Fired (!)',
                               #~ 16: 'Off',
                               #~ 24: 'Auto Off',
                               #~ 25: 'Auto Fired',
                               #~ 29: 'Auto Fired (?)',
                               #~ 31: 'Auto Fired (!)',
                               #~ 32: 'Not Available'}),

                               # 89 : Yes, auto, red-eye reduction
        try:
            v=int(self.__info["Exif.Photo.Flash"])
            if v in (1,5,7,9,13,15,25,29,31,89, 73):
                self.__isflash      = "Yes"
            elif v in (0,16,24):
                self.__isflash      = "No"
            else:
                raise "UNKNow flash value : %d '%s'"%(v,self.__file.encode("utf_8"))
        except KeyError:
            self.__isflash    =""

        self.__comment = self.__info.getComment().decode("utf_8")

        try:
            l=self.__info["Iptc.Application2.Keywords"]
            if type(l) == tuple:
                self.__tags = [unicode(i.strip("\x00"),"utf_8") for i in l] # strip("\x00") = digikam patch
                self.__tags.sort()
            else:
                self.__tags = [unicode(l,"utf_8")]
        except KeyError:
            self.__tags = []


    def __saveTB(self,f):   # not used
        self.__info.dumpThumbnailToFile(f)

    def __getThumbnail(self):
        try:
            t=self.__info.getThumbnailData()
            return t[1]
        except IOError: #Cannot access image thumbnail
            return ""

    def showAll(self):
        for key in self.__info.exifKeys():
            print key,(self.__info[key],)   # tuple to avoid unicode error in print
        for key in self.__info.iptcKeys():
            print key,(self.__info[key],)   # tuple to avoid unicode error in print

    def __repr__(self):
        return """file : %s
readonly : %s
isflash : %s
resolution : %s
filedate : %s
exifdate : %s
thumb : %d
isreal : %s""" % (
            self.__file,
            self.__readonly,
            self.__isflash,
            self.__resolution,
            self.__filedate,
            self.__exifdate,
            len(self.__getThumbnail()),
            self.__isreal,
            )

    def redate(self,w,d,h,m,s):
        """
        redate jpeg file from offset : weeks, days, hours, minutes,seconds
        """
        if self.__readonly: return False

        #TODO:attention au fichier sans EXIF ici !!!!

        fd=self.__info["Exif.Image.DateTime"]
        fd+=timedelta(weeks=w, days=d,hours=h,minutes=m,seconds=s)

        self.__info["Exif.Image.DateTime"]=fd
        self.__info["Exif.Photo.DateTimeOriginal"]=fd
        self.__info["Exif.Photo.DateTimeDigitized"]=fd

        self.__maj()
        return True


    def clear(self):
        if self.__readonly: return False
        try:
            prec = self.__info["Iptc.Application2.Keywords"] #TODO: to bypass a bug in pyexiv2
            self.__info["Iptc.Application2.Keywords"] = []
        except:
            pass
        self.__maj()
        return True


    def sub(self,t):
        assert type(t)==unicode
        if self.__readonly: return False
        if t in self.__tags:
            self.__tags.remove(t)
            self.__majTags()
            return True
        else:
            return False

    def add(self,t):
        assert type(t)==unicode
        if self.__readonly: return False
        if t in self.__tags:
            return False
        else:
            self.__tags.append(t)
            self.__majTags()
            return True

    def addTags(self,tags): # *new*
        """ add a list of tags to the file, return False if it can't """
        if self.__readonly: return False
        isModified = False
        for t in tags:
            assert type(t)==unicode
            if t not in self.__tags:
                isModified = True
                self.__tags.append(t)

        if isModified:
            self.__majTags()
        return True


    def subTags(self,tags): # *new*
        """ sub a list of tags to the file, return False if it can't """
        if self.__readonly: return False
        
        isModified = False
        for t in tags:
            assert type(t)==unicode
            if t in self.__tags:
                isModified = True
                self.__tags.remove(t)

        if isModified:
            self.__majTags()
        return True

    def destroyInfo(self):
        """ destroy ALL info (exif/iptc)
        """
        if self.__readonly: return False
        
        # delete EXIF and IPTC tags :
        l=self.__info.exifKeys() + self.__info.iptcKeys()
        for i in l:
            self.__info[i]=""       # avoid a bug in pyexiv2
            self.__info[i]=None     # delete tag ("del t[]" doesn't do the job)

        self.__info.deleteThumbnail()   # seems not needed !
        self.__info.clearComment()

        self.__maj()    # so, ONLY CASE where self.exifdate==""
        return True


    def copyInfoTo(self,file2):
        """ copy exif/iptc to "file2", return dest photonode
        """
        assert type(file2)==unicode
        assert os.path.isfile(file2)

        np = PhotoCmd(file2)
        np.destroyInfo()
        
        # copy all exif/iptc info
        l=self.__info.exifKeys() + self.__info.iptcKeys()
        for i in l:
            if i not in ["Exif.Photo.UserComment",]: # key "Exif.Photo.UserComment" bugs always ?!
                if not i.startswith("Exif.Thumbnail"):  # don't need exif.thumb things because it's rebuilded after
                    np.__info[i] =self.__info[i]

        # copy comment
        np.addComment( self.comment )

        # and rebuild exif
        np.rebuildExifTB()

        return np


    def rebuildExifTB(self):
        if self.__readonly: return False
        
        im= Image.open(self.__file)
        im.thumbnail((160,160), Image.ANTIALIAS)

        file1 = StringIO.StringIO()
        im.save(file1, "JPEG")
        buf=file1.getvalue()
        file1.close()
        self.__info.setThumbnailData(buf)

        self.__maj()
        return True



    def __majTags(self):
        self.__info["Iptc.Application2.Keywords"] = [i.encode("utf_8") for i in self.__tags]
        self.__maj()

    def __maj(self):
        self.__info.writeMetadata()
        self.__refresh()








    def addComment(self,c):
    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        assert type(c)==unicode
        c=c.strip()
        if c=="":
            self.__info.clearComment()
        else:
            self.__info.setComment(c.encode("utf_8"))

        self.__maj()
        return True

    def rotate(self,sens):
    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        """ rotate LOSSLESS the picture 'file', and its internal thumbnail according 'sens' (R/L)"""
        if sens=="R":
            deg = "90"
            opt = "-9"
        else:
            deg = "270"
            opt = "-2"

        if _Command.isWin:
            ret= _Command._run( [_Command._jpegtran,'-rotate',deg,'-copy','all',self.__file,self.__file] )
            # rebuild the exif thumb, because jpegtran doesn't do it on windows
            self.rebuildExifTB()
        else:
            ret= _Command._run( [_Command._exiftran,opt,'-i',self.__file] ) # exiftran rotate internal exif thumb

        self.__refresh()


     #~ def rotates(self):           # NO ROTATE LOSS LESS ;-(
        #~ im=Image.open(self.__file)
        #~ im=im.transpose(Image.ROTATE_90)
        #~ im.save(self.__file)

    def isThumbOk(self):
        #  1 : thumb seems good with original (same orientation)
        #  0 : not same orientation
        # -1 : no thumb
        isThumbOk = None


        im=Image.open(self.__file)
        im.verify()
        w,h = im.size
        isImageHorizon =w>h

        t=self.__getThumbnail()
        if t:
            f=StringIO.StringIO()
            f.write(t)
            f.seek(0)
            tw,th=Image.open(f).size
            isTImageHorizon = tw>th

            if isImageHorizon == isTImageHorizon:
                isThumbOk = 1
            else:
                isThumbOk = 0
        else:
            isThumbOk=-1

        assert (self.__info["Exif.Image.DateTime"]==self.__info["Exif.Photo.DateTimeOriginal"]==self.__info["Exif.Photo.DateTimeDigitized"])

        return isThumbOk

    #@staticmethod
    #def normalizeName(file):
    #    """
    #    normalize name (only real exif pictures !!!!)
    #    """
    #    assert type(file)==unicode
    #    p=PhotoCmd(file)
    #    p.__rename()
    #    return p.file

    @staticmethod
    def setNormalizeNameFormat(format):
        PhotoCmd.format=format


    @staticmethod
    def giveMeANewName(name):
        n,ext = os.path.splitext(name)
        mo= re.match("(.*)\((\d+)\)$",n)
        if mo:
            n=mo.group(1)
            num=int(mo.group(2)) +1
        else:
            num=1

        return "%s(%d)%s" % (n,num,ext)


    #@staticmethod
    #def prepareFile(file,needRename,needAutoRot):
    #    """
    #    prepare file, rotating/autorotating according exif tags
    #    (same things as normalizename + autorot, in one action)
    #    only called at IMPORT/REFRESH albums
    #    """
    #    assert type(file)==unicode
    #
    #
    #    if needAutoRot:
    #        if _Command.isWin:
    #            # do nothing
    #            # -> because no gpl tools which rotate well (img+thumb) automatically according exif
    #            #    if you provide me one, i'll integrate here
    #            pass
    #        else:
    #            _Command._run( [_Command._exiftran,'-ai',file] )
    #
    #    if needRename:
    #        return PhotoCmd.normalizeName(file)
    #    else:
    #        return file


if __name__=="__main__":

    #~ f=u"images_exemples/IMG_3320.JPG"
    #~ help(pyexiv2)
    #~ i=PhotoCmd(f)
    #~ i.showAll()
    #~ i.showExiv()
    #~ print i.file
    #~ i.autorotate()
    #~ i.rename()
    #~ i.destroyInfo()
    #~ print len(i.getThumbnail())
    #~ print i["Exif.Image.DateTime"]
    #~ print i["Exif.Image.DateTime"]
    #~ print i.control()
    #~ print i
    pass
