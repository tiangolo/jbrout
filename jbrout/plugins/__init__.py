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
    def PhotosProcess(cls,lbl,icon=None,order=1000,alter=True,key=None):
        def _m(method):
            cls._saveMenu(method,"method",method.__name__)
            cls._saveMenu(method,"doc",method.__doc__)
            
            cls._saveMenu(method,"order",order)
            cls._saveMenu(method,"alter",alter)
            cls._saveMenu(method,"icon",icon)
            cls._saveMenu(method,"key",key)
            return cls._saveMenu(method,"label",lbl)
        return _m



    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    # decorators specifique pour les plugins "album"
    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
    @classmethod
    def AlbumProcess(cls,lbl,order=1000,alter=True,key=None):
        def _m(method):
            cls._saveAlbum(method,"method",method.__name__)
            cls._saveAlbum(method,"doc",method.__doc__)
            
            cls._saveAlbum(method,"order",order)
            cls._saveAlbum(method,"alter",alter)
            cls._saveAlbum(method,"key",key)
            return cls._saveAlbum(method,"label",lbl)
        return _m


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

    def __init__(self,homePath,conf):
        """ Initialize the plugins ...
            will create a list of instance in self.__plugins, from
            the plugins which sit in the current path

            if homePath is defined, it will try to import plugins from homePath
        """
        self.__conf = conf
        
        def fillPluginsFrom(folder):
            """ good old plugins importer """
            for id in os.listdir(folder):
                path = folder+"/"+id
                if id[0]!="." and os.path.isdir(path):
                    namespace = path.replace("/",".")
                    
                    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- to be run from here ;-)
                    namespace= re.sub("\.\.+","",namespace)
                    #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- manatlan
                    
                    old=__builtins__["_"]   # save the jbrout _()
                    try:
                        _trans = createGetText("plugin",os.path.join(path,"po"))
                        
                        __builtins__["_"] = _trans

                        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- reset the Entry def
                        Entry.definitions={}
                        #=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
                        
                        # import the module plugin
                        module=__import__(namespace,[_],[_],["Plugin"])

                        # create the _() for __init__ plugins
                        module.__dict__["_"] = _trans

                        # create an instance
                        instance = module.Plugin(id,path)

                        # and fill plugin contents in --> self.__plugins
                        self.__plugins[instance]=[]
                        for tupl,properties in Entry.definitions.items():
                            typ,methodName = tupl
                            
                            # define the callback (which go thru self.__caller) -> callback
                            method = getattr(instance,methodName)
                            callback = self.__caller(method,instance)

                            # correct dict of properties -> properties
                            for key,val in properties.items():
                                if key == "icon": # make absolute path for icon
                                    properties[key] = val and os.path.join(instance.path,val) or None

                            self.__plugins[instance].append( (typ,callback,properties) )
                        
                    except:
                        self.__plugError("in creation of '%s'"%(id,))
                    finally:
                        __builtins__["_"] = old
                        pass
                            

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

    def request(self,kind, isAlter=None, isKey=None, isIcon=None, all=False):
        """ request plugins
        
            WARNING : 'all'(bool) bypass config about plugin enabled/disabled
        """
        l=[]
        for instance,liste in self.__plugins.items():
            for typ,callback,properties in liste:
                if kind == typ:
                    l.append( (instance, callback, properties) )
        if not l: raise Exception("jPlugins.request() bad call, kind exists ?="+kind)
        
        if not all:
            ps=self.__conf["plugins"] or []
            l = [(i,c,p) for i,c,p in l if "%s.%s"%(i.id,p["method"]) in ps]
        
        if isAlter is not None:
            l = [(i,c,p) for i,c,p in l if p.get("alter","")==isAlter]
            
        if isIcon is not None:
            if isIcon:
                l = [(i,c,p) for i,c,p in l if p.get("icon",None) is not None]
            else:
                l = [(i,c,p) for i,c,p in l if p.get("icon",None) is None]


        if isKey is not None:
            if isKey:
                l = [(i,c,p) for i,c,p in l if p.get("key",None) is not None]
            else:
                l = [(i,c,p) for i,c,p in l if p.get("key",None) is None]
        
        l.sort( cmp=lambda a,b: cmp(a[2]["order"],b[2]["order"]))
        return l


    def __caller(self,callback,instance):
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
        m=[]
        for instance,liste in self.__plugins.items():
            m.append( "" )
            m.append( "Plugin %s (%s %s %s)"%(instance.id,instance.__author__,instance.__version__,instance.__doc__) )
            m.append( "-"*79)
            for typ,callback,properties in liste:
                m.append(  " - %s, %s, %s" % (typ,callback,properties) )
        return "\n".join(m)
        

if __name__=="__main__":
    JPlugins.path="."
    j=JPlugins()
    print j
    
    def aff(l):
        print "-"*30
        if l:
            for i in l:
                print i
        else:
            print "none"
            
    l=j.request("AlbumProcess")
    aff(l)

    l=j.request("PhotosProcess") # request all PhotosProcess 
    aff(l)

    l=j.request("PhotosProcess",isAlter=False)  # request PhotosProcess which don't change db/photos only !
    aff(l)

    l=j.request("PhotosProcess",isAlter=True)  # request PhotosProcess which change db/photos only !
    aff(l)

    l=j.request("PhotosProcess",isAlter=True,isKey=True)  # request PhotosProcess which change db/photos only and KEY only
    aff(l)
