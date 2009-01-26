# -*- coding: utf-8 -*-
#!/usr/bin/env python﻿
##
##    Copyright (C) 2009 Rob Wallace rob[at]wallace(dot)gen(dot)nz
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
import sys
#====
import pygtk
pygtk.require('2.0')
#====

import gtk
import gobject

import re

if __name__ == '__main__':
    os.chdir('..')
from libs.gladeapp import GladeApp
from common import caseFreeCmp

class FolderSelect(GladeApp):
    """Folder selection dialog allowing the selection of single or multiple
    folders"""
    glade = os.path.join(os.path.dirname(__file__), 'folderselect.glade')
    window = "dlgSelectFolder"

    def init(self, folder=None, selectMultiple=False, showHidden=False):
        """
        Initalises the folder selection window and draws the initial tree

        Keyword Arguments:
        folder         - The folder to be select upon opening the dialog
        selectMultiple - If true allow selection of multiple folders
        """

        self.mdl = gtk.TreeStore( gobject.TYPE_STRING,
                                         gobject.TYPE_STRING )

        self.renderer = gtk.CellRendererText()
        self.column0 = gtk.TreeViewColumn("Select Folder",
                                          self.renderer,
                                          text=0)
        self.view = gtk.TreeView( self.mdl )
        self.view.append_column( self.column0 )
        self.view.set_rubber_banding(True)
        self.view.set_headers_visible(False)
        self.view.set_enable_tree_lines(True)
        self.view.connect('row-expanded', self.on_node_expand)
        self.selection =  self.view.get_selection()
        self.setSelectMultiple(selectMultiple)

        self.swFolderList.add(self.view)
        self.swFolderList.show_all()

        self.setShowHidden(showHidden)

        self.initTree()

        if folder:
            self.selectDir(folder)

        return

    def setSelectMultiple(self, multiple):
        """Sets if multiple selections of folders are allowed"""
        if multiple:
            self.selection.set_mode(gtk.SELECTION_MULTIPLE)
        else:
            self.selection.set_mode(gtk.SELECTION_SINGLE)

    def setShowHidden(self, showHidden):
        """Sets if hidden folders are shown"""
        self.showHidden = showHidden
        self.cbShowHidden.set_active(self.showHidden)

    def selectDir(self, path):
        """Sets the currently selected folder/directory to path"""
        if os.path.isdir(path):
            pathSplit= []
            while True:
                (path, b) = os.path.split(path)
                if b == '':
                    pathSplit.insert(0,path)
                    break
                else:
                    pathSplit.insert(0,b)
            tIter = self.mdl.get_iter_root()
            for folder in pathSplit:
                while tIter is not None:
                    if self.mdl.get_value(tIter, 0) == folder:
                        break
                    tIter = self.mdl.iter_next(tIter)
                tPath = self.mdl.get_path(tIter)
                if self.mdl.iter_has_child(tIter):
                    self.view.expand_row(tPath, False)
                    tIter = self.mdl.iter_children(tIter)
                else:
                    break
            self.view.set_cursor(tPath)


    def addDir(self, folder, maxDepth=1, parent=None, depth=0):
        """
        Adds a directory/folder and children as determined by arguments to the
        tree.

        Note: this does not check that the folder/directory is being added in
              the right place

        Keyword Arguments:
        folder   - path to folder/directory to add
        maxDepth - depth of folders/directories to add
        parent   - parent node (folder/directory) in the tree to add to
        depth    - current depth (used for recursion)
        """
        depth += 1
        try:
            for subFolder in sorted(os.listdir(folder), cmp=caseFreeCmp):
                subFolderFull = os.path.join(folder,subFolder)
                if self.checkFolder(subFolder, subFolderFull):
                    newParent = self.mdl.append(parent,(subFolder,subFolderFull))
                    if maxDepth > depth:
                        self.addDir(subFolderFull, maxDepth, newParent, depth)
        except:
            print "Something happening with permissions at %s" % folder

    def checkFolder(self, folder, folderFull):
        """Checks a folder to see if it should be displayed based on full path"""
        try:
            pathOk = os.path.isdir(folderFull) and\
                     os.access(folderFull,os.X_OK)
        except:
            pathOk = False
        if self.showHidden:
            ret = pathOk
        else:
            ret = pathOk and re.match('^\..*',folder) == None
        return ret

    def winDrives(self):
        """Returns a list of the windows drives in cluding :\ eg: 'C:\'"""
        # A missing not in search list as it causes errors which can not be
        # trapped
        dl = 'BCDEFGHIJKLMNOPQRSTUVWXYZ'
        drives = ['%s:\\' % d for d in dl if os.path.exists('%s:\\' % d)]
        return drives

    def initTree(self):
        """Initalises the folder tree with the roots and their direct
        children"""
        if sys.platform[:3].lower()=="win":
            roots = self.winDrives()
        else:
            roots = ['/']
        for root in roots:
            parent = self.mdl.append(None,(root, root))
            self.addDir(root, maxDepth=1, parent=parent)

    def on_node_expand(self,treeview,iter, path,*args):
        """Handles the expansion of nodes and builds the tree under them as
        necessary"""
        to_remove=[]
        def remove_iter(iter_r, remove_this=True):
            child_iter=self.mdl.iter_children(iter_r)
            while child_iter:
                remove_iter(child_iter)
                child_iter=self.mdl.iter_next(child_iter)
            if remove_this:
                sub_node=self.mdl[iter_r].iter
                to_remove.append(sub_node)
        remove_iter(iter, False)
        self.addDir(self.mdl[path][1],2,iter)
        for node in to_remove:
            self.mdl.remove(node)

    def on_cbShowHidden_toggled(self,*args):
        """Handles toggling of the show Hidden check button and sets the
        internal state, refresh of the tree is not performed, this can be done
        by the user contracting and expanding the branches"""
        self.showHidden = self.cbShowHidden.get_active()

    def on_butOpen_clicked(self,*args):
        """Handles closing the dialog and returning the folders/directories
        selected when the Open button is clicked"""
        self.quit([tuple(self.mdl[path])[1] for path in
                   self.selection.get_selected_rows()[1]])

    def on_butCancel_clicked(self,*args):
        """Handles closing the dialog and returning an empty list when the
        Cancel button is clicked"""
        self.quit([])

    def on_dlgSelectFolder_delete_event(self,*args):
        """Handles closing the dialog and returning an empty list when the
        dialog is closed programatically"""
        self.quit([])

if __name__ == '__main__':
    fs = FolderSelect()
    fs.setSelectMultiple(True)
    if sys.platform[:3].lower()=="win":
        fs.selectDir('S:\\jbrout\\dist')
    else:
        fs.selectDir('/home/robertw')

    folders = fs.loop()[0]

    if len(folders):
        print "Folders selected are:"
        for folder in folders:
            print '  %s' % folder
    else:
        print 'No folders selected'
