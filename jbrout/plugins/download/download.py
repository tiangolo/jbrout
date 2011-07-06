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

import sys
import urllib

import datetime
import time
import re
import shutil

from libs import extListview
from jbrout import pyexiv
from libs.gladeapp import GladeApp

from jbrout.common import format_file_size_for_display,ed2d,dnd_args_to_dir_list
from jbrout.tools import PhotoCmd,_Command, autoTrans
from jbrout.commongtk import InputBox,MessageBox,InputQuestion,Img

from nameBuilder import NameBuilder,WinNameBuilderTokens

from __main__ import Buffer,TreeTags

SUP_EXT = ('jpg', 'raw', 'cr2','nef')

def sup_ext():
    ret = []
    for ext in SUP_EXT:
        ret.append('.' + ext)
        ret.append('.' + ext.upper())
    return ret

class dc():
    """Class to contain column download constants"""
    (
        C_SRC,    # Source file location
        C_SIZE,   # File size formatted for printing
        C_SZ_RAW, # Raw size for sorting & comparrison
        C_DATE,   # EXIF date or file date if no EXIF
        C_DATET,  # Date text
        C_EXIF,   # EXIF information
        C_DEST,   # Destination file name
        C_STAT,   # Status formatted for printing
        C_SS,     # Short status used programatically
        C_ROT,    # Rotation formatted for printing
        C_RS      # Short rotation used programatically
    ) = range(11)

class cc():
    """Class to contain camera mapping column constants"""
    (
        C_MODEL,  # Camera Model from EXIF
        C_SERIAL, # Camera serial Number from EXIF if used
        C_OWNER,  # Camera owner string from EXIF if used
        C_USER,   # Camera user comment from EXIF if used
        C_T8,     # String to use for {T8} tag
        C_T9,     # String to use for {T9} tag
        C_TAG     # Tag to automatically tag images
    ) = range(7)

