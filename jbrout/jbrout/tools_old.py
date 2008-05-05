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

# here is the worst code of jbrout (but it works well ;-)
# this file should be redone from scratch, one day ... manatlan

import time
import sys,os,string,re
from datetime import timedelta
import datetime
from subprocess import Popen,PIPE
import tempfile
from common import cd2d,ed2d,ed2cd


# Protect against crappy output of some unnamed (ehm,
# ehm, jhead) programs. Prepare tables for later use.
nonPCData = ''

# additional procedure for working with Unicode -- normal
# string.maketrans doesn't work with Unicode strings.
# originally from
# http://groups.google.com/group/comp.lang.python/msg/4dbebae9e040a7b3
def maketransU(s1, s2, todel=""):
    trans_tab = dict( zip( map(ord, s1), map(ord, s2) ) )
    trans_tab.update( (ord(c),None) for c in todel )
    return trans_tab

# These are codes of characters which are not PCDATA
# and so they cannot happen in XML file.
nonPCDataRange = range(0x00,0x08)+[0x0b,0x0c]+range(0x0e,0x19)
# The following ones are stricly speaking not incorrect (and XML
# parse won't choke on them), but they are unprintable control
# characters, so they will probably never happen in metadata.
nonPCDataRange += range(0x7f,0x9f)
for i in nonPCDataRange:
   nonPCData += chr(i)
allchars = maketransU('','',nonPCData)


class CommandException(Exception):
   def __init__(self,m):
      self.message=m
   def __str__(self):
      return self.message

