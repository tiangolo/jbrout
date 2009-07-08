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
import gobject

from libs.gladeapp import GladeApp

from __main__ import Buffer,TreeTags

class WinBulkTag (GladeApp):
    """Class to handle bulk tagging tag selection window"""

    glade = os.path.join(os.path.dirname(__file__), 'bulkTag.glade')
    window = "winBulkTag"

    def init(self, tags):
        self.ltags = tags

        def filename(column, cell, model, iter):
            cell.set_property('text', model.get_value(iter, 0))
            cell.set_property('foreground', model.get_value(iter, 2))
            cell.set_property('xalign', 0)
            #~ cell.set_property('xpad', 1)
        def pixbuf(column, cell, model, iter):
            node=model.get_value(iter,1)
            if node.__class__.__name__ == "TagNode":
                if model.get_value(iter, 3)==0:
                    cell.set_property('pixbuf', Buffer.pbCheckEmpty)
                elif model.get_value(iter, 3)==1:
                    cell.set_property('pixbuf', Buffer.pbCheckInclude)
                elif model.get_value(iter, 3)==2:
                    cell.set_property('pixbuf', Buffer.pbCheckExclude)
                else:
                    cell.set_property('pixbuf', Buffer.pbCheckDisabled)
            else:
                cell.set_property('pixbuf', None)

            cell.set_property('width', 16)
            cell.set_property('xalign', 0)
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start(cellpb, False)
        column.pack_start(cell, True)
        column.set_cell_data_func(cellpb, pixbuf)
        column.set_cell_data_func(cell, filename)

        self.tvTags.append_column(column)
        treeselection = self.tvTags.get_selection()
        treeselection.set_mode(gtk.SELECTION_NONE)

        storeTags = TreeTags()
        self.tvTags.set_model( storeTags )
        self.tvTags.set_enable_search(False)
        self.tvTags.set_state(gtk.CAN_FOCUS)

        storeTags.expander(self.tvTags)
        storeTags.cleanSelections()
        storeTags.setSelected(self.ltags)
        tags = ", ".join(self.ltags)
        self.lblTags.set_label("Tags to be added to the selected photos:\n %s" %tags)

    def on_btnOk_clicked(self, widget, *args):
        """Handles the Ok button"""
        self.quit(True, self.ltags)

    def on_btnCancel_clicked(self, widget, *args):
        """Handles the Cancel button"""
        self.quit(False, [])

    def on_tvTags_button_press_event(self, widget, *args):
        """Handles button presses in the AutoTag list"""
        event=args[0]
        tup= widget.get_path_at_pos( int(event.x), int(event.y) )
        if tup:
            path,obj,x,y = tup

            if path:
                model = widget.get_model()
                iterTo = model.get_iter(path)
                node = model.get(iterTo)

                # let's find the x beginning of the cell
                xcell = widget.get_cell_area(path, widget.get_column(0) ).x

                if node.__class__.__name__ == "TagNode":
                    if x>xcell:
                        # click on the cell (not on the arrow)
                        if event.button==1:
                            cv = model.get_value(iterTo,3)
                            if cv == 1:
                                # Delete tag
                                self.ltags.remove(node.name)
                            else:
                                # Add tag
                                self.ltags.append(node.name)
                                self.ltags.sort()
                        model=self.tvTags.get_model()
                        model.setSelected(self.ltags)
                        tags = ", ".join(self.ltags)
                        self.lblTags.set_label("Tags to be added to the selected photos:\n %s" %tags)
                        return 1 # stop the propagation of the even

    def on_tvTags_row_activated(self, widget, *args):
        """handles activation of rows in the auto tag list"""
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()
        if iter0:
            model.switch(iter0)