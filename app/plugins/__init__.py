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
## URL : http://jbrout.python-hosting.com/wiki


import os,sys,traceback

"""

class JPlugin:
    __author__="undefined"
    __version__="undefined"

    def __init__(self,id,path):
        self.id = id
        self.path=path
"""
import gtk
from libs.i18n import createGetText
#~ from datetime import datetime

class JPlugins:
    path = "plugins"
    outputFullError=True

    def __init__(self,homePath=None):
        """ Initialize the plugins ...
            will create a list of instance in self.__plugins, from
            the plugins which sit in the current path

            if homePath is defined, it will try to import plugins from homePath
        """

        def fillPluginsFrom(folder):
            """ good old plugins importer """
            for id in os.listdir(folder):
                if id != "show":        #TODO: drop this line
                    path = folder+"/"+id
                    if id[0]!="." and os.path.isdir(path):
                        namespace = path.replace("/",".")

                        try:
                            # import the module plugin
                            module=__import__(namespace,[],[],["Plugin"])

                            # create the _() for __init__ plugins
                            module.__dict__["_"] = createGetText("plugin",os.path.join(path,"lang"))

                            # create an instance
                            instance = module.Plugin(id,path)

                            #add to the list
                            self.__plugins.append(instance)
                        except:
                            self.__plugError("in creation of '%s'"%(id,))

        def fillPluginsFrom2(folder):
            """ new home plugin importer """
            sys.path.append(folder)             # CHANGE SYS.PATH !!!!!!

            for id in os.listdir(folder):
                path = folder+"/"+id
                if id[0]!="." and os.path.isdir(path):

                    try:
                        # import the module plugin
                        module=__import__(id,[],[],["Plugin"])  # IMPORT ID !!!!!!!!!!!!

                        # create the _() for __init__ plugins
                        module.__dict__["_"] = createGetText("plugin",os.path.join(path,"lang"))

                        # create an instance
                        instance = module.Plugin(id,path)

                        #add to the list
                        self.__plugins.append(instance)
                    except:
                        self.__plugError("in creation of '%s'"%(id,))

        self.__plugins = []
        fillPluginsFrom(JPlugins.path)  # feed with the traditional plugins

        if homePath:
            homePlugins = os.path.join(homePath,JPlugins.path)
            if os.path.isdir(homePlugins):
                fillPluginsFrom2(homePlugins)  # feed with home plugins

    def __plugError(self,m=""):
        print >>sys.stderr,"PLUGIN ERROR : %s" % m
        if JPlugins.outputFullError:
            print >>sys.stderr,'-'*60
            traceback.print_exc(file=sys.stderr)
            print >>sys.stderr,'-'*60

    #def show(self,ln,idx):
    #    """
    #    find the first plugin which have the method showEntry
    #    and call it by passing ln and idx
    #    """
    #    find=False
    #    for instance in self.__plugins:
    #        if hasattr(instance,"showEntry"):
    #            find=True
    #            try:
    #                instance.showEntry(ln,idx)
    #            except:
    #                self.__plugError("%s.showEntry() is bugged "%instance.id)
    #
    #    if not find:
    #        print "no plugin to show"

    def menuEntries(self,l=[]):
        """ will return a ordered list of "menu entries" of plugins
            [ ( order, label, alter, callback, IMAGE ),  ... ]

            "l" can be the present selection of photonode
        """
        # get all the menuentries of plugins in --> a
        a=[]
        for instance in self.__plugins:
            try:
                if hasattr(instance,"menuEntries"):
                    menus = instance.menuEntries(l)
                else:
                    menus=[]
            except:
                self.__plugError("%s.menuEntries() is bugged "%instance.id)
                menus=[]

            for ordre,label,alter,callback,img in menus:
                a.append( (ordre,label,alter,callback,img,instance) )


        # sort them, according the "order" value
        a.sort( cmp=lambda a,b: cmp(a[0],b[0]) )

        # remakes the order (from 0), and place callback of callback, from a --> b
        b=[]
        for ord,nom,alter,callback,img,instance in a:
            pathImg = img and os.path.join(instance.path,img) or None
            b.append( (len(b),nom,alter,self.__callMenuEntry(callback,instance),pathImg ))
        return b


    def albumEntries(self,node):
        """ will return a ordered list of "album entries" of plugins
            [ ( order, label, alter, callback ),  ... ]

            "node" is a folder node
        """
        # get all the albumentries of plugins in --> a
        a=[]
        for instance in self.__plugins:
            try:
                if hasattr(instance,"albumEntries"):
                    menus = instance.albumEntries(node)
                else:
                    menus=[]
            except:
                self.__plugError("%s.albumEntries() is bugged "%instance.id)
                menus=[]

            for ordre,label,alter,callback in menus:
                a.append( (ordre,label,alter,callback,instance) )

        # sort them, according the "order" value
        a.sort( cmp=lambda a,b: cmp(a[0],b[0]) )

        # remakes the order (from 0), and place callback of callback, from a --> b
        b=[]
        for ord,nom,alter,callback,instance in a:
            b.append( (len(b),nom,alter,self.__callMenuEntry(callback,instance) ))
        return b


    def __callMenuEntry(self,callback,instance):
        """ callBack of callback .. to be able to control what appends while
            the call of the original callback
        """
        def myCallBack(*a,**k):

            old=__builtins__["_"]   # save the jbrout _()
            try:
                # for the .glade files
                from libs.gladeapp import GladeApp
                GladeApp.bindtextdomain("plugin",os.path.join(instance.path, 'lang'))

                # for the "_()" in "window gladeapp" code
                __builtins__["_"] = createGetText("plugin",os.path.join(instance.path,"lang"))

                ret=callback(*a,**k)
            finally:
                __builtins__["_"] = old # restore the jbrout _()
                pass
            return ret
        return myCallBack

    def __repr__(self):
        m="Plugins : %d\n" % len(self.__plugins)
        for i in self.__plugins:
            m+= "\tPlugin '%s %s' from %s: %s \n" % (i.id,i.__version__,i.__author__,i.__doc__)
        return m

if __name__=="__main__":
    j=JPlugins()
    for id,nom,alter,callback in j.menuEntries():
        print ">>>>>>>>>>> %d. '%s' (mod:%s)" % (id,nom,alter), callback
