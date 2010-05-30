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
## URL : http://jbrout.googlecode.com

from subprocess import Popen,PIPE
import os,sys,time,string


import re

def splitCommandLine(cmd):
    SUB= "[@]"
    g=re.findall('"[^"]*"',cmd)
    for i in g: cmd=cmd.replace(i,SUB)
    c=0 ; nl=[]
    for i in cmd.split():
        if i==SUB:
            nl.append( g[c][1:-1] )
            c+=1
        else:
            if SUB in i: return None
            nl.append( i.strip('"') )
    return nl

def testSplitCommandLine():
    assert splitCommandLine("""/bin/toto   " to fork" -aa """) == \
                   ['/bin/toto', ' to fork', '-aa']

    assert splitCommandLine(""" /bin/toto  " to fork " -aa " h l " -i "9" """) == \
                    ['/bin/toto', ' to fork ', '-aa', ' h l ', '-i', '9']

    assert splitCommandLine("""  /bin/to to   -s 'ko ko '""") == \
                   ['/bin/to','to', '-s',"'ko","ko","'"]

    assert splitCommandLine("""  /bin/toto "ko """) == \
                   ['/bin/toto','ko']

    assert splitCommandLine("""  /bin/toto "ki ki " "ko """) == \
                   ['/bin/toto',"ki ki ",'ko']

    assert splitCommandLine("""  /bin/toto ko" """) == \
                   ['/bin/toto','ko']

    assert splitCommandLine("""  /bin/toto ko"ka """) == \
                   ['/bin/toto','ko"ka']

    assert splitCommandLine("""  /bin/toto " ko ka"ku """) == None
    assert splitCommandLine("""  /bin/toto ku" ko ka" """) == None
    assert splitCommandLine("""  /bin/toto " ko ka"-ku """) == None
    assert splitCommandLine("""  /bin/toto -ku" ko ka" """) == None
    assert splitCommandLine("") == []



#========================================================
class ExternalTool(object):
#========================================================
    label=property(lambda self: self.__label)

    # needed only to enable/disbable the entry menu
    canModify=property(lambda self: self.__canModify)

    def __init__(self,label,cmd,canModify=True):
        assert type(cmd)==unicode
        self.__line = cmd   # for __repr__ only
        self.__label=label
        self.__cmds=splitCommandLine(cmd)
        self.__canModify = canModify

    def __repr__(self):
        return "<externaltool: '%s' : %s>" % (self.__label,self.__line)

    def g_run(self,l,testOnly=False):
        assert type(l) == list

        if "$*" in self.__cmds:
            # run all in one command line
            # ($* = ONLY full filenames)
            cmds = self.__cmds
            cmds[ cmds.index("$*"):cmds.index("$*")+1 ] = [i.file for i in l]
            assert "$*" not in cmds, "multiple $*"
            self.__run(cmds,testOnly)
        else:
            # run one command line by item
            # (can use patterns $f,$a, ... NOT $*)
            for i in l:
                cmds = []
                for a in self.__cmds:
                    cmds.append( self.__subst(a,i))
                self.__run(cmds,testOnly)
                yield True
        yield False

    def __subst(self,a,n):
        rp = lambda c,r,s: re.sub("(\$"+c+")([^\w]|\Z)",r+"\\2",s)
        assert rp("f","[X]","$f xxx $f $foo xx$f $f xxx $foo $f") == "[X] xxx [X] $foo xx[X] [X] xxx $foo [X]"
        a=rp("f",n.file,a)
        a=rp("F",n.name,a)
        a=rp("a",n.folder,a)
        a=rp("A",n.folderName,a)
        a=rp("t",", ".join(n.tags),a)
        a=rp("c",n.comment,a)
        a=rp("d",n.date,a)
        return a

    def __run(self,cmds,testOnly):
        if testOnly:
            print " - ",cmds
        else:
            try:
                cmds = [i.encode(sys.getfilesystemencoding()) for i in cmds]

                p = Popen(cmds, shell=False,stdout=PIPE,stderr=PIPE)
                time.sleep(0.01)    # to avoid "IOError: [Errno 4] Interrupted system call"
                out = string.join(p.stdout.readlines() ).strip()
                outerr = string.join(p.stderr.readlines() ).strip()
            except Exception,m:
                raise m
            return out+outerr

