# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import time
from datetime import datetime

from event_storage import Event
from http_ajax import HttpAjax
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_show_visitors import DlgShowVisitors

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
        labelRoom.setBuddy(self.comboRoom)

        labelStatus = QLabel(_('Status'))
        self.comboStatus = QComboBox()
        self.comboStatus.addItem(_('Waiting'), QVariant(0))
        self.comboStatus.addItem(_('Warning'), QVariant(1))
        self.comboStatus.addItem(_('Passed'), QVariant(2))
        labelStatus.setBuddy(self.comboStatus)

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

        self.buttonVisitors = QPushButton(_('Visitors'))
        self.buttonVisit = QPushButton(_('Visit'))
        self.buttonRemove = QPushButton(_('Remove'))
        self.buttonClose = QPushButton(_('Close'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonVisitors)
        buttonLayout.addWidget(self.buttonVisit)
        buttonLayout.addWidget(self.buttonRemove)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonClose)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(groupLayout)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle(_('Event'))
        self.setSignals()

    def setCallback(self, callback):
        self.callback = callback

    def setModel(self, model):
        self.tree.setModel(model)

    def setSignals(self):
        self.connect(self.comboRoom, SIGNAL('currentIndexChanged(int)'),
                     self.changeRoom)
        self.connect(self.buttonVisitors, SIGNAL('clicked()'),
                     self.showVisitors)
        self.connect(self.buttonVisit, SIGNAL('clicked()'),
                     self.visitEvent)
        self.connect(self.buttonRemove, SIGNAL('clicked()'),
                     self.eventRemove)
        self.connect(self.buttonClose, SIGNAL('clicked()'),
                     self, SLOT('reject()'))

    def initData(self, schedule, room_id):
        ajax = HttpAjax(self, '/manager/get_event_info/',
                        {'id': schedule.id}, self.parent.session_id)
        self.schedule = schedule
        response = ajax.parse_json()
        self.schedule = schedule = response['info']
        print schedule
        event = schedule['event']
        room = schedule['room']
        self.editTitle.setText(event['title'])
        if schedule['type'] == 'training':
            self.editCoach.setText(event['coaches'])
        begin = __(schedule['begin'])
        end = __(schedule['end'])
        self.editBegin.setDateTime(QDateTime(begin))
        duration = (end - begin).seconds / 60
        self.editDuration.setText(str(duration))
        self.initRooms(int(room['id']))
        self.comboStatus.setCurrentIndex( int(schedule['status']) )

    def initRooms(self, current_id):
        self.current_room_index = current_id - 1
        for title, color, id in self.parent.rooms:
            self.comboRoom.addItem(title, QVariant(id))
            if id == current_id + 100:
                current = self.comboRoom.count() - 1
        self.comboRoom.setCurrentIndex(current_room_index)

    def changeRoom(self, new_index):
        """
        Замена зала.
        1. Выбранный зал пуст в течении всего периода.
           Изменить зал для события.
        2. Выбранный зал занят полностью, т.е. два занятия совпадают.
           Обменять залы.
        3. Выбранный зал занят частично.
           Отменить замену, выдать сообщение.
        """
        if new_index != self.current_room_index:
            # выполнить проверку занятости зала
            #
            pass

    def visitEvent(self):
	def callback(rfid):
	    self.rfid_id = rfid

	self.callback = callback
	self.dialog = DlgWaitingRFID(self)
	self.dialog.setModal(True)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
	    ajax = HttpAjax(self, '/manager/register_visit/',
			    {'rfid_code': self.rfid_id,
                             'event_id': self.schedule['id']}, self.parent.session_id)
	    response = ajax.parse_json()
            if response and 'code' in response:
                if response['code'] == 200:
                    reply = QMessageBox.information(
                        self, _('Client registration'),
                        _('The client is registered on this event.'))
                else:
                    QMessageBox.warning(self, _('Warning'), response['desc'])
            else:
                print _('Check response format!')
	else:
	    print 'dialog was rejected'

    def eventRemove(self):
        reply = QMessageBox.question(
            self, _('Event remove'),
            _('Are you sure to remove this event from the calendar?'),
            QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            ajax = HttpAjax(self, '/manager/cal_event_del/',
                            {'id': self.schedule['id']}, self.parent.session_id)
            if ajax:
                response = ajax.parse_json()
                if 'code' in response:
                    if response['code'] == 200:
                        index = self.comboRoom.currentIndex()
                        room_id, ok = self.comboRoom.itemData(index).toInt()
                        model = self.parent.scheduleModel
                        model.remove(self.schedule, room_id)
                        self.reject()
                else:
                    print _('Check response format!')
        else:
            print 'just a joke'

    def showVisitors(self):
        dialog = DlgShowVisitors(self)
        dialog.setModal(True)
        dialog.initData(self.schedule['id'])
        dialog.exec_()
