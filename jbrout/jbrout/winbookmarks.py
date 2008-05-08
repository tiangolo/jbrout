# -*- coding: UTF-8 -*-
##
##    Copyright (C) 2008 manatlan manatlan[at]gmail(dot)com
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
import sys
from __main__ import GladeApp

class WinBookmark(GladeApp):
    glade= 'data/jbrout.glade'
    window="WinBookmark"
    
    def init(self,l):
        self.__saved=l[:]

        model = gtk.ListStore(str,str)
        for a,b in l:
            model.append([a,b])
        self.tvBookmarks.set_model(model)

        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("name", cell_renderer,text=0)
        
        self.tvBookmarks.append_column(column)

        self.main_widget.show_all()

    def on_WinBookmark_delete_event(self,*args):
        self.quit(self.__saved)
        
    def on_tvBookmarks_cursor_changed(self,*args):
        pass
    
    def on_btnRemove_clicked(self,widget):
        treeselection = self.tvBookmarks.get_selection()
        model, iter0 = treeselection.get_selected()
        if iter0:
            model.remove(iter0)
        
    def on_btnClose_clicked(self,*args):
        model=self.tvBookmarks.get_model()
        self.quit([(i[0],i[1]) for i in model])
        
if __name__=="__main__":
    l=[("albert","kkk"),("john","kkk"),("kill","kkk")]
    w=WinBookmark(l)
    ret=w.loop()[0]
    print ret
 