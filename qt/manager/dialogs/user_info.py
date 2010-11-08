# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from settings import _, DEBUG, userRoles

from dialogs.rfid_wait import WaitingRFID
from dialogs.assign_card import DlgAssignCard

#from model_sorting import SortClientTeams
from card_list import CardListModel
from rent_list import RentListModel, RentList
from dlg_rent_assign import DlgRentAssign
from settings import _, userRoles
from ui_dialog import UiDlgTemplate
from library import dictlist2dict, dictlist_keyval

from datetime import datetime

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtXml import *
from PyQt4.QtXmlPatterns import *
from PyQt4 import uic

class WizardDialog(QDialog):
    """ The dialog gives the description of a actions sequence and
    asks user for datas and process his replies."""

    ui_file = None # will define later
    params = None

    def __init__(self, parent=None, params=dict()):
        QDialog.__init__(self, parent)

        self.params = params

        dlg = uic.loadUi(self.ui_file, self)
        self.setupUi(dlg)

    def prefill(self, title):
        self.setWindowTitle(title)

    def setupUi(self, dialog):
        back_title = self.params.get('button_back', None)
        next_title = self.params.get('button_next', None)
        if back_title:
            dialog.goBack.setText(back_title)
        if next_title:
            dialog.goNext.setText(next_title)

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
        WizardDialog.__init__(self, parent, params)

    def prefill(self, title, data, callback):
        WizardDialog.prefill(self, title)
        self.callback = callback

        for id, text in data:
            item = QListWidgetItem(text, self.listWidget)
            item.setData(Qt.UserRole, QVariant(id))

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
        result = item.data(Qt.UserRole).toPyObject()
        self.callback(result)
        self.close()

class WizardSpinDlg(WizardDialog):

    dialog = None
    ui_file = 'uis/dlg_spin.ui'
    callback = None
    SPIN_STEP = 4

    def __init__(self, parent=None, params=dict()):
        WizardDialog.__init__(self, parent, params)

    def prefill(self, title, data, callback):
        WizardDialog.prefill(self, title)
        self.callback = callback

        self.spinBox.setValue(data)

    def setupUi(self, dialog):
        self.dialog = dialog
        WizardDialog.setupUi(self, self)

        self.dialog.spinBox.setRange(0, 1000000)
        self.dialog.spinBox.setSingleStep(self.SPIN_STEP)
        self.connect(self.dialog.spinBox, SIGNAL('editingFinished()'), self.editing_finished)

    def go_back(self):
        print 'Back'

    def go_next(self):
        spin_widget = self.dialog.spinBox
        result = spin_widget.value()
        self.callback(result)
        self.close()

    def editing_finished(self):
        """
        The editingFinished() signal handler.
        The value has to be dividable by SPIN_STEP
        """
        value = self.dialog.spinBox.value()
        if value < self.SPIN_STEP:
            self.dialog.spinBox.setValue(self.SPIN_STEP)
            return

        reminder = value % self.SPIN_STEP
        if reminder != 0:
            self.dialog.spinBox.setValue(value - reminder)

class WizardPriceDlg(WizardDialog):

    dialog = None
    ui_file = 'uis/dlg_price.ui'
    callback = None

    def __init__(self, parent=None, params=dict()):
        WizardDialog.__init__(self, parent, params)

    def prefill(self, title, data, callback):
        WizardDialog.prefill(self, title)
        self.callback = callback

        self.doubleSpinBox.setValue(data)

    def setupUi(self, dialog):
        self.dialog = dialog
        WizardDialog.setupUi(self, self)
        self.dialog.doubleSpinBox.setMaximum(1000000)

    def go_back(self):
        print 'Back'

    def go_next(self):
        spin_widget = self.dialog.doubleSpinBox
        result = spin_widget.value()
        self.callback(result)
        self.close()

