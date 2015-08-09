![http://jbrout.googlecode.com/svn/trunk/jbrout/data/gfx/jbrout.png](http://jbrout.googlecode.com/svn/trunk/jbrout/data/gfx/jbrout.png)

**jBrout** is a photo manager, written in python/pygtk under the GPL licence. It's cross-platform, and has been tested on GNU/linux and windows XP/2k.

**jBrout** is able to :
  * manage albums/photos (= folders/files)
  * tag photos with IPTC keywords
  * use internal exif jpeg thumbnail
  * comment photos (with jpeg comment) and album (textfile in folder)
  * rotate loss-less jpeg (and internal exif jpeg thumbnail)
  * use EXIF info (date, size ..)
  * search pictures (tags, comment, date, ...) (a [flash demo](http://jbrout.free.fr/demo/jbrout_search.htm))
  * use plugins (to export to html/gallery, to act like a httpserver, to export pictures to be mailed, ...)
  * work without database ! (just a xmlfile which can be rebuild from scratch)
  * handle a lot of photos (me : more than 30000)
  * export to a flickr account, **to a picasaweb account**
  * use a basket system to pick some photos
  * can be localized (now French and english version)
  * create minimal exif informations for pictures without exif
  * auto rotation of pictures
  * share pictures to upnp/dlna devices
  * ...

JBrout can be downloaded in the [Download](Install.md) section !

**jBrout** is looking for beta-testers, plugin developpers, packagers, translators, wiki'ers ... if you are interested, contact me (i'm french).

### History ###
The [first jBrout](http://jbrout.free.fr) was my first python application. I'd started to developp it because i was unable to find a ''good application'' to manage my collection of pictures. I'd tested a lot of well-known applications (adobe photoshop album, picasa, imatch, jasc photoalbum...) on windows. But no one was perfect (use of database (and often proprietary database), no respect for pictures, not cross-platforms (for future)...), so i've decided to build my own, and build & use jBrout ! Now, i've redevelopped jBrout 0.2.x from scratch ! I manage more than 30000 photos, with iptc keywords, and i'm really happy ...

jBrout stands for J-Brout. "J" as Jpeg, and "brout" as brouteur (a french world meanning "browser"). When i'd started this project google returned 0 pages pour the word "jbrout" ;-)

### Concepts ###
**jBrout** doesn't use a database to handle your pictures ! It just uses a xml file to handle your tags ! The albums/pictures are managed like folders/files !!!
All information that could be used in the interface are stored in your pictures :
  * tags (as IPTC keywords, in the picture)
  * dates (as EXIF tags, in the picture)
  * comments ( as JPEG comment, in the picture)
  * album comments ( as a text file in the folder of the picture)
  * thumbnails ( as EXIF internal thumbnail, in the picture)

In fact, it uses an xml file to handle your pictures, but this FILE can be rebuilt from scratch at anytime, because all informations are in your filesystem, not in a database !!

**jBrout** RESPECTS your pictures ! it doesn't change any capital information in your pictures ! (internal thumbnail are respected ! rotation are loss-less...). jBrout uses well-known tools for lossless rotation (jpegtran on win32, exiftran on **nix))**

**jBrout** doesn't clutter your disk by building thumbnail for each picture ! It uses the internal exif thumbnails stored in your pictures !


### Plugin'able ###
**jBrout** is pluginable ! In jBrout, Plugins are tools that can be applied on a set of pictures, or on an album. You can select one or more pictures, or an album, and call a plugin in the contextual menu. Here are the plugins :
  * "comment" : to set a comment for a set of pictures, to set a comment per picture. (Use core functions)
  * "redate" : to shift the dates of the pictures. (Use core functions)
  * "rotate" : to rotate loss-less the pictures. (Use core functions)
  * "exportToHtml" : to build an html-gallery ! HTML pages are created with a [XSLT](http://en.wikipedia.org/wiki/XSLT) stylesheet. (if you know XSLT, it should be really easy to build your own XSLT stylesheet)
  * "export" : to export pictures to another folder (pictures can be resized, and recompressed)
  * "instantWeb" : to share your pictures on the [WWW](http://en.wikipedia.org/wiki/Www). It transforms jbrout as a [http server](http://en.wikipedia.org/wiki/HTTP_Server), and everyone can show your selected pictures in its own browser pointing at your IP.
  * "uploadToFlickr" : to upload photos (with tags and comment) to a flickr account
  * "uploadToPicasaWeb" : to upload photos (with comment as caption) to a PicasaWeb(google) account
  * "openExplorer" : open selected photo in ''explorer'' under windows or ''nautilus'' under **nix.
  * "viewExif" : display meta data (exif and iptc)**

Starts [your own plugin](DevPlugin.md), it's really easy !


### Roadmap ###
  * bugs chase & some little finitions