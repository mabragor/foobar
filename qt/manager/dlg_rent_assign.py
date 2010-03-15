# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgRentAssign(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        self.rentTitle = QLineEdit()
        labelTitle = QLabel(_('Title'))
        labelTitle.setBuddy(self.rentTitle)

        self.rentDesc = QTextEdit()
        self.rentDesc.setAcceptRichText(False)
        self.rentDesc.setTabChangesFocus(True)
        labelDesc = QLabel(_('Description'))
        labelDesc.setBuddy(self.rentDesc)

        self.rentStatus = QComboBox()
        for i in [_('Reserved'), _('Paid partially'), _('Paid')]:
            self.rentStatus.addItem(i)
        labelStatus = QLabel(_('Status'))
        labelStatus.setBuddy(self.rentStatus)

        self.rentPaid = QLineEdit()
        self.rentPaid.setText('0')
        labelPaid = QLabel(_('Paid'))
        labelPaid.setBuddy(self.rentPaid)

        self.rentBegin = QDateEdit()
        current = QDate.currentDate()
        self.rentBegin.setDate(current)
        self.rentBegin.setMinimumDate(current)
        labelBegin = QLabel(_('Begin'))
        labelBegin.setBuddy(self.rentBegin)

        self.rentEnd = QDateEdit()
        current = QDate.currentDate()
        self.rentEnd.setDate(current)
        self.rentEnd.setMinimumDate(current)
        labelEnd = QLabel(_('End'))
        labelEnd.setBuddy(self.rentEnd)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelTitle, 0, 0)
        groupLayout.addWidget(self.rentTitle, 0, 1)
        groupLayout.addWidget(labelDesc, 1, 0)
        groupLayout.addWidget(self.rentDesc, 1, 1)
        groupLayout.addWidget(labelStatus, 2, 0)
        groupLayout.addWidget(self.rentStatus, 2, 1)
        groupLayout.addWidget(labelPaid, 3, 0)
        groupLayout.addWidget(self.rentPaid, 3, 1)
        groupLayout.addWidget(labelBegin, 4, 0)
        groupLayout.addWidget(self.rentBegin, 4, 1)
        groupLayout.addWidget(labelEnd, 5, 0)
        groupLayout.addWidget(self.rentEnd, 5, 1)

        self.buttonAssign = QPushButton(_('Assign'))
        self.buttonCancel = QPushButton(_('Cancel'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonAssign)
        buttonLayout.addWidget(self.buttonCancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(groupLayout)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(_('Rent registration'))
        self.setSignals()

    def setCallback(self, callback):
        self.callback = callback

    def setSignals(self):
        self.connect(self.buttonAssign, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(self.buttonCancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def applyDialog(self):
        title = self.rentTitle.text()
        desc = self.rentDesc.toPlainText()
        status = self.rentStatus.currentIndex()
        paid = float( self.rentPaid.text() )
        begin = self.rentBegin.date().toPyDate()
        end = self.rentEnd.date().toPyDate()
        self.callback(title, desc, status, paid, begin, end)
        self.accept()
