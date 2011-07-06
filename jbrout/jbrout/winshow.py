# -*- coding: utf-8 -*-
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
import gtk,gc,pango,gobject,os
from __main__ import Buffer,GladeApp,JBrout
from commongtk import WinKeyTag
from common import cd2rd,format_file_size_for_display
from jbrout.externaltools import ExternalTools
#TODO: add ops : add/del from basket
#TODO: add ops : external tools

class TagList(gtk.VBox):
    #TODO: this object need to display its parent Hscrollbar when needed (does'nt work ?!)
    def __init__(self,callbackRemove):
        #self.b = gtk.Button()
        #self.b.set_label("Test bouton")
        gtk.VBox.__init__(self)
        self.__callbackRemove = callbackRemove
        self.__tags= dict(JBrout.tags.getAllTags())

    def fill(self,ll):
        ll.sort(lambda a,b: cmp(a.lower(),b.lower()))
        self.__ll = ll
        self.__refresh()

    def __refresh(self):
        l=self.get_children()
        for a in l:
            a.destroy()
            del a

        for i in self.__ll:

            hb=gtk.HBox()
            lbl=gtk.Label()
            lbl.set_label("%s (%s)" %(i,self.__tags[i]))
            hb.pack_start(lbl,False,False)
            btn=gtk.Button()
            btn.set_label("X")
            btn.connect('button-press-event', self.__callbackRemove,i)
            hb.pack_end(btn,False)

            self.pack_start(hb,False)

        self.resize_children()
        self.show_all()



