#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import sys, re, time
from datetime import datetime, timedelta

from http_ajax import HttpAjax
from rfid import WaitingRFID
from event_storage import Event, EventStorage
from qtschedule import QtScheduleDelegate, QtSchedule
from courses_tree import TreeItem, TreeModel, CoursesTree

from dlg_settings import DlgSettings
from dlg_waiting_rfid import DlgWaitingRFID

from PyQt4.QtGui import *
from PyQt4.QtCore import *

waiting = True

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        self.createMenus()
        self.setupViews()

        self.mimes = {'course': 'application/x-course-item',
                      'event':  'application/x-calendar-event',
                      }

        self.setWindowTitle(self.tr('Manager\'s interface'))
        self.statusBar().showMessage(self.tr('Ready'))
        self.resize(640, 480)

    def setupViews(self):
        self.tree = self.initCourses()
        self.schedule = QtSchedule((8, 23), timedelta(minutes=30), self)

        splitter = QSplitter()
        splitter.addWidget(self.tree)
        splitter.addWidget(self.schedule)

        self.setCentralWidget(splitter)

    def initCourses(self):
        ajax = HttpAjax(self, '/manager/get_course_tree/', {})
        json_like = ajax.parse_json()
        self.model = TreeModel(json_like)
        tree = CoursesTree(self)
        tree.setModel(self.model)
        return tree

    def getMime(self, name):
        return self.mimes.get(name, None)

    def getRooms(self):
        ajax = HttpAjax(self, '/manager/get_rooms/', {})
        json_like = ajax.parse_json()
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
            (self.tr('&Tools'), [
                    (self.tr('Application settings'), self.tr('Ctrl+T'),
                     'setupApp', self.tr('Manage the application settings.')),
                    (self.tr('Test'), self.tr('Ctrl+T'),
                     'test', self.tr('Test')),
                    ]
             ),
            (self.tr('&Mode'), [
                    (self.tr('Wait for RFID'), self.tr('Ctrl+R'),
                     'waitingRFID', self.tr('Enable RFID reader and wait for a RFID id.')),
                    ]
             )
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

    def setupApp(self):
        # подготовить диалог
        self.dialog = DlgSettings(self)
        self.dialog.setModal(True)
        # показать диалог
        self.dialog.exec_()

    def test(self):
        print 'test test test'

    def waitingRFID(self):
        """ Обработчик меню. Отображает диалог и запускает поток обработки
        данных RFID считывателя. """
        self.callback = self.readedRFID
        # подготовить диалог
        self.dialog = DlgWaitingRFID(self)
        self.dialog.setModal(True)
        # показать диалог
        self.dialog.exec_()

    def readedRFID(self, rfid):
        """ Callback функция, вызывается из потока RFID считывателя, получая
        идентификатор карты. """
        self.rfid_id = rfid
        print 'readedRFID:', rfid
        self.getUserInfo(rfid)

    # Обработчики меню: конец

    def getUserInfo(self, rfid):
        """ Метод для получения информации о пользователе по идентификатору
        его карты. """
        ajax = HttpAjax(self, '/manager/user_info/', {'rfid_code': rfid})
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
