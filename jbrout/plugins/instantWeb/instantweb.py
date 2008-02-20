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

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socket
import datetime
import cgi,urllib
from cStringIO import StringIO
import thread,gobject,time,math
import select

from jbrout.common import cd2rd

try:
    import Image
except:
    raise "you should install PIL module (http://www.pythonware.com/products/pil/)"


# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
import random

class fn(object):
    """ fake FolderNode """
    def __init__(self):
        self.name = "marco"+str(int(random.random()*10))

    def __repr__(self):
        return "<fn:%s>" % self.name

class pn(object):
    """ fake PhotoNode """
    cpt=0
    def __init__(self):
        pn.cpt+=1
        self.name= "nom"+str(pn.cpt)
        self.date = "28/05/2005 13:38:34"
    def getParent(self):
        return fn()
    def __repr__(self):
        return "<pn:%s>" % self.name
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

# ==============================================================================
class MyHandler(BaseHTTPRequestHandler):
# ==============================================================================
    __continueToServe=True
    """
    win : windows to log
    root : site object (cp2)
    """

    def do_GET(self):
        # /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
        #~ print self.path
        if self.path.find('?')>=0:
            page = self.path[1:self.path.index("?")]
            args=self.query(cgi.parse_qs(self.path[self.path.find('?')+1:]))
        else:
            page = self.path[1:]
            args=[]

        MyHandler.__ip=self.client_address[0]

        if not page: page="index"

        if hasattr(MyHandler.root,page):
            obj = getattr(MyHandler.root,page)

            try:
                if hasattr(obj,"content_type"):
                    # the page/method has a different content-type, use it
                    content_type=getattr(obj,"content_type")
                else:
                    # default ct
                    content_type="text/html"

                self.send_response(200, 'OK')
                self.send_header('Content-type', content_type)
                self.end_headers()

                if args:
                    # if there are args, call with args
                    b=obj(*(),**(args))  # generator de Site."page"()
                else:
                    # if there aren't args, call with no args
                    b=obj()  # generator de Site."page"()

                if hasattr(b,"next"):
                    # it's a generator()
                    while True:
                        # fetch its yield statement
                        try:
                            self.wfile.write( b.next() )
                        except StopIteration:
                            break
                else:
                    self.wfile.write( str(b) )

            except TypeError,detail:
                b="Type Error : " + str(detail)
                self.wfile.write( b )
            except Exception,detail:
                b="Error : " + str(detail)
                self.wfile.write( b )

        else:
            self.send_response(404, 'OK')
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("404 , page '%s' not found !"%page)
            self.wfile.write("<hr>Jbrout http server")



    def query(self,parsedQuery):
        """Returns the QUERY dictionary, similar to the result of cgi.parse_qs
        except that :
        - if the key ends with [], returns the value (a Python list)
        - if not, returns a string, empty if the list is empty, or with the
        first value in the list"""
        res={}
        for item in parsedQuery.keys():
            value=parsedQuery[item] # a Python list
            if item.endswith("[]"):
                res[item[:-2]]=value
            else:
                if len(value)==0:
                    res[item]=''
                else:
                    res[item]=value[0]
        return res

    @staticmethod
    def handleRequest(s):
        gtk.threads_enter()
        try:
            rd, wr, ex = select.select([s.socket.fileno()], [], [], 1)
        except:
            rd=None
        if rd: s.handle_request()
        gtk.threads_leave()
        return MyHandler.__continueToServe

    @staticmethod
    def stopHandler():
        MyHandler.__continueToServe=False

    @staticmethod
    def startHandler():
        MyHandler.__continueToServe=True

    @staticmethod
    def log(m):
        MyHandler.win.log("%s: %s" % (MyHandler.__ip,m))

