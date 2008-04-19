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
#TODO: add ops : add/del from basket
#TODO: add ops : external tools



class WinShow(GladeApp):
    glade=os.path.join(os.path.dirname(os.path.dirname(__file__)),'data','jbrout.glade')
    #glade='data/jbrout.glade'
    window="WinShow"

    def init(self,storeTags, ln,idx,showInfo=True,isModify=False):
        self.ln=[]+ln
        self.idx=idx
        self.selected=[] # to be able to handle a new selection (reselect with space)
        self.removed=[]  # deleted items
        self.invalid=[]  # items with invalid thumbnail
        self.isBasketUpdate=False
        self.needInfo=showInfo
        self.isModify=isModify

        PixbufCache._file=None
        PixbufCache._cache=None
        


        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        ###################
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
        ###################

        self.tv_tags.append_column(column)
        treeselection = self.tv_tags.get_selection()
        treeselection.set_mode(gtk.SELECTION_NONE)


        self.tv_tags.set_model( storeTags )
        self.tv_tags.set_enable_search(False)
        self.tv_tags.set_state(gtk.CAN_FOCUS)

        storeTags.expander(self.tv_tags)
        storeTags.cleanSelections()
        #/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        self.viewer = ImageShow()

        self.hpShow.add2(self.viewer)

        image=gtk.Image()
        image.set_from_pixbuf(Buffer.pbBasket)
        image.show()

        self.basket.set_icon_widget(image)
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.main_widget.show_all()
        self.main_widget.fullscreen()

        self.draw()

    def on_eb_scroll_event(self,widget,b):
        if int(b.direction)==1:
            self.idx+=1
        else:
            self.idx-=1
        self.draw()
    def on_WinShow_key_press_event(self, widget, b):
        key= gtk.gdk.keyval_name(b.keyval).lower()
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
        #~ elif b.keyval == 65451: # +
            #~ self.zoom=min(self.zoom+1,10)
            #~ self.show()
        #~ elif b.keyval == 65453: # -
            #~ self.zoom=max(self.zoom-1,1)
            #~ self.show()
        elif key=="backspace":
            # clear selection
            self.selected=[]
            self.draw()
        elif key=="delete":
            # delete
            self.on_delete_clicked(None)    # and call draw
        elif key=="insert":
            self.needInfo = not self.needInfo
            self.draw()
        else:
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

            return 0

    def draw(self,invalid=False):
        """
        Draws the currently selected photo in the full screen view
        
        Keyword Arguments
        invalid - indicates if the cached image has been invalidated
        """
        
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
            print ltags
            folder=node.folderName
            resolution=info["resolution"]
            tags=", ".join(ltags)
            comment=info["comment"]
            exifdate=cd2rd(info["exifdate"])
    #        filedate=cd2rd(info["filedate"])
            filesize=format_file_size_for_display(info["filesize"])

            msg = _("""
%(exifdate)s

%(resolution)s, %(filesize)s

%(folder)s

TAGS :
%(tags)s

COMMENT :
%(comment)s

""") % locals()
        except Exception,m:
            msg = ""
            ltags=[]
            print m

        if self.isModify and not node.isReadOnly:
            self.delete.show()
        else:
            self.delete.hide()

        model=self.tv_tags.get_model()
        model.setSelected(ltags)

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
        d.image = PixbufCache().get(node.file,invalid)
        d.title = "%d/%d"%(self.idx+1,len(self.ln))
        try:
            self.lbl_info.set_text(msg)
        except Exception,m:
            self.lbl_info.set_text("")
            print "*ERROR* bad characters in jpeg info : ",m
        d.isSelected = (node in self.selected)
        d.nbSelected = len(self.selected)
        self.viewer.show( d )
        gc.collect()


    def on_WinShow_delete_event(self,*args):
        self.quit()

    def on_WinShow_button_press_event(self,*args):
        self.quit()

    def on_tv_tags_button_press_event(self, widget, *args):
        event=args[0]
        tup= widget.get_path_at_pos( int(event.x), int(event.y) )
        if self.isModify:
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
                                currentNode = self.viewer.display.node
                                if currentNode:
                                    # TODO : test if readonly
                                    # TODO : test jbrout.modify

                                    cv = model.get_value(iterTo,3)  # TODO : really bad way ! should be better done
                                    if cv == 1:
                                        currentNode.delTag(node.name)
                                    else:
                                        # add tag
                                        currentNode.addTag(node.name)
                                    self.draw()

                            return 1 # stop the propagation of the event

        return 0 # let the event propagation



    def on_tv_tags_row_activated(self, widget, *args):
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()
        if iter0:
            model.switch(iter0)

    def on_delete_clicked(self,*args):
        if self.isModify:
            node = self.ln[self.idx]
            #currentNode = self.viewer.display.node
            self.ln.remove(node)
            self.removed.append(node)
            if node in self.invalid:
                self.invalid.remove(node)
            self.draw()

    def on_basket_toggled(self,widget):
        currentNode = self.viewer.display.node
        if currentNode:
            if widget.get_active():
                currentNode.addToBasket()
            else:
                currentNode.removeFromBasket()
            self.isBasketUpdate=True
    
    def on_left_clicked(self,*args):
        """ Handles the rotate right button """
        self.__rotate("L")
    
    def on_right_clicked(self,*args):
        """ Handles the rotate right button """
        self.__rotate("R")
        
    def __rotate(self,sens):
        """
        Rotates the currently selected image using the selected sense

        Keyword argument:
        sens - Direction in witch to perform the rotation (L,R)
        """
        node = self.ln[self.idx]
        if self.isModify and not node.isReadOnly:
            node.rotate(sens)
            node=self.ln[self.idx]
            if node not in self.invalid:
                self.invalid.append(node)
            self.draw(True)
    
    def on_comment_clicked(self,*args):
        """Handles the comment button"""
        node = self.ln[self.idx]
        info = node.getInfo()
        comment=info["comment"]
        winComment = WinComment(comment)
        ret=winComment.loop()
        if ret[0]:
            node.setComment(unicode(ret[1]))
            self.draw()
        
