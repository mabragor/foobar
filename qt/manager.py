#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re, time
from datetime import datetime, timedelta

import gettext
gettext.bindtextdomain('project', './locale/')
gettext.textdomain('project')
_ = lambda a: unicode(gettext.gettext(a), 'utf8')

from http_ajax import HttpAjax
from event_storage import Event, EventStorage
from qtschedule import QtScheduleDelegate, QtSchedule

from courses_tree import CoursesTree, TreeModel

from dlg_settings import DlgSettings
from dlg_waiting_rfid import DlgWaitingRFID
from dlg_searching import DlgSearchByName
from dlg_user_info import DlgUserInfo
from dlg_event_assign import DlgEventAssign

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
	QMainWindow.__init__(self, parent)

	self.createMenus()
	self.setupViews()

	self.mimes = {'course': 'application/x-course-item',
		      'event':  'application/x-calendar-event',
		      }

	self.setWindowTitle(_('Manager\'s interface'))
	self.statusBar().showMessage(_('Ready'))
	self.resize(640, 480)

    def setupViews(self):
	self.tree = self.initCourses()
	self.schedule = QtSchedule((8, 23), timedelta(minutes=30), self)

	splitter = QSplitter()
	splitter.addWidget(self.tree)
	splitter.addWidget(self.schedule)

	self.setCentralWidget(splitter)

    def initCourses(self):
	ajax = HttpAjax(self, '/manager/available_courses/', {})
	json_like = ajax.parse_json() # see format at courses_tree.py
	self.modelCoursesTree = TreeModel(json_like)
	tree = CoursesTree(self)
	tree.setModel(self.modelCoursesTree)
	return tree

    def getMime(self, name):
	return self.mimes.get(name, None)

    def getRooms(self):
	ajax = HttpAjax(self, '/manager/get_rooms/', {})
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

    def createMenus(self):
	""" Метод для генерации меню приложения. """
	""" Использование: Описать меню со всеми действиями в блоке
	data. Создать обработчики для каждого действия. """
	data = [
	    (_('File'), [
		    (_('Exit'), '',
		     'close', _('Close the application.')),
		    ]
	     ),
	    (_('Client'), [
		    (_('New'), 'Ctrl+N',
		     'clientNew', _('Register new client.')),
		    (_('Search by RFID'), 'Ctrl+R',
		     'clientSearchRFID', _('Search a client with its RFID card.')),
		    (_('Search by name'), 'Ctrl+F',
		     'clientSearchName', _('Search a client with its name.')),
		    (_('One visit'), '',
		     'clientOneVisit', _('One visit client.')),
		    ]
	     ),
	    (_('Event'), [
		    (_('Assign'), 'Ctrl+E',
		     'eventAssign', _('Assign event.')),
                    ]
             ),
	    (_('Tools'), [
		    (_('Application settings'), 'Ctrl+T',
		     'setupApp', _('Manage the application settings.')),
		    (_('Test'), 'Ctrl+Z',
		     'test', _('Test')),
		    ]
	     ),
	    ]

	for topic, info in data:
	    self.toolsMenu = self.menuBar().addMenu(topic)
	    for title, short, name, desc in info:
		setattr(self, 'act_%s' % name, QAction(title, self))
		action = getattr(self, 'act_%s' % name)
		action.setShortcut(short)
		action.setStatusTip(desc)
		self.connect(action, SIGNAL('triggered()'), getattr(self, name))
		self.toolsMenu.addAction(action)

    # Обработчики меню: начало

    def clientNew(self):
	print 'register new client'
	self.dialog = DlgUserInfo(self)
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
	    ajax = HttpAjax(self, '/manager/get_user_info/',
			    {'rfid_code': self.rfid_id})
	    json_like = ajax.parse_json()
	    self.dialog = DlgUserInfo(self)
	    self.dialog.setModal(True)
	    self.dialog.initData(json_like)
	    self.dialog.exec_()
	else:
	    print 'dialog was rejected'

    def clientSearchName(self):
	print 'search client by its name'
	def callback(rfid):
	    self.rfid_id = rfid

	self.dialog = DlgSearchByName(self)
	self.dialog.setModal(True)
	self.dialog.setCallback(callback)
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
	    ajax = HttpAjax(self, '/manager/get_user_info/',
			    {'rfid_code': self.rfid_id})
	    json_like = ajax.parse_json()
	    self.dialog = DlgUserInfo(self)
	    self.dialog.setModal(True)
	    self.dialog.initData(json_like)
	    self.dialog.exec_()
	else:
	    print 'dialog was rejected'

    def clientOneVisit(self):
	print 'one visit client'

    def eventAssign(self):
        def callback(e_date, e_time, room_tuple, course):
            print e_date, e_time, room, course
            print type(e_date), type(e_time)
            room, ok = room_tuple
            title = course[0]
            begin = datetime.combine(e_date, e_time)
            duration = timedelta(minutes=int(course[5] * 60))
            event = Event(begin, duration, title)
            self.schedule.insertEvent(room, event)

	self.dialog = DlgEventAssign(self)
	self.dialog.setModal(True)
        self.dialog.setCallback(callback)
        self.dialog.setModel(self.modelCoursesTree)
        self.dialog.setRooms(self.getRooms()['rows'])
	dlgStatus = self.dialog.exec_()

	if QDialog.Accepted == dlgStatus:
            print 'accept'
        else:
            print 'reject'

    def setupApp(self):
	# подготовить диалог
	self.dialog = DlgSettings(self)
	self.dialog.setModal(True)
	# показать диалог
	self.dialog.exec_()

    def test(self):
	self.dialog = DlgUserInfo(self)
	self.dialog.setModal(True)
	self.dialog.exec_()

    # Обработчики меню: конец

    def getUserInfo(self, rfid):
	""" Метод для получения информации о пользователе по идентификатору
	его карты. """
	ajax = HttpAjax(self, '/manager/get_user_info/',
			{'rfid_code': rfid})
	json_like = ajax.parse_json()
	print 'USER INFO:', json_like
	return json_like

    # Drag'n'Drop section begins
    def mousePressEvent(self, event):
	print 'press event', event.button()

    def mouseMoveEvent(self, event):
	print 'move event', event.pos()
    # Drag'n'Drop section ends


if __name__=="__main__":

    # глобальные параметры настроек приложения
    QCoreApplication.setOrganizationName('Home, Sweet Home')
    QCoreApplication.setOrganizationDomain('snegiri.dontexist.org')
    QCoreApplication.setApplicationName('foobar')
    QCoreApplication.setApplicationVersion('1.0')

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
