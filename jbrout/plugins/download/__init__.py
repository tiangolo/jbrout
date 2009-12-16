# -*- coding: UTF-8 -*-
##
##    Copyright (C) 2007 Rob Wallace rob[at]wallace(dot)gen(dot)nz
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
import os


class ExportConf(object):
    __attrs={
        "height": 500,
        "width": 800,
        "sourceFolder": os.path.dirname(__file__),  # FS,HG,PW,FR or SM or FT
        "delete": "0", # Delete source files after download, 0=False, 1=True
        "autoRotate": "0", # Auto rotate photos after download, 0=False, 1=True
        "copyOther": "0", # Copy other files with the same name as the jpeg
        "autoComment": "", # Photo auto comment
        "nameFormat": "{o}", #Photo naming format (default origional file name")
        "jobCode": "",
        "promptJobCode": "0",# Prompt for job code, 0=False, 1=True
        "autoTag": [], # List of tags to automaticaly add to photos on import
        "dcraw": "0", # Enable conversion of Raw files
        "dcrawCopyMetaData": "0", # Enable copying of metadata 
        "dcrawCopyRaw": "0" # Copy the origional file when converting RAW files
    }
    def __init__(self,conf):
        self.__conf = conf

        for i in self.__attrs.keys():
            try:
                self.__attrs[i] = self.__conf[i] or self.__attrs[i]
            except:
                pass

    def __getitem__(self,key):
        if key in self.__attrs:
            return self.__attrs[key]
        else:
            raise Exception("key doesn't exist : "+key)

    def __setitem__(self,key,value):
        if key not in ["__conf","__attrs"]:
            if key in self.__attrs:
                self.__attrs[key] = value
            else:
                raise Exception("key doesn't exist : "+key)

    def save(self):
        for i in self.__attrs.keys():
            self.__conf[i] = self.__attrs[i]
        pass

class Plugin(JPlugin):
    """ Download Photos from Camera/Card to the selected album """
    __author__ = "Rob Wallace"
    __version__ = "0.0.1"

    #def albumEntries(self,l):
    #    return [ (900,_("Download"),True,self.download), ]

    @JPlugin.Entry.AlbumProcess( _("Download"),order=900 )
    def download(self,nodeFolder):
        from download import WinDownload,WinDownloadExecute

        ec=ExportConf(self.conf)

        winDownload = WinDownload(ec, nodeFolder)
        execute = winDownload.loop()[0]
        ec.save()
        if execute:
            winExecute = WinDownloadExecute(ec,winDownload.getToDownload(),
                winDownload.srcFolder, winDownload.destFolder)
            winExecute.loop()
            return True
        else:
            return False
