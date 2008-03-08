# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $
inherit eutils

DESCRIPTION="Photo manager written in python/pygtk"
HOMEPAGE="http://jbrout.python-hosting.com/wiki/WikiStart"
SRC_URI="http://jbrout.free.fr/download/sources/${P}.sources.tar.gz"

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
	dev-python/imaging"

RDEPEND="${DEPEND}"

S="${WORKDIR}/${PN}"

src_unpack() {
	unpack ${A}
	cd "${S}"
}

src_install() {
	insdir="/usr/local/jbrout"
	cd "${S}"

	dodir ${insdir}
	exeinto ${insdir}
	doexe *.py *.glade
	insinto ${insdir}/po
	doins po/*.pot
	insinto ${insdir}/po/fr/LC_MESSAGES
	doins po/fr/LC_MESSAGES/*.mo
	doins po/fr/LC_MESSAGES/*.po
	insinto ${insdir}/po/it/LC_MESSAGES
	doins po/it/LC_MESSAGES/*.mo
	doins po/it/LC_MESSAGES/*.po

	dodir ${insdir}/gfx
	insinto ${insdir}/gfx
	doins gfx/*.png gfx/*.ico gfx/*.xcf

	dodir ${insdir}/libs
	exeinto ${insdir}/libs
	doexe libs/*.py

	exeinto ${insdir}/plugins
	doexe plugins/*.py
	exeinto ${insdir}/plugins/comment
	doexe plugins/comment/*.py plugins/comment/*.glade
	insinto ${insdir}/plugins/comment/po
	doins plugins/comment/po/*.pot
	insinto ${insdir}/plugins/comment/po/fr/LC_MESSAGES
	doins plugins/comment/po/fr/LC_MESSAGES/*.mo
	doins plugins/comment/po/fr/LC_MESSAGES/*.po
	insinto ${insdir/plugins/comment/}/po/it/LC_MESSAGES
	doins plugins/comment/po/it/LC_MESSAGES/*.mo
	doins plugins/comment/po/it/LC_MESSAGES/*.po
	
	exeinto ${insdir}/plugins/foldersByDates
	doexe plugins/foldersByDates/*.py
	insinto ${insdir}/plugins/foldersByDates/po
	doins po/*.pot
	insinto ${insdir}/plugins/foldersByDates//po/fr/LC_MESSAGES
	doins plugins/foldersByDates/po/fr/LC_MESSAGES/*.mo
	doins plugins/foldersByDates/po/fr/LC_MESSAGES/*.po
	insinto ${insdir}/plugins/foldersByDates//po/it/LC_MESSAGES
	doins plugins/foldersByDates/po/it/LC_MESSAGES/*.mo
	doins plugins/foldersByDates/po/it/LC_MESSAGES/*.po
	
	exeinto ${insdir}/plugins/instantWeb
	doexe plugins/instantWeb/*.py plugins/instantWeb/*.glade
	insinto ${insdir}/plugins/instantWeb/po
	doins plugins/instantWeb/po/*.pot
	insinto ${insdir}/plugins/instantWeb/po/fr/LC_MESSAGES
	doins plugins/instantWeb/po/fr/LC_MESSAGES/*.mo
	doins plugins/instantWeb/po/fr/LC_MESSAGES/*.po
	insinto ${insdir}/plugins/instantWeb/po/it/LC_MESSAGES
	doins plugins/instantWeb/po/it/LC_MESSAGES/*.mo
	doins plugins/instantWeb/po/it/LC_MESSAGES/*.po
	
	exeinto ${insdir}/plugins/multiexport
	doexe plugins/multiexport/*.py plugins/multiexport/*.glade
	insinto ${insdir}/plugins/multiexport/po
	doins plugins/multiexport/po/*.pot
	insinto ${insdir}/plugins/multiexport/po/fr/LC_MESSAGES
	doins plugins/multiexport/po/fr/LC_MESSAGES/*.mo
	doins plugins/multiexport/po/fr/LC_MESSAGES/*.po
	insinto ${insdir}/plugins/multiexport/po/it/LC_MESSAGES
	doins plugins/multiexport/po/it/LC_MESSAGES/*.mo
	doins plugins/multiexport/po/it/LC_MESSAGES/*.po
	exeinto ${insdir}/plugins/multiexport/libs
	doexe plugins/multiexport/libs/*.py
	exeinto ${insdir}/plugins/multiexport/libs/picasaweb
	doexe plugins/multiexport/libs/picasaweb/*.py
	exeinto ${insdir}/plugins/multiexport/libs/picasaweb/atom
	doexe plugins/multiexport/libs/picasaweb/atom/*.py
	exeinto ${insdir}/plugins/multiexport/libs/picasaweb/gdata
	doexe plugins/multiexport/libs/picasaweb/gdata/*.py
	exeinto ${insdir}/plugins/multiexport/libs/picasaweb/gdata/base
	doexe plugins/multiexport/libs/picasaweb/gdata/base/*.py
	insinto ${insdir}/plugins/multiexport/xsl
	doins plugins/multiexport/xsl/*.xsl
	
	exeinto ${insdir}/plugins/openExplorer
	doexe plugins/openExplorer/*.py
	insinto ${insdir}/plugins/openExplorer/po
	doins plugins/openExplorer/po/*.pot
	insinto ${insdir}/plugins/openExplorer/po/fr/LC_MESSAGES
	doins plugins/openExplorer/po/fr/LC_MESSAGES/*.mo
	doins plugins/openExplorer/po/fr/LC_MESSAGES/*.po
	insinto ${insdir}/plugins/openExplorer/po/it/LC_MESSAGES
	doins plugins/openExplorer/po/it/LC_MESSAGES/*.mo
	doins plugins/openExplorer/po/it/LC_MESSAGES/*.po
	
	exeinto ${insdir}/plugins/redate
	doexe plugins/redate/*.py plugins/redate/*.glade
	insinto ${insdir}/plugins/redate/po
	doins plugins/redate/po/*.pot
	insinto ${insdir}/plugins/redate/po/fr/LC_MESSAGES
	doins plugins/redate/po/fr/LC_MESSAGES/*.mo
	doins plugins/redate/po/fr/LC_MESSAGES/*.po
	insinto ${insdir}/plugins/redate/po/it/LC_MESSAGES
	doins plugins/redate/po/it/LC_MESSAGES/*.mo
	doins plugins/redate/po/it/LC_MESSAGES/*.po
	
	exeinto ${insdir}/plugins/rotate
	doexe plugins/rotate/*.py
	insinto ${insdir}/plugins/redate/po
	doins plugins/redate/po/*.pot
	insinto ${insdir}/plugins/redate/po/fr/LC_MESSAGES
	doins plugins/redate/po/fr/LC_MESSAGES/*.mo
	doins plugins/redate/po/fr/LC_MESSAGES/*.po
	insinto ${insdir}/plugins/redate/po/it/LC_MESSAGES
	doins plugins/redate/po/it/LC_MESSAGES/*.mo
	doins plugins/redate/po/it/LC_MESSAGES/*.po
	insinto ${insdir}/plugins/rotate/gfx
	doins plugins/rotate/gfx/*.png
	
	exeinto ${insdir}/plugins/viewExif
	doexe plugins/viewExif/*.py plugins/viewExif/*.glade
	insinto ${insdir}/po
	doins plugins/viewExif/po/*.pot
	insinto ${insdir}/plugins/viewExif/po/fr/LC_MESSAGES
	doins plugins/viewExif/po/fr/LC_MESSAGES/*.mo
	doins plugins/viewExif/po/fr/LC_MESSAGES/*.po

	exeinto /usr/bin
	doexe ${FILESDIR}/jbrout

	doicon ${FILESDIR}/jbrout.png
	make_desktop_entry "jbrout" "jBrout Photo Manager" "jbrout"	"Graphics;Photography"

	
}
