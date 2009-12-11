#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from courses_tree import CoursesTree

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgCourseAssign(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(800)

        self.tree = CoursesTree(self)

        courseLayout = QVBoxLayout()
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

    def setModel(self, model):
        self.tree.setModel(model)

    def applyDialog(self):
        """ Применить настройки. """
        self.saveSettings()
        self.accept()

    def saveSettings(self):
        index = self.tree.currentIndex()
        print 'saveSettings'
        print index.data(Qt.DisplayRole)


