#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

from PyQt4.QtGui import *
from PyQt4.QtCore import *

class CourseListModel(QAbstractTableModel):

    def __init__(self, parent=None):
        QAbstractTableModel.__init__(self, parent)

        self.storage = []

        self.labels = [self.tr('Title'), self.tr('Price'),
                       self.tr('Assigned'), self.tr('Used'),
                       self.tr('Bought'), self.tr('State'),
                       self.tr('When')]

    def setData(self, data):
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
        if role == Qt.DisplayRole:
            row = self.storage[index.row()]
            item = row[index.column()+2]
            return QVariant(item)
        return QVariant()

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