class Img:
    """
    class to convert a pixbuf to a Img (pil/Image based)
    provide operations :
        - to get a stream of jpeg
        - resize
    """
    def __init__(self,pb=None,im=None):
        # create a Img (pil/Image based) from a pixbuf
        if pb:
            #~ width,height = pb.get_width(),pb.get_height()
            #~ self.__im = Image.fromstring("RGB",(width,height),pb.get_pixels() )
            dimensions = pb.get_width(), pb.get_height()
            stride = pb.get_rowstride()
            pixels = pb.get_pixels()
            mode = pb.get_has_alpha() and "RGBA" or "RGB"
            self.__im=Image.frombuffer(mode, dimensions, pixels,
                            "raw", mode, stride, 1)

        elif im:
            self.__im = im
        else:
            raise "bad call of Img()"

    def getStreamJpeg(self,q=70):
        f = StringIO()
        self.__im.save(f, "JPEG",quality=q)
        f.seek(0)
        return f

    def resize(self,size):  # proportionnal in a box
        (wx,wy) = self.__im.size
        rx=1.0*wx/size
        ry=1.0*wy/size
        if rx>ry:
            rr=rx
        else:
            rr=ry
        return Img( im=self.__im.resize((int(wx/rr),int(wy/rr))) )


class Mix:
    """ class to manipulate the list of nodes like a list of nodes ;-)
    or albums (dict of list)
    """
    def __init__(self,ln):
        self.list=ln

        a={}
        for i in ln:
            n=i.getParent().name
            if n not in a:
                a[n]=[]
            a[n].append(i)
        self.album=a

        albums = a.keys()
        albums.sort()
        self.albums = albums

    def getAlbum(self,n=None):
        if n==None:
            return self.list
        else:
            if type(n)==int:
                nom = self.albums[n]
            else:
                nom = n
            return self.album[nom]


#~ def do_idle_operation(function, *args, **kw):
    #~ def idle_func():
        #~ gtk.threads_enter()
        #~ try:
            #~ function(*args, **kw)
            #~ return False
        #~ finally:
            #~ gtk.threads_leave()
            #~ pass
    #~ gobject.idle_add(idle_func)

# *********************************************************************************
# *********************************************************************************
# *********************************************************************************
class Site:
    """ a site object (a cherrypy2 like) """

    CSS="""
* {
    font-family: helvetica,arial,sans-serif;
    color: #fff;
    font-size:9pt;
}

h1,h2,h3 {font-size:12pt;}

body {
    background-color: #600;
    margin: 0px;
}
a {
    text-decoration: none;
    color:yellow;
}

a.sel{border:4px solid black}

input{color:black;padding:0px}

/* liste de repertoires */
div#menu {margin-top:40px;float:left}
div#menu a, div#dirs span {display:block;
-moz-border-radius:4px;
text-decoration: none;
margin-bottom:1px;
padding:1px;
color:black;
}

div#menu a{
      background:#EEE;
      width:190px;
    }

/* liste de photos*/
div#photos {}
div#photos div {float:left;width:160;height:160;margin:10px;text-align:center;}
div#photos img {border:4px solid white}

/* liens de navig */
div#pages {text-align:left;}
div#pages a, div#pages span {display:inline}
div#pages a {color:black;text-decoration:none;-moz-border-radius:10px;background:#EEE;padding:4px;}
div#pages span {font-size:20px;}


a:hover {
    color:#F0F;
    background:yellow !important;
}

"""
    def __page(self,titre,hm,hp,ho):
        return """
            <html>
            <head>
                <title>%s</title>
                <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
                <style>%s</style>
            <head>
            <body>
        <div id='menu'>%s</div>
        <div id='pages'>%s</div>
        <div id='photos'>%s</div>
        </body>
        </html>
        """ % (titre,Site.CSS,hm,hp,ho)

    def index(self,a="0",p="0"):
        #~ # presente en classe
        data = MyHandler.win.mix

        p =int(p)
        a=int(a)
        NB=10

        if MyHandler.win.cb_albums.get_active():
            nom = data.albums[a]
            ll = data.getAlbum(a)
            hmenu="".join(["<a class='%s' href='index?a=%d&p=0'>%s</a>" % (a==data.albums.index(i) and "sel" or "",data.albums.index(i),i) for i in data.albums])
        else:
            nom = "Selection"
            ll = data.getAlbum()
            hmenu=""

        nbp = math.ceil(float(len(ll))/NB)

        self.__log("album:[%s] page:%d/%d" % (nom,p+1,nbp))

        all = data.getAlbum()
        if len(ll)>NB:
            hpages="Pages: "+"".join(["<a class='%s' href='index?a=%d&p=%d'>%d</a>" % (p==i and "sel" or "",a,i,i+1) for i in range(nbp)])
        else:
            hpages=""
        hphotos="".join(["<div><a href='view?n=%d'><img src='thumb?n=%d'></a>%s</div>" % (all.index(n),all.index(n),cd2rd(n.date)) for n in ll[p*NB:(p+1)*NB]] )

        titre = "%s (%d)" % (nom,len(ll))

        return self.__page(titre,hmenu,hpages,hphotos)

    def thumb(self,n):
        n=int(n)
        data = MyHandler.win.mix
        all = data.getAlbum()
        node = all[n]
        i = Img( node.getThumb() )
        return i.getStreamJpeg(60)


    thumb.content_type="image/jpeg"

    def view(self,n):
        n=int(n)
        data = MyHandler.win.mix
        all = data.getAlbum()
        node = all[n]

        self.__log("view:[%s] album:[%s]" % (node.name,node.getParent().name))
        i = Img( node.getImage() )
        if MyHandler.win.cb_originals.get_active():
            return i.getStreamJpeg(80)
        else:
            i = i.resize(800)
            return i.getStreamJpeg(60)
    view.content_type="image/jpeg"

    def __log(self,m):
        MyHandler.log(m)

# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
# ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
#~ import sys
#~ sys.path.append("../../libs")
#~ from gladeapp import GladeApp

from libs.gladeapp import GladeApp

class Winweb(GladeApp):
    glade=os.path.join(os.path.dirname(__file__), 'instantweb.glade')

    def init(self):
        self.main_widget.set_modal(True)
        self.main_widget.set_position(gtk.WIN_POS_CENTER)

        ip=socket.gethostbyname( socket.gethostname() )
        if ip=="127.0.0.1":
            f = urllib.urlopen("http://ipid.shat.net/iponly/")
            data = f.readlines()
            f.close()
            ip=data[2].strip()
            ip=ip[:ip.index("<")]


        port=8080
        self.label.set_text("http://%s:%d"%(ip,port))

        #~ webStart("",8080)

        MyHandler.root = Site()
        MyHandler.win = self
        MyHandler.startHandler()

        self.server = HTTPServer(('', 8080), MyHandler)
        #~ thread.start_new_thread(jo, (server,) )
        #~ gobject.timeout_add(500, jo,server)
        gobject.idle_add(MyHandler.handleRequest,self.server)
        self.log("Start")



    def setNodes(self,ln):
        self.mix =Mix(ln)

    def log(self,t):
        t="%s : %s \n" % (datetime.datetime.now().strftime("%H:%M:%S") , t)
        end_iter = self.textview1.get_buffer().get_end_iter()
        self.textview1.get_buffer().insert(end_iter, t)
        self.textview1.scroll_to_iter(end_iter,0)

    def quitt(self):
        self.log("Stop")
        self.main_widget.set_sensitive(False)
        MyHandler.stopHandler()

        #~ while gtk.events_pending():
            #~ gtk.main_iteration()

        self.server.server_close()
        self.quit()




    def on_winWeb_delete_event(self, widget, *args):
        self.quitt()



    def on_btn_stop_clicked(self, widget, *args):
        self.quitt()





def main():
    # fake photonode ...
    ln=[]
    for i in range(200):
        ln.append(pn())

    win_web = Winweb()
    win_web.setNodes(ln)

    win_web.loop()

if __name__ == "__main__":
    main()


