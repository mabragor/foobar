#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re, time
from datetime import datetime, timedelta

from os.path import dirname, join

from settings import _, DEBUG
from http import Http
from event_storage import Event
from qtschedule import QtSchedule

from team_tree import TreeModel

from dlg_settings import DlgSettings
from dlg_login import DlgLogin
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_searching import DlgSearchByName
from dlg_user_info import DlgClientInfo, DlgRenterInfo
from dlg_event_assign import DlgEventAssign
from dlg_event_info import DlgEventInfo
from dlg_copy_week import DlgCopyWeek
from dlg_accounting import DlgAccounting

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
	QMainWindow.__init__(self, parent)

	self.mimes = {'team': 'application/x-team-item',
		      'event':  'application/x-calendar-event',
		      }
        self.rooms = []
        self.tree = []
        self.rfid_id = None

        self.http = Http(self)

        self.work_hours = (8, 24)
        self.schedule_quant = timedelta(minutes=30)

        self.menus = []
	self.create_menus()
	self.setup_views()

        settings = QSettings()
        settings.beginGroup('network')
        host = settings.value('addressHttpServer', QVariant('WrongHost'))
        settings.endGroup()

        if 'WrongHost' == host.toString():
            self.setupApp()

        self.baseTitle = _('Manager\'s interface')
	self.logoutTitle()
	self.statusBar().showMessage(_('Ready'), 2000)
	self.resize(640, 480)

    def loggedTitle(self, name):
	self.setWindowTitle('%s : %s' % (self.baseTitle, name))

    def logoutTitle(self):
	self.setWindowTitle('%s : %s' % (self.baseTitle, _('Login to start session')))

    def get_dynamic(self):
        self.schedule.model().update()

        self.bpMonday.setText(self.schedule.model().getMonday().strftime('%d/%m/%Y'))
        self.bpSunday.setText(self.schedule.model().getSunday().strftime('%d/%m/%Y'))

    def get_static(self):
        """ This methods get static information from server. """
        # get rooms
        self.http.request('/manager/get_rooms/', {})
        default_response = {'rows': []}
        response = self.http.parse(default_response)
	"""
	{'rows': [{'color': 'FFAAAA', 'text': 'red', 'id': 1},
		  {'color': 'AAFFAA', 'text': 'green', 'id': 2},
		  ...]}
	"""
        self.rooms = tuple( [ (a['title'], a['color'], a['id']) for a in response['rows'] ] )
        self.schedule.update_static( {'rooms': self.rooms} )

        # available teams
        self.http.request('/manager/available_teams/', {})
        response = self.http.parse() # see format at team_tree.py
        self.tree = TreeModel(response)


    def update_interface(self):
        """ This method updates application's interface using static
        information obtained in previous method. """
        # rooms
        if self.rooms and len(self.rooms) > 0:
            for title, color, id in self.rooms:
                buttonFilter = QPushButton(title)
                buttonFilter.setCheckable(True)
                buttonFilter.setDisabled(True) # BUG #28
                self.panelRooms.addWidget(buttonFilter)
                self.connect(buttonFilter, SIGNAL('clicked()'),
                             self.prepare_filter(id, title))


    def prepare_filter(self, id, title):
        def handler():
            self.statusBar().showMessage(_('Filter: Room "%s" is changed its state') % title)
        return handler

    def setup_views(self):
        self.panelRooms = QHBoxLayout()

        schedule_params = {
            'http': self.http,
            'work_hours': self.work_hours,
            'quant': self.schedule_quant,
            'rooms': self.rooms,
            }
	self.schedule = QtSchedule(self, schedule_params)

        self.bpMonday = QLabel('--/--/----')
        self.bpSunday = QLabel('--/--/----')
        self.buttonPrev = QPushButton(_('<<'))
        self.buttonNext = QPushButton(_('>>'))
        self.buttonToday = QPushButton(_('Today'))
        self.buttonPrev.setDisabled(True)
        self.buttonNext.setDisabled(True)
        self.buttonToday.setDisabled(True)

        # callback helper function
        def prev_week():
            week_range = self.schedule.model().showPrevWeek()
            self.showWeekRange(week_range)
        def next_week():
            week_range = self.schedule.model().showNextWeek()
            self.showWeekRange(week_range)
        def today():
            week_range = self.schedule.model().showCurrWeek()
            self.showWeekRange(week_range)

        self.connect(self.buttonPrev, SIGNAL('clicked()'), prev_week)
        self.connect(self.buttonNext, SIGNAL('clicked()'), next_week)
        self.connect(self.buttonToday, SIGNAL('clicked()'), today)

        bottomPanel = QHBoxLayout()
        bottomPanel.addWidget(QLabel(_('Week:')))
        bottomPanel.addWidget(self.bpMonday)
        bottomPanel.addWidget(QLabel('-'))
        bottomPanel.addWidget(self.bpSunday)
        bottomPanel.addStretch(1)
        bottomPanel.addWidget(self.buttonPrev)
        bottomPanel.addWidget(self.buttonToday)
        bottomPanel.addWidget(self.buttonNext)

        mainLayout = QVBoxLayout()
        mainLayout.addLayout(self.panelRooms)
        mainLayout.addWidget(self.schedule)
        mainLayout.addLayout(bottomPanel)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

	self.setCentralWidget(mainWidget)

    def showWeekRange(self, week_range):
        if self.schedule.model().getShowMode() == 'week':
            monday, sunday = week_range
            self.bpMonday.setText(monday.strftime('%d/%m/%Y'))
            self.bpSunday.setText(sunday.strftime('%d/%m/%Y'))

    def getMime(self, name):
	return self.mimes.get(name, None)

    def create_menus(self):
	""" Метод для генерации меню приложения. """
	""" Использование: Описать меню со всеми действиями в блоке
	data. Создать обработчики для каждого действия. """
	data = [
	    (_('File'), [
		    (_('Log in'), 'Ctrl+I',
		     'login', _('Start user session.')),
		    (_('Log out'), '',
		     'logout', _('End user session.')),
                    (None, None, None, None),
		    (_('Application settings'), 'Ctrl+G',
		     'setupApp', _('Manage the application settings.')),
                    (None, None, None, None),
		    (_('Exit'), '',
		     'close', _('Close the application.')),
		    ]
	     ),
	    (_('Client'), [
		    (_('New'), 'Ctrl+N',
		     'client_new', _('Register new client.')),
		    (_('Search by RFID'), 'Ctrl+D',
		     'client_search_rfid', _('Search a client with its RFID card.')),
		    (_('Search by name'), 'Ctrl+F',
		     'clientSearchName', _('Search a client with its name.')),
		    ]
	     ),
	    (_('Renter'), [
		    (_('New'), '',
		     'renterNew', _('Register new renter.')),
		    (_('Search by name'), '',
		     'renterSearchName', _('Search a renter with its name.')),
		    ]
	     ),
# 	    (_('Event'), [
# 		    (_('Training'), 'Ctrl+T',
# 		     'eventTraining', _('Assign a training event.')),
# 		    (_('Rent'), 'Ctrl+R',
# 		     'eventRent', _('Assign a rent event.')),
#                     ]
#              ),
	    (_('Calendar'), [
		    (_('Fill week'), 'Ctrl+L',
		     'fillWeek', _('Fill current week.')),
# 		    (_('Copy week'), 'Ctrl+W',
# 		     'copyWeek', _('Copy current week into other.')),
                    ]
             ),
# 	    (_('Accounting'), [
# 		    (_('Add resources'), '',
# 		     'addResources', _('Add new set of resources into accounting.')),
#                     ]
#              ),
	    ]


	for topic, info in data:
	    menu = self.menuBar().addMenu(topic)
            # Отключаем элементы меню, надо войти в систему
            if topic != _('File'):
                menu.setDisabled(True)
	    for title, short, name, desc in info:
                if not title:
                    menu.addSeparator()
                    continue
		setattr(self, 'act_%s' % name, QAction(title, self))
		action = getattr(self, 'act_%s' % name)
		action.setShortcut(short)
		action.setStatusTip(desc)
		self.connect(action, SIGNAL('triggered()'), getattr(self, name))
		menu.addAction(action)
            self.menus.append(menu)

    def activate_interface(self):
        # Активировать элементы меню
        for menu in self.menus:
            menu.setDisabled(False)
        # Активировать кнопки навигации
        self.buttonPrev.setDisabled(False)
        self.buttonNext.setDisabled(False)
        self.buttonToday.setDisabled(False)

    def refresh_data(self):
        """ Метод для получения данных от сервера. Вызывается
        периодически с помощью таймера."""
        # если пользователь не аутентифицирован, ничего не делаем
        if not self.http.is_session_open():
            return
        # пока обновляем только модель календаря
        self.schedule.model().update

    # Обработчики меню: начало

    def login(self):
	def callback(credentials):
	    self.credentials = credentials

	self.dialog = DlgLogin(self)
	self.dialog.setCallback(callback)
	self.dialog.setModal(True)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
            self.http.request('/manager/login/', self.credentials)
            default_response = None
	    response = self.http.parse(default_response)
            if response and 'user_info' in response:
                self.loggedTitle(response['user_info'])

                # update application's interface
                self.get_static()
                self.get_dynamic()
                self.update_interface()

                self.schedule.model().showCurrWeek()

                # run refresh timer
                self.refreshTimer = QTimer(self)
                from settings import SCHEDULE_REFRESH_TIMEOUT
                self.refreshTimer.setInterval(SCHEDULE_REFRESH_TIMEOUT)
                self.connect(self.refreshTimer, SIGNAL('timeout()'), self.refresh_data)
                self.refreshTimer.start()

                self.activate_interface() # CHECK THIS
        else:
            QMessageBox.warning(self, _('Login failed'),
                                _('It seems you\'ve entered wrong login/password.'))

    def logout(self):
        # Деактивировать элементы меню
        for menu in self.menus[1:]:
            menu.setDisabled(True)
        self.setWindowTitle('%s : %s' % (self.baseTitle, _('Login to start session')))
        self.schedule.model().storage.init()

    def setupApp(self):
	self.dialog = DlgSettings(self)
	self.dialog.setModal(True)
	self.dialog.exec_()
        self.get_dynamic()

    def client_new(self):
        self.dialog = DlgClientInfo(self, {'http': self.http})
	self.dialog.setModal(True)
	self.dialog.exec_()

    def client_search_rfid(self):
	def callback(rfid):
	    self.rfid_id = rfid

	self.callback = callback
	self.dialog = DlgWaitingRFID(self)
	self.dialog.setModal(True)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus and self.rfid_id is not None:
	    self.http.request('/manager/get_client_info/',
                              {'rfid_code': self.rfid_id,
                               'mode': 'client'})
            default_response = None
	    response = self.http.parse(default_response)
            if not response or response['info'] is None:
                QMessageBox.warning(self, _('Warning'),
                                    _('This RFID belongs to nobody.'))
            else:
                self.dialog = DlgClientInfo(self)
                self.dialog.setModal(True)
                self.dialog.initData(response['info'])
                self.dialog.exec_()
                self.rfid_id = None

    def clientSearchName(self):
	def callback(user_id):
	    self.user_id = user_id

	self.dialog = DlgSearchByName('client', self)
	self.dialog.setModal(True)
	self.dialog.setCallback(callback)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
	    ajax = HttpAjax(self, '/manager/get_client_info/',
			    {'user_id': self.user_id,
                             'mode': 'client'}, self.session_id)
	    response = ajax.parse_json()
	    self.dialog = DlgClientInfo(self)
	    self.dialog.setModal(True)
	    self.dialog.initData(response['info'])
	    self.dialog.exec_()

    def renterNew(self):
	self.dialog = DlgRenterInfo(self)
	self.dialog.setModal(True)
	self.dialog.exec_()

    def renterSearchName(self):
	def callback(id):
	    self.user_id = id

	self.dialog = DlgSearchByName('renter', self)
	self.dialog.setModal(True)
	self.dialog.setCallback(callback)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
	    ajax = HttpAjax(self, '/manager/get_renter_info/',
			    {'user_id': self.user_id,
                             'mode': 'renter'}, self.session_id)
	    response = ajax.parse_json()
	    self.dialog = DlgRenterInfo(self)
	    self.dialog.setModal(True)
	    self.dialog.initData(response['info'])
	    self.dialog.exec_()

    def eventTraining(self):
        def callback(e_date, e_time, room_tuple, team):
            room, ok = room_tuple
            title, team_id, count, price, coach, duration = team
            begin = datetime.combine(e_date, e_time)
            duration = timedelta(minutes=int(duration * 60))

            ajax = HttpAjax(self, '/manager/cal_event_add/',
                            {'event_id': team_id,
                             'room_id': room,
                             'begin': begin,
                             'ev_type': 0}, self.session_id)
            response = ajax.parse_json()
            id = int(response['saved_id'])
            event_info = {'id': id,
                          'title': title, 'price': price,
                          'count': count, 'coach': coach,
                          'duration': duration,
                          'groups': _('Waiting for update.')}
            eventObj = Event({}) # FIXME
            self.schedule.insertEvent(room, eventObj)

	self.dialog = DlgEventAssign('training', self)
	self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.setModel(self.tree)
        self.dialog.setRooms(self.rooms)
	self.dialog.exec_()

    def eventRent(self):
        def callback(e_date, e_time, e_duration, room_tuple, rent):
            room, ok = room_tuple
            rent_id = rent['id']
            begin = datetime.combine(e_date, e_time)
            duration = timedelta(hours=e_duration.hour,
                                 minutes=e_duration.minute)
            params = {
                'event_id': rent_id,
                'room_id': room,
                'begin': begin,
                'ev_type': 1,
                'duration': float(duration.seconds) / 3600
                }
            ajax = HttpAjax(self, '/manager/cal_event_add/', params, self.session_id)
            response = ajax.parse_json()
            id = int(response['saved_id'])
            eventObj = Event({}) # FIXME
            self.schedule.insertEvent(room, eventObj)
	self.dialog = DlgEventAssign('rent', self)
	self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.setRooms(self.rooms)
	self.dialog.exec_()

    def fillWeek(self):
        def callback(selected_date):
            model = self.schedule.model()
            from_range = model.weekRange
            to_range = model.date2range(selected_date)

            self.http.request('/manager/fill_week/', {'to_date': to_range[0]})
            default_response = None
            response = self.http.parse(default_response)
            if response and 'saved_id' in response:
                # inform user
                info = response['saved_id']
                msg = _('The week has been filled sucessfully. Copied: %(copied)i. Passed: %(passed)i.')
                self.statusBar().showMessage(msg % info)
                # FIXME: pause here, but not just sleep, use timer
                # update view
                self.schedule.model().update()

	self.dialog = DlgCopyWeek(self)
	self.dialog.setModal(True)
        self.dialog.setCallback(callback)
	self.dialog.exec_()

    def copyWeek(self):
        def callback(selected_date):
            model = self.scheduleModel
            from_range = model.weekRange
            to_range = model.date2range(selected_date)
            ajax = HttpAjax(self, '/manager/copy_week/',
                            {'from_date': from_range[0],
                             'to_date': to_range[0]}, self.session_id)
            response = ajax.parse_json()
            self.statusBar().showMessage(_('The week has been copied sucessfully.'))

	self.dialog = DlgCopyWeek(self)
	self.dialog.setModal(True)
        self.dialog.setCallback(callback)
	self.dialog.exec_()

    def addResources(self):
        def callback(count, price):