# ##############################################################################################
class _Command:
# ##############################################################################################
   """ low-level access (wrapper) to external tools used in jbrout
   """

   format = "p%Y%m%d_%H%M%S"
   #format = "%Y-%m-%d_%H-%M-%S"

   isWin=(sys.platform[:3] == "win")
   __path =os.path.join(os.getcwdu(),u"data/tools")

   err=""
   if isWin:
      # set windows path
      __jhead = os.path.join(__path,"jhead.exe")
      __exiftran = None
      __jpegtran = os.path.join(__path,"jpegtran.exe")
      __jpegnail = os.path.join(__path,"jpegnail.exe")
      __exifedit = os.path.join(__path,"exifedit.exe") #perhaps it's there !

      if not os.path.isfile(__jhead):
          err+="jhead is not present in 'tools'\n"
      if not os.path.isfile(__jpegtran):
          err+="jpegtran is not present in 'tools'\n"
      if not os.path.isfile(__jpegnail):
          err+="jpegnail is not present in 'tools'\n"

   else:
      # set "non windows" path (needs 'which')
      __jhead = u"".join(os.popen("which jhead").readlines()).strip()
      __exiftran = u"".join(os.popen("which exiftran").readlines()).strip()
      __jpegtran = None
      __jpegnail = None
      __exifedit = None

      if not os.path.isfile(__jhead):
          err+="jhead is not present, please install 'jhead'\n"
      if not os.path.isfile(__exiftran):
          err+="exiftran is not present, please install 'exiftran'(fbida)\n"

   if err:
      raise CommandException(err)



   @staticmethod
   def _run(cmds):
        cmdline = str( [" ".join(cmds)] ) # to output easily (with strange chars)
        try:
            cmds = [i.encode(sys.getfilesystemencoding()) for i in cmds]
        except:
            raise CommandException( cmdline +"\n encoding trouble")

        p = Popen(cmds, shell=False,stdout=PIPE,stderr=PIPE)
        time.sleep(0.01)    # to avoid "IOError: [Errno 4] Interrupted system call"
        out = string.join(p.stdout.readlines() ).strip()
        outerr = string.join(p.stderr.readlines() ).strip()

        if "jhead" in cmdline:
           if "Nonfatal Error" in outerr:
               # possible "Suspicious offset of first IFD value" (non fatal error of jhead)
               outerr=""
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

           # Protect against crappy output of some unnamed (ehm,
           # ehm, jhead) programs. Use tables from the top of this
           # module.
           out = out.translate(allchars)

           return out #unicode


   #----------------------------------------------------------------------------
   @staticmethod
   def setDate(file, newDate ):
   #----------------------------------------------------------------------------
        """ set the Exif and File dates of file 'file' to date 'newDate' """
        _Command._run( [_Command.__jhead,"-ts"+newDate.strftime("%Y:%m:%d-%H:%M:%S"),'-ft',file] )

   #----------------------------------------------------------------------------
   @staticmethod
   def getExifInfo(file):
   #----------------------------------------------------------------------------
        """ get the result Exif of jhead """
        return _Command._run( [_Command.__jhead,file] )


   #----------------------------------------------------------------------------
   @staticmethod
   def prepareFile(file,needRename=True,needAutoRot=False):
   #----------------------------------------------------------------------------
        """
          prepare the file (rename/rotate according exif) ... (in one jhead action (optimization))

          if needRename :
            rename file according its exifdate, and set datefile = date exif,
            and return the new name (or old one if not renamed)

          and do autorot according exif tag if "needAutoRot" is True
        """

        if _Command.isWin:
            needAutoRot = False # no autorotate on windows (jpegtran trouble)

        if needRename:
            # renaming is needed, we'll need to return the new name
            if needAutoRot:
                buf = _Command._run( [_Command.__jhead,"-ft","-autorot","-nf"+_Command.format,file] )
            else:
                buf = _Command._run( [_Command.__jhead,'-ft',"-nf"+_Command.format,file] )

            # rename has be done, we need to get the newname
            # (we get it in jhead output)
            p = buf.find("-->")
            if p>0:
               # it was renamed
               return buf[p+3:].strip()
            else:
               # not renamed, return original name
               return file

        else:
            # no renaming, return the original filename (to be compatible)
            if needAutoRot:
                _Command._run( [_Command.__jhead,"-ft","-autorot",file] )

            return file

   #----------------------------------------------------------------------------
   @staticmethod
   def getExif(file):
   #----------------------------------------------------------------------------
      """ return a dict of exif info of the file(jpeg) 'file'
          filedate,resolution,exifdate,isflash,jpegcomment
      """

      tag = {}

      buf = _Command._run( [_Command.__jhead,file] )
      assert type(buf)==unicode

      try:
          tag["filedate"] = re.findall( "File date    : (\d\d\d\d:\d\d:\d\d \d\d:\d\d:\d\d)", buf )[0].strip()
          tag["resolution"] = re.findall( "Resolution   : (.*)", buf )[0].strip()
      except:
          raise CommandException( "Exif decoding trouble in "+file +"\n"+buf)


      # try to get exif info (from jhead)
      try:
         exifdate   = re.findall( "Date/Time    : (\d\d\d\d:\d\d:\d\d \d\d:\d\d:\d\d)", buf )[0].strip()
         isflash    = re.findall( "Flash used   : (.*)", buf )[0].strip()
      except IndexError:
         exifdate   =""
         isflash    =""

      try:
         cd2d(ed2cd(exifdate))    # just to test if it's a real date
      except:
         exifdate = ""

      tag["exifdate"]   =exifdate
      tag["isflash"]    =isflash

      # get the comment (which can be multilines)
      mo_comm = re.findall( "Comment      : (.*)", buf )
      comment = u""
      for i in mo_comm:
         if comment != "" : comment = comment + "\n"
         comment = comment + i.strip()
      tag["jpegcomment"]=comment

      # convert date to format yyyymmddhhiiss
      tag["filedate"]=ed2cd(tag["filedate"])
      tag["exifdate"]=ed2cd(tag["exifdate"])

      return tag


   #----------------------------------------------------------------------------
   @staticmethod
   def setJpegComment(file,buf):
   #----------------------------------------------------------------------------
      """ set the jpegcomment 'buf' in the picture 'file' """
      if buf:
         assert type(buf)==unicode

         tmp_fd, tmp_name = tempfile.mkstemp(prefix='jbrout')
         tf = os.fdopen(tmp_fd, 'w')
         if tf:
            tf.write( buf.encode("utf_8") ) # comment in UTF8 *new*
            tf.close()

            _Command._run( [_Command.__jhead,'-ci',tmp_name,file] )

            try:
               os.unlink(tmp_name)
            except:
               pass
            return True

         return False
      else:
         # kill the jpeg comment
         _Command._run( [_Command.__jhead,'-dc',file] )
         return True



   #----------------------------------------------------------------------------
   @staticmethod
   def rotate(file,sens):
   #----------------------------------------------------------------------------
      """ rotate the picture 'file', and its internal thumbnail according 'sens' (R/L)"""
      if sens=="R":
         deg = "90"
         opt = "-9"
      else:
         deg = "270"
         opt = "-2"

      if _Command.isWin:
        b= _Command._run( [_Command.__jpegtran,'-rotate',deg,'-copy','all',file,file] )
        # rebuild the exif thumb, because jpegtran doesn't do
        _Command.rebuildExifThumb(file)
      else:
        b= _Command._run( [_Command.__exiftran,opt,'-ip',file] )

      return b


   #----------------------------------------------------------------------------
   @staticmethod
   def rebuildExifThumb(file):
   #----------------------------------------------------------------------------
      """ rebuild the internal thumbnail of the picture 'file' """

      if _Command.isWin:
         if os.path.isfile( _Command.__exifedit ): # if exifedit is here
            # it's a lot better to use exifedit on win32
            _Command._run( [_Command.__exifedit,"/t","a,160","/b",file] )
         else:
            _Command._run( [_Command.__jpegnail, '-q', '75', '-x', '160', '-y', '160',file ] )
      else:
         _Command._run( [_Command.__exiftran, '-g', '-ip', file ] )


   #----------------------------------------------------------------------------
   @staticmethod
   def removeExif(file):
   #----------------------------------------------------------------------------
      """ remove all exif tags of picture 'file' """
      _Command._run( [_Command.__jhead,'-de',"-dt","-dc",file] )

   #----------------------------------------------------------------------------
   @staticmethod
   def copyExif(file1,file2):
   #----------------------------------------------------------------------------
      """ copy exif info from file1 to file2 (and redate filedate of file2) """
      _Command._run( [_Command.__jhead,"-ft",'-te',file1,file2] )



