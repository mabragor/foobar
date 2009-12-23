# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class SortClientCourses(QSortFilterProxyModel):

    """ Proxy class to change representation of client's courses
    information. """

    def __init__(self, parent=None):
        QSortFilterProxyModel.__init__(self, parent)
