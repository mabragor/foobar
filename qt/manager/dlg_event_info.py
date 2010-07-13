# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import time
from datetime import datetime

from settings import _, DEBUG
from event_storage import Event
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_show_visitors import DlgShowVisitors

__ = lambda x: datetime(*time.strptime(str(x), '%Y-%m-%d %H:%M:%S')[:6])

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgEventInfo(QDialog):

    def __init__(self, parent=None, params=dict()):
        QDialog.__init__(self, parent)

        self.parent = parent
        self.http = params.get('http', None)

        self.setMinimumWidth(600)

        self.editTitle = QLineEdit(); self.editTitle.setReadOnly(True)
        self.editCoach = QLineEdit(); self.editCoach.setReadOnly(True)
        self.editBegin = QDateTimeEdit(); self.editBegin.setReadOnly(True)
        self.editDuration = QLineEdit(); self.editDuration.setReadOnly(True)
        self.comboRoom = QComboBox(); self.comboRoom.setDisabled(True)

        labelChange = QLabel(_('Coach change'))
        self.comboChange = QComboBox()
        self.comboChange.addItem(_('No change'), QVariant(None))
        self.buttonChange = QPushButton(_('Change'))

        self.comboFix = QComboBox()
        self.comboFix.addItem(_('Waiting'), QVariant(0))
        self.comboFix.addItem(_('Done'), QVariant(1))
        self.comboFix.addItem(_('Cancelled'), QVariant(2))
        self.buttonFix = QPushButton(_('Fix'))

        groupLayout = QGridLayout()
        groupLayout.setColumnStretch(1, 1)
        groupLayout.setColumnMinimumWidth(1, 250)

        groupLayout.addWidget(QLabel(_('Title')), 0, 0)
        groupLayout.addWidget(self.editTitle, 0, 1)
        groupLayout.addWidget(QLabel(_('Coach')), 1, 0)
        groupLayout.addWidget(self.editCoach, 1, 1)
        groupLayout.addWidget(QLabel(_('Begin')), 3, 0)
        groupLayout.addWidget(self.editBegin, 3, 1)
        groupLayout.addWidget(QLabel(_('Duration')), 4, 0)
        groupLayout.addWidget(self.editDuration, 4, 1)
        groupLayout.addWidget(QLabel(_('Room')), 5, 0)
        groupLayout.addWidget(self.comboRoom, 5, 1)
        groupLayout.addWidget(QLabel(_('Fix as')), 6, 0)
        groupLayout.addWidget(self.comboFix, 6, 1)
        groupLayout.addWidget(self.buttonFix, 6, 2)

        groupLayout.addWidget(QLabel(_('Coach change')), 2, 0)
        groupLayout.addWidget(self.comboChange, 2, 1)
        groupLayout.addWidget(self.buttonChange, 2, 2)

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
        self.connect(self.buttonFix, SIGNAL('clicked()'),
                     self.fixEvent)
        self.connect(self.buttonClose, SIGNAL('clicked()'),
                     self, SLOT('reject()'))
        self.connect(self.comboChange, SIGNAL('currentIndexChanged(int)'),
                     self.enableComboChange)
        self.connect(self.comboFix, SIGNAL('currentIndexChanged(int)'),
                     self.enableComboFix)

    def initData(self, schedule):
        """ Use this method to initialize the dialog. """
        # get the coaches list first
        self.http.request('/manager/get_coaches/', {})
        default_response = {'coaches_list': dict()}
        response = self.http.parse(default_response)
        for i in response['coaches_list']:
            item = '%s %s' % (i['last_name'], i['first_name'])
            self.comboChange.addItem(item, QVariant(int(i['id'])))

        # get the event's information
        self.http.request('/manager/get_event_info/', {'id': schedule.id})
        default_response = None
        response = self.http.parse(default_response)

        self.schedule = response['info']

        event = self.schedule['event']
        room = self.schedule['room']
        self.editTitle.setText(event['title'])

        if schedule.isTeam():
            self.editCoach.setText(event['coach']['name'])

        begin = __(self.schedule['begin_datetime'])
        end = __(self.schedule['end_datetime'])
        self.editBegin.setDateTime(QDateTime(begin))
        duration = (end - begin).seconds / 60
        self.editDuration.setText(str(duration))
        self.initRooms(int(room['id']))

        try:
            index = int(self.schedule.get('change', 0))
        except ValueError:
            index = 0
        self.comboChange.setCurrentIndex(index)
        self.buttonChange.setDisabled(True)

        try:
            index = int(self.schedule.get('fixed', 0))
        except ValueError:
            index = 0
        self.comboFix.setCurrentIndex(index)
        self.buttonFix.setDisabled(True)

        self.buttonRemove.setDisabled( begin < datetime.now() )

    def initRooms(self, current_id):
        self.current_room_index = current_id - 1
        for title, color, id in self.parent.rooms:
            self.comboRoom.addItem(title, QVariant(id))
            if id == current_id + 100:
                current = self.comboRoom.count() - 1
        self.comboRoom.setCurrentIndex(self.current_room_index)

    def changeRoom(self, new_index):
        # Room change:
        # 1. The choosen room is empty inside whole time period.
        #    Change a room for the event.
        # 2. The choosen room is busy at all, i.e. two event are equal in time.
        #    Change the rooms.
        # 3. The choosen room is busy partially.
        #    Cancel the change, raise message.
        if new_index != self.current_room_index:
            # make room checking
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
                model.remove(self.schedule['id'], room_id, True)
                QMessageBox.information(self, _('Event removing'),
                                        _('Complete.'))
                self.accept()
            else:
                QMessageBox.information(self, _('Event removing'),
                                        _('Unable to remove this event!'))

    def showVisitors(self):
        dialog = DlgShowVisitors(self)
        dialog.setModal(True)
        dialog.initData(self.schedule['id'])
        dialog.exec_()

    def enableComboChange(self, index):
        self.buttonChange.setDisabled(False)

    def enableComboFix(self, index):
        self.buttonFix.setDisabled(False)

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

    def fixEvent(self):
        index = self.comboFix.currentIndex()
        fix_id, ok = self.comboFix.itemData(index).toInt()

        params = {'event_id': self.schedule['id'],
                  'fix_id': fix_id}
        ajax = HttpAjax(self, '/manager/register_fix/',
                        params, self.parent.session_id)
        response = ajax.parse_json()
        if response:
            message = _('The event has been fixed.')
        else:
            message = _('Unable to fix this event.')
        QMessageBox.information(self, _('Event fix registration'), message)
