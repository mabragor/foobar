# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _
from ui_dialog import UiDlgTemplate

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class ShowVisitors(UiDlgTemplate):

    ui_file = 'uis/dlg_event_visitors.ui'
    title = _('Registered visitors')
    event_id = None

    def __init__(self, parent=None, params=dict()):
        UiDlgTemplate.__init__(self, parent, params)

    def setupUi(self):
        UiDlgTemplate.setupUi(self)

        self.connect(self.buttonManual, SIGNAL('clicked()'), self.registerManually)
        self.connect(self.buttonClose, SIGNAL('clicked()'), self, SLOT('reject()'))


    def initData(self, event_id):
        self.event_id = event_id
        self.http.request('/manager/get_visitors/', {'event_id': event_id})
        default_response = None
        response = self.http.parse(default_response)
        visitor_list = response['visitor_list']
        for last_name, first_name, rfid_code, reg_datetime in visitor_list:
            lastRow = self.tableVisitors.rowCount()
            self.tableVisitors.insertRow(lastRow)
            self.tableVisitors.setItem(lastRow, 0, QTableWidgetItem(last_name))
            self.tableVisitors.setItem(lastRow, 1, QTableWidgetItem(first_name))
            self.tableVisitors.setItem(lastRow, 2, QTableWidgetItem(rfid_code))
            self.tableVisitors.setItem(lastRow, 3, QTableWidgetItem(reg_datetime))

    def registerManually(self):
        rfid_id, ok = QInputDialog.getText(self, _('Register manually'),
                                           _('Enter a client\'s RFID code.'))
        if ok:
            if not rfid_id.isEmpty():
                params = {'rfid_code': rfid_id,
                          'event_id': self.event_id}
                self.http.request('/manager/register_visit/', params)
                default_response = None
                response = self.http.parse(default_response)
                if response:
                    self.initData(self.event_id)
            else:
                QMessageBox.warning(self, _('Register manually'),
                                    _('You\'ve entered empty string.'))
