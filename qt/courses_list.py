# -*- coding: utf-8 -*-
# (c) 2009 Ruslan Popov <ruslan.popov@gmail.com>

import time
from  datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta

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
                       self.tr('Card'),
                       self.tr('Sold'), self.tr('Used'),
                       self.tr('Assigned'), self.tr('Begin'),
                       self.tr('Expired'), self.tr('Cancelled'),
                       'id', 'course_id']
        self.model_fields = ['title', 'price', 'card_type', 'count_sold', 'count_used',
                             'reg_date', 'bgn_date', 'exp_date', 'cnl_date',
                             'id', 'course_id']

    def initData(self, data):
        """
        Формат полученных данных:
        [{id, course_id, title, price, card_type,
          count_sold, count_used,
          reg_date, exp_date, cnl_date},
          ...
          ]
        """
        for rec in data:
            if type(rec) is not dict:
                raise 'Check format'
            row = []
            for i in self.model_fields: # reorder items
                row.append(rec[i])
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
            obj = self.model_fields
            index_course_id = obj.index('course_id')
            course_id = i[index_course_id]
            index_card_type = obj.index('card_type')
            card_type = i[index_card_type]
            index_bgn_date = obj.index('bgn_date')
            bgn_date = i[index_bgn_date]
            assigned.append( (course_id, card_type, unicode(bgn_date)) )
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
            return len(self.labels) - 2

    def modelColumnCount(self):
        return len(self.model_fields)

    def headerData(self, section, orientation, role): # base class method
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return QVariant(self.labels[section])
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return QVariant(section+1) # порядковый номер
        return QVariant()

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def _dtapply(self, value):
        if value is not None:
            if type(value) is date:
                return value
            if type(value) is datetime:
                result = value
            else:
                result = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return result.date()
        else:
            return None

    def _card_type(self, value):
        return [self.tr('Normal'), self.tr('Club')][int(value)]

    def data(self, index, role): # base class method
        if not index.isValid():
            return QVariant()
        if role not in (Qt.DisplayRole, Qt.ToolTipRole) :
            return QVariant()
        idx_row = index.row()
        idx_col = index.column()
        record = list(self.storage[idx_row])

        map = (unicode, float, self._card_type,
               int, int,
               self._dtapply, self._dtapply,
               self._dtapply, self._dtapply,
               int, int)

        meta_func = map[idx_col]
        try:
            value = record[idx_col]
        except IndexError:
            return QVariant() # запись в модели ещё не заполнена

        if value is None:
            return QVariant() # пустое значение
        else:
            return QVariant(meta_func(value))

    def setRow(self, index, record, role, card_type=1,
               bgn_date=date.today(), duration_index=0):
        print 'setRow:', card_type, duration_index
        if index.isValid() and role == Qt.EditRole:
            today = date.today()
            reg_date = today
            if card_type == 0:
                exp_date = bgn_date + timedelta(days=30)
            else:
                deltas = (relativedelta(months=+3), #0
                          relativedelta(months=+6), #1
                          relativedelta(months=+9), #2
                          relativedelta(months=+12), #3
                      )
                exp_date = bgn_date + deltas[duration_index]
            print bgn_date, type(bgn_date)
            print exp_date, type(exp_date)
            title, course_id, count, price, coaches, duration = record
            record = [title, price, card_type, count, 0,
                      reg_date, bgn_date, exp_date, None, 0, course_id]

            idx_row = index.row()
            idx_col = 0
            for i in record:
                self.setData(self.createIndex(idx_row, idx_col), i, role)
                idx_col += 1

            self.temporary_assigned.append(record)

    def setData(self, index, value, role):
        if index.isValid() and role == Qt.EditRole:
            idx_row = index.row()
            idx_col = index.column()

            record = list(self.storage[idx_row])
            if len(record) == 0: # init record in this case
                for i in xrange(self.modelColumnCount()):
                    record.append(None)
            if type(value) is QVariant:
                v, ok = value.toInt()
            else:
                v = value
            #print type(value), value
            record[idx_col] = v
            self.storage[idx_row] = tuple(record)

#             for item in self.storage:
#                 print '\t',
#                 for col in item:
#                     print col,
#                 print

            self.emit(SIGNAL('dataChanged(QModelIndex, QModelIndex)'),
                      index, index)
            return True
        return False

    def insertRows(self, position, rows, parent):
        self.beginInsertRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            self.storage.insert(0, tuple())

        self.endInsertRows()
        return True

    def removeRows(self, position, rows, parent):
        self.beginRemoveRows(QModelIndex(), position, position+rows-1)
        for i in xrange(rows):
            del(self.storage[position + i])
        self.endRemoveRows()
        return True

class CoursesListDelegate(QItemDelegate):

    """ Делегат, позволяющий пользователю изменять содержимое ячеек. """

    def __init__(self, parent=None):
        QItemDelegate.__init__(self, parent)

#     def eventFilter(obj, event):
#         print 'event type', event.type()

    def createEditor(self, parent, option, index):
        editor = QSpinBox(parent)
        editor.setMinimum(0)
        editor.setMaximum(64)
        editor.installEventFilter(self)
        return editor

    def setEditorData(self, spinBox, index):
        value, ok = index.model().data(index, Qt.DisplayRole).toInt()

        spinBox.setValue(value)

    def setModelData(self, spinBox, model, index):
        spinBox.interpretText()
        value = spinBox.value()
        model.setData(index, QVariant(value), Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class CoursesList(QTableView):

    """ Класс списка курсов. """

    def __init__(self, parent=None):
        QTableView.__init__(self, parent)

        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)

        self.actionCourseCancel = QAction(self.tr('Cance&l course'), self)
        self.actionCourseCancel.setStatusTip(self.tr('Cancel current course.'))
        self.connect(self.actionCourseCancel, SIGNAL('triggered()'), self.courseCancel)

#     def mousePressEvent(self, event):
#         if event.button() == Qt.LeftButton:
#             index = self.indexAt(event.pos())
#             print index.row()

    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        self.contextRow = index.row()
        menu = QMenu(self)
        menu.addAction(self.actionCourseCancel)
        menu.exec_(event.globalPos())

    def courseCancel(self):
        print 'canceled [%i]' % self.contextRow
