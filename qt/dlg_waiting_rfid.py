#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from rfid import WaitingRFID

class DlgWaitingRFID(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.parent.dialog = self
        self.reader = WaitingRFID(self.parent)
        self.reader.setTerminationEnabled(True)

        self.layout = QVBoxLayout()

        self.label = QLabel(self.tr('Put the RFID label on to the RFID reader, please.'))
        self.layout.addWidget(self.label)

        self.cancel = QPushButton(self.tr('&Cancel'), self)
        self.layout.addWidget(self.cancel)

        self.setLayout(self.layout)
        self.setWindowTitle(self.tr('RFID reader'))

        self.connect(self.cancel, SIGNAL('clicked()'),
                     self.unlink)
        self.connect(self.cancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        self.reader.start()

    def unlink(self):
        """ Посылаем потоку RFID считывателя команду тихо завершиться. """
        self.reader.timeToDie()
