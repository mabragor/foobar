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

        labelChange = QLabel(_('Coach change'))
        self.comboChange = QComboBox()
        self.comboChange.addItem(_('No change'), QVariant(None))
        labelChange.setBuddy(self.comboChange)
        self.buttonChange = QPushButton(_('Change'))

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
        groupLayout.addWidget(labelChange, 2, 0)
        groupLayout.addWidget(self.comboChange, 2, 1)
        groupLayout.addWidget(self.buttonChange, 2, 2)
        groupLayout.addWidget(labelBegin, 3, 0)
        groupLayout.addWidget(self.editBegin, 3, 1)
        groupLayout.addWidget(labelDuration, 4, 0)
        groupLayout.addWidget(self.editDuration, 4, 1)
        groupLayout.addWidget(labelRoom, 5, 0)
        groupLayout.addWidget(self.comboRoom, 5, 1)

        self.buttonVisitors = QPushButton(_('Visitors'))
        self.buttonVisit = QPushButton(_('Visit'))
        self.buttonRemove = QPushButton(_('Remove'))
        self.buttonClose = QPushButton(_('Close'))

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.buttonVisitors)
        buttonLayout.addWidget(self.buttonVisit)
        buttonLayout.addWidget(self.buttonRemove)
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(self.buttonChange)
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
        self.connect(self.buttonChange, SIGNAL('clicked()'),
                     self.changeCoach)
        self.connect(self.buttonClose, SIGNAL('clicked()'),
                     self, SLOT('reject()'))
        self.connect(self.comboChange, SIGNAL('currentIndexChanged(int)'),
                     self.enableComboChange)

    def initData(self, schedule, room_id):
        ajax = HttpAjax(self, '/manager/get_coaches/',
                        {}, self.parent.session_id)
        response = ajax.parse_json()
        for i in response['coaches_list']:
            self.comboChange.addItem('%s %s' % (i['last_name'], i['first_name']), QVariant(int(i['id'])))

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
            self.editCoach.setText(event['coach'])
        begin = __(schedule['begin'])
        end = __(schedule['end'])
        self.editBegin.setDateTime(QDateTime(begin))
        duration = (end - begin).seconds / 60
        self.editDuration.setText(str(duration))
        self.initRooms(int(room['id']))
        self.comboStatus.setCurrentIndex( int(schedule['status']) )
        try:
            index = int(schedule['change'])
        except:
            index = 0
        self.comboChange.setCurrentIndex(index)
        self.buttonChange.setDisabled(True)
        self.buttonRemove.setDisabled( begin < datetime.now() )

    def initRooms(self, current_id):
        self.current_room_index = current_id - 1
        for title, color, id in self.parent.rooms:
            self.comboRoom.addItem(title, QVariant(id))
            if id == current_id + 100:
                current = self.comboRoom.count() - 1
        self.comboRoom.setCurrentIndex(self.current_room_index)

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
            params = {'rfid_code': self.rfid_id,
                      'event_id': self.schedule['id']}
	    ajax = HttpAjax(self, '/manager/register_visit/',
                            params, self.parent.session_id)
	    response = ajax.parse_json()
            if response:
                message = _('The client is registered on this event.')
            else:
                message = _('Unable to register the visit!')
            QMessageBox.information(self, _('Client registration'), message)
	else:
	    print 'dialog was rejected'

    def eventRemove(self):
        reply = QMessageBox.question(
            self, _('Event remove'),
            _('Are you sure to remove this event from the calendar?'),
            QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            params = {'id': self.schedule['id']}
            ajax = HttpAjax(self, '/manager/cal_event_del/',
                            params, self.parent.session_id)
            response = ajax.parse_json()
            if response:
                index = self.comboRoom.currentIndex()
                room_id, ok = self.comboRoom.itemData(index).toInt()
                model = self.parent.scheduleModel
                model.remove(self.schedule, room_id)
                QMessageBox.information(self, _('Event removing'),
                                        _('Complete.'))
                self.reject()
            else:
                QMessageBox.information(self, _('Event removing'),
                                        _('Unable to remove this event!'))
        else:
            print 'just a joke'

    def showVisitors(self):
        dialog = DlgShowVisitors(self)
        dialog.setModal(True)
        dialog.initData(self.schedule['id'])
        dialog.exec_()

    def enableComboChange(self, index):
        self.buttonChange.setDisabled(False)

    def changeCoach(self):
        index = self.comboChange.currentIndex()
        coach_id, ok = self.comboChange.itemData(index).toInt()

        params = {'event_id': self.schedule['id'],
                  'coach_id': coach_id}
        ajax = HttpAjax(self, '/manager/register_change/',
                        params, self.parent.session_id)
        response = ajax.parse_json()
        if response:
            message = _('The coach of this event has been changed.')
        else:
            message = _('Unable to change a coach.')
        QMessageBox.information(self, _('Coach change registration'), message)
