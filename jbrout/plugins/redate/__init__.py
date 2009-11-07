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


from __main__ import JPlugin

import datetime
from jbrout.common import cd2d


class Plugin(JPlugin):
    """to change the datetime of a photo"""

    __author__ = "manatlan"
    __version__ = "2.0"


    #def menuEntries(self,l):
    #    return [(2500,_("Change Datetime"),True,self.redate,None)]

    @JPlugin.Entry.PhotosProcess( _("Change Datetime"), order=2500 )
    def redate(self,list):
        from redate import Winredate

        Winredate.defaultDate = cd2d(list[0].date)
        win = Winredate()

        ret=win.loop()[0]
        if ret:
            method,value = ret
            if method == 'relative':
                vw,vd,vh,vi,vs = value
            try:
                for i in list:
                    self.showProgress( list.index(i), len(list) , _("Redating") )
                    if method == 'relative':
                        i.redate(vw,vd,vh,vi,vs)
                    else:
                        i.setDate(value)
            finally:
                self.showProgress()

            return True
        else:
            return False
