#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup
#import py2exe
import sys
import glob

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
if sys.version < '2.2.3':
    from distutils.dist import DistributionMetadata
    DistributionMetadata.classifiers = None
    DistributionMetadata.download_url = None
import os

from distutils.command.install_data import install_data
class smart_install_data(install_data):
    def run(self):
        #need to change self.install_dir to the library dir
        install_cmd = self.get_finalized_command('install')
        self.install_dir = getattr(install_cmd, 'install_lib')
        return install_data.run(self)

def isPackage( filename ):
    return(
        os.path.isdir(filename) and
        os.path.isfile(os.path.join(filename,'__init__.py'))
    )

def packagesFor( filename, basePackage="" ):
    """Find all packages in filename"""
    set = {}
    for item in os.listdir(filename):
        dir = os.path.join(filename, item)
        if isPackage( dir ):
            if basePackage:
                moduleName = basePackage+'.'+item
            else:
                moduleName = item
            set[ moduleName] = dir
            set.update( packagesFor( dir, moduleName))
    return set

def filesFor( dirname ):
    """Return all non-python-file filenames in dir"""
    result = []
    allResults = []
    for name in os.listdir(dirname):
        path = os.path.join( dirname, name )
        if (
            os.path.isfile( path) and
            os.path.splitext( name )[1] in
                ('.glade','.txt','.pot','.po','.mo','.png','.xcf','.ico','.xsl','.exe')
        ):
            result.append( path )
        elif os.path.isdir( path ) and name.lower() not in ('dist','.svn'):
            allResults.extend( filesFor(path))
    if result:
        allResults.append( (dirname, result))
    return allResults
srcPath = '.'
try:
    __version__ = open(os.path.join(srcPath,"jbrout","data","version.txt"))\
        .read().strip()
except:
    __version__ = "src"


dataFiles = filesFor( srcPath)
packages = packagesFor(srcPath)
setup(
    name="jbrout",
    description="Photo manager written in python/pygtk",
    version=__version__,
    author="Marc Lentz",
    author_email="matlan@gmail.com",
    maintainer="Rob Wallace",
    maintainer_email="rob@wallace.gen.nz",
    url="http://jbrout.googlecode.com",
    packages=packages.keys(),
    data_files = dataFiles,
    license="GPL-2",
    long_description="Photo manager written in python/pygtk for Win32, Linux",
    cmdclass = {'install_data':smart_install_data},
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License Version 2 only (GPL-V2)',
        'Natural Language :: English',
        'Natural Language :: French',
        'Natural Language :: Italian',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Viewers',
    ],
)