class ImageShow(gtk.DrawingArea):
    def __init__(self):
        super(gtk.DrawingArea, self).__init__()
        self.connect("expose_event", self.expose)

        self.display = None

    def expose(self, widget, event):
        context = widget.window.cairo_create()

        # set a clip region for the expose event
        context.rectangle(event.area.x, event.area.y,
                               event.area.width, event.area.height)
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
                pb,x,y=render(self.display.image,rect.width,rect.height)
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


    def show(self,d):
        # store instance display
        self.display = d

        # and trig expose event to redraw all
        rect = self.get_allocation()
        self.queue_draw_area(0,0,rect.width,rect.height)

def fit(orig_width, orig_height, dest_width, dest_height,zoom):
    if orig_width == 0 or orig_height == 0:
        return 0, 0
    scale = min(dest_width/orig_width, dest_height/orig_height)
    if scale > 1:
        scale = 1
    scale*=zoom
    fit_width = scale * orig_width
    fit_height = scale * orig_height
    return int(fit_width), int(fit_height)

def render(pb,maxw,maxh):
    """ resize pixbuf 'pb' to fit in box maxw*maxh
        return the new pixbuf and x,y to center it
    """
    (wx,wy) = pb.get_width(),pb.get_height()
    dwx,dwy = fit(wx,wy,float(maxw),float(maxh),1)
    pb = pb.scale_simple(dwx,dwy,gtk.gdk.INTERP_NEAREST)
    x,y=(maxw/2)-(dwx/2),(maxh/2)-(dwy/2)
    return pb,x,y

class Display(object):
    """ container class to pass params """
    pass
    node=None

class PixbufCache(object):
    """ class to cache pixbuf by filename"""
    _cache=None
    _file=None
    def get(self,file,invalid=False):
        
        if file != PixbufCache._file or invalid: # TODO: Fix this to check modification
            PixbufCache._file = file
            if os.path.isfile(file):
                PixbufCache._cache=gtk.gdk.pixbuf_new_from_file(file)
            else:
                PixbufCache._cache=None

        return PixbufCache._cache

class WinComment(GladeApp):
    """ Creates and handles the dialog for Editing photo comments """
    glade=os.path.join(os.path.dirname(os.path.dirname(__file__)),'data','jbrout.glade')
    window="WinComment"
    
    def init(self,comment):
        """ Initalisation """
        self.tbufComment = self.txtComment.get_buffer()
        self.tbufComment.set_text(comment)
    
    def on_btnCancel_clicked(self,*args):
        """ Handles the Cancel button """
        self.quit(False,"")
    
    def on_btnOk_clicked(self,*args):
        """ Handles the rotate right button """
        start=self.tbufComment.get_start_iter()
        end =self.tbufComment.get_end_iter()
        self.quit(True,self.tbufComment.gset_mnemonic_modifieret_text(start,end,False))
        
    def on_WinGetComment_delete_event(self,*args):
        """ Handles window delete (close) events """
        self.quit(False,"")


if __name__ == "__main__":
    # self test
    pass

