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

import os
import gtk
from datetime import datetime,timedelta

from libs.gladeapp import GladeApp

class Winredate(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'redate.glade')


    def init(self):
        self.main_widget.set_modal(True)
        self.main_widget.set_position(gtk.WIN_POS_CENTER)

        try:
            self.d = Winredate.defaultDate
        except:
            self.d = datetime.now() # just for self run
        self.recalc()
        self.hour.set_value(self.d.hour)
        self.minute.set_value(self.d.minute)
        self.second.set_value(self.d.second)
        self.date.select_month(self.d.month-1, self.d.year)
        self.date.select_day(self.d.day)
        print self.d


    def recalc(self):
        vw= self.weeks.get_value()
        vd= self.days.get_value()
        vh= self.hours.get_value()
        vi= self.minutes.get_value()
        vs= self.seconds.get_value()

        f = lambda x: x.strftime( unicode(_("%m/%d/%Y %H:%M:%S")).encode("utf_8") )

        dn=self.d
        dn+=timedelta(weeks=vw, days=vd,hours=vh,minutes=vi,seconds=vs)

        msg = _("Example date : %s \n\n\n") % f(self.d)
        if vw == vd == vh == vi == vs == 0:
            self.vals = None
            msg += _("No change")
        else:
            self.vals = (vw,vd,vh,vi,vs)
            msg += _("Change to %s :\n\n") % f(dn)
        self.msg.set_text(msg)


    def on_WinRedate_delete_event(self, widget, *args):
        self.quit(False)

    def on_weeks_value_changed(self, widget, *args):
        self.recalc()

    def on_days_value_changed(self, widget, *args):
        self.recalc()

    def on_hours_value_changed(self, widget, *args):
        self.recalc()

    def on_minutes_value_changed(self, widget, *args):
        self.recalc()

    def on_seconds_value_changed(self, widget, *args):
        self.recalc()

    def on_btn_annuler_clicked(self, widget, *args):
        self.quit(False)

    def on_btn_appliquer_clicked(self, widget, *args):
        if self.notebook.get_current_page() == 0:
            if self.vals == None:
                rep = None
            else:
                rep=('relative',self.vals)
        else:
            [ny,nm,nd]=self.date.get_date()
            ndt=datetime(ny,nm+1,nd,int(self.hour.get_value()),
                         int(self.minute.get_value()),
                         int(self.second.get_value()))
            rep=('absolute',ndt)
        self.quit(rep)


def main():
    win_redate = Winredate()

    win_redate.loop()

if __name__ == "__main__":
    main()


