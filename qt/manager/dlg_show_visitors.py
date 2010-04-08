# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _
from http_ajax import HttpAjax

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgShowVisitors(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)
        self.event_id = None

        labels = QStringList([_('Last name'),
                              _('First name'),
                              _('RFID')])

        self.visitors = QTableWidget(0, 3)
        self.visitors.setHorizontalHeaderLabels(labels)
        self.visitors.setSelectionMode(QAbstractItemView.NoSelection)

        visitLayout = QVBoxLayout()
        visitLayout.addWidget(self.visitors)
        group = QGroupBox(_('Visitors'))
        group.setLayout(visitLayout)

        buttonManual = QPushButton( _('Register manually') )
        buttonClose = QPushButton( _('Close') )

        self.connect(buttonManual, SIGNAL('clicked()'),
                     self.registerManually)
        self.connect(buttonClose, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(buttonManual)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonClose)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(group)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle( _('Registered visitors') )

    def initData(self, event_id):
        self.event_id = event_id
        ajax = HttpAjax(self, '/manager/get_visitors/',
                        {'event_id': event_id}, self.parent.parent.session_id)
        response = ajax.parse_json()
        visitor_list = response['visitor_list']
        for last_name, first_name, rfid_code in visitor_list:
            lastRow = self.visitors.rowCount()
            self.visitors.insertRow(lastRow)
            self.visitors.setItem(lastRow, 0, QTableWidgetItem(last_name))
            self.visitors.setItem(lastRow, 1, QTableWidgetItem(first_name))
            self.visitors.setItem(lastRow, 2, QTableWidgetItem(rfid_code))

    def registerManually(self):
        rfid_id, ok = QInputDialog.getText(self, _('Register manually'),
                                           _('Enter a client\'s RFID code.'))
        if ok:
            if not rfid_id.isEmpty():
                params = {'rfid_code': rfid_id,
                          'event_id': self.event_id}
                ajax = HttpAjax(self, '/manager/register_visit/',
                                params, self.parent.parent.session_id)
                response = ajax.parse_json()
                if response:
                    self.initData(self.event_id)
                else:
                    QMessageBox.warning(self, _('Register manually'),
                                        _('You\'ve entered wrong RFID code.'))
            else:
                QMessageBox.warning(self, _('Register manually'),
                                    _('You\'ve entered empty string.'))
