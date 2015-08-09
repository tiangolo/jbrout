## to be continued ##

**jbrout** depends on :

  * python (works with python >=2.4, but needs 2.5 to use the picasaweb plugin)
  * python-lxml (>=0.7)
  * python-gtk2
  * python-glade2
  * python-imaging (also known as [pil](http://www.pythonware.com/products/pil/))
  * python-pyexiv2 (>=0.1.2)


## Jbrout tools/libs ##

**jBrout** use some external tools.

  * on **Win32 systems** : they are provided in the [tools folder](http://jbrout.googlecode.com/svn/trunk/data/tools/).
    * ~~Jhead of [Matthias Wandel](http://www.sentex.net/~mwandel/jhead/) (Public domain). Which is used to extract exif information of pictures, and exif-redate pictures.~~
    * ~~Jpegnail of [photomolo](http://www.funet.fi/pub/sci/graphics/packages/photomolo/photomolo.html) from [Marko Mäkelä](http://www.funet.fi/~msmakela/) (GPL licence). Which is used to rebuild internal exif thumbnail on win32 platform.~~
    * Jpegtran of [Jpeg Club](http://sylvana.net/jpegcrop/)(public Domain). Which is used to rotate loss-less pictures on win32 platform.

  * on **`*nix systems`**, **you should install them** ! So, please, install them for your distribution :
    * Exiftran of [Gerd Knorr](http://linux.bytesex.org/fbida/) (GPL licence). (also known as "fbida package"). Which is used to rotate loss-less pictures.
    * ~~Jhead of [Matthias Wandel](http://www.sentex.net/~mwandel/jhead/) (Public domain).~~


~~**jBrout** sources comes with external python libs, located in [libs folder](http://jbrout.googlecode.com/svn/trunk/libs/) :
  *~~EXIF.py from [Gene Cash](http://home.cfl.rr.com/genecash/digital_camera.html) (GPL licence)~~*~~iptcinfo.py from [Tamás Gulácsi](http://www.python.org/pypi?%3Aaction=search&name=&version=&summary=&description=iptc&keywords=&_pypi_hidden=0) (GPL licence)