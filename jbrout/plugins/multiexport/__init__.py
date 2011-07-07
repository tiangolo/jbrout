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
import tempfile, ftplib

from __main__ import JPlugin

# For CA (Compressed Archive)
import tarfile
import zipfile

# For HG (Html Gallery)
from lxml.etree import Element,ElementTree,parse,XSLT

# for FR (flickr)
from libs.flickr import FlickrUploader

# for PW (picasaweb)
#from libs.pycasaweb import PycasaWeb
try:
    from libs.picasaweb import *
except ImportError,m:
    print "*WARNING* Python Import Error :",m
    PicasaWeb = lambda *a : None


# for SM (send mail)
from libs.mailer import sendMail

# for common
import os,time,shutil

from jbrout.common import cd2rd
from crypt import uncrypt

class ExportConf(object):
    __attrs={
        "type":"FS",  # CA, FS,HG,PW,FR or SM or FT

        # Compressed Archive conf
        # ===================
        "CA.folder": "",

        "CA.type":'zip',  # tar. tbz, tgz or zip
        "CA.resize":0,    # 0:NO, 1:PERCENT, 2:MAXSIDE
        "CA.percent":80,
        "CA.maxside":1600,
        "CA.quality":80,
        "CA.order":0,
        "CA.metadata":0,  # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all


        # FileSystem conf
        # ===================
        "FS.folder": "",

        "FS.resize":0,    # 0:NO, 1:PERCENT, 2:MAXSIDE
        "FS.percent":80,
        "FS.maxside":1600,
        "FS.quality":80,
        "FS.order":0,
        "FS.metadata":0,  # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all


        # Html Gallery conf
        # ===================
        "HG.folder": "",
        "HG.template": 0,

        "HG.resize":0,    # 0:NO, 1:PERCENT, 2:MAXSIDE
        "HG.percent":80,
        "HG.maxside":1600,
        "HG.quality":80,
        "HG.order":0,
        "HG.metadata":0,  # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all


        # Pycasa conf
        # ===================
        "PW.login": "",
        "PW.password": "",
        "PW.privacy": 0,       # 0 or 1

        "PW.resize":0,    # 0:NO, 1:PERCENT, 2:MAXSIDE
        "PW.percent":80,
        "PW.maxside":1600,
        "PW.quality":80,
        "PW.order":0,
        "PW.metadata":0,  # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all

        # flickr conf
        # ===================
        "FR.public": 0,
        "FR.friends": 0,
        "FR.family": 0,
        "FR.same_privacy":0,       # 0 or 1

        "FR.resize":0,    # 0:NO, 1:PERCENT, 2:MAXSIDE
        "FR.percent":80,
        "FR.maxside":1600,
        "FR.quality":80,
        "FR.order":0,
        "FR.metadata":0,  # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all

        # Mail conf
        # ===================
        "SM.smtp":"",
        "SM.auth":0,
        "SM.username":"",
        "SM.password":"",
        "SM.security":0,
        "SM.port":25,
        "SM.to":"",
        "SM.from":"",
        "SM.subject":"",
        "SM.message":"",

        "SM.resize":0,    # 0:NO, 1:PERCENT, 2:MAXSIDE
        "SM.percent":80,
        "SM.maxside":1600,
        "SM.quality":80,
        "SM.order":0,
        "SM.metadata":0,  # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all

        # FTP conf
        # ===================
        "FT.ftp":"",
        "FT.login":"",
        "FT.password":"",
        "FT.path":"",

        "FT.resize":0,    # 0:NO, 1:PERCENT, 2:MAXSIDE
        "FT.percent":80,
        "FT.maxside":1600,
        "FT.quality":80,
        "FT.order":0,
        "FT.metadata":0,  # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all

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

class PicasaException(Exception): pass

class Plugin(JPlugin):
    """ Multi export plugin"""

    __author__ = "manatlan"
    __version__ = "0.10"

    #def menuEntries(self,l):
    #    return [(3000,_("Export to"),False,self.export,None)]

    @JPlugin.Entry.PhotosProcess( _("Export to"), order=3000, alter=False )
    def export(self,list):
        from winexport import Windowexport

        ec=ExportConf(self.conf)

        pathXsl=os.path.join(os.path.dirname(__file__),"xsl")
        XSL = [i for i in os.listdir(pathXsl) if i[0]!="."]

        window_export = Windowexport(ec,"%d photos" % len(list),list,XSL)

        type=window_export.loop()[0]
        if type:
            # so save conf back to conf object !
            ec.save()

            # CONF WAS SAVED in the window
            # so the results are in ec[type+".*"]

            # get the commons
            resize=ec[type+".resize"]
            percent=ec[type+".percent"]
            quality=ec[type+".quality"]
            maxside=ec[type+".maxside"]
            order=ec[type+".order"]
            metadata=ec[type+".metadata"]

            delCom=False
            delTags=False
            keepInfo=True
            if metadata == 4:
                keepInfo = False
            elif metadata == 3:
                delCom = True
                delTags = True
            elif metadata == 2:
                delTags = True
            elif metadata == 1:
                delCom = True

            # 0:Keep, 1:Del comment, 2:Del tags, 3:Del comment & tags, 4:Del all

            if type == "CA":
                msg = _("Export to archive")
                #==================================================================
                path = ec["CA.folder"]
                if os.path.isdir(path):
                    destination=unicode(tempfile.mkdtemp(".tmp","jbrout"))
                    print "Opening Archive"
                    if ec["CA.type"] in ['tar','tbz','tgz']:
                        if ec["CA.type"] == 'tar':
                            archMode = 'w'
                        elif ec["CA.type"] == 'tbz':
                            archMode = 'w:bz2'
                        else:
                            archMode = 'w:gz'
                        archive = tarfile.open(os.path.join(path, ("Jbrout " + time.strftime("%Y-%m-%d, %H-%M-%S") + '.' + ec["CA.type"])), archMode)
                    else:
                        archive = zipfile.ZipFile(os.path.join(path, ("Jbrout " + time.strftime("%Y-%m-%d, %H-%M-%S") + '.zip')), "w")
                else:
                    self.MessageBox(_("The selected path doesn't exists !"))
                    return False

            elif type == "FS":
                msg = _("Export to folder")
                #==================================================================
                path = ec["FS.folder"]
                if os.path.isdir(path):
                    destination = unicode( path + "/Jbrout " + time.strftime("%Y-%m-%d, %H-%M-%S") )
                else:
                    self.MessageBox(_("The selected path doesn't exists !"))
                    return False

            elif type == "HG":
                msg = _("Export as a Html Gallery")
                #==================================================================
                path = ec["HG.folder"]
                if os.path.isdir(path):
                    destg = unicode( path + "/Html " + time.strftime("%Y-%m-%d, %H-%M-%S") )

                    # prepare the destination
                    os.mkdir(destg)

                    destination = os.path.join(destg,"img")
                    dirThumbs = os.path.join(destg,"thumbs")

                    if not os.path.isdir(destination):
                        os.mkdir( destination )
                    if not os.path.isdir(dirThumbs):
                        os.mkdir( dirThumbs )

                    # and prepare le xml
                    nodeAlbum = Element("export")

                else:
                    self.MessageBox(_("The selected path doesn't exists !"))
                    return False

            elif type == "PW":
                msg = _("Export to PicasaWeb")
                #==================================================================
                destination=unicode(tempfile.mkdtemp(".tmp","jbrout"))

                try:
                    picasa = PicasaWeb(ec["PW.login"],uncrypt(ec["PW.password"]))
                    if picasa:
                        album=picasa.createAlbum("Jbrout " + time.strftime("%Y-%m-%d, %H-%M-%S"),public=(ec["PW.privacy"]==0))
                    else:
                        raise PicasaException(_("Sorry, you can't upload to picasaweb (python import error)"))
                except Exception,err:
                    self.MessageBox(_("Upload error : ")+str(err))
                    return False


            elif type == "FR":
                msg = _("Export to Flickr")
                #==================================================================
                destination=unicode(tempfile.mkdtemp(".tmp","jbrout"))
                flickr_uploader = FlickrUploader(self.conf,self.validateWin)

            elif type == "SM":
                msg = _("Export to Email")
                #==================================================================
                destination=unicode(tempfile.mkdtemp(".tmp","jbrout"))
                filesToSend=[]

            elif type == "FT":
                msg = _("Export to FTP")
                #==================================================================
                destination=unicode(tempfile.mkdtemp(".tmp","jbrout"))

                try:
                    ftp = ftplib.FTP(ec["FT.ftp"],ec["FT.login"],uncrypt(ec["FT.password"]))
                    try:
                        ftp.cwd(ec["FT.path"])
                    except:
                        ftp.mkd(ec["FT.path"])
                        ftp.cwd(ec["FT.path"])
                except Exception,err:
                    self.MessageBox(_("FTP error : ")+str(err))
                    return False

            if order == 1:  # olders first
                list.reverse()

            try:
                try:

                    if not os.path.isdir(destination): # if it was not create before
                        os.mkdir(destination)

                    for photo in list:
                        self.showProgress( list.index(photo), len(list) , msg )

                        if resize == 0: # no resize
                            file = photo.copyTo(destination, keepInfo=keepInfo, delCom=delCom, delTags=delTags)
                        elif resize == 1: # resize
                            file = photo.copyTo(destination,resize=( float(percent/100),quality))
                        elif resize == 2: # max side
                            file = photo.copyTo(destination,resize=( int(maxside),quality))

                        if type == "CA":
                            # TODO: add file to archive
                            print "Adding file '%s'" % file
                            if ec["CA.type"] in ['tar','tbz','tgz']:
                                archive.add(file, os.path.basename(file).encode("utf_8"))
                            else:
                                archive.write(file, os.path.basename(file).encode("utf_8"))
                        elif type == "FS":
                            # nothing to do more
                            pass
                        elif type == "HG":
                            # create a img node
                            nodeImg = Element("img")

                            # and create the thumb
                            dest = os.path.join( dirThumbs, photo.name)
                            pb = photo.getThumb()
                            pb.save(dest, "jpeg", {"quality":"80"})

                            # and fill the node
                            nodeImg.set("src","img/"+photo.name)
                            nodeImg.set("mini","thumbs/"+photo.name)

                            nodeImg.set("albumComment",photo.getParent().comment)
                            nodeImg.set("album",photo.getParent().name)
                            nodeImg.set("comment",photo.comment)
                            nodeImg.set("tags",", ".join(photo.tags))
                            nodeImg.set("hdate",cd2rd(photo.date))  # human date ;-)
                            nodeImg.set("date",photo.date)

                            # and add it to the album
                            nodeAlbum.append(nodeImg)

                        elif type == "PW":
                            album.uploadPhoto(file,photo.comment) # (pycasaweb)
                            #album.uploadPhoto(file)
                        elif type == "FR":
                            err=flickr_uploader.upload(file,photo.comment,photo.tags,window_export.getPrivacyFR(photo))
                            if err: raise Exception(err)
                        elif type == "SM":
                            filesToSend.append(file)
                        elif type == "FT":
                            fid = open(file,'rb')
                            ftp.storbinary('STOR '+os.path.basename(file), fid)

                    # and close the work
                    if type == "CA":
                        # TODO: close archive
                        print "Closing archive"
                        archive.close()
                    elif type == "HG":
                        # finish the work for the html galleyr
                        xml_doc = ElementTree(nodeAlbum)

                        # save a copy of the xml used file for info (can be deleted)
                        fid = open(destg+"/photos.xml","w")
                        xml_doc.write(fid)
                        fid.close()

                        # applys the xslt transformation
                        xslt_doc = parse( os.path.join(pathXsl, XSL[ ec["HG.template"] ]) )
                        nodeParams = xslt_doc.xpath("//xsl:param",namespaces={"xsl":"http://www.w3.org/1999/XSL/Transform"})

                        p=1
                        while True:

                            # the worst way to pass a param ;-)
                            nodeParams[0].text=str(p)
                            #~ nodeParams[1].text="8"

                            style = XSLT(xslt_doc)

                            result = style.apply( xml_doc)
                            page = style.tostring(result)
                            if "body" in page:
                                open(destg+"/page%d.html" % p,"w").write(page)
                                p+=1
                            else:
                                break;
                    elif type=="SM":
                        fro = ec["SM.from"]

                        if "," in ec["SM.to"]:
                            to = ec["SM.to"].split(",")
                        elif ";" in ec["SM.to"]:
                            to = ec["SM.to"].split(";")
                        else:
                            to = [ ec["SM.to"], ]

                        text = ec["SM.message"]
                        subject = ec["SM.subject"]
                        server = ec["SM.smtp"]
                        secTypes = ['none', 'ssl', 'start tls']
                        security = secTypes[int(ec["SM.security"])]
                        port = int(ec["SM.port"])
                        auth = bool(ec["SM.auth"])
                        username = ec["SM.username"].encode("utf_8")
                        password = uncrypt(ec["SM.password"]).encode("utf_8")

                        sendMail(fro, to, subject, text, filesToSend,server,
                        security, port, auth, username, password)
                    elif type=="FT":
                        ftp.quit()

                    if destination.endswith(".tmp"):    # it's a temp dir
                        shutil.rmtree(destination)

                except Exception,err:
                    self.MessageBox(_("Plugin error : ")+str(err))


            finally:
                self.showProgress()


            # TODO : delete temp album if here
            # TODO : order is not usefull for FS


        return False

    def validateWin(self,url):
        msg=_("""You need to give jBrout permission to upload your photos to Flickr.
This is done via a Flickr-session in your web browser to which you are logged in.

If you press the OK-button, jBrout will open your browser.
When done, return to jBrout to finish the authentication procedure.""")
        self.MessageBox(msg, _("Export to Flickr"))
        self.openURL("http://flickr.com/services/auth/?"+url)
        self.MessageBox(_("jBrout should now open a web broser. When you're done there, return to this message box and click the OK-button."),_("Export to Flickr"))
        return True
