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
import os
#====
import pygtk
pygtk.require('2.0')
#====

import gtk
from jbrout.commongtk import PictureSelector

from libs.gladeapp import GladeApp
from jbrout import pyexiv

import re

class WinViewExif(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'viewExif.glade')

    #-- WinViewExif.new {
    def init(self, nodes):
        #############################################################
        ## IN in self.nodes:
        ##  - a list of PhotoNodes()
        #############################################################
        self.main_widget.set_modal(True)
        self.main_widget.set_position(gtk.WIN_POS_CENTER)

        self.nodes = nodes

        self.ignoredPattern = '.*0x.*'
        self.ignoredKeys = ['Exif.Photo.MakerNote']

        ## Set-up the Picture selector
        self.selector = PictureSelector(self.nodes)
        self.vbox2.pack_start
        self.vbox2.pack_start(self.selector)
        self.selector.connect("value_changed", self.on_selector_value_changed)
        self.selector.show()

        self.exifList = gtk.ListStore(str, str)

        self.treeview=gtk.TreeView(self.exifList)

        self.tagColumn = gtk.TreeViewColumn(_('Tag'))
        self.valueColumn = gtk.TreeViewColumn(_('Value'))

        self.treeview.append_column(self.tagColumn)
        self.treeview.append_column(self.valueColumn)

        self.cell = gtk.CellRendererText()

        self.tagColumn.pack_start(self.cell, True)
        self.valueColumn.pack_start(self.cell, True)

        self.tagColumn.add_attribute(self.cell, 'text', 0)
        self.valueColumn.add_attribute(self.cell, 'text', 1)

        # Gridlines commented out as libries shipped with current windows
        # jbrout pack do not support this, need new libs to enable.
        try:
            self.treeview.set_grid_lines(gtk.TREE_VIEW_GRID_LINES_BOTH)
        except:
            pass

        self.scrolledwindow1.add(self.treeview)

        self.scrolledwindow1.show_all()

        # Call set-photo to populate the table with the values for the first picture
        self.setPhoto(0)

    def setPhoto(self,i):
        self.exifList.clear()
        if os.path.isfile(self.nodes[i].file):
            image=pyexiv.Image(self.nodes[i].file)
            image.readMetadata()
            try:
                self.exifList.append([_('JPEG Comment'),image.getComment().decode("utf_8","replace")])
            except:
                print "Error reafing JPEG comment"
            for key in image.exifKeys():
                if re.match(self.ignoredPattern, key) == None and key not in self.ignoredKeys:
                    tag_details = image.tagDetails(key)
                    try:
                        self.exifList.append(["Exif: "+tag_details[0],
                            image.interpretedExifValue(key)])
                    except:
                        print "Error on tag " + key
            for key in image.iptcKeys():
                if re.match(self.ignoredPattern, key) == None and key not in self.ignoredKeys:
                    tag_details = image.tagDetails(key)
                    try:
                        self.exifList.append(["Iptc: "+tag_details[0], image[key]])
                    except:
                        print "Error on tag " + key
            for key in image.xmpKeys():
                if re.match(self.ignoredPattern, key) == None and key not in self.ignoredKeys:
                    tag_details = image.tagDetails(key)
                    try:
                        self.exifList.append(["Xmp: "+tag_details[0], image[key]])
                    except:
                        print "Error on tag " + key
            if len(self.exifList)==0:
                self.exifList.append([_('No Displayable Meta Data found in file!'), ''])

        else:
            self.exifList.append([_('Can not open file!'), ''])

    def on_winViewExif_delete_event(self, widget, *args):
        self.quit(False)

    def on_button_close_clicked(self, widget, *args):
        self.quit(False)

    def on_selector_value_changed(self, *args):
        self.setPhoto(self.selector.getValue())

def main():
    win_viewExif = WinViewExif()

    win_viewExif.loop()

if __name__ == "__main__":
    from libs.i18n import createGetText

    # make translation available in the gui/gtk
    GladeApp.bindtextdomain("jbrout",os.path.join(os.path.dirname(__file__), 'po'))

    # make translation available in the code
    __builtins__.__dict__["_"] = createGetText("jbrout",os.path.join(os.path.dirname(__file__), 'po'))

    main()
