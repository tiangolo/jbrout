# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $
inherit subversion eutils distutils

ESVN_REPO_URI="http://jbrout.googlecode.com/svn/trunk/"

DESCRIPTION="Photo manager written in python/pygtk"
HOMEPAGE="http://http://code.google.com/p/jbrout/"
SRC_URI=""

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~x86 ~amd64"
IUSE=""

DEPEND=">=dev-lang/python-2.4
	dev-libs/libxml2
	dev-libs/libxslt
	>=dev-python/pygtk-2.6
	media-gfx/fbida
	media-gfx/jhead
	dev-python/lxml
	dev-python/imaging
	>=media-gfx/pyexiv2-0.1.2"

RDEPEND="${DEPEND}"

S="${WORKDIR}/${PN}" 

src_unpack() {
	#mkdir ${S}
	#cd ${S}
	#svn export http://jbrout.googlecode.com/svn/trunk/setup.py -r HEAD setup.py
	#svn export http://jbrout.googlecode.com/svn/trunk/jbrout -r HEAD jbrout
	
	subversion_src_unpack
	cd "${S}"
}

#src_compile(){
#}

src_install() {
	distutils_src_install

	cd ${D}
	mkdir ${S}/sh
	echo -e "#\041/bin/bash" >> ${S}/sh/jbrout
	echo "cd $(find -name jbrout.py | cut -c2- | rev | cut -c11- | rev)" >> ${S}/sh/jbrout
	echo "/usr/bin/env python jbrout.py \$@" >> ${S}/sh/jbrout

	exeinto /usr/bin
	doexe ${S}/sh/jbrout

	doicon ${S}/jbrout/data/gfx/jbrout.png
	make_desktop_entry "jbrout" "jBrout Photo Manager" "jbrout" "Graphics;Photography"

}
