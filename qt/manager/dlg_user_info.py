# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, DEBUG
#from model_sorting import SortClientTeams
from card_list import CardList
from rent_list import RentListModel, RentList
from dlg_waiting_rfid import DlgWaitingRFID
from dialogs.assign_card import DlgAssignCard
from dlg_rent_assign import DlgRentAssign

from datetime import datetime

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4.QtXmlPatterns import *
from PyQt4 import uic

class WizardDialog(QDialog):
    """
    Диалог получает описание последовательности действий и
    обеспечивает запросы пользователю и обработку ответов в
    соответствии с данным описанием.
    """

    ui_file = None # will define later

    def __init__(self, parent=None, params=dict()):
        QDialog.__init__(self, parent)

        dlg = uic.loadUi(self.ui_file, self)
        self.setupUi(dlg)

    def prefill(self, title):
        self.setWindowTitle(title)

    def setupUi(self, dialog):
        self.connect(dialog.goBack, SIGNAL('clicked()'), self.go_back)
        self.connect(dialog.goNext, SIGNAL('clicked()'), self.go_next)

    def go_back(self):
        print 'Back button pressed'

    def go_next(self):
        print 'Next button pressed'

class WizardListDlg(WizardDialog):

    dialog = None
    ui_file = 'uis/dlg_list.ui'
    callback = None

    def __init__(self, parent=None, params=dict()):
        WizardDialog.__init__(self, parent)

    def prefill(self, title, data, callback):
        WizardDialog.prefill(self, title)
        self.callback = callback

        #import pprint; pprint.pprint(data)
        for id, text, slug in data:
            item = QListWidgetItem(text, self.listWidget)
            item.setData(Qt.UserRole, QVariant( (id, slug) ))

    def setupUi(self, dialog):
        self.dialog = dialog
        WizardDialog.setupUi(self, self)
        self.connect(self.dialog.listWidget,
                     SIGNAL('itemDoubleClicked(QListWidgetItem *)'),
                     self.go_next)

    def go_back(self):
        print 'Back'

    def go_next(self):
        list_widget = self.dialog.listWidget
        item = list_widget.currentItem()
        result = (item.data(Qt.UserRole), item.text().toUtf8())
        self.callback(result)
        self.close()

