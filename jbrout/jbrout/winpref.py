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


class WinPref(GladeApp):
    glade= 'data/jbrout.glade'
    window="WinPref"

    def init(self,plugins,liste):
        self.notebook1.set_current_page(1)
        self.liste = liste[:]
        #
        model = gtk.TreeStore(str,int,int,object)
        self.tvPlugins.set_model(model)

        def mkRacine(nom,typ):
            it=model.append(None,[nom,0,0,""])
            for instance,callback,props in plugins.request(typ,all=True):
                isChecked = "%s.%s"%(instance.id,props["method"]) in self.liste
                model.append(it,[props["label"],isChecked,1,(instance,callback,props)])

            self.tvPlugins.expand_row( model.get_path(it),False )
            return it


        mkRacine(_("Photos"),"PhotosProcess")
        mkRacine(_("Albums"),"AlbumProcess")


        renderer = gtk.CellRendererToggle();
        renderer.set_data("column", 1)  # data on col 1
        renderer.connect("toggled", self.on_item_toggled, model)
        column = gtk.TreeViewColumn("chk", renderer,
                                    active=1,   # active on col 1
                                    visible=2,  # visibl on col 2
                        )
        column.set_sizing(gtk.TREE_VIEW_COLUMN_AUTOSIZE)
        #~ column.set_fixed_width(50)
        column.set_clickable(True)
        self.tvPlugins.append_column(column)

        #
        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("name", cell_renderer,text=0)
        self.tvPlugins.append_column(column)
        #


        self.main_widget.show_all()

    def on_item_toggled(self,cell,path,model):
        #~ column = cell.get_data('column')
        it = model.get_iter_from_string(path)
        v=model.get_value(it,1) # get col1

        instance,cb,props = model.get(it,3)[0]    # get col3 to tuple
        pid = "%s.%s"%(instance.id,props["method"])

        if v:
            if pid in self.liste: self.liste.remove(pid)
        else:
            if pid not in self.liste: self.liste.append(pid)

        isChecked = pid in self.liste

        model.set(it,1,isChecked)   # set col1


    def on_WinPref_delete_event(self,*args):
        self.quit(None)
    def on_bntClose_clicked(self,*args):
        self.quit(self.liste)

    def on_tvPlugins_cursor_changed(self,tv):
        treeselection = tv.get_selection()
        model, it = treeselection.get_selected()
        self.info.set_label("")
        if it:
            isPlugin = model.get(it,2)[0]==1    # test col2 to see if it's a child
            if isPlugin:
                instance,cb,props = model.get(it,3)[0]    # get col3 to tuple

                self.info.set_label("""Plugin: %s
Version: %s
Creator: %s
Description : %s

More infos:
%s
""" % (instance.id,instance.__version__,instance.__author__,instance.__doc__,props["doc"] ))

if __name__=="__main__":
    pass
