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


from __main__ import Buffer,JBrout,GladeApp


from datetime import datetime,timedelta
import string

def mkpcom(valRech):    # photo comment
    valRech=unicode(valRech).encode("utf_16")
    sfrom = u"ABCDEFGHIJKLMNOPQRSTUVWXYZàâäéèêëïîôöûùüç"
    sto   = u"abcdefghijklmnopqrstuvwxyzaaaeeeeiioouuuc"
    valRech = valRech.translate( string.maketrans(sfrom.encode("utf_16"),sto.encode("utf_16")) ).decode("utf_16")
    return u"""contains(translate(c, "%s", "%s") ,"%s")""" % (sfrom,sto,valRech)

def mkacom(valRech):    # album comment
    valRech=unicode(valRech).encode("utf_16")
    sfrom = u"ABCDEFGHIJKLMNOPQRSTUVWXYZàâäéèêëïîôöûùüç"
    sto   = u"abcdefghijklmnopqrstuvwxyzaaaeeeeiioouuuc"
    valRech = valRech.translate( string.maketrans(sfrom.encode("utf_16"),sto.encode("utf_16")) ).decode("utf_16")
    return  u""" ( contains(translate(../c, "%s", "%s") ,"%s")""" % (sfrom,sto,valRech) +\
            u""" or contains(translate(../@name, "%s", "%s") ,"%s") )""" % (sfrom,sto,valRech)



def string2ops(chaine,callback):
    tmots=[]
    mots=[]
    l = chaine.strip().split(" ")
    for i in range(len(l)):
        mot = l[i].strip().lower()
        if mot:
            if mot[0] == "-":
                mots.append( u"not(%s)" % callback(mot[1:]) )
                tmots.append( _(u"NOT %s") % mot[1:])
            else:
                mots.append( callback(mot) )
                tmots.append( mot )
    return tmots,mots

#===

