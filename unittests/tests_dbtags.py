#!/usr/bin/env python
# -*- coding: utf-8 -*-

__builtins__.__dict__["_"] = lambda x: x

from jbrout.db import *
import os

if __name__ == "__main__":

    ##########################################################################
    # # Tests DBTags, CatgNode and TagNode
    ##########################################################################
    file = "/home/manatlan/db_jbrout_tags.xml"
    if os.path.isfile(file):
        os.unlink(file)
    dbt = DBTags(file)
    assert dbt.getAllTags() == [], "dbtag not empty"
    assert dbt.updateImportedTags([u"ab", u"ac"]) == 2, \
        "update import tag error"
    assert len(dbt.getAllTags()) == 2, "not 2 tags in dbtag"

    r = dbt.getRootTag()
    assert r.name == "Tags", "First catg is not named 'Tags'"
    assert r.getTags() == [], "..."
    assert len(r.getAllTags()) == 2
    lrc = r.getCatgs()
    assert len(lrc) == 1
    catg = lrc[0]
    assert catg.name == "Imported Tags"

    tag = r.addTag(u"kiki")
    assert tag
    assert not r.addTag(u"kiki")
    assert len(r.getTags()) == 1
    assert len(r.getAllTags()) == 3
    tag.moveToCatg(catg)  # move tag in another catg
    assert r.getTags() == []
    assert len(r.getAllTags()) == 3
    assert len(catg.getTags()) == 3
    assert len(catg.getAllTags()) == 3

    ncatg = r.addCatg(u"kôko")
    assert ncatg
    assert not r.addCatg(u"kôko")
    assert len(r.getCatgs()) == 2
    assert ncatg.name == u"kôko"

    assert ncatg.expand is True
    ncatg.setExpand(False)
    assert ncatg.expand is False

    ncatg.moveToCatg(catg)  # move catg in another catg
    assert len(catg.getCatgs()) == 1
    ncatg.remove()
    assert len(catg.getCatgs()) == 0

    tag.remove()
    assert len(r.getAllTags()) == 2
    tag = r.addTag(u"kloûm")
    assert len(r.getAllTags()) == 3
    assert tag.name == u"kloûm"

    dbt.save()
    dbt = DBTags(file)
    assert len(r.getAllTags()) == 3

    assert open(file, "r").read() == \
        '<?xml version="1.0" encoding="UTF-8"?><tags>' + \
        '<tags name="Imported Tags"><tag>ab</tag><tag>ac</tag></tags>' + \
        '<tag>kloûm</tag></tags>'
    os.unlink(file)

    # ~ file="/home/manatlan/db_jbrout_albums.xml"
    # ~ DBPhotos( file )
