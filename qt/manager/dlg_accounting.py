# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _
from settings import MODEL_PROPERTIES
from http import Http

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgAccounting(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        labels = QStringList([_('Resource'), _('Count'), _('Action')])

        self.accounts = QTableWidget(0, 3)
        self.accounts.setHorizontalHeaderLabels(labels)
        self.accounts.setSelectionMode(QAbstractItemView.SingleSelection)

        resultLayout = QVBoxLayout()
        resultLayout.addWidget(self.accounts)

        groupList = QGroupBox(_('Resources'))
        groupList.setLayout(resultLayout)

        buttonClose = QPushButton(_('Close'))

        self.connect(buttonClose, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonClose)

        self.mainLayout = QVBoxLayout()
        self.mainLayout.addWidget(groupList)
        self.mainLayout.addLayout(buttonLayout)

        self.setLayout(self.mainLayout)

        self.setWindowTitle(_('Accounting'))

        self.initData()

    def setCallback(self, callback):
        self.callback = callback

    def initData(self):
        ajax = HttpAjax(self, '/manager/get_accounting/', {}, self.parent.session_id)
        response = ajax.parse_json()
        if response is None:
            return

        while self.accounts.rowCount() > 0:
            self.accounts.removeRow(0)

        for item in response['accounting_list']:
            lastRow = self.accounts.rowCount()
            self.accounts.insertRow(lastRow)
            self.accounts.setItem(lastRow, 0, QTableWidgetItem(item['type']))
            self.accounts.setItem(lastRow, 1, QTableWidgetItem(str(item['count'])))

            def clicked():
                id = lambda: item['id']
                self.addResource(id())

            button = QPushButton(_('Add'))
            self.connect(button, SIGNAL('clicked()'), clicked)
            self.accounts.setCellWidget(lastRow, 2, button)

    def addResource(self, id):
        def callback(count, price):
            params = {'id': id, 'count': count, 'price': price}
            ajax = HttpAjax(self, '/manager/add_resource/', params, self.parent.session_id)
            response = ajax.parse_json()
            if response is not None:
                self.initData()

        dialog = DlgResource(self)
	dialog.setModal(True)
        dialog.setCallback(callback)
	dialog.exec_()

class DlgResource(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        self.count = QLineEdit()
        self.price = QLineEdit()

        layoutGrid = QGridLayout()
        layoutGrid.setColumnStretch(1, 1)
        layoutGrid.setColumnMinimumWidth(1, 250)

        layoutGrid.addWidget(QLabel(_('Count')), 0, 0)
        layoutGrid.addWidget(self.count, 0, 1)
        layoutGrid.addWidget(QLabel(_('Price')), 1, 0)
        layoutGrid.addWidget(self.price, 1, 1)

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
        layout.addLayout(layoutGrid)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.setWindowTitle(_('Add resource'))

    def setCallback(self, callback):
        self.callback = callback

    def applyDialog(self):
        try:
            count = int( self.count.text() )
            price = float( self.price.text() )
        except:
            QMessageBox.warning(self, _('Warning'), _('Improper values.'))
            return
        self.callback(count, price)
        self.accept()