class DlgClientInfo(QDialog):

    def __init__(self, parent=None, params=dict()):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.params = params
        self.http = params['http']
        self.static = params['static']

        self.client_id = u'0'
        self.setMinimumWidth(800)

        self.editLastName = QLineEdit()
        self.editFirstName = QLineEdit()
        self.editEmail = QLineEdit()
        self.editPhone = QLineEdit()
        self.comboDiscount = QComboBox()
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
        layoutUser.addWidget(self.comboDiscount, 4, 1)
        layoutUser.addWidget(QLabel(_('Date of birth')), 5, 0)
        layoutUser.addWidget(self.dateBirth, 5, 1)
        layoutUser.addWidget( QLabel(_('RFID')), 6, 0)
        layoutUser.addWidget(self.editRFID, 6, 1)
        layoutUser.addWidget(self.buttonAssignRFID, 6, 2)

        groupUser = QGroupBox(_('Base data'))
        groupUser.setLayout(layoutUser)

        self.button_assign_card = QPushButton(_('Assign card'))
        self.buttonApplyDialog = QPushButton(_('Apply'))
        self.buttonCancelDialog = QPushButton(_('Cancel'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.button_assign_card)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonApplyDialog)
        buttonLayout.addWidget(self.buttonCancelDialog)

        # купленные курсы
        self.cardinfo = CardList(self, self.params)

        cardLayout = QVBoxLayout()
        cardLayout.addWidget(self.cardinfo)

        groupCard = QGroupBox(_('Card history'))
        groupCard.setLayout(cardLayout)

        layout = QVBoxLayout()
        layout.addWidget(groupUser)
        layout.addLayout(buttonLayout)
        layout.addWidget(groupCard)

        self.setLayout(layout)
        self.setWindowTitle(_('Client\'s information'))

        self.setRequired()
        self.setSignals()

        # discount combo
        for i in self.params.get('discounts', list()): # see params
            id = i['id']
            title = u'%s - %s%%' % (i['title'], i['percent'])
            self.comboDiscount.addItem(title, QVariant(id))

    def setRequired(self):
        self.editLastName.setProperty('required', QVariant(True))
        self.editFirstName.setProperty('required', QVariant(True))
        self.editEmail.setProperty('required', QVariant(True))
        self.editPhone.setProperty('required', QVariant(True))
        self.comboDiscount.setProperty('required', QVariant(True))
        self.dateBirth.setProperty('required', QVariant(True))
        self.editRFID.setProperty('required', QVariant(True))

    def setSignals(self):
        self.connect(self.buttonAssignRFID, SIGNAL('clicked()'),
                     self.assignRFID)
        self.connect(self.button_assign_card, SIGNAL('clicked()'),
                     self.assign_card)
        self.connect(self.buttonApplyDialog, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(self.buttonCancelDialog, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def initData(self, data=dict()):
        self.client_id = data.get('id', '0')
        self.editFirstName.setText(data.get('first_name', ''))
        self.editLastName.setText(data.get('last_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editPhone.setText(data.get('phone', ''))

        discount = data.get('discount', None)
        if discount:
            index = self.comboDiscount.findData(QVariant( int(discount.get('id', 0)) ))
            self.comboDiscount.setCurrentIndex( index )

        def str2date(value):
            import time
            return datetime(*time.strptime(value, '%Y-%m-%d')[:3])

        birth_date = data.get('birth_date', None) # it could be none while testing
        self.dateBirth.setDate(birth_date and str2date(birth_date) or \
                               QDate.currentDate())
        self.editRFID.setText(data.get('rfid_code', ''))

        card_list = data.get('team_list', [])
        self.cardinfo.model().initData(card_list)

    def cancelCard(self):
        row = self.cardinfo.currentRow()
        if DEBUG:
            print 'cancel card'
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

    def add_card_record(self):
        data  = {
            'card_types': 1,
            'price_cats_team': 1,
            'count_sold': 0,
            'price': 0.0,
            'discount': 0,
            'count_available': 0,
            'count_used': 0,
            'reg_datetime': _('Now'),
            }
        rows = []
        rows.append(data)
        model = self.cardinfo.model()
        lastRow = model.rowCount(QModelIndex())
        ok = model.insertRows(lastRow, rows, QModelIndex())
        model.dump()

    def xml_query(self, file_name, xquery):

        from os.path import dirname, join

        class Handler(QAbstractMessageHandler):
            def handleMessage(self, msg_type, desc, identifier, loc):
                print 'QUERY:', msg_type, desc, identifier, loc

        handler = Handler()

        query  = QXmlQuery()
        query.setMessageHandler(handler)
        query.setQuery(xquery % join(dirname(__file__), file_name))

        array = QByteArray()
        buf = QBuffer(array)
        buf.open(QIODevice.WriteOnly)

        if query.isValid():
            if query.evaluateTo(buf):
                results = QString.fromUtf8(array)
                return results
            else:
                print 'not evaluated'
        else:
            print 'not valid'
        return None

    def assign_card(self):

        # получить списки карт
        card_list = []
        for i in self.static['card_ordinary']:
            item = (i['id'], i['title'], i['slug'])
            card_list.append(item)
        if 0 < len(self.static['card_club']):
            item = (-1, _('Club Card'), 'club')
            card_list.append(item)
        if 0 < len(self.static['card_promo']):
            item = (-2, _('Promo Card'), 'promo')
            card_list.append(item)

        def callback(data):
            print 'callback trigger'
            self.wizard = data # id, title

        self.dialog = WizardListDlg(self)
        self.dialog.setModal(True)
        self.dialog.prefill(_('Choose the card\'s type'), card_list, callback)
        self.dialog.exec_()

        file_name = 'uis/logic_clientcard.xml'
        xquery = "doc('%s')/logic/rule[@name='abonement']/sequence"
        results = self.xml_query(file_name, xquery)
        if results:
            sequence = QDomDocument()
            if not sequence.setContent(results):
                raise ValueError('could not parse XML:', results)

            root = sequence.documentElement()
            print root.tagName()
            node = root.firstChild()
            while not node.isNull():
                element = node.toElement()
                print element.tagName()
                if node.hasAttributes():
                    print '%s is %s' % (
                        element.attribute('name'),
                        element.attribute('type')
                        )
                node = node.nextSibling()
        return

        # add user's discount
        data.update( {'discount': self.comboDiscount.currentIndex()} )
        # send data to user's model
        model = self.cardinfo.model()
        lastRow = model.rowCount(QModelIndex())
        if model.insertRows(lastRow, 1, QModelIndex()):
            index = model.index(0, 0)
            model.set_row(index, data, Qt.EditRole)

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
        discount, ok = self.comboDiscount.itemData(self.comboDiscount.currentIndex()).toInt()
        userinfo = {
            'last_name': self.editLastName.text().toUtf8(),
            'first_name': self.editFirstName.text().toUtf8(),
            'phone': self.editPhone.text().toUtf8(),
            'email': self.editEmail.text().toUtf8(),
            'birth_date': self.dateBirth.date().toPyDate(),
            'rfid_code': self.editRFID.text().toUtf8(),
            'discount': discount
            }
        for k,v in userinfo.items():
            if k is 'birth_date':
                continue
            if type(v) is int:
                continue
            if len(v) == 0:
                return (userinfo, False)
        return (userinfo, True)

    def saveSettings(self, userinfo):
        # save client's information
        params = { 'user_id': self.client_id, }
        params.update(userinfo)
        self.http.request('/manager/set_client_info/', params)
        default_response = None
        response = self.http.parse(default_response)
        self.client_id = int( response['saved_id'] )

        # save client's card
        model = self.cardinfo.model()
        params = model.get_model_as_formset(self.client_id)
        self.http.request('/manager/set_client_card/', params)
        response = self.http.parse(default_response)

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
            self.rentInfoModel.set_row(index, params, Qt.EditRole)

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

