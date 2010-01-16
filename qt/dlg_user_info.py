# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

from model_sorting import SortClientCourses
from courses_list import CourseListModel, CoursesListDelegate, CoursesList
from http_ajax import HttpAjax
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_course_assign import DlgCourseAssign
from dlg_rent_assign import DlgRentAssign

from datetime import datetime

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgClientInfo(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.user_id = u'0'
        self.setMinimumWidth(800)

        # основные данные пользователя
        labelFirstName = QLabel(_('First name'))
        labelLastName = QLabel(_('Last name'))
        labelEmail = QLabel(_('Email'))
        labelYearBirth = QLabel(_('Year of birth'))
        labelUserSex = QLabel(_('Sex'))
        labelRFID = QLabel(_('RFID'))

        self.editFirstName = QLineEdit()
        self.editLastName = QLineEdit()
        self.editEmail = QLineEdit()
        self.editYearBirth = QLineEdit()
        self.editUserSex = QComboBox()
        self.editUserSex.addItem(_('Male'))
        self.editUserSex.addItem(_('Female'))
        self.editRFID = QLineEdit()
        self.editRFID.setReadOnly(True)

        layoutUser = QGridLayout()
        layoutUser.setColumnStretch(1, 1)
        layoutUser.setColumnMinimumWidth(1, 250)

        layoutUser.addWidget(labelFirstName, 0, 0)
        layoutUser.addWidget(self.editFirstName, 0, 1)
        layoutUser.addWidget(labelLastName, 1, 0)
        layoutUser.addWidget(self.editLastName, 1, 1)
        layoutUser.addWidget(labelEmail, 2, 0)
        layoutUser.addWidget(self.editEmail, 2, 1)
#         layoutUser.addWidget(labelYearBirth, 3, 0)
#         layoutUser.addWidget(self.editYearBirth, 3, 1)
#         layoutUser.addWidget(labelUserSex, 4, 0)
#         layoutUser.addWidget(self.editUserSex, 4, 1)
        layoutUser.addWidget(labelRFID, 3, 0)
        layoutUser.addWidget(self.editRFID, 3, 1)

        groupUser = QGroupBox(_('Base data'))
        groupUser.setLayout(layoutUser)

        # купленные курсы
        self.cardinfo = CoursesList(self)

        cardLayout = QVBoxLayout()
        cardLayout.addWidget(self.cardinfo)

        groupCard = QGroupBox(_('Courses\' history'))
        groupCard.setLayout(cardLayout)

        buttonAssignRFID = QPushButton(_('Assign RFID'))
        buttonAssignCourse = QPushButton(_('Assign course'))
        buttonApplyDialog = QPushButton(_('Apply'))
        buttonCancelDialog = QPushButton(_('Cancel'))

        self.connect(buttonAssignRFID, SIGNAL('clicked()'),
                     self.assignRFID)
        self.connect(buttonAssignCourse, SIGNAL('clicked()'),
                     self.showAssignCourseDlg)
        self.connect(buttonApplyDialog, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(buttonCancelDialog, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(buttonAssignRFID)
        buttonLayout.addWidget(buttonAssignCourse)
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
        self.coursesModel = CourseListModel(self)
        # proxy model
        #self.proxyModel = SortClientCourses(self)
        #self.proxyModel.setSourceModel(self.coursesModel)
        # use proxy model to change data representation
        self.cardinfo.setModel(self.coursesModel)
        self.delegate = CoursesListDelegate()
        #self.cardinfo.setItemDelegate(self.delegate)

    def initData(self, data):
        self.user_id = data['id']
        self.editFirstName.setText(data.get('first_name', ''))
        self.editLastName.setText(data.get('last_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editRFID.setText(data.get('rfid_code', ''))

        courses = data.get('course_list', [])
        self.coursesModel.initData(courses)

    def cancelCourse(self):
        print 'cancel course'
        row = self.cardinfo.currentRow()
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

    def showAssignCourseDlg(self):
        dialog = DlgCourseAssign(self)
        dialog.setCallback(self.assignCourse)
        dialog.setModel(self.parent.tree)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

    def assignCourse(self, card_type, bgn_date, duration_index, data):
        # duration matters for club card only
        lastRow = self.coursesModel.rowCount(QModelIndex())
        if self.coursesModel.insertRows(lastRow, 1, QModelIndex()):
            index = self.coursesModel.index(0, 0)
            self.coursesModel.setRow(index, data, Qt.EditRole, card_type, bgn_date, duration_index)

        print 'DlgUserInfo::assignCourse DUMP:'
        for item in self.coursesModel.storage:
            print '\t',
            for col in item:
                print col,
            print

    def applyDialog(self):
        """ Применить настройки. """
        course_changes = self.coursesModel.get_changes_and_clean()
        self.saveSettings(course_changes)
        self.accept()

    def saveSettings(self, course_changes):
        assigned, cancelled, changed = course_changes
        params = {
            'user_id': self.user_id,
            'first_name': self.editFirstName.text().toUtf8(),
            'last_name': self.editLastName.text().toUtf8(),
            'email': self.editEmail.text().toUtf8(),
            'rfid_code': self.editRFID.text().toUtf8(),
            'course_assigned': assigned,
            'course_cancelled': cancelled,
            'course_changed': changed
            }
        #print 'DlgClientInfo::saveSettings', params
        ajax = HttpAjax(self, '/manager/set_user_info/', params)
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
        ajax = HttpAjax(self, '/manager/set_renter_info/', params)
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
            ajax = HttpAjax(self, '/manager/set_rent/', params)
            response = ajax.parse_json()
            rent_id = int( response['saved_id'] )

        self.accept()
