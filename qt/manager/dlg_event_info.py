# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import time
from datetime import datetime

from settings import _, DEBUG
from event_storage import Event
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_show_visitors import ShowVisitors
from dialogs.show_coaches import ShowCoaches
from dialogs.searching import Searching
from ui_dialog import UiDlgTemplate

__ = lambda x: datetime(*time.strptime(str(x), '%Y-%m-%d %H:%M:%S')[:6])

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class EventInfo(UiDlgTemplate):

    ui_file = 'uis/dlg_event_info.ui'
    title = _('Event\'s information')

    def __init__(self, parent=None, params=dict()):
        UiDlgTemplate.__init__(self, parent, params)

    def setupUi(self):
        UiDlgTemplate.setupUi(self)

        self.connect(self.buttonClose,       SIGNAL('clicked()'), self.close)
        self.connect(self.buttonVisitors,    SIGNAL('clicked()'), self.showVisitors)
        self.connect(self.buttonVisitRFID,   SIGNAL('clicked()'), self.visitEventRFID)
        self.connect(self.buttonVisitManual, SIGNAL('clicked()'), self.visitEventManual)
        self.connect(self.buttonRemove,      SIGNAL('clicked()'), self.removeEvent)
        self.connect(self.buttonFix,         SIGNAL('clicked()'), self.fixEvent)
        self.connect(self.buttonChange,      SIGNAL('clicked()'), self.changeCoaches)
        self.connect(self.comboFix, SIGNAL('currentIndexChanged(int)'),
                     lambda: self.buttonFix.setDisabled(False))

    def enableComboFix(self, index):
        self.buttonFix.setDisabled(False)

    def initData(self, obj, index):
        """ Use this method to initialize the dialog. """

        self.schedule_object = obj
        self.schedule_index = index

        # get the event's information
        self.http.request('/manager/get_event_info/', {'id': self.schedule_object.id})
        default_response = None
        response = self.http.parse(default_response)

        self.schedule = response['info']
        event = self.schedule['event']
        status = self.schedule.get('status', 0) # 0 means wainting
        room = self.schedule['room']
        self.editTitle.setText(event['title'])

        if self.schedule_object.isTeam(): # get coaches list from schedule, not from team, because of exchange
            coaches_list = self.schedule.get('coaches', None)
            if coaches_list:
                title = ', '.join([i['name'] for i in coaches_list])
            else:
                title = _('Unknown')
            self.editCoaches.setText(title)

        begin = __(self.schedule['begin_datetime'])
        end = __(self.schedule['end_datetime'])
        self.editBegin.setDateTime(QDateTime(begin))
        self.editEnd.setDateTime(QDateTime(end))

        current_id = int(room['id'])
        self.current_room_index = current_id - 1
        for title, color, room_id in self.parent.rooms:
            self.comboRoom.addItem(title, QVariant(room_id))
            if id == current_id + 100:
                current = self.comboRoom.count() - 1
        self.comboRoom.setCurrentIndex(self.current_room_index)

        # disable controls for events in the past
        is_past = begin < datetime.now()
        self.buttonRemove.setDisabled(is_past)
        self.buttonVisitRFID.setDisabled(is_past)
        self.buttonVisitManual.setDisabled(is_past)
        self.buttonChange.setDisabled(is_past)

        self._init_fix(status)

    def _init_fix(self, current):
        """ Helper method to init eventFix combo."""
        for id, title in self.parent.static['event_fix_choice']:
            self.comboFix.addItem(title, QVariant(id))
        self.comboFix.setCurrentIndex(int(current))
        self.buttonFix.setDisabled(True)

    def showVisitors(self):
        dialog = ShowVisitors(self, {'http': self.http})
        dialog.setModal(True)
        dialog.initData(self.schedule['id'])
        dialog.exec_()

    def visitEventRFID(self):
        """
        Register the visit by client's RFID label.
        """

        def callback(rfid):
            self.rfid_id = rfid

        self.callback = callback
        self.dialog = DlgWaitingRFID(self)
        self.dialog.setModal(True)
        dlgStatus = self.dialog.exec_()

        if QDialog.Accepted == dlgStatus:
            params = {'rfid_code': self.rfid_id,
                      'event_id': self.schedule['id']}
            self.http.request('/manager/register_visit/', params)
            default_response = None
            response = self.http.parse(default_response)
            if response:
                message = _('The client is registered on this event.')
            else:
                error_msg = self.http.error_msg
                message = _('Unable to register the visit!\nReason:\n%s') % error_msg
            QMessageBox.information(self, _('Client registration'), message)

    def visitEventManual(self):
        """
        Register the visit manually through searching a client.
        """

        def callback(user_id):
            self.user_id = user_id

        params = {
            'http': self.http,
            'static': self.parent.static,
            'mode': 'client',
            'apply_title': _('Register'),
            }
        self.dialog = Searching(self, params)
        self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        dlgStatus = self.dialog.exec_()

        if QDialog.Accepted == dlgStatus:
            params = {'event_id': self.schedule['id'],
                      'client_id': self.user_id}
            self.http.request('/manager/register_visit/', params)
            default_response = None
            response = self.http.parse(default_response)
            if response:
                message = _('The client is registered on this event.')
            else:
                error_msg = self.http.error_msg
                message = _('Unable to register the visit!\nReason:\n%s') % error_msg
            QMessageBox.information(self, _('Client registration'), message)

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

    def removeEvent(self):
        reply = QMessageBox.question(
            self, _('Event remove'),
            _('Are you sure to remove this event from the calendar?'),
            QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            params = {'id': self.schedule['id']}
            self.http.request('/manager/cal_event_del/', params)
            default_response = None
            response = self.http.parse(default_response)
            if response:
                index = self.comboRoom.currentIndex()
                room_id, ok = self.comboRoom.itemData(index).toInt()
                model = self.parent.schedule.model()
                model.remove(self.schedule_object, self.schedule_index, True)
                QMessageBox.information(self, _('Event removing'),
                                        _('Complete.'))
                self.accept()
            else:
                QMessageBox.information(self, _('Event removing'),
                                        _('Unable to remove this event!'))

    def fixEvent(self):
        index = self.comboFix.currentIndex()
        fix_id, ok = self.comboFix.itemData(index).toInt()

        params = {'event_id': self.schedule['id'],
                  'fix_id': fix_id}
        self.http.request('/manager/register_fix/', params)
        default_response = None
        response = self.http.parse(default_response)
        if response:
            message = _('The event has been fixed.')

            self.schedule_object.set_fixed(fix_id)
            model = self.parent.schedule.model()
            model.change(self.schedule_object, self.schedule_index)
            self.buttonFix.setDisabled(True)
        else:
            message = _('Unable to fix this event.')
        QMessageBox.information(self, _('Event fix registration'), message)

    def changeCoaches(self):

        def coaches_callback(coach_id_list):
            from library import dictlist_keyval
            # get the coach descriptions' list using its id list
            coaches_dictlist = dictlist_keyval(self.parent.static['coaches'], 'id', coach_id_list)
            self.schedule_object.set_coaches(coaches_dictlist)

        dialog = ShowCoaches(self, {'http': self.http})
        dialog.setCallback(coaches_callback)
        dialog.setModal(True)
        dialog.initData(self.schedule)
        dialog.exec_()

        # update the dialog's info
        self.initData(self.schedule_object, self.schedule_index)

        # update schedule model to immediate refresh this event
        model = self.parent.schedule.model()
        model.change(self.schedule_object, self.schedule_index)
