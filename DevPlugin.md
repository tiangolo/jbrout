## Plugin Interface ##


Here is the minimal plugin, the most simple you can do.
In the "plugins/" folder of the application, create a folder "minimal", and copy/paste the code behind in the file `plugins/minimal/__init__.py` :
```
#!/usr/bin/python
# -*- coding: utf-8 -*-

from __main__ import JPlugin

class Plugin(JPlugin):
    """ the minimal plugin """
    __author__ = "you"
    __version__ = "1.0"

    @JPlugin.Entry.PhotosProcess( _("say hello"), order=1 )
    def sayHello(self,listOfPhotoNodes):
        self.MessageBox("%d photos are selected" % len(listOfPhotoNodes))
        return False
```
Now, run jbrout, and you will have a new entry in the contextual menu which will be named "say hello". Select it, and it will display the number of pictures which are selected !
**Congratulations**, you have made your first jbrout's plugin  !!!

## How it works ##
Now, let's see how it works :

As you can see you must create a class "Plugin" which subclass JPlugin ! Your class should be named "Plugin", but in fact, the name/identifier of the plugin is the name of the folder. Here it is "minimal" !


### the JPlugin interface ###
The JPlugin interface provide some facilities. It exposes some usefull attributs :

  * id, a string, which is the name/identifier of the plugin (here it is "minimal")
  * path, a string, which is the relative path from jbrout to your plugin
  * conf, a dict, which can be used to store some preferences between 2 jbrout session (keys must be strings)
  * parent, a reference to the main gtk.Window of jbrout

And it exposes some GUI methods :

  * MessageBox(self,message,title=None) : display a message box
  * InputBox(self,val,message,title=None) : ask to modify the "val" in a message box, return the new val or None
  * InputQuestion(self,message,title=None) : ask to response yes or no, returns a boolean
  * showProgress(self,num=None,max=None,message=None) : display the progress bar at the position "num" on "max"
  * showProgress(self) : hide the progress bar

Notes :

  * when the plugin is called, it is executed in its context path. So when you use relative path, make sure they are relatives at your code !
  * the plugin can be translated, just add po/mo files in a "po" folder at the root of the plugin. jBrout provides a _() method in the namespace of the plugin._

### Kind of plugins ###
In this example, we made a plugin which process on a list of photos. But jBrout can have different kinds of plugins :

  * JPlugin.Entry.PhotosProcess : process on a list of photos
  * JPlugin.Entry.AlbumProcess : process on an album
  * ...

#### JPlugin.Entry.PhotosProcess ####
The method where this decorator is added must be like that :

> def method(self, listOfPhotoNodes): return boolean

Must return a boolean, which is used by jbrout to be able to know if the action has modified a PhotoNode (redated, rotated, ...). (true if something has been modified, else false) (see `PhotoNode` class in db.py)

the PhotosProcess can be defined like this :

> @JPlugin.Entry.PhotosProcess(label, icon=None, order=1000, alter=True, key=None)

  * label : a string to fill the entry of the contextual menu on photos.
  * icon : if defined, display an icon in the menu and in the toolbar
  * order : if defined, define the order of the entry point in the menu
  * alter : a information for jbrout, to let jbrout aware if this entry-point alter db/photos
  * key : the gtk keycode to call the plugin with CTRL+key

#### JPlugin.Entry.AlbumProcess ####
The method where this decorator is added must be like that :

> def method(self, folderNode): return boolean

Must return a boolean, which is used by jbrout to be able to know if the action has modified the folderNode (redated, rotated, ...). (true if something has been modified, else false) (see `FolderNode` class in db.py)

the AlbumProcess can be defined like this :

> @JPlugin.Entry.AlbumProcess(label, order=1000, alter=True):

  * label : a string to fill the entry of the contextual menu on an album.
  * order : if defined, define the order of the entry point in the menu
  * alter : a information for jbrout, to let jbrout aware if this entry-point alter db/albums/photos




**... to be continued ...**

To help you to developp your plugin, you should look thoses which are now in your jbrout. The simplest is rotate, which use internal methods of `PhotoNode` to rotate the pictures or rebuild internal exif thumbs ... "openExplorer" is really easy too ...