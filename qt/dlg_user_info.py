#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from model_sorting import SortClientCourses
from courses_list import CourseListModel, CoursesListDelegate, CoursesList
from http_ajax import HttpAjax
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_course_assign import DlgCourseAssign

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgUserInfo(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.user_id = u'0'
        self.setMinimumWidth(800)

        # основные данные пользователя
        labelFirstName = QLabel(self.tr('First name'))
        labelLastName = QLabel(self.tr('Last name'))
        labelEmail = QLabel(self.tr('Email'))
        labelYearBirth = QLabel(self.tr('Year of birth'))
        labelUserSex = QLabel(self.tr('Sex'))
        labelRFID = QLabel(self.tr('RFID'))

        self.editFirstName = QLineEdit()
        self.editLastName = QLineEdit()
        self.editEmail = QLineEdit()
        self.editYearBirth = QLineEdit()
        self.editUserSex = QComboBox()
        self.editUserSex.addItem(self.tr('Male'))
        self.editUserSex.addItem(self.tr('Female'))
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

        groupUser = QGroupBox(self.tr('Base data'))
        groupUser.setLayout(layoutUser)

        # купленные курсы
        self.cardinfo = CoursesList(self)

        cardLayout = QVBoxLayout()
        cardLayout.addWidget(self.cardinfo)

        groupCard = QGroupBox(self.tr('Courses\' history'))
        groupCard.setLayout(cardLayout)

        buttonAssignRFID = QPushButton(self.tr('Assign RFID'))
        buttonAssignCourse = QPushButton(self.tr('Assign course'))
        buttonApplyDialog = QPushButton(self.tr('Apply'))
        buttonCancelDialog = QPushButton(self.tr('Cancel'))

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
        self.setWindowTitle(self.tr('User\'s information'))

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
        self.user_id = data['user_id']
        self.editFirstName.setText(data.get('first_name', ''))
        self.editLastName.setText(data.get('last_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editRFID.setText(data.get('rfid_id', ''))

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
        dialog.setModel(self.parent.modelCoursesTree)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

    def assignCourse(self, data):
        lastRow = self.coursesModel.rowCount(QModelIndex())
        if self.coursesModel.insertRows(lastRow, 1, QModelIndex()):
            index = self.coursesModel.index(0, 0)
            self.coursesModel.setRow(index, data, Qt.EditRole)

#         print 'DlgUserInfo::assignCourse DUMP:'
#         for item in self.coursesModel.storage:
#             print '\t',
#             for col in item:
#                 print col,
#             print

    def applyDialog(self):
        """ Применить настройки. """
        course_changes = self.coursesModel.get_changes_and_clean()
        self.saveSettings(course_changes)
        self.accept()

    def saveSettings(self, course_changes):
        assigned, cancelled, changed = course_changes
        print assigned
        print cancelled
        print changed
        ajax = HttpAjax(self, '/manager/set_user_info/',
                        {
                'user_id': self.user_id,
                'first_name': self.editFirstName.text(),
                'last_name': self.editLastName.text(),
                'email': self.editEmail.text(),
                'rfid_code': self.editRFID.text(),
                'course_assigned': assigned,
                'course_cancelled': cancelled,
                'course_changed': changed
                })
        json_like = ajax.parse_json()
        if 'code' in json_like:
            print 'AJAX result: [%(code)s] %(desc)s' % json_like
        else:
            print 'Check response format!'


