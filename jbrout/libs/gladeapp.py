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
"""
======================================================================
GLADEAPP ... "dynamic simple tepache method", by manatlan (c) 2006
======================================================================

just subclass GladeApp like this :

--------------------------------
class window(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'window.glade')

    def init(self,x,y):
        pass

    def on_button1_clicked(self,*args):
        print "hello"

    def on_window1_delete_event(self, *args):
        self.quit("exit")
--------------------------------

so you can instantiate window, by passing params x,y to .init() method :

    w = window(12,13)

and decide to loop it (needed for the first window !!!)
(if a loop already running, a new window will be displayed in the already exixting loop)

    ret = w.loop()

and get back the tuple value returned by the .quit() method (the .exit() method force quit all)
(quit() can take arguments only if win is in loop ... for the returned value)

gladeapp will autoconnect signals and warn when missing a binding method
if there is multiple window defined in glade, you must specify it like this :

--------------------------------
class window(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'window.glade')
    window = "window1"
    ...
--------------------------------

changelog
16/9/2006
   - try/except on the quit() ... sometimes __inloop was problematic
"""
import pygtk
pygtk.require ('2.0')
import gtk
import gtk.glade
import gtk.gdk
import gobject
from xml.dom.minidom import parse, parseString

import re
import os
import sys


class GladeApp:
    __win=[]

    def __init__(self,*args,**dargs):
        n=self.__class__.__name__
        assert hasattr(self,"glade"), "*ERROR* manque attribut 'glade' dans '%s'"%n
        assert hasattr(self,"init"), "*ERROR* manque methode 'init' dans '%s'"%n

        # recupere la liste des windows du glade -> l
        x=parse(self.glade)
        l=[(i.getAttribute("id"),i) for i in x.documentElement.childNodes if i.nodeType == i.ELEMENT_NODE]
        assert len(l)>=1,"*ERROR* pas de widget dans le .glade"

        # controle le matching object avec une ou la window du glade
        if len(l)>1:
            theId,theNode=None,None
            assert hasattr(self,"window"), "*ERROR* manque attribut 'window' dans '%s' (car le glade en possede plusieurs)"%n
            for id,node in l:
                if self.window == id:
                    theId,theNode=id,node
                    break;
            assert theNode!=None, "*ERROR* l'attribut 'window' dans '%s' ne correspond a aucune window dans le .glade"%n
        else:
            theId,theNode=l[0]

        # verifi que ses events sont presents
        for i in re.findall(r"""<signal handler="([^"]+)" """,theNode.toxml()):
            if not hasattr(self,i):
                print "*WARNING* manque methode dans '%s'"%n
                print "    def %s(self,*args):" % i

        # chargement du glage
        self.__xml = gtk.glade.XML(self.glade,theId)

        # autoconnect les signaux
        self.__xml.signal_autoconnect(self)

        # autodéfini les attributs (objets)
        self.main_widget=None
        l=self.__xml.get_widget_prefix("")
        for w in l:
            name = gtk.Widget.get_name(w)
            if name == theId:
                self.main_widget = w
            else:
                setattr(self, name,w )

        assert self.main_widget != None, "main_widget not found ?!?"

        # et appel la methode init, en passant les arguments !
        obj=getattr(self,"init")
        obj(*(args),**(dargs))

        # stock la win en session
        GladeApp.__win.append(self)

        self.__inLoop=None


    def loop(self):
        self.__return=None
        if self in GladeApp.__win:
            GladeApp.__win.remove(self)

        # run a loop
        self.__inLoop=gobject.MainLoop()
        self.__inLoop.run()

        return self.__return

    def quit(self,*a,**k):
        """ handle the main quit
        (count instance, and when at zero : real quit ! (except loop)
        """
        try:                            # *NEW*

            if self.__inLoop:
                # if was in loop, quit loop properly
                self.main_widget.destroy()
                self.__return=a                         # pass the args
                gobject.MainLoop.quit(self.__inLoop)    # quit the loop
                self.__inLoop=None
            else:
                assert not a,"*ERROR* Cette fenetre ne loop pas! pas d'args"
                if self in GladeApp.__win:
                    GladeApp.__win.remove(self)
                    self.main_widget.destroy()

        except AttributeError:          # *NEW*
            self.main_widget.destroy()  # *NEW*

    def exit(self,ret=0):
        """ exit direct """
        sys.exit(ret)

    @staticmethod
    def setDefaultIcon(file):
        gtk.window_set_default_icon_from_file(file)

    @staticmethod
    def bindtextdomain(app_name,locale_dir):
        # make translation available in the glade
        gtk.glade.bindtextdomain(app_name, locale_dir)
        gtk.glade.textdomain(app_name)


