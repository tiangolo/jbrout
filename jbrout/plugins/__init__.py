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


import os,sys,traceback,re

"""

class JPlugin:
    __author__="undefined"
    __version__="undefined"

    def __init__(self,id,path):
        self.id = id
        self.path=path
"""
import gtk


class Entry(object):
    definitions={}

    @classmethod
    def _saveMenu(cls,method,n,v):
        k=("PhotosProcess",method.__name__)
        if k in cls.definitions:
            cls.definitions[k][n]=v
        else:
            cls.definitions[k]={n:v}
        return method

    @classmethod
    def _saveAlbum(cls,method,n,v):
        k=("AlbumProcess",method.__name__)
        if k in cls.definitions:
            cls.definitions[k][n]=v
        else:
            cls.definitions[k]={n:v}
        return method


    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # decorators specifique pour les plugins "photos"
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    @classmethod
    def PhotosProcess(cls,lbl,icon=None,order=1000):
        def _m(method):
            cls._saveMenu(method,"order",order)
            cls._saveMenu(method,"alter",True) # default option
            cls._saveMenu(method,"icon",icon)
            return cls._saveMenu(method,"label",lbl)
        return _m


    @classmethod
    def PhotosProcessDontAlter(cls,method):         # OPTIONNEL
        return cls._saveMenu(method,"alter",False)



    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # decorators specifique pour les plugins "album"
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    @classmethod
    def AlbumProcess(cls,lbl,order=1000):
        def _m(method):
            cls._saveAlbum(method,"order",order)
            cls._saveAlbum(method,"alter",True) # default option
            return cls._saveAlbum(method,"label",lbl)
        return _m

    @classmethod
    def AlbumProcessDontAlter(cls,method):         # OPTIONNEL
        return cls._saveAlbum(method,"alter",False)

try:
    from libs.i18n import createGetText
except:
    # run from here
    # so we mock the needed object/path
    sys.path.append("..")
    createGetText = lambda a,b : lambda x:x
    __builtins__.__dict__["_"] =createGetText("","")
    runWith=lambda x:x
    class JPlugin :
        Entry=Entry
        def __init__(self,i,p):
            self.id=i
            self.path=p



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
                        
                        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- to be run from here ;-)
                        namespace= re.sub("\.\.+","",namespace)
                        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- manatlan
                        
                        old=__builtins__["_"]   # save the jbrout _()

                        try:
                            __builtins__["_"] = createGetText("plugin",os.path.join(path,"po"))

                            #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- reset the Entry def
                            Entry.definitions={}
                            #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
                            
                            # import the module plugin
                            module=__import__(namespace,[_],[_],["Plugin"])

                            # create the _() for __init__ plugins
                            module.__dict__["_"] = createGetText("plugin",os.path.join(path,"po"))

                            # create an instance
                            instance = module.Plugin(id,path)

                            #add to the list
                            self.__plugins[instance]=Entry.definitions.copy()
                            
                        except:
                            self.__plugError("in creation of '%s'"%(id,))
                        finally:
                            __builtins__["_"] = old
                            

        #def fillPluginsFrom2(folder):
        #    """ new home plugin importer """
        #    sys.path.append(folder)             # CHANGE SYS.PATH !!!!!!
        #
        #    for id in os.listdir(folder):
        #        path = folder+"/"+id
        #        if id[0]!="." and os.path.isdir(path):
        #
        #            try:
        #                #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- reset the Entry def
        #                Entry.definitions={}
        #                #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        #                
        #                # import the module plugin
        #                module=__import__(id,[],[],["Plugin"])  # IMPORT ID !!!!!!!!!!!!
        #
        #                # create the _() for __init__ plugins
        #                module.__dict__["_"] = createGetText("plugin",os.path.join(path,"po"))
        #
        #                # create an instance
        #                instance = module.Plugin(id,path)
        #
        #                #add to the list
        #                self.__plugins[instance]=Entry.definitions.copy()
        #
        #            except:
        #                self.__plugError("in creation of '%s'"%(id,))

       
        self.__plugins = {}
        fillPluginsFrom(JPlugins.path)  # feed with the traditional plugins

        #if homePath:
        #    homePlugins = os.path.join(homePath,JPlugins.path)
        #    if os.path.isdir(homePlugins):
        #        fillPluginsFrom2(homePlugins)  # feed with home plugins




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
            [ ( order, id, label, alter, callback, IMAGE ),  ... ]

            "l" can be the present selection of photonode
        """
        # get all the menuentries of plugins in --> a
        a=[]
        for instance,newDef in self.__plugins.items():
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

            #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- new plugins system
            for k,v in newDef.items():
                typ,methodName = k
                if typ=="PhotosProcess":
                    callback = getattr(instance,methodName)
                    a.append( (v["order"],v["label"],v["alter"],callback,v["icon"],instance) )
            #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
        
        # sort them, according the "order" value
        a.sort( cmp=lambda a,b: cmp(a[0],b[0]) )

        # remakes the order (from 0), and place callback of callback, from a --> b
        b=[]
        for ord,nom,alter,callback,img,instance in a:
            pathImg = img and os.path.join(instance.path,img) or None
            b.append( (len(b),instance.id,nom,alter,self.__callMenuEntry(callback,instance),pathImg ))
        return b


    def albumEntries(self,node):
        """ will return a ordered list of "album entries" of plugins
            [ ( order, id, label, alter, callback ),  ... ]

            "node" is a folder node
        """
        # get all the albumentries of plugins in --> a
        a=[]
        for instance,newDef in self.__plugins.items():
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

            #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- new plugins system
            for k,v in newDef.items():
                typ,methodName = k
                if typ=="AlbumProcess":
                    callback = getattr(instance,methodName)
                    a.append( (v["order"],v["label"],v["alter"],callback,instance) )
            #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

        # sort them, according the "order" value
        a.sort( cmp=lambda a,b: cmp(a[0],b[0]) )

        # remakes the order (from 0), and place callback of callback, from a --> b
        b=[]
        for ord,nom,alter,callback,instance in a:
            b.append( (len(b),instance.id,nom,alter,self.__callMenuEntry(callback,instance) ))
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
                GladeApp.bindtextdomain("plugin",os.path.join(instance.path, 'po'))

                # for the "_()" in "window gladeapp" code
                __builtins__["_"] = createGetText("plugin",os.path.join(instance.path,"po"))

                ret=callback(*a,**k)
            finally:
                __builtins__["_"] = old # restore the jbrout _()
                pass
            return ret
        return myCallBack

    def __repr__(self):
        m="Plugins : %d\n" % len(self.__plugins)
        for i,d in self.__plugins.items():
            m+= "\tPlugin '%s %s' from %s: %s (new:%s)\n" % (i.id,i.__version__,i.__author__,i.__doc__,str(d))
        return m

if __name__=="__main__":
    JPlugins.path="."
    j=JPlugins()
    print j
    for ord,id,nom,alter,callback,img in j.menuEntries():
        print ">>>>>Photos >>> %s. '%s' (mod:%s)" % (id,nom,alter), callback,img
    for ord,id,nom,alter,callback in j.albumEntries(None):
        print ">>>>>Album >>>> %s. '%s' (mod:%s)" % (id,nom,alter), callback
