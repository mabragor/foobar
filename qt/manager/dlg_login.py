# -*- coding: utf-8 -*-
# (c) 2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, DEBUG
from http import Http

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgLogin(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.callback = None
        self.setMinimumWidth(300)

        self.editLogin = QLineEdit()
        labelLogin = QLabel(_('Login'))
        labelLogin.setBuddy(self.editLogin)

        self.editPassword = QLineEdit()
        self.editPassword.setEchoMode(QLineEdit.Password)
        labelPassword = QLabel(_('Password'))
        labelPassword.setBuddy(self.editPassword)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelLogin, 0, 0)
        groupLayout.addWidget(self.editLogin, 0, 1)
        groupLayout.addWidget(labelPassword, 1, 0)
        groupLayout.addWidget(self.editPassword, 1, 1)

        self.buttonOk = QPushButton(_('Ok'))
        buttonCancel = QPushButton(_('Cancel'))

        self.connect(self.buttonOk, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(buttonCancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonOk)
        buttonLayout.addWidget(buttonCancel)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(groupLayout)
        self.mainLayout.addLayout(buttonLayout)

        self.setLayout(self.mainLayout)
        self.setWindowTitle(_('Authentication'))

    def setCallback(self, callback):
        self.callback = callback

    def applyDialog(self):
        login = self.editLogin.text()
        password = self.editPassword.text()
        if self.callback:
            self.callback(login, password)
            self.accept()
        else:
            if DEBUG:
                print '[DlgLogin::applyDialog]: Check callback!'
            self.reject()
