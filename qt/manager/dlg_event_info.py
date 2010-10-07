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
from PyQt4 import uic

class UiDlgTemplate(QDialog):
    """ This is a common template for all UI dialogs. """

    ui_file = None
    dialog = None
    http = None

    def __init__(self, parent=None, params=dict()):
        QDialog.__init__(self, parent)

        self.http = params.get('http', None)

        self.dialog = uic.loadUi(self.ui_file, self)
        self.setupUi()

    def setupUi(self, title=None):
        if title:
            self.setWindowTitle(title)
        # init controls here

class EventInfo(UiDlgTemplate):

    ui_file = 'uis/dlg_event_info.ui'
    dialog = None

    def __init__(self, parent=None, params=dict()):
        UiDlgTemplate.__init__(self, parent, params)

    def setupUi(self, title=None):
        UiDlgTemplate.setupUi(self, title)
        self.connect(self.dialog.buttonClose,
                     SIGNAL('clicked()'), self.close)
        self.connect(self.dialog.comboFix,
                     SIGNAL('currentIndexChanged(int)'),
                     self.enableComboFix)

    def enableComboFix(self, index):
        self.dialog.buttonFix.setDisabled(False)


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
        # self.http.request('/manager/get_coaches/', {})
        # default_response = {'coaches_list': dict()}
        # response = self.http.parse(default_response)
        # for i in response['coaches_list']:
        #     item = '%s %s' % (i['last_name'], i['first_name'])
        #     self.comboChange.addItem(item, QVariant(int(i['id'])))

        # get the event's information
        self.http.request('/manager/get_event_info/', {'id': schedule.id})
        default_response = None
        response = self.http.parse(default_response)

        self.schedule = response['info']

        event = self.schedule['event']
        room = self.schedule['room']
        self.editTitle.setText(event['title'])

        if schedule.isTeam():
            self.editCoaches.setText(event['coaches'])

        begin = __(self.schedule['begin_datetime'])
        end = __(self.schedule['end_datetime'])
        self.editBegin.setDateTime(QDateTime(begin))
        self.editEnd.setDateTime(QDateTime(end))
        #self.initRooms(int(room['id']))

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
