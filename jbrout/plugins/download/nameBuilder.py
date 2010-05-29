# -*- coding: UTF-8 -*-
##
##    Copyright (C) 2007 Rob Wallace rob[at]wallace(dot)gen(dot)nz
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
#====
import pygtk
pygtk.require('2.0')
#====

import gtk
import gobject

import datetime
import time
import re

from libs import extListview
from libs.gladeapp import GladeApp

from jbrout.common import ed2d,caseFreeCmp

class WinNameBuilderTokens(GladeApp):
    """Class used to display a window containing a list of tokens, examples
    and their descriptions"""
    glade = os.path.join(os.path.dirname(__file__), 'nameBuilder.glade')
    window = "winDownloadTokens"

    def init(self,exSource, exExif, exDate, jobCode):
        """
        Initalises a window listing the tokens and buils examples based on the
        arguments
        
        Keyword Arguments:
        exSource - source filename to ues in building examples
        exExif   - source EXIF image info to be used in building examples
        exDate   - source image date to be used in building examples
        jobCode  - Job Code to be used in building examples
        """
        txtRdr = gtk.CellRendererText()

        (
            COL_TOKEN,
            COL_EXAMPLE,
            COL_DESCRIPTION
        ) = range(3)

        columns = (('Token',      [(txtRdr, gobject.TYPE_STRING)],
                    (COL_TOKEN,),      True),
                   ('Example',        [(txtRdr, gobject.TYPE_STRING)],
                    (COL_EXAMPLE,),        True),\
                   ('Description',   [(txtRdr, gobject.TYPE_STRING)],
                    (COL_DESCRIPTION,),        True))

        self.tokenList = extListview.ExtListView(columns,False)

        self.swTokenList.add(self.tokenList)
        self.swTokenList.show_all()

        self.nb = NameBuilder()
        self.nb.name(exSource,"","",exExif, exDate, jobCode)
        example = _(
"""Image Information
_________________""")
        self.tokenList.insertRows([['',example,'']])
        self.keys = self.nb.tokens.keys()
        self.keys.sort(caseFreeCmp)
        for key in self.keys:
            self.tokenList.insertRows([[key,
                                        self.nb.tokens[key][0](),
                                        self.nb.tokens[key][1]]])
        header = _(
"""Serial Numbering
________________""")
        description = _(
"""use only one of these. 
Add a number after the letter in the braces to pad with
zeros out to x digits""")
        self.tokenList.insertRows([['',header,description]])
        self.keys = self.nb.serialTokens.keys()
        self.keys.sort(caseFreeCmp)
        for key in self.keys:
            self.tokenList.insertRows([[key,
                                        self.nb.serialTokens[key][0],
                                        self.nb.serialTokens[key][1]]])

    def on_winDownloadTokens_delete_event(self, widget, *args):
        """Handles programatically closing the window"""
        self.quit(False)

    def on_btnClose_clicked(self, widget, *args):
        """Handles the Close button"""
        self.quit(False)