defaultContent=u"""# -*- coding: utf-8 -*-
# =============================================================================
# HERE YOU CAN EDIT YOUR EXTERNAL TOOLS, here are the usable patterns
# See: http://code.google.com/p/jbrout/wiki/ExternalTools
# =============================================================================
# $* : all files (can't be used with others patterns)
# $f : file path
# $F : file name
# $a : album path
# $A : album name
# $t : tags separated by a comma
# $c : comment jpeg
# $d : datetime exif
# =============================================================================


# here are some external tools to uncomment ::
#  1|Edit with The Gimp|gimp $*
#  1|Write Comment on the picture| montage -geometry +0+0 -background white -label "$c" -pointsize 40 $f $f
#  0|Slideshow|qiv -s -d 3 -f -i $*
#  0|File Date from EXIF| exiv2 -T mv $*
#  0|Send...|nautilus-sendto $*

"""

#========================================================
class ExternalTools(list):
#========================================================
    @staticmethod
    def generate(file):
        """ generate an 'external tools file' at 'file' """
        # TODO : generate it !
        buf = defaultContent.encode("utf_8")
        fid=open(file,"w")
        fid.write(buf.replace("\n","\r\n") )
        fid.close()

    def __init__(self,file):
        list.__init__(self,[])

        if type(file)==unicode or type(file)==str:
            # it's a filename
            ExternalTools.file = file   # to replace $x
            if os.path.isfile(file):
                f=open(file)
            else:
                f=[]
        elif hasattr(file,"read"):
            # it's a IO buffer, for the test
            ExternalTools.file = "FAKE_TEXT"   # to replace $x
            f=file
        else:
            raise Exception("ExternalTools() : bad constructor")


        for line in f:
            line=unicode(line.strip())
            if line:
                if line.startswith("#"):
                    # it's a comment ... ignore it
                    pass
                else:
                    items = line.split("|")
                    if len(items)>=3:
                        canModify = items[0].strip() == "1"
                        label = items[1].strip()
                        cmd = line[ line.index(items[2]): ].strip()
                        self.append( ExternalTool(label,cmd,canModify))







class Fpn:   # Fake PhotoNode
    def __init__(self,f):
        self.file = f
        self.name = os.path.basename(f)
        self.folder = os.path.dirname(f)
        self.folderName = os.path.basename(os.path.dirname(f))
        self.tags = ["zoe","luna"]
        self.comment = "it's a comment !"
        self.date = "14/11/1970 14:20:00"


if __name__=="__main__":
    testSplitCommandLine()  #unittest


    tools=u"""# -*- coding: utf-8 -*-
    # $* : all files (can't be used with others patterns)
    # $f : file path
    # $F : file name
    # $a : album path
    # $A : album name
    # $t : tags separated by a comma
    # $c : comment jpeg
    # $d : datetime exif

    # cool scripts here : http://artmoves.free.fr/?p=199

    1|Edite dans gimp|      /usr/bin/gimp -s $* -t
    1|edite dans gthumb|    /usr/bin/gthumb $*
    0|mk thumb|             mkthumb $f
    1|augmente contraste|   /usr/bin/convert "re $A.bak" -jo "$c" $f
    0|Edit External tools|  gedit $x
    1|Test win             |notepad $f $a.txt

    """

    import StringIO
    et=ExternalTools( StringIO.StringIO(tools) )

    # test rendering command line
    l=[Fpn(u"/home/manatlan/Desktop/fotaux/test_jbrout/nouveau dossier/p20040616_185047.jpg"),
        Fpn(u"/home/manatlan/Desktop/fotaux/test_jbrout/nouveau dossier/p20040730_213710.jpg")]
    for i in et:
        print i
        g=i.g_run(l,testOnly=True)
        while g.next() : pass

    #~ # test win
    #~ l=[Fpn(ur"D:\Documents and Settings\si07375\Bureau\Nouveau Document texte.txt")]
    #~ et[-1].run(l)
