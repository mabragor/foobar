# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from http_ajax import HttpAjax

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgSearchByName(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.setMinimumWidth(500)

        labelField = QLabel(self.tr('Search'))
        self.editField = QLineEdit()
        labelField.setBuddy(self.editField)

        fieldLayout = QHBoxLayout()
        fieldLayout.addWidget(labelField)
        fieldLayout.addWidget(self.editField)

        buttonFind = QPushButton(self.tr('Find'))
        buttonCancel = QPushButton(self.tr('Cancel'))

        self.connect(buttonFind, SIGNAL('clicked()'),
                     self.searchFor)
        self.connect(buttonCancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonFind)
        buttonLayout.addWidget(buttonCancel)

        labels = QStringList([self.tr('Last name'),
                              self.tr('First name'),
                              self.tr('RFID code')])

        self.userTable = QTableWidget(0, 3)
        self.userTable.setHorizontalHeaderLabels(labels)
        self.userTable.hideColumn(2)

        self.userTable.setSelectionMode(QAbstractItemView.SingleSelection)

        resultLayout = QVBoxLayout()
        resultLayout.addWidget(self.userTable)

        groupList = QGroupBox(self.tr('Results'))
        groupList.setObjectName(QString('SearchResults'))
        groupList.setLayout(resultLayout)

        self.buttonShow = QPushButton(self.tr('Show'))

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
        self.setWindowTitle(self.tr('Search client by name'))

    def setCallback(self, callback):
        self.callback = callback

    def searchFor(self):
        name = self.editField.text()
        ajax = HttpAjax(self, '/manager/get_users_info_by_name/',
                        {'name': name,})
        response = ajax.parse_json()
        if 'code' in response:
            if response['code'] == 200:
                user_list = response['user_list']
                self.showList(user_list)
            print 'AJAX result: [%(code)s] %(desc)s' % response
        else:
            print 'Check response format!'


    def showList(self, user_list):
        self.user_list = user_list
        while self.userTable.rowCount() > 0:
            self.userTable.removeRow(0)

        for last_name, first_name, rfid_code in user_list:
            lastRow = self.userTable.rowCount()
            self.userTable.insertRow(lastRow)
            self.userTable.setItem(lastRow, 0, QTableWidgetItem(last_name))
            self.userTable.setItem(lastRow, 1, QTableWidgetItem(first_name))
            self.userTable.setItem(lastRow, 2, QTableWidgetItem(rfid_code))

        if len(user_list) > 0:
            self.userTable.selectRow(0)
            self.buttonShow.setDisabled(False)
            self.buttonShow.setFocus(Qt.OtherFocusReason)
        else:
            self.buttonShow.setDisabled(True)
            self.buttonFind.setFocus(Qt.OtherFocusReason)

    def applyDialog(self):
        index = self.userTable.currentIndex()
        rfid_code = self.user_list[index.row()][2]
        self.callback(rfid_code)
        self.accept()