class Winsearch(GladeApp):
    glade= 'data/jbrout.glade'
    window="WinSearch"

    def init(self,storeTags,parent):
        try:
            min,max=JBrout.db.getMinMaxDates()
        except:
            min = datetime.now()
        self.__begin= min
        self.__end = datetime.now()

        t=(self.__end - self.__begin).days
        self.hs_from.set_range(0,t)
        self.hs_to.set_range(0,t)

        self.hs_from.set_increments(0.5, 30)
        self.hs_to.set_increments(0.5, 30)
        self.hs_from.set_value(1)
        self.hs_from.set_value(0)
        self.hs_to.set_value(t)

        #~ tooltips = gtk.Tooltips()
        #~ tooltips.set_tip(self.__lbl,nom)

        cell = gtk.CellRendererText()
        self.cb_format.pack_start(cell, True)
        self.cb_format.add_attribute(cell, 'text',0)

        self.setCombo(self.cb_format,["",_("Landscape"),_("Portrait")],0)

        ###################
        def filename(column, cell, model, iter):
            cell.set_property('text', model.get_value(iter, 0))
            cell.set_property('foreground', model.get_value(iter, 2))
            cell.set_property('xalign', 0)
            #~ cell.set_property('xpad', 1)
        def pixbuf(column, cell, model, iter):
            if model.get_value(iter, 3)==0:
                cell.set_property('pixbuf', Buffer.pbCheckEmpty)
            elif model.get_value(iter, 3)==1:
                cell.set_property('pixbuf', Buffer.pbCheckInclude)
            elif model.get_value(iter, 3)==2:
                cell.set_property('pixbuf', Buffer.pbCheckExclude)
            else:
                cell.set_property('pixbuf', Buffer.pbCheckDisabled)
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

        #~ self.tv_tags.append_column(column)

        try:
            self.tv_tags.set_model( storeTags )
            storeTags.expander(self.tv_tags)
            storeTags.cleanSelections()
        except:
            pass


        self.main_widget.set_transient_for(parent)
        w,h=JBrout.conf["search.width"] or 500,JBrout.conf["search.height"] or 400
        #self.main_widget.resize( w,h )
        # work arround for bug in pygtk/gtk 2.10.6 on windows set default size
        # then reshow with initial (default) size instead of simple resize
        self.main_widget.set_default_size(w,h)
        self.main_widget.reshow_with_initial_size()

        self.main_widget.resize_children()
        try:
            self.hpaned1.set_position( JBrout.conf["hpaned"] )
        except:
            self.hpaned1.set_position( 160 )
        self.main_widget.resize_children()
        self.main_widget.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

    def on_kk(self,widget,*args):
        pass

    def setCombo(self,obj,list,n):
        m=gtk.ListStore( str)
        m.clear()
        for i in list:
            m.append( [i,] )
        obj.set_model(m)

        obj.set_active(n)

    def getDateFromScale(self,val):
        return (self.__begin + timedelta(days=val)).date()

    def quitt(self):
        JBrout.conf["search.width"],JBrout.conf["search.height"] = self.main_widget.get_size()
        self.quit()


    def on_WinSearch_delete_event(self, widget, *args):
        self.xpath=None
        self.quitt()

    def on_tv_tags_button_press_event(self, widget, *args):

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

                if node.__class__.__name__ != "TagNode":
                    # we are on a category, there is an arrow at the beginning of
                    # the cell to set expand or collapse
                    # we must shift the xcell beginning
                    xcell+=16

                if x>xcell:
                    # click on the cell (not on the arrow)
                    if event.button==1:
                        model.switch_inc(iterTo)
                    elif event.button==3:
                        model.switch_exc(iterTo)
                    return 1 # stop the propagation of the event
                else:
                    # click nowhere or on the arrow ;-)
                    return 0 # let the event propagation


        #~ event=args[0]
        #~ click_info = widget.get_dest_row_at_pos( int(event.x), int(event.y) )
        #~ if click_info:
            #~ print event.type
            #~ model = widget.get_model()
            #~ path, position = click_info
            #~ print position, type(position)

            #~ iterTo = model.get_iter(path)
            #~ if event.button==2:
                #~ model.switch_inc(iterTo)
            #~ elif event.button==3:
                #~ model.switch_exc(iterTo)


    def on_tv_tags_row_activated(self, widget, *args):
        treeselection = widget.get_selection()
        model, iter0 = treeselection.get_selected()
        if iter0:
            model.switch(iter0)




    def on_btn_cancel_clicked(self, widget, *args):
        self.xpath=None
        self.quitt()



    def on_btn_valid_clicked(self, widget, *args):
        dt_from = self.getDateFromScale(self.hs_from.get_value())
        dt_to = self.getDateFromScale(self.hs_to.get_value())

        tops=[] #textual operands
        ops=[]
        if self.__begin.date()!=dt_from:
            ops.append(u"substring(@date,1,8)>='%s'" % dt_from.strftime('%Y%m%d'))
            tops.append(dt_from.strftime('From:%d/%m/%Y'))
        if self.__end.date()!=dt_to:
            ops.append(u"substring(@date,1,8)<='%s'" % dt_to.strftime('%Y%m%d'))
            tops.append(dt_to.strftime('To:%d/%m/%Y'))

        if self.cb_format.get_active()==1: # landscape
            ops.append( u"substring-before(@resolution, 'x')>substring-after(@resolution, 'x')" )
            tops.append(_("Format:Landscape"))
        if self.cb_format.get_active()==2: # portrait
            ops.append( u"substring-before(@resolution, 'x')<substring-after(@resolution, 'x')" )
            tops.append(_("Format:Portrait"))

        tcom,op = string2ops(self.e_pcom.get_text(), mkpcom)
        if op:
            ops+=op
            tops.append(_("comment(%s)") % _(" and ").join(tcom) )
        tcom,op=string2ops(self.e_acom.get_text(), mkacom)
        if op:
            ops+=op
            tops.append(_("album(%s)") % _(" and ").join(tcom) )

        store=self.tv_tags.get_model(  )
        if store:
            ll=store.getSelected()
            for tcheck,nom,l in ll:
                if type(l)==list:
                    orList = u" or ".join([u"t='%s'"%i for i in l])
                    if tcheck==1: #include
                        ops.append( u"(%s)" % orList )
                        tops.append(u"'%s'"%nom)
                    else: # ==2 #exclude
                        ops.append( u"not(%s)" % orList )
                        tops.append(_(u"NOT '%s'")%nom)
                else:
                    op = u"t='%s'"%l
                    if tcheck==1: #include
                        ops.append( op )
                        tops.append(u"'%s'"%nom)
                    else: # ==2 #exclude
                        ops.append( u"not(%s)" % op )
                        tops.append(_(u"NOT '%s'")%nom)

        if ops:
            self.xpath = u" and ".join(tops),u"//photo[%s]" % u" and ".join(ops)
        else:
            self.xpath = _(u"ALL"),u"//photo"

        self.quitt()



    def on_hs_to_change_value(self, widget, *args):
        print "on_hs_to_change_value called with self.%s" % widget.get_name()



    def on_hs_to_move_slider(self, widget, *args):
        print "on_hs_to_move_slider called with self.%s" % widget.get_name()



    def on_hs_to_value_changed(self, widget, *args):
        val=widget.get_value()
        if val<self.hs_from.get_value():
            self.hs_from.set_value(val)
        d=self.getDateFromScale(val)
        self.l_to.set_label( d.strftime( unicode(_("To %m/%d/%Y %A")).encode("utf_8") ) )

    def on_hs_from_change_value(self, widget, *args):
        evt,val = args

    def on_hs_from_move_slider(self, widget, *args):
        print "on_hs_from_move_slider called with self.%s" % widget.get_name()



    def on_hs_from_value_changed(self, widget, *args):
        val=widget.get_value()
        if val>self.hs_to.get_value():
            self.hs_to.set_value(val)
        d=self.getDateFromScale(val)
        self.l_from.set_label(  d.strftime( unicode(_("From %m/%d/%Y %A")).encode("utf_8") ) )





def main():
    win_search = Winsearch()

    win_search.loop()

if __name__ == "__main__":
    main()


