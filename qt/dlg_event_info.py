# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import time
from datetime import datetime

from event_storage import Event
from http_ajax import HttpAjax

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')
__ = lambda x: datetime(*time.strptime(str(x), '%Y-%m-%d %H:%M:%S')[:6])

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgEventInfo(QDialog):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.setMinimumWidth(600)

        labelTitle = QLabel(_('Title'))
        self.editTitle = QLineEdit()
        self.editTitle.setReadOnly(True)
        labelTitle.setBuddy(self.editTitle)

        labelCoach = QLabel(_('Coach'))
        self.editCoach = QLineEdit()
        self.editCoach.setReadOnly(True)
        labelCoach.setBuddy(self.editCoach)

        labelBegin = QLabel(_('Begin'))
        self.editBegin = QDateTimeEdit()
        self.editBegin.setReadOnly(True)
        labelBegin.setBuddy(self.editBegin)

        labelDuration = QLabel(_('Duration'))
        self.editDuration = QLineEdit()
        self.editDuration.setReadOnly(True)
        labelDuration.setBuddy(self.editDuration)

        labelRoom = QLabel(_('Room'))
        self.comboRoom = QComboBox()
        self.comboRoom.setDisabled(True)
        labelRoom.setBuddy(self.comboRoom)

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(labelTitle, 0, 0)
        groupLayout.addWidget(self.editTitle, 0, 1)
        groupLayout.addWidget(labelCoach, 1, 0)
        groupLayout.addWidget(self.editCoach, 1, 1)
        groupLayout.addWidget(labelBegin, 2, 0)
        groupLayout.addWidget(self.editBegin, 2, 1)
        groupLayout.addWidget(labelDuration, 3, 0)
        groupLayout.addWidget(self.editDuration, 3, 1)
        groupLayout.addWidget(labelRoom, 4, 0)
        groupLayout.addWidget(self.comboRoom, 4, 1)

        self.buttonVisit = QPushButton(_('Visit'))
        self.buttonClose = QPushButton(_('Close'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonVisit)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonClose)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(groupLayout)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(_('Register the visit'))
        self.setSignals()

    def setCallback(self, callback):
        self.callback = callback

    def setModel(self, model):
        self.tree.setModel(model)

    def setSignals(self):
        self.connect(self.buttonVisit, SIGNAL('clicked()'),
                     self.visitEvent)
        self.connect(self.buttonClose, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def initData(self, event_id, rooms):
        ajax = HttpAjax(self, '/manager/get_course_info/',
                        {'id': event_id})
        response = ajax.parse_json()
        if response['code'] != 200:
            return QMessageBox.warning(
                self,
                _('Warning'),
                '[%(code)s] %(desc)s' % response,
                QMessageBox.Ok, QMessageBox.Ok)
        info = response['info']
        self.editTitle.setText(info['title'])
        self.editCoach.setText(info['coach'])
        start = __(info['start'])
        end = __(info['end'])
        self.editBegin.setDateTime(QDateTime(start))
        duration = (end - start).seconds / 60
        self.editDuration.setText(str(duration))
        self.setRooms(rooms, int(info['room']) + 100)

    def setRooms(self, rooms, current_id):
        current = 0
        for title, color, id in rooms:
            self.comboRoom.addItem(title, QVariant(id))
            if id == current_id:
                current = self.comboRoom.count() - 1
        self.comboRoom.setCurrentIndex(current)

    def visitEvent(self):
        print 'registered'

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
        self.callback(e_date, e_time, room, course)
        self.accept()
