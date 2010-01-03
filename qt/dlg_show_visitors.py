# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from http_ajax import HttpAjax

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgShowVisitors(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        labels = QStringList([_('Last name'),
                              _('First name'),
                              _('Type')])

        self.visitors = QTableWidget(0, 3)
        self.visitors.setHorizontalHeaderLabels(labels)
        self.visitors.setSelectionMode(QAbstractItemView.NoSelection)

        visitLayout = QVBoxLayout()
        visitLayout.addWidget(self.visitors)
        group = QGroupBox(_('Visitors'))
        group.setLayout(visitLayout)

        buttonClose = QPushButton(_('Close'))
        self.connect(buttonClose, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonClose)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(group)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(_('Registered visitors'))

    def initData(self, event_id):
        ajax = HttpAjax(self, '/manager/get_visitors/',
                        {'event_id': event_id})
        response = ajax.parse_json()
        if 'code' in response:
            if response['code'] == 200:
                visitor_list = response['visitor_list']
                for last_name, first_name, rfid_code in visitor_list:
                    lastRow = self.visitors.rowCount()
                    self.visitors.insertRow(lastRow)
                    self.visitors.setItem(lastRow, 0, QTableWidgetItem(last_name))
                    self.visitors.setItem(lastRow, 1, QTableWidgetItem(first_name))
                    self.visitors.setItem(lastRow, 2, QTableWidgetItem(rfid_code))
        else:
            print 'Check response format!'
        return