class PaymentDlg(WizardDialog):

    dialog = None
    ui_file = 'uis/dlg_price.ui'
    callback = None

    def __init__(self, parent=None, params=dict()):
        WizardDialog.__init__(self, parent, params)

    def setupUi(self, dialog):
        self.dialog = dialog
        WizardDialog.setupUi(self, self)

        self.callback = self.params.get('callback', None)
        initial_value = self.params.get('initial_value', 0)
        dialog_title = self.params.get('title', _('Unknown'))
        self.doubleSpinBox.setRange(0, initial_value)
        self.doubleSpinBox.setValue(initial_value)
        WizardDialog.prefill(self, dialog_title)

    def go_back(self):
        self.reject()

    def go_next(self):
        value = self.doubleSpinBox.value()
        self.callback(value)
        self.accept()

class ClientInfo(UiDlgTemplate):

    ui_file = 'uis/dlg_user_info.ui'
    title = _('Client\'s information')
    card_model = None
    static = None
    client_id = u'0'

    COLUMN_PRICE_INDEX = 4
    COLUMN_PAID_INDEX = 5
    COLUMN_CANCEL_INDEX = 12

    def __init__(self, parent=None, params=dict()):
        self.static = params['static']
        UiDlgTemplate.__init__(self, parent, params)

    def setupUi(self):
        UiDlgTemplate.setupUi(self)

        self.tableHistory.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.card_model = CardListModel(self)
        self.tableHistory.setModel(self.card_model)
        self.tableHistory.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableHistory.customContextMenuRequested.connect(self.context_menu)

        for i in self.static.get('discounts', list()): # see params
            title = u'%(title)s - %(percent)s%%' % i
            self.comboDiscount.addItem(title, QVariant(i['id']))

        self.connect(self.buttonAssign, SIGNAL('clicked()'), self.assign_card)
        self.connect(self.buttonRFID,   SIGNAL('clicked()'), self.assignRFID)
        self.connect(self.buttonApply,  SIGNAL('clicked()'), self.applyDialog)
        self.connect(self.buttonClose,  SIGNAL('clicked()'), self, SLOT('reject()'))

    def context_menu(self, position):
        """ Create context menu."""

        menu = QMenu()

        index = self.tableHistory.indexAt(position)
        model = index.model()

        # payment
        action_payment_add = menu.addAction(_('Payment'))
        need_to_add = self.payment_diff(index)
        if need_to_add < 0.01:
            action_payment_add.setDisabled(True)
        # cancel
        action_cancel = menu.addAction(_('Cancel'))
        idx_cancel = model.index(index.row(), self.COLUMN_CANCEL_INDEX)
        card_cancel = model.data(idx_cancel, Qt.DisplayRole)
        if type(card_cancel) is unicode:
            action_cancel.setDisabled(True)

        # show context menu
        action = menu.exec_(self.tableHistory.mapToGlobal(position))

        # choose action
        if action == action_payment_add:
            self.payment_add(index, need_to_add)
        elif action == action_cancel:
            QMessageBox.warning(self, _('Warning'),
                                _('Not yet implemented!'))
        else:
            print 'unknown'

    def initData(self, data=dict()):
        self.client_id = data.get('id', '0')

        meta = [('last_name', self.editLastName),
                ('first_name', self.editFirstName),
                ('email', self.editEmail),
                ('phone', self.editPhone),
                ]
        for key, obj in meta:
            text = data.get(key, '')
            obj.setText(text)
            obj.setToolTip(text)

        discount = data.get('discount', None)
        if discount:
            index = self.comboDiscount.findData(QVariant( int(discount.get('id', 0)) ))
            self.comboDiscount.setCurrentIndex( index )

        def str2date(value):
            return datetime.strptime(value, '%Y-%m-%d').date()

        birth_date = data.get('birth_date', None) # it could be none while testing
        self.dateBirth.setDate(birth_date and str2date(birth_date) or \
                               QDate.currentDate())
        rfid = data.get('rfid_code', None)
        if rfid:
            self.buttonRFID.setText(rfid)
            self.buttonRFID.setToolTip(_('RFID code of this client.'))
            self.buttonRFID.setDisabled(True)

        # fill the card list
        card_list = data.get('team_list', [])
        self.tableHistory.model().initData(card_list)

    def payment_diff(self, index):
        """ Calculate payment amount. """

        model = index.model()
        idx_price = model.index(index.row(), self.COLUMN_PRICE_INDEX)
        card_price = model.data(idx_price, Qt.DisplayRole)
        idx_paid = model.index(index.row(), self.COLUMN_PAID_INDEX)
        card_paid = model.data(idx_paid, Qt.DisplayRole)
        initial_value = card_price - card_paid

        return initial_value

    def payment_add(self, index, initial_value=0.00):
        """ Show price dialog and register payment. """

        def callback(value):
            print 'callback value is', value
            self.payment = value

        model = index.model()
        card_id = model.get_record_id(index.row())

        idx_price = model.index(index.row(), self.COLUMN_PRICE_INDEX)
        idx_paid = model.index(index.row(), self.COLUMN_PAID_INDEX)
        card_paid = model.data(idx_paid, Qt.DisplayRole)

        params = {
            'title': _('Payment'),
            'button_back': _('Cancel'),
            'button_next': _('Apply'),
            'callback': callback,
            'initial_value': initial_value,
            }

        dialog = PaymentDlg(self, params)
        dialog.setModal(True)

        if QDialog.Accepted == dialog.exec_():
            params = {'card_id': card_id, 'amount': self.payment}
            if not self.http.request('/manager/payment_add/', params):
                QMessageBox.critical(self, _('Register payment'), _('Unable to register: %s') % self.http.error_msg)
                return
            default_response = None
            response = self.http.parse(default_response)

            if response and response.get('saved_id', 0) == card_id:
                value = card_paid + self.payment
                model.setData(idx_paid, value, Qt.EditRole)


    def assignRFID(self):
        def callback(rfid):
            self.rfid_id = rfid

        params = {
            'http': self.http,
            'static': self.static,
            'mode': 'client',
            'callback': callback,
            }
        dialog = WaitingRFID(self, params)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

        if QDialog.Accepted == dlgStatus:
            # check the rfid code
            params = {'rfid_code': self.rfid_id, 'mode': 'client'}
            if not self.http.request('/manager/get_client_info/', params):
                QMessageBox.critical(self, _('Client info'), _('Unable to fetch: %s') % self.http.error_msg)
                return
            default_response = None
            response = self.http.parse(default_response)
            if response and 'info' in response and response['info'] is not None:
                QMessageBox.warning(self, _('Warning'),
                                    _('This RFID is used already!'))
            else:
                self.buttonRFID.setText(self.rfid_id)
                self.buttonRFID.setDisabled(True)

    def cancelCard(self):
        row = self.cardinfo.currentRow()
        if DEBUG:
            print 'cancel card'
            print row
        self.cardinfo.removeRow(row)

    def xml_query(self, file_name, xquery, slug):

        from os.path import dirname, join

        class Handler(QAbstractMessageHandler):
            def handleMessage(self, msg_type, desc, identifier, loc):
                print 'QUERY:', msg_type, desc, identifier, loc

        handler = Handler()

        query  = QXmlQuery()
        query.setMessageHandler(handler)
        prepared_query = xquery % (join(dirname(__file__), file_name), slug)
        query.setQuery(prepared_query)

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

    def wizard_dialog(self, dtype, title, data_to_fill):
        self.wizard_data = None

        def callback(data):
            self.wizard_data = data # id, title, slug

        dialogs = {
            'list': WizardListDlg,
            'spin': WizardSpinDlg,
            'price': WizardPriceDlg,
            }

        self.dialog = dialogs[dtype](self)
        self.dialog.setModal(True)
        self.dialog.prefill(title, data_to_fill, callback)
        self.dialog.exec_()

        return self.wizard_data

    def generate_card_list(self):
        card_list = []
        for i in self.static['card_ordinary']:
            item = (i['slug'], i['title'])
            card_list.append(item)
        if 0 < len(self.static['card_club']):
            item = ('club', _('Club Card'))
            card_list.append(item)
        if 0 < len(self.static['card_promo']):
            item = ('promo', _('Promo Card'))
            card_list.append(item)
        return card_list

    def assign_card(self):
        slug = self.wizard_dialog('list', _('Choose the card\'s type'),
                                  self.generate_card_list())
        if not slug: # user has pressed 'Escape' or closes the dialog
            return

        file_name = '../uis/logic_clientcard.xml'
        xquery = "doc('%s')/logic/rule[@name='%s']/sequence"
        results = self.xml_query(file_name, xquery, slug)
        if results:
            sequence = QDomDocument()
            if not sequence.setContent(results):
                raise ValueError('could not parse XML:', results)

            card_type = dictlist_keyval(self.static['card_ordinary'], 'slug', slug)[0]
            steps = {'slug': str(slug)}

            root = sequence.documentElement()
            node = root.firstChild()
            while not node.isNull():
                element = node.toElement()
                if 'dialog' == element.tagName():
                    if node.hasAttributes():
                        # get dialog's attributes
                        dlg_type = element.attribute('type')
                        dlg_title = element.attribute('title')
                        dlg_name = element.attribute('name')
                        static_key = element.hasAttribute('static') and str(element.attribute('static')) or None
                        default = element.hasAttribute('default') and element.attribute('default') or 0

                        # get the result type info
                        result_as = str(element.attribute('result_as'))
                        result_types = {'integer': int, 'float': float}
                        conv = result_types[result_as]

                        # if there are child nodes, so
                        if node.hasChildNodes():
                            child = node.firstChild()
                            element = child.toElement()
                            if 'calculate' == element.tagName():
                                # it needs to calculate the value using this class method
                                if element.hasAttribute('function'):
                                    method_name = element.attribute('function')
                                    if hasattr(self, str(method_name)):
                                        function = eval('self.%s' % method_name)
                                        if callable(function):
                                            default = function(card_type, steps)
                                        else:
                                            print 'This is not a callable.'
                                    else:
                                        print 'This method is not defined in the class.'

                        # show dialog and get a data from user
                        result = None
                        result = self.show_ui_dialog(dlg_type, dlg_title, default, static_key)
                        if not result: # user has pressed 'Escape' or closes the dialog
                            return

                        # save user date with needed type
                        steps[str(dlg_name)] = conv(result)

                        # skip the following dialog if it needs
                        # ToDo: skip all dialogs until the one
                        if self.need_skip_next_dlg(node, conv, result):
                            node = node.nextSibling()

                node = node.nextSibling()
            # end while

            #print card_type
            #print steps
            # fill count_available
            if not card_type['is_priceless']:
                # here all prices defined hard, no delays for payment
                if card_type['slug'] in ('test', 'once'):
                    key = '%s_price' % card_type['slug']
                    prices = dictlist_keyval(card_type['price_categories'], 'id', steps['price_category'])[0]
                    price = float(prices[key])
                    steps['price'] = steps['paid'] = price
                    steps['count_sold'] = 1

                if float(steps['price']) - float(steps['paid']) < 0.01: # client paid full price
                    steps['count_available'] = steps['count_sold']
                else: # need to calculate
                    prices = dictlist_keyval(card_type['price_categories'], 'id', steps['price_category'])[0]
                    price = float(prices['once_price'])
                    from math import floor
                    steps['count_available'] = int(floor(steps['paid'] / price))

            # import pprint
            # print 'STEPS:'
            # pprint.pprint(steps)

            # send data to user's model
            model = self.tableHistory.model()
            model.insert_new(steps, 0)
            # model.dump()

    def need_skip_next_dlg(self, node, conv, value):
        """ This method realises the skipping a next dialog by condition. """
        skip = False
        if node.hasChildNodes():
            child = node.firstChild()
            element = child.toElement()
            if 'skip_next_if' == element.tagName():
                if element.hasAttribute('lower_than') and value < conv( element.attribute('lower_than') ):
                    skip = True
                if element.hasAttribute('greater_than') and value > conv( element.attribute('greater_than') ):
                    skip = True
        return skip

    def _price_abonement(self, card_type, steps):
        """ This method calculate the abonement price. See logic_clientcard.xml. """
        prices = dictlist_keyval(card_type['price_categories'], 'id', steps['price_category'])[0]

        count = int(steps['count_sold'])
        if count == 1:
            price = float(prices['once_price'])
        elif count == 4:
            price = float(prices['half_price'])
        elif count == 8:
            price = float(prices['full_price'])
        elif count > 8 and count % 8 == 0:
            price = float(prices['full_price']) * (count / 8)
        else:
            print _('Invalid usage. Why do you use count=%i' % count)
            price = float(0.0)

        steps['price'] = price
        return price

    def show_ui_dialog(self, dlg_type, dlg_title, default=0, static_key=None):
        if 'list' == dlg_type and static_key is not None:
            prefill = [(i['id'], i['title']) for i in self.static[static_key]]
            result = self.wizard_dialog('list', dlg_title, prefill)
        if 'spin' == dlg_type:
            result = self.wizard_dialog('spin', dlg_title, int(default))
        if 'price' == dlg_type:
            result = self.wizard_dialog('price', dlg_title, float(default))
        return result

    def applyDialog(self):
        """ Apply settings. """
        userinfo, ok = self.checkFields()
        if ok:
            if self.saveSettings(userinfo):
                self.accept()
        else:
            QMessageBox.warning(self, _('Warning'),
                                _('Please fill all fields.'))
    def checkFields(self):
        discount, ok = self.comboDiscount.itemData(self.comboDiscount.currentIndex()).toInt()
        userinfo = {
            'last_name': self.editLastName.text().toUtf8(),
            'first_name': self.editFirstName.text().toUtf8(),
            'phone': self.editPhone.text().toUtf8(),
            'email': self.editEmail.text().toUtf8(),
            'birth_date': self.dateBirth.date().toPyDate(),
            'rfid_code': self.buttonRFID.text().toUtf8(),
            'discount': discount
            }

        # this may be uninitialized, so remove it from dictionary
        if len(userinfo['rfid_code']) != 8:
            del(userinfo['rfid_code'])

        for k,v in userinfo.items():
            if k is 'birth_date':
                continue
            if type(v) is int:
                continue
            if len(v) == 0:
                return (userinfo, False)
        return (userinfo, True)

    def saveSettings(self, userinfo):
        default_response = None

        # save client's information
        params = { 'user_id': self.client_id, }
        params.update(userinfo)
        if not self.http.request('/manager/set_client_info/', params):
            QMessageBox.critical(self, _('Save info'), _('Unable to save: %s') % self.http.error_msg)
            return
        response = self.http.parse(default_response)
        if not response:
            error_msg = self.http.error_msg
            message = _('Unable to save client\'s info!\nReason:\n%s') % error_msg
            QMessageBox.warning(self, _('Saving'), message)
            return False

        # save client's card
        model = self.tableHistory.model()
        params = model.get_model_as_formset(response['saved_id'])
        if not self.http.request('/manager/set_client_card/', params):
            QMessageBox.critical(self, _('Save cards'), _('Unable to save: %s') % self.http.error_msg)
            return
        response = self.http.parse(default_response)
        if not response:
            error_msg = self.http.error_msg
            message = _('Unable to save client\'s card!\nReason:\n%s') % error_msg
            QMessageBox.warning(self, _('Saving'), message)
            return False

        return True

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

