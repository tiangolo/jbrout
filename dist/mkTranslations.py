#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    this will generate pot files and compile po/mo files
    for jbrout
    for each plugin
"""
import os
from libs import run,megarun,glob

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
