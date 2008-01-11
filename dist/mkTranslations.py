#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    this will generate pot files and compile po/mo files
    for jbrout
    for each plugin
"""


import os,sys

import time,string
from subprocess import Popen,PIPE
def run(cmds):
    p = Popen(cmds, shell=False,stdout=PIPE,stderr=PIPE)
    time.sleep(0.01)    # to avoid "IOError: [Errno 4] Interrupted system call"
    out = string.join(p.stdout.readlines() ).strip()
    outerr = string.join(p.stderr.readlines() ).strip()
    return out

def megarun(m):
    ligne = m.split("\n")
    for i in ligne:
        i=i.strip()
        if i:
            print ">>",i
            os.system(i)


import os,sys,stat
from fnmatch import fnmatch

def glob(path,exts=[],excludes=[],includes=[],absolute=True):
    #-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
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
    #-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    if exts:
        lexts=[i.lower() for i in exts]

    path=os.path.normpath(path)
    list=[]
    for (basepath, children) in walktree(path,False):
        for child in children:
            add=True
            rpath = os.path.join(basepath[len(path)+1:], child)

            if includes:
                add=False
                for i in includes:
                    if fnmatch(rpath,i):
                        add = True
                        break
                if not add:
                    continue

            if excludes:
                for i in excludes:
                    if fnmatch(rpath,i):
                        add = False
                        break
                if not add:
                    continue

            if exts:
                if child.split(".")[-1].lower() not in lexts:
                    continue

            if add:
                if absolute:
                    file = os.path.join(basepath, child)
                else:
                    file = rpath
                list.append( file.decode( sys.getfilesystemencoding() ) )

    return list


if __name__ == "__main__":
    #==========================================================================
    # CHDIR at the root of jbrout app
    #==========================================================================
    os.chdir(os.path.join(os.path.dirname(__file__),"..","jbrout"))


    #==========================================================================
    # Update and compile PO/MO of jbrout
    #==========================================================================
    # extract glade in tmp/*.h
    for i in glob(".",["glade"],excludes=["plugins/*"]):
        megarun('intltool-extract -l --type=gettext/glade %s'%i)

    # build a POTFILES.in for py and tmp/*.glade.h
    l=glob(".",["h","py"],excludes=["plugins/*"],absolute=False)
    open("po/POTFILES.in","w").write("\n".join(["[encoding: UTF-8]"]+l+[""]))

    # update the pot file
    megarun("""
        cd po; intltool-update --pot --gettext-package=jbrout
        rm -rf tmp
        rm po/POTFILES.in
        """)

    # updates all po file, and compile to mo
    for i in glob("po",["po"]):
        f=i[:-3]

        megarun("""
            msgmerge -q -U %(i)s po/jbrout.pot
            msgfmt %(f)s.po -o %(f)s.mo
            msgfmt --statistics %(i)s
            rm messages.mo
            """ % locals() )

    #==========================================================================
    # Update and compile PO/MO of plugins
    #==========================================================================
    path="plugins"
    plugins = [path+"/"+i for i in os.listdir(path) if i[0]!="." and os.path.isdir(path+"/"+i)]

    for path in plugins:

        print "plugins '%s'" % path

        # extract glade in tmp/*.h
        for i in glob(path,["glade"],excludes=["plugins/*"]):
            megarun('intltool-extract -l --type=gettext/glade %s'%i)

        # build a POTFILES.in for py and tmp/*.glade.h of plugin
        l=glob(".",["h","py"],includes=[path+"*","tmp/*"],absolute=False)

        open("po/POTFILES.in","w").write("\n".join(["[encoding: UTF-8]"]+l+[""]))

        # update the pot file
        megarun("""
            cd po; intltool-update --pot --gettext-package=plugin
            rm -rf tmp
            rm po/POTFILES.in
            """)

        # and place the plugin.pot in its folder !!!
        poDir=os.path.join(path,"po")
        if not os.path.isdir(poDir):
            os.mkdir(poDir)
        os.rename("po/plugin.pot",poDir+"/plugin.pot")

        for i in glob(path,includes=["*.po"]):
            f=i[:-3]

            megarun("""
                msgmerge -q -U %(i)s %(poDir)s/plugin.pot
                msgfmt %(f)s.po -o %(f)s.mo
                msgfmt --statistics %(i)s
                rm messages.mo
                """ % locals() )
