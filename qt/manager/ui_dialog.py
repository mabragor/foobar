# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, DEBUG

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4 import uic

class UiDlgTemplate(QDialog):
    """ This is a common template for all UI dialogs. """

    parent = None
    ui_file = None
    title = None
    http = None

    def __init__(self, parent=None, params=dict()):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.http = params.get('http', None)
        uic.loadUi(self.ui_file, self)
        self.setupUi()

    def setupUi(self):
        if self.title:
            self.setWindowTitle(self.title)