class WinShow(GladeApp):
    """ a window that displays an image in full screen
        it may switch to next/previous image
        WinShow receives a set of jbrout.db.PhotoNodes
    """
    glade=os.path.join(os.path.dirname(os.path.dirname(__file__)),'data','jbrout.glade')
    window="WinShow"

    def init(self, ln,idx,showInfo=True,isModify=False,selected=[]):
        self.ln=[]+ln
        self.idx=idx
        if len(selected)>1:
            self.selected=selected # to be able to handle a new selection (reselect with space)
        else:
            self.selected=[]
        self.removed=[]  # deleted items
        self.invalidThumbs=[]

        self.zoom=False

        self.win_width=0
        self.win_height=0
        self.pointer_position = (0,0,0,0) #x, y, screen_width, screen_height

        self.isBasketUpdate=False
        self.needInfo=showInfo
        self.isModify=isModify

        PixbufCache._file=None
        PixbufCache._cache=None

        self.taglist = TagList(self.on_remove_tag)
        self.sc_tags.add_with_viewport(self.taglist)

        self.viewer = ImageShow()

        self.hpShow.add2(self.viewer)

        image=gtk.Image()
        image.set_from_pixbuf(Buffer.pbBasket)
        image.show()

        self.basket.set_icon_widget(image)
        self.toolbar1.set_style(gtk.TOOLBAR_ICONS)

        #=======================================================================
        # put real plugins
        #=======================================================================
        self.tooltips = gtk.Tooltips()
        if isModify:
            l=JBrout.plugins.request("PhotosProcess",isIcon=True)
        else:
            l=JBrout.plugins.request("PhotosProcess",isIcon=True,isAlter=False)

        for instance,callback,props in l:
            image=gtk.Image()
            image.set_from_file(props["icon"])
            image.show()

            bb = gtk.ToolButton(image)
            txt = props["label"]
            if props["key"]: txt+=" (ctrl + %s)"%props["key"]
            bb.set_tooltip(self.tooltips, txt)
            bb.connect("clicked", self.on_selecteur_menu_select_plugin,callback)
            self.toolbar1.insert(bb, 3)
            bb.show()
        #=======================================================================


        self.main_widget.show_all()
        self.main_widget.fullscreen()
        self.main_widget.maximize()

        self.draw()

    def on_selecteur_menu_select_plugin(self,ib,callback):
        currentNode = self.ln[self.idx]
        if self.isModify and not currentNode.isReadOnly:

            ret=callback([currentNode,])   #TODO: try/cath here

            if ret: # if change have be done ...
                if currentNode not in self.invalidThumbs:
                    self.invalidThumbs.append(currentNode)

                self.draw(forceReload=True)

            #TODO: if plugin "redate" is called, we'll need to redraw "time tab"

    def on_eb_scroll_event(self,widget,b):
        #print "eb scroll event !"
        if int(b.direction)==1:
            self.idx+=1
        else:
            self.idx-=1
        self.draw()

    def on_WinShow_key_press_event(self, widget, b):
        key= gtk.gdk.keyval_name(b.keyval).lower()
        isCtrl = b.state & gtk.gdk.CONTROL_MASK
        if isCtrl:
            currentNode = self.ln[self.idx]
            if self.isModify and not currentNode.isReadOnly:
                pluginsWithKey = JBrout.plugins.request("PhotosProcess",isKey=True)
            else:
                pluginsWithKey = JBrout.plugins.request("PhotosProcess",isKey=True,isAlter=False)

            for instance,callback,props in pluginsWithKey:
                if props["key"]==key:
                    self.on_selecteur_menu_select_plugin("?!?",callback)   #TODO: what's ib ? see "?!?"
                    return 1
        else:
            if (key == "page_up") or (key == "up") or (key == "left"):
                self.idx-=1
                self.draw()
            elif (key == "page_down") or (key == "down") or (key == "right"):
                self.idx+=1
                self.draw()
            elif key=="home":
                self.idx=0
                self.draw()
            elif key=="end":
                self.idx=len(self.ln) -1
                self.draw()
            elif key=="escape":
                self.quit();

            elif key=="space":
                # add/remove this photo to selection
                node=self.ln[self.idx]
                if node in self.selected:
                    self.selected.remove(node)
                else:
                    self.selected.append(node)
                self.draw()
            elif key == "f11":
                self.on_zoom_toggled()
            elif key=="backspace":
                # clear selection
                self.selected=[]
                self.draw()
            elif key=="delete":
                # delete
                self.on_delete_clicked(None)    # and call draw
            elif key=="insert" or key=="f9":
                self.needInfo = not self.needInfo
                self.draw()
            else:
                # print key
                currentNode = self.ln[self.idx]
                if self.isModify and not currentNode.isReadOnly:
                    if b.keyval<255 and b.string.strip()!="":
                        wk=WinKeyTag(_("Apply to this photo"),b.string,JBrout.tags.getAllTags())
                        ret=wk.loop()
                        self.main_widget.fullscreen()
                        if ret:
                            tag = ret[0]
                            currentNode.addTag(tag)
                            self.draw()
                    elif b.string>='0' and b.string<='5':
                        # capture keypad 0-5 for rating
                        currentNode.setRating(int(b.string))
                        self.draw()

                return 0

    def draw(self,forceReload=False):
        """
        Draws the currently selected photo in the full screen view

        """
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        self.main_widget.window.set_cursor(cursor)

        gobject.idle_add( self._draw, forceReload )

    def _draw(self,forceReload):
        if self.idx >= len(self.ln):
            self.idx = len(self.ln)-1
        if self.idx < 0:
            self.idx = 0

        try:
            node = self.ln[self.idx]
        except IndexError:
            self.quit()
            return
        try:
            info = node.getInfo()
            ltags=info["tags"]
            folder=node.folderName
            filename=os.path.basename(node.file)
            resolution=info["resolution"]

            comment=info["comment"]
            exifdate=cd2rd(info["exifdate"])
    #        filedate=cd2rd(info["filedate"])
            filesize=format_file_size_for_display(info["filesize"])

            rating=info["rating"]

            msg = _("""
%(exifdate)s

%(resolution)s, %(filesize)s

FILENAME :
%(filename)s

ALBUM :
%(folder)s

RATING : %(rating)s/5

COMMENT :
%(comment)s

TAGS :
""") % locals()
        except Exception,m:
            msg = ""
            ltags=[]
            print m

        if self.isModify and not node.isReadOnly:
            self.delete.show()
        else:
            self.delete.hide()

        self.taglist.fill(ltags)

        d=Display()
        d.node = None
        self.viewer.display=d   # prevent toggle event
        self.basket.set_active(node.isInBasket)

        if self.needInfo:
            self.vb_info.show()
        else:
            self.vb_info.hide()

        d=Display()
        d.node = node
        if forceReload:
            d.image = PixbufCache().get(node,forceReload)
        else:
            d.image = PixbufCache().get(node)
        d.title = "%d/%d"%(self.idx+1,len(self.ln))
        try:
            self.lbl_info.set_text(msg)
        except Exception,m:
            self.lbl_info.set_text("")
            print "*ERROR* bad characters in jpeg info : ",m
        d.isSelected = (node in self.selected)
        d.nbSelected = len(self.selected)
        d.rating = rating
        self.viewer.show( d,self.zoom,self.pointer_position )
        gc.collect()

        self.main_widget.window.set_cursor(None)

    def on_WinShow_delete_event(self,*args):
        self.quit()

    def on_WinShow_button_press_event(self, widget, data):
        #print "winshow button press"
        screen_width, screen_height=data.window.get_size()
        pointer_x, pointer_y = data.get_coords()
        self.pointer_position=(pointer_x, pointer_y, screen_width,screen_height)
        #print "Type %s, button %s, x = %s,y = %s" % (data.type, data.button, self.pointer_position[0], self.pointer_position[1])
        if data.button == 1: #left click does zoom
            self.on_zoom_toggled()
        elif data.button == 2 : #center click
            self.quit()
        else: #button 3 closes
            self.quit()

    def on_remove_tag(self,widget,event,tag):
        currentNode = self.viewer.display.node
        currentNode.delTag(tag)
        self.draw()

    def on_delete_clicked(self,*args):
        if self.isModify:
            node = self.ln[self.idx]
            #currentNode = self.viewer.display.node
            self.ln.remove(node)
            self.removed.append(node)
            self.draw()

    def on_basket_toggled(self,widget):
        currentNode = self.viewer.display.node
        if currentNode:
            if widget.get_active():
                currentNode.addToBasket()
            else:
                currentNode.removeFromBasket()
            self.isBasketUpdate=True

    def on_zoom_toggled(self):
        self.zoom= not self.zoom
        self.draw()

