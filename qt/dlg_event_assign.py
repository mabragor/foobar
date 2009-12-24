# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from settings import userRoles
from courses_tree import CoursesTree

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgEventAssign(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        labelDate = QLabel(_('Date'))
        self.editDate = QDateEdit()
        labelDate.setBuddy(self.editDate)
        current = QDate.currentDate()
        self.editDate.setDate(current)
        self.editDate.setMinimumDate(current)

        labelTime = QLabel(_('Time'))
        self.editTime = QTimeEdit()
        labelTime.setBuddy(self.editTime)
        current = QTime.currentTime()
        self.editTime.setTime(current)

        labelRoom = QLabel(_('Room'))
        self.comboRoom = QComboBox()
        labelRoom.setBuddy(self.comboRoom)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelDate, 0, 0)
        groupLayout.addWidget(self.editDate, 0, 1)
        groupLayout.addWidget(labelTime, 1, 0)
        groupLayout.addWidget(self.editTime, 1, 1)
        groupLayout.addWidget(labelRoom, 2, 0)
        groupLayout.addWidget(self.comboRoom, 2, 1)

        self.tree = CoursesTree(self)

        courseLayout = QVBoxLayout()
        courseLayout.addWidget(self.tree)

        groupCourses = QGroupBox(_('Available courses'))
        groupCourses.setLayout(courseLayout)

        self.buttonAssign = QPushButton(_('Assign'))
        self.buttonCancel = QPushButton(_('Cancel'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonAssign)
        buttonLayout.addWidget(self.buttonCancel)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(groupLayout)
        mainLayout.addWidget(groupCourses)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(_('Assign the event'))
        self.setSignals()

    def setCallback(self, callback):
        self.callback = callback

    def setModel(self, model):
        self.tree.setModel(model)

    def setSignals(self):
        self.connect(self.buttonAssign, SIGNAL('clicked()'),
                     self.applyDialog)
        self.connect(self.buttonCancel, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def setRooms(self, rooms):
        for title, color, id in rooms:
            self.comboRoom.addItem(title, QVariant(id))

    def applyDialog(self):
        e_date = self.editDate.date().toPyDate()
        e_time = self.editTime.time().toPyTime()
        index = self.comboRoom.currentIndex()
        room = self.comboRoom.itemData(index).toInt()
        index = self.tree.currentIndex()
        course = index.data(userRoles['getObjectID']).toPyObject()
        if type(course) is not list:
            return QMessageBox.warning(
                self,
                _('Warning'),
                '\n'.join([_('What course do you want to assign?'),
                           _('Choose the course on the course\'s tree.')]),
                QMessageBox.Ok, QMessageBox.Ok)
        #print course
        self.callback(e_date, e_time, room, course)
        self.accept()