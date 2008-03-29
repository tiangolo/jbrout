#!/usr/bin/env python
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
## URL : http://jbrout.googlecode.com

import os
import sys,time # to hack thread on win32

try:
    import subprocess
except ImportError:
    print "jbrout need python2.4 or +"
    sys.exit()

try:
    os.chdir(os.path.split(sys.argv[0])[0])
except:
    pass

#====
import pygtk
pygtk.require('2.0')
#====


import gtk
import locale

from libs.gladeapp import GladeApp
from libs.i18n import createGetText

# make translation available in the gui/gtk
GladeApp.bindtextdomain("jbrout",os.path.join(os.path.dirname(__file__), 'po'))

# make translation available in the code
__builtins__.__dict__["_"] = createGetText("jbrout",os.path.join(os.path.dirname(__file__), 'po'))


#=============================================================================


import gobject


try:
    __version__ = open(os.path.join(os.path.dirname(__file__),
        "data","version.txt")).read().strip()
except:
    __version__ = "src"




from jbrout.common import cd2rd,cd2d,format_file_size_for_display,runWith,openURL # for selecteur
from jbrout.commongtk import AlbumCommenter,InputBox,MessageBox,InputQuestion,Img,WinKeyTag,colorToString
from jbrout.db import JBrout,Buffer
from jbrout.winsearch import Winsearch
from jbrout.winshow import WinShow
from jbrout.listview import ThumbnailsView
from jbrout.externaltools import ExternalTools

import tempfile,shutil

import urllib,time,datetime,sys
import traceback, string, optparse


def myExceptHook(type, value, tb):
    sys.__excepthook__(type, value, tb)
    lines = traceback.format_exception(type, value, tb)
    MessageBox(None,string.join(lines),title=_("Jbrout Error"))

def beep(m):
    print >>sys.stdout,m

#class WinGetKey(GladeApp):
#    glade=os.path.join(os.path.dirname(__file__), 'jbrout.glade')
#    window="WinGetKey"
#    def init(self,k):
#        self.main_widget.set_modal(True)
#        self.main_widget.set_position(gtk.WIN_POS_CENTER)
#        if k: self.label.set_text(k)
#    def on_WinGetKey_key_press_event(self,w,e):
#        if e.keyval<1000:  # no big keys (return, arrows, alt, ctrl, shift ..)
#            key=gtk.gdk.keyval_name(e.keyval).lower()
#            self.label.set_text(key)
#    def on_btnCancel_clicked(self,*args):
#        self.quit(False)
#    def on_btnUndo_clicked(self,*args):
#        self.quit("")
#    def on_btnOk_clicked(self,*args):
#        self.quit(self.label.get_text())
#    def on_WinGetKey_delete_event(self,*a):
#        self.quit(False)


class JStyle:
    """ static class to handle jbrout colors """

    w = gtk.Window()    # create a fake window
    w.realize()         # realize it ...
    style=w.get_style() # ... to obtain the REAL theme style
    del(w)              # it's the only trick i've found

    # Normal text
    TEXT= colorToString(style.text[gtk.STATE_NORMAL])

    # grey text (folder without jpg, category, ...)
    TEXT_LOLIGHT = colorToString(style.fg[gtk.STATE_INSENSITIVE])

    # colored text (basket color ...)
    TEXT_HILIGHT = "#FF0000" #colorToString(style.bg[gtk.STATE_PRELIGHT])

    # input background
    BACKGROUND = colorToString(style.base[gtk.STATE_NORMAL])



#========================================================
class JPlugin:
#========================================================
    # JPlugin.parent : parent win (init at the start)

    class PlugConf:
        def __init__(self,myConf,myName):
            self.__conf = myConf
            self.__name = myName
        def __setitem__(self,n,v):
            self.__conf[self.__name+"."+n] = v
        def __getitem__(self,n):
            return self.__conf[self.__name+"."+n]

    def __init__(self,id,path):
        self.id=id
        self.path=path
        self.conf = JPlugin.PlugConf(JBrout.conf,id)

    def MessageBox(self,m,title=None):
        MessageBox(JPlugin.parent.main_widget,m,title)
    def InputBox(self,t,m,title=None):
        return InputBox(JPlugin.parent.main_widget,t,m,title)
    def InputQuestion(self,m,title=None):
        return InputQuestion(JPlugin.parent.main_widget,m,title)

    def openURL(self,url):
        return openURL(url)

    def showProgress(self,c=None,m=None,msg=None):
        JPlugin.parent.showProgress(c,m,msg)

    def getGeneralConfItem(self,n):
        """Permit to read General JBrout configuration parameter 'n' """
        return self.__conf[n]