class WinDownload(GladeApp):
    """Class to handle main download window"""

    glade = os.path.join(os.path.dirname(__file__), 'download.glade')
    window = "winDownloadStart"

    def init(self, conf, nodeFolder):
        """Initalises the main download window and builds download table"""

        self.btnSourceFolder.drag_dest_set(
            gtk.DEST_DEFAULT_ALL,
            [( 'text/uri-list', 0, 1 ),('text/plain', 0, 1)], # drag from os
            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

        txtRdr = gtk.CellRendererText()

        columns = ((_('Source'),      [(txtRdr, gobject.TYPE_STRING)],
                    (dc.C_SRC,),    True),
                   (_('Size'),        [(txtRdr, gobject.TYPE_STRING)],
                    (dc.C_SZ_RAW,), True),
                   (None,             [(None, gobject.TYPE_STRING)],
                    (None,),          False),# Raw size
                   (None,             [(None, gobject.TYPE_PYOBJECT)],
                    (None,),          False), # Datetime object
                   (_('Date/Time'),   [(txtRdr, gobject.TYPE_STRING)],
                    (dc.C_DATE,),   True), # Date for display
                   (None,             [(None, gobject.TYPE_PYOBJECT)],
                    (None,),          False),# EXIF
                   (_('Destination'), [(txtRdr, gobject.TYPE_STRING)],
                    (dc.C_DEST,),   True),
                   (_('Status'),      [(txtRdr, gobject.TYPE_STRING)],
                    (dc.C_STAT,),   True),
                   (None,             [(None, gobject.TYPE_STRING)],
                    (None,),          False),# Short Status
                   (_('Rotation'),    [(txtRdr, gobject.TYPE_STRING)],
                    (dc.C_ROT,),    True),
                   (None,             [(None, gobject.TYPE_STRING)],
                    (None,),          False))

        self.imLst = extListview.ExtListView(columns)
        self.imLst.enableDNDReordering()

        self.swFileList.add(self.imLst)
        self.swFileList.show_all()

        self.destFolder = nodeFolder.file

        self.cidStatusBar = self.statusBar.get_context_id(
            _("Download Photos From Camera"))

        self._initFromConf(conf)
        self.invalidSource = True
        self.invalidDest  = True
        self.badPattern = False
        self.buildListRunning = False
        self.quitNow = False
        task = self._bgWork()
        gobject.idle_add(task.next)

    def _initFromConf(self, conf):
        """
        Initalise the download window from the stored configuration

        Keyword Arguments:
        conf - Configuration object
        """
        self.__conf = conf
        self.nb = NameBuilder()
        self.srcFolder = self.__conf['sourceFolder']
        if not os.path.isdir(self.srcFolder):
            self.srcFolder = os.path.dirname(__file__)
        self.entSourceFolder.set_text(self.srcFolder)
        self.entDestFolder.set_text(self.destFolder)
        self.chkDelete.set_active(self.__conf['delete'] == 1)

        w,h = self.__conf['width'] or 800,self.__conf['height'] or 400
        # work arround for bug in pygtk/gtk 2.10.6 on windows set default size
        # then reshow with initial (default) size instead of simple resize
        self.main_widget.set_default_size(w,h)
        self.main_widget.reshow_with_initial_size()
        self.main_widget.resize_children()
        if self.__conf['promptJobCode'] == 1:
            newJobCode = InputBox(self.main_widget,
            _('Please enter the new Job Code'),
            '%s' % self.__conf['jobCode'])
            if newJobCode != None:
                self.__conf['jobCode'] = newJobCode

    def _bgWork(self):
        """Backgroud task to build/update image download table"""
        while not self.quitNow:
            if self.invalidSource and not self.buildListRunning:
                self.btnExecute.set_sensitive(False)
                self.buildListRunning = True
                task = self._buildListSource()
                gobject.idle_add(task.next)
            yield True
            (self.invalidSource, self.invalidDest,self.buildListRunning)
            if self.invalidDest and\
                    not self.invalidSource and\
                    not self.buildListRunning and\
                    not self.badPattern:
                self.buildListRunning = True
                self.btnExecute.set_sensitive(False)
                task = self._buildListDest()
                gobject.idle_add(task.next)
            yield True
        yield False

    def _buildListSource(self):
        """Builds list of files to be downloaded"""
        self.invalidSource = False
        self.invalidDest = True
        self.imLst.clear()
        self.statusBar.push(self.cidStatusBar,
            _('Finding source files in "%s"') % self.srcFolder)
        yield True
        self.imgInfs = []
        fileList = self._listFiles(self.srcFolder)
        fileList.sort()
        self.statusBar.pop(self.cidStatusBar)
        self.statusBar.push(self.cidStatusBar,
            _('Reading source file information from "%s"') % self.srcFolder)
        yield True

        model = self.imLst.get_model()
        self.imLst.set_model(None)

        if self.invalidSource or self.quitNow:
            self.statusBar.pop(self.cidStatusBar)
            self.buildListRunning = False
            yield False
        for srcFile in fileList:
            exifData=pyexiv.Image(srcFile)
            exifData.readMetadata()
            size=os.path.getsize(srcFile)
            if 'Exif.Photo.DateTimeOriginal' in exifData.exifKeys():
                date = ed2d(exifData.interpretedExifValue('Exif.Photo.DateTimeOriginal'))
            else:
                date = datetime.datetime.fromtimestamp(os.path.getmtime(srcFile))
            row=[
                srcFile[len(self.srcFolder)+1:],
                format_file_size_for_display(size),
                size,
                date,
                date,
                exifData,
                '',
                '',
                '',
                '',
                '']
            self.imgInfs.append(row[:-4])
            self.imLst.appendRows([row])

            if self.invalidSource or self.quitNow:
                self.statusBar.pop(self.cidStatusBar)
                self.buildListRunning = False
                yield False
            yield True

        self.imLst.set_model(model)

        self.buildListRunning = False
        self.statusBar.pop(self.cidStatusBar)
        yield False

    def _buildListDest (self):
        """Adds destination file name, download status and rotation to a list
        of files to be downloaded"""
        self.invalidDest = False
        # Check that the list is not empty
        if self.imLst.getCount() == 0:
            self.buildListRunning = False
            yield False

        model = self.imLst.get_model()
        self.imLst.set_model(None)

        # Start new
        # Build image Names
        # Build names without seralisation
        self.statusBar.push(self.cidStatusBar, _('Building destination Names'))
        yield True
        # Clear all destination information
        for rowIdx in range(self.imLst.getCount()):
            self.imLst.setItem(rowIdx, dc.C_SS, '')
            self.imLst.setItem(rowIdx, dc.C_STAT, '')
            self.imLst.setItem(rowIdx, dc.C_RS, '')
            self.imLst.setItem(rowIdx, dc.C_ROT, '')
        for imageInfo in self.imgInfs:
            imageInfo[dc.C_DEST] = self.nb.name(
                                    imageInfo[dc.C_SRC],
                                    '', # Dest folder blank as not needed here
                                    self.__conf['nameFormat'],
                                    imageInfo[dc.C_EXIF],
                                    imageInfo[dc.C_DATE],
                                    self.__conf['jobCode'])
        if not self.nb.seralize(self.imgInfs,dc.C_SRC,dc.C_DATE,dc.C_DEST):
            MessageBox(self.main_widget,
            _("More than one serialisation tag used please use preferencess to remove from File Naming > Parttern"))
            self.statusBar.pop(self.cidStatusBar)
            self.invalidDest - True
            self.badPattern = True
            self.buildListRunning = False
            yield False
        if self.invalidSource or self.invalidDest or self.quitNow:
            self.statusBar.pop(self.cidStatusBar)
            self.buildListRunning = False
            yield False
        yield True
        # Note need to make sure self.imgInfs is sorted by source file
        # for the below to work
        # Write destination names into imList
        for imgIdx, imgInf in enumerate(self.imgInfs):
            if self.imLst.getItem(imgIdx,dc.C_SRC) != imgInf[dc.C_SRC]:
                print "No Match at %d ?" % (imgIdx)
                print "List: %s" % self.imLst.getItem(imageIndex,dc.C_SRC)
                print "Source: %s" % imgInf[dc.C_SRC]
            else:
                self.imLst.setItem(imgIdx,
                                   dc.C_DEST,
                                   imgInf[dc.C_DEST])
            if self.invalidSource or self.invalidDest or self.quitNow:
                self.statusBar.pop(self.cidStatusBar)
                self.buildListRunning = False
                yield False
            yield True
        self.statusBar.pop(self.cidStatusBar)
        # Check Status
        self.statusBar.push(self.cidStatusBar, _('Checking Status of Images'))
        yield True
        for rowIdx, row in enumerate(self.imLst.iterAllRows()):
            destFile = os.path.join(self.destFolder,row[dc.C_DEST])
            count = 0
            for chkRow in self.imLst.iterAllRows():
                if chkRow[dc.C_DEST] == row[dc.C_DEST]:
                    count += 1
            if count > 1:
                statS = 'C'
                statL = _('Collision with New')
            elif os.path.isfile(destFile):
                destExif = pyexiv.Image(destFile)
                destExif.readMetadata()
                if 'Image DateTime' in destExif.exifKeys():
                    destDate = ed2d(destExif.interpretedExifValue('Exif.Photo.DateTimeOriginal'))
                else:
                    destDate = datetime.datetime.fromtimestamp(
                        os.path.getmtime(destFile))
                if destDate.timetuple() == row[dc.C_DATE].timetuple():
                    statS = 'D'
                    statL = _('Downloaded')
                else:
                    statS = 'C'
                    statL = _('Collision with Existing')
            else:
                statS = 'N'
                statL = _('New')
            if self.invalidSource or self.invalidDest or self.quitNow:
                self.statusBar.pop(self.cidStatusBar)
                self.buildListRunning = False
                yield False
            self.imLst.setItem(rowIdx, dc.C_SS, statS)
            self.imLst.setItem(rowIdx, dc.C_STAT, statL)
            yield True
        self.statusBar.pop(self.cidStatusBar)
        # Check Rotation
        self.statusBar.push(self.cidStatusBar, _('Checking Rotation Required for Images'))
        yield True
        for rowIdx, row in enumerate(self.imLst.iterAllRows()):
            if self.__conf["autoRotate"] == 1:
                try:
                    rotS = autoTrans[int(row[dc.C_EXIF]['Exif.Image.Orientation'])][0]
                    rotL = autoTrans[int(row[dc.C_EXIF]['Exif.Image.Orientation'])][1]
                except KeyError:
                    rotS = autoTrans[1][0]
                    rotL = autoTrans[1][1]
            else:
                rotS = autoTrans[1][0]
                rotL = _('Disabled')
            if self.invalidSource or self.invalidDest or self.quitNow:
                self.statusBar.pop(self.cidStatusBar)
                self.buildListRunning = False
                yield False
            self.imLst.setItem(rowIdx, dc.C_RS, rotS)
            self.imLst.setItem(rowIdx, dc.C_ROT, rotL)
            yield True
        self.statusBar.pop(self.cidStatusBar)

        self.imLst.set_model(model)

        # Completed exiting
        self.btnExecute.set_sensitive(True)
        self.buildListRunning = False
        yield False

    def _listFiles(self, dir):
        """
        Recursivley builds and returns a list of valid image files in a given
        directory

        Keyword Arguments:
        dir - Folder to recursivley list image files from
        """
        fileList=[]
        for name in os.listdir(dir):
            path = os.path.join(dir, name)
            if (
            os.path.isfile( path) and
            os.path.splitext( name )[1] in sup_ext()
            ):
                fileList +=[path]
            elif (os.path.isdir(path)):
                fileList += self._listFiles(path)
        return fileList

    def on_btnSourceFolder_clicked(self, widget, *args):
        """Handles the chanmge source folder button (...), gets the new source
        folder and initiates the update of the download list"""
        dialog = gtk.FileChooserDialog(_('Select source folder'),
                self.main_widget,
                gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        dialog.set_filename(self.srcFolder)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            if dialog.get_filename != self.srcFolder:
                self.srcFolder = dialog.get_filename()
                self.invalidSource = True
                self.entSourceFolder.set_text(self.srcFolder)
        dialog.destroy()

    def on_btnSourceFolder_drag_data_received(self, widget, *args):

        list = dnd_args_to_dir_list(args)

        if list:
            self.srcFolder = list[0]
            self.invalidSource = True
            self.entSourceFolder.set_text(self.srcFolder)

    def on_btnPreferences_clicked(self, widget, *args):
        """Handles the Preferences button, loads the preferences dialog and
        initiates the update of the download list"""
        if self.imLst.getCount() == 0:
            preferences = WinDownloadPreferences(
                self.__conf,
                self.destFolder,
                os.path.join(os.path.dirname(__file__),
                             '123camera',
                             'img_4567.jpg'),
                dict(),
                datetime.datetime.now())
        else:
            if self.imLst.getSelectedRowsCount() == 0:
                selIdx = 0
            else:
                selIdx = self.imLst.getFirstSelectedRowIndex()
            preferences = WinDownloadPreferences(
                self.__conf,
                self.destFolder,
                self.imLst.getItem(selIdx, dc.C_SRC),
                self.imLst.getItem(selIdx, dc.C_EXIF),
                self.imLst.getItem(selIdx, dc.C_DATE))
        response = preferences.loop()[0]
        if response:
            self.badPattern = False
            self.invalidDest = True


    def on_btnExecute_clicked(self, widget, *args):
        """Handles the Execute button and starts the download process"""
        # Save settings
        self.quitNow = True
        self.__conf["sourceFolder"]=self.entSourceFolder.get_text()
        if self.chkDelete.get_active(): self.__conf['delete'] = 1
        else: self.__conf['delete'] = 0
        self.__conf["width"],self.__conf["height"] = self.main_widget.get_size()

        # Build the list of images to download
        noRowsSelected = self.imLst.getSelectedRowsCount()
        if noRowsSelected == 0 or noRowsSelected == len(self.imgInfs):
            self.toDownload = self.imLst.getAllRows()
        else:
            self.toDownload = self.imLst.getSelectedRows()
        self.quit(True)

    def on_chkDelete_toggled(self, widget, *args):
        """Handles toggling of the delete check box"""
        pass

    def on_winDownloadStart_delete_event(self,*args):
        """Handles programatically closing the window"""
        self.quitNow = True
        self.quit(False)

    def on_btnCancel_clicked(self, widget, *args):
        """Handles the Cancle button and closes the window"""
        self.quitNow = True
        self.quit(False)

    def getToDownload(self):
        """Returns the list of 'selected' images to be downloaded
        (can be run after the window has been closed)"""
        return self.toDownload

class WinDownloadPreferences(GladeApp):
    """Class to handle the Download Preferences window"""
    # TODO: implement camera tagging settings

    glade = os.path.join(os.path.dirname(__file__), 'download.glade')
    window = "winDownloadPreferences"

    def init(self, conf, destination, exSource, exExif, exDate):
        """
        Initalise the Download preferences window

        Keyword arguments:
        conf        - configuration object
        destination - destination folder for downloaded images
        exSource    - source file name (used for generating examples)
        exExif      - source EXIF data (used for generating examples)
        exDate      - source date (used for generating examples)
        """
        self.__conf = conf
        self.exSource = exSource
        self.exExif = exExif
        self.exDate = exDate
        self.nb = NameBuilder()
        self.tbufComment = self.txtComment.get_buffer()

        # Init general page
        self.chkAutoRotate.set_active(self.__conf["autoRotate"]==1)
        self.chkCopyOther.set_active(self.__conf["copyOther"]==1)
        self.chkAutoComment.set_active(not len(self.__conf["autoComment"])==0)
        comment = self.__conf["autoComment"]
        self.tbufComment.set_text(comment.replace("\\n", "\n"))
        # Init naming page
        self.entDestination.set_text(destination)
        self.entFilename.set_text(self.__conf["nameFormat"])
        self.origJobCode = self.__conf["jobCode"]
        self.entJobCode.set_text(self.__conf["jobCode"])
        self.chkJobCode.set_active(self.__conf["promptJobCode"]==1)
        self.updateExample()
        # Init Auto Tag page
        self.ltags = eval('%s' % self.__conf['autoTag'])

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
        self.lblTags.set_label("Tags: %s" %tags)
        # Init Conversion Page
        self.chkDcraw.set_active(self.__conf["dcraw"]==1)
        self.chkDcrawCopyMetaData.set_active(self.__conf["dcrawCopyMetaData"]==1)
        self.chkDcrawCopyRaw.set_active(self.__conf["dcrawCopyRaw"]==1)
        # Remove un-implemented pages
        self.ntbkPreferences.remove_page(4) # Conversion
        self.ntbkPreferences.remove_page(3) # Camera Mapping

    # Main Window handlers
    def on_winDownloadPreferences_delete_event(self, widget, *args):
        """Handles programatically closing the window"""
        self.quit(False)

    def on_btnOk_clicked(self, widget, *args):
        """Handles the Ok button and saves the preferences"""
        # Save general page
        if self.chkAutoRotate.get_active(): self.__conf["autoRotate"] = 1
        else: self.__conf["autoRotate"] = 0
        if self.chkCopyOther.get_active(): self.__conf["copyOther"] = 1
        else: self.__conf["copyOther"] = 0
        comment = self.tbufComment.get_text(self.tbufComment.get_start_iter(),
                                            self.tbufComment.get_end_iter())
        self.__conf["autoComment"] = comment.replace("\n", "\\n")
        # Save naming page
        self.__conf["nameFormat"] = self.entFilename.get_text()
        self.__conf["jobCode"] = self.entJobCode.get_text()
        if self.chkJobCode.get_active(): self.__conf["promptJobCode"] = 1
        else: self.__conf["promptJobCode"] = 0
        self.quit(True)
        # Save Auto Tag page
        self.__conf['autoTag']=self.ltags
        # Save Conversion page
        if self.chkDcraw.get_active(): self.__conf["dcraw"] = 1
        else: self.__conf["dcraw"] = 0
        if self.chkDcrawCopyMetaData.get_active(): self.__conf["dcrawCopyMetaData"] = 1
        else: self.__conf["dcrawCopyMetaData"] = 0
        if self.chkDcrawCopyRaw.get_active(): self.__conf["dcrawCopyRaw"] = 1
        else: self.__conf["dcrawCopyRaw"] = 0

    def on_btnCancel_clicked(self, widget, *args):
        """Handles the Cancel button"""
        self.quit(False)

    ## General tab handlers
    def on_chkAutoComment_toggled(self, widget, *args):
        """handles toggling of the Auto Comment tick-box and en/disables the
        comment text entry"""
        if self.chkAutoComment.get_active():
            self.txtComment.set_editable(True)
            self.txtComment.set_flags(gtk.CAN_FOCUS)
            self.txtComment.set_flags(gtk.SENSITIVE)
        else:
            self.txtComment.set_editable(False)
            self.txtComment.unset_flags(gtk.CAN_FOCUS)
            self.txtComment.unset_flags(gtk.SENSITIVE)
            self.tbufComment.set_text("")

    ## Naming tab handlers
    def on_entFilename_changed(self, widget, *args):
        """Detects changes in the destination file name pattern and initates an
         update of the example"""
        self.updateExample()

    def on_entJobCode_changed(self, widget, *args):
        """Detects changes in the job code and initates an update of the
        example"""
        self.updateExample()

    def on_btnTokens_clicked(self, widget, *args):
        """Handles the Show all Tokens buttons & launches the list of tokens"""
        tokens=WinNameBuilderTokens(self.exSource,
                                    self.exExif,
                                    self.exDate,
                                    self.entJobCode.get_text())
        tokens.loop()

    def updateExample(self):
        """Updates the example destination file name"""
        self.entExample.set_text(
            self.nb.singleSeralize(
                self.nb.name(
                    self.exSource,
                    self.entDestination.get_text(),
                    self.entFilename.get_text(),
                    self.exExif,
                    self.exDate,
                    self.entJobCode.get_text())))

    ## Auto Tag Tab Handlers
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
                        self.lblTags.set_label("Tags: %s" %tags)
                        return 1 # stop the propagation of the event



    def on_tvTags_row_activated(self, widget, *args):
        """handles activation of rows in the auto tag list"""
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()
        if iter0:
            model.switch(iter0)

    ## Conversion Tab Handlers
    def on_chkDcraw_toggled(self, widget, *args):
        """handles toggling of the dcraw tick-box and en/disables the
        the associated options"""
        if self.chkDcraw.get_active():
            self.chkDcrawCopyMetaData.set_flags(gtk.CAN_FOCUS)
            self.chkDcrawCopyMetaData.set_flags(gtk.SENSITIVE)
            self.chkDcrawCopyRaw.set_flags(gtk.CAN_FOCUS)
            self.chkDcrawCopyRaw.set_flags(gtk.SENSITIVE)
        else:
            self.chkDcrawCopyMetaData.unset_flags(gtk.CAN_FOCUS)
            self.chkDcrawCopyMetaData.unset_flags(gtk.SENSITIVE)
            self.chkDcrawCopyMetaData.set_active(False)
            self.chkDcrawCopyRaw.unset_flags(gtk.CAN_FOCUS)
            self.chkDcrawCopyRaw.unset_flags(gtk.SENSITIVE)
            self.chkDcrawCopyRaw.set_active(False)


    ## Camera mapping Tab Handlers
    def on_btnMappingAdd_clicked(self,*args):
        """Handles the Add Mapping button and adds a new camera mapping from
        the classes in example file & exif information (future)"""
        pass

    def on_btnMappingAddFile_clicked(self,*args):
        """Handles the Add Mapping from File button and adds a new camera
        mapping from the user selected image file (future)"""
        pass

    def btnMappingDelete_clicked_cb(self,*args):
        """Handles the Delete Mapping button and deletes the selected
        mappings (future)"""
        pass

    def on_btnMappingEdit_clicked(self,*args):
        """Handles the Edit Mapping button and initiates alwos the used to edit
        the selected mappings (future)"""
        pass

    def on_chkMappingIdentify_toggled(self,*args):
        """Handles toggling of the additional information in Mapping check-box
        and updates the current camer information (future)"""
        pass

class WinCameraMapping(GladeApp):
    """Class to handle the camera mapping window (future, untested)"""

    # TODO: Implement camera mapping window class
    glade = os.path.join(os.path.dirname(__file__), 'download.glade')
    window = "dlgCameraMapping"

    def init(self, map):
        """Initalises the window and fills out the existing values"""
        comment = _('Please enter the values to use for {T8}, {T9} and auto Tag for the selected camera:')
        comment = comment + "\n%s: %s" % (_('Camera'),map[cc.MODEL])
        if map[cc.SERIAL] != '':
            comment = comment + "\n%s: %s" % (_('Serial Number'),map[cc.MODEL])
        if map[cc.OWNER] != '':
            comment = comment + "\n%s: %s" % (_('Owner String'),map[cc.OWNER])
        if map[cc.USER] != '':
            comment = comment + "\n%s: %s" % (_('User Comment'),map[cc.USER])
        self.lblIntro.set_text(comment)
        self.entT8.set_text(map[cc.C_T8])
        self.entT9.set_text(map[cc.C_T9])
        self.entTag.set_text(map[cc.C_TAG])

    def on_btnCancel_clicked(self,*args):
        """Handles the cancel button"""
        self.quit(False)

    def on_btnOk_clicked(self,*args):
        """Handles the Ok button and saves the modified values"""
        map[cc.C_T8] = self.entT8.get_text()
        map[cc.C_T9] = self.entT9.get_text()
        map[cc.C_TAG] = self.entTag.get_text()
        self.quit(True)

    def on_dlgCameraMapping_delete_event(self, widget, *args):
        """Handles programatically closing the window"""
        self.quit(False)

class WinDownloadExecute(GladeApp):
    """Class to handle the download execution window"""

    glade = os.path.join(os.path.dirname(__file__), 'download.glade')
    window = "winDownloadProgress"

    def init(self, conf, list, srcFolder, destFolder):
        """Handles window initalisation"""
        self.conf = conf
        self.list = list
        self.srcFolder = srcFolder
        self.destFolder = destFolder

        self.quitNow = False
        task = self.doIt()
        gobject.idle_add(task.next)

    def on_winDownloadProgress_delete_event(self, widget, *args):
        """Handles programatically closing the window"""
        self.quitNow = True

    def on_btnCancel_clicked(self, widget, *args):
        """Handles the Cancel button"""
        self.quitNow = True

    def doIt(self):
        """Background task to perform the actual work and send/receive updates
        from the GUI"""
        for itemIndex, item in enumerate(self.list):
            if  item[dc.C_SS] != 'C': # Not Conflicted
                # Initial set-up for item
                src = os.path.join(self.srcFolder,item[dc.C_SRC])
                dest = os.path.join(self.destFolder,item[dc.C_DEST])
                self.lblSource.set_label(src)
                self.lblDest.set_label(dest)
                self.progressbar.set_text(_("Downloading %d of %d") %
                    (itemIndex+1, len(self.list)))
                self.progressbar.set_fraction(
                    float(itemIndex)/len(self.list))
                # Load preview
                self.lblAction.set_label(_('Loading preview'))
                yield True
                noThumb = False
                try:
                    if item[dc.C_EXIF].getThumbnailData():
                        thumbJpeg = item[dc.C_EXIF].getThumbnailData()[1]
                        loader = gtk.gdk.PixbufLoader ('jpeg')
                        loader.write (thumbJpeg, len(thumbJpeg))
                        thumbIm = loader.get_pixbuf ()
                        loader.close ()
                        if item[dc.C_RS] == "flipHorizontal":
                            thumbIm = thumbIm.flip(True)
                        elif item[dc.C_RS] == "rotate180":
                            thumbIm = thumbIm.rotate_simple(gtk.gdk.PIXBUF_ROTATE_UPSIDEDOWN)
                        elif item[dc.C_RS] == "flipVertical":
                            thumbIm = thumbIm.flip(False)
                        elif item[dc.C_RS] == "transpose":
                            thumbIm = thumbIm.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
                            thumbIm = thumbIm.flip(False)
                        elif item[dc.C_RS] == "rotate90":
                            thumbIm = thumbIm.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
                        elif item[dc.C_RS] == "transverse":
                            thumbIm = thumbIm.rotate_simple(gtk.gdk.PIXBUF_ROTATE_CLOCKWISE)
                            thumbIm = thumbIm.flip(True)
                        elif item[dc.C_RS] == "rotate270":
                            thumbIm = thumbIm.rotate_simple(gtk.gdk.PIXBUF_ROTATE_COUNTERCLOCKWISE)
                    else:
                        noThumb = True
                except:
                    noThumb = True

                if noThumb:
                    thumbIm = gtk.gdk.pixbuf_new_from_file(
                        os.path.join('data','gfx','imgNoThumb.png'))
                self.imgPreview.set_from_pixbuf(thumbIm)
            if item[dc.C_SS] == 'N': # New item
                # Copying file
                self.lblAction.set_label(_('Copying'))
                yield True
                if not os.path.isdir(os.path.dirname(dest)):
                    os.makedirs(os.path.dirname(dest))
                shutil.copy2(src, dest)
                pc = PhotoCmd(unicode(dest))
                # Rotation if enabled/needed
                if item[dc.C_RS] != 'N':
                    self.lblAction.set_label(
                        '%s %s' % (_('Performing Transformation:'),item[dc.C_ROT]))
                    yield True
                    pc.transform(item[dc.C_RS])
                # Build thumb if broken or non existant
                if noThumb:
                    self.lblAction.set_label(_('Building Thumbnail'))
                    yield True
                    pc.rebuildExifTB()
                # Auto comment if enabled
                if len(self.conf['autoComment']) > 0:
                    self.lblAction.set_label(_('Commenting'))
                    yield True
                    comment =self.conf['autoComment']
                    pc.addComment(unicode(comment.replace("\\n", "\n")))
                # Auto tagging
                # TODO: Implement tagging based on Camera Name
                if len(eval('%s' % self.conf['autoTag'])) > 0:
                    self.lblAction.set_label(_('Tagging'))
                    yield True
                    pc.addTags(eval('%s' % self.conf['autoTag']))
                # Set file modification date/time stamp
                self.lblAction.set_label(_('Setting Modification Times'))
                yield True
                timeStamp = time.mktime(item[dc.C_DATE].timetuple())
                self._touch(dest,timeStamp)
            # Delete source if enabled and No collision
            if  item[dc.C_SS] != 'C' and self.conf['delete'] == 1:
                self.lblAction.set_label(_('Deleting Source'))
                yield True
                self._delete(src)
            # Copy related files if enabled and no collision
            if self.conf['copyOther'] == 1 and item[dc.C_SS] != 'C':
                self.lblAction.set_label(_('Finding Related Files'))
                yield True
                for file in os.listdir(os.path.dirname(src)):
                    if (file != os.path.basename(src)) and \
                       (os.path.splitext(file)[0] ==
                       os.path.splitext(os.path.basename(src))[0])\
                       and not(os.path.splitext(file)[1] in ['.jpg','.JPG']):# TODO: programatically get list of file types allowed
                        relSrc = os.path.join(os.path.dirname(src), file)
                        relDest = os.path.splitext(dest)[0] +\
                            os.path.splitext(file)[1]
                        if not os.path.exists(relDest):
                            self.lblSource.set_label(relSrc)
                            self.lblDest.set_label(relDest)
                            self.lblAction.set_label(_('Copying Related File'))
                            yield True
                            shutil.copy2(relSrc, relDest)
                            self.lblAction.set_label(_('Setting Related File Modification Time'))
                            yield True
                            self._touch(relDest,timeStamp)
                            # Delete associated source if enabled
                            if  self.conf['delete'] == 1:
                                self.lblAction.set_label(_('Deleting Related File Source'))
                                yield True
                                self._delete(relSrc)
            # Check if we need to exit
            if self.quitNow:
                if InputQuestion(self.main_widget,
                _('Do you realy want to stop the download process'),
                _("Jbrout Question"),
                (gtk.STOCK_NO, gtk.RESPONSE_CANCEL,
                 gtk.STOCK_YES, gtk.RESPONSE_OK)):
                    self.quit(True)
                    yield False
                else:
                    self.quitNow = False
        self.quit(True)
        yield False

    def _delete(self, file):
        """Simple function to delete the passed in file"""
        try:
            os.unlink(unicode(file))
        except os.error, detail:
            raise Exception(detail)

    def _touch(self, file, timeStamp):
        """
        Sets the dates/time stamps on the given file.

        Keyword arguments:
        file      - file to have it's date/time stamps set
        timeStamp - the datetime object containing the date/time that the file is to be set to
        """
        try:
            os.utime(file,(timeStamp,timeStamp))
        except OSError,detail:
            # utime doesn't work well if uid/gid are not the same
            # so we need to use the real touch ;-) (with mtime)
            print "need to touch ;-("
            stime = time.strftime("%Y%m%d%H%M.%S",time.localtime(timeStamp) )
            _Command._run( ["touch",'-t',stime,file] )