class DateSave:
    def __init__(self,file):
        """ save dates info """
        self.file = file
        s = os.stat(file)
        self.atime = s.st_atime
        self.mtime = s.st_mtime

    def touch(self):
        """ return the error or "" if not """
        try:
            os.utime(self.file,(self.atime,self.mtime))
            return ""
        except OSError,detail:
            # utime doesn't work well if uid/gid are not the same
            # so we need to use the real touch ;-) (with mtime)
            print "need to touch ;-("
            stime = time.strftime("%Y%m%d%H%M.%S",time.localtime(self.mtime) )
            _Command._run( ["touch",'-t',stime,self.file] )
            return ""

    def redate(self,w,d,h,m,s ):
        t= time.localtime(self.mtime)
        dt = datetime.datetime(t[0],t[1],t[2],t[3],t[4],t[5])
        dt+=datetime.timedelta(d,s,0,0,m,h,w)
        t = dt.timetuple()
        self.mtime= time.mktime(t)
        self.atime= self.mtime
        self.touch()


from libs.iptcinfo import IPTCInfo
# ============================================================================================
class PhotoCmd(object):
# ============================================================================================
   """ Manipulate photos(jpg)
   """
   @staticmethod
   def normalizeName(file):
        """
        normalize name (only real exif pictures !!!!)
        """
        assert type(file)==unicode

        return _Command.prepareFile(file,needRename=True,needAutoRot=False)

   @staticmethod
   def prepareFile(file,needRename,needAutoRot):
        """
        prepare file, rotating/autorotating according exif tags
        (same things as normalizename + autorot, in one action)
        only called at IMPORT/REFRESH albums
        """
        assert type(file)==unicode

        return _Command.prepareFile(file,needRename,needAutoRot)


   @staticmethod
   def setNormalizeNameFormat(format):
        """ set format for normalized files (see prepareFile())"""
        _Command.format = format


   def __init__(self,file):
      assert type(file)==unicode,"ERROR:"+str(type(file))
      assert os.path.isfile(file)



      self.file = file
      self.__read()

      # save filesystem mtime/atime
      self.ds = DateSave(self.file)

   def __getTags(self):
       return self.__iptc.keywords
   tags = property(__getTags)

   def __read(self):
      t = _Command.getExif(self.file)

      self.comment      = t["jpegcomment"]
      self.filedate     = t["filedate"]
      self.resolution   = t["resolution"]
      self.exifdate     = t["exifdate"]
      self.isflash      = t["isflash"]
      self.readonly     = not os.access( self.file, os.W_OK)

      self.__iptc = IPTCInfo(self.file,True)

      self.__iptc.keywords.sort()


   def sub(self,t):
      assert type(t)==unicode
      if t in self.__iptc.keywords:
         self.__iptc.keywords.remove(t)
         return self._write()
      else:
         return False

   def add(self,t):
      assert type(t)==unicode
      if t in self.__iptc.keywords:
         return False
      else:
         self.__iptc.keywords.append(t)
         return self._write()

   def addTags(self,tags): # *new*
        """ add a list of tags to the file, return False if it can't """
        isModified = False
        for t in tags:
            assert type(t)==unicode
            if t not in self.__iptc.keywords:
                isModified = True
                self.__iptc.keywords.append(t)

        if isModified:
            return self._write()
        return True

   def _setCommentAndTags(self,c,t): # **special convert**
        assert type(c)==unicode,str(type(c))+" : "+c
        for i in t:
            assert type(i)==unicode
            pass
        self.comment = c
        self.__iptc.keywords = t
        return self._write()


   def subTags(self,tags): # *new*
        """ sub a list of tags to the file, return False if it can't """
        isModified = False
        for t in tags:
            assert type(t)==unicode
            if t in self.__iptc.keywords:
                isModified = True
                self.__iptc.keywords.remove(t)

        if isModified:
            return self._write()
        return True

   def clear(self):
      self.__iptc.keywords = []
      return self._write()

   def addComment(self,c):
      assert type(c)==unicode
      self.comment = c
      return self._write()


   def _write(self):
      """ writes tags/comment (sub(),add(),addTags(),subTags(),clear(),addComment())
          return True if tags/comment were written, false if not
      """

      if self.__iptc.save():
         _Command.setJpegComment(self.file,self.comment)
         self.ds.touch()    # retouch filesystem mtime/atime
         return True
      else:
         return False

   def redate(self,w,d,h,m,s ):
        """
        redate jpeg file from offset : weeks, days, hours, minutes,seconds
        if exif : redate internal date and fs dates (jhead -ft)
        if not : redate file dates (atime/mtime)
        """
        if self.exifdate:
            # redate internal exif date
            # and redate "filesystem dates" with "jhead -ft" !!!
            newDate=cd2d(self.exifdate)
            newDate+=timedelta(weeks=w, days=d,hours=h,minutes=m,seconds=s)

            _Command.setDate(self.file,newDate )
        else:
            # ONLY redate "filesystem dates"
            self.ds.redate(w,d,h,m,s )
        self.__read() # read again, exifdate has changed

   def rotate(self,sens):
      _Command.rotate(self.file,sens)
      self.ds.touch()    # retouch filesystem mtime/atime
      self.__read() # read again, because resolution has changed

   def rebuildExifTB(self):
      _Command.rebuildExifThumb(self.file)
      self.ds.touch()    # retouch filesystem mtime/atime
      self.__read() # read again, perhaps something has changed

   def getExifInfo(self):
      """ return the result of jhead on this file """
      return _Command.getExifInfo(self.file)

   def destroyInfo(self):
      """ destroy info (exif/iptc) of the file
          but keep filesystem date

          *IMPORTANT* : it doesn't kill IPTC-block, only KEYWORDS !
      """
      _Command.removeExif(self.file)
      self.clear()      # clear IPTC tags
      self.ds.touch()    # retouch filesystem mtime/atime
      self.__read() # read again, perhaps something has changed

   def copyInfoTo(self,file2):
      """ copy exif/iptc to "file2"
          and redate filesystem date of file2 according exif
      """
      assert type(file2)==unicode

      #copy iptc tags
      i=IPTCInfo(file2,True)
      i.keywords=[]
      i.keywords+=self.__iptc.keywords
      i.save()

      # copy exif (exif, thumb + jpegcomment), and redate
      _Command.copyExif(self.file,file2)

      # and rebuild i-thumb (should set good resolution in exif)
      ds = DateSave(file2)
      _Command.rebuildExifThumb(file2)
      ds.touch()