#========================================================
class ListView(ThumbnailsView):
#========================================================

    choix = [_("Tags"),_("Comment"),_("Album"),_("Date"),_("Name")]

    def __init__(self, pere,allow_dragndrop):
        ThumbnailsView.__init__(self)
        self.parentWin = pere

        self.connect('key-press-event', self.on_key_press_for_tag)

        if allow_dragndrop:
            # allow drag
            self.drag_source_set(gtk.gdk.BUTTON1_MASK | gtk.gdk.BUTTON2_MASK,
                  [('to_albums', 0, 111),], gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

            # allow drop
            self.drag_dest_set(gtk.DEST_DEFAULT_ALL, [('from_tags', 0, 111),('from_ftags', 0, 112),],
                gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
            self.connect("drag_data_received",self.on_drag_data_received_data)

    def on_key_press_for_tag(self,widget,event):
        if JBrout.modify:
            nbSelected = len(self.selection)
            if nbSelected>0:
                if event.keyval<255 and event.string.strip()!="":
                    wk=WinKeyTag(_("Apply to %d photo(s)")%nbSelected,event.string,JBrout.tags.getAllTags())
                    ret=wk.loop()
                    if ret:
                        tag = ret[0]
                        self.parentWin.setTagsOnSelected(self,[tag,])
            self.grab_focus()

        #if JBrout.modify:
            #if self.parentWin.cbxUseTagKey.get_active():
            #    key=gtk.gdk.keyval_name(event.keyval).lower()
            #    t= JBrout.tags.getTagForKey(key)
            #    if t:
            #        self.parentWin.setTagsOnSelected(self,[t])
            #    self.grab_focus()

    def on_drag_data_received_data(self, widget, object,x,y,sdata,code,time):
        """ event drop notified """
        #~ code == 111 treeviewtags
        #~ code == 112 tvFilteredTags
        y+=self.get_vadjustment().get_value()
        cell_num = self.cell_at_position(x,y,False)
        if cell_num >=0:
            if cell_num not in self.selection:
                self.selection.set([cell_num])
            self.parentWin.on_selecteur_drop(self)

    def notify_selection_change(self,old):
        """ event selection changed """
        ThumbnailsView.notify_selection_change(self,old)

        nbSelected = len(self.selection)
        focusedItem = self.focus_cell
        #~ print "select change",self.selection.real_selection

        if nbSelected==1:
            try:
                photo_node = self.items[focusedItem]
                #info_text = photo_node.name+" - "+photo_node.resolution+" - "+cd2d(photo_node.date).strftime('%d %B %Y %H:%M')+ " - " + ", ".join(photo_node.tags)
                info_text = "%d/%d" % (focusedItem+1,len(self.items) )+" - "+photo_node.name+" - "+photo_node.resolution+" - "+cd2d(photo_node.date).strftime('%d %B %Y %H:%M')+ " - " + ", ".join(photo_node.tags)
            except:
                info_text=""
        elif nbSelected>0:
            info_text = _("%d/%d selected") % (nbSelected,len(self.items) )
        else:
            info_text = ""

        try:
            self.parentWin.label_image_infos.set_text(info_text)
        except:
            pass

    def getSelected(self):
        return [self.items[i] for i in self.selection.real_selection if i<len(self.items)]

    def setSelected(self,ln):
        if ln:
            lf=[i.file for i in self.items]     #build the list of filenames
            ls = [lf.index(i.file) for i in ln] #build the list of index
            lold=self.selection.real_selection  # save the old selection
            self.selection.set(ls)
            self.focus_cell=ls[0]
            self.scroll_to(self.focus_cell)
            self.notify_selection_change(lold)
            self.refresh()

    def reSelectFocus(self):
        if self.focus_cell < len(self.items) and self.items:
            self.setSelected( [self.items[self.focus_cell],] )

    def init(self,l,orderAscending=0):
        sclwin=self.get_parent()
        ss=sclwin.get_vscrollbar()
        ss.set_value(0)

        if orderAscending:
            l.sort( cmp=lambda x,y: cmp(x.date,y.date))
        else:
            l.sort( cmp=lambda x,y: -cmp(x.date,y.date))
        self.set_photos(l)

    def remove(self,n):
        #~ lold=self.selection.real_selection  # save the old selection
            #~ self.selection.set(ls)
            #~ self.focus_cell=ls[0]
            #~ self.scroll_to(self.focus_cell)
            #~ self.notify_selection_change(lold)
        idx=self.items.index(n)

        # ensure the real_selection follow
        if idx in self.selection.real_selection:
            self.selection.remove(idx)


        self.items.remove(n)

        # ensure the focus follow
        if self.focus_cell>=len(self.items):
            self.focus_cell=max(0,len(self.items) -1)
            self.scroll_to(self.focus_cell)

        self.refresh()

    def refresh(self):
        """ refresh the layout """

        self.notify_selection_change(self.selection.real_selection)   # redraw bottom line (in case of tagguing)

        #~ self.update_layout()
        self.invalidate_view()

    def get_text(self, idx):               # override !
        node = self.items[idx]

        a= [
            ", ".join(node.tags),
            node.comment,
            node.folderName,
            cd2rd(node.date),
            node.name
        ] [self.select]

        return a

    def is_thumb(self,idx):
        node = self.items[idx]
        return node.file in Buffer.images

    def get_thumb(self,idx):
        node = self.items[idx]
        if not self.is_thumb(idx):
            Buffer.images[node.file]=node.getThumb()
        pb=Buffer.images[node.file]

        if node.isInBasket:
            pb2 = pb.copy()
            Buffer.pbBasket.copy_area(0, 0, 15, 13, pb2, 7, 7)
            pb=pb2

        if node.isReadOnly:
            pb2 = pb.copy()
            wx= pb.get_width()
            Buffer.pbReadOnly.copy_area(0, 0, 15, 13, pb2, wx-22,7)
            pb=pb2

        return pb
#========================================================
class DateDB(gtk.TreeStore):
#========================================================
    def __init__(self):
        gtk.TreeStore.__init__(self, str,gtk.gdk.Pixbuf,str)

    def init(self,offset=0,today=False,selectDate=None):
        self.clear()

        if offset!=0:
            y=self.selectedDate.year
            m=self.selectedDate.month
            d=self.selectedDate.day


            if abs(offset)==1:
                m+=offset
                if m>12:
                    m=1
                    y+=1
                if m<1:
                    m=12
                    y-=1
            elif abs(offset)==12:
                y+=(offset/12)

            self.selectedDate = datetime.datetime(y,m,d)

        if today:
            t=datetime.datetime.now()
            self.selectedDate = datetime.datetime(t.year,t.month,1)
        if selectDate:
            t=selectDate
            self.selectedDate = datetime.datetime(t.year,t.month,1)

        ym = self.selectedDate.strftime("%Y%m")
        ln = JBrout.db.select("""//photo[substring(@date,1,6)="%s"]""" % ym)
        jour={}
        for node in ln:
            jour[ node.date[:8] ] = node

        jours = [i for i in jour.keys()]
        jours.sort()
        for i in jours:
            node = jour[i]
            d= datetime.datetime(int(i[:4]),int(i[4:6]),int(i[6:8]))
            date = unicode(d.strftime("%A %d"),locale.getpreferredencoding ())

            ymd = d.strftime("%Y%m%d")
            self.append(None,[date,node.getThumb().scale_simple(80,80,gtk.gdk.INTERP_NEAREST),ymd])

        return self.selectedDate

    def whichPos(self,d):
        ymd=d.strftime("%Y%m%d")
        cpt=0
        for nom,pb,yymmdd in self:
            if ymd==yymmdd:
                return cpt
            cpt+=1
        return None

#========================================================
class TreeDB(gtk.TreeStore):
#========================================================
    def __init__(self,filter=None):
        gtk.TreeStore.__init__(self, str,str,object,str)
        #~ self.fill(None,None)

        self.__filter=filter
        if filter==None or filter:  # to avoid filter=[] draw only the root
            self.init()

    def init(self):
        """ Init the tree and the basket (which will be refreshed) """
        self.clear()

        self.zapfill( JBrout.db.getRootFolder() ,None)

        self.__iterBasket = None
        self.activeBasket()

    def zapfill(self,node,attach):
        """ same as fill, but zap the beginning of the useless tree, and branch to fill """
        if node != None:
            folders = node.getFolders()
            photos = node.getPhotos()
            if len(folders)==1 and len(photos)==0: # zap the useless folders
                return self.zapfill(folders[0],attach)
            else:
                return self.fill(node,attach)

    def fill(self,node,attach):
        """ rebuild treestore from the nodefolder 'node' to the iter 'attach' """
        if node != None:
            folders = node.getFolders()

            new = self.add(attach,node )

            def isInFilter(f):
                for i in self.__filter:
                    if f==i[:len(ufile)]:
                        if i==f:
                            #exactly the one, so it's good
                            return True
                        else:
                            # perhaps a parent folder ?
                            if i[len(ufile)] in "\\/":
                                # yes !
                                return True
                return False

            for i in folders:
                if self.__filter!=None:
                    ufile = i.file
                    if isInFilter( ufile ):
                        self.fill(i,new)
                else:
                    self.fill(i,new)

            return new

    ## BUGGED in pygtk 2.10.3 on foreach/treeiter
    #~ def find(self,node):
        #~ """ return the 'iter' of the node in the model or None """
        #~ def _lookInside(model, path, iter0, rechNode):
            #~ node = model.get(iter0)
            #~ if node and node.file == rechNode.file:
                #~ _lookInside.ite = iter0
                #~ return True
        #~ _lookInside.ite=None
        #~ self.foreach( _lookInside, node )
        #~ return _lookInside.ite

    ## new version, with recursive process, to avoid bug (see below)
    def find(self,node):
        """ return the 'iter' of the node in the model or None """
        a = self.get_iter_root()
        while a:
            r=self.ffind(a,node)
            if r: return r
            a = self.iter_next(a)

    def ffind(self,it,node):
        nnode = self.get(it)

        if nnode and nnode.file == node.file:
            return it
        else:
            ic=self.iter_children(it)
            while ic:
                f=self.ffind(ic,node)
                if f:
                    return f
                else:
                    ic = self.iter_next(ic)



    def expander(self,tree):
        """ do the expand/collapse from the model(node) to the treeview 'tree' """
        def _expander(model, path, iter0, tree):
            node = model.get(iter0)
            if node and node.expand:
                tree.expand_row(path,False)
        self.foreach( _expander, tree )


    def get(self,it):
        """ get the 'node' of the iter 'it' """
        node = self.get_value(it,2)
        return node

    def set(self,it,node):
        """ set the 'node' of the iter 'it' """
        self.set_value(it,0,node.name)
        self.set_value(it,1,len(node.getPhotos()))
        self.set_value(it,2,node)

        color = len(node.getPhotos())>0 and JStyle.TEXT or JStyle.TEXT_LOLIGHT
        self.set_value(it,3,color)

    def add(self,it,node):
        """ append the 'node' to the iter """
        color = len(node.getPhotos())>0 and JStyle.TEXT or JStyle.TEXT_LOLIGHT

        return self.append(it,[node.name,len(node.getPhotos()),node,color])


    def activeBasket(self):
        if JBrout.db.isBasket():
            if self.__iterBasket:
                self.remove(self.__iterBasket)

            nb = len(JBrout.db.getBasket())
            self.__iterBasket = self.prepend(None,[_("Basket"),nb,None,JStyle.TEXT_HILIGHT])
        else:
            if self.__iterBasket:
                self.remove(self.__iterBasket)
            self.__iterBasket = None


#========================================================
class TreeTags(gtk.TreeStore):
#========================================================
    def __init__(self,filter=None):
        gtk.TreeStore.__init__(self, str,object,str,  int,str)
        self.__filter=filter  # to filter on tags in this list
        self.init()

    def init(self):
        self.clear()
        self.fill( JBrout.tags.getRootTag() ,None)


    def fill(self,node,attach):
        """ rebuild treestore from the catgnode 'node' to the iter 'attach' """
        catgs = node.getCatgs()
        tags = node.getTags()

        new = self.add(attach,node)
        for i in catgs:
            self.fill(i,new)

        for i in tags:
            if self.__filter!=None:
                # there is a filter (a tag list)
                if i.name in self.__filter:
                    self.add(new,i)
            else:
                self.add(new,i)

        if self.__filter!=None:
            # there is a filter, so we remove empty catg !!!
            if self.iter_children(new) == None:
                # the iter 'new' has no children, let's remove it
                self.remove(new)

    def find(self,name):
        """ return the 'iter' of the node 'name" in the model or None """
        def _lookInside(model, path, iter0, rechNode):
            node = model.get(iter0)
            if node and node.name==rechNode:
                _lookInside.ite = iter0
                return True
        _lookInside.ite=None
        self.foreach( _lookInside, name )
        return _lookInside.ite

    def expander(self,tree):
        """ do the expand/collapse from the model(node) to the treeview 'tree' """
        def _expander(model, path, iter0, tree):
            node = model.get(iter0)
            if node.__class__.__name__ == "CatgNode" and node.expand:
                tree.expand_row(path,False)
        self.foreach( _expander, tree )


    def get(self,it):
        """ get the 'node' of the iter 'it' """
        node = self.get_value(it,1)
        return node

    #def refreshKey(self,it):
    #    """ refresh the display ok the key'tag in the iter 'it' """
    #    node = self.get_value(it,1)
    #    self.set_value(it,4,self.__displayKey(node))

    def cleanSelections(self):
        """ clean selections in the tree """
        def _clean(model, path, iter0):
            model.set_value(iter0,3,0)
        self.foreach( _clean )


    def switch_inc(self,it):
        if self.get_value(it,3)!=1:
            self.set_value(it,3,1)
            dis=True
        else:
            self.set_value(it,3,0)
            dis=False

        self.__switchChilds(it,dis)

    def switch_exc(self,it):
        if self.get_value(it,3)!=2:
            self.set_value(it,3,2)
            dis=True
        else:
            self.set_value(it,3,0)
            dis=False

        self.__switchChilds(it,dis)

    def __switchChilds(self,it,dis):
        node = self.get_value(it,1)
        if node.__class__.__name__ == "CatgNode":
            ii=self.iter_children(it)
            while ii:
                if dis:
                    self.set_value(ii,3,3)
                    self.__switchChilds(ii,dis)
                else:
                    self.set_value(ii,3,0)
                    self.__switchChilds(ii,dis)
                ii = self.iter_next(ii)

    def getSelected(self):
        """ return a list of tuple (type_of_check,name,sons_or_self)
             - type_of_check : include or exclude
             - name : name of the branch (tag or catg)
             - sons_or_self : if it's a tag, it is its name, else (a catg), it's a list of tags descendant
        """
        ii=self.get_iter_root()
        ii=self.iter_children(ii)


        def getAllLeaves(ii):
            l=[]
            while ii:
                node = self.get_value(ii,1)
                if node.__class__.__name__ == "CatgNode":
                    l+=getAllLeaves(self.iter_children(ii))
                else:
                    l.append( node.name )
                ii = self.iter_next(ii)
            return l


        def par(ii):
            l=[]
            while ii:
                node = self.get_value(ii,1)
                tcheck = self.get_value(ii,3)
                if node.__class__.__name__ == "CatgNode":
                    if tcheck in (1,2):
                        l.append( (tcheck,node.name,getAllLeaves(self.iter_children(ii))) )
                    else:
                        l+=par(self.iter_children(ii))
                else:
                    if tcheck in (1,2):
                        l.append( (tcheck,node.name,node.name) )
                ii = self.iter_next(ii)
            return l

        return par(ii)


    def setSelected(self,ltags):
        """ set included for all TAGS in 'ltags'
            (used by winshow)
        """
        def _set(model, path, iter0):
            node=model.get_value(iter0,1)
            if node.__class__.__name__ == "TagNode" and node.name in ltags:
                model.set_value(iter0,3,1)
            else:
                model.set_value(iter0,3,0)
        self.foreach( _set )

    def __displayKey(self,node):
        return node.key and "(%s)"%node.key or ""

    def add(self,it,node):
        """ append the 'node' to the iter """
        if node.__class__.__name__ == "TagNode":
            return self.append(it,[node.name,node,JStyle.TEXT,0,self.__displayKey(node)])
        else:
            return self.append(it,["[%s]" % node.name,node,JStyle.TEXT_LOLIGHT,0,""])



#=============================================================================

class Window(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'data/jbrout.glade')
    window="window"

    def init(self):
        #=============================================================================
        if JBrout.conf["normalizeName"] == None:
            ret=InputQuestion(self.main_widget,
                _('Do you want JBrout to rename your imported photos according to their create timestamp (Recommended) ?'),
                buttons=(gtk.STOCK_NO, gtk.RESPONSE_CANCEL, gtk.STOCK_YES, gtk.RESPONSE_OK)
             )
            if ret:
                JBrout.conf["normalizeName"] = 1
            else:
                JBrout.conf["normalizeName"] = 0


        if JBrout.conf["normalizeNameFormat"] == None:              # key not present
            JBrout.conf["normalizeNameFormat"] = "p%Y%m%d_%H%M%S"   # set default

        if JBrout.conf["autorotAtImport"] == None:    # key not present
            JBrout.conf["autorotAtImport"] = 0        # set default


        JBrout.db.setNormalizeName( JBrout.conf["normalizeName"]==1 )
        JBrout.db.setNormalizeNameFormat( JBrout.conf["normalizeNameFormat"] )
        JBrout.db.setAutorotAtImport( JBrout.conf["autorotAtImport"]==1 )

        self.tagsInSelection=[]
        self.foldersInSelection=[]

        # create the listview with the right thumbsize
        table = ListView(self,JBrout.modify)
        table.connect('button-press-event', self.on_selecteur_mouseClick)

        # and init all static images
        Buffer.clear()


        # build the "plugins buttons"
        self.tooltips = gtk.Tooltips()
        canModify = JBrout.modify
        for ord,text,alter,callback,img in JBrout.plugins.menuEntries():
            if img:
                # try to detect if plugin are enable or not
                if canModify:
                    enableMenu = True
                else:
                    # jbrout doesn't allow modification
                    # so, only plugins not alter'able are enabled
                    enableMenu = not alter
                if enableMenu:
                    image=gtk.Image()
                    image.set_from_file(img)
                    image.show()

                    bb = gtk.ToolButton(image)
                    bb.set_tooltip(self.tooltips, text)
                    bb.connect("clicked", self.on_selecteur_menu_select_plugin,table,callback)
                    self.toolbar.insert(bb, 3)
                    bb.show()

        # build the status bar
        frame_default = self.statusbar.get_children()[0]
        self.label_image_infos= frame_default.get_children()[0]
        self.label_image_infos.set_text("welcome")

        progress_info_frame = gtk.Frame()
        progress_info_frame.set_shadow_type(gtk.SHADOW_IN)
        self.label_progress_infos = gtk.Label()

        self.progress_bar = gtk.ProgressBar()
        self.statusbar.pack_start(progress_info_frame, False, False, 0)
        hbox = gtk.HBox()
        hbox.pack_start(self.label_progress_infos, False, False, 5)
        hbox.pack_start(self.progress_bar, False, False, 0)
        progress_info_frame.add(hbox)
        hbox.show_all()

        self.statusbar.show_all()
        self.progress_bar.hide()

        self.main_widget.set_redraw_on_allocate(False)
        self.comment=AlbumCommenter(JBrout.modify)
        b=gtk.VBox()
        b.show()
        b.pack_start(self.comment,False,True,2)

        sclwin = gtk.ScrolledWindow()
        sclwin.set_policy(gtk.POLICY_NEVER, gtk.POLICY_ALWAYS)
        sclwin.add(table)
        sclwin.show()
        b.pack_start(sclwin)

        #~ self.hpaned1.add(b)
        self.hpanedView.remove(self.frameFilter)  # remove the frame
        #~ self.frameFilter.hide()                 # hide it
        self.hpanedView.pack1(b,True)                    # add the combo album/listview
        self.hpanedView.pack2(self.frameFilter,False)     # and so, re-add the frame
        #~ self.hpanedView.pack1(b,True)
        #~ self.hs_size.set_right_justified(True)

        table.show()
        table.grab_focus()
        self.tbl = table
        sclwin.set_shadow_type(1)
        self.hpaned1.set_focus_chain((self.tbl,))
        TARGET_STRING = 0
        TARGET_ROOTWIN = 1

        self.main_widget.set_title("JBrout "+__version__)

        if JBrout.modify:
            TARGETS = [
            ('MY_TREE_MODEL_ROW', gtk.TARGET_SAME_WIDGET, 0),
            #~ ('text/plain', 0, 1),
            ('TEXT', 0, 2),
            ('STRING', 0, 3),
            ]
            self.treeviewdb.enable_model_drag_source( gtk.gdk.BUTTON1_MASK,
                                                    [TARGETS[0]],
                                                    gtk.gdk.ACTION_DEFAULT|
                                                    gtk.gdk.ACTION_COPY)
            self.treeviewdb.enable_model_drag_dest([TARGETS[0]]+[("to_albums",0,0)],                 # can receive from self and selecteur
                                                 gtk.gdk.ACTION_DEFAULT)


            self.btn_addFolder.drag_dest_set(gtk.DEST_DEFAULT_ALL, [( 'text/uri-list', 0, 1 ),('text/plain', 0, 1)], # drag from os
                                            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)


            self.treeviewtags.enable_model_drag_source( gtk.gdk.BUTTON1_MASK|gtk.gdk.BUTTON2_MASK,
                                                    [TARGETS[0]]+[("from_tags",0,0)],               # drag on self and listview
                                                    gtk.gdk.ACTION_DEFAULT|
                                                    gtk.gdk.ACTION_COPY)
            self.tvFilteredTags.enable_model_drag_source( gtk.gdk.BUTTON1_MASK|gtk.gdk.BUTTON2_MASK,
                                                    [("from_ftags",0,0)],                            # drag on listview only !!
                                                    gtk.gdk.ACTION_DEFAULT|
                                                    gtk.gdk.ACTION_COPY)
            self.treeviewtags.enable_model_drag_dest([TARGETS[0]],          # can receive from self only
                                                 gtk.gdk.ACTION_DEFAULT)

            self.treeviewtags.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
            self.tvFilteredTags.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

            self.btn_addFolder.show()
        else:
            self.btn_addFolder.hide()

        ################
        #~ cell_renderer = gtk.CellRendererText()
        #~ column = gtk.TreeViewColumn("folder", cell_renderer,text=0,foreground=3)
        ################

        def filename(column, cell, model, iter):
            v=model.get_value(iter, 1)
            if int(v)>0:
                nb= "   (%s)" %v
            else:
                nb=""

            cell.set_property('text', model.get_value(iter, 0)+nb)
            cell.set_property('foreground', model.get_value(iter, 3))
            cell.set_property('xalign', 0)
            #~ cell.set_property('xpad', 1)
        def pixbuf(column, cell, model, iter):
            if model.get_value(iter, 2)==None:
                cell.set_property('pixbuf', Buffer.pbBasket)
            else:
                cell.set_property('pixbuf', Buffer.pbFolder)
            cell.set_property('width', 16)
            cell.set_property('xalign', 0)

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        #~ cellnb = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start(cellpb, False)
        column.pack_start(cell, False)
        #~ column.pack_end(cellnb, False)
        column.set_cell_data_func(cell, filename)
        column.set_cell_data_func(cellpb, pixbuf)
        #~ column.set_cell_data_func(cellnb, affnb)
        ################

        self.treeviewdb.append_column(column)

        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        #~ cellnb = gtk.CellRendererText()
        column = gtk.TreeViewColumn()
        column.pack_start(cellpb, False)
        column.pack_start(cell, False)
        #~ column.pack_end(cellnb, False)
        column.set_cell_data_func(cell, filename)
        column.set_cell_data_func(cellpb, pixbuf)
        #~ column.set_cell_data_func(cellnb, affnb)
        ################

        self.tvFilteredAlbums.append_column(column)

        #~ cell_renderer = gtk.CellRendererText()
        #~ column = gtk.TreeViewColumn("nb", cell_renderer,text=1)
        #~ self.treeviewdb.append_column(column)

        store = TreeDB()
        self.treeviewdb.set_model( store )
        store.expander(self.treeviewdb)


        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Tags", cell_renderer,text=0,foreground=2)
        self.treeviewtags.append_column(column)
        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Tags", cell_renderer,text=0,foreground=2)
        self.tvFilteredTags.append_column(column)

        #if JBrout.modify:
        #    # if modify enabled display keyboar shortcuts
        #    cell_renderer = gtk.CellRendererText()
        #    column = gtk.TreeViewColumn("Key", cell_renderer,text=4,foreground=2)
        #    self.treeviewtags.append_column(column)

        store = TreeTags()
        self.treeviewtags.set_model( store )
        store.expander(self.treeviewtags)


        cell_renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Dates", cell_renderer,text=0)
        self.selectDate.append_column(column)
        cellpb = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn("View", cellpb,pixbuf=1)
        self.selectDate.append_column(column)

        # prepare the date combo in "tab time"
        cell = gtk.CellRendererText()
        self.comboboxyear.pack_start(cell, True)
        self.comboboxyear.add_attribute(cell, 'text',0)
        # and fill it
        self.fillComboYear()

        # init the "tab time"
        m = DateDB()
        m.init(today=True)
        self.selectDate.set_model(m)

        # build the display menu *!*
        #----------------------------------------------------------
        menuDisplay=self.menuitem3.get_submenu()
        gitem=None
        for i in reversed(ListView.choix):
            item = gtk.RadioMenuItem(gitem,i)
            if not gitem: gitem = item
            idx = self.tbl.choix.index(i) + 1
            item.connect("activate",self.on_affichage_select,idx )
            if idx == (JBrout.conf["viewSelection"] or 5):
                self.tbl.select=idx
                item.set_active(True)
            item.show()
            menuDisplay.prepend(item)


        # get order from config
        self.menuAscending.set_active( JBrout.conf["orderAscending"]==1 )

        self.tvFilteredTags.connect("row_activated",self.on_treeviewtags_row_activated)
        self.tvFilteredAlbums.connect("row_activated",self.on_treeviewdb_row_activated)

        w,h=JBrout.conf["width"] or 800,JBrout.conf["height"] or 600

        if sys.platform[:3].lower()=="win":
            # work arround for bug in pygtk/gtk 2.10.6 on windows set default size
            # then reshow with initial (default) size instead of simple resize
            self.main_widget.set_default_size(w,h)
            self.main_widget.reshow_with_initial_size()
        else:
            self.main_widget.resize( w,h )

        self.hpaned1.set_position( JBrout.conf["hpaned"] or 160 )
        self.frameFilter.hide()

        self.hpanedView.set_position( -1 )
        self.hs_size.set_value( int(JBrout.conf["thumbsize"] or 160) )

        # define constant mode
        Window.MODEBASKET="basket"
        Window.MODEFOLDER="folder"
        Window.MODETIME="time"
        Window.MODETAG="tag"
        # and set it
        self.mode = Window.MODEFOLDER

        # init some attributs
        self.storeMultipleSelectedPathsOfTags=[]


        #=============================================================================

    def fillComboYear(self):
        """ fill the comboyear in tab "time" """
        drange=JBrout.db.getMinMaxDates()
        if drange:
            min,max=drange
            m=gtk.ListStore( str)
            m.clear()
            if min and max :
                for i in range(min.year,max.year+1):
                    m.append( [str(i),] )
            self.comboboxyear.set_model(m)

    def on_order_changed(self,*args):
        JBrout.conf["orderAscending"] = self.menuAscending.get_active() and 1 or 0

        # live change
        self.tbl.init(self.tbl.items,JBrout.conf["orderAscending"])

    def on_affichage_select(self,widget,idx):
        self.tbl.select=idx - 1
        self.tbl.refresh()

        label = self.menuitem3.get_children()[0]
        label.set_text(_("Display (%s)") % self.tbl.choix[idx-1])

        JBrout.conf["viewSelection"]=idx
        return True

    def showProgress(self,cur=None,max=None,msg=None):
        """
            to show a current process is pending ... 3 types of call:
            - showProgress(True) : block principal window (no msg, no win)
            - showProgress(cur,max,msg) : block principal window, and show a progress bar cur/max + msg
            - showProgress() : release principal window
        """

        def off():
            self.progress_bar.hide()
            self.main_widget.window.set_cursor(None)
            self.label_progress_infos.set_text('')
            #~ self.main_widget.set_sensitive(True)
            self.toolbar.set_sensitive(True)
            self.menubar.set_sensitive(True)
            self.notebook1.set_sensitive(True)
            self.tbl.set_sensitive(True)
            self.label_image_infos.set_sensitive(True)
            self.comment.set_sensitive(True)

        def on():
            cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
            self.main_widget.window.set_cursor(cursor)
            self.progress_bar.show()
            #~ self.main_widget.set_sensitive(False)
            self.toolbar.set_sensitive(False)
            self.menubar.set_sensitive(False)
            self.notebook1.set_sensitive(False)
            self.tbl.set_sensitive(False)
            self.label_image_infos.set_sensitive(False)
            self.comment.set_sensitive(False)

        if cur is None and max is None:
            self.tbl.start()#restart background process of listview
            off()
        else:
            if max is None:
                self.tbl.start()#restart background process of listview
                off()
            else:
                self.tbl.stop() #stop background process of listview
                on()
                if cur <= 0:
                    cur = 0.01
                elif cur >= max:
                    cur = max
                percent = float(cur)/max

                self.progress_bar.set_fraction(percent)
                self.label_progress_infos.set_text(msg)

                # in the future:
                # http://www.async.com.br/faq/pygtk/index.py?req=show&file=faq23.020.htp
                while gtk.events_pending():      # *!*
                    gtk.main_iteration(False)




    def SetSelection(self,title,ln,mode,withFilter=True):
        self.mode = mode
        self.main_widget.set_title(_("%s (%d photo(s))") % (title,len(ln)))
        self.tbl.init(ln,JBrout.conf["orderAscending"])
        if mode != Window.MODEFOLDER:
            self.comment.hide()

        if withFilter:
            self.refreshFilltered()

        self.tbl.grab_focus()

    def refreshFilltered(self):
        ln=self.tbl.items
        # feed albums from selection into --> f
        # feed taglist from selection into --> t
        t=set()
        f=set()
        for i in ln:
            t=t.union(i.tags)
            f=f.union([i.folder,])

        # store filtered tags and albums
        self.tagsInSelection = list(t)
        self.foldersInSelection = list(f)

        if self.cbxFilter.get_active():
            # if filter view is shown : fill trees
            store = TreeTags( self.tagsInSelection)
            self.tvFilteredTags.set_model( store )
            store.expander(self.tvFilteredTags)

            store = TreeDB( self.foldersInSelection )
            self.tvFilteredAlbums.set_model( store )
            store.expander(self.tvFilteredAlbums)


    ###################################################################################
    ## TREEVIEW DB
    ###################################################################################
    def selectAlbum(self,model,iter0,all=True,fromFilteredTree=False):
        if iter0:
            self.showProgress(True)
            try:
                path = model.get_path(iter0)
                node = model.get(iter0)
                if node:
                    # on a real folder
                    if all:
                        # get all photos and photos from children
                        ln = node.getAllPhotos()
                    else:
                        ln = node.getPhotos()
                    name = node.name
                    mode = Window.MODEFOLDER
                    self.comment.set(node)
                else:
                    # on the basket (perhaps ?! ;-)
                    ln = JBrout.db.getBasket()
                    name = _("Basket")
                    mode = Window.MODEBASKET

                if not fromFilteredTree:
                    self.treeviewdb.expand_to_path( path )
                    self.treeviewdb.set_cursor( path )
                self.SetSelection(name,ln,mode,not fromFilteredTree)
            finally:
                self.showProgress()
                pass

    def on_menu_rename(self,e):
        treeselection = self.treeviewdb.get_selection()
        model, iter0 = treeselection.get_selected()
        node = model.get(iter0)

        self.showProgress(True)
        ret = InputBox(self.main_widget,_("Rename folder"),node.name)
        self.showProgress()

        if ret and ret != node.name:
            if node.rename(ret):
                model.set(iter0,node)

                # delete from basket the photo which are moved
                model.activeBasket()

                self.selectAlbum(model,iter0)

    def on_menu_new_folder(self,e):
        treeselection = self.treeviewdb.get_selection()
        model, iter0 = treeselection.get_selected()
        node = model.get(iter0)

        self.showProgress(True)
        ret = InputBox(self.main_widget,_("New folder"),"")
        self.showProgress()

        if ret:
            newNode = node.createNewFolder(ret)
            if newNode:
                iter1=model.add(iter0,newNode)
                self.selectAlbum(model,iter1)

    def on_menu_refresh(self,e):
        Buffer.clear()

        treeselection = self.treeviewdb.get_selection()
        model, iter0 = treeselection.get_selected()
        node = model.get(iter0)

        parentIter = model.iter_parent(iter0)
        path = node.file.decode("utf_8")    # because node.file is utf_8 ;-(

        self.on_drop_folders_from_os(model,[path])

    def on_menu_delete_from_db(self,e):
        treeselection = self.treeviewdb.get_selection()
        model, iter0 = treeselection.get_selected()
        node = model.get(iter0)

        parentIter = model.iter_parent(iter0)
        node.remove()
        model.remove(iter0)

        # delete from basket the photo which are moved
        model.activeBasket()

        self.selectAlbum(model,parentIter)

    def on_menu_delete_from_disk(self,e):
        treeselection = self.treeviewdb.get_selection()
        model, iter0 = treeselection.get_selected()
        node = model.get(iter0)
        nbsubfiles = len(os.listdir(node.file))
        parentIter = model.iter_parent(iter0)

        self.showProgress(True)
        if nbsubfiles==0:
            question = _("Are you sure to delete this folder ?")
        else:
            question = _("Are you sure to delete this folder ?\n(This folder contains %d file(s))") % nbsubfiles
        ret = InputQuestion(self.main_widget,question)
        self.showProgress()
        if ret:
            if node.delete():
                model.remove(iter0)

                # delete from basket the photo which are moved
                model.activeBasket()

                self.selectAlbum(model,parentIter)


    def on_menu_remove_basket(self,e):
        JBrout.db.clearBasket()
        model = self.treeviewdb.get_model()
        model.activeBasket()
        self.tbl.refresh()


    def on_menu_select_only(self,e):
        treeselection = self.treeviewdb.get_selection()
        model, iter0 = treeselection.get_selected()
        self.selectAlbum(model,iter0,False)

    def on_drop_photos(self,model,iter0):
        node = model.get(iter0)

        self.tbl.hide()
        if node:
            # drop photos on a real folder
            for i in self.tbl.getSelected():
                nodeFolderParent = i.getParent()
                if nodeFolderParent.file != node.file: # don't move from the same folder ;-)
                    if i.moveToFolder(node):
                        self.tbl.remove(i)

                        # to set the counter from source
                        iterFolderParent = model.find( nodeFolderParent)
                        model.set(iterFolderParent,nodeFolderParent)
            # to set the counter to dest
            model.set(iter0,node)
        else:
            # drop photos on the basket
            for node in self.tbl.getSelected():
                node.addToBasket()
            self.tbl.refresh()

        self.tbl.show()
        model.activeBasket()
        self.tbl.reSelectFocus()


    def on_drop_folders_from_os(self,model,files):
        self.showProgress(0,1,"import") # not displayed
        try:
            newNodeFolder=None

            importedTags={}


            for folder in files:
                if os.path.isdir(folder):
                    iterator = JBrout.db.add( folder,importedTags )
                    total = iterator.next()
                    for nb in iterator:
                        if type(nb)==int and nb>=0:
                            self.showProgress(nb,total,_("Importing %d/%d")%(nb,total))
                    if nb:
                        newNodeFolder = nb

            if newNodeFolder: # at least one folder as be imported
                tags = importedTags.keys()
                if tags:
                    nbNewTags = JBrout.tags.updateImportedTags( tags )
                    if nbNewTags: # some are news !!!
                        tmodel = self.treeviewtags.get_model()
                        tmodel.init()
                        tmodel.expander(self.treeviewtags)
                        MessageBox(self.main_widget,_("%d tag(s) were added !") % nbNewTags)

                model.init( ) # redraw the full tree (+basket)
                model.expander(self.treeviewdb)
                newIterFolder = model.find( newNodeFolder )
                #~ print model.iter_is_valid(newIterFolder)

                self.selectAlbum(model,newIterFolder)
        finally:
            self.showProgress()



    def on_move_folder(self,model,ifrom,ito):
        nfrom = model.get(ifrom)
        nto = model.get(ito)
        if nto!=None:
            # drop on a real folder

            if nfrom !=None:
                # drag from a real folder
                if  InputQuestion(self.main_widget,_("Are you sure to move this folder here ?")):
                    new = nfrom.moveToFolder(nto)
                    if new:
                        model.remove(ifrom)
                        iter0=model.fill(new,ito)

                        self.selectAlbum(model,iter0)

                        # delete from basket the photo which are moved
                        model.activeBasket()
            else:
                # drag from the basket
                MessageBox(self.main_widget,_("Can't drag the basket to a folder"))
        else:
            # drop on the basket
            if nfrom !=None:
                # drag from a real folder
                for node in nfrom.getAllPhotos():
                    node.addToBasket()
                model.activeBasket()

                # refresh the photos view
                self.tbl.refresh()

    ###################################################################################
    ## SELECTEUR / LISTVIEW
    ###################################################################################

    def on_selecteur_mouseClick(self,widget,event): #sel,item,event):
        if event.button==3 and event.type == gtk.gdk.BUTTON_PRESS:

            def makeItem(nom,callback,selecteur):
                item = gtk.ImageMenuItem(nom)
                item.connect("activate",callback,selecteur)
                item.show()
                return item

            ln = widget.getSelected()

            # control if we can add/remove selected photos from basket -> can*
            # control if there is a readOnly file
            canBasketRemove=False
            canBasketAdd=False
            isThereAReadOnlyFile = False
            for node in ln:
                if node.isInBasket:
                    canBasketRemove = True
                else:
                    canBasketAdd = True

                if node.isReadOnly:
                    isThereAReadOnlyFile = True

            #detect if modification are allowed
            canModify = JBrout.modify and (not isThereAReadOnlyFile)

            menu = gtk.Menu()
            if canBasketAdd: # there are pictures which could be added to basket
                menu.append( makeItem(_("Add to Basket"), self.on_selecteur_menu_add_to_basket,widget) )
            if canBasketRemove: # there are pictures which could be removed basket
                menu.append( makeItem(_("Remove From Basket"), self.on_selecteur_menu_remove_from_basket,widget) )

            if len(ln)==1: # there is only one selected picture
                menu.append( makeItem(_("Select this folder"), self.on_selecteur_menu_select_folder,widget ))
                menu.append( makeItem(_("Select this time"), self.on_selecteur_menu_select_time,widget ))

            menu2 = gtk.Menu()
            isEntries = False
            for ord,text,alter,callback,img in JBrout.plugins.menuEntries(ln):
                # try to detect if plugin are enable or not
                if canModify:
                    enableMenu = True
                else:
                    # jbrout doesn't allow modification
                    # so, only plugins not alter'able are enabled
                    enableMenu = not alter

                if enableMenu:
                    item = gtk.ImageMenuItem( text )

                    if img:
                        ii=gtk.Image()
                        ii.set_from_file(img)
                        ii.show()
                        item.set_image(ii)

                    menu2.append(item)
                    item.connect("activate",self.on_selecteur_menu_select_plugin,widget,callback)
                    isEntries = True


            if isEntries:
                smenu2=gtk.ImageMenuItem(_("Operations"))
                smenu2.set_submenu(menu2)
                smenu2.show_all()
                menu.append(smenu2)

            # create menu entries for external tools
            menuET = gtk.Menu()
            isEntries=False
            listET = ExternalTools(JBrout.toolsFile)
            for et in listET:
                if canModify:
                    enableItem=True
                else:
                    enableItem=not et.canModify

                if enableItem:
                    item = gtk.ImageMenuItem( et.label )
                    menuET.append(item)
                    item.connect("activate",self.on_selecteur_menu_select_external_tool,widget,et)
                    isEntries=True

            if isEntries:
                smenuET=gtk.ImageMenuItem(_("External Tools"))
                smenuET.set_submenu(menuET)
                smenuET.show_all()
                menu.append(smenuET)


            # build the "delete tags" sub menu
            if canModify:
                # search all tags from selection, to present the delete tags menu
                d=[]
                for pnode in ln:
                    for t in pnode.tags:
                        if t not in d:
                            d.append(t)

                if d:
                    d.sort()
                    menu3 = gtk.Menu()
                    for tag in d:
                        item = gtk.ImageMenuItem( tag )
                        item.connect("activate",self.on_selecteur_menu_delete_tag,widget,tag)
                        menu3.append(item)
                    item = gtk.ImageMenuItem( _("** ALL **") )
                    item.connect("activate",self.on_selecteur_menu_delete_tag,widget,"*")
                    menu3.append(item)
                    smenu3=gtk.ImageMenuItem(_("Delete tag"))
                    smenu3.set_submenu(menu3)
                    smenu3.show_all()
                    menu.append(smenu3)

                menu.append( makeItem(_("Delete"), self.on_selecteur_menu_delete,widget ))

            menu.popup(None,None,None,event.button,event.time)
            return 1
        elif event.button==1 and event.type == gtk.gdk._2BUTTON_PRESS:
            # call the winshow

            l,i = widget.items,widget.focus_cell
            isInfo = JBrout.conf["showInfo"]==1 and True or False
            isModify = JBrout.modify
            w=WinShow(TreeTags(),l,i,isInfo,isModify)
            w.hpShow.set_position( int(JBrout.conf["viewertreewidth"] or 160) )
            w.loop()
            JBrout.conf["viewertreewidth"] = int(w.hpShow.get_position())
            JBrout.conf["showInfo"]=w.needInfo and 1 or 0

            if w.removed:
                sel = self.tbl.setSelected(w.removed)
                self.on_selecteur_menu_delete(None,self.tbl)

            if w.selected:  # perhaps a new desired selection
                sel = self.tbl.setSelected(w.selected)

            if w.isBasketUpdate:    #is basket updated ?
                model=self.treeviewdb.get_model()
                model.activeBasket()
            if w.invalid:   # remove invalidated thumbnails
                for i in w.invalid:
                    Buffer.remove(i.file)

            return 1

    def on_selecteur_menu_delete_tag(self,b,sel,tag):
        ln=sel.getSelected()
        try:
            for i in ln:
                self.showProgress(ln.index(i),len(ln),_("Deleting tags"))
                if tag=="*":
                    i.clearTags()
                else:
                    i.delTag(tag)
        finally:
            self.showProgress()
        sel.refresh()

    def on_selecteur_menu_add_to_basket(self,b,sel):
        ln = sel.getSelected()
        for node in ln:
            node.addToBasket()

        model=self.treeviewdb.get_model()
        model.activeBasket()
        sel.refresh()

    def on_selecteur_menu_remove_from_basket(self,b,sel):
        ln = sel.getSelected()
        for node in ln:
            node.removeFromBasket()
            if self.mode == Window.MODEBASKET:
                sel.remove(node)

        model=self.treeviewdb.get_model()
        model.activeBasket()
        sel.refresh()

    def on_selecteur_menu_select_folder(self,b,sel):
        ln = sel.getSelected()
        assert len(ln)==1
        node = ln[0]

        # select its folder
        self.notebook1.set_current_page(0)
        folderNode = node.getParent()
        model = self.treeviewdb.get_model()
        iterFolder = model.find( folderNode)
        self.selectAlbum(model,iterFolder)

        # and select the selected photo
        sel.setSelected([node])

    def on_selecteur_menu_select_time(self,b,sel):
        ln = sel.getSelected()
        assert len(ln)==1
        node = ln[0]

        # select its date
        d=cd2d(node.date)
        self.notebook1.set_current_page(1)
        model=self.selectDate.get_model()
        self.date_display_update(model.init(selectDate=d))
        pos=model.whichPos(d)
        if pos:
            treeselection = self.selectDate.get_selection()
            treeselection.select_path( pos )
            self.on_selectDate_row_activated(self.selectDate,None)
            self.selectDate.set_cursor( pos )   # set focus (ensure visible)


            # and select the selected photo
            sel.setSelected([node])


    def on_selecteur_menu_delete(self,b,sel):
        l = sel.getSelected()
        ret = InputQuestion(None,_("Delete %d photo(s) are you sure ?") % len(l))
        if ret:
            sel.hide()
            model = self.treeviewdb.get_model()
            for i in l:
                file = i.file
                folderNode = i.getParent()

                if i.delete():

                    # remove from buffer images
                    Buffer.remove(file)

                    # remove from the selection widget
                    sel.remove(i)

                    # to set the counter from source
                    iterFolderParent = model.find( folderNode)

                    model.set(iterFolderParent,folderNode)

            # delete from basket the photo which are moved
            model.activeBasket()

            # refresh the selection widget
            sel.show()
            sel.refresh()

            sel.reSelectFocus()

    def on_selecteur_menu_select_plugin(self,ib,listview,callback):
        l = listview.getSelected()
        if l:
            self.showProgress(True)
            try:
                #~ self.tbl.stop()
                ret=callback(l)
                #~ self.tbl.start()
            finally:
                self.showProgress()
            if ret:
                # perhaps a file was redated and renamed

                # let's suppress thumbnails in cache
                for i in l:
                    Buffer.remove(i.file)

                self.treeviewdb.get_model().activeBasket()
                listview.refresh()
                listview.refresh() # on win, the first call do nothing

    def on_selecteur_menu_select_external_tool(self,ib,listview,et):
        l = listview.getSelected()
        self.showProgress(True)

        destination=unicode(tempfile.mkdtemp(".tmp","jbrout"))

        # backup all files
        for pnode in l:
            # make a copy (to store all info)
            pnode.copyTo(destination)

        try:
            g=et.g_run(l)
            c=1
            while 1:
                self.showProgress( c, len(l) , et.label )
                c+=1
                if not g.next(): break
        finally:
            self.showProgress()

        # don't believe in et.__canModify, because all external tools are devils
        # for jbrout ;-) (so we are pretty sure that an external tool can't broke
        # some important internal infos)
        # so restore all infos (exif, iptc, jpeg header) and rebuild exif thumb
        for pnode in l:
            tmpfile = os.path.join(destination,pnode.name)
            try:
                pnode.getInfoFrom( tmpfile )
            except IOError:
                # file was deleted by external tools ? not cool
                # get back the file from temp dir
                shutil.move(tmpfile,pnode.file)


        try:
           shutil.rmtree(destination)
        except:
           pass

        for i in l:
            Buffer.remove(i.file)

        self.treeviewdb.get_model().activeBasket()
        listview.refresh()
        listview.refresh() # on win, the first call do nothing


    def on_selecteur_drop(self,sel):
        self.setTagsOnSelected(sel,self.dragTags)

    def setTagsOnSelected(self,sel,l):
        if l:

            ln = sel.getSelected()
            try:
                for i in ln:
                    self.showProgress(ln.index(i),len(ln),_("Adding tags"))
                    if i.isReadOnly:
                        beep(_("can't add tag to a readonly picture"))
                    else:
                        i.addTags(l)
            finally:
                self.showProgress()

            sel.refresh()
        #~ context, x, y, selection, info, time = args
        #~ dragFrom =context.get_source_widget().__class__.__name__
        #~ print dragFrom


    ###################################################################################
    ## TREEVIEW TAGS
    ###################################################################################
    def on_cbxFilter_toggled(self,widg,*args):
        if widg.get_active():
            self.frameFilter.show()
            self.refreshFilltered()
        else:
            self.frameFilter.hide()

    #def on_cbxUseTagKey_toggled(self,*args):
    #    self.tbl.grab_focus()


    # too complex to filter ..
    #~ def on_cbxTagsInSelection_toggled(self,w,*args):
        #~ if w.get_active():
            #~ def visible_func(model, iter, user_data):
                #~ print model.get(iter)
                #~ return True
            #~ ss=self.treeviewtags.get_model().filter_new()
            #~ ss.set_visible_func(visible_func,"koko")
            #~ self.treeviewtags.set_model(ss)
        #~ else:
            #~ pass

    def on_menu_add_tag(self,e):
        treeselection = self.treeviewtags.get_selection()
        model,paths = treeselection.get_selected_rows()
        if len(paths)==1:
            iter0 = model.get_iter(paths[0])
            node = model.get(iter0)

            self.showProgress(True)
            ret = InputBox(self.main_widget,_("New tag"),"")
            self.showProgress()

            if ret:
                newt = node.addTag(ret.strip())
                if newt:
                    newiter=model.add(iter0,newt)
                    path=model.get_path(newiter)
                    self.treeviewtags.expand_to_path( path )
                    self.treeviewtags.set_cursor( path )
                else:
                    MessageBox(self.main_widget,_("Tag already exists"))

    def on_menu_add_catg(self,e):
        treeselection = self.treeviewtags.get_selection()
        model,paths = treeselection.get_selected_rows()
        if len(paths)==1:
            iter0 = model.get_iter(paths[0])
            node = model.get(iter0)

            self.showProgress(True)
            ret = InputBox(self.main_widget,_("New category"),"")
            self.showProgress()

            if ret:
                newt = node.addCatg(ret.strip())
                if newt:
                    newiter=model.add(iter0,newt)
                    path=model.get_path(newiter)
                    self.treeviewtags.expand_to_path( path )
                    self.treeviewtags.set_cursor( path )
                else:
                    MessageBox(self.main_widget,_("Category already exists"))

    #def on_menu_set_key(self, e):
    #    treeselection = self.treeviewtags.get_selection()
    #    model,paths = treeselection.get_selected_rows()
    #    if len(paths)==1:
    #        iter0 = model.get_iter(paths[0])
    #        node = model.get(iter0)
    #
    #        if node.__class__.__name__ == "TagNode":
    #            w=WinGetKey(node.key)
    #            ret=w.loop()[0]
    #            if ret != False:
    #                if ret!="":
    #                    # try to verify if key is already in use
    #                    isInUse=JBrout.tags.getTagForKey(ret)
    #                else:
    #                    isInUse=False
    #
    #                if isInUse:
    #                    MessageBox(self.main_widget,_("This key is already in use"))
    #                else:
    #                    node.key=ret
    #                    model.refreshKey(iter0)

    def on_menu_delete_tags(self,e):
        treeselection = self.treeviewtags.get_selection()
        model,paths = treeselection.get_selected_rows()
        if len(paths)==1:
            iter0 = model.get_iter(paths[0])
            node = model.get(iter0)

            if node.__class__.__name__ == "TagNode":
                ln = JBrout.db.select("""//photo[t="%s"]""" % node.name)
                if len(ln)>0:
                    MessageBox(self.main_widget,_("This tag is in use"))
                else:
                    node.remove()
                    model.remove(iter0)

            else:
                ln = node.getTags() + node.getCatgs()
                if len(ln)==0:
                    node.remove()
                    model.remove(iter0)
                else:
                    MessageBox(self.main_widget,_("Category is not empty"))



    def date_display_update(self, date):
        # try to find the active item in the list -> act
        act=0
        m=self.comboboxyear.get_model()
        if m:
            for i in range(len(m)):
                if date.year == int(m[i][0]):
                    act=i

        # and set them
        self.comboboxyear.set_active(act)
        self.comboboxmonth.set_active(date.month-1)


    ###################################################################################




    def on_window_delete_event(self, widget, *args):
        #~ JBrout.conf["hpanedView"]=self.hpanedView.get_position()

        JBrout.conf["hpaned"] = self.hpaned1.get_position()
        JBrout.conf["width"],JBrout.conf["height"] = self.main_widget.get_size()
        JBrout.db.save()
        JBrout.tags.save()
        JBrout.conf.save()
        self.quit()


    def on_window_size_allocate(self, widget, *args):
        pass

    def on_editTools_activate(self,*args):
        if not os.path.isfile(JBrout.toolsFile):
            ExternalTools.generate(JBrout.toolsFile)
        runWith(["notepad.exe","leafpad","scite","gedit","kate"],unicode(JBrout.toolsFile))

    def on_search_activate(self, widget, *args):
        win_search = Winsearch( TreeTags(), self.main_widget )
        win_search.loop()

        if win_search.xpath:
            libl,xpath = win_search.xpath
            ln = JBrout.db.select(xpath)
            self.SetSelection(libl,ln,Window.MODETAG)



    def on_quitter_activate(self, widget, *args):
        self.on_window_delete_event(widget,*args)


    def on_help_activate(self,*args):
        try:
            import locale
            lang=locale.getdefaultlocale()[0][:2].lower()
            if lang!="fr":
                lang="en"
        except:
            lang="en"
        openURL(u"http://jbrout.free.fr/help/%s/" % lang)

    def on_a_propos_activate(self, widget, *args):
        about = gtk.AboutDialog()
        about.set_name('jbrout')
        about.set_version(__version__)
        about.set_copyright('Copyright 2005 Marc Lentz')
        about.set_license(open("data/gpl.txt").read())
        about.set_authors(['Marc Lentz',"","thanks to:", '- Frederic Peters',"- Erik Charlesson (french online help)","- Pieter Edelman (flickr uploader)"])
        about.set_website('http://jbrout.googlecode.com')
        def close(w, res):
            if res == gtk.RESPONSE_CANCEL:
                w.destroy()
        about.connect("response", close)
        #~ about.set_comments('handle your photos')
        about.show()


    def on_btn_addFolder_clicked(self, widget, *args):
        print "on_btn_addFolder_clicked called with self.%s" % widget.get_name()



    def on_btn_addFolder_drag_data_received(self, widget, *args):
        print "on_btn_addFolder_drag_data_received called with self.%s" % widget.get_name()



    def on_hs_size_value_changed(self, widget, *args):
        self.tbl.thumbnail_width = int(widget.get_value())
        JBrout.conf["thumbsize"] = int(widget.get_value())



    def on_notebook1_switch_page(self, widget, *args):
         gpoint,page= args
         if page==1: # tab "time"
             # perhaps we must change the "year interval" in tap "time" combo ...
             self.fillComboYear()

             date = self.selectDate.get_model().init()
             self.date_display_update(date)



    def on_treeviewdb_drag_data_received(self, widget, *args):
        context, x, y, selection, info, time = args

        dragFrom =context.get_source_widget().__class__.__name__

        if dragFrom == "TreeView":
            model = widget.get_model()
            if self.dragFolder:

                drop_info = widget.get_dest_row_at_pos(x, y)
                if drop_info:
                    path, position = drop_info
                    iterTo = model.get_iter(path)

                    _cur = iterTo
                    parents=[model.get_path(_cur)]
                    while 1:
                        _cur = model.iter_parent(_cur)
                        if _cur:
                            parents.append(model.get_path(_cur))
                        else:
                            break
                    if model.get_path(self.dragFolder) not in parents:
                        self.on_move_folder(model,self.dragFolder,iterTo)
                        self.dragFolder=None
                        context.finish(True, False, time)
                    else:
                        beep(_("Don't drop parents to a child"))
                else:
                    beep(_("Drop in space"))
            else:
                beep(_("Nothing was dragged"))
        elif dragFrom == "ListView":        # a photo to a folder
            drop_info = widget.get_dest_row_at_pos(x, y)
            model=widget.get_model()
            if drop_info:
                path, position = drop_info
                if position in [gtk.TREE_VIEW_DROP_INTO_OR_BEFORE,gtk.TREE_VIEW_DROP_INTO_OR_AFTER]:
                    iterTo = model.get_iter(path)
                    self.on_drop_photos(model,iterTo)
        else:
            beep(_("Drop from nowhere"))
        context.finish(True,False, time)

    def on_treeviewdb_row_expanded(self, widget, *args):
        iter0,path = args
        model = widget.get_model()
        node = model.get(iter0)
        node.setExpand(True)

    def on_treeviewdb_row_collapsed(self, widget, *args):
        iter0,path = args
        model = widget.get_model()
        node = model.get(iter0)
        node.setExpand(False)

    def on_treeviewdb_row_activated(self, widget, *args):
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()

        fromFilteredTree = (widget == self.tvFilteredAlbums)
        self.selectAlbum( model, iter0, fromFilteredTree = fromFilteredTree )

    def on_treeviewdb_drag_data_get(self, widget, *args):
        #~ context, selection, target_id,etime = args
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()
        self.dragFolder = iter0
    #
    #def on_treeviewdb_button_release_event(self, widget, *args):
    #    pass

    def on_treeviewdb_button_press_event(self, widget, event):
        def makeItem(nom,callback):
            item = gtk.ImageMenuItem(nom)
            item.connect("activate",callback)
            item.show()
            return item

        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()
        if iter0 and event.type == gtk.gdk.BUTTON_PRESS:

            node = model.get(iter0)

            if node!=None:
                # on a real folder
                if event.button==3:
                    menu = gtk.Menu()
                    menu.append( makeItem(_("Select only"),self.on_menu_select_only) )
                    if JBrout.modify:
                        menu.append( makeItem(_("Rename"),self.on_menu_rename) )
                        menu.append( makeItem(_("New folder"),self.on_menu_new_folder) )
                        menu.append( makeItem(_("Refresh"),self.on_menu_refresh) )
                        menu.append( makeItem(_("Remove from db"),self.on_menu_delete_from_db) )
                        menu.append( makeItem(_("Delete from disk"),self.on_menu_delete_from_disk) )

                    #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
                    # new album plugin
                    #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
                    menu2 = gtk.Menu()
                    isEntries = False
                    for ord,text,alter,callback in JBrout.plugins.albumEntries(node):
                        # try to detect if plugin are enable or not
                        if JBrout.modify:
                            enableMenu = True
                        else:
                            # jbrout doesn't allow modification
                            # so, only plugins not alter'able are enabled
                            enableMenu = not alter

                        if enableMenu:
                            item = gtk.ImageMenuItem( text )
                            item.connect("activate",self.on_album_menu_select_plugin,widget,callback)
                            menu2.append(item)
                            isEntries = True

                    if isEntries:
                        smenu2=gtk.ImageMenuItem(_("Operations"))
                        smenu2.set_submenu(menu2)
                        smenu2.show_all()
                        menu.append(smenu2)
                    #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
                    menu.popup(None,None,None,event.button,event.time)
                    return 1
                elif event.button==2:
                    self.selectAlbum(model,iter0,False)
                    return 1
            else:
                # on the basket
                if event.button==3:
                    menu = gtk.Menu()
                    menu.append( makeItem(_("Remove"),self.on_menu_remove_basket) )
                    menu.popup(None,None,None,event.button,event.time)
                    return 1
                elif event.button==2:
                    self.selectAlbum(model,iter0)
                    return 1

    def on_album_menu_select_plugin(self,ib,widget,callback):
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()

        if iter0:
            node = model.get(iter0)

            self.showProgress(True)
            try:
                ret=callback(node)
            finally:
                self.showProgress()
            if ret:
                # perhaps a file was redated and renamed
                self.on_menu_refresh(None)

                # delete from basket the photo which are moved
                model.activeBasket()

                #~ self.selectAlbum(model,iter0)

    def on_btn_addFolder_clicked(self, widget, *args):
        dialog = gtk.FileChooserDialog (_("Add Folder"),
             None, gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
             (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN,
              gtk.RESPONSE_OK))
        dialog.set_default_response (gtk.RESPONSE_OK)
        dialog.set_transient_for (self.main_widget)

        if sys.platform[:3].lower()=="win":
            default="c:\\"
        else:
            default=""

        # preselect the previous mount point
        dialog.select_filename (JBrout.conf["addFolderDefaultPath"] or default)

        response = dialog.run ()
        if response == gtk.RESPONSE_OK:
            folder = dialog.get_filename().decode( "utf_8" ) # gtk return utf8
            JBrout.conf["addFolderDefaultPath"] = folder
        else:
            folder = None
        dialog.destroy()


        if folder:
            self.on_drop_folders_from_os(self.treeviewdb.get_model(),[folder])



    def on_btn_addFolder_drag_data_received(self, widget, *args):

        #def get_file_path_from_dnd_dropped_uri(uri):
        #    path = urllib.url2pathname(uri) # escape special chars
        #    path = path.strip('\r\n\x00') # remove \r\n and NULL
        #
        #    # get the path to file
        #    if path.startswith('file:\\\\\\'): # windows
        #        path = path[8:] # 8 is len('file:///')
        #    elif path.startswith('file://'): # nautilus, rox
        #        path = path[7:] # 7 is len('file://')
        #    elif path.startswith('file:'): # xffm
        #        path = path[5:] # 5 is len('file:')
        #    return unicode(path)

        def get_file_path_from_dnd_dropped_uri(uri):    # rob wallace was here
            if sys.platform[:3].lower()=="win":
                if uri.startswith('file:///'):
                    uri = uri[8:] # 8 is len('file:///')
                elif uri.startswith('file:\\\\\\'):
                    uri = uri[8:] # 8 is len('file:///')
            else:
                if uri.startswith('file:///'): # nautilus, rox
                    uri = uri[7:] # 7 is len('file://')
                elif uri.startswith('file:'): # xffm
                    uri = uri[5:] # 5 is len('file:')
            path = urllib.url2pathname(uri) # escape special chars
            path = path.strip('\r\n\x00') # remove \r\n and NULL
            return unicode(path)


        context, x, y, selection, info, time = args

        # new way
        #----------------------------------
        list=[]
        uri = selection.data.strip()
        uri_splitted = uri.split() # we may have more than one file dropped
        for uri in uri_splitted:
            path = get_file_path_from_dnd_dropped_uri(uri)
            if os.path.isdir(path):
                list.append(path)

        if list:
            self.on_drop_folders_from_os(self.treeviewdb.get_model(),list)



    def on_btn_yl_clicked(self, widget, *args):
        self.date_display_update( self.selectDate.get_model().init(-12))



    def on_btn_ml_clicked(self, widget, *args):
        self.date_display_update(self.selectDate.get_model().init(-1))


    def on_btl_mm_clicked(self, widget, *args):
        self.date_display_update(self.selectDate.get_model().init(1))


    def on_btn_ym_clicked(self, widget, *args):
        self.date_display_update(self.selectDate.get_model().init(12))


    def on_selectDate_row_activated(self, widget, *args):
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()
        ymd = model.get_value(iter0,2)

        name = datetime.date(int(ymd[:4]), int(ymd[4:6]), int(ymd[6:8])).strftime('%A %e %B %Y')
        name = unicode(name,locale.getpreferredencoding ())

        self.showProgress(True)
        try:
            ln = JBrout.db.select("""//photo[substring(@date,1,8)="%s"]""" % ymd)
            self.SetSelection(name,ln,Window.MODETIME)
        finally:
            self.showProgress()



    def on_combodate_changed(self, widget, *args):
        try:
            year=int(self.comboboxyear.get_active_text())
            month = 1 + self.comboboxmonth.get_active()
            date = datetime.date(year, month, 1)
        except:
            date=None

        if date:
            self.date_display_update(self.selectDate.get_model().init(selectDate = date))



    def on_treeviewtags_row_activated(self, widget, *args):
        treeselection = widget.get_selection()
        model,paths = treeselection.get_selected_rows()
        if len(paths)==1:
            iter0 = model.get_iter(paths[0])
            node = model.get(iter0)
            if node.__class__.__name__ == "TagNode":
                tag = node.name
                xpath = 't="%s"'%tag
                npath = _("Tag %s")%tag
            else:
                l = [i.name for i in node.getAllTags()]
                if l:
                    xpath = " or ".join( ['t="%s"'%t for t in l] )
                    npath = _("Tags ")+(", ".join( ['%s'%t for t in l] ))
                else:
                    xpath=None

            withFilter = (widget == self.treeviewtags)

            if xpath:
                self.showProgress(True)
                try:
                    ln = JBrout.db.select("""//photo[%s]""" % xpath)
                    self.SetSelection(npath,ln,Window.MODETAG,withFilter)
                finally:
                    self.showProgress()


    def on_treeviewtags_row_collapsed(self, widget, *args):
        iter0,path = args
        model = widget.get_model()
        node = model.get(iter0)
        if node: # because can be None (TIS:tags in selection)
            node.setExpand(False)

    def on_treeviewtags_row_expanded(self, widget, *args):
        iter0,path = args
        model = widget.get_model()
        node = model.get(iter0)
        if node: # because can be None (TIS:tags in selection)
            node.setExpand(True)

    def on_treeviewtags_drag_data_get(self, widget, *args):
        context, selection, target_id,etime = args
        treeselection = widget.get_selection()
        model,paths = treeselection.get_selected_rows()
        iters = [model.get_iter(i) for i in paths]

        l=[]
        for i in iters:
            node = model.get(i)
            if node.__class__.__name__ == "TagNode":
                l.append(node.name)
            else:
                l.extend( [i.name for i in node.getAllTags()] )

        self.dragTags = l
        selection.set(selection.target, 8, "tags" )

    def on_treeviewtags_drag_data_received(self, widget, *args):
        context, x, y, selection, info, time = args

        dragFrom =context.get_source_widget().__class__.__name__

        model = widget.get_model()

        drop_info = widget.get_dest_row_at_pos(x, y)
        if drop_info:
            path, position = drop_info
            iterTo = model.get_iter(path)
            if self.dragTags:
                nodeTo = model.get(iterTo)
                if nodeTo.__class__.__name__=="TagNode":
                    beep(_("Don't drop tags on a tag"))
                else:
                    moved=False
                    for i in self.dragTags:
                        it = model.find(i)
                        node = model.get(it) # node can be a TagNode or a CatgNode

                        _cur = iterTo
                        parents=[model.get_path(_cur)]
                        while 1:
                            _cur = model.iter_parent(_cur)
                            if _cur:
                                parents.append(model.get_path(_cur))
                            else:
                                break

                        if model.get_path(it) not in parents:
                            node.moveToCatg(nodeTo)
                            moved=True
                        else:
                            beep(_("Tag/catg couldn't be a parent of the destination"))

                    if moved:
                        model.init()
                        model.expander(self.treeviewtags)

            else:
                beep(_("Nothing was dragged"))
        else:
            beep(_("Drop in space"))

        context.finish(True, False, time)

    def on_treeviewtags_button_release_event(self, widget, *args):

        def makeItem(nom,callback):
            item = gtk.ImageMenuItem(nom)
            item.connect("activate",callback)
            item.show()
            return item

        if JBrout.modify:
            event = args[0]
            treeselection = widget.get_selection()

            model,paths = treeselection.get_selected_rows()
            if len(paths)==1:
                iter0 = model.get_iter(paths[0])

                node = model.get(iter0)
                if node :
                    if event.button==3:
                        menu = gtk.Menu()
                        if node.__class__.__name__ == "CatgNode":
                            menu.append( makeItem(_("Add Tag"),self.on_menu_add_tag) )
                            menu.append( makeItem(_("Add Category"),self.on_menu_add_catg) )
                        #if node.__class__.__name__ == "TagNode":
                        #    menu.append( makeItem(_("Set keyboard shortcut"),self.on_menu_set_key) )
                        menu.append( makeItem(_("Delete"),self.on_menu_delete_tags) )
                        menu.popup(None,None,None,event.button,0)


    def on_treeviewtags_cursor_changed(self, widget, *args):
        if self.storeMultipleSelectedPathsOfTags:
            # redraw multiple selection
            treeselection = widget.get_selection()
            for path in self.storeMultipleSelectedPathsOfTags:
                treeselection.select_path(path)

    def on_treeviewtags_button_press_event(self, widget, *args):
        self.storeMultipleSelectedPathsOfTags = []
        if JBrout.modify: # if in modification, can select multiple tags
            event = args[0]
            tup = widget.get_path_at_pos( int(event.x), int(event.y) )
            if tup: # if click on something
                path,obj,x,y= tup
                if path: # if clicked on something
                    model = widget.get_model()
                    iterTo = model.get_iter(path)
                    if event.button==2: # with middle click
                        #we are going to make multiple selection

                        treeselection = widget.get_selection()

                        # select/unselect
                        if treeselection.iter_is_selected(iterTo):
                            treeselection.unselect_iter(iterTo)
                            ret=1   # stop propagation-event on unselect (to cancel drag'n'drop begin)
                        else:
                            treeselection.select_iter(iterTo)
                            ret=0   # leave propagation on select (to able d'n'd begin)

                        # save the current multiple selection ...
                        # thus we can reselect them in the event "cursor_changed", to be able
                        # to not loose them
                        model,paths = treeselection.get_selected_rows()
                        self.storeMultipleSelectedPathsOfTags = paths

                        return ret
                        #~ return ret


def main(canModify=True):
    if JBrout.lockOn():
        try:
            sys.excepthook = myExceptHook

            JBrout.init(canModify)

            #~ JBrout.db.redoIPTC()
            #~ JBrout.db.save()
            gtk.window_set_default_icon_from_file("data/gfx/jbrout.ico")
            window = Window()

            JPlugin.parent = window
            window.loop()
        finally:
            JBrout.lockOff()
    else:
        print "jbrout is already running (~/.jbrout/jbrout.lock)"
        sys.exit(1)

USAGE = """%s [options]
JBrout %s by Marc Lentz (c)2003-2007, Licence GPL2
http://jbrout.googlecode.com""" % ("%prog",__version__)

if __name__ == "__main__":
    try:
        parser = optparse.OptionParser(usage=USAGE, version=("JBrout "+__version__))
        parser.add_option("-v","--view",action="store_true",dest="view",
                            help="run in view mode only")

        (options, args) = parser.parse_args()

        if options.view:
            main(False)
        else:
            main()

    except KeyboardInterrupt:
        pass
    sys.exit(0)
