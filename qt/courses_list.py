#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class CourseListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        # хранилище данных модели
        self.storage = []
        # хранилище временных данных, т.е. назначенные, но ещё не
        # подтверждённые курсы
        self.temporary = []

        self.labels = [self.tr('Title'), self.tr('Price'),
                       self.tr('Assigned'), self.tr('Used'),
                       self.tr('Bought'), self.tr('State'),
                       self.tr('When')]

    def initData(self, data):
        """
        Формат полученных данных:
        [{id, course_id, title, price,
          count_sold, count_used,
          reg_date, exp_date, cnl_date},
          ...
          ]
        """
        order = ['id', 'course_id', 'title', 'price',
                 'count_sold', 'count_used',
                 'reg_date', 'exp_date', 'cnl_date']
        for rec in data:
            if type(rec) is not dict:
                raise 'Check format'
            row = (rec['id'], rec['course_id'],
                   rec['title'], rec['price'],
                   rec['count_sold'], rec['count_used'],
                   rec['reg_date'], rec['exp_date'],
                   rec['cnl_date'])
            self.storage.append(row)

    def rowCount(self, parent): # base class method
        if parent.isValid():
            return 0
        else:
            return len(self.storage)

    def columnCount(self, parent):# base class method
        if parent.isValid():
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
            row = self.storage[index.row()]
            item = row[index.column()+2]
            return QVariant(item)
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            from  datetime import datetime, timedelta
            now = datetime.now()
            day30 = timedelta(days=30)
            print value
            title, course_id, count, price, coaches, duration = value
            # to: id, course_id, title, price, cnt1, cnt2, dates(3)
            row = (0, course_id, title, price, count, 0, now, now+day30, None)
            self.storage[-1] = row
            self.temporary.append(row)
            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                      index, index)
            return True
        return False

    def insertRows(self, position, rows, parent):
        self.beginInsertRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            print 'storage len is', len(self.storage)
            self.storage.append( tuple() )
            print 'storage len is', len(self.storage)

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
