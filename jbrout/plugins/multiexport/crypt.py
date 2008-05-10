# -*- coding: UTF-8 -*-
##
##    Copyright (C) 2008 manatlan manatlan[at]gmail(dot)com
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
import base64
u64enc = base64.urlsafe_b64encode
u64dec = base64.urlsafe_b64decode

def mix(s):
    if len(s)%2!=0: s+=" "
    return "".join([a+b for a,b in zip(s[:len(s)/2],s[len(s)/2:])])

def unmix(s):
    l=list(s)
    return ("".join(l[::2]+l[1::2])).strip()

def crypt(s):
    " simple crypt method "
    if s!=None and s:
        if type(s)==unicode:
            s=s.encode("utf_8")
        chk = sum([ord(i) for i in s])+51
        s=mix(str(chk)+"¡"+s)
        return mix(u64enc(s))
    else:
        return u""

def uncrypt(eobj):
    " simple uncrypt method, work with crypt() below "
    if eobj!=None and eobj!="":
        if type(eobj)==unicode:
            eobj = eobj.encode("utf_8")
        try:
            t= u64dec(unmix(eobj))
            chk,chaine = unmix(t).split("¡")
            if int(chk) == sum([ord(i) for i in chaine])+51:
                return chaine.decode("utf_8")
        except:
            return u""
    else:
        return u""

if __name__=="__main__":
    assert crypt(None) == ""
    assert crypt("") == ""
    assert crypt(u"") == ""
    
    assert uncrypt(None) == ""
    assert uncrypt("") == ""
    assert uncrypt("something_not_encrypted") == ""

    assert "marco" == uncrypt(crypt("marco"))
    assert u"marcô" == uncrypt(crypt("marcô"))
    assert u"marcô" == uncrypt(crypt(u"marcô"))
    assert "" == uncrypt(crypt(""))
    assert "" == uncrypt(crypt(None))
    
