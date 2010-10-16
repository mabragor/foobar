# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, userRoles
from ui_dialog import UiDlgTemplate
from http import Http

from PyQt4.QtGui import *
from PyQt4.QtCore import *

GET_ID_ROLE = userRoles['getObjectID']

class Searching(UiDlgTemplate):

    ui_file = 'uis/dlg_searching.ui'
    dialog = None
    title = None
    mode = None

    def __init__(self, parent, params=dict()):
        self.mode = params.get('mode', 'client')
        if self.mode == 'client':
            self.title = _('Search client')
        else:
            self.title = _('Search renter')
        UiDlgTemplate.__init__(self, parent, params)

    def setupUi(self):
        UiDlgTemplate.setupUi(self)

        self.tableUsers.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.connect(self.dialog.buttonSearch, SIGNAL('clicked()'), self.searchFor)
        self.connect(self.dialog.buttonShow, SIGNAL('clicked()'), self.applyDialog)
        self.connect(self.dialog.buttonClose,  SIGNAL('clicked()'), self, SLOT('reject()'))

    def setCallback(self, callback):
        self.callback = callback

    def searchFor(self):
        name = self.editSearch.text().toUtf8()
        params = {'name': name, 'mode': self.mode}
        self.http.request('/manager/get_users_info_by_name/', params)
        default_response = None
        response = self.http.parse(default_response)
        if response and 'users' in response:
            user_list = response['users']
            self.showList(user_list)

    def showList(self, user_list):
        self.user_list = user_list
        while self.tableUsers.rowCount() > 0:
            self.tableUsers.removeRow(0)

        for user in user_list:
            lastRow = self.tableUsers.rowCount()
            self.tableUsers.insertRow(lastRow)
            name = QTableWidgetItem(user['last_name']) # data may assign on cells only, use first one
            name.setData(GET_ID_ROLE, int(user['id']))
            self.dialog.tableUsers.setItem(lastRow, 0, name)
            self.tableUsers.setItem(lastRow, 0, QTableWidgetItem(user['last_name']))
            self.tableUsers.setItem(lastRow, 1, QTableWidgetItem(user['first_name']))
            self.tableUsers.setItem(lastRow, 2, QTableWidgetItem(user['email']))

        if len(user_list) > 0:
            self.tableUsers.selectRow(0)
            self.buttonFind.setDisabled(False)
            self.buttonShow.setFocus(Qt.OtherFocusReason)
        else:
            self.buttonShow.setDisabled(True)
            self.buttonFind.setFocus(Qt.OtherFocusReason)

    def applyDialog(self):
        index = self.tableUsers.currentIndex()
        user_id = self.user_list[index.row()]['id']
        self.callback(user_id)
        self.accept()
