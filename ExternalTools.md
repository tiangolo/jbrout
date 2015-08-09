# DOC : External Tools #
In a recent update of jBrout (>= 0.2.113), a new feature is available, it's called "External Tools". It let you specify some external tools, and use them from jbrout.

And jbrout **preserve yours informations (exif, iptc ...)** while processing external tools. You will not loose yours tags, comment, exif data !!!!

So you can personalize your own needs :
  * enhancement of photo
  * generate thumbnails
  * make color histograms
  * ...

## Configuration ##
Just use the entry "Edit external tools" in the main menu, under "File Menu". It runs a text editor, and you can add your external tools according the defined structure :

```
[Can modify] | [Label of the entry menu] | [command line]
```

  * **Can modify** :  must be **1 or 0**. It's to tell to jbrout if this external tools can modify the picture. Only you can know that. And it will only enable/disable the entry menu when Jbrout is in "view mode" only. (If a external tools modify a picture, it will not be available in mode "view")
  * **Label** : it's the name of the menu entry in the contextual menu, under "External tools".
  * **Command line** :  is the command line to call the external tools (see belove).

**Note :**
  * if a line starts with a '#' : it's a comment, and it's not interpreted by jbrout

### Command Line ###
You can make some powerful call by using some internal pattern. Here they are :

```
Mass process:
   $* : all files (can't be used with others patterns)

File process:
   $f : file path
   $F : file name
   $a : album path
   $A : album name
   $t : tags separated by a comma
   $c : comment jpeg
   $d : datetime exif
```

**Important**

When many pictures are selected:
  * If you call a command like 'gimp $**' : it will run one gimp and open all selected pictures.
  * If you call a command like 'gimp $f' : it will run many gimps : one by picture !
So the use of $** and $f/$a/... **are exclusive** !! '$**' is for mass process, so you can't specify another pattern !**

Here are some examples :
```
1|Write comment on the image| montage -geometry +0+0 -background white -label "$c" -pointsize 40 $f $f
```
This entry will write the comment under the picture, in a white box. It will be called for each selected picture ! (it use Image Magick)

```
1|Make a border| convert $f -bordercolor white -compose Copy  -border 20 $f
```
This entry will make a white border around the selected pictures. It will be called for each selected picture ! (it use Image Magick)

```
1|Open in Gimp|      /usr/bin/gimp $*
```
This entry will open one gimp with all selected pictures. (it use gimp ;-)

```
1|Open in XnView|      "c:/Program Files/XnView/XnView" $*
```
On Windows : This entry will open one xnview with all selected pictures. (it use xnview ;-)


## Use an external tools ##
When you select photos, you can access to external tools, by selecting the menu entry "External Tools" in the contextual menu of the selection.

Many image processing tools are not aware of internal informations (exif, iptc ..), and destroy them after manipulations. But when you use yours external tools from jbrout, jbrout will backup extra informations and put it back after the work. So, you are pretty sure to not loose capital informations ! Everything is preserved (exif, iptc, jpeg comment, file date ...), and the internal thumbnail is regenerated !

**IF YOU FIND SOME USEFULL EXTERNAL TOOLS, AND GREAT COMMAND LINE, don't hesitate to post them in the forum, and i will include them in jbrout**