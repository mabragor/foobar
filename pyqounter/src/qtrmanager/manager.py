#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009-2010 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re, time
from datetime import datetime, timedelta

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from http_ajax import HttpAjax
from event_storage import EventTraining, EventRent, EventStorage
from qtschedule import QtScheduleDelegate, QtSchedule

from courses_tree import CoursesTree, TreeModel

from dlg_settings import DlgSettings
from dlg_login import DlgLogin
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_searching import DlgSearchByName
from dlg_user_info import DlgClientInfo, DlgRenterInfo
from dlg_event_assign import DlgEventAssign
from dlg_event_info import DlgEventInfo
from dlg_copy_week import DlgCopyWeek

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
	QMainWindow.__init__(self, parent)

        self.session_id = None

	self.mimes = {'course': 'application/x-course-item',
		      'event':  'application/x-calendar-event',
		      }
        self.rooms = []
        self.tree = []

	self.createMenus()
	self.setupViews()

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

        # start here event loading thread
        self.loadInitialData()

    def loggedTitle(self, name):
	self.setWindowTitle('%s : %s' % (self.baseTitle, name))

    def logoutTitle(self):
	self.setWindowTitle('%s : %s' % (self.baseTitle, _('Login to start session')))

    def prepareFilter(self, id, title):
        def handler():
            self.statusBar().showMessage(_('Filter: Room "%s" is changed its state') % title)
        return handler

    def setupViews(self):
        self.rooms = tuple( [ (a['title'], a['color'], a['id']) for a in self.getRooms()['rows'] ] )

	self.schedule = QtSchedule((8, 24), timedelta(minutes=30), self.rooms, self)

        headerPanel = QHBoxLayout()
        if self.rooms and len(self.rooms) > 0:
            for title, color, id in self.rooms:
                buttonFilter = QPushButton(title)
                buttonFilter.setCheckable(True)
                headerPanel.addWidget(buttonFilter)
                self.connect(buttonFilter, SIGNAL('clicked()'),
                             self.prepareFilter(id, title))

        self.bpMonday = QLabel('--/--/----')
        self.bpSunday = QLabel('--/--/----')
        self.buttonPrev = QPushButton(_('<<'))
        self.buttonNext = QPushButton(_('>>'))
        self.buttonToday = QPushButton(_('Today'))

        # callback helper function
        def prev_week():
            week_range = self.scheduleModel.showPrevWeek()
            self.showWeekRange(week_range)
        def next_week():
            week_range = self.scheduleModel.showNextWeek()
            self.showWeekRange(week_range)
        def today():
            week_range = self.scheduleModel.showCurrWeek()
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
        mainLayout.addLayout(headerPanel)
        mainLayout.addWidget(self.schedule)
        mainLayout.addLayout(bottomPanel)

        mainWidget = QWidget()
        mainWidget.setLayout(mainLayout)

	self.setCentralWidget(mainWidget)

    def loadInitialData(self):
        #self.tree = self.getCoursesTree()
        self.scheduleModel = EventStorage(
            (8, 24), timedelta(minutes=30), self.rooms, self
            )
        self.schedule.setModel(self.scheduleModel)
        self.bpMonday.setText(self.scheduleModel.getMonday().strftime('%d/%m/%Y'))
        self.bpSunday.setText(self.scheduleModel.getSunday().strftime('%d/%m/%Y'))

    def showWeekRange(self, week_range):
        monday, sunday = week_range
        self.bpMonday.setText(monday.strftime('%d/%m/%Y'))
        self.bpSunday.setText(sunday.strftime('%d/%m/%Y'))

    def getMime(self, name):
	return self.mimes.get(name, None)

    def getRooms(self):
	ajax = HttpAjax(self, '/manager/get_rooms/', {}, self.session_id)
	if ajax:
	    json_like = ajax.parse_json()
	else:
	    json_like = {'rows': []}
	"""
	{'rows': [{'color': 'FFAAAA', 'text': 'red', 'id': 1},
		  {'color': 'AAFFAA', 'text': 'green', 'id': 2},
		  ...]}
	"""
	return json_like

    def getCoursesTree(self):
	ajax = HttpAjax(self, '/manager/available_courses/', {}, self.session_id)
	response = ajax.parse_json() # see format at courses_tree.py
	return TreeModel(response)

    def createMenus(self):
	""" Метод для генерации меню приложения. """
	""" Использование: Описать меню со всеми действиями в блоке
	data. Создать обработчики для каждого действия. """
	data = [
	    (_('File'), [
		    (_('Log in'), '',
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
		     'clientNew', _('Register new client.')),
		    (_('Search by RFID'), 'Ctrl+D',
		     'clientSearchRFID', _('Search a client with its RFID card.')),
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
	    (_('Event'), [
		    (_('Training'), 'Ctrl+T',
		     'eventTraining', _('Assign a training event.')),
		    (_('Rent'), 'Ctrl+R',
		     'eventRent', _('Assign a rent event.')),
                    ]
             ),
	    (_('Calendar'), [
		    (_('Copy week'), 'Ctrl+W',
		     'copyWeek', _('Copy current week into other.')),
                    ]
             ),
	    ]

	for topic, info in data:
	    self.menu = self.menuBar().addMenu(topic)
	    for title, short, name, desc in info:
                if not title:
                    self.menu.addSeparator()
                    continue
		setattr(self, 'act_%s' % name, QAction(title, self))
		action = getattr(self, 'act_%s' % name)
		action.setShortcut(short)
		action.setStatusTip(desc)
		self.connect(action, SIGNAL('triggered()'), getattr(self, name))
		self.menu.addAction(action)

    def setSessionID(self, id):
        self.session_id = id

    # Обработчики меню: начало

    def login(self):
	def callback(login, password):
	    self.login = login
            self.password = password

	self.dialog = DlgLogin(self)
	self.dialog.setCallback(callback)
	self.dialog.setModal(True)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
            print 'may login', self.login, self.password
            params = {'login': self.login,
                      'password': self.password}
	    ajax = HttpAjax(self, '/manager/login/',
                            params, self.session_id)
	    response = ajax.parse_json()
            if 'user_info' in response:
                self.loggedTitle(response['user_info'])
                self.tree = self.getCoursesTree()
                self.scheduleModel.showCurrWeek()
        else:
            print 'rejected'

    def logout(self):
        self.session_id = None
        self.setWindowTitle('%s : %s' % (self.baseTitle, _('Login to start session')))
        self.scheduleModel.initModel()

    def setupApp(self):
	self.dialog = DlgSettings(self)
	self.dialog.setModal(True)
	self.dialog.exec_()
        self.loadInitialData()

    def clientNew(self):
	print 'register new client'
	self.dialog = DlgClientInfo(self)
	self.dialog.setModal(True)
	self.dialog.exec_()

    def clientSearchRFID(self):
	print 'search client by its rfid'
	def callback(rfid):
	    self.rfid_id = rfid

	self.callback = callback
	self.dialog = DlgWaitingRFID(self)
	self.dialog.setModal(True)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
	    ajax = HttpAjax(self, '/manager/get_client_info/',
			    {'rfid_code': self.rfid_id,
                             'mode': 'client'}, self.session_id)
	    response = ajax.parse_json()
	    self.dialog = DlgClientInfo(self)
	    self.dialog.setModal(True)
	    self.dialog.initData(response['info'])
	    self.dialog.exec_()
	else:
	    print 'dialog was rejected'

    def clientSearchName(self):
	print 'search client by its name'
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
	else:
	    print 'dialog was rejected'

    def renterNew(self):
	print 'register new renter'
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
	else:
	    print 'dialog was rejected'

    def eventTraining(self):
        def callback(e_date, e_time, room_tuple, course):
            room, ok = room_tuple
            title, course_id, count, price, coaches, duration = course
            begin = datetime.combine(e_date, e_time)
            duration = timedelta(minutes=int(duration * 60))

            ajax = HttpAjax(self, '/manager/cal_event_add/',
                            {'event_id': course_id,
                             'room_id': room,
                             'begin': begin,
                             'ev_type': 0}, self.session_id)
            response = ajax.parse_json()
            id = int(response['saved_id'])
            event = EventTraining(course, id, begin, duration, 0)
            self.schedule.insertEvent(room, event)

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
            event = EventRent(rent_id, id, begin, duration, rent['title'])
            self.schedule.insertEvent(room, event)
	self.dialog = DlgEventAssign('rent', self)
	self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.setRooms(self.rooms)
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

    # Обработчики меню: конец

#     def getUserInfo(self, rfid):
# 	""" Метод для получения информации о пользователе по идентификатору
# 	его карты. """
# 	ajax = HttpAjax(self, '/manager/get_client_info/',
# 			{'rfid_code': rfid, mode='client'})
# 	json_like = ajax.parse_json()
# 	print 'USER INFO:', json_like
# 	return json_like

    def showEventProperties(self, calendar_event, room_id):
	self.dialog = DlgEventInfo(self)
	self.dialog.setModal(True)
        self.dialog.initData(calendar_event, room_id)
	self.dialog.exec_()

    # Drag'n'Drop section begins
    def mousePressEvent(self, event):
	print 'press event', event.button()

    def mouseMoveEvent(self, event):
	print 'move event', event.pos()
    # Drag'n'Drop section ends


if __name__=="__main__":

    def readStyleSheet(fileName) :
        css = QString()
        file = QFile(fileName)
        if file.open(QIODevice.ReadOnly) :
                css = QString(file.readAll())
                file.close()
        return css

    # глобальные параметры настроек приложения
    QCoreApplication.setOrganizationName('Home, Sweet Home')
    QCoreApplication.setOrganizationDomain('snegiri.dontexist.org')
    QCoreApplication.setApplicationName('foobar')
    QCoreApplication.setApplicationVersion('1.0')

    app = QApplication(sys.argv)
    app.setStyleSheet(readStyleSheet('manager.css'))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
