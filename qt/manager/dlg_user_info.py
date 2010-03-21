# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, DEBUG
from model_sorting import SortClientTeams
from team_list import TeamListModel, TeamListDelegate, TeamList
from http_ajax import HttpAjax
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_team_assign import DlgTeamAssign
from dlg_rent_assign import DlgRentAssign

from datetime import datetime

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgClientInfo(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.user_id = u'0'
        self.setMinimumWidth(800)

        self.editLastName = QLineEdit()
        self.editFirstName = QLineEdit()
        self.editEmail = QLineEdit()
        self.editPhone = QLineEdit()
        self.editDiscount = QLineEdit()
        self.dateBirth = QDateEdit()
        self.editRFID = QLineEdit()
        self.editRFID.setReadOnly(True)

        layoutUser = QGridLayout()
        layoutUser.setColumnStretch(1, 1)
        layoutUser.setColumnMinimumWidth(1, 250)

        layoutUser.addWidget(QLabel(_('Last name')), 0, 0)
        layoutUser.addWidget(self.editLastName, 0, 1)
        layoutUser.addWidget(QLabel(_('First name')), 1, 0)
        layoutUser.addWidget(self.editFirstName, 1, 1)
        layoutUser.addWidget(QLabel(_('E-mail')), 2, 0)
        layoutUser.addWidget(self.editEmail, 2, 1)
        layoutUser.addWidget(QLabel(_('Phone')), 3, 0)
        layoutUser.addWidget(self.editPhone, 3, 1)
        layoutUser.addWidget(QLabel(_('Discount')), 4, 0)
        layoutUser.addWidget(self.editDiscount, 4, 1)
        layoutUser.addWidget(QLabel(_('Date of birth')), 5, 0)
        layoutUser.addWidget(self.dateBirth, 5, 1)
        layoutUser.addWidget( QLabel(_('RFID')), 6, 0)
        layoutUser.addWidget(self.editRFID, 6, 1)

        groupUser = QGroupBox(_('Base data'))
        groupUser.setLayout(layoutUser)

        # купленные курсы
        self.cardinfo = TeamList(self)

        cardLayout = QVBoxLayout()
        cardLayout.addWidget(self.cardinfo)

        groupCard = QGroupBox(_('Teams\' history'))
        groupCard.setLayout(cardLayout)

        buttonAssignRFID = QPushButton(_('Assign RFID'))
        buttonAssignTeam = QPushButton(_('Assign team'))
        buttonApplyDialog = QPushButton(_('Apply'))
        buttonCancelDialog = QPushButton(_('Cancel'))

        self.connect(buttonAssignRFID, SIGNAL('clicked()'),
                     self.assignRFID)
        self.connect(buttonAssignTeam, SIGNAL('clicked()'),
                     self.showAssignTeamDlg)
        self.connect(buttonApplyDialog, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(buttonCancelDialog, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(buttonAssignRFID)
        buttonLayout.addWidget(buttonAssignTeam)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonApplyDialog)
        buttonLayout.addWidget(buttonCancelDialog)

        layout = QVBoxLayout()
        layout.addWidget(groupUser)
        layout.addWidget(groupCard)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.setWindowTitle(_('Client\'s information'))

        # source model
        self.teamsModel = TeamListModel(self)
        # proxy model
        #self.proxyModel = SortClientTeams(self)
        #self.proxyModel.setSourceModel(self.teamsModel)
        # use proxy model to change data representation
        self.cardinfo.setModel(self.teamsModel)
        self.delegate = TeamListDelegate()
        #self.cardinfo.setItemDelegate(self.delegate)

    def initData(self, data):
        self.user_id = data['id']
        self.editFirstName.setText(data.get('first_name', ''))
        self.editLastName.setText(data.get('last_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editPhone.setText(data.get('phone', ''))
        self.editDiscount.setText(str(data.get('discount', 0)))

        def str2date(value):
            import time
            return datetime(*time.strptime(value, '%Y-%m-%d')[:3])

        self.dateBirth.setDate(str2date(data['birthday']))
        self.editRFID.setText(data.get('rfid_code', ''))

        teams = data.get('team_list', [])
        self.teamsModel.initData(teams)

    def cancelTeam(self):
        row = self.cardinfo.currentRow()
        if DEBUG:
            print 'cancel team'
            print row
        self.cardinfo.removeRow(row)

    def assignRFID(self):
        def callback(rfid):
            self.rfid_id = rfid

        self.callback = callback
        self.dialog = DlgWaitingRFID(self)
        self.dialog.setModal(True)
        dlgStatus = self.dialog.exec_()

        """ Назначить карту пользователю. """
        if QDialog.Accepted == dlgStatus:
            self.editRFID.setText(self.rfid_id)

    def showAssignTeamDlg(self):
        dialog = DlgTeamAssign(self)
        dialog.setCallback(self.assignTeam)
        dialog.setModel(self.parent.tree)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

    def assignTeam(self, card_type, bgn_date, duration_index, data):
        # duration matters for club card only
        lastRow = self.teamsModel.rowCount(QModelIndex())
        if self.teamsModel.insertRows(lastRow, 1, QModelIndex()):
            index = self.teamsModel.index(0, 0)
            self.teamsModel.setRow(index, data, Qt.EditRole, card_type, bgn_date, duration_index)

        if DEBUG:
            print 'DlgUserInfo::assignTeam DUMP:'
            for item in self.teamsModel.storage:
                print '\t',
                for col in item:
                    print col,
                print

    def applyDialog(self):
        """ Применить настройки. """
        team_changes = self.teamsModel.get_changes_and_clean()
        self.saveSettings(team_changes)
        self.accept()

    def saveSettings(self, team_changes):
        assigned, cancelled, changed = team_changes
        params = {
            'user_id': self.user_id,
            'first_name': self.editFirstName.text().toUtf8(),
            'last_name': self.editLastName.text().toUtf8(),
            'email': self.editEmail.text().toUtf8(),
            'phone': self.editPhone.text().toUtf8(),
            'discount': self.editDiscount.text().toUtf8(),
            'birthday': self.dateBirth.date().toPyDate(),
            'rfid_code': self.editRFID.text().toUtf8(),
            'team_assigned': assigned,
            'team_cancelled': cancelled,
            'team_changed': changed
            }
        #print 'DlgClientInfo::saveSettings', params
        ajax = HttpAjax(self, '/manager/set_user_info/', params, self.parent.session_id)
        response = ajax.parse_json()
        self.accept()

class DlgRenterInfo(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.user_id = u'0'
        self.setMinimumWidth(800)

        self.assigned = []

        self.editFirstName = QLineEdit()
        self.editLastName = QLineEdit()
        self.editEmail = QLineEdit()
        self.editPhoneMobile = QLineEdit()
        self.editPhoneWork = QLineEdit()
        self.editPhoneHome = QLineEdit()

        layoutUser = QGridLayout()
        layoutUser.setColumnStretch(1, 1)
        layoutUser.setColumnMinimumWidth(1, 250)

        layoutUser.addWidget(QLabel(_('Last name')), 0, 0)
        layoutUser.addWidget(self.editLastName, 0, 1)
        layoutUser.addWidget(QLabel(_('First name')), 1, 0)
        layoutUser.addWidget(self.editFirstName, 1, 1)
        layoutUser.addWidget(QLabel(_('E-mail')), 2, 0)
        layoutUser.addWidget(self.editEmail, 2, 1)
        layoutUser.addWidget(QLabel(_('Mobile phone')), 3, 0)
        layoutUser.addWidget(self.editPhoneMobile, 3, 1)
        layoutUser.addWidget(QLabel(_('Work phone')), 4, 0)
        layoutUser.addWidget(self.editPhoneWork, 4, 1)
        layoutUser.addWidget(QLabel(_('Home phone')), 5, 0)
        layoutUser.addWidget(self.editPhoneHome, 5, 1)

        groupUser = QGroupBox(_('Base data'))
        groupUser.setLayout(layoutUser)

        labels = QStringList([_('Title'), _('Status'), _('Paid'),
                              _('Begin'), _('End'), _('Registered')])

        self.rentinfo = QTableWidget(0, 6)
        self.rentinfo.setHorizontalHeaderLabels(labels)
        self.rentinfo.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        #self.rentinfo.hideColumn(2)

        rentLayout = QVBoxLayout()
        rentLayout.addWidget(self.rentinfo)

        groupRent = QGroupBox(_('Rents\' history'))
        groupRent.setLayout(rentLayout)

        buttonAssignRent = QPushButton(_('Assign rent'))
        buttonApplyDialog = QPushButton(_('Apply'))
        buttonCancelDialog = QPushButton(_('Cancel'))

        self.connect(buttonAssignRent, SIGNAL('clicked()'),
                     self.showAssignRentDlg)
        self.connect(buttonApplyDialog, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(buttonCancelDialog, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(buttonAssignRent)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonApplyDialog)
        buttonLayout.addWidget(buttonCancelDialog)

        layout = QVBoxLayout()
        layout.addWidget(groupUser)
        layout.addWidget(groupRent)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.setWindowTitle(_('Renter\'s information'))

        #self.editLastName.setProperty('errorHighlight', QVariant(True))

    def initData(self, data):
        self.user_id = data['id']
        self.editLastName.setText(data.get('last_name', ''))
        self.editFirstName.setText(data.get('first_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editPhoneMobile.setText(data.get('phone_mobile', ''))
        self.editPhoneWork.setText(data.get('phone_work', ''))
        self.editPhoneHome.setText(data.get('phone_home', ''))

        self.fillRentList(data.get('rent_list', []))

    def fillRentList(self, rent_list):
        for rent in rent_list:
            self.addOneRow(rent)

    def addOneRow(self, row):
        status = [_('Reserved'), _('Paid partially'), _('Paid')][int( row['status'] )]
        lastRow = self.rentinfo.rowCount()
        self.rentinfo.insertRow(lastRow)
        self.rentinfo.setItem(lastRow, 0, QTableWidgetItem(row['title']))
        self.rentinfo.setItem(lastRow, 1, QTableWidgetItem(status))
        self.rentinfo.setItem(lastRow, 2, QTableWidgetItem(str(row['paid'])))
        self.rentinfo.setItem(lastRow, 3, QTableWidgetItem(str(row['begin_date'])))
        self.rentinfo.setItem(lastRow, 4, QTableWidgetItem(str(row['end_date'])))
        self.rentinfo.setItem(lastRow, 5, QTableWidgetItem(str(row['reg_date'])))

    def showAssignRentDlg(self):
        dialog = DlgRentAssign(self)
        dialog.setCallback(self.assignRent)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

    def assignRent(self, title, desc, status, paid, begin, end):
        params = {
            'renter_id': self.user_id,
            'title': title,
            'desc': desc,
            'status': status,
            'paid': paid,
            'begin_date': begin,
            'end_date': end,
            'reg_date': datetime.now()
            }
        #print 'DlgRenterInfo::assignRent\n', params, '\n'
        self.assigned.append(params)
        self.addOneRow(params)

    def applyDialog(self):
        errorHighlight = []
        phones = 0
        for title, widget in [(_('Last name'), self.editLastName),
                              (_('First name'), self.editFirstName),
                              (_('E-mail'), self.editEmail)]:
            if 0 == len(widget.text().toUtf8()):
                errorHighlight.append(title)
        for title, widget in [(_('Mobile phone'), self.editPhoneMobile),
                              (_('Work phone'), self.editPhoneWork),
                              (_('Home phone'), self.editPhoneHome)]:
            if 0 < len(widget.text().toUtf8()):
                phones += 1
        if phones == 0:
            errorHighlight.append(_('Phones'))
        if len(errorHighlight) > 0:
            QMessageBox.critical(
                self.parent, _('Dialog error'),
                'Fields %s must be filled.' % ', '.join(errorHighlight))
            return
        params = {
            'user_id': self.user_id,
            'last_name': self.editLastName.text().toUtf8(),
            'first_name': self.editFirstName.text().toUtf8(),
            'email': self.editEmail.text().toUtf8(),
            'phone_mobile': self.editPhoneMobile.text().toUtf8(),
            'phone_work': self.editPhoneWork.text().toUtf8(),
            'phone_home': self.editPhoneHome.text().toUtf8(),
            }
        #print 'DlgRentAssign::applyDialog\n', params, '\n';
        ajax = HttpAjax(self, '/manager/set_renter_info/', params, self.parent.session_id)
        response = ajax.parse_json()
        renter_id = int( response['saved_id'] )

        for rent in self.assigned:
            params = {
                'renter_id'  : renter_id,
                'status'     : rent['status'],
                'title'      : rent['title'].toUtf8(),
                'desc'       : rent['desc'].toUtf8(),
                'begin_date' : rent['begin_date'],
                'end_date'   : rent['end_date'],
                'paid'       : rent['paid'],
                }
            ajax = HttpAjax(self, '/manager/set_rent/', params, self.parent.session_id)
            response = ajax.parse_json()
            rent_id = int( response['saved_id'] )

        self.accept()
