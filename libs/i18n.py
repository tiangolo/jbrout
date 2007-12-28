# -*- coding: utf-8 -*-
##
##    Copyright (C) 2006 manatlan manatlan[at]gmail(dot)com
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

import locale,gettext

def createGetText(app_name, locale_dir):
    """ create the _() function for translation of 'app_name' in 'locale_dir'
        return the function
    """
    # make translation available in the code
    lc = locale.getdefaultlocale()[0]
    if lc:
        return gettext.translation (app_name, locale_dir, languages=(lc,), fallback=True).ugettext
    else:
        return lambda x: x

if __name__ == "__main__":
    pass
