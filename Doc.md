### [You should read that](http://jbrout.free.fr/help/) ###

## Documentation ##

## First use, you must know ##
**jBrout** can rename your photos when you import them. It can rename and redate (filesystem) according the exif timestamp ! At the first use, JBrout ask you if you want to do so. (recommanded)
**important** : it's a best practice to let jbrout renaming your pictures !

## Use the interface ##
**jBrout** got a simple interface. Main actions are in drag'n'drop or by the contextual menu.
  * it load the ''database'' at the start, and save it when you quit. But modifications on pictures are done in live.
  * it is full of drag'n'drop features (move photos from folder to another, move folders, tag photos, ...)
  * when multiple selection is enabled (select multiples photos or multiple tags), you can use CTRL or SHIFT to select. BUT **you can use the middle click too** (like in rox-filer) ... it's a real breeze !!!!

## Use the search system ##
Here is a [a flash demo](http://jbrout.free.fr/demo/jbrout_search.htm), to learn to use the powerful search engine of **jBrout** ;-)

## Image Legend ##
**jBrout** use the "Internal Exif Thumbnail" of your photo to display a thumbnail. It displays some pictures/effects too, to inform you on the nature of the photo.

If the thumbnail have got **RED** borders, your photo hadn't got valid exif information (or bad exif format), and jBrout had setted them (minimal exif information, setted at import/refresh). If they are **wHITE**, your photo have got a valid exif information.

If your photo can't be modified (because it's write-protected), the http://jbrout.python-hosting.com/file/trunk/gfx/check_no.png?rev=1&format=raw icon is displayed at the top-right of your thumbnail.

If the http://jbrout.python-hosting.com/file/trunk/gfx/basket.png?rev=1&format=raw icon appears in the top-left of your thumbnail, it's to warn you that it is selected in the basket system.

Here are the images which can be displayed in place of your thumbnails :
|http://jbrout.python-hosting.com/file/trunk/gfx/refresh.png?format=raw | jBrout is searching for the thumbnail, it will appear soon ;-) |
|:----------------------------------------------------------------------|:---------------------------------------------------------------|
|http://jbrout.python-hosting.com/file/trunk/gfx/imgNoThumb.png?format=raw | It seems that your photo doesn't have a thumbnail, try to rebuild it with the contextual menu. (but sometimes jBrout is not able to rebuild the internal thumbnail) |
|http://jbrout.python-hosting.com/file/trunk/gfx/imgError.png?format=raw | This photo have got a bad "exif format"                        |
|http://jbrout.python-hosting.com/file/trunk/gfx/imgNotFound.png?format=raw | This photo is in the database of jbrout, but doesn't exists on your harddisk ! Just refresh your album/folder. (in fact, if you see this picture, there is a **bug** in jbrout) |


## Use External Tools ##
jBrout can now use ExternalTools, without loosing exif/iptc metadata

**... to be continued ...**