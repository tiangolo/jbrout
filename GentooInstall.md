# Introduction #
This page describes how to install jBrout under Gentoo Linux.
As jBrout is not in the main portage tree it must be installed using an overlay, the easiest way to do this and keep jBrout up to date is to use [Layman](http://layman.sourceforge.net).

# Installation #
## Setting up Layman ##
  1. Emerge layman
```
emerge app-portage/layman
```
  1. Add the layman configuration to make.conf
```
echo "source /usr/portage/local/layman/make.conf" >> /etc/make.conf
```

## Adding the jBrout overlay to Layman ##
  1. Modify the overlays section of /etc/layman/layman.cfg so that it is as follows:
```
overlays  : http://www.gentoo.org/proj/en/overlays/layman-global.txt
            http://jbrout.googlecode.com/svn/trunk/dist/gentoo/jbrout-layman-list.xml
```
  1. Add the jBrout overlay to your installed overlays
```
layman -f -a jbrout
```

## Installing jBrout ##
### Latest Package ###
  1. If you do not have "ACCEPT\_KEYWORDS="~amd64"" or "ACCEPT\_KEYWORDS="~x86"" in your /etc/make.conf you will need to keywords for jBrout-svn and pyexiv2 as follows:
```
echo "media-gfx/jbrout" >> /etc/portage/package.keywords
echo "media-gfx/pyexiv2" >> /etc/portage/package.keywords
```
  1. Emerge jBrout:
```
emerge jbrout
```

### Bleeding Edge (From Subversion) ###
  1. If you do not have "ACCEPT\_KEYWORDS="~amd64"" or "ACCEPT\_KEYWORDS="~x86"" in your /etc/make.conf you will need to keywords for jBrout and pyexiv2 as follows:
```
echo "media-gfx/jbrout-svn" >> /etc/portage/package.keywords
echo "media-gfx/pyexiv2" >> /etc/portage/package.keywords
```
  1. Emerge jBrout from Subversion:
```
emerge jbrout-svn
```

# Updating #
## Latest Package ##
  1. Update the Layman overlay:
```
layman -s jbrout
```
  1. Update jBrout:
```
emerge -u jbrout
```
> or
```
emerge -u world
```

## Bleeding Edge (From Subversion) ##
  1. Update the Layman overlay:
```
layman -s jbrout
```
  1. Update jBrout:
```
emerge jbrout-svn
```
**Note:** jBrout will not automatically stay up to date when "media-gfx/jbrout-svn" is installed as the ebuild only changes when a bug is found in it or the installation method changes which is unlikely to be as often as the releases are made for "media-gfx/jbrout".
So jbrout-svn must be reinstalled as shown above instead of updated individually or as part of world.