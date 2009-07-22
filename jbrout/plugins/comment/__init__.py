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

class Plugin(JPlugin):
    """Plugin to change the comment of pictures (mass or one by one)"""

    __author__ = "manatlan"
    __version__ = "1.0"

    #def menuEntries(self,l):
    #    return [(2000,_("Comment"),True,self.comment,"gfx/gtk-edit.png")]


    @JPlugin.Entry.PhotosProcess( _("Comment"), order=2000, icon="gfx/gtk-edit.png" )
    def comment(self,list):
        from comment import Wincomment

        win = Wincomment(list)
        if len(list)>1:
            win.notebook1.set_current_page(self.conf["mode"] or 0)

        ret=win.loop()[0]
        if ret!=False:
            try:
                if type(ret) == type([]):
                    self.conf["mode"] = 1
                    for i in list:
                        idx = list.index(i)
                        self.showProgress( idx, len(list) , _("Commenting") )
                        i.setComment(ret[idx])
                else:
                    self.conf["mode"] = 0
                    for i in list:
                        self.showProgress( list.index(i), len(list) , _("Commenting") )
                        i.setComment(ret)
            finally:
                self.showProgress()

            return True
        else:
            return False
