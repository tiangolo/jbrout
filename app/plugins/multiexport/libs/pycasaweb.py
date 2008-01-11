# -*- coding: utf-8 -*-

##    PycasaWeb V0.4 (inspiration from "google-sharp")
##
##    Copyright (C) 2006 manatlan manatlan[at]gmail(dot)com
##
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
"""
Changelog

  V0.4.2 (07-04-17):
        - getAlbums() : change the get by NS to nodename (photo:id) (thankx to fabien)

  V0.4.1 (07-02-11):
        - change in connection (the "=" stuff) in "location"

  V0.4 (06-08-26):
        - connection works for recent google account now !
        - some possible errors are intercepted
"""
import sys,os
import urllib,urllib2,urlparse,cookielib,mimetypes,mimetools
from datetime import datetime
from xml.dom.minidom import parseString

# init ...
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)


#===============================================================================
# functions helpers ...
#===============================================================================
def getText(x):
    """ get textual content of the node 'x' """
    r=""
    for i in x.childNodes:
        if i.nodeType == x.TEXT_NODE:
            r+=i.nodeValue
    return r




def getResultFromXml(xml):
    """ Test node result of the xml returned by google api
        return content "ID node" if present, or True
        or raise PycasaWebException if failure !
    """
    try:
        root=parseString(xml).documentElement
        result=getText(root.getElementsByTagName("result")[0])
    except Exception,m:
        raise PycasaWebException( "xml resulted is bad :"+m )
    if result=="success":
        l=root.getElementsByTagName("id")
        if len(l)>0:
            return getText(l[0])
        else:
            return True
    else:
        reason=getText(root.getElementsByTagName("reason")[0])
        raise PycasaWebException( utf8(reason) )



def utf8(v):
    """ ensure to get 'v' in an UTF8 encoding (respect None) """
    if v!=None:
        if type(v)!=unicode:
            v=unicode(v,"utf_8","replace")
        v=v.encode("utf_8")
    return v



def getUrlScheme(u):
    """  explode url in (scheme,host,path)"""
    scheme,host,path,nop,params,nop= urlparse.urlparse(u)
    if params:
        return scheme,host,path+"?"+params
    else:
        return scheme,host,path


def mkRequest(url,data=None,headers={}):
    """ create a urlib2.Request """
    if data:
        data = urllib.urlencode(data)
    return urllib2.Request(url,data,headers)


#-------------------------------------------------------------------------------
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/146306
#-------------------------------------------------------------------------------

def post_multipart(host, selector, fields, files):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    headers = {'Content-Type': content_type,
               'Content-Length': str(len(body))}
    r = urllib2.Request("http://%s%s" % (host, selector), body, headers)
    return urllib2.urlopen(r).read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    mimetools._prefix = "some-random-string-you-like"    # vincent patch : http://mail.python.org/pipermail/python-list/2006-December/420360.html
    BOUNDARY = mimetools.choose_boundary()
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
#-------------------------------------------------------------------------------




#===============================================================================
# classes
#===============================================================================
class PycasaWebException(Exception):
    pass

###############################################################################
class GoogleConnection(object):
###############################################################################
    __URLAUTHENT = "https://www.google.com/accounts/ServiceLoginAuth?service=lh2&passive=true&continue=http%3A%2F%2Fpicasaweb.google.com%2F"
    __URLLIST = "http://picasaweb.google.com/api/urls?version=1"

    __user=None
    user=property(lambda s: s.__user)

    __urlGallery=None
    __urlPost=None
    urlGallery=property(lambda s: s.__urlGallery)
    urlPost=property(lambda s: s.__urlPost)

    def __init__(self,u,p):
        u=utf8(u)
        p=utf8(p)
        self.__user = u

        headers = {"Content-type": "application/x-www-form-urlencoded",}
        data =    { "null":"Sign in",
                     "Email":u,
                     "Passwd":p,
                     "service":"lh2",
                     "passive":"true",
                     "continue":"http://picasaweb.google.com/",
        }

        request = mkRequest(GoogleConnection.__URLAUTHENT,data,headers)   # POST
        response = opener.open(request)
        buf=response.read()

        try:
            p1=buf.index('.replace("')+10
            p2=buf.index('")',p1)
            location=buf[p1:p2]
        except:
            raise PycasaWebException("unable to connect (bad account ?)")

        if "SetSID?" in location:   # it's a recent account
            location= location.replace("\u003d","=")
        elif "invitationRequired" in location:
            raise PycasaWebException("Your picasaweb account is not open, you must log in on picasaweb")

        # 11/02/2007 : add this line to make good "=" always
        location = location.replace("\u003d","=")

        #~ # Process the redirect to Valid authent
        request = mkRequest(location)
        response = opener.open(request)
        buf=response.read() # garbage

        # Get XML/RSS of "picasa urls"
        try:
            request = mkRequest(GoogleConnection.__URLLIST)
            response = opener.open(request)
            xml=response.read()
        except urllib2.HTTPError:
            raise PycasaWebException("Picasaweb is not activated, you must sign in on the web")



        # Parse XML of "picasa urls" and store the needed ones
        root=parseString(xml).documentElement
        for i in (root.getElementsByTagName("channel")[0]).getElementsByTagName("item"):
            title = getText( i.getElementsByTagName("title")[0] )
            link = getText( i.getElementsByTagName("link")[0] )
            if title == "gallery":
                self.__urlGallery = link
            if title == "post":     # can be obtained only if authentified !
                self.__urlPost = link
            #~ print title,"=",link

        assert self.__urlPost!=None, "can't get POST url"




