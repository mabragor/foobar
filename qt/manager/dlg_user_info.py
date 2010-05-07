# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, DEBUG
from model_sorting import SortClientTeams
from team_list import TeamListModel, TeamList
from rent_list import RentListModel, RentList
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
        self.client_id = u'0'
        self.setMinimumWidth(800)

        self.editLastName = QLineEdit()
        self.editFirstName = QLineEdit()
        self.editEmail = QLineEdit()
        self.editPhone = QLineEdit()
        self.editDiscount = QLineEdit(); self.editDiscount.setText('0')
        self.dateBirth = QDateEdit()
        self.editRFID = QLineEdit(); self.editRFID.setReadOnly(True)

        self.buttonAssignRFID = QPushButton(_('Assign RFID'))

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
        layoutUser.addWidget(self.buttonAssignRFID, 6, 2)

        groupUser = QGroupBox(_('Base data'))
        groupUser.setLayout(layoutUser)

        self.buttonAssignTeam = QPushButton(_('Assign team'))
        self.buttonApplyDialog = QPushButton(_('Apply'))
        self.buttonCancelDialog = QPushButton(_('Cancel'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonAssignTeam)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonApplyDialog)
        buttonLayout.addWidget(self.buttonCancelDialog)

        # купленные курсы
        self.cardinfo = TeamList(self)

        cardLayout = QVBoxLayout()
        cardLayout.addWidget(self.cardinfo)

        groupCard = QGroupBox(_('Teams\' history'))
        groupCard.setLayout(cardLayout)

        layout = QVBoxLayout()
        layout.addWidget(groupUser)
        layout.addLayout(buttonLayout)
        layout.addWidget(groupCard)

        self.setLayout(layout)
        self.setWindowTitle(_('Client\'s information'))

        self.setRequired()
        self.setSignals()
        self.initData( {} )

    def setRequired(self):
        self.editLastName.setProperty('required', QVariant(True))
        self.editFirstName.setProperty('required', QVariant(True))
        self.editEmail.setProperty('required', QVariant(True))
        self.editPhone.setProperty('required', QVariant(True))
        self.editDiscount.setProperty('required', QVariant(True))
        self.dateBirth.setProperty('required', QVariant(True))
        self.editRFID.setProperty('required', QVariant(True))

    def setSignals(self):
        self.connect(self.buttonAssignRFID, SIGNAL('clicked()'),
                     self.assignRFID)
        self.connect(self.buttonAssignTeam, SIGNAL('clicked()'),
                     self.showAssignTeamDlg)
        self.connect(self.buttonApplyDialog, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(self.buttonCancelDialog, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def initData(self, data):
        self.client_id = data.get('id', '0')
        self.editFirstName.setText(data.get('first_name', ''))
        self.editLastName.setText(data.get('last_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editPhone.setText(data.get('phone', ''))
        self.editDiscount.setText(str(data.get('discount', 0)))

        def str2date(value):
            import time
            return datetime(*time.strptime(value, '%Y-%m-%d')[:3])

        birth_date = data.get('birth_date', None) # it could be none while testing
        self.dateBirth.setDate(birth_date and str2date(birth_date) or \
                               QDate.currentDate())
        self.editRFID.setText(data.get('rfid_code', ''))

        self.prices = data.get('prices', [])

        teams = data.get('team_list', [])
        self.cardinfo.model().initData(teams, self.prices)

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

    def assignTeam(self, data):
        model = self.cardinfo.model()
        lastRow = model.rowCount(QModelIndex())
        if model.insertRows(lastRow, 1, QModelIndex()):
            index = model.index(0, 0)
            model.setRow(index, data, Qt.EditRole)

    def applyDialog(self):
        """ Применить настройки. """
        userinfo, ok = self.checkFields()
        if ok:
            self.saveSettings(userinfo)
            self.accept()
        else:
            QMessageBox.warning(self, _('Warning'),
                                _('Please fill required fields.'))
    def checkFields(self):
        userinfo = {
            'last_name': self.editLastName.text().toUtf8(),
            'first_name': self.editFirstName.text().toUtf8(),
            'phone': self.editPhone.text().toUtf8(),
            'email': self.editEmail.text().toUtf8(),
            'birth_date': self.dateBirth.date().toPyDate(),
            'rfid_code': self.editRFID.text().toUtf8(),
            'discount': self.editDiscount.text().toUtf8(),
            }
        for k,v in userinfo.items():
            if k is not 'birth_date' and len(v) == 0:
                return (userinfo, False)
        return (userinfo, True)

    def saveSettings(self, userinfo):
        params = { 'user_id': self.client_id, }
        params.update(userinfo)

        ajax = HttpAjax(self, '/manager/set_client_info/', params, self.parent.session_id)
        response = ajax.parse_json()

        self.client_id = int( response['saved_id'] )
        model = self.cardinfo.model()
        params = model.get_model_as_formset(self.client_id)
        ajax = HttpAjax(self, '/manager/set_client_card/', params, self.parent.session_id)
        response = ajax.parse_json()

class DlgRenterInfo(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.user_id = u'0'
        self.setMinimumWidth(800)

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

        self.buttonAssignRent = QPushButton(_('Assign rent'))
        self.buttonApplyDialog = QPushButton(_('Apply'))
        self.buttonCancelDialog = QPushButton(_('Cancel'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonAssignRent)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonApplyDialog)
        buttonLayout.addWidget(self.buttonCancelDialog)

        self.rentinfo = RentList(self)
        self.rentInfoModel = RentListModel(self)
        self.rentinfo.setModel(self.rentInfoModel)

        rentLayout = QVBoxLayout()
        rentLayout.addWidget(self.rentinfo)

        groupRent = QGroupBox(_('Rents\' history'))
        groupRent.setLayout(rentLayout)

        layout = QVBoxLayout()
        layout.addWidget(groupUser)
        layout.addLayout(buttonLayout)
        layout.addWidget(groupRent)

        self.setLayout(layout)
        self.setWindowTitle(_('Renter\'s information'))

        self.setSignals()

    def setSignals(self):
        self.connect(self.buttonAssignRent, SIGNAL('clicked()'),
                     self.showAssignRentDlg)
        self.connect(self.buttonApplyDialog, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(self.buttonCancelDialog, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def initData(self, data):
        self.renter_id = data['id']
        self.editLastName.setText(data.get('last_name', ''))
        self.editFirstName.setText(data.get('first_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editPhoneMobile.setText(data.get('phone_mobile', ''))
        self.editPhoneWork.setText(data.get('phone_work', ''))
        self.editPhoneHome.setText(data.get('phone_home', ''))

        rents = data.get('rent_list', [])
        self.rentInfoModel.initData(self.renter_id, rents)

    def showAssignRentDlg(self):
        dialog = DlgRentAssign(self)
        dialog.setCallback(self.assignRent)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

    def assignRent(self, title, desc, status, paid, begin, end):
        params = {
            'id': '0', # rent_id
            'title': title,
            'desc': desc,
            'status': status,
            'paid': paid,
            'begin_date': begin,
            'end_date': end,
            'reg_date': datetime.now()
            }
        #print 'DlgRenterInfo::assignRent\n', params, '\n'
        lastRow = self.rentInfoModel.rowCount(QModelIndex())
        if self.rentInfoModel.insertRows(lastRow, 1, QModelIndex()):
            index = self.rentInfoModel.index(0, 0)
            self.rentInfoModel.setRow(index, params, Qt.EditRole)

    def applyDialog(self):
        userinfo, ok = self.checkFields()
        if ok:
            rents_info = self.rentInfoModel.get_model_as_formset()
            self.saveSettings(userinfo, rents_info)
            self.accept()
        else:
            QMessageBox.warning(self, _('Warning'),
                                _('Please fill required fields.'))

    def checkFields(self):
        userinfo = {
            'last_name': self.editLastName.text().toUtf8(),
            'first_name': self.editFirstName.text().toUtf8(),
            'email': self.editEmail.text().toUtf8(),
            'phone_mobile': self.editPhoneMobile.text().toUtf8(),
            'phone_work': self.editPhoneWork.text().toUtf8(),
            'phone_home': self.editPhoneHome.text().toUtf8(),
            }

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
            return (userinfo, False)
        return (userinfo, True)

    def saveSettings(self, userinfo, formset):
        params = {
            'user_id': self.renter_id,
            }
        params.update(userinfo)
        ajax = HttpAjax(self, '/manager/set_renter_info/', params, self.parent.session_id)
        response = ajax.parse_json()
        renter_id = int( response['saved_id'] )

        params = {}
        for i in xrange( int( formset['form-TOTAL_FORMS'] ) ):
            params.update( { 'form-%s-renter' % i: renter_id } )
        params.update(formset)
        ajax = HttpAjax(self, '/manager/set_renter_card/', params, self.parent.session_id)
        response = ajax.parse_json()
