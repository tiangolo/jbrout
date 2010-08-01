# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: $
inherit eutils

DESCRIPTION="pyexiv2 is a python binding to exiv2, the C++ library for manipulation of EXIF and IPTC image metadata"
HOMEPAGE="http://tilloy.net/dev/pyexiv2/index.htm"
SRC_URI="http://launchpad.net/pyexiv2/0.2.x/${PV}/+download/${P}.tar.bz2"

LICENSE="GPL-2"
SLOT="0"
KEYWORDS="~x86 ~amd64"
IUSE="doc"

DEPEND=">=dev-lang/python-2.5.1
	>=media-gfx/exiv2-0.19
	>=dev-libs/boost-1.35
	dev-util/scons
	doc? ( dev-python/sphinx )"

RDEPEND="${DEPEND}"

S=${WORKDIR}/${P}

src_unpack() {
	unpack ${A}
	cd "${S}"
}

src_compile() {
	cd "${S}"
	scons lib || die " Build Failed"
}

src_install() {
	cd "${S}"
	scons DESTDIR=${D} install || die "Install Failed"
	if use doc ; then
		dohtml "${S}/doc/html/api.html"
		dohtml "${S}/doc/html/developers.html"
		dohtml "${S}/doc/html/genindex.html"
		dohtml "${S}/doc/html/index.html"
		dohtml "${S}/doc/html/modindex.html"
		dohtml "${S}/doc/html/release_procedure.html"
		dohtml "${S}/doc/html/search.html"
		dohtml "${S}/doc/html/searchindex.js"
		dohtml "${S}/doc/html/tutorial.html"
		docinto "/html/_static"
		dodoc "${S}/doc/html/_static/basic.css"
		dodoc "${S}/doc/html/_static/default.css"
		dodoc "${S}/doc/html/_static/doctools.js"
		dodoc "${S}/doc/html/_static/file.png"
		dodoc "${S}/doc/html/_static/jquery.js"
		dodoc "${S}/doc/html/_static/minus.png"
		dodoc "${S}/doc/html/_static/plus.png"
		dodoc "${S}/doc/html/_static/pyexiv2-big-192x192.png"
		dodoc "${S}/doc/html/_static/pyexiv2.ico"
		dodoc "${S}/doc/html/_static/pygments.css"
		dodoc "${S}/doc/html/_static/searchtools.js"
	fi

}
