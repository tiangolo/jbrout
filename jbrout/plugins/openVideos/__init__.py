#!/usr/bin/python
# -*- coding: utf-8 -*-

from __main__ import JPlugin,runWith
import os
import glob
from subprocess import Popen

class Plugin(JPlugin):
    """ Plugin to open the videos associated to selected files in totem/vlc/mplayer (linux/windows) """
    __author__ = "fchartier"
    __version__ = "1.0"

    LIST_VIDEO_SUFFIX = [ ".mpg", ".mpeg", ".mp4", ".avi", ".wma", ".mov" ] 

    @JPlugin.Entry.PhotosProcess( _("Open associated videos"), order=2001, alter=False )
    def openAssociatedVideos(self,listOfPhotoNodes):
        """Open associated video of selected files"""
        listVideos = []
        
        for picture in listOfPhotoNodes:
            #self.showProgress(listOfPhotoNodes.index(picture), len(listOfPhotoNodes), _("Searching videos") )
            
            picfile=picture.file
            # remove extension
            picshort = picfile[0:picfile.rfind(".")]
            #picshort = picfile[0:len(picfile)-4]
            print picfile + " => " + picshort

            # Search files starting like picture, but with all extensions
            listFic = glob.glob(picshort + "*")
            for fic in listFic:
                suffix=fic[fic.rfind("."):].lower()
                if suffix in self.LIST_VIDEO_SUFFIX:
                    print "Found video: " + fic
                    listVideos.append(fic)
            #self.showProgress()

        self.openVideoList(listVideos)
        return False    # no visual modif
    
    @JPlugin.Entry.AlbumProcess( _("Open associated videos"), order=2001, alter=False )
    def openFolderVideos(self,node):
        """Open videos in selected folder"""
        listVideos = []

        print "Searching videos in [" + node.file + "]"
        # Search files in folder
        listFic = os.listdir(node.file)
        listFic.sort()
        for fic in listFic:
            suffix=fic[fic.rfind("."):].lower()
            #print "suffix:" + suffix
            if suffix in self.LIST_VIDEO_SUFFIX:
                videoFic = os.path.join(node.file, fic)
                print "Found video: " + videoFic
                listVideos.append(videoFic)
        
        self.openVideoList(listVideos)
        return False    # no visual modif

    def openVideoList(self, list):
        """ try opening the list of videos with different players """
        if len(list) == 0:
            self.MessageBox( _("No video was found"))
        else:
            self.runListWith(["totem", "vlc", "mplayer"], list)
        

    def runListWith(self, listCmd, listArgs):
        """ try command in the list 'listCmd' with the list listArgs """
        for c in listCmd:
            try:
                execList = [c]
                for a in listArgs:
                    execList.append(unicode(a))
                Popen(execList)
                
            except OSError:
                pass
            else:
                return True
        return False