###############################################################################
class PycasaWeb:
###############################################################################
    def __init__(self, user,password):
        """ Create a PycasaWeb instance for the account user/password """
        #~ try:
            #~ self.__gc=GoogleConnection(user,password)
        #~ except Exception,m:
            #~ raise PycasaWebException(m)
        self.__gc=GoogleConnection(user,password)

    def getAlbums(self):
        """ Get a list of PicasaAlbum available on this account """
        l=[]

        request = mkRequest(self.__gc.urlGallery)
        response = opener.open(request)
        xml=response.read()

        root=parseString(xml).documentElement
        GPHOTO = "http://picasaweb.google.com/lh/picasaweb"
        for i in root.getElementsByTagName("item"):
            name = getText(i.getElementsByTagName("title")[0]) # title
            id = getText(i.getElementsByTagName("gphoto:id")[0])  # gphoto:id
            l.append( PicasaAlbum(self.__gc,id,name) )

        return l

    def createAlbum(self,name,description="",date=None, public=True):
        """ Create an Album on picasaweb, return the PicasaAlbum instance """
        name=utf8(name)
        description=utf8(description)

        if date==None:
            date = datetime.now()

        dat = date.strftime("%d MONTH %Y %H:%M:%S GMT")  # TODO : GMT timezone
        # replace MONTH by a english month (because in french : it makes an error)
        dat=dat.replace("MONTH","jan,feb,mar,apr,may,jun,jui,aug,sep,oct,nov,dec".split(",")[date.month-1])

        xml="""<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:gphoto="http://www.temp.com/">
 <channel>
  <title>%s</title>
  <description>%s</description>
  <pubDate>%s</pubDate>
  <gphoto:access>%s</gphoto:access>
  <gphoto:user>%s</gphoto:user>
  <gphoto:location/>
  <gphoto:op>createAlbum</gphoto:op>
 </channel>
</rss>""" % (
                name,
                description,
                dat,
                public and "Public" or "Private",
                self.__gc.user
            )

        content_type, body = encode_multipart_formdata([("xml",xml)], [])

        headers = {'Content-Type': content_type,
               'Content-Length': str(len(body)),
                   }

        request = urllib2.Request(self.__gc.urlPost, body, headers)
        response = opener.open(request)
        xml=response.read()

        id = getResultFromXml(xml)  # obtain ID
        return PicasaAlbum(self.__gc,id,name)





###############################################################################
class PicasaAlbum(object):
###############################################################################
    __name=None
    name=property(lambda s: s.__name)

    __id=None
    __gc=None

    def __init__(self,gc,id,name):
        """ should be only called by PycasaWeb """
        self.__gc = gc
        self.__name = name
        self.__id = utf8(id)

    def uploadPhoto(self,filename,description=""):
        """ Upload a picture on this album, return the ID of the new picture """
        filename=utf8(filename)
        description=utf8(description)

        if os.path.isfile(filename):
            uid=abs(id(filename))
            name = os.path.basename(filename)

            xml="""<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:gphoto="http://www.temp.com/">
 <channel>
  <gphoto:user>%s</gphoto:user>
  <gphoto:id>%s</gphoto:id>
  <gphoto:op>createAndAppendPhotoToAlbum</gphoto:op>
  <item>
   <title>%s</title>
   <description>%s</description>
   <gphoto:multipart>%d</gphoto:multipart>
   <gphoto:layout>0.000000</gphoto:layout>
   <gphoto:client>pycasaweb</gphoto:client>
  </item>
 </channel>
</rss>""" % (self.__gc.user,self.__id,name,description,uid )


            content_type, body = encode_multipart_formdata([("xml",xml)], [(uid,filename,open(filename,"rb").read() )])

            headers = {'Content-Type': content_type,
                   'Content-Length': str(len(body)),
                       }

            request = urllib2.Request(self.__gc.urlPost, body, headers)
            response = opener.open(request)
            xml=response.read()

            return getResultFromXml(xml)    # obtain ID
        else:
            raise PycasaWebException("File doesn't exists")


    def deleteAlbum(self):

        xml="""<?xml version="1.0" encoding="utf-8" ?>
<rss version="2.0" xmlns:gphoto="http://www.temp.com/">
 <channel>
  <gphoto:user>%s</gphoto:user>
  <gphoto:id>%s</gphoto:id>
  <gphoto:op>deleteAlbum</gphoto:op>
 </channel>
</rss>""" % (self.__gc.user,self.__id )

        content_type, body = encode_multipart_formdata([("xml",xml)], [])

        headers = {'Content-Type': content_type,
               'Content-Length': str(len(body)),
                   }

        request = urllib2.Request(self.__gc.urlPost, body, headers)
        response = opener.open(request)
        xml=response.read()

        return getResultFromXml(xml)    # obtain true


    def __repr__(self):
        return "<album %s : %s>" % (self.__id,self.__name)



if __name__=="__main__":
    picasa = PycasaWeb("manatlan@gmail.com","xxxxx")
    p="/home/manatlan/Desktop/fotaux/p20060401_090621.jpg"

    album=picasa.createAlbum("TEST")
    album.uploadPhoto(p)

    for a in picasa.getAlbums():
        if a.name == "TEST":
            a.uploadPhoto(p)
            break

    a.deleteAlbum()

    print picasa.getAlbums()