#             ajax = HttpAjax(self, '/manager/add_resource/',
#                             {'from_date': from_range[0],
#                              'to_date': to_range[0]}, self.session_id)
            response = ajax.parse_json()
            self.statusBar().showMessage(_('The week has been copied sucessfully.'))

	self.dialog = DlgAccounting(self)
	self.dialog.setModal(True)
        self.dialog.setCallback(callback)
	self.dialog.exec_()

    # Обработчики меню: конец

#     def getUserInfo(self, rfid):
# 	""" Метод для получения информации о пользователе по идентификатору
# 	его карты. """
# 	ajax = HttpAjax(self, '/manager/get_client_info/',
# 			{'rfid_code': rfid, mode='client'})
# 	json_like = ajax.parse_json()
# 	print 'USER INFO:', json_like
# 	return json_like

    def showEventProperties(self, calendar_event): #, room_id):
        self.dialog = DlgEventInfo(self, {'http': self.http})
	self.dialog.setModal(True)
        self.dialog.initData(calendar_event)
	self.dialog.exec_()

    # Drag'n'Drop section begins
    def mousePressEvent(self, event):
        if DEBUG:
            print 'press event', event.button()

    def mouseMoveEvent(self, event):
        if DEBUG:
            print 'move event', event.pos()
    # Drag'n'Drop section ends


if __name__=="__main__":

    def readStyleSheet(fileName) :
        css = QString()
        file = QFile(join(dirname(__file__), fileName))
        if file.open(QIODevice.ReadOnly) :
                css = QString(file.readAll())
                file.close()
        return css

    # глобальные параметры настроек приложения
    QCoreApplication.setOrganizationName('Home, Sweet Home')
    QCoreApplication.setOrganizationDomain('snegiri.dontexist.org')
    QCoreApplication.setApplicationName('foobar')
    QCoreApplication.setApplicationVersion('0.1')

    app = QApplication(sys.argv)
    app.setStyleSheet(readStyleSheet('manager.css'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
