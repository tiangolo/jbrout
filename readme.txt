=======================================================================
JBrout 0.3.x - by Marc Lentz, under GPL2 licence
=======================================================================
Website    : http://jbrout.googlecode.com
Contact me : manatlan (AT] gmail [dOt) com
=======================================================================

Changes from 0.2.xxx
- new layout for codes/folders at top of svn :

    - jbrout/       : main application dir
        - data/     : all data
                      which now contains the previous "gfx" & "tools" folder,
                      gpl.txt, version.txt (used by jbrout to know who is it),
                      jbrout.glade
        - jbrout/   : core program
        - po/       : translations for main program (
        - libs/     : external libs
        - plugins/  : (the __init__.py contains the class jplugin now)
                      each plugins contains a folder "po"
        - jbrout.py : the application
    - unittests/ : unit tests
    - dist/         # Distribution scripts other than setup.py

- about's close button works now ;-)
- new icon
- folder unittests for unit tests
- download plugin for getting images from a mounted camera or flash card
- additional options for rotation plugin including auto-rotate
- option to auto-rotate on import
- new plugin for Down loading images from camera or media
