# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, DEBUG, userRoles

import pprint
def dumpobj(title, value):
    print title
    pprint.pprint(value)

def dictlist2dict(dictlist, key_field):
    """ This function converts the list of dictionaries into one
    dictionary using appropriate key field."""
    def _convertor(listitem):
        if type(listitem) is not dict:
            raise ValueError(_('It expexts a dictionary but took %s') % type(key_field))
        if key_field not in listitem:
            raise KeyError(_('Key "%s" does not exists. Check dictionary.') % key_field)

        result.update( {listitem[key_field]: listitem} )
        return True

    result = {}
    map(_convertor, dictlist)
    return result

def dictlist_keyval(dictlist, key_field, value):
    """ This function makes search on the list of dictionaries and
    returns the list of items, which the value of appropriate key
    equals the given value or values."""
    def _search(listitem):
        if type(listitem) is not dict:
            raise ValueError(_('It expexts a dictionary but took %s') % type(key_field))
        if key_field not in listitem:
            raise KeyError(_('Key "%s" does not exists. Check dictionary.') % key_field)
        if type(value) in (list, tuple):
            return listitem[key_field] in value
        else:
            return listitem[key_field] == value

    return filter(_search, dictlist)

