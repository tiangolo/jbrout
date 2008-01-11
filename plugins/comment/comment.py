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
from jbrout.commongtk import PictureSelector

from libs.gladeapp import GladeApp


class Wincomment(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'comment.glade')

    #-- Wincomment.new {
    def init(self, nodes):
        #############################################################
        ## IN in self.nodes:
        ##  - a list of PhotoNodes()
        ##
        ##
        ## OUT in self.reponse:
        ##  - boolean False : operation abandonned
        ##  - string : one comment for all the pictures
        ##  - [string,] : multi comments
        #############################################################
        self.main_widget.set_modal(True)
        self.main_widget.set_position(gtk.WIN_POS_CENTER)

        self.nodes = nodes

        self.selector = PictureSelector(self.nodes)
        self.hbox1.pack_start(self.selector)
        self.selector.connect("value_changed", self.on_selector_value_changed)
        self.selector.show()

        self.list=[]
        for i in self.nodes:
            b = gtk.TextBuffer()
            b.set_text(i.comment)
            self.list.append( (i,b) )

        self.lbl_all.set_text(_("%d photo(s)") % len(self.list))
        if len(self.nodes)==1:
            self.tv_all_comment.get_buffer().set_text(self.nodes[0].comment)
            self.notebook1.remove_page(1)
            self.tv_all_comment.grab_focus()
        else:
            self.setPhoto(0)

    def setPhoto(self,i):
        info = self.list[i]
        node = info[0]
        self.tv_comment.set_buffer( info[1] )
    def getTextFromBuffer(self,b):
        start=b.get_start_iter()
        end =b.get_end_iter()
        txt= b.get_text(start,end,False)
        txt = txt.replace("\r","")
        txt= txt.strip()
        return txt.decode("utf_8")


    def on_winComment_delete_event(self, widget, *args):
        self.quit(False)

    def on_notebook1_switch_page(self, widget, *args):
        gpoint,page= args
        if page==0:
            self.tv_all_comment.grab_focus()
        else:
            self.tv_comment.grab_focus()

    def on_selector_value_changed(self, *args):
        sel = self.selector.getValue()
        self.setPhoto(sel)

    def on_tv_comment_key_press_event(self, widget, *args):
        event=args[0]
        if event.get_state() & gtk.gdk.CONTROL_MASK:
            if event.keyval == 65365:
                self.selector.slider.set_value( self.selector.slider.get_value()-1 )
                return True # don't do the key !
            elif event.keyval in [65366,65293]:
                self.selector.slider.set_value( self.selector.slider.get_value()+1 )
                return True # don't do the key !
            elif event.keyval == 65360: # HOME
                self.selector.slider.set_value(0)
                return True # don't do the key !
            elif event.keyval == 65367: # END
                self.selector.slider.set_value(len(self.list))
                return True # don't do the key !

    def on_btn_annuler_clicked(self, widget, *args):
        self.quit(False)


    def on_btn_ok_clicked(self, widget, *args):
        selectedTab = self.notebook1.get_current_page()
        if selectedTab==0:
            # comment all
            reponse=self.getTextFromBuffer( self.tv_all_comment.get_buffer() )
        else:
            # comment one by one
            reponse=[self.getTextFromBuffer( b ) for n,b in self.list]
        self.quit(reponse)


def main():
    win_comment = Wincomment()

    win_comment.loop()

if __name__ == "__main__":
    main()