class ImageShow(gtk.DrawingArea):
    def __init__(self):
        self.zoom=False
        self.pointer_position=(0,0,0,0) #x,y,window_width,window_height
        super(gtk.DrawingArea, self).__init__()
        self.connect("expose_event", self.expose)

        self.display = None

    def expose(self, widget, event):
        context = widget.window.cairo_create()

        # set a clip region for the expose event
        context.rectangle(event.area.x, event.area.y,
                               event.area.width, event.area.height)
        #print "expose : x:%s y:%s witdth:%s height:%s" %(event.area.x, event.area.y,event.area.width,event.area.height)
        context.clip()

        self.draw(context)

        return False

    def draw(self, context):
        fond=(0,0,0,0.4)
        rect = self.get_allocation()

        context.set_source_rgb(0,0,0)
        context.paint()

        if self.display:
            if self.display.image:
                context.save()
                #print self.zoom
                pb,x,y=render(self.display.image,rect.width,rect.height,self.zoom,self.pointer_position)
                context.set_source_pixbuf(pb,x,y)
                context.paint()
                context.restore()


            if self.display.title:
                context.set_source_rgba(*fond)
                context.rectangle(0,0,200,30)
                context.fill()

                title = self.display.title
                if self.display.isSelected:
                    context.set_source_rgb(1,1,0)
                    title+="*"
                else:
                    context.set_source_rgb(1,1,1)

                context.move_to(20,20)
                context.set_font_size(20)
                context.show_text(title)

                if self.display.nbSelected>0:
                    context.set_source_rgb(1,1,0)
                    context.rel_move_to(5,0)
                    context.set_font_size(12)
                    context.show_text(_("(%d selected)") % self.display.nbSelected)

                if self.display.rating:
                    context.move_to(rect.width-35, 20)
                    context.set_source_rgb(1,1,1)
                    context.set_font_size(12)
                    context.show_text((self.display.rating*"*")+((5-self.display.rating)*"-"))

            #if self.display.info:
            #    wx=200
            #    wy=400
            #    context.set_source_rgba(*fond)
            #    context.rectangle(rect.width-wx,rect.height-wy,wx,wy)
            #    context.fill()
            #
            #    context.move_to(rect.width-wx+5,rect.height-wy+5)
            #    context.set_source_rgb(1,1,1)
            #
            #    layout=context.create_layout ()
            #    layout.set_text(self.display.info)
            #    layout.set_font_description(pango.FontDescription ("courier 8"))
            #    layout.set_width((wx-5)*1000)
            #    layout.set_wrap(1)
            #    context.show_layout(layout)


    def show(self,d,zoom=False,pointer_position=()):
        # store instance display
        self.display = d
        self.zoom=zoom
        self.pointer_position=pointer_position

        # and trig expose event to redraw all
        rect = self.get_allocation()
        self.queue_draw_area(0,0,rect.width,rect.height)

