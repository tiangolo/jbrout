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
import re, sys, thread, shutil, stat, string

from libs.dict4ini import DictIni
from plugins import JPlugins
import os, os.path
from db import DBPhotos,DBTags
import socket
import glib

# ============================================================================================
class Conf(object):
# ============================================================================================

    def __init__(self,file):
        self.__ini = DictIni(file)

        # to recreate the new INI file, bases on dict4ini
        if not self.__ini.has_key("jBrout"):
            # clear old values, to restart a new one
            self.__ini.clear()

    def __getitem__(self,n):
        """ main conf get """
        return self.__ini.jBrout[n]

    def has_key(self,n):
        """ main conf test """
        return self.__ini.jBrout.has_key(n)

    def __setitem__(self,n,v):
        """ main conf set """
        self.__ini.jBrout[n]=v

    def getSubConf(self,n):
        """ sub conf get """
        return self.__ini[n]

    def save(self):
        self.__ini.save()

class JBrout:
    #~ __lockFile = "jbrout.lock"
    __lockSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #~ @staticmethod
    #~ def lockOn():
        #~ """ create the lock file, return True if it can"""
        #~ file = os.path.join(JBrout.getHomeDir("jbrout"),JBrout.__lockFile)
        #~ if os.path.isfile(file):
            #~ print file
            #~ return False
        #~ else:
            #~ open(file,"w").write("")
            #~ return True

    #~ @staticmethod
    #~ def lockOff():
        #~ """ delete the lockfile """
        #~ file = os.path.join(JBrout.getHomeDir("jbrout"),JBrout.__lockFile)
        #~ if os.path.isfile(file):
            #~ os.unlink(file)


    @classmethod
    def isRunning(cls,p=64738): # "sys 64738" nostaligc ;-)
        try:
            JBrout.__lockSocket.bind(("localhost", p))
            JBrout.__lockSocket.listen(1)
            return False
        except:
            return True

    @staticmethod
    def getHomeDir(mkdir=None):
        """
        Return the "Home dir" of the system (if it exists), or None
        (if mkdir is set : it will create a subFolder "mkdir" if the path exist,
        and will append to it (the newfolder can begins with a "." or not))
        """
        maskDir=False
        glibConfDir = glib.get_user_data_dir()

        # Find legacy home dir
        #windows NT,2k,XP,etc.
        if (os.name == "nt") and ("APPDATA" in os.environ):
            home = os.environ['APPDATA']
            if not os.path.isdir(home):
                raise OSError("Missing %APPDATA% directory")
            maskDir=False
        elif ("XDG_CONFIG_HOME" in os.environ):
            home = os.environ['XDG_CONFIG_HOME']
            if not os.path.isdir(home):
                raise OSError("Missing $XDG_CONFIG_HOME directory")
            maskDir = False
        elif (os.path.expanduser("~") != "~"):
            home = os.path.expanduser("~")
            if not os.path.isdir(home):
                raise OSError("Missing ~ directory. Weird.")
            maskDir=True
        elif ("HOME" in os.environ):
            home = os.environ["HOME"]
            if os.path.isdir(home):
                conf = os.path.join(home,".config")
                if os.path.isdir(conf):
                    home = conf
                    maskDir=False
                else:
                    # keep home
                    maskDir=True
            else:
                raise OSError("Missing $HOME directory.")
        else:
            #What os are people using?
            home = None

        if glibConfDir:
            if mkdir:
                if maskDir:
                    newDir = "." + mkdir
                else:
                    newDir = mkdir

                confDir = os.path.join(glibConfDir, mkdir)
                oldConfDir = os.path.join(home, newDir)
                if not os.path.isdir(confDir):
                    # copy old data if we have them
                    if os.path.isdir(oldConfDir):
                        print "Copying %s to %s" % (oldConfDir, confDir)
                        shutil.copytree(oldConfDir, confDir,
                            symlinks=True)
                    else:
                        print "Creating new dir %s" % confDir
                        os.mkdir(confDir)

        return confDir


    @staticmethod
    def getConfFile(name):
        if os.path.isfile(name):
            # the file exists in the local "./"
            # so we use it first
            return name
        else:
            # the file doesn't exist in the local "./"
            # it must exist in the "jbrout" config dir
            home = JBrout.getHomeDir("jbrout")
            if home:
                # there is a "jbrout" config dir
                # the file must be present/created in this dir
                return os.path.join(home,name)
            else:
                # there is not a "jbrout" config dir
                # the file must be present/created in this local "./"
                return name
    @staticmethod
    def init(modify):

        JBrout.modify = modify


        # initialisation de ".db"
        #======================================================================
        JBrout.db = DBPhotos( JBrout.getConfFile("db.xml") )

        # initialisation de ".tags"
        #======================================================================
        JBrout.tags = DBTags( JBrout.getConfFile("tags.xml") )

        # initialisation de ".conf"
        #======================================================================
        JBrout.conf = Conf( JBrout.getConfFile("jbrout.conf") )

        # initialisation de ".conf"
        #======================================================================
        JBrout.toolsFile = JBrout.getConfFile("tools.txt")

        # initialisation de ".plugins"
        #======================================================================
        jbroutHomePath = JBrout.getHomeDir("jbrout")

        JBrout.plugins = JPlugins(jbroutHomePath,JBrout.conf)

if __name__ == "__main__":
    #~ doc = lxml.etree.fromstring("<foo>fd<bar>kk</bar>oi</foo>")
    #~ r = doc.xpath('/foo/bar')
    #~ print len(r)
    #~ print r[0].tag
    #~ print doc.tag
    #~ print doc.text

    db = DBPhotos()
    #db.clearBasket()
    #~ db.add("/home/manatlan/Desktop/tests")

    #~ print db.cpt()
    #~ db.save()
    #~ print db.getRootBasket()

    #~ db=DBTags()
    #~ r=db.getRootTag()

    #~ for i in r.getTags():
        #~ print type(i),i.name
    #~ for i in r.getCatgs():
        #~ print type(i),i.name

    #~ ln = db.select("//photo")
    #~ for i in ln:
        #~ print i.name, i.file
    #~ print ln[0].getParent()

