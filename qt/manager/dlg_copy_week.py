# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgCopyWeek(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(400)

        self.calendar = QCalendarWidget()
        self.calendar.setFirstDayOfWeek(Qt.Monday)
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.showToday()

        buttonApplyDialog = QPushButton(_('Apply'))
        buttonCancelDialog = QPushButton(_('Cancel'))

        self.connect(buttonApplyDialog, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(buttonCancelDialog, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonApplyDialog)
        buttonLayout.addWidget(buttonCancelDialog)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.setWindowTitle(_('Choose a week to copy to'))

    def setCallback(self, callback):
        self.callback = callback

    def applyDialog(self):
        """ Применить настройки. """
        selected = self.calendar.selectedDate()
        if QMessageBox.Ok == self.callback(selected.toPyDate()):
            return
        self.accept()

