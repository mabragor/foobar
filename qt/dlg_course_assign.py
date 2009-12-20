#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from settings import userRoles
from courses_tree import CoursesTree

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgCourseAssign(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        labelCardType = QLabel(self.tr('Type of card'))
        self.comboCardType = QComboBox()
        labelCardType.setBuddy(self.comboCardType)
        self.comboCardType.addItem(self.tr('Normal'))
        self.comboCardType.addItem(self.tr('Club'))

        labelBeginning = QLabel(self.tr('Course starts'))
        self.editBeginning = QDateEdit()
        current = QDate.currentDate()
        self.editBeginning.setDate(current)
        self.editBeginning.setMinimumDate(current)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelCardType, 0, 0)
        groupLayout.addWidget(self.comboCardType, 0, 1)
        groupLayout.addWidget(labelBeginning, 1, 0)
        groupLayout.addWidget(self.editBeginning, 1, 1)

        self.tree = CoursesTree(self)

        courseLayout = QVBoxLayout()
        courseLayout.addLayout(groupLayout)
        courseLayout.addWidget(self.tree)

        groupCourses = QGroupBox(self.tr('Available courses'))
        groupCourses.setLayout(courseLayout)

        buttonAssign = QPushButton(self.tr('Assign'))
        buttonCancel = QPushButton(self.tr('Cancel'))

        self.connect(buttonAssign, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(buttonCancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(buttonAssign)
        buttonLayout.addWidget(buttonCancel)

        layout = QVBoxLayout()
        layout.addWidget(groupCourses)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
        self.setWindowTitle(self.tr('Choose the course'))

    def setCallback(self, callback):
        self.callback = callback

    def setModel(self, model):
        self.tree.setModel(model)

    def applyDialog(self):
        card_type = self.comboCardType.currentIndex()
        bgn_date = self.editBeginning.date().toPyDate()
        index = self.tree.currentIndex()
        course_data = index.data(userRoles['getObjectID']).toPyObject()
        self.callback(card_type, bgn_date, course_data)
        self.accept()
