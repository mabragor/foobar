#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import time
from  datetime import datetime, timedelta

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class CourseListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        # хранилище данных модели
        self.storage = []
        # хранилище временных данных, т.е. назначенные, но ещё не
        # подтверждённые курсы
        self.temporary_assigned = []

        self.labels = [self.tr('Title'), self.tr('Price'),
                       self.tr('Sold'), self.tr('Used'),
                       self.tr('Assigned'), self.tr('State'),
                       self.tr('Till/When')]

    def str2date(self, value):
        return datetime(*time.strptime(value, '%Y-%m-%d %H:%M:%S')[:6])

    def initData(self, data):
        """
        Формат полученных данных:
        [{id, course_id, title, price,
          count_sold, count_used,
          reg_date, exp_date, cnl_date},
          ...
          ]
        """
        for rec in data:
            if type(rec) is not dict:
                raise 'Check format'
            row = (rec['id'], rec['course_id'],
                   rec['title'], rec['price'],
                   rec['count_sold'], rec['count_used'],
                   rec['reg_date'], rec['exp_date'], rec['cnl_date'])
            self.storage.append(row)

        self.emit(SIGNAL('rowsInserted(QModelIndex, int, int)'),
                  QModelIndex(), 1, self.rowCount())

#         self.emit(SIGNAL('columnsInserted(QModelIndex, int, int)'),
#                   QModelIndex(), 1, cols)
#         self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
#                   self.createIndex(0, 0),
#                   self.createIndex(self.rowCount(), self.columnCount()))

    def get_changes_and_clean(self):
        assigned = []
        cancelled = []
        changed = []
        for i in self.temporary_assigned:
            course_id = i[1]
            assigned.append(course_id)
        self.temporary_assigned = []
        return (assigned, cancelled, changed)

    def rowCount(self, parent=None): # base class method
        if parent and parent.isValid():
            return 0
        else:
            return len(self.storage)

    def columnCount(self, parent=None):# base class method
        if parent and parent.isValid():
            return 0
        else:
            return len(self.labels)

    def headerData(self, section, orientation, role): # base class method
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section+1) # порядковый номер
        return QVariant()

    def data(self, index, role): # base class method
        if not index.isValid():
            return QVariant()
        if role in (Qt.DisplayRole, Qt.ToolTipRole) :
            # source data
            id, course_id, title, price, sold, used, assign, expired, cancelled = self.storage[index.row()]

            if cancelled is not None:
                state = self.tr('Cancelled')
                till_when = cancelled
            elif self.str2date(expired) > datetime.now():
                state = self.tr('Active')
                till_when = None
            else:
                state = self.tr('Expired')
                till_when = expired
            # representation for widget
            row = (title, price, sold, used, assign, state, till_when)

            item = row[index.column()]
            return QVariant(item)
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            now = datetime.now()
            bought = now.strftime('%Y-%m-%d %H:%M:%S')
            expired = (now + timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
            title, course_id, count, price, coaches, duration = value
            row = (0, course_id, title, price, count, 0, bought, expired, None)
            self.storage[-1] = row
            self.temporary_assigned.append(row)
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                      index, index)
            return True
        return False

    def insertRows(self, position, rows, parent):
        self.beginInsertRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            self.storage.append( tuple() )

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            del(self.storage[position + i])
        self.endRemoveRows()
        return True

class CoursesList(QTableView):

    """ Класс списка курсов. """

    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.verticalHeader().stretchLastSection = True

        self.actionCourseCancel = QAction(self.tr('Cance&l course'), self)
        self.actionCourseCancel.setStatusTip(self.tr('Cancel current course.'))
        self.connect(self.actionCourseCancel, SIGNAL('triggered()'), self.courseCancel)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            index = self.indexAt(event.pos())
            print index.row()

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        print index.row()
        self.contextRow = index.row()
        menu = QMenu(self)
        menu.addAction(self.actionCourseCancel)
        menu.exec_(event.globalPos())

    def courseCancel(self):
        print 'canceled [%i]' % self.contextRow
