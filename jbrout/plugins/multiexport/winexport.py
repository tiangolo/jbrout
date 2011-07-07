# -*- coding: UTF-8 -*-
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
import os
import gtk
import time
from jbrout.commongtk import PictureSelector
from crypt import crypt,uncrypt

from __main__ import GladeApp # no "libs.gladeapp", because there is a libs dir here ;-(

def chooseFolder(t):
    dialog = gtk.FileChooserDialog (_("Select the destination"),
         None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
         (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,
          gtk.RESPONSE_OK))
    dialog.set_default_response (gtk.RESPONSE_OK)

    # preselect the previous mount point
    dialog.select_filename (t)

    response = dialog.run ()
    if response == gtk.RESPONSE_OK:
        ret = dialog.get_filename()
    else:
        ret = None

    dialog.destroy()
    return ret

class Windowexport(GladeApp):

    glade=os.path.join(os.path.dirname(__file__), 'winexport.glade')

    def init(self,conf,titre,photoList,templateList):
        self.main_widget.set_modal(True)
        #~ self.main_widget.set_keep_above(True)
        self.main_widget.set_position(gtk.WIN_POS_CENTER)
        self.lblTitre.set_text(titre)

        cell = gtk.CellRendererText()
        self.cbTemplate.pack_start(cell, True)
        self.cbTemplate.add_attribute(cell, 'text',0)

        m=gtk.ListStore( str)
        m.clear()
        for i in templateList:
            m.append( [i,] )
        self.cbTemplate.set_model(m)

        self.cbTypeA.pack_start(cell, True)
        self.cbTypeA.add_attribute(cell, 'text',0)

        am=gtk.ListStore( str)
        am.clear()
        am.append( ['Uncompressed tar (.tar)',] )
        am.append( ['Tar bzip2 (.tbz)',] )
        am.append( ['Tar gzip (.tgz)',] )
        am.append( ['Zip (.zip)',] )

        self.cbTypeA.set_model(am)


        self.photoList = photoList

        self.privacyFR = {}

        # Create the Flickr thumbnail selector
        self.psThumbSelectFR = PictureSelector(self.photoList)
        self.psThumbSelectFR.connect("value_changed", self.on_psThumbSelectFR_value_changed)
        self.tableFlickr.attach(self.psThumbSelectFR, 1, 2, 0, 1)
        self.psThumbSelectFR.show()

        # Configure the smpt port spin button
        self.adjPortSM = gtk.Adjustment(1, 1, 64000, 1,100,100)
        self.spPortSM.set_adjustment(self.adjPortSM)
        self.spPortSM.set_digits(0)

        self.initFromConf(conf)

        self.setPrivacyFR(apply_to_all = True)

        self.on_nbExport_switch_page(None)  #simulate tab changed


    def initFromConf(self,conf):
        self.__conf = conf

        if conf["type"] == "FS":
            self.nbExport.set_current_page(0)
        elif conf["type"] == "HG":
            self.nbExport.set_current_page(1)
        elif conf["type"] == "PW":
            self.nbExport.set_current_page(2)
        elif conf["type"] == "FR":
            self.nbExport.set_current_page(3)
        elif conf["type"] == "SM":
            self.nbExport.set_current_page(4)
        elif conf["type"] == "FT":
            self.nbExport.set_current_page(5)
        elif conf["type"] == "CA":
            self.nbExport.set_current_page(6)
        else:
            print "bad export type in conf : %s" % str(conf["type"])
            self.nbExport.set_current_page(0)

        self.tbFolderA.set_text( conf["CA.folder"] )
        if conf["CA.type"] == "tar":
            self.cbTypeA.set_active(0)
        elif conf["CA.type"] == "tbz":
            self.cbTypeA.set_active(1)
        elif conf["CA.type"] == "tgz":
            self.cbTypeA.set_active(2)
        else: # Use zip as the default/failsafe
            self.cbTypeA.set_active(3)

        self.tbFolderF.set_text( conf["FS.folder"] )

        self.tbFolderH.set_text( conf["HG.folder"] )
        self.cbTemplate.set_active( conf["HG.template"] )

        self.tbLoginPW.set_text( conf["PW.login"] )
        self.tbPasswordPW.set_text( uncrypt(conf["PW.password"]) )
        if (bool(conf["PW.privacy"])): self.rbPrivatePW.set_active(1)
        else: self.rbPublicPW.set_active(1)

        if (bool(conf["FR.public"])): self.rbPublicFR.set_active(1)
        else: self.rbPrivateFR.set_active(1)
        if (bool(conf["FR.friends"])): self.cbFriendsFR.set_active(1)
        else: self.cbFriendsFR.set_active(0)
        if (bool(conf["FR.family"])): self.cbFamilyFR.set_active(1)
        else: self.cbFamilyFR.set_active(0)
        if (bool(conf["FR.same_privacy"])): self.cbSelectAllFR.set_active(1)
        else: self.cbSelectAllFR.set_active(0)

        self.tbSmtp.set_text(conf["SM.smtp"])
        self.spPortSM.set_value(int(conf["SM.port"]))
        if (bool(conf["SM.auth"])):
            self.cbAuthSM.set_active(True)
            self.tbUserSM.set_sensitive(True)
            self.tbPasswordSM.set_sensitive(True)
        else:
            self.cbAuthSM.set_active(False)
            self.tbUserSM.set_sensitive(False)
            self.tbPasswordSM.set_sensitive(False)
        self.tbUserSM.set_text(conf["SM.username"])
        self.tbPasswordSM.set_text(uncrypt(conf["SM.password"]))
        self.cbSecurity.set_active(int(conf["SM.security"]))
        self.tbTo.set_text( conf["SM.to"] )
        self.tbFrom.set_text( conf["SM.from"] )
        self.tbSubject.set_text( conf["SM.subject"] )
        self.tbMessage.set_text( conf["SM.message"] )

        self.tbFtp.set_text( conf["FT.ftp"] )
        self.tbLoginFT.set_text( conf["FT.login"] )
        self.tbPasswordFT.set_text( uncrypt(conf["FT.password"]) )
        self.tbPath.set_text( conf["FT.path"] )

    def getExportType(self):
        return ["FS","HG","PW","FR","SM","FT","CA"][self.nbExport.get_current_page()]

    def getResizeType(self):
        if self.rbNoResize.get_active():
            return 0
        elif self.rbResize.get_active():
            return 1
        elif self.rbMaxSide.get_active():
            return 2

    def getServiceType(self):
        return ["picasaweb","flickr"][self.cbWebService.get_active()]

    def on_winExport_delete_event(self,*args):
        self.quit(False)

    def on_btnCancel_clicked(self,*args):
        self.quit(False)

    def on_btnOk_clicked(self,*args):
        type = self.getExportType() # self.__conf["type"]

        # Put back the conf which is desired
        self.__conf["type"] = type

        if type == "CA":
            self.__conf["CA.folder"]=self.tbFolderA.get_text()
            types = ['tar','tbz','tgz','zip']
            self.__conf["CA.type"]=types[self.cbTypeA.get_active()]
        elif type == "FS":
            self.__conf["FS.folder"]=self.tbFolderF.get_text()
        elif type == "HG":
            self.__conf["HG.folder"]=self.tbFolderH.get_text()
            self.__conf["HG.template"]=self.cbTemplate.get_active()
        elif type == "PW":
            self.__conf["PW.login"]=self.tbLoginPW.get_text(  )
            self.__conf["PW.password"]=crypt(self.tbPasswordPW.get_text(  ))
            self.__conf["PW.privacy"]=int(self.rbPrivatePW.get_active())
        elif type == "FR":
            self.__conf["FR.public"]=int(self.rbPublicFR.get_active())
            self.__conf["FR.friends"]=int(self.cbFriendsFR.get_active())
            self.__conf["FR.family"]=int(self.cbFamilyFR.get_active())
        elif type == "SM":
            self.__conf["SM.smtp"]=self.tbSmtp.get_text(  )
            self.__conf["SM.port"]=self.spPortSM.get_value_as_int()
            self.__conf["SM.auth"]=int(self.cbAuthSM.get_active())
            if self.cbAuthSM.get_active():
                self.__conf["SM.username"]=self.tbUserSM.get_text()
                self.__conf["SM.password"]=crypt(self.tbPasswordSM.get_text())
            self.__conf["SM.security"]=self.cbSecurity.get_active()
            self.__conf["SM.to"]=self.tbTo.get_text(  )
            self.__conf["SM.from"]=self.tbFrom.get_text(  )
            self.__conf["SM.subject"]=self.tbSubject.get_text(  )
            self.__conf["SM.message"]=self.tbMessage.get_text( )
        elif type == "FT":
            self.__conf["FT.ftp"]=self.tbFtp.get_text(  )
            self.__conf["FT.login"]=self.tbLoginFT.get_text(  )
            self.__conf["FT.password"]=crypt(self.tbPasswordFT.get_text(  ))
            self.__conf["FT.path"]=self.tbPath.get_text( )

        # common
        self.__conf[type+".resize"]= self.getResizeType()
        self.__conf[type+".percent"]=self.hsResize.get_value()
        self.__conf[type+".quality"]=self.hsQuality.get_value()
        self.__conf[type+".maxside"]=self.eMaxSide.get_text()
        self.__conf[type+".order"]=self.cbOrder.get_active()
        self.__conf[type+".metadata"]=self.cbMetadata.get_active()

        self.quit(type)

    def on_resize_toggled(self,*args):
        t=self.getResizeType()
        if t==0:    # no
            self.hsResize.set_sensitive(False)
            #self.tbMaxSide.set_sensitive(False)
            self.cbMaxSide.set_sensitive(False)
            self.hsQuality.set_sensitive(False)
        elif t==1:  # resize
            self.hsResize.set_sensitive(True)
            #self.tbMaxSide.set_sensitive(False)
            self.cbMaxSide.set_sensitive(False)
            self.hsQuality.set_sensitive(True)
        else:       # max side
            self.hsResize.set_sensitive(False)
            #self.tbMaxSide.set_sensitive(True)
            self.cbMaxSide.set_sensitive(True)
            self.hsQuality.set_sensitive(True)

    def on_nbExport_switch_page(self,*args):
        tp = self.getExportType()
        if tp in ["CA","FS","FT"]:
            self.frameOrder.hide()
        else:
            self.frameOrder.show()
        self.rbNoResize.set_active(self.__conf[tp+".resize"]==0)
        self.rbResize.set_active(self.__conf[tp+".resize"]==1)
        self.rbMaxSide.set_active(self.__conf[tp+".resize"]==2)

        self.hsResize.set_value(float(self.__conf[tp+".percent"]))
        self.hsQuality.set_value(float(self.__conf[tp+".quality"]))
        self.eMaxSide.set_text(str(self.__conf[tp+".maxside"]))    #combobox
        self.cbOrder.set_active(int(self.__conf[tp+".order"]))
        self.cbMetadata.set_active(int(self.__conf[tp+".metadata"]))

    def on_btnFolderA_clicked(self,*args):
        ret=chooseFolder(self.tbFolderA.get_text())
        if ret:
            self.tbFolderA.set_text( ret )

    def on_btnFolderH_clicked(self,*args):
        ret=chooseFolder(self.tbFolderH.get_text())
        if ret:
            self.tbFolderH.set_text( ret )

    def on_btnFolderF_clicked(self,*args):
        ret=chooseFolder(self.tbFolderF.get_text())
        if ret:
            self.tbFolderF.set_text( ret )

    # Stuff to make the privacy selections work

    def on_psThumbSelectFR_value_changed(self, widget, *args):
        # This method is called when the value of the Flickr slider changes
        photo_num = widget.getValue()
        is_public, is_friends, is_family = self.privacyFR[self.photoList[photo_num]]
        if (is_public):
            self.rbPublicFR.set_active(True)
        else:
          self.rbPrivateFR.set_active(True)
        self.cbFriendsFR.set_active(is_friends)
        self.cbFamilyFR.set_active(is_family)

    def on_cbSelectAllFR_toggled(self, widget, *args):
        if (self.cbSelectAllFR.get_active()):
            self.psThumbSelectFR.set_sensitive(False)
            self.setPrivacyFR()
        else:
            self.psThumbSelectFR.set_sensitive(True)

    def on_rbPrivateFR_toggled(self, widget, *args):
        # (De)activates the friends and family checkbuttons in the Flickr tab when "public" is (de)selected
        if (widget.get_active()):
            self.cbFriendsFR.set_sensitive(True)
            self.cbFamilyFR.set_sensitive(True)
        else:
            self.cbFriendsFR.set_sensitive(False)
            self.cbFamilyFR.set_sensitive(False)
        self.setPrivacyFR()

    def on_friends_or_family_toggled(self, *args):
        # The checkbuttons for privacy can't call setPrivacy directly,because they give extra arguments which setPrivacy can't use
        self.setPrivacyFR()

    def setPrivacyFR(self, apply_to_all = None):
        # Set the Flickr privacy as indicated in the window to the photos indicated in te window
        # If apply_to_all is given, it overrides the checkbutton (used for initialization)

        if (apply_to_all == None):
            apply_to_all = self.cbSelectAllFR.get_active()

        photo = self.photoList[int(self.psThumbSelectFR.getValue())]
        is_public = self.rbPublicFR.get_active()
        is_friends = self.cbFriendsFR.get_active()
        is_family = self.cbFamilyFR.get_active()
        privacy = [is_public, is_friends, is_family]

        if not (apply_to_all):
            self.privacyFR[photo] = privacy
        else:
            for photo in self.photoList:
                self.privacyFR[photo] = privacy

    def getPrivacyFR(self, photo):
        return self.privacyFR[photo]

    def on_cbAuthSM_toggled(self, widget, *args):
        '''
        Handles toggling of the email authentication check box and
        enables/disables the username and password fields
        '''
        if widget.get_active():
            self.tbUserSM.set_sensitive(True)
            self.tbPasswordSM.set_sensitive(True)
        else:
            self.tbUserSM.set_sensitive(False)
            self.tbPasswordSM.set_sensitive(False)

    def on_cbSecurity_changed(self, widget, *args):
        if widget.get_active() == 1:
            if self.spPortSM.get_value_as_int() == 25:
                self.spPortSM.set_value(465)
        else:
            if self.spPortSM.get_value_as_int() == 465:
                self.spPortSM.set_value(25)

