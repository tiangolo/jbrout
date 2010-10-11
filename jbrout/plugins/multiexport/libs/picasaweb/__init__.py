#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
=========
PicasaWeb
=========
Implementation of PycasaWeb using gdata api, manatlan (manatlan#gmail.com)
work with py2.4 + ElementTree or py2.5 (ElementTree base lib)

Based on the script "picasa_upload.py" by Marcin Sochacki (wanted#linux.gda.pl)
  and Ulrik Stervbo (ulrik.stervbo#gmail.com)
  http://wanted.eu.org/en/computers/linux/uploading_photos_to_picasaweb    (en)

need ElementTree (py2.5 included battery)
"""
import sys,os
sys.path.append(os.path.dirname(__file__))  # bad things ;-)

import atom
import gdata.service
import gdata
import gdata.base

class PicasaWeb(gdata.service.GDataService):
    def __init__(self,username,password):
        gdata.service.GDataService.__init__(self)
        self.email = username
        self.password = password
        self.service = 'lh2'
        self.source = 'GDataService upload script'

        try:
            self.ProgrammaticLogin()
        except gdata.service.CaptchaRequired:
            raise Exception('Required Captcha')
        except gdata.service.BadAuthentication:
            raise Exception('Bad Authentication')
        except gdata.service.Error:
            raise Exception('Login Error')

    def getAlbums(self):
        try:
            albums = self.GetFeed(
                    'http://picasaweb.google.com/data/feed/api/user/'
                    + self.email
                    + '?kind=album&access=all'
                    )
            return [PicasaAlbum(self,a) for a in albums.entry]
        except:
            raise Exception("GetAlbums() error ?!")


    def createAlbum(self,folderName,public=True):
        gd_entry = gdata.GDataEntry()
        gd_entry.title = atom.Title(text=folderName)
        gd_entry.category.append(atom.Category(
            scheme='http://schemas.google.com/g/2005#kind',
            term='http://schemas.google.com/photos/2007#album'))

        rights = public and "public" or "private"
        gd_entry.rights = atom.Rights(text=rights)

        ext_rights = atom.ExtensionElement( tag='access',
            namespace='http://schemas.google.com/photos/2007')
        ext_rights.text = rights
        gd_entry.extension_elements.append(ext_rights)

        album_entry = self.Post(gd_entry,
            'http://picasaweb.google.com/data/feed/api/user/' + self.email)

        return PicasaAlbum(self,album_entry)

class PicasaAlbum(object):
    name = property(lambda self:self.__ae.title.text)

    def __init__(self,gd,album_entry):
        self.__gd=gd
        self.__ae=album_entry

    def uploadPhoto(self,file, description=""):
        ms = gdata.MediaSource()

        try:
            ms.setFile(file, 'image/jpeg')
            metadata_entry = gdata.GDataEntry()
            name = os.path.basename(file)
            metadata_entry.title = atom.Title(text=name)
            metadata_entry.summary = atom.Summary(text=description)
            metadata_entry.category.append(atom.Category(scheme = 'http://schemas.google.com/g/2005#kind', term = 'http://schemas.google.com/photos/2007#photo'))

            link = self.__ae.link[0].href # self.__ae.GetFeedLink().href on created album
            media_entry = self.__gd.Post(metadata_entry,link, media_source = ms)
            return True
        except gdata.service.RequestError:
            return False



if __name__ == '__main__':
    pw=PicasaWeb("manatlan@gmail.com",open("/home/manatlan/.pass","r").read())
    #~ for a in pw.getAlbums():
        #~ if a.name=="Blue Photos":
            #~ print a.uploadPhoto("p20070608_175721.jpg")
    a=pw.createAlbum("Aefff3")
    print a.uploadPhoto("p20070608_175721.jpg")
