#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class DlgCourseAssign(QDialog):

    def __init__(self, room_list, parent=None):
        QDialog.__init__(self, parent)

        self.room_list = room_list
        print room_list

        self.weekDayLabel = QLabel(self.tr('Day of week'))
        self.weekDayList = QListView()

        self.dayTimeLabel = QLabel(self.tr('Time'))
        self.dayTimeList = QListView()

        self.roomListLabel = QLabel(self.tr('Rooms'))
        self.roomListList = QListWidget()
        rooms = QStringList()
        for data in room_list:
            rooms.append(data['text'])
        self.roomListList.insertItems(0, rooms)

        layout = QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        layout.addWidget(self.weekDayLabel, 0, 0)
        layout.addWidget(self.weekDayList, 1, 0)
        layout.addWidget(self.dayTimeLabel, 0, 1)
        layout.addWidget(self.dayTimeList, 1, 1)
        layout.addWidget(self.roomListLabel, 0, 2)
        layout.addWidget(self.roomListList, 1, 2)

        self.setLayout(layout)
        self.setWindowTitle(self.tr('Place the course'))

