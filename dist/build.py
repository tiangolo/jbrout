#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    the build process is done with py2deb (http://manatlan.infogami.com/py2deb)
    it will build the packages DEB, RPM and SRC at the root of svn

"""
import sys,os,re,stat
from libs import run,megarun

try:
    from py2deb import Py2deb
except ImportError:
    print "you'll need Py2deb to run this (http://manatlan.infogami.com/py2deb)"


def walktree (top = ".", depthfirst = True):
    names = os.listdir(top)
    if not depthfirst:
        yield top, names
    for name in names:
        try:
            st = os.lstat(os.path.join(top, name))
        except os.error:
            continue
        if stat.S_ISDIR(st.st_mode):
            for (newtop, children) in walktree (os.path.join(top, name), depthfirst):
                yield newtop, children
    if depthfirst:
        yield top, names



if __name__ == "__main__":

    version ="0.3"

    #==========================================================================
    # CHDIR at the root of svn (to able to read full changelog, and make
    # relaative path for py2deb)
    #==========================================================================
    os.chdir(os.path.join(os.path.dirname(__file__),".."))


    #==========================================================================
    # clean the source
    #==========================================================================
    megarun(""" find jbrout -name "*.pyc" | xargs rm -fr
                find jbrout -name "*.orig" | xargs rm -fr
                find jbrout -name "*.rej" | xargs rm -fr
                find jbrout -name "*.bak" | xargs rm -fr
                find jbrout -name "*.gladep" | xargs rm -fr
                find jbrout -name "*.*~" | xargs rm -fr
                """)


    #==========================================================================
    # compile the sources
    #==========================================================================
    import compileall # http://effbot.org/zone/python-compile.htm
    compileall.compile_dir("jbrout", force=1)


    #==========================================================================
    # get the revision number -> v
    #==========================================================================
    try:
        version+="."+re.search("(\d+)\.$",run(["svn","update"])).groups(0)[0]
        open("jbrout/data/version.txt","w").write(version)
    except:
        version="src"


    #==========================================================================
    # get the log -> log
    #==========================================================================
    try:
        log=run(["svn","log"])
    except:
        log=""



    #==========================================================================
    # Collect all jbrout files -> list
    #==========================================================================
    path="jbrout"
    list=[]
    for (basepath, children) in walktree(path,False):
        for child in children:
            if ".svn" not in basepath:  # don't take .svn
                if not child.lower().endswith(".exe"):  # don't take exe (win32only)
                    rpath = os.path.join(basepath, child)
                    if os.path.isfile(rpath):
                        list.append(rpath)

    #==========================================================================
    # make the version with revision
    #==========================================================================

    p=Py2deb("jbrout")
    p.author="manatlan"
    p.mail="manatlan@gmail.com"
    p.description="""jBrout is a photo manager, written in python/pygtk under the GPL licence.
It's cross-platform, and has been tested on GNU/linux and windows XP/2k.
jBrout is able to :
    * manage albums/photos (= folders/files)
    * tag photos with IPTC keywords
    * use internal jpeg thumbnail
    * comment photos (with jpeg comment) and album (textfile in folder)
    * rotate loss-less jpeg (and internal exif jpeg thumbnail)
    * use EXIF info (date, size ..)
    * search pictures (tags, comment, date, ...)
    * use plugins (to export to html/gallery, to act like a httpserver, to send ftp/mail, export to picasaweb/flickr ...)
    * work without database ! (just a xmlfile which can be rebuild from scratch)
    * can manage a lot of photos
    * ...
    """
    p.url = "http://jbrout.free.fr"
    p.depends="python, python-lxml, python-gtk2, python-glade2, python-imaging, exiftran, jhead"
    p.license="gpl"
    p.section="graphics"
    p.arch="all"

    # install freedekstop icon
    p["/usr/share/applications"]=["dist/data/jbrout.desktop|jbrout.desktop "]

    # install jbrout launcher
    p["/usr/bin"]=["dist/data/jbrout|jbrout"]

    # install jbrout application
    p["/usr/lib"]=list


    p.generate(version,log,src=True,rpm=True)
