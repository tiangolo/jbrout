#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" clean the jbrout folder """

import os
from libs import megarun

def clean():
    megarun(""" find jbrout -name "*.pyc" | xargs rm -fr
                find jbrout -name "*.orig" | xargs rm -fr
                find jbrout -name "*.rej" | xargs rm -fr
                find jbrout -name "*.bak" | xargs rm -fr
                find jbrout -name "*.gladep" | xargs rm -fr
                find jbrout -name "*.*~" | xargs rm -fr
                """)

if __name__ == "__main__":
    #==========================================================================
    # CHDIR at the root of svn (to able to read full changelog, and make
    # relaative path for py2deb)
    #==========================================================================
    os.chdir(os.path.join(os.path.dirname(__file__),".."))


    #==========================================================================
    # clean the source
    #==========================================================================
    clean()
