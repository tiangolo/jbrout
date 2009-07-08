# -*- coding: UTF-8 -*-
##
##    Copyright (C) 2009 Rob Wallace rob[at]wallace(dot)gen(dot)nz
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
    """Plugin to perform mass tagging changes"""

    __author__ = "Rob Wallace"
    __version__ = "0.1"

    def menuEntries(self,l):
        return [(8000,_("Unify Tags"),True,self.unifyTags,None)]


    def unifyTags(self,list):
        """Unifys tags between the selected list of photos (makes the Tags all the same)"""
        tags=[]
        for i in list:
            self.showProgress(list.index(i), len(list), _("Reading Tags"))
            for tag in i.tags:
                if tag not in tags:
                    tags.append(tag)
        self.showProgress()
        if len(tags) != 0:
            msg = u""
            for tag in tags:
                msg = msg + ', ' + tag
            msg = _("Are you sure you whish to add the following tags to the selected images:\n") + msg[2:]
            if self.InputQuestion(msg,title=_("Unify Tags")):
                for i in list:
                    self.showProgress(list.index(i), len(list), _("Tagging"))
                    i.addTags(tags)
                ret = True
            else:
                ret = False
        else:
            ret = False
        self.showProgress()
        return ret

