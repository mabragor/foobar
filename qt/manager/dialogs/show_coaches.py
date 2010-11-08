# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, userRoles
from ui_dialog import UiDlgTemplate

from PyQt4.QtGui import *
from PyQt4.QtCore import *

GET_ID_ROLE = userRoles['getObjectID']

class ShowCoaches(UiDlgTemplate):

    ui_file = 'uis/dlg_event_coaches.ui'
    title = _('Registered visitors')
    callback = None
    event_id = None

    def __init__(self, parent=None, params=dict()):
        UiDlgTemplate.__init__(self, parent, params)

    def setupUi(self):
        UiDlgTemplate.setupUi(self)

        self.tableCoaches.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.connect(self.buttonApply, SIGNAL('clicked()'), self.apply)
        self.connect(self.buttonClose,  SIGNAL('clicked()'), self, SLOT('reject()'))

    def setCallback(self, callback):
        self.callback = callback

    def initData(self, schedule):
        self.event_id = schedule.get('id', None)
        for coach in self.parent.parent.static['coaches']:
            lastRow = self.tableCoaches.rowCount()
            self.tableCoaches.insertRow(lastRow)
            name = QTableWidgetItem(coach['last_name']) # data may assign on cells only, use first one
            name.setData(GET_ID_ROLE, int(coach['id']))
            self.tableCoaches.setItem(lastRow, 0, name)
            self.tableCoaches.setItem(lastRow, 1, QTableWidgetItem(coach['first_name']))
            self.tableCoaches.setItem(lastRow, 2, QTableWidgetItem('--'))
            self.tableCoaches.setItem(lastRow, 3, QTableWidgetItem(coach['reg_datetime']))

    def apply(self):
        coach_id_list = []
        selected = self.tableCoaches.selectionModel().selectedRows()
        if len(selected) > 3:
            message = _('Select no more three coaches.')
        else:
            for index in selected:
                model = index.model()
                coach_id, ok = model.data(index, GET_ID_ROLE).toInt()
                if ok:
                    coach_id_list.append(coach_id)

            if len(coach_id_list) > 0:
                params = {'event_id': self.event_id, 'coach_id_list': ','.join([str(i) for i in coach_id_list])}
                if not self.http.request('/manager/register_change/', params):
                    QMessageBox.critical(self, _('Register change'), _('Unable to register: %s') % self.http.error_msg)
                    return
                default_response = None
                response = self.http.parse(default_response)
                if response:
                    self.accept()
                    self.callback(coach_id_list)
                    return
                else:
                    message = _('Unable to exchange.')
            else:
                message = _('No selection, skip...')
        QMessageBox.warning(self, _('Coaches exchange'), message)
