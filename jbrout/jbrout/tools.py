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
  - autorot only available on LINUX and Windows
  - addition of transfrom command (rotate is now depricated)
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
from subprocess import Popen,PIPE,call
import db 

def ed2cd(f): #yyyy/mm/dd hh:ii:ss -> yyyymmddhhiiss
   if f:
      return f[:4]+f[5:7]+f[8:10]+f[11:13]+f[14:16]+f[17:19]
   else:
      return f

# the second argument provides a string when using this code to provide rotation to plugins
autoTrans = {
    1: ["none", "None"],
    2: ["flipHorizontal", "Flip Horizontal"],
    3: ["rotate180", "Rotate 180"],
    4: ["flipVertical", "Flip Vertical"],
    5: ["transpose", "Transpose"],
    6: ["rotate90", "Rotate Left"],
    7: ["transverse", "Transverse"],
    8: ["rotate270", "Rotate Right"]}

rawFormats=["NEF","nef","DNG","dng","cr2","CR2"]
#           "cr2","CR2" files are for canon RAW. Makes pyexiv2 crash 14/07/2009 works with exiv2 though
supportedFormats=["JPG","jpg","JPEG","jpeg","NEF","nef","DNG","dng","cr2","CR2"]

class CommandException(Exception):
   def __init__(self,m):
      self.message=m
   def __str__(self):
      return self.message


def decode(s, encodings=['ascii', 'utf8', 'latin1',] ):
    """ method to decode text (tag or comment) to unicode """
    for encoding in encodings:
        try:
            return s.decode(encoding)
        except UnicodeDecodeError:
            pass
    print " *WARNING* : no valid decoding for string '%s'"%(str([s]))
    return s.decode('utf8', 'replace')


