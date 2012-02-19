#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
# Originally from http://boodebr.org/main/python/all-about-python-and-unicode#UNI_XML
# http://coreapython.hosting.paran.com/boodebr/All%20About%20Python%20and%20Unicode%20%20boodebr_org.htm#UNI_XML

def raw_illegal_xml_regex():
    """
    I want to define a regexp to match *illegal* characters.
    That way, I can do "re.search()" to find a single character,
    instead of "re.match()" to match the entire string. [Based on
    my assumption that .search() would be faster in this case.]

    Here is a verbose map of the XML character space (as defined
    in section 2.2 of the XML specification):

         u0000 - u0008           = Illegal
         u0009 - u000A           = Legal
         u000B - u000C           = Illegal
         u000D                   = Legal
         u000E - u001F           = Illegal
         u0020 - uD7FF           = Legal
         uD800 - uDFFF           = Illegal (See note!)
         uE000 - uFFFD           = Legal
         uFFFE - uFFFF           = Illegal
         U00010000 - U0010FFFF = Legal (See note!)

    Note:

       The range U00010000 - U0010FFFF is coded as 2-character sequences
       using the codes (D800-DBFF),(DC00-DFFF), which are both illegal
       when used as single chars, from above.

       Python won't let you define \U character ranges, so you can't
       just say '\U00010000-\U0010FFFF'. However, you can take advantage
       of the fact that (D800-DBFF) and (DC00-DFFF) are illegal, unless
       part of a 2-character sequence, to match for the \U characters.
    """

    # First, add a group for all the basic illegal areas above
    re_xml_illegal = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])'

    re_xml_illegal += u"|"

    # Next, we know that (uD800-uDBFF) must ALWAYS be followed by (uDC00-uDFFF),
    # and (uDC00-uDFFF) must ALWAYS be preceded by (uD800-uDBFF), so this
    # is how we check for the U00010000-U0010FFFF range. There are also special
    # case checks for start & end of string cases.

    # I've defined this oddly due to the bug mentioned at the top of this file
    re_xml_illegal += u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \
                      (unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
                       unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff),
                       unichr(0xd800), unichr(0xdbff), unichr(0xdc00), unichr(0xdfff))

    return re_xml_illegal

def make_illegal_xml_regex():
    return re.compile(raw_illegal_xml_regex())

c_re_xml_illegal = make_illegal_xml_regex()

def is_legal_xml(uval):
    """
    Given a Unicode object, figure out if it is legal
    to place it in an XML file.
    """
    return (c_re_xml_illegal.search(uval) == None)

def make_xml_string_legal(instr):
    return c_re_xml_illegal.sub('', instr)

def is_legal_xml_char(uchar):
    """
    Check if a single unicode char is XML-legal.
    (This is faster that running the full 'is_legal_xml()' regexp
    when you need to go character-at-a-time. For string-at-a-time
    of course you want to use is_legal_xml().)

    USAGE NOTE:
       If you want to use this in a 'for' loop,
       make sure use usplit(), e.g.:

       for c in usplit( uval ):
          if is_legal_xml_char(c):
                 ...

       Otherwise, the first char of a legal 2-character
       sequence will be incorrectly tagged as illegal, on
       Pythons where \U is stored as 2-chars.
    """

    # due to inconsistencies in how \U is handled (based on
    # how Python was compiled) it is shorter to test for
    # illegal chars than legal ones, and invert the result.
    #
    # (as one example: (u'\ud900' > u'\U00100000') can be True,
    # depending on how Python was compiled. Testing for illegal chars
    # lets us stick with the single char sequences (all 2-char
    # sequences are legal for XML).

    if len(uchar) == 1:
        return not \
               (
               (uchar >= u'\u0000' and uchar <= u'\u0008') or \
               (uchar >= u'\u000b' and uchar <= u'\u000c') or \
               (uchar >= u'\u000e' and uchar <= u'\u001f') or \
               # always illegal as single chars
               (uchar >= unichr(0xd800) and uchar <= unichr(0xdfff)) or \
               (uchar >= u'\ufffe' and uchar <= u'\uffff')
               )
    elif len(uchar) == 2:
        # all 2-char codings are legal in XML
        # (this looks weird, but remember that even after calling
        # usplit(), \U00010000 is STILL len() of 2, usplit() just
        # made it a single listitem
        return True

    else:
        raise Exception("Must pass a single character to is_legal_xml_char")

