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

def _(m):
    return m


def cd2rd(f): #yyyymmddhhiiss -> dd/mm/yyyy hh:ii:ss
   if f:
      if len(f) == 14:
         return f[6:8]+"/"+f[4:6]+"/"+f[:4]+" "+f[8:10]+":"+f[10:12]+":"+f[12:14]
      else:
         return f[6:8]+"/"+f[4:6]+"/"+f[:4]
   else:
      return f

from datetime import datetime
def cd2d(f): #yyyymmddhhiiss -> datetime
   return datetime(int(f[:4]),int(f[4:6]), int(f[6:8]),int(f[8:10]),int(f[10:12]),int(f[12:14]))

def ed2d(f): #yyyy:mm:dd hh:ii:ss -> datetime (output from exif lib)
    return datetime(int(f[:4]),int(f[5:7]), int(f[8:10]),int(f[11:13]),int(f[14:16]),int(f[17:19]))

def format_file_size_for_display(file_size):
    KILOBYTE_FACTOR = 1024.0
    MEGABYTE_FACTOR = 1024.0 ** 2
    GIGABYTE_FACTOR = 1024.0 ** 3

    if file_size < KILOBYTE_FACTOR:
        return _('%u bytes') % file_size
    if file_size < MEGABYTE_FACTOR:
        return _('%.1f KB') % (file_size/KILOBYTE_FACTOR)
    if file_size < GIGABYTE_FACTOR:
        return _('%.1f MB') % (file_size/MEGABYTE_FACTOR)
    return _('%.1f GB') % (file_size/GIGABYTE_FACTOR)


from subprocess import call,Popen
def runWith(l,file,wait=True):
    """ try command in the list 'l' with the file 'file' """
    assert type(file)==unicode
    for c in l:
        try:
            if wait:
                p = call([c,file])
            else:
                Popen([c,file])
        except OSError:
            pass
        else:
            return True
    return False

def caseFreeCmp (a,b):
    if a.upper() < b.upper():
        return -1
    elif a.upper() > b.upper():
        return 1
    else:
        if a < b:
            return 1
        elif a > b:
            return -1
        else:
            return 0

import os,sys
def openURL(url):
    """ open the url in the current browser (don't wait the browser)"""
    if sys.platform[:3].lower() == "win":
        os.startfile(url)
    else:
        runWith(["gnome-open","mozilla-firefox","firefox","konqueror","epiphany","galeon"],unicode(url),False)

if __name__ == "__main__":
    #~ print JBrout.home
    #~ JBrout.conf["jo"] = "hack"
    #~ print JBrout.conf["jo"]
    #~ JBrout.conf.save()
    runWith(["StaRT","geany"],u"toto",False)
    pass