if __name__ == "__main__":
    f="/home/manatlan/Desktop/test_jbrout/100_fuji/p20041126_230000.jpg"

    #~ f=u"phôto.jpg"
    #~ f=u"photo.jpg"
    #~ f="/home/manatlan/Desktop/100_FUJI_recentes/p20060714_205539.jpg"
    #~ print _Command.getExifInfo(f)


    def test_Command(f):
       c=_Command
       com = u"""héllçàé€$£'"€&&<>~^à"""
       t=c.getExif(f)
       res = t["resolution"]
       c.setJpegComment(f,com)
       c.rotate(f,"L")
       t=c.getExif(f)
       com2 = t["jpegcomment"]
       print [com,com2]
       assert res != t["resolution"], "rotate is bad"
       #~ assert com == com2, "jpegcomment problem"
       c.rotate(f,"R")
       c.setJpegComment(f,"")

       newf="jp.jpg"
       import shutil
       shutil.copy(f,newf)

       d=datetime.datetime(2000,11,14,12,10,59)
       c.setDate(newf,d)
       t=c.getExif(newf)
       assert cd2d(t["filedate"]) == cd2d(t["exifdate"]) == d,"dates problem"

       newNewf = c.normalizeName(newf)
       c.rebuildExifThumb(newNewf)
       c.removeExif(newNewf)
       os.unlink(newNewf)   #raise error if a problem

    #~ test_Command(f)
