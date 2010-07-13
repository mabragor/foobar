# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _
from http import Http

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgSearchByName(QDialog):

    def __init__(self, mode='client', parent=None):
        QDialog.__init__(self, parent)

        self.setMinimumWidth(500)
        self.parent = parent
        self.mode = mode

        labelField = QLabel(_('Search'))
        self.editField = QLineEdit()
        labelField.setBuddy(self.editField)

        fieldLayout = QHBoxLayout()
        fieldLayout.addWidget(labelField)
        fieldLayout.addWidget(self.editField)

        self.buttonFind = QPushButton(_('Find'))
        buttonCancel = QPushButton(_('Cancel'))

        self.connect(self.buttonFind, SIGNAL('clicked()'),
                     self.searchFor)
        self.connect(buttonCancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonFind)
        buttonLayout.addWidget(buttonCancel)

        labels = QStringList([_('Last name'),
                              _('First name'),
                              _('E-mail')])

        self.userTable = QTableWidget(0, 3)
        self.userTable.setHorizontalHeaderLabels(labels)
        #self.userTable.hideColumn(2)

        self.userTable.setSelectionMode(QAbstractItemView.SingleSelection)

        resultLayout = QVBoxLayout()
        resultLayout.addWidget(self.userTable)

        groupList = QGroupBox(_('Results'))
        groupList.setObjectName(QString('SearchResults'))
        groupList.setLayout(resultLayout)

        self.buttonShow = QPushButton(_('Show'))

        self.connect(self.buttonShow, SIGNAL('clicked()'),
                     self.applyDialog)

        button2Layout = QHBoxLayout()
        button2Layout.addStretch(1)
        button2Layout.addWidget(self.buttonShow)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addLayout(fieldLayout)
        self.mainLayout.addLayout(buttonLayout)
        self.mainLayout.addWidget(groupList)
        self.mainLayout.addLayout(button2Layout)

        self.setLayout(self.mainLayout)

        if self.mode == 'client':
            self.setWindowTitle(_('Search client by name'))
        else:
            self.setWindowTitle(_('Search renter by name'))

    def setCallback(self, callback):
        self.callback = callback

    def searchFor(self):
        name = self.editField.text().toUtf8()
        params = {'name': name, 'mode': self.mode}
        ajax = HttpAjax(self, '/manager/get_users_info_by_name/', params, self.parent.session_id)
        response = ajax.parse_json()
        if response:
            user_list = response['users']
            self.showList(user_list)

    def showList(self, user_list):
        self.user_list = user_list
        while self.userTable.rowCount() > 0:
            self.userTable.removeRow(0)

        for user in user_list:
            lastRow = self.userTable.rowCount()
            self.userTable.insertRow(lastRow)
            self.userTable.setItem(lastRow, 0, QTableWidgetItem(user['last_name']))
            self.userTable.setItem(lastRow, 1, QTableWidgetItem(user['first_name']))
            self.userTable.setItem(lastRow, 2, QTableWidgetItem(user['email']))

        if len(user_list) > 0:
            self.userTable.selectRow(0)
            self.buttonFind.setDisabled(False)
            self.buttonShow.setFocus(Qt.OtherFocusReason)
        else:
            self.buttonShow.setDisabled(True)
            self.buttonFind.setFocus(Qt.OtherFocusReason)

    def applyDialog(self):
        index = self.userTable.currentIndex()
        user_id = self.user_list[index.row()]['id']
        self.callback(user_id)
        self.accept()
