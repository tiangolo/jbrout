#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os,sys

import time,string
from subprocess import Popen,PIPE
def run(cmds):
    p = Popen(cmds, shell=False,stdout=PIPE,stderr=PIPE)
    time.sleep(0.01)    # to avoid "IOError: [Errno 4] Interrupted system call"
    out = string.join(p.stdout.readlines() ).strip()
    outerr = string.join(p.stderr.readlines() ).strip()
    return out

def megarun(m):
    ligne = m.split("\n")
    for i in ligne:
        i=i.strip()
        if i:
            print ">>",i
            os.system(i)


import os,sys,stat
from fnmatch import fnmatch

def glob(path,exts=[],excludes=[],includes=[],absolute=True):
    #-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    def walktree (top = ".", depthfirst = True):
        names = os.listdir(top)
        if not depthfirst:
            yield top, names
        for name in names:
            try:
                st = os.lstat(os.path.join(top, name))
            except os.error:
                continue
            if stat.S_ISDIR(st.st_mode):
                for (newtop, children) in walktree (os.path.join(top, name), depthfirst):
                    yield newtop, children
        if depthfirst:
            yield top, names
    #-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

    if exts:
        lexts=[i.lower() for i in exts]

    path=os.path.normpath(path)
    list=[]
    for (basepath, children) in walktree(path,False):
        for child in children:
            add=True
            rpath = os.path.join(basepath[len(path)+1:], child)

            if includes:
                add=False
                for i in includes:
                    if fnmatch(rpath,i):
                        add = True
                        break
                if not add:
                    continue

            if excludes:
                for i in excludes:
                    if fnmatch(rpath,i):
                        add = False
                        break
                if not add:
                    continue

            if exts:
                if child.split(".")[-1].lower() not in lexts:
                    continue

            if add:
                if absolute:
                    file = os.path.join(basepath, child)
                else:
                    file = rpath
                list.append( file.decode( sys.getfilesystemencoding() ) )

    return list

if __name__ == "__main__":
    pass