class NameBuilder():
    """Class to provide name building services based on the source file name,
    date and image exif data"""
    def __init__(self):
        """Handles Initalisation"""
        self.tokens={
            '{a}': (self.a, _("Abbreviated weekday name")),
            '{A}': (self.A, _("full weekday name")),
            '{b}': (self.b, _("Abbreviated month name")),
            '{B}': (self.B, _("Full month name")),
            '{c}': (self.c, _("Camera serial number (Canon only)")),
            '{d}': (self.d, _("Date in the form YYMMDD")),
            '{D}': (self.D, _("Day of the month (01 to 31)")),
            '{e}': (self.e, _("File extension without the '.'")),
            '{E}': (self.E, _("File type: 'JPG' or 'RAW'")),
            '{E1}': (self.E1, _("File type: empty or 'RAW'")),
            '{E2}': (self.E2, _("File type: 'JPG' or empty")),
            '{f}': (self.f, _("First 3 characters of image name")),
            '{H}': (self.H, _("Hour (00 to 23)")),
            '{i}': (self.i, _("ISO")),
            '{I}': (self.I, _("Hour (01 to 12)")),
            '{j}': (self.j, _("Day of the year (001 to 366)")),
            '{J}': (self.J, _("Job Code")),
            '{k}': (self.k, _("ISO (same as %i except 0 is returned as 'Auto')")),
            '{K1}': (self.K1, _("Focal length in mm")),
            '{K2}': (self.K2, _("Aperture")),
            '{K3}': (self.K3, _("Shutter speed e.g. 125 for 1/125 sec")),
            '{m}': (self.m, _("Month (0 to 12)")),
            '{M}': (self.M, _("Minutes (00 to 59)")),
            '{o}': (self.o, _("Origional file name")),
            '{O}': (self.O, _("Owner string (Canon only)")),
            '{p}': (self.p, _("am/pm indicator")),
            '{P}': (self.P, _("Quarter: Jan-Mar=1, Apr-Jun=2, Jul-Sep=3, Oct-Dec=4")),
            '{q}': (self.q, _("Source folder number")),
            '{Q}': (self.Q, _("Source folder number & name")),
            '{r}': (self.r, _("Image number")),
            '{r1}': (self.r1, _("Last digit of image number")),
            '{r2}': (self.r2, _("Last 2 digits of image number")),
            '{r3}': (self.r3, _("Last 3 digits of image number")),
            '{r4}': (self.r4, _("Last 4 digits of image number")),
            '{r5}': (self.r5, _("Last digit of folder number followed by last 4 digits of image number")),
            '{r6}': (self.r6, _("First digit of folder number followed by last 4 digits of image number")),
            '{r7}': (self.r7, _("First digit of folder number - 1, followed by last 4 digits of image number")),
            '{s}': (self.s, _("Subsecond timing (Nikon DSLR's only")),
            '{S}': (self.S, _("Seconds (00 to 59)")),
            '{t}': (self.t, _("Time in the form HHMMSS")),
            '{T}': (self.T, _("Camera model name starting from the first word containing digits")),
            '{T1}': (self.T1, _("Same as %T except '-' are treated as spaces")),
            '{T2}': (self.T2, _("Full camera model name")),
            '{T3}': (self.T3, _("First word of camera model name containing digits")),
            '{T4}': (self.T4, _("Same as %T3 except '-' are treated as spaces")),
            '{T5}': (self.T5, _("Last word of camera model name containing digits")),
            '{T6}': (self.T6, _("Same as %T5 except '-' are treated as spaces")),
            '{T8}': (self.T8, _("Value defined in camera mapping (sas %T1 if undefined")),
            '{T9}': (self.T9, _("Value defined in camera mapping (sas %T1 if undefined")),
            '{v}': (self.v, _("Same as %T (Compatability)")),
            '{V}': (self.V, _("Same as %T2 (Compatability)")),
            '{W}': (self.W, _("Week Number (00 to 53)")),
            '{x}': (self.x, _("Date representation for locale")),
            '{X}': (self.X, _("Time representation for locale")),
            '{y}': (self.y, _("Year without century")),
            '{Y}': (self.Y, _("Year with century")),
            '{z}': (self.z, _("Time zone name")),
            '{Z}': (self.Z, _("Time zone offset wrt UTC")),
            '{dtl}': (self.dtl, _("Long Date & Time")),
            '{dl}': (self.dl, _("Long Date")),
            '{1}': (self.no1, _("Year 'now' with century i.e. the download date")),
            '{2}': (self.no2, _("Month 'now' i.e. the download date")),
            '{3}': (self.no3, _("Day 'now' i.e. the download date")),
            '{4}': (self.no4, _("Year 'now' without century i.e. the download date")),
            '{5}': (self.no5, _("Year without century less 3 hours")),
            '{6}': (self.no6, _("Month less 3 hours")),
            '{7}': (self.no7, _("Day less 3 hours"))}

        self.serialTokens={
            '{l}': ('2', _("'Uniqueness' number or empty if filename is unique")),
            '{L}': ('1', _("'Uniqueness' number evaluates to 1 or higher")),
            '{n}': ('1', _("Download sequence number with no leading zeros")),
            '{N}': ('1', _("Date based download sequence number"))}

    def name(self, sourceName, destFolder, pattern, exif, date, jobCode=''):
        """
        Builds a destination file name based on a pattern and image information
        
        Keyword Arguments:
        sourceName - Name of the source image
        destFolder - Destination folder
        pattern    - Pattern for building the destination file name
        exif       - Source image exif information
        date       - Source image date/time
        jobCode    - Jobe code '' if none supplied
        """
        self.sourceName = sourceName
        self.exif = exif
        self.date = date
        self.jobCode = jobCode
        destName = pattern
        patTokens = re.findall("\{\w\}",pattern)
        for token in patTokens:
            if token in self.tokens:
                destName = destName.replace(token,self.tokens[token][0]())
        destName = destName + os.path.splitext(self.sourceName)[1].lower()
        return(os.path.join(destFolder, destName))
    
    def seralize(self,data,srcCol,dateCol,destCol,start=1):
        """
        Serialises a table of destination image names in place by replacing
        tokens in the existing destination names and returns the table sorted
        by source name
        Returns True on sucess, False if more than one seralisation token 

        Keyword Arguments:
        data    - table containing the 
        srcCol  - index of the column containing the source image name
        dateCol - index of the column containing the date/time of the image
        destCol - index of the column containing the destination image name
        start   - sequence start number for {Nx} (1 if undefrined)
        """
        if len(data) == 0:
            # no rows = no need to do anything
            return True
        serTokens = re.findall("\{[lLnN]\d*\}",data[0][destCol])
        if len(serTokens) == 0:
            # No need to seralise - no tokens
            return True
        if len(serTokens) !=1:
            return False
        token = serTokens[0]
        # determine amount of zero padding required
        numRef = re.search("\d+",token)
        if numRef == None:
            padTo = 0
        else:
            padTo = int(numRef.group())
        format = "%%0%dd" % padTo
        date = False
        continuous = False
        notOnUnique = False
        if token[1] == 'l':
            start = 0
            notOnUnique = True
        elif token[1] == 'L':
            start = 1
        elif token[1] == 'n':
            continuous = True
        elif token[1] == 'N':
            start = 1
            date = True
        count = start
        # do the first line
        if date:
            data.sort(lambda x,y:cmp(x[dateCol],y[dateCol]))
        elif not continuous:
            data.sort(lambda x,y:cmp(x[destCol],y[destCol]))
        if len(data) > 1 and notOnUnique:
            if data[0][destCol] == data[1][destCol]:
                count += 1
        if count == 0:
            replacement = ''
        else:
            replacement = format % count
        previous = data[0][destCol]
        data[0][destCol] = data[0][destCol].replace(token, replacement)
        if len(data) == 1:
            return True
        for idx in range(1,len(data)):
            if continuous:
                count += 1
            elif date:
                if data[idx][dateCol].year == data[idx-1][dateCol].year\
                and data[idx][dateCol].month == data[idx-1][dateCol].month\
                and data[idx][dateCol].day == data[idx-1][dateCol].day:
                    count += 1
                else:
                    count = start
            elif data[idx][destCol] == previous:
                count += 1
            elif notOnUnique and idx+1 < len(data):
                if data[idx][destCol] == data[idx+1][destCol]:
                    count = start +1
                else:
                    count = start
            else:
                count = start
            previous = data[idx][destCol]
            if count == 0:
                replacement = ''
            else:
                replacement = format % count
            data[idx][destCol] = data[idx][destCol].replace(token, replacement)
        # Return data to correct order
        if not continuous:
            data.sort(lambda x,y:cmp(x[srcCol],y[srcCol]))
        return True

    def singleSeralize(self,pattern,start=1):
        """
        Wrapper around seralize to enable seralizing of a single file name,
        returns seralized file name

        Keyword Arguments:
        pattern - file name to seralize
        start - sequence start number for {Nx} (1 if undefrined)
        """
        toSeralize = [['','',pattern]]
        if not self.seralize(toSeralize,0,1,2,start):
            MessageBox(self.main_widget,
            _("More than one serialisation tag used please remove extras from File Naming > Pattern "))
        return toSeralize[0][2]

    # Tag string functions for details of their function see the dictionary
    # above
    def a(self):
        return self.date.strftime("%a")

    def A(self):
        return self.date.strftime("%A")

    def b(self):
        return self.date.strftime("%b")

    def B(self):
        return self.date.strftime("%B")

    def c(self):
        return self.getExifTag('Exif.Canon.SerialNumber')

    def d (self):
        return self.date.strftime("%y%m%d")

    def D(self):
        return self.date.strftime("%d")

    def e(self):
        return os.path.splitext(self.sourceName)[1][1:]

    def E(self):
        if self.e().upper() == 'JPG': return 'JPG'
        else: return 'RAW'

    def E1(self):
        if self.e().upper() == 'JPG': return ''
        else: return 'RAW'

    def E2(self):
        if self.e().upper() == 'JPG': return 'JPG'
        else: return ''

    def f(self):
        return os.path.basename(self.sourceName)[:3]

    def H(self):
        return self.date.strftime("%H")

    def i(self):
        return self.getExifTag('Exif.Photo.ISOSpeedRatings')

    def I(self):
        return self.date.strftime("%I")

    def j(self):
        return self.date.strftime("%j")

    def J(self):
        return self.jobCode

    def k(self):
        if self.i() == "0":
            return "Auto"
        else:
            return self.i()

    def K1(self):
        return self.getExifTag('Exif.Photo.FocalLength')

    def K2(self):
        return self.getExifTag('Exif.Photo.ApertureValue')

    def K3(self):
        return self.getExifTag('Exif.Photo.ExposureTime')

    def m(self):
        return self.date.strftime("%m")

    def M(self):
        return self.date.strftime("%M")

    def o(self):
        return os.path.basename(os.path.splitext(self.sourceName)[0])

    def O(self):
        return self.getExifTag('Exif.Canon.OwnerName')

    def p(self):
        return self.date.strftime("%p")

    def P(self):
        month = self.date.strftime("%m")
        if month in ['01', '02', '03']:
            return '1'
        elif month in ['04', '05', '06']:
            return '2'
        elif month in ['07', '08', '09']:
            return '3'
        else:
            return '4'
        return "4"

    def q(self):
        try:
            return re.search('\d+',self.Q()).group()
        except:
            return ""

    def Q(self):
        return os.path.basename(os.path.dirname(self.sourceName))

    def r(self):
        try:
            return re.search("\d+", os.path.basename(self.sourceName)).group()
        except:
            return ""

    def r1(self):
        return self.r()[-1:]

    def r2(self):
        return self.r()[-2:]

    def r3(self):
        return self.r()[-3:]

    def r4(self):
        return self.r()[-4:]

    def r5(self):
        return self.q()[-1:] + self.r()[-4:]

    def r6(self):
        return self.q()[:1] + self.r()[-4:]

    def r7(self):
        tmp = self.q()[:1]
        if tmp.isdigit():
            if int(tmp) > 0:
                return "%s%s" % (int(tmp)-1,self.r()[-4:])
            else:
                return '0' + self.r()[-4:]
        else:
            return '0' + self.r()[-4:]

    def s(self):
        return self.getExifTag('Exif.Photo.SubSecTime')

    def S(self):
        return self.date.strftime("%S")

    def t(self):
        return self.date.strftime("%H%M%S")

    def T(self):
        try:
            return re.search('[a-z,A-Z]*\d+.*',self.T2()).group()
        except:
            return ""

    def T1(self):
        try:
            return re.search('[a-z,A-Z]*\d+.*',re.sub('-',' ',self.T2())).group()
        except:
            return ""

    def T2(self):
        return self.getExifTag('Exif.Image.Model')

    def T3(self):
        try:
            return re.search('[a-z,A-Z]*\d+[a-z,A-Z]*',self.T2()).group()
        except:
            return ""

    def T4(self):
        try:
            return re.search('[a-z,A-Z]*\d+[a-z,A-Z]*',re.sub('-',' ',self.T2())).group()
        except:
            return ""

    def T5(self):
        try:
            return re.search('[a-z,A-Z]*\d+[a-z,A-Z]*(?!.*\d+)',self.T2()).group()
        except:
            return ""

    def T6(self):
        try:
            return re.search('[a-z,A-Z]*\d+[a-z,A-Z]*(?!.*\d+)',re.sub('-',' ',self.T2())).group()

        except:
            return ""

    def T8(self):
        return self.T1() # TODO: replace with camera mapping

    def T9(self):
        return self.T1() # TODO: replace with camera mapping

    def v(self):
        return self.T()

    def V(self):
        return self.T2()

    def W(self):
        return self.date.strftime("%W")

    def x(self):
        return self.date.strftime("%x")

    def X(self):
        return self.date.strftime("%X")

    def y(self):
        return self.date.strftime("%y")

    def Y(self):
        return self.date.strftime("%Y")

    def z(self):
        return time.tzname[time.daylight]

    def Z(self):
        if time.daylight:
            to = -time.altzone
        else:
            to = -time.timezone
        if to >= 0:
            return "+%i:%02i" % (abs(to)/3600,(abs(to)%3600)/60)
        else:
            return "-%i:%02i" % (abs(to)/3600,(abs(to)%3600)/60)

    def dtl(self):
        return self.date.strftime("%A, %d %B %Y %I:%M:%S%p")

    def dl(self):
        return self.date.strftime("%A, %d %B %Y")

    def no1(self):
        return self.getDateTimeNow().strftime("%Y")

    def no2(self):
        return self.getDateTimeNow().strftime("%m")

    def no3(self):
        return self.getDateTimeNow().strftime("%d")

    def no4(self):
        return self.getDateTimeNow().strftime("%y")

    def no5(self):
        return self.getDateTimeOld().strftime("%y")

    def no6(self):
        return self.getDateTimeOld().strftime("%m")

    def no7(self):
        return self.getDateTimeOld().strftime("%d")

    def getDateTimeNow(self):
        """Returns the current time"""
        return datetime.datetime.now()

    def getDateTimeOld(self):
        """Returns the current time less Three hours"""
        return datetime.datetime.now() + datetime.timedelta(hours=-3)

    def getExifTag(self, tag):
        """Returns a given EXIF tag if it exists in the images EXIF info"""
        try:
            return "%s" % self.exif.interpretedExifValue(tag)
        except:
            return ""