# ##############################################################################################
class _Command:
# ##############################################################################################
   """ low-level access (wrapper) to external tools used in jbrout
   """
   isWin=(sys.platform[:3] == "win")
   __path =os.path.join(os.getcwdu(),u"data",u"tools")

   err=""
   if isWin:
      # set windows path
      _exiftran = None
      _jpegtran = os.path.join(__path,"jpegtran.exe")

      if not os.path.isfile(_jpegtran):
          err+="jpegtran is not present in 'tools'\n"
      
      _exiftool = os.path.join(__path,"exiftool.exe")
      if not os.path.isfile(_exiftool):
          err+="exiftool is not present in 'tools'\n"

   else:
      # set "non windows" path (needs 'which')
      _exiftran = u"".join(os.popen("which exiftran").readlines()).strip()
      _jpegtran = None
      _exiftool = u"".join(os.popen("which exiftool").readlines()).strip()

      if not os.path.isfile(_exiftran):
          err+="exiftran is not present, please install 'exiftran'(fbida)\n"

      if not os.path.isfile(_exiftool):
          err+="exiftool is not present, please install 'exiftool'\n"

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
        if "exiftool" in cmdline:
            if "Warning" in outerr:
                #exiftool warning that has no impact on result
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
        

        self.__file = file
        self.__readonly = not os.access( self.__file, os.W_OK)
        
        # pre-read

        self.__info = pyexiv2.Image(self.__file)
        self.__info.readMetadata()

        if self.readonly:
            self.debug( "*WARNING* File %s is READONLY" % file )
        else:
            #-----------------------------------------------------------
            # try to correct exif date if wrong
            #-----------------------------------------------------------
            # if no exifdate ---> put the filedate in exifdate
            # SO exifdate=filedate FOR ALL
            try:
                #self.__info["Exif.Image.DateTime"].strftime("%Y%m%d%H%M%S")
                self.__info["Exif.Photo.DateTimeOriginal"].strftime("%Y%m%d%H%M%S")
                isDateExifOk=True
            except KeyError:        # tag exif datetime not present
                isDateExifOk=False
            except AttributeError:  # content of tag exif datetime is not a datetime
                isDateExifOk=False

            if not isDateExifOk:
                self.debug( "*WARNING* File %s had wrong exif date -> corrected" % file )

                fd=datetime.fromtimestamp(os.stat(file).st_mtime)
                self.__info["Exif.Image.Make"]="jBrout" # mark exif made by jbrout
                self.__info["Exif.Image.DateTime"]=fd
                self.__info["Exif.Photo.DateTimeOriginal"]=fd
                self.__info["Exif.Photo.DateTimeDigitized"]=fd
                self.__info.writeMetadata()

            #exifdate = self.__info["Exif.Image.DateTime"]
            exifdate = self.__info["Exif.Photo.DateTimeOriginal"]

            #-----------------------------------------------------------
            # try to autorot, if wanted
            #-----------------------------------------------------------
            if needAutoRotation :
                self.transform("auto")

            #-----------------------------------------------------------
            # try to autorename, if wanted
            #-----------------------------------------------------------
            if needAutoRename :
                folder=os.path.dirname(file)
                nameShouldBe = unicode(exifdate.strftime(PhotoCmd.format))
                newname = nameShouldBe+u'.'+file.split('.')[-1].lower()

                if not os.path.isfile(os.path.join(folder,newname)):
                    # there is no files which already have this name
                    # we can simply rename it
                    newfile = os.path.join(folder,newname)

                    os.rename(file,newfile)
                    self.__file = newfile
                else:
                    # there is a file, in the same folder which already got
                    # the same name

                    if nameShouldBe != os.path.basename(file)[:len(nameShouldBe)]:
                        while os.path.isfile(os.path.join(folder,newname) ):
                            newname=PhotoCmd.giveMeANewName(newname)

                        newfile = os.path.join(folder,newname)

                        os.rename(file,newfile)
                        self.__file = newfile
                        #self.debug( "*WARNING* File %s needs to be renamed -> %s" % (file,newfile) )

        self.__refresh()

    def __refresh(self):
        self.__info = pyexiv2.Image(self.__file)
        self.__info.readMetadata()

        try:
            self.__isreal   = (self.__info["Exif.Image.Make"]!="jBrout")    # except if a cam maker is named jBrout (currently, it doesn't exist ;-)
        except:
            # can only be here after a destroyInfo()
            self.__isreal = False

        try:
            #self.__exifdate = self.__info["Exif.Image.DateTime"].strftime("%Y%m%d%H%M%S")
            self.__exifdate = self.__info["Exif.Photo.DateTimeOriginal"].strftime("%Y%m%d%H%M%S")
        except:
            try:
                self.__exifdate = self.__info["Exif.Image.DateTime"].strftime("%Y%m%d%H%M%S")
            except:
                # can only be here after a destroyInfo()
                self.__exifdate=""

        self.__filedate = self.__exifdate

        try:
            w,h= Image.open(self.__file).size
        except IOError:
            w,h=0,0 # XXX not recognized yetwith exiv2
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
            # value taken from http://209.85.129.132/search?q=cache:YYpAe4uzONgJ:gallery.menalto.com/node/55248+exif+%22flash+value%22+95&hl=fr&ct=clnk&cd=3&gl=fr
            if v in (1,5,7,9,13,15,25,29,31,65,69,71,73,77,79,89,93,95):
                self.__isflash      = "Yes"
            elif v in (0,4,16,24,32,80,88):
                self.__isflash      = "No"
            else:
                print "*WARNING* : Unknown exif flash value : %d in '%s'"%(v,str([self.__file]))
                if v%2: #impair
                    self.__isflash      = "Yes"
                else:
                    self.__isflash      = "No"
        except KeyError:
            self.__isflash    =""

        self.__comment = decode(self.__info.getComment())

        try:
            l=self.__info["Iptc.Application2.Keywords"]
            if type(l) == tuple:
                self.__tags = [decode(i.strip("\x00")) for i in l] # strip("\x00") = digikam patch
                self.__tags.sort()
            else:
                self.__tags = [decode(l.strip("\x00"))]
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

        #fd=self.__info["Exif.Image.DateTime"]
        fd=self.__info["Exif.Photo.DateTimeOriginal"]
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
            try:
                del self.__info[i]
            except KeyError: # 'tag not set'
                # the tag seems not to be here, so
                # we don't need to clear it, no ?
                pass

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
                    if len(re.findall('0x0',i))==0: # Work around to fix error in pyev2 with most unknown makernoite tags
                        # TODO: fix nasty bodge to get around pyexiv2 issues with multi part exif fields
                        # known not to copy the following:
                        #   - unknown maker not fields
                        #   - lens data for canon
                        try:
                            np.__info[i] =self.__info[i]
                        except:
                            print "Problems copying %s keyword" %i

        # copy comment
        np.addComment( self.comment )

        # and rebuild exif
        np.rebuildExifTB()
        
        return np

    def rebuildExifTB(self):
        if self.__readonly: return False

        try:
            im= Image.open(self.__file)
            im.thumbnail((160,160), Image.ANTIALIAS)
        except Exception,m:
            print "*WARNING* can't load this file : ",(self.__file,),m
            im=None

        if im:
            file1 = StringIO.StringIO()
            im.save(file1, "JPEG")
            buf=file1.getvalue()
            file1.close()
            self.__info.setThumbnailData(buf)

            self.__maj()
            return True
        else:
            return False

    def __majTags(self):
        self.__info["Iptc.Application2.Keywords"] = [i.encode("utf_8") for i in self.__tags]
        self.__maj()
        
    def __maj(self):
        try:
            self.__info.writeMetadata()
        except IOError:
            # XXX not recognized yet by pyexiv2. Another option to save infos ?
            pass
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

    def transform(self,sens):
    # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        """ LOSSLESS transformation of the picture 'file', and its internal
        thumbnail according 'sens'
         """
        if sens=="auto":
            try:
                sens = autoTrans[int(self.__info['Exif.Image.Orientation'])][0]
            except KeyError:
                sens = autoTrans[1][0]
        if sens=="rotate90":
            jpegtranOpt = ["-rotate", "90"]
            exiftranOpt = "-9"
        elif sens=="rotate180":
            jpegtranOpt = ["-rotate", "180"]
            exiftranOpt = "-1"
        elif sens=="rotate270":
            jpegtranOpt = ["-rotate", "270"]
            exiftranOpt = "-2"
        elif sens=="flipHorizontal":
            jpegtranOpt = ["-flip", "horizontal"]
            exiftranOpt = "-f"
        elif sens=="flipVertical":
            jpegtranOpt = ["-flip", "vertical"]
            exiftranOpt = "-F"
        elif sens=="transpose":
            jpegtranOpt = ["-transpose"]
            exiftranOpt = "-t"
        elif sens=="transverse":
            jpegtranOpt = ["-transverse"]
            exiftranOpt = "-T"

        if not(sens == "none"):
            if _Command.isWin:
                    ret= _Command._run( [_Command._jpegtran]+jpegtranOpt+['-copy','all',self.__file,self.__file] )
                    # rebuild the exif thumb, because jpegtran doesn't do it on windows
                    self.rebuildExifTB()
            else:
                ret= _Command._run( [_Command._exiftran,exiftranOpt,'-i',self.__file] ) # exiftran rotate internal exif thumb

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

        return u"%s(%d)%s" % (n,num,ext)


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

class XMPUpdater():
    def __init__(self,photo_list):
        """XMPUpdater is in charge of manipulating XMP data.
        It might disapear when pyexiv2 will have XMP support"""
        
        # Do we synchronize automatically ?
        self.synchronizeXmp=db.JBrout.conf["synchronizeXmp"]
        
        # List of pictures
        self.list=photo_list
        
        # List of pictures' name
        if len(self.list)>0:
            if type(self.list[0]) in [str,unicode]:
                self.pictures=self.list
            else:
                self.pictures=[]
                for picture in self.list:
                    self.pictures.append(picture.file.encode('utf-8'))

    def SyncXmpIptc(self):
        """Merge XMP and IPTC if option is on"""
        if not self.synchronizeXmp:
            return 1
        self.DoMergeXmpIptc()
        
    def UpdateXmp(self):
        """Save tags to XMP subjects if option is on"""
        if not self.synchronizeXmp:
            return 1
        self.DoSaveXmp()

    def DoMergeXmpIptc(self):
        """Import XMP subjects, merge with IPTC keywords and save to both"""
        if not self.synchronizeXmp:
            return 1
        #initialize command
        command=[_Command._exiftool]
        #remove subject from keywords to avoid duplicates
        command.extend(["-r", "-overwrite_original", "-addtagsfromfile@", "-keywords-<subject"])
        #add pictures list
        command.extend(self.pictures)
        ret= _Command._run( command )

        #initialize command
        command=[_Command._exiftool]
        #add subject to keywords
        command.extend(["-r", "-overwrite_original", "-addtagsfromfile@", "-keywords+<subject"])
        #add pictures list
        command.extend(self.pictures)
        ret= _Command._run( command )
        
        #initialize command
        command=[_Command._exiftool]
        #copy keywords to subect
        command.extend(["-r", "-overwrite_original", "-subject< keywords"])
        command.extend(self.pictures)
        ret= _Command._run(command) 

    def DoSaveXmp(self):
        """Save tags to XMP subjects"""
        if not self.synchronizeXmp:
            return 1
        command=[_Command._exiftool]
        command.extend(["-r", "-overwrite_original", "-subject< keywords"])
        command.extend(self.pictures)
        ret= _Command._run(command) 

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
