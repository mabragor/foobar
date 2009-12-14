#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from model_sorting import SortClientCourses
from courses_list import CourseListModel, CoursesList
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_course_assign import DlgCourseAssign

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgUserInfo(QDialog):

    def __init__(self, mode, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
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

        groupCard = QGroupBox(self.tr('Course\'s history'))
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

    def initData(self, data):
        self.editFirstName.setText(data.get('first_name', ''))
        self.editLastName.setText(data.get('last_name', ''))
        self.editEmail.setText(data.get('email', ''))
        self.editRFID.setText(data.get('rfid_id', ''))

        courses = data.get('course_list', [])
        # source model
        #self.coursesModel = CourseListModel(self)
        self.coursesModel.initData(courses)
        # proxy model
        self.proxyModel = SortClientCourses(self)
        self.proxyModel.setSourceModel(self.coursesModel)
        # use proxy model to change data representation
        self.cardinfo.setModel(self.proxyModel)

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
            print self.rfid_id
            self.editRFID.setText(self.rfid_id)
        else:
            print 'rejected'

    def showAssignCourseDlg(self):
        dialog = DlgCourseAssign(self)
        dialog.setCallback(self.assignCourse)
        dialog.setModel(self.parent.modelCoursesTree)
        dialog.setModal(True)
        dlgStatus = dialog.exec_()

    def assignCourse(self, data):
        lastRow = self.coursesModel.rowCount(QModelIndex())
        print 'DlgUserInfo::assignCourse:', lastRow
        if self.coursesModel.insertRows(lastRow, 1, QModelIndex()):
            print 'DlgUserInfo::assignCourse:', lastRow
            index = self.coursesModel.index(lastRow, 0)
            self.coursesModel.setData(index, data, Qt.EditRole)
        print data

    def applyDialog(self):
        """ Применить настройки. """
        self.saveSettings()
        self.accept()

    def saveSettings(self):
        result = (self.editFirstName.text(),
                  self.editLastName.text(),
                  self.editEmail.text())
        print result