def fit(orig_width, orig_height, dest_width, dest_height,zoom=False,pointer_position=(0,0,0,0)):
    if orig_width == 0 or orig_height == 0:
        return 0, 0
    scale = min(dest_width/orig_width, dest_height/orig_height)
    if scale > 1:
        scale = 1
    if zoom==True:
        scale=1
    #print "fit: zoom %s scale %s" % (zoom, scale)
    fit_width = scale * orig_width
    fit_height = scale * orig_height
    return int(fit_width), int(fit_height)

def render(pb,maxw,maxh,zoom=1,pointer_position=(0,0,0,0)):
    """ resize pixbuf 'pb' to fit in box maxw*maxh
        return the new pixbuf and x,y to center it
    """
    (wx,wy) = pb.get_width(),pb.get_height()
    dwx,dwy = fit(wx,wy,float(maxw),float(maxh),zoom)
    image_x, image_y = fit(wx,wy,float(maxw),float(maxh), False)
    pb = pb.scale_simple(dwx,dwy,gtk.gdk.INTERP_NEAREST)
    if pointer_position==(0,0,0,0) or zoom==False:
        ratiox=ratioy=1.0/2
    else:
        (mouse_x,mouse_y,screen_width,screen_height)=pointer_position

        mouse_x=max(mouse_x -(screen_width-maxw),0) #remove pane space
        mouse_x=max(mouse_x-(maxw-image_x)/2.0, 0)
        if mouse_x>image_x:
            mouse_x=image_x
        mouse_y=max(mouse_y -(screen_height-maxh),0) #remove eventual space
        mouse_y=max(mouse_y-(maxh-image_y)/2.0, 0)
        if mouse_y>dwy:
            mouse_y=dwy

        ratiox=1.0*(mouse_x/image_x)
        ratioy=1.0*(mouse_y/image_y)
    if zoom:
        x,y=maxw/2 - min(wx-maxw/2, max(maxw/2,dwx*ratiox)), maxh/2 - min(wy-maxh/2, max(maxh/2, dwy*ratioy))
    else:
        x,y=(maxw - dwx)*ratiox,(maxh - dwy)*ratioy

    return pb,x,y

class Display(object):
    """ container class to pass params """
    pass
    node=None

class PixbufCache(object):
    """ class to cache pixbuf by filename"""
    _cache=None
    _file=None
    def get(self,node,forceReload=False):
        file = node.file
        if file == PixbufCache._file :
            if forceReload:
                PixbufCache._cache=node.getImage()
        else:
            PixbufCache._file = file
            if os.path.isfile(file):
                try:
                    PixbufCache._cache=node.getImage()
                except Exception,m:
                    print "*WARNING* can't load this file : ",(file,),m
                    PixbufCache._cache=None
            else:
                PixbufCache._cache=None
        return PixbufCache._cache


#class WinComment(GladeApp):
#    """ Creates and handles the dialog for Editing photo comments """
#    glade=os.path.join(os.path.dirname(os.path.dirname(__file__)),'data','jbrout.glade')
#    window="WinComment"
#
#    def init(self,comment):
#        """ Initalisation """
#        self.tbufComment = self.txtComment.get_buffer()
#        self.tbufComment.set_text(comment)
#
#    def on_btnCancel_clicked(self,*args):
#        """ Handles the Cancel button """
#        self.quit(False,"")
#
#    def on_btnOk_clicked(self,*args):
#        """ Handles the rotate right button """
#        start=self.tbufComment.get_start_iter()
#        end =self.tbufComment.get_end_iter()
#        self.quit(True,self.tbufComment.gset_mnemonic_modifieret_text(start,end,False))
#
#    def on_WinGetComment_delete_event(self,*args):
#        """ Handles window delete (close) events """
#        self.quit(False,"")


if __name__ == "__main__":
    # self test
    pass

