#!/usr/bin/python
# -*- coding: utf-8 -*-

from __main__ import JPlugin
import os


class ExportConf(object):
    __attrs={
        "height": 500,
        "width": 800,
        "sourceFolder": os.path.dirname(__file__),  # FS,HG,PW,FR or SM or FT
        "delete": "0", # Delete source files after download, 0=False, 1=True
        "autoRotate": "0", # Auto rotate photos after download, 0=False, 1=True
        "preview": "0", # Preview photos while downloading, 0=False, 1=True
        "autoComment": "", # Photo auto comment
        "nameFormat": "{o}", #Photo naming format (default origional file name")
        "jobCode": "",
        "promptJobCode": "0",# Prompt for job code, 0=False, 1=True
        "autoTag": [] # List of tags to automaticaly add to photos on import
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
            raise "key doesn't exist : "+key

    def __setitem__(self,key,value):
        if key not in ["__conf","__attrs"]:
            if key in self.__attrs:
                self.__attrs[key] = value
            else:
                raise "key doesn't exist : "+key

    def save(self):
        for i in self.__attrs.keys():
            self.__conf[i] = self.__attrs[i]
        pass

class Plugin(JPlugin):
    """ Download Photos from Camera/Card to the selected album """
    __author__ = "Rob Wallace"
    __version__ = "0.0.1"

    def albumEntries(self,l):
        return [ (900,_("Download"),True,self.download), ]

    def download(self,nodeFolder):
        from download import WinDownload,WinDownloadExecute

        ec=ExportConf(self.conf)

        winDownload = WinDownload(ec, nodeFolder)
        execute = winDownload.loop()[0]
        ec.save()
        if execute:
            winExecute = WinDownloadExecute(ec,winDownload.getToDownload())
            winExecute.loop()
            return True
        else:
            